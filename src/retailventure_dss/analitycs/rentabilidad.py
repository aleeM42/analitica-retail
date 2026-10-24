"""A2 (parte 1): contribución al margen, segmentos en declive y estacionalidad.

Ejecutar: python -m retailventure_dss.analitycs.rentabilidad
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests

from retailventure_dss.analitycs._base import cargar_ventas, guardar

MODULO = "rentabilidad"


# --------------------------------------------------------------------------------------
# 1. Contribución al margen bruto por segmento, categoría y canal
# --------------------------------------------------------------------------------------
def contribucion_margen(ventas: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Ingreso, margen y participación por `dimension`.

    Se reportan dos márgenes tras devoluciones para no esconder la fuga:
      - conservador: la mercancía devuelta no se recupera (margen - monto devuelto).
      - optimista: la mercancía se revende al costo (margen - devuelto + costo devuelto).
    """
    g = ventas.groupby(dimension).agg(
        transacciones=("transaccion_id", "size"),
        ingreso=("monto_neto", "sum"),
        margen_bruto=("margen", "sum"),
        monto_devuelto=("monto_devuelto", "sum"),
        costo_devuelto=("costo_devuelto", "sum"),
    )
    g["margen_pct"] = g["margen_bruto"] / g["ingreso"]
    g["pct_del_ingreso"] = g["ingreso"] / g["ingreso"].sum()
    g["pct_del_margen"] = g["margen_bruto"] / g["margen_bruto"].sum()
    g["brecha_margen_vs_ingreso_pp"] = (g["pct_del_margen"] - g["pct_del_ingreso"]) * 100
    g["margen_tras_devol_conservador"] = g["margen_bruto"] - g["monto_devuelto"]
    g["margen_tras_devol_optimista"] = (
        g["margen_bruto"] - g["monto_devuelto"] + g["costo_devuelto"]
    )
    g["margen_pct_tras_devol_conservador"] = (
        g["margen_tras_devol_conservador"] / (g["ingreso"] - g["monto_devuelto"])
    )
    return g.sort_values("margen_bruto", ascending=False).reset_index()


# --------------------------------------------------------------------------------------
# 2. Segmentos en declive (2024 vs 2023) con prueba estadística
# --------------------------------------------------------------------------------------
def segmentos_en_declive(
    ventas: pd.DataFrame, umbral: float = -0.05, alfa: float = 0.05
) -> pd.DataFrame:
    """Compara 2024 contra 2023 por segmento.

    Un segmento se marca en declive solo si el ingreso cae más de `umbral` Y la caída
    en número de transacciones o en ticket es estadísticamente significativa. Sin la
    prueba, cualquier fluctuación de azar se leería como "declive".
    """
    v = ventas.assign(anio=ventas["fecha"].dt.year)
    filas = []
    for seg, d in v.groupby("segmento"):
        a, b = d[d["anio"] == 2023], d[d["anio"] == 2024]
        n23, n24 = len(a), len(b)
        # Mismo periodo de exposición (365 vs 366 días): H0 -> proporción 365/731
        p_trx = stats.binomtest(n24, n23 + n24, 366 / 731).pvalue
        p_ticket = stats.ttest_ind(
            b["monto_neto"], a["monto_neto"], equal_var=False
        ).pvalue
        c23, c24 = set(a["cliente_id"]), set(b["cliente_id"])
        ing23, ing24 = a["monto_neto"].sum(), b["monto_neto"].sum()
        mar23, mar24 = a["margen"].sum(), b["margen"].sum()
        var_ing = ing24 / ing23 - 1
        significativo = (p_trx < alfa) or (p_ticket < alfa)
        filas.append(
            {
                "segmento": seg,
                "ingreso_2023": ing23,
                "ingreso_2024": ing24,
                "var_ingreso_pct": var_ing * 100,
                "margen_2023": mar23,
                "margen_2024": mar24,
                "var_margen_pct": (mar24 / mar23 - 1) * 100,
                "transacciones_2023": n23,
                "transacciones_2024": n24,
                "ticket_2023": a["monto_neto"].mean(),
                "ticket_2024": b["monto_neto"].mean(),
                "clientes_activos_2023": len(c23),
                "clientes_activos_2024": len(c24),
                "retencion_2023_a_2024": len(c23 & c24) / len(c23) if c23 else np.nan,
                "p_valor_transacciones": p_trx,
                "p_valor_ticket": p_ticket,
                "en_declive": bool(var_ing < umbral and significativo),
            }
        )
    return pd.DataFrame(filas).sort_values("var_ingreso_pct")


# --------------------------------------------------------------------------------------
# 3. Estacionalidad
# --------------------------------------------------------------------------------------
def _serie_mensual(ventas: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    v = ventas.assign(mes=ventas["fecha"].dt.to_period("M"))
    m = v.groupby(columnas + ["mes"]).agg(
        ingreso=("monto_neto", "sum"),
        margen=("margen", "sum"),
        transacciones=("transaccion_id", "size"),
    )
    m = m.reset_index()
    m["dias"] = m["mes"].dt.days_in_month
    m["ingreso_por_dia"] = m["ingreso"] / m["dias"]
    return m


def indice_estacional(ventas: pd.DataFrame, dimension: str | None = None) -> pd.DataFrame:
    """Índice estacional por mes calendario (1.00 = promedio), normalizado por días.

    El índice es descriptivo. La señal pico/valle se decide con una prueba estadística
    sobre el ingreso DIARIO (Welch: días de ese mes vs resto de días), corregida por
    comparaciones múltiples (Benjamini-Hochberg). Con solo 2 años de historia, una
    desviación visual del 5-10 % por mes es compatible con puro azar.
    """
    cols = [dimension] if dimension else []
    m = _serie_mensual(ventas, cols)
    m["anio"] = m["mes"].dt.year
    m["mes_num"] = m["mes"].dt.month
    clave = cols + ["anio"]
    m["indice"] = m["ingreso_por_dia"] / m.groupby(clave)["ingreso_por_dia"].transform("mean")
    p = m.pivot_table(index=cols + ["mes_num"], columns="anio", values="indice").reset_index()
    p.columns = [str(c) for c in p.columns]
    p["indice_promedio"] = p[["2023", "2024"]].mean(axis=1)

    # prueba sobre ingreso diario
    dias = pd.date_range(ventas["fecha"].min(), ventas["fecha"].max(), freq="D")
    grupos = ventas.groupby(dimension) if dimension else [(None, ventas)]
    pvals = {}
    for nombre, d in grupos:
        diario = d.groupby("fecha")["monto_neto"].sum().reindex(dias, fill_value=0.0)
        mes = diario.index.month
        for mm in range(1, 13):
            pvals[(nombre, mm)] = stats.ttest_ind(
                diario[mes == mm], diario[mes != mm], equal_var=False
            ).pvalue
    llaves = list(pvals)
    q = multipletests([pvals[k] for k in llaves], method="fdr_bh")[1]
    qmap = dict(zip(llaves, q))
    pmap = pvals
    if dimension:
        p["p_valor"] = [pmap[(r[dimension], r["mes_num"])] for _, r in p.iterrows()]
        p["q_valor_fdr"] = [qmap[(r[dimension], r["mes_num"])] for _, r in p.iterrows()]
    else:
        p["p_valor"] = [pmap[(None, mm)] for mm in p["mes_num"]]
        p["q_valor_fdr"] = [qmap[(None, mm)] for mm in p["mes_num"]]
    p["senal"] = np.where(
        p["q_valor_fdr"] >= 0.05, "sin patron",
        np.where(p["indice_promedio"] > 1, "pico", "valle"),
    )
    return p


def tendencia_mensual(ventas: pd.DataFrame, dimension: str | None = None) -> pd.DataFrame:
    """Pendiente de la tendencia lineal (ingreso por día) con su p-valor."""
    cols = [dimension] if dimension else []
    m = _serie_mensual(ventas, cols)
    filas = []
    grupos = m.groupby(dimension) if dimension else [(None, m)]
    for clave, d in grupos:
        d = d.sort_values("mes")
        x = sm.add_constant(np.arange(len(d)))
        fit = sm.OLS(d["ingreso_por_dia"].to_numpy(), x).fit()
        media = d["ingreso_por_dia"].mean()
        filas.append(
            {
                **({dimension: clave} if dimension else {}),
                "pendiente_pct_mensual": fit.params[1] / media * 100,
                "p_valor": fit.pvalues[1],
                "tendencia": "significativa" if fit.pvalues[1] < 0.05 else "no significativa",
            }
        )
    return pd.DataFrame(filas)


def prueba_estacionalidad(ventas: pd.DataFrame) -> pd.DataFrame:
    """Chi-cuadrado: ¿las transacciones se reparten por mes distinto a lo que implican
    los días del mes? Global, y mes x categoría / mes x canal (independencia)."""
    v = ventas.assign(mes_num=ventas["fecha"].dt.month)
    filas = []
    obs = v.groupby("mes_num").size().sort_index()
    dias = pd.Series([31, 28.5, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], index=range(1, 13))
    esp = dias / dias.sum() * obs.sum()
    chi, p = stats.chisquare(obs, esp)
    filas.append({"prueba": "transacciones por mes vs dias del mes", "chi2": chi, "p_valor": p})
    for dim in ["categoria", "canal"]:
        tabla = pd.crosstab(v["mes_num"], v[dim])
        chi, p, _, _ = stats.chi2_contingency(tabla)
        filas.append({"prueba": f"mes x {dim} (independencia)", "chi2": chi, "p_valor": p})
    out = pd.DataFrame(filas)
    out["conclusion"] = np.select(
        [out["p_valor"] < 0.01, out["p_valor"] < 0.05],
        ["hay estacionalidad", "evidencia marginal; ningún mes lo confirma tras FDR"],
        default="no se detecta",
    )
    return out


def run() -> dict[str, pd.DataFrame]:
    ventas = cargar_ventas()
    res: dict[str, pd.DataFrame] = {}
    for dim in ["segmento", "categoria", "canal"]:
        res[f"margen_por_{dim}"] = contribucion_margen(ventas, dim)
    res["segmentos_declive"] = segmentos_en_declive(ventas)
    res["estacionalidad_global"] = indice_estacional(ventas)
    res["estacionalidad_categoria"] = indice_estacional(ventas, "categoria")
    res["estacionalidad_canal"] = indice_estacional(ventas, "canal")
    res["tendencia_global"] = tendencia_mensual(ventas)
    res["tendencia_categoria"] = tendencia_mensual(ventas, "categoria")
    res["tendencia_canal"] = tendencia_mensual(ventas, "canal")
    res["prueba_estacionalidad"] = prueba_estacionalidad(ventas)
    for nombre, df in res.items():
        guardar(df, MODULO, nombre)
    return res


if __name__ == "__main__":
    pd.set_option("display.width", 220, "display.max_columns", 30)
    for nombre, df in run().items():
        print(f"\n=== {nombre} ===")
        print(df.round(3).to_string(index=False))
