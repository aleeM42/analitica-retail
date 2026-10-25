"""A3 (cierre): validación del modelo de churn e impacto consolidado de las fugas a 6 meses.

Ejecutar: python -m retailventure_dss.analitycs.fugas

Produce (en data/out/resultados/fugas/):
  - churn_backtest_por_estado.csv       ¿los clientes marcados realmente dejaron de comprar?
  - churn_backtest_en_riesgo_por_segmento.csv
  - fugas_impacto_6m.csv                tabla única de ingresos perdidos proyectados a 6 meses
"""

import numpy as np
import pandas as pd

from retailventure_dss.analitycs._base import cargar_clientes, cargar_ventas, guardar
from retailventure_dss.analitycs.clv_churn import HORIZONTE_DIAS, clasificar_churn
from retailventure_dss.analitycs.return_anomalies import tasas_vs_base

MODULO = "fugas"
FECHA_CORTE_BACKTEST = "2024-06-30"  # deja 6 meses completos de "futuro" (jul-dic 2024)
SEMESTRES_EN_VENTANA = 4             # 24 meses de historia = 4 semestres


# --------------------------------------------------------------------------------------
# 1. Backtest del churn: clasificar con datos hasta el corte y mirar qué pasó después
# --------------------------------------------------------------------------------------
def validar_churn(
    ventas: pd.DataFrame, clientes: pd.DataFrame, corte: str = FECHA_CORTE_BACKTEST
) -> dict[str, pd.DataFrame]:
    corte_ts = pd.Timestamp(corte)
    pasado = ventas[ventas["fecha"] <= corte_ts]
    futuro = ventas[
        (ventas["fecha"] > corte_ts) & (ventas["fecha"] <= corte_ts + pd.Timedelta(days=HORIZONTE_DIAS))
    ]
    t = clasificar_churn(pasado, clientes[clientes["fecha_registro"] <= corte_ts], fin=corte_ts)
    t["volvio"] = t["cliente_id"].isin(set(futuro["cliente_id"]))

    por_estado = t.groupby("estado").agg(
        clientes=("cliente_id", "size"),
        pct_volvio_real=("volvio", "mean"),
        pct_no_retorno_predicho=("prob_no_retorno_6m", "mean"),
    )
    por_estado["pct_no_retorno_real"] = 1 - por_estado["pct_volvio_real"]
    por_estado = (por_estado * [1, 100, 100, 100]).round(1).reset_index()

    riesgo = t[t["estado"] == "En riesgo"]
    por_segmento = riesgo.groupby("segmento").agg(
        clientes=("cliente_id", "size"),
        pct_volvio_real=("volvio", "mean"),
        pct_no_retorno_predicho=("prob_no_retorno_6m", "mean"),
    )
    por_segmento["pct_no_retorno_real"] = 1 - por_segmento["pct_volvio_real"]
    por_segmento = (por_segmento * [1, 100, 100, 100]).round(1).reset_index()
    return {
        "churn_backtest_por_estado": por_estado.assign(corte=corte),
        "churn_backtest_en_riesgo_por_segmento": por_segmento.assign(corte=corte),
    }


# --------------------------------------------------------------------------------------
# 2. Impacto consolidado a 6 meses
# --------------------------------------------------------------------------------------
def _devoluciones_en_exceso(ventas: pd.DataFrame) -> dict[str, float]:
    """Si las categorías con tasa anómalamente alta devolvieran como el resto de categorías."""
    cat = tasas_vs_base(ventas, "categoria")
    monto = margen_conservador = margen_optimista = 0.0
    detalle = []
    for _, r in cat[cat["anomalo_alto"]].iterrows():
        c = r["categoria"]
        tasa_ref = ventas.loc[ventas["categoria"] != c, "devuelta"].mean()
        dev = ventas[(ventas["categoria"] == c) & ventas["devuelta"]]
        exceso_n = max(r["devoluciones"] - tasa_ref * r["transacciones"], 0.0)
        m = exceso_n * dev["monto_devuelto"].mean()
        monto += m
        margen_conservador += m  # la mercancía devuelta se pierde: evitar la devolución recupera todo
        margen_optimista += m - exceso_n * dev["costo_devuelto"].mean()  # mercancía se revende al costo
        detalle.append(c)
    return {
        "ingreso_24m": monto,
        "margen_conservador_24m": margen_conservador,
        "margen_optimista_24m": margen_optimista,
        "categorias": ", ".join(detalle),
    }


def tabla_fugas_6m(ventas: pd.DataFrame, t_churn: pd.DataFrame) -> pd.DataFrame:
    """Una fila por fuga, todas expresadas en ingresos proyectados a 6 meses (USD)."""
    ingreso_semestre = ventas["monto_neto"].sum() / SEMESTRES_EN_VENTANA
    filas = []

    # a) Devoluciones por encima de lo normal
    d = _devoluciones_en_exceso(ventas)
    filas.append(
        {
            "fuga": "Devoluciones en exceso (" + d["categorias"] + ")",
            "ingreso_6m": d["ingreso_24m"] / SEMESTRES_EN_VENTANA,
            "rango_bajo": np.nan,
            "rango_alto": np.nan,
            "margen_6m_conservador": d["margen_conservador_24m"] / SEMESTRES_EN_VENTANA,
            "margen_6m_optimista": d["margen_optimista_24m"] / SEMESTRES_EN_VENTANA,
            "nota": "Ingreso que se conservaría si esas categorías devolvieran como el resto. "
                    "Margen: conservador = mercancía devuelta se pierde; optimista = se revende al costo.",
        }
    )

    # b) Churn: titular = pérdida esperada ponderada; rango = [atribuible a inactividad, expuesto]
    r = t_churn[t_churn["estado"] == "En riesgo"]
    perdida = r["ingreso_esperado_perdido_6m"].sum()
    margen = (r["ingreso_esperado_perdido_6m"] * r["margen_pct_segmento"]).sum()
    filas.append(
        {
            "fuga": f"Churn ({len(r)} clientes 'En riesgo')",
            "ingreso_6m": perdida,
            "rango_bajo": r["ingreso_perdido_incremental_6m"].sum(),
            "rango_alto": r["ingreso_esperado_6m"].sum(),
            "margen_6m_conservador": margen,
            "margen_6m_optimista": margen,
            "nota": "Titular = ingreso esperado x prob. de no retorno. Bajo = solo la parte atribuible "
                    "a la inactividad prolongada. Alto = escenario donde NADIE vuelve (no realista: ver backtest).",
        }
    )

    # c) CRM: se reporta honestamente que no hay efecto demostrable
    filas.append(
        {
            "fuga": "Quejas sin resolver (CRM)",
            "ingreso_6m": np.nan,
            "rango_bajo": np.nan,
            "rango_alto": np.nan,
            "margen_6m_conservador": np.nan,
            "margen_6m_optimista": np.nan,
            "nota": "Sin efecto demostrable sobre la frecuencia de compra (IC95 incluye 0). "
                    "No se cuantifica; ver efecto_minimo_detectable en crm_efecto_ajustado.csv.",
        }
    )

    # d) Descuentos (A2): la mayor fuga de margen; el descuento sale directo del margen
    bruto = ventas["precio_unitario"] * ventas["cantidad"]
    desc = (bruto * ventas["descuento"]).sum() / SEMESTRES_EN_VENTANA
    filas.append(
        {
            "fuga": "Descuentos sin efecto en volumen (A2)",
            "ingreso_6m": desc,
            "rango_bajo": np.nan,
            "rango_alto": np.nan,
            "margen_6m_conservador": desc,
            "margen_6m_optimista": desc,
            "nota": "Techo: supone que sin descuento no se pierde volumen (efecto estimado ~0, "
                    "ver efecto_volumen_efectos_fijos.csv). Validar con un piloto antes de eliminarlos.",
        }
    )

    out = pd.DataFrame(filas)
    out["pct_ingreso_semestral"] = out["ingreso_6m"] / ingreso_semestre * 100
    return out[["fuga", "ingreso_6m", "pct_ingreso_semestral", "rango_bajo", "rango_alto",
                "margen_6m_conservador", "margen_6m_optimista", "nota"]]


def run() -> dict[str, pd.DataFrame]:
    ventas, clientes = cargar_ventas(), cargar_clientes()
    res = validar_churn(ventas, clientes)
    res["fugas_impacto_6m"] = tabla_fugas_6m(ventas, clasificar_churn(ventas, clientes))
    for nombre, df in res.items():
        guardar(df, MODULO, nombre)
    return res


if __name__ == "__main__":
    pd.set_option("display.width", 250, "display.max_columns", 30, "display.max_colwidth", 60)
    for nombre, df in run().items():
        print(f"\n=== {nombre} ===")
        print(df.drop(columns=["nota"], errors="ignore").round(1).to_string(index=False))
