"""A4: Evaluación de la Efectividad del Marketing.

Ejecutar:
    python -m retailventure_dss.analitycs.marketing_effectiveness

Produce (en data/out/resultados/marketing/ y docs/resultados/marketing/):
  - conversion_combinaciones.csv     Tasa de conversión x tipo × canal × segmento + test estadístico
  - efecto_descuento_logistico.csv   Logit multivariado: OR, IC95, p-valor del descuento
  - efectos_marginales_descuento.csv AME: puntos porcentuales de probabilidad por unidad de descuento
  - perfil_no_convertidores.csv      Comparación CRM + devoluciones entre convertidores y no-convertidores
  - hipotesis_causas_no_conversion.csv  3 hipótesis basadas en evidencia con estadístico y p-valor
  - roi_campanas.csv                 ROI bruto y ROI neto de margen por tipo de campaña

Metodología clave (ver INSTRUCCIONES_CLAUDE_A4_A5.md §3):
  - Causalidad sobre correlación: se controla por segmento, canal y tipo de campaña.
  - Pruebas de dos proporciones (Z-test) para significancia de las tasas de conversión.
  - Regresión logística con efectos fijos categoriales y errores HC1 para el efecto del descuento.
  - Efectos marginales promedio (AME) para interpretación en unidades de probabilidad.
  - ROI evaluado sobre MARGEN BRUTO REAL, no sobre venta bruta (ver nota en calcular_roi_campanas).
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from retailventure_dss.analitycs._base import (
    cargar_campanas,
    cargar_crm,
    cargar_ventas,
    guardar,
)

MODULO = "marketing"
# Ventana de atribución: días máximos entre envío de campaña y compra que se le atribuye.
VENTANA_ATRIBUCION_DIAS = 30
# SLA de respuesta CRM en horas (tomado de quality_rules.py para consistencia).
SLA_RESPUESTA_HRS = 72
# Costos operativos de envío estimados por canal (USD por impacto enviado).
COSTO_ENVIO = {"email": 0.005, "app": 0.002, "sms": 0.025}


# ──────────────────────────────────────────────────────────────────────────────
# A4.1: Tasa de conversión por tipo de campaña × canal × segmento
# ──────────────────────────────────────────────────────────────────────────────
def conversion_por_combinacion(campanas: pd.DataFrame) -> pd.DataFrame:
    """Tasas de conversión por cada combinación tipo × canal × segmento.

    Contraste estadístico: Z-test de dos proporciones contra la tasa media global
    (alfa = 0.05). Las combinaciones con < 30 envíos se marcan con 'insuficiente'
    para evitar conclusiones a partir de muestras demasiado pequeñas.
    """
    tasa_global = campanas["convertido"].mean()
    n_global = len(campanas)

    dims = ["tipo_campana", "canal_campana", "segmento"]
    g = campanas.groupby(dims).agg(
        total_envios=("campana_id", "size"),
        total_abiertas=("abierto", "sum"),
        total_convertidas=("convertido", "sum"),
    ).reset_index()

    g["open_rate"] = g["total_abiertas"] / g["total_envios"]
    g["conversion_rate_global"] = g["total_convertidas"] / g["total_envios"]
    g["conversion_rate_aperturas"] = np.where(
        g["total_abiertas"] > 0,
        g["total_convertidas"] / g["total_abiertas"],
        np.nan,
    )

    # Z-test de dos proporciones: celda vs tasa global
    filas_stat = []
    for _, r in g.iterrows():
        n = r["total_envios"]
        k = r["total_convertidas"]
        if n < 30:
            filas_stat.append({"p_valor": np.nan, "significancia": "insuficiente"})
            continue
        p_hat = k / n
        # Pooled standard error bajo H0: p_hat == tasa_global
        se = np.sqrt(tasa_global * (1 - tasa_global) / n)
        z = (p_hat - tasa_global) / se if se > 0 else np.nan
        p = 2 * (1 - stats.norm.cdf(abs(z))) if not np.isnan(z) else np.nan
        if np.isnan(p):
            sig = "insuficiente"
        elif p < 0.05 and p_hat > tasa_global:
            sig = "significativamente_superior"
        elif p < 0.05 and p_hat < tasa_global:
            sig = "significativamente_inferior"
        else:
            sig = "no_significativo"
        filas_stat.append({"p_valor": p, "significancia": sig})

    stat_df = pd.DataFrame(filas_stat)
    resultado = pd.concat([g.reset_index(drop=True), stat_df], axis=1)
    resultado.insert(0, "tasa_global_referencia", tasa_global)
    return resultado.sort_values("conversion_rate_global", ascending=False)


# ──────────────────────────────────────────────────────────────────────────────
# A4.2: Efecto del descuento ofrecido sobre la conversión (Logit multivariado)
# ──────────────────────────────────────────────────────────────────────────────
def efecto_descuento_logistico(
    campanas: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Regresión logística para aislar el efecto del descuento controlando por confusores.

    Modelos estimados:
      (1) Main effects: convertido ~ descuento_ofrecido + C(segmento) + C(canal_campana)
                        + C(tipo_campana)
      (2) Interacción: agrega descuento × segmento para capturar heterogeneidad.

    Ambos usan errores robustos HC1. Se extraen:
      - Odds Ratios e IC95% del modelo (1).
      - Average Marginal Effects (AME) del descuento del modelo (1).
    """
    df = campanas.copy()
    df["convertido_int"] = df["convertido"].astype(int)
    # Referencia: segmento más pequeño para que los efectos sean fácilmente legibles.
    df["segmento"] = df["segmento"].astype("category")
    df["canal_campana"] = df["canal_campana"].astype("category")
    df["tipo_campana"] = df["tipo_campana"].astype("category")

    # C(canal_campana) se omite porque es colineal con C(tipo_campana)
    # (cada tipo de campana se envia por un canal fijo o email).
    formula_main = (
        "convertido_int ~ descuento_ofrecido + C(segmento) + C(tipo_campana)"
    )
    formula_int = (
        "convertido_int ~ descuento_ofrecido * C(segmento) + C(tipo_campana)"
    )


    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        modelo_main = smf.logit(formula_main, data=df).fit(
            cov_type="HC1", disp=False
        )
        modelo_int = smf.logit(formula_int, data=df).fit(
            cov_type="HC1", disp=False
        )

    # ── Tabla de coeficientes + OR + IC95% (modelo main) ──────────────────────
    ci = modelo_main.conf_int()
    rows = []
    for name in modelo_main.params.index:
        rows.append(
            {
                "variable": name,
                "coeficiente": modelo_main.params[name],
                "odds_ratio": np.exp(modelo_main.params[name]),
                "ic95_inf_or": np.exp(ci.loc[name, 0]),
                "ic95_sup_or": np.exp(ci.loc[name, 1]),
                "p_valor": modelo_main.pvalues[name],
                "significativo_005": bool(modelo_main.pvalues[name] < 0.05),
            }
        )
    df_coef = pd.DataFrame(rows)

    # ── Average Marginal Effects (AME) del descuento ──────────────────────────
    margeff = modelo_main.get_margeff()
    ame_rows = []
    me_values = margeff.margeff
    me_se = margeff.margeff_se
    me_pval = margeff.pvalues
    for i, vname in enumerate(margeff.summary_frame().index):
        ame_rows.append(
            {
                "variable": vname,
                "ame": me_values[i],
                "se": me_se[i],
                "p_valor": me_pval[i],
                # Interpretación: cambio en pp de prob. conversión por +5% de descuento
                "ame_por_5pct_descuento": me_values[i] * 0.05
                if "descuento" in vname
                else np.nan,
            }
        )
    df_ame = pd.DataFrame(ame_rows)

    # ── Resumen de significancia del descuento ─────────────────────────────────
    desc_row = df_coef[df_coef["variable"] == "descuento_ofrecido"].iloc[0]
    df_coef.insert(0, "pseudo_r2_mcfadden", modelo_main.prsquared)
    df_coef.insert(0, "n_obs", int(modelo_main.nobs))

    # Marca si el descuento tiene efecto neto real tras controles
    df_ame["interpretacion_descuento"] = df_ame["variable"].apply(
        lambda v: (
            "descuento_sin_efecto_significativo"
            if "descuento" in v and desc_row["p_valor"] >= 0.05
            else (
                "descuento_incrementa_conversion"
                if "descuento" in v and desc_row["coeficiente"] > 0
                else ("descuento_reduce_conversion" if "descuento" in v else "control")
            )
        )
    )

    return {
        "efecto_descuento_logistico": df_coef,
        "efectos_marginales_descuento": df_ame,
    }


# ──────────────────────────────────────────────────────────────────────────────
# A4.3: Perfilado de no-convertidores e hipótesis causales
# ──────────────────────────────────────────────────────────────────────────────
def analizar_no_convertidores(
    campanas: pd.DataFrame,
    crm: pd.DataFrame,
    ventas: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Compara convertidores vs no-convertidores con datos de CRM y devoluciones.

    Definiciones:
      Convertidor:            cliente con >= 1 campaña convertida.
      No-convertidor         cliente con >= 1 campaña recibida y 0 conversiones.

    Tests:
      - Mann-Whitney U para variables continuas (no se asume normalidad).
      - Chi-cuadrado para proporciones (quejas, devoluciones).
    """
    # ── Perfil de conversión por cliente ────────────────────────────────────
    por_cliente = campanas.groupby("cliente_id").agg(
        total_campanas=("campana_id", "size"),
        campanas_convertidas=("convertido", "sum"),
        campanas_abiertas=("abierto", "sum"),
        segmento=("segmento", "first"),
        edad=("edad", "first"),
        genero=("genero", "first"),
        canal_adquisicion=("canal_adquisicion", "first"),
        descuento_medio_recibido=("descuento_ofrecido", "mean"),
    ).reset_index()
    por_cliente["es_convertidor"] = por_cliente["campanas_convertidas"] > 0
    por_cliente["open_rate_cliente"] = (
        por_cliente["campanas_abiertas"] / por_cliente["total_campanas"]
    )

    # ── Cruce CRM ────────────────────────────────────────────────────────────
    crm_quejas = crm[crm["tipo"] == "queja"].copy()
    crm_quejas["no_resuelta"] = (crm_quejas["resolucion"] != "resuelta") | (
        crm_quejas["tiempo_respuesta_hrs"] > SLA_RESPUESTA_HRS
    )
    crm_agg = crm_quejas.groupby("cliente_id").agg(
        total_quejas=("interaccion_id", "size"),
        quejas_no_resueltas=("no_resuelta", "sum"),
        tiempo_promedio_respuesta=("tiempo_respuesta_hrs", "mean"),
    ).reset_index()
    crm_agg["tuvo_quejas"] = True

    # ── Cruce Devoluciones ───────────────────────────────────────────────────
    dev_agg = ventas[ventas["devuelta"]].groupby("cliente_id").agg(
        devoluciones_totales=("transaccion_id", "size"),
        monto_devuelto_acumulado=("monto_devuelto", "sum"),
    ).reset_index()
    dev_agg["tuvo_devolucion"] = True

    # Transacciones totales por cliente (para calcular tasa de devolución)
    trx_por_cliente = ventas.groupby("cliente_id").agg(
        transacciones_totales=("transaccion_id", "size"),
    ).reset_index()

    # ── Merge todo ───────────────────────────────────────────────────────────
    perfil = (
        por_cliente
        .merge(crm_agg, on="cliente_id", how="left")
        .merge(dev_agg, on="cliente_id", how="left")
        .merge(trx_por_cliente, on="cliente_id", how="left")
    )
    perfil["total_quejas"] = perfil["total_quejas"].fillna(0).astype(int)
    perfil["quejas_no_resueltas"] = perfil["quejas_no_resueltas"].fillna(0).astype(int)
    perfil["tuvo_quejas"] = perfil["tuvo_quejas"].fillna(False)
    perfil["tuvo_devolucion"] = perfil["tuvo_devolucion"].fillna(False)
    perfil["devoluciones_totales"] = perfil["devoluciones_totales"].fillna(0).astype(int)
    perfil["monto_devuelto_acumulado"] = perfil["monto_devuelto_acumulado"].fillna(0.0)
    perfil["transacciones_totales"] = perfil["transacciones_totales"].fillna(0).astype(int)
    perfil["tasa_devolucion_cliente"] = np.where(
        perfil["transacciones_totales"] > 0,
        perfil["devoluciones_totales"] / perfil["transacciones_totales"],
        np.nan,
    )

    # ── Pruebas de hipótesis ─────────────────────────────────────────────────
    conv = perfil[perfil["es_convertidor"]]
    noconv = perfil[~perfil["es_convertidor"]]

    def mwu(col: str) -> tuple[float, float]:
        """Mann-Whitney U entre convertidores y no-convertidores para `col`."""
        a = conv[col].dropna()
        b = noconv[col].dropna()
        if len(a) < 5 or len(b) < 5:
            return np.nan, np.nan
        u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        return float(u), float(p)

    def chi2_prop(col: str) -> tuple[float, float]:
        """Chi-cuadrado para variable binaria `col`."""
        tabla = pd.crosstab(perfil["es_convertidor"], perfil[col])
        if tabla.shape == (2, 2):
            chi, p, _, _ = stats.chi2_contingency(tabla)
            return float(chi), float(p)
        return np.nan, np.nan

    hipotesis = []
    # H1: Fricción post-venta (quejas no resueltas)
    u1, p1 = mwu("quejas_no_resueltas")
    mediana_noconv_quejas = noconv["quejas_no_resueltas"].median()
    mediana_conv_quejas = conv["quejas_no_resueltas"].median()
    hipotesis.append({
        "hipotesis": "H1: No-convertidores tienen más quejas no resueltas que bloquean el re-engagement",
        "variable_test": "quejas_no_resueltas",
        "estadistico": "Mann-Whitney U",
        "valor_estadistico": u1,
        "p_valor": p1,
        "confirmada_005": bool(p1 < 0.05) if not np.isnan(p1) else False,
        "mediana_convertidores": mediana_conv_quejas,
        "mediana_no_convertidores": mediana_noconv_quejas,
        "interpretacion": (
            "Confirmada: los no-convertidores tienen mayor carga de quejas no resueltas"
            if (not np.isnan(p1) and p1 < 0.05 and mediana_noconv_quejas > mediana_conv_quejas)
            else "No confirmada estadísticamente"
        ),
    })

    # H2: Experiencia deficiente de producto (devoluciones previas)
    chi2_d, p2 = chi2_prop("tuvo_devolucion")
    pct_noconv_dev = noconv["tuvo_devolucion"].mean() * 100
    pct_conv_dev = conv["tuvo_devolucion"].mean() * 100
    hipotesis.append({
        "hipotesis": "H2: No-convertidores tuvieron más devoluciones previas (mala experiencia de producto)",
        "variable_test": "tuvo_devolucion",
        "estadistico": "Chi-cuadrado",
        "valor_estadistico": chi2_d,
        "p_valor": p2,
        "confirmada_005": bool(p2 < 0.05) if not np.isnan(p2) else False,
        "mediana_convertidores": pct_conv_dev,
        "mediana_no_convertidores": pct_noconv_dev,
        "interpretacion": (
            "Confirmada: proporción de devolvedores es mayor en no-convertidores"
            if (not np.isnan(p2) and p2 < 0.05 and pct_noconv_dev > pct_conv_dev)
            else "No confirmada estadísticamente"
        ),
    })

    # H3: Desalineación canal/segmento (tasa de apertura)
    u3, p3 = mwu("open_rate_cliente")
    mediana_noconv_or = noconv["open_rate_cliente"].median()
    mediana_conv_or = conv["open_rate_cliente"].median()
    hipotesis.append({
        "hipotesis": "H3: No-convertidores tienen menor open_rate (desalineación canal-segmento)",
        "variable_test": "open_rate_cliente",
        "estadistico": "Mann-Whitney U",
        "valor_estadistico": u3,
        "p_valor": p3,
        "confirmada_005": bool(p3 < 0.05) if not np.isnan(p3) else False,
        "mediana_convertidores": mediana_conv_or,
        "mediana_no_convertidores": mediana_noconv_or,
        "interpretacion": (
            "Confirmada: los no-convertidores abren menos los mensajes antes de decidir"
            if (not np.isnan(p3) and p3 < 0.05 and mediana_noconv_or < mediana_conv_or)
            else "No confirmada estadísticamente"
        ),
    })

    df_hip = pd.DataFrame(hipotesis)

    return {
        "perfil_no_convertidores": perfil,
        "hipotesis_causas_no_conversion": df_hip,
    }


# ──────────────────────────────────────────────────────────────────────────────
# A4.4: ROI por tipo de campaña (sobre margen bruto real, no venta bruta)
# ──────────────────────────────────────────────────────────────────────────────
def calcular_roi_campanas(
    campanas: pd.DataFrame,
    ventas: pd.DataFrame,
) -> pd.DataFrame:
    """ROI estimado por tipo de campaña usando atribución first-touch.

    Ventana de atribución: primera compra del cliente dentro de los
    VENTANA_ATRIBUCION_DIAS días posteriores al envío de la campaña.

    Dos perspectivas de ROI (ver §3.5 de INSTRUCCIONES_CLAUDE_A4_A5.md):
      ROI_bruto  = (Ventas atribuidas - Costo descuento campaña) / Costo descuento campaña
      ROI_margen = (Margen bruto atribuido - Costo total [descuento + envío]) / Costo total

    NOTA CRÍTICA: el costo del descuento aquí es el descuento ofrecido en la campaña
    convertido a USD usando el monto de la compra atribuida. No es el descuento de la
    transacción (ya capturado en margen), sino el subsidio de marketing al precio de venta.
    """
    ventas_base = ventas[["cliente_id", "fecha", "transaccion_id",
                           "monto_neto", "margen", "descuento"]].copy()
    campanas_conv = campanas[campanas["convertido"]].copy()

    filas = []
    for _, cam in campanas_conv.iterrows():
        cliente = cam["cliente_id"]
        fecha_envio = cam["fecha_envio"]
        ventana_fin = fecha_envio + pd.Timedelta(days=VENTANA_ATRIBUCION_DIAS)
        compras_ventana = ventas_base[
            (ventas_base["cliente_id"] == cliente)
            & (ventas_base["fecha"] >= fecha_envio)
            & (ventas_base["fecha"] <= ventana_fin)
        ].sort_values("fecha")
        if compras_ventana.empty:
            continue
        primera = compras_ventana.iloc[0]
        costo_descuento_campana = cam["descuento_ofrecido"] * primera["monto_neto"]
        canal_key = cam["canal_campana"].lower().split("_")[-1]  # 'email', 'app', 'sms'
        costo_envio = COSTO_ENVIO.get(canal_key, COSTO_ENVIO["email"])
        filas.append(
            {
                "campana_id": cam["campana_id"],
                "tipo_campana": cam["tipo_campana"],
                "canal_campana": cam["canal_campana"],
                "segmento": cam["segmento"],
                "monto_compra_atribuida": primera["monto_neto"],
                "margen_bruto_atribuido": primera["margen"],
                "costo_descuento_campana": costo_descuento_campana,
                "costo_envio": costo_envio,
                "costo_total": costo_descuento_campana + costo_envio,
            }
        )

    if not filas:
        return pd.DataFrame()

    df_attr = pd.DataFrame(filas)

    # Agregar por tipo de campaña
    g = df_attr.groupby("tipo_campana").agg(
        campanas_convertidas=("campana_id", "size"),
        monto_total_atribuido=("monto_compra_atribuida", "sum"),
        margen_total_atribuido=("margen_bruto_atribuido", "sum"),
        costo_descuento_total=("costo_descuento_campana", "sum"),
        costo_envio_total=("costo_envio", "sum"),
        costo_total=("costo_total", "sum"),
        ticket_medio_atribuido=("monto_compra_atribuida", "mean"),
        margen_medio_atribuido=("margen_bruto_atribuido", "mean"),
    ).reset_index()

    g["roi_bruto"] = np.where(
        g["costo_descuento_total"] > 0,
        (g["monto_total_atribuido"] - g["costo_descuento_total"]) / g["costo_descuento_total"],
        np.nan,
    )
    g["roi_neto_margen"] = np.where(
        g["costo_total"] > 0,
        (g["margen_total_atribuido"] - g["costo_total"]) / g["costo_total"],
        np.nan,
    )
    g["margen_pct_sobre_venta"] = g["margen_total_atribuido"] / g["monto_total_atribuido"]
    g["nota"] = (
        "ROI_bruto sobre venta bruta - críticamente infla efectividad. "
        "ROI_neto_margen es la métrica BI correcta: incorpora costo del descuento "
        "y costo operativo de envío estimado."
    )
    return g.sort_values("roi_neto_margen", ascending=False)


# ──────────────────────────────────────────────────────────────────────────────
# Pipeline principal
# ──────────────────────────────────────────────────────────────────────────────
def run() -> dict[str, pd.DataFrame]:
    campanas = cargar_campanas()
    crm = cargar_crm()
    ventas = cargar_ventas()

    resultados: dict[str, pd.DataFrame] = {}

    # A4.1
    resultados["conversion_combinaciones"] = conversion_por_combinacion(campanas)

    # A4.2
    resultados.update(efecto_descuento_logistico(campanas))

    # A4.3
    resultados.update(analizar_no_convertidores(campanas, crm, ventas))

    # A4.4
    resultados["roi_campanas"] = calcular_roi_campanas(campanas, ventas)

    for nombre, df in resultados.items():
        guardar(df, MODULO, nombre)

    return resultados


if __name__ == "__main__":
    pd.set_option("display.width", 220, "display.max_columns", 30)
    for nombre, df in run().items():
        print(f"\n{'=' * 60}")
        print(f"  {nombre}  ({len(df)} filas)")
        print("=" * 60)
        print(df.round(4).to_string(index=False))
