"""A2 (CLV) y A3 (churn): valor del cliente con margen real y riesgo de fuga.

Ejecutar: python -m retailventure_dss.analitycs.clv_churn

"""

import numpy as np
import pandas as pd

from retailventure_dss.analitycs._base import (
    DIAS_VENTANA,
    FIN_VENTANA,
    INICIO_VENTANA,
    cargar_clientes,
    cargar_ventas,
    guardar,
)

MODULO = "clv_churn"
HORIZONTE_DIAS = 180            # proyección a 6 meses
TASA_DESCUENTO = 0.10           # supuesto: tasa anual de descuento para el CLV
HORIZONTE_CLV_ANIOS = 3         # supuesto: horizonte del CLV
UMBRAL_VIGILANCIA = 0.25        # S(recencia) < 25 %: más silencio que 3 de cada 4 intervalos
UMBRAL_RIESGO = 0.10            # S(recencia) < 10 %: más silencio que 9 de cada 10 intervalos
MIN_INTERVALOS = 300            # mínimo de intervalos para estimar la curva de un segmento
SEGMENTO_FALLBACK = "Esporádico"


# --------------------------------------------------------------------------------------
# CLV con margen real
# --------------------------------------------------------------------------------------
def clv_por_segmento(
    ventas: pd.DataFrame,
    clientes: pd.DataFrame,
    horizonte_anios: int = HORIZONTE_CLV_ANIOS,
    tasa_descuento: float = TASA_DESCUENTO,
) -> pd.DataFrame:
    """CLV = margen anual por cliente comprador x factor de retención y descuento.

    factor = suma_{k=0}^{H-1} (r / (1 + d))^k, con r = retención anual observada
    (clientes que compraron en 2023 y también en 2024 / compradores de 2023).
    Se reporta por cliente comprador y por cliente registrado (incluye los que nunca
    compraron) y con el margen bruto y el margen tras devoluciones (conservador).
    """
    v = ventas.assign(anio=ventas["fecha"].dt.year)
    anios = DIAS_VENTANA / 365.25
    filas = []
    for seg, c in clientes.groupby("segmento"):
        d = v[v["segmento"] == seg]
        compradores = d["cliente_id"].nunique()
        c23 = set(d.loc[d["anio"] == 2023, "cliente_id"])
        c24 = set(d.loc[d["anio"] == 2024, "cliente_id"])
        retencion = len(c23 & c24) / len(c23) if c23 else np.nan
        r = retencion if not np.isnan(retencion) else 0.0
        factor = sum((r / (1 + tasa_descuento)) ** k for k in range(horizonte_anios))
        margen_anual = d["margen"].sum() / anios
        margen_neto_anual = (d["margen"].sum() - d["monto_devuelto"].sum()) / anios
        por_comprador = margen_anual / compradores if compradores else 0.0
        por_comprador_neto = margen_neto_anual / compradores if compradores else 0.0
        filas.append(
            {
                "segmento": seg,
                "clientes_registrados": len(c),
                "clientes_compradores": compradores,
                "pct_sin_compras": (1 - compradores / len(c)) * 100,
                "margen_anual_por_comprador": por_comprador,
                "retencion_anual_observada": retencion,
                "factor_clv": factor,
                "clv_por_comprador": por_comprador * factor,
                "clv_por_cliente_registrado": por_comprador * factor * compradores / len(c),
                "clv_por_comprador_tras_devol": por_comprador_neto * factor,
                "clv_total_segmento": por_comprador * factor * compradores,
                "ticket_medio": d["monto_neto"].mean(),
                "compras_por_comprador_anio": len(d) / compradores / anios if compradores else 0,
            }
        )
    return pd.DataFrame(filas).sort_values("clv_por_comprador", ascending=False)


# --------------------------------------------------------------------------------------
# Churn: inactividad relativa a la cadencia de recompra
# --------------------------------------------------------------------------------------
class SupervivenciaKM:
    """Kaplan-Meier del tiempo entre compras. S(x) = P(el siguiente intervalo > x días).

    Incluye como observación censurada el silencio actual de cada cliente (todavía no
    compró de nuevo), para no subestimar los intervalos largos.
    """

    def __init__(self, duraciones: np.ndarray, observado: np.ndarray):
        d = pd.DataFrame({"t": duraciones, "e": observado})
        tiempos = np.sort(d.loc[d["e"] == 1, "t"].unique())
        s, curva = 1.0, []
        for t in tiempos:
            en_riesgo = (d["t"] >= t).sum()
            eventos = ((d["t"] == t) & (d["e"] == 1)).sum()
            s *= 1 - eventos / en_riesgo
            curva.append(s)
        self.tiempos = tiempos
        self.curva = np.array(curva)

    def __call__(self, x: float) -> float:
        i = np.searchsorted(self.tiempos, x, side="right")
        return 1.0 if i == 0 else float(self.curva[i - 1])

    def prob_no_retorno(self, recencia: float, horizonte: float) -> float:
        """P(no compra en los próximos `horizonte` días | ya lleva `recencia` días sin comprar)."""
        s0 = self(recencia)
        return 1.0 if s0 <= 0 else self(recencia + horizonte) / s0


def tabla_clientes(
    ventas: pd.DataFrame, clientes: pd.DataFrame, fin: pd.Timestamp = FIN_VENTANA
) -> pd.DataFrame:
    g = ventas.groupby("cliente_id").agg(
        primera_compra=("fecha", "min"),
        ultima_compra=("fecha", "max"),
        frecuencia=("transaccion_id", "nunique"),
        ingreso_total=("monto_neto", "sum"),
        margen_total=("margen", "sum"),
    )
    g["ticket_medio"] = g["ingreso_total"] / g["frecuencia"]
    g["recencia_dias"] = (fin - g["ultima_compra"]).dt.days
    return clientes[["cliente_id", "segmento", "ciudad", "canal_adquisicion"]].merge(
        g, on="cliente_id", how="left"
    )


def _curvas_por_segmento(ventas: pd.DataFrame, tabla: pd.DataFrame) -> dict[str, SupervivenciaKM]:
    v = ventas.sort_values(["cliente_id", "fecha"]).copy()
    v["intervalo"] = v.groupby("cliente_id")["fecha"].diff().dt.days
    obs = v.dropna(subset=["intervalo"])[["cliente_id", "segmento", "intervalo"]]
    obs = obs.assign(e=1)
    cens = tabla.dropna(subset=["recencia_dias"])[["cliente_id", "segmento", "recencia_dias"]]
    cens = cens.rename(columns={"recencia_dias": "intervalo"}).assign(e=0)
    todo = pd.concat([obs, cens], ignore_index=True)
    curvas: dict[str, SupervivenciaKM] = {}
    for seg, d in todo.groupby("segmento"):
        if (d["e"] == 1).sum() >= MIN_INTERVALOS:
            curvas[seg] = SupervivenciaKM(d["intervalo"].to_numpy(), d["e"].to_numpy())
    # Segmentos sin recompras suficientes (Inactivo, Nuevo) usan la cadencia del Esporádico
    fb = curvas[SEGMENTO_FALLBACK]
    for seg in todo["segmento"].unique():
        curvas.setdefault(seg, fb)
    return curvas


def clasificar_churn(
    ventas: pd.DataFrame, clientes: pd.DataFrame, fin: pd.Timestamp = FIN_VENTANA
) -> pd.DataFrame:
    """`fin` permite clasificar a una fecha pasada (backtest); por defecto, el fin de la ventana."""
    dias_ventana = (fin - INICIO_VENTANA).days + 1
    t = tabla_clientes(ventas, clientes, fin)
    curvas = _curvas_por_segmento(ventas, t)
    margen_pct = (
        ventas.groupby("segmento")["margen"].sum() / ventas.groupby("segmento")["monto_neto"].sum()
    )
    t["curva_usada"] = t["segmento"].where(
        t["segmento"].map(lambda s: curvas[s] is not curvas[SEGMENTO_FALLBACK]) | (t["segmento"] == SEGMENTO_FALLBACK),
        SEGMENTO_FALLBACK,
    )
    sin_compras = t["recencia_dias"].isna()
    t["s_recencia"] = np.nan
    t["prob_no_retorno_6m"] = np.nan
    t["prob_no_retorno_6m_base"] = np.nan
    for i, r in t[~sin_compras].iterrows():
        km = curvas[r["segmento"]]
        t.at[i, "s_recencia"] = km(r["recencia_dias"])
        t.at[i, "prob_no_retorno_6m"] = km.prob_no_retorno(r["recencia_dias"], HORIZONTE_DIAS)
        t.at[i, "prob_no_retorno_6m_base"] = km.prob_no_retorno(0, HORIZONTE_DIAS)
    t["estado"] = np.select(
        [sin_compras, t["s_recencia"] < UMBRAL_RIESGO, t["s_recencia"] < UMBRAL_VIGILANCIA],
        ["Sin compras", "En riesgo", "En vigilancia"],
        default="Activo",
    )
    # Ingreso esperado a 6 meses si el cliente siguiera su ritmo histórico
    t["ingreso_esperado_6m"] = t["ingreso_total"] / dias_ventana * HORIZONTE_DIAS
    # Escenario adverso: el cliente marcado no vuelve. Esperado: ponderado por la
    # probabilidad de no retorno que implica la cadencia observada.
    t["ingreso_esperado_perdido_6m"] = t["ingreso_esperado_6m"] * t["prob_no_retorno_6m"]
    # Parte atribuible a la inactividad prolongada: exceso sobre un cliente recién activo
    exceso = (t["prob_no_retorno_6m"] - t["prob_no_retorno_6m_base"]).clip(lower=0)
    t["ingreso_perdido_incremental_6m"] = t["ingreso_esperado_6m"] * exceso
    t["margen_pct_segmento"] = t["segmento"].map(margen_pct)
    t["margen_esperado_6m"] = t["ingreso_esperado_6m"] * t["margen_pct_segmento"]
    t["margen_perdido_incremental_6m"] = t["ingreso_perdido_incremental_6m"] * t["margen_pct_segmento"]
    return t


def resumen_churn(t: pd.DataFrame) -> pd.DataFrame:
    g = t.groupby(["segmento", "estado"]).agg(
        clientes=("cliente_id", "size"),
        ingreso_historico=("ingreso_total", "sum"),
        ingreso_expuesto_6m=("ingreso_esperado_6m", "sum"),
        ingreso_esperado_perdido_6m=("ingreso_esperado_perdido_6m", "sum"),
        ingreso_perdido_incremental_6m=("ingreso_perdido_incremental_6m", "sum"),
    )
    return g.reset_index()


def segmento_mayor_valor_en_riesgo(t: pd.DataFrame) -> pd.DataFrame:
    """Clientes 'En riesgo' agrupados por segmento y por tramo de valor (quintil de
    ingreso histórico entre todos los compradores), ordenados por pérdida esperada."""
    comp = t.dropna(subset=["ingreso_total"]).copy()
    comp["quintil_valor"] = pd.qcut(comp["ingreso_total"].rank(method="first"), 5, labels=["Q1 (menor)", "Q2", "Q3", "Q4", "Q5 (mayor)"])
    riesgo = comp[comp["estado"].isin(["En riesgo"])]
    g = riesgo.groupby(["segmento", "quintil_valor"], observed=True).agg(
        clientes=("cliente_id", "size"),
        ingreso_historico=("ingreso_total", "sum"),
        ingreso_expuesto_6m=("ingreso_esperado_6m", "sum"),
        margen_expuesto_6m=("margen_esperado_6m", "sum"),
        ingreso_esperado_perdido_6m=("ingreso_esperado_perdido_6m", "sum"),
        ingreso_perdido_incremental_6m=("ingreso_perdido_incremental_6m", "sum"),
    )
    # Se ordena por la pérdida ESPERADA (ponderada por la probabilidad de no retorno), no por
    # el ingreso expuesto: el expuesto asume que nadie vuelve y sobrestima el riesgo de
    # segmentos regulares (Premium/Frecuente), que en el backtest casi siempre regresan.
    return g.reset_index().sort_values("ingreso_esperado_perdido_6m", ascending=False)


def umbrales_inactividad(ventas: pd.DataFrame, t: pd.DataFrame) -> pd.DataFrame:
    """Días de silencio que corresponden a los umbrales de vigilancia y riesgo, por segmento."""
    curvas = _curvas_por_segmento(ventas, t)
    filas = []
    for seg, km in curvas.items():
        def dias_para(p: float) -> float:
            idx = np.where(km.curva < p)[0]
            return float(km.tiempos[idx[0]]) if len(idx) else np.nan
        filas.append(
            {
                "segmento": seg,
                "dias_vigilancia": dias_para(UMBRAL_VIGILANCIA),
                "dias_riesgo": dias_para(UMBRAL_RIESGO),
                "mediana_intervalo": dias_para(0.5),
                "curva_propia": km is not curvas[SEGMENTO_FALLBACK] or seg == SEGMENTO_FALLBACK,
            }
        )
    return pd.DataFrame(filas)


def run() -> dict[str, pd.DataFrame]:
    ventas, clientes = cargar_ventas(), cargar_clientes()
    t = clasificar_churn(ventas, clientes)
    res = {
        "clv_por_segmento": clv_por_segmento(ventas, clientes),
        "umbrales_inactividad": umbrales_inactividad(ventas, t),
        "churn_resumen": resumen_churn(t),
        "churn_mayor_valor_en_riesgo": segmento_mayor_valor_en_riesgo(t),
        "churn_detalle_clientes": t,
    }
    for nombre, df in res.items():
        guardar(df, MODULO, nombre)
    return res


if __name__ == "__main__":
    pd.set_option("display.width", 220, "display.max_columns", 30)
    res = run()
    for nombre, df in res.items():
        if nombre == "churn_detalle_clientes":
            continue
        print(f"\n=== {nombre} ===")
        print(df.round(3).to_string(index=False))
    t = res["churn_detalle_clientes"]
    r = t[t["estado"] == "En riesgo"]
    print("\nClientes 'En riesgo':", len(r))
    print("Ingreso expuesto a 6 meses (si no vuelven):", round(r["ingreso_esperado_6m"].sum()))
    print("Margen expuesto a 6 meses:", round(r["margen_esperado_6m"].sum()))
    print("Ingreso esperado perdido (ponderado):", round(r["ingreso_esperado_perdido_6m"].sum()))
    print("Parte atribuible a la inactividad:", round(t["ingreso_perdido_incremental_6m"].sum()))
