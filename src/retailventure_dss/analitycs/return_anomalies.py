"""A3: fugas por devoluciones y efecto de las quejas del CRM sobre la recompra.

Ejecutar: python -m retailventure_dss.analitycs.return_anomalies

Principios metodológicos:
  - Tasa de devolución = devoluciones / transacciones, por cohorte de COMPRA (no por
    fecha de devolución, que arrastra el efecto de borde de fin de ventana).
  - Anomalía = diferencia estadísticamente significativa contra una base (global o la
    de la categoría), con corrección por comparaciones múltiples (Benjamini-Hochberg).
  - Reincidencia = exceso de clientes con muchas devoluciones respecto a lo que
    produciría el azar dado su mix de productos (simulación Monte Carlo).
  - Efecto CRM = diferencias en diferencias (antes/después de la queja) contra un
    grupo de control sin quejas, controlando por segmento.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests

from retailventure_dss.analitycs._base import (
    FIN_VENTANA,
    INICIO_VENTANA,
    cargar_clientes,
    cargar_crm,
    cargar_ventas,
    guardar,
)

MODULO = "devoluciones_crm"
ALFA = 0.05


# --------------------------------------------------------------------------------------
# 1. Tasas de devolución y anomalías
# --------------------------------------------------------------------------------------
def tasas_vs_base(
    ventas: pd.DataFrame, dimension: str, base: str | None = None, una_cola: bool = False
) -> pd.DataFrame:
    """Tasa de devolución por `dimension` contra una tasa base.

    base=None: base = tasa global. base="categoria": base = tasa de la categoría del
    grupo (útil para productos: separa "el producto es malo" de "su categoría devuelve más").
    """
    claves = [base, dimension] if base else [dimension]
    g = ventas.groupby(claves).agg(
        transacciones=("transaccion_id", "size"),
        devoluciones=("devuelta", "sum"),
        monto_vendido=("monto_neto", "sum"),
        monto_devuelto=("monto_devuelto", "sum"),
    ).reset_index()
    if base:
        tb = ventas.groupby(base)["devuelta"].mean().rename("tasa_base")
        g = g.merge(tb, left_on=base, right_index=True)
    else:
        g["tasa_base"] = ventas["devuelta"].mean()
    g["tasa"] = g["devoluciones"] / g["transacciones"]
    g["lift_vs_base"] = g["tasa"] / g["tasa_base"]
    alt = "greater" if una_cola else "two-sided"
    g["p_valor"] = [
        stats.binomtest(int(k), int(n), p, alternative=alt).pvalue
        for k, n, p in zip(g["devoluciones"], g["transacciones"], g["tasa_base"])
    ]
    g["q_valor_fdr"] = multipletests(g["p_valor"], method="fdr_bh")[1]
    g["anomalo_alto"] = (g["q_valor_fdr"] < ALFA) & (g["tasa"] > g["tasa_base"])
    g["anomalo_bajo"] = (g["q_valor_fdr"] < ALFA) & (g["tasa"] < g["tasa_base"])
    g["devoluciones_en_exceso"] = (g["devoluciones"] - g["tasa_base"] * g["transacciones"]).clip(lower=0)
    return g.sort_values("tasa", ascending=False)


def motivos_por_categoria(ventas: pd.DataFrame) -> pd.DataFrame:
    d = ventas[ventas["devuelta"]]
    t = pd.crosstab(d["categoria"], d["motivo"], normalize="index") * 100
    return t.reset_index()


def tendencia_devoluciones(ventas: pd.DataFrame) -> pd.DataFrame:
    """Tasa trimestral por cohorte de compra y por fecha de devolución.

    La segunda es la que produce el pico aparente de Q4 2024: las devoluciones se
    asignan al trimestre en que ocurren, y a fin de ventana se acumulan (hay 158
    devoluciones fechadas exactamente el 2024-12-31, el máximo del dataset).
    """
    v = ventas.assign(trim_compra=ventas["fecha"].dt.to_period("Q"))
    coh = v.groupby("trim_compra").agg(
        transacciones=("transaccion_id", "size"), devoluciones=("devuelta", "sum")
    )
    coh["tasa_por_cohorte_compra_pct"] = coh["devoluciones"] / coh["transacciones"] * 100
    dev = v[v["devuelta"]].assign(trim_dev=lambda x: x["fecha_devolucion"].dt.to_period("Q"))
    por_fecha = dev.groupby("trim_dev").size().rename("devoluciones_por_fecha_devolucion")
    out = coh.join(por_fecha, how="left")
    out["tasa_por_fecha_devolucion_pct"] = out["devoluciones_por_fecha_devolucion"] / out["transacciones"] * 100
    return out.reset_index().rename(columns={"trim_compra": "trimestre"}).astype({"trimestre": str})


def prueba_tendencia_cohorte(ventas: pd.DataFrame) -> pd.DataFrame:
    """Regresión logística de devuelta ~ mes de compra: ¿sube la tasa en el tiempo?"""
    v = ventas.assign(t=(ventas["fecha"] - INICIO_VENTANA).dt.days / 30.44)
    m = sm.Logit(v["devuelta"].astype(int), sm.add_constant(v["t"])).fit(disp=0)
    return pd.DataFrame(
        [{
            "odds_ratio_por_mes": float(np.exp(m.params["t"])),
            "p_valor": float(m.pvalues["t"]),
            "conclusion": "la tasa cambia en el tiempo" if m.pvalues["t"] < ALFA else "tasa estable en el tiempo",
        }]
    )


def conteo_fin_de_ventana(ventas: pd.DataFrame) -> pd.DataFrame:
    d = ventas[ventas["devuelta"]]
    por_dia = d.groupby("fecha_devolucion").size()
    ultimo = int(por_dia.get(FIN_VENTANA, 0))
    return pd.DataFrame(
        [{
            "devoluciones_el_ultimo_dia": ultimo,
            "promedio_diario_resto": float(por_dia.drop(FIN_VENTANA, errors="ignore").mean()),
            "interpretacion": "fechas truncadas al fin de la ventana: no usar fecha_devolucion para tendencias",
        }]
    )


# --------------------------------------------------------------------------------------
# 2. Clientes recurrentes en devoluciones
# --------------------------------------------------------------------------------------
def reincidencia(ventas: pd.DataFrame, simulaciones: int = 300, semilla: int = 7) -> dict[str, pd.DataFrame]:
    """¿Hay más clientes con muchas devoluciones de las que daría el azar?

    Nulo: cada transacción se devuelve con la tasa de SU categoría, de forma
    independiente. Si los reincidentes fueran un fenómeno de comportamiento del cliente,
    el número observado de clientes con >= k devoluciones superaría lo simulado.
    """
    v = ventas.sort_values("cliente_id").reset_index(drop=True)
    p = v["categoria"].map(v.groupby("categoria")["devuelta"].mean()).to_numpy()
    inicios = np.flatnonzero(np.r_[True, v["cliente_id"].to_numpy()[1:] != v["cliente_id"].to_numpy()[:-1]])
    obs_por_cliente = v.groupby("cliente_id")["devuelta"].sum()
    rng = np.random.default_rng(semilla)
    ks = [2, 3, 4, 5, 6]
    sim = np.zeros((simulaciones, len(ks)))
    for s in range(simulaciones):
        dev = rng.random(len(v)) < p
        por_cli = np.add.reduceat(dev.astype(np.int16), inicios)
        for j, k in enumerate(ks):
            sim[s, j] = (por_cli >= k).sum()
    filas = []
    for j, k in enumerate(ks):
        observado = int((obs_por_cliente >= k).sum())
        filas.append(
            {
                "devoluciones_minimas": k,
                "clientes_observados": observado,
                "clientes_esperados_por_azar": sim[:, j].mean(),
                "ic95_inf": np.percentile(sim[:, j], 2.5),
                "ic95_sup": np.percentile(sim[:, j], 97.5),
                "p_valor_exceso": (1 + (sim[:, j] >= observado).sum()) / (simulaciones + 1),
                "hay_exceso": observado > np.percentile(sim[:, j], 97.5),
            }
        )
    top = (
        v.groupby("cliente_id")
        .agg(
            segmento=("segmento", "first"),
            compras=("transaccion_id", "size"),
            devoluciones=("devuelta", "sum"),
            monto_devuelto=("monto_devuelto", "sum"),
        )
    )
    top["esperadas_por_azar"] = pd.Series(p, index=v.index).groupby(v["cliente_id"]).sum()
    top["tasa_personal"] = top["devoluciones"] / top["compras"]
    top = top.sort_values(["devoluciones", "monto_devuelto"], ascending=False).head(25).reset_index()
    return {"reincidencia_vs_azar": pd.DataFrame(filas), "top_clientes_devoluciones": top}


# --------------------------------------------------------------------------------------
# 3. Impacto económico de las devoluciones
# --------------------------------------------------------------------------------------
def impacto_devoluciones(ventas: pd.DataFrame, tasas_categoria: pd.DataFrame) -> pd.DataFrame:
    """Monto devuelto en exceso: si las categorías anómalas devolvieran como el resto."""
    cat = tasas_categoria.set_index("categoria")
    filas = []
    for c, r in cat.iterrows():
        resto = cat.drop(c)
        tasa_ref = resto["devoluciones"].sum() / resto["transacciones"].sum()
        monto_prom = r["monto_devuelto"] / r["devoluciones"]
        exceso_n = max(r["devoluciones"] - tasa_ref * r["transacciones"], 0)
        filas.append(
            {
                "categoria": c,
                "tasa": r["tasa"],
                "tasa_resto_categorias": tasa_ref,
                "monto_devuelto_total": r["monto_devuelto"],
                "pct_del_monto_vendido": r["monto_devuelto"] / r["monto_vendido"] * 100,
                "devoluciones_en_exceso": exceso_n,
                "monto_en_exceso_24m": exceso_n * monto_prom,
                "monto_en_exceso_anualizado": exceso_n * monto_prom / 2,  # 24 meses -> año
            }
        )
    return pd.DataFrame(filas).sort_values("monto_en_exceso_24m", ascending=False)


# --------------------------------------------------------------------------------------
# 4. CRM: ¿las quejas sin resolver reducen la frecuencia de compra?
# --------------------------------------------------------------------------------------
def _conteos_antes_despues(ventas: pd.DataFrame, pares: pd.DataFrame, ventana: int) -> pd.DataFrame:
    fechas = ventas.groupby("cliente_id")["fecha"].apply(lambda s: s.to_numpy("datetime64[D]"))
    antes, despues = [], []
    w = np.timedelta64(ventana, "D")
    for cid, f in zip(pares["cliente_id"], pares["fecha_indice"].to_numpy("datetime64[D]")):
        arr = fechas.get(cid)
        if arr is None:
            antes.append(0); despues.append(0); continue
        antes.append(int(((arr >= f - w) & (arr < f)).sum()))
        despues.append(int(((arr > f) & (arr <= f + w)).sum()))
    out = pares.copy()
    out["compras_antes"], out["compras_despues"] = antes, despues
    out["delta"] = out["compras_despues"] - out["compras_antes"]
    return out


def efecto_quejas(ventas: pd.DataFrame, crm: pd.DataFrame, clientes: pd.DataFrame, ventana: int = 90, semilla: int = 11) -> dict[str, pd.DataFrame]:
    """Diferencias en diferencias sobre la primera queja de cada cliente.

    Unidad: cliente. Índice: fecha de su primera queja dentro de la zona donde existen
    `ventana` días completos antes y después. Grupos: queja sin resolver, resuelta,
    parcial/escalada y CONTROL (clientes sin ninguna queja, con fecha índice sorteada de
    la misma distribución de fechas de quejas). El efecto es la diferencia de cambios
    (después - antes) entre grupos, ajustada por segmento (que determina cuánto compra
    el cliente y por tanto cuánto puede cambiar). La referencia del modelo es el CONTROL:
    cada coeficiente es el cambio en compras de ese grupo menos el del control.
    """
    lo = INICIO_VENTANA + pd.Timedelta(days=ventana)
    hi = FIN_VENTANA - pd.Timedelta(days=ventana)
    q = crm[crm["tipo"] == "queja"].copy()
    q = q[(q["fecha"] >= lo) & (q["fecha"] <= hi)].sort_values("fecha").drop_duplicates("cliente_id")
    q["grupo"] = q["resolucion"].map(
        {"sin_resolver": "queja sin resolver", "resuelto": "queja resuelta",
         "parcialmente_resuelto": "queja parcial/escalada", "escalado": "queja parcial/escalada"}
    )
    q = q.rename(columns={"fecha": "fecha_indice"})[["cliente_id", "fecha_indice", "grupo"]]

    con_queja = set(crm.loc[crm["tipo"] == "queja", "cliente_id"])
    ctrl = clientes[~clientes["cliente_id"].isin(con_queja)][["cliente_id"]].copy()
    rng = np.random.default_rng(semilla)
    ctrl["fecha_indice"] = rng.choice(q["fecha_indice"].to_numpy(), size=len(ctrl))
    ctrl["grupo"] = "control (sin quejas)"

    base = pd.concat([q, ctrl], ignore_index=True)
    base = base.merge(clientes[["cliente_id", "segmento"]], on="cliente_id")
    d = _conteos_antes_despues(ventas, base, ventana)

    resumen = d.groupby("grupo").agg(
        clientes=("cliente_id", "size"),
        compras_antes=("compras_antes", "mean"),
        compras_despues=("compras_despues", "mean"),
        delta_medio=("delta", "mean"),
        error_estandar=("delta", lambda s: s.std(ddof=1) / np.sqrt(len(s))),
    ).reset_index()

    # Efecto ajustado por segmento, referencia = control (clientes sin quejas)
    m = smf.ols(
        "delta ~ C(grupo, Treatment('control (sin quejas)')) + C(segmento)", data=d
    ).fit(cov_type="HC3")
    ci = m.conf_int()
    efectos = []
    for nombre in m.params.index:
        if nombre.startswith("C(grupo"):
            efectos.append(
                {
                    "comparacion_vs_control": nombre.split("T.")[1].rstrip("]"),
                    "efecto_en_compras": m.params[nombre],
                    "ic95_inf": ci.loc[nombre, 0],
                    "ic95_sup": ci.loc[nombre, 1],
                    "p_valor": m.pvalues[nombre],
                    # efecto mínimo detectable (80 % de potencia): 2.8 x error estándar
                    "efecto_minimo_detectable": 2.8 * (ci.loc[nombre, 1] - ci.loc[nombre, 0]) / 3.92,
                    "ventana_dias": ventana,
                }
            )
    return {"crm_antes_despues": resumen.assign(ventana_dias=ventana), "crm_efecto_ajustado": pd.DataFrame(efectos)}


def efecto_quejas_sensibilidad(ventas, crm, clientes) -> pd.DataFrame:
    filas = []
    for w in (60, 90, 120):
        e = efecto_quejas(ventas, crm, clientes, ventana=w)["crm_efecto_ajustado"]
        filas.append(e)
    return pd.concat(filas, ignore_index=True)


def perfil_quejas(crm: pd.DataFrame) -> pd.DataFrame:
    q = crm[crm["tipo"] == "queja"]
    g = q.groupby("resolucion").agg(
        quejas=("interaccion_id", "size"),
        clientes=("cliente_id", "nunique"),
        respuesta_media_hrs=("tiempo_respuesta_hrs", "mean"),
    ).reset_index()
    g["pct_de_quejas"] = g["quejas"] / g["quejas"].sum() * 100
    return g


def run() -> dict[str, pd.DataFrame]:
    ventas, crm, clientes = cargar_ventas(), cargar_crm(), cargar_clientes()
    res: dict[str, pd.DataFrame] = {}
    res["tasa_global"] = pd.DataFrame(
        [{"transacciones": len(ventas), "devoluciones": int(ventas["devuelta"].sum()),
          "tasa_global": ventas["devuelta"].mean(), "monto_devuelto": ventas["monto_devuelto"].sum(),
          "pct_del_ingreso": ventas["monto_devuelto"].sum() / ventas["monto_neto"].sum() * 100}]
    )
    res["tasa_por_categoria"] = tasas_vs_base(ventas, "categoria")
    res["tasa_por_subcategoria"] = tasas_vs_base(ventas, "subcategoria", base="categoria")
    res["tasa_por_producto_vs_su_categoria"] = tasas_vs_base(ventas, "producto_id", base="categoria", una_cola=True)
    res["tasa_por_segmento"] = tasas_vs_base(ventas, "segmento")
    res["tasa_por_canal"] = tasas_vs_base(ventas, "canal")
    res["tasa_por_canal_adquisicion"] = tasas_vs_base(ventas, "canal_adquisicion")
    res["motivos_por_categoria"] = motivos_por_categoria(ventas)
    res["tendencia_trimestral"] = tendencia_devoluciones(ventas)
    res["tendencia_prueba"] = prueba_tendencia_cohorte(ventas)
    res["efecto_borde_fin_ventana"] = conteo_fin_de_ventana(ventas)
    res.update(reincidencia(ventas))
    res["impacto_exceso_por_categoria"] = impacto_devoluciones(ventas, res["tasa_por_categoria"])
    res["crm_perfil_quejas"] = perfil_quejas(crm)
    res.update(efecto_quejas(ventas, crm, clientes))
    res["crm_sensibilidad_ventana"] = efecto_quejas_sensibilidad(ventas, crm, clientes)
    for nombre, df in res.items():
        guardar(df, MODULO, nombre)
    return res


if __name__ == "__main__":
    pd.set_option("display.width", 230, "display.max_columns", 30, "display.max_rows", 60)
    res = run()
    for nombre, df in res.items():
        if nombre == "tasa_por_producto_vs_su_categoria":
            print(f"\n=== {nombre} (top 15 de {len(df)}; anómalos: {int(df['anomalo_alto'].sum())}) ===")
            print(df.head(15).round(4).to_string(index=False))
            continue
        print(f"\n=== {nombre} ===")
        print(df.round(4).to_string(index=False))
