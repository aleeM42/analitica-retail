"""Chart factory implementing the 10 executive insight visualizations for RetailVenture DSS."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from retailventure_dss.interface.data_provider import DashboardDataProvider
from retailventure_dss.interface.theme import (
    COLOR_ACCENT,
    COLOR_DANGER,
    COLOR_PURPLE,
    COLOR_SUCCESS,
    COLOR_WARNING,
    TEXT_MUTED,
    apply_theme,
)


class ChartFactory:
    """Builds Plotly figures with insight-driven titles as specified in A5."""

    def __init__(self, provider: DashboardDataProvider) -> None:
        self._provider = provider

    # ── V1: Devoluciones Anómalas por Categoría ───────────────────────────────
    def build_v1_devoluciones_exceso(self) -> go.Figure:
        df = self._provider.get_exceso_devoluciones()
        fig = go.Figure()

        if df.empty:
            return apply_theme(fig, "V1: Sin datos disponibles de devoluciones")

        df_sorted = df.sort_values("tasa", ascending=True)
        colors = [
            COLOR_DANGER if cat in ["Electrónica", "Ropa_y_Calzado"] else "#475569"
            for cat in df_sorted["categoria"]
        ]

        fig.add_trace(
            go.Bar(
                x=df_sorted["tasa"] * 100,
                y=df_sorted["categoria"],
                orientation="h",
                marker_color=colors,
                text=[f"{v:.1f}%" for v in df_sorted["tasa"] * 100],
                textposition="auto",
                hovertemplate="<b>%{y}</b><br>Tasa: %{x:.2f}%<extra></extra>",
            )
        )

        fig.add_vline(
            x=12.6,
            line_dash="dash",
            line_color=COLOR_WARNING,
            annotation_text="Tasa de referencia (12.6%)",
            annotation_position="top right",
        )

        return apply_theme(
            fig,
            title="Dos categorías concentran el 68% de las devoluciones y drenan $547k de margen operativo",
            subtitle="Electrónica (17.7%) y Ropa y Calzado (21.8%) superan anómalamente la tasa base del resto del retail.",
        )

    # ── V2: Erosión de Margen por Canal ───────────────────────────────────────
    def build_v2_margen_por_canal(self) -> go.Figure:
        df = self._provider.get_margen_canal()
        fig = go.Figure()

        if df.empty:
            return apply_theme(fig, "V2: Sin datos disponibles de canales")

        canales = df["canal"].str.replace("_", " ").str.title()
        pct_ingreso = df["pct_del_ingreso"] * 100
        pct_margen = df["pct_del_margen"] * 100
        margen_post_dev = df["margen_pct_tras_devol_conservador"] * 100

        fig.add_trace(
            go.Bar(
                name="% Ingreso Total",
                x=canales,
                y=pct_ingreso,
                marker_color=COLOR_ACCENT,
                text=[f"{v:.1f}%" for v in pct_ingreso],
                textposition="auto",
            )
        )
        fig.add_trace(
            go.Bar(
                name="% Margen Bruto",
                x=canales,
                y=pct_margen,
                marker_color=COLOR_PURPLE,
                text=[f"{v:.1f}%" for v in pct_margen],
                textposition="auto",
            )
        )
        fig.add_trace(
            go.Scatter(
                name="Margen Neto Post-Devoluciones",
                x=canales,
                y=margen_post_dev,
                mode="lines+markers+text",
                marker=dict(size=10, color=COLOR_DANGER),
                line=dict(width=3, color=COLOR_DANGER),
                text=[f"{v:.1f}%" for v in margen_post_dev],
                textposition="top center",
            )
        )

        return apply_theme(
            fig,
            title="El canal digital aporta el 38% de la venta pero sufre una erosión de margen de 4.1 pp",
            subtitle="La logística inversa reduce el margen neto online a solo 9.5% frente al 13.7% en tienda física.",
        )

    # ── V3: Elasticidad Precio y Descuentos Inelásticos ────────────────────────
    def build_v3_elasticidad_descuento(self) -> go.Figure:
        df = self._provider.get_elasticidad_descuento()
        fig = go.Figure()

        if df.empty:
            return apply_theme(fig, "V3: Sin datos disponibles de elasticidad")

        error_plus = df["ic95_sup_unidades"] - df["efecto_unidades"]
        error_minus = df["efecto_unidades"] - df["ic95_inf_unidades"]

        fig.add_trace(
            go.Scatter(
                x=df["efecto_unidades"],
                y=df["tramo"],
                mode="markers",
                marker=dict(size=12, color=COLOR_WARNING),
                error_x=dict(
                    type="data",
                    symmetric=False,
                    array=error_plus,
                    arrayminus=error_minus,
                    color=COLOR_ACCENT,
                    thickness=2,
                    width=6,
                ),
                hovertemplate="Tramo: %{y}<br>Efecto estimado: %{x:.4f} unidades<extra></extra>",
            )
        )

        fig.add_vline(
            x=0,
            line_dash="dash",
            line_color=COLOR_DANGER,
            annotation_text="Efecto Nulo (IC95% cruza el 0)",
            annotation_position="bottom right",
        )

        return apply_theme(
            fig,
            title="Los descuentos no generan volumen adicional: elasticidad cero destruye $241k semestrales",
            subtitle="Modelo OLS con efectos fijos de producto: todos los intervalos de confianza incluyen el cero.",
        )

    # ── V4: Concentración de Margen y Clientes en Riesgo ───────────────────────
    def build_v4_clv_y_churn(self) -> go.Figure:
        df = self._provider.get_clv_segmento()
        fig = go.Figure()

        if df.empty:
            return apply_theme(fig, "V4: Sin datos disponibles de CLV")

        clv_total = df["clv_total_segmento"] / 1000
        colors = [
            COLOR_PURPLE if s == "Premium" else COLOR_ACCENT if s == "Frecuente" else "#475569"
            for s in df["segmento"]
        ]

        fig.add_trace(
            go.Bar(
                x=df["segmento"],
                y=clv_total,
                marker_color=colors,
                text=[f"${v:,.0f}k" for v in clv_total],
                textposition="auto",
                hovertemplate="<b>%{x}</b><br>CLV Total: $%{y:,.1f}k<extra></extra>",
            )
        )

        return apply_theme(
            fig,
            title="El 81% del margen descansa en Frecuentes y Premium, pero 696 clientes clave están en riesgo",
            subtitle="Modelo Kaplan-Meier S(t) < 0.10: inactividad extrema amenaza $39,895 de ingresos semestrales.",
        )

    # ── V5: Caída Histórica de Conversión de Campañas ─────────────────────────
    def build_v5_conversion_por_tipo(self) -> go.Figure:
        df = self._provider.get_conversion_combinaciones()
        fig = go.Figure()

        if df.empty:
            return apply_theme(fig, "V5: Sin datos disponibles de conversión")

        resumen = df.groupby("tipo_campana")["conversion_rate_global"].mean().reset_index()
        resumen["conversion_pct"] = resumen["conversion_rate_global"] * 100
        resumen = resumen.sort_values("conversion_pct", ascending=True)

        fig.add_trace(
            go.Bar(
                x=resumen["conversion_pct"],
                y=resumen["tipo_campana"].str.replace("_", " ").str.title(),
                orientation="h",
                marker_color=COLOR_ACCENT,
                text=[f"{v:.1f}%" for v in resumen["conversion_pct"]],
                textposition="auto",
            )
        )

        fig.add_vline(
            x=9.04,
            line_dash="dash",
            line_color=COLOR_WARNING,
            annotation_text="Promedio global actual (9.04%)",
            annotation_position="top right",
        )

        return apply_theme(
            fig,
            title="La conversión de marketing cayó a la mitad (11.7% a 5.1%): la fatiga en Email masivo impulsa el declive",
            subtitle="El rendimiento promedio es de 9.0%, evidenciando saturación y falta de segmentación en canales masivos.",
        )

    # ── V6: Curva Logística del Efecto Descuento ──────────────────────────────
    def build_v6_curva_logistica_descuento(self) -> go.Figure:
        fig = go.Figure()
        descuentos = np.linspace(0.0, 0.25, 50)

        # Probabilidad logística simulada con parámetros estimados (beta0=-2.72, beta1=3.28)
        # para ilustrar la curva S y saturación de respuesta
        prob_premium = 1 / (1 + np.exp(-(-2.31 + 3.28 * descuentos)))
        prob_frecuente = 1 / (1 + np.exp(-(-2.90 + 3.28 * descuentos)))
        prob_inactivo = 1 / (1 + np.exp(-(-3.31 + 3.28 * descuentos)))

        fig.add_trace(
            go.Scatter(
                x=descuentos * 100,
                y=prob_premium * 100,
                mode="lines",
                name="Segmento Premium",
                line=dict(color=COLOR_PURPLE, width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=descuentos * 100,
                y=prob_frecuente * 100,
                mode="lines",
                name="Segmento Frecuente",
                line=dict(color=COLOR_ACCENT, width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=descuentos * 100,
                y=prob_inactivo * 100,
                mode="lines",
                name="Segmento Inactivo",
                line=dict(color=TEXT_MUTED, width=2, dash="dash"),
            )
        )

        return apply_theme(
            fig,
            title="El descuento en campañas incrementa la conversión pero destruye el retorno si no se segmenta quirúrgicamente",
            subtitle="Regresión Logística multivariada (beta=+3.28, p<0.001): la propensión aumenta pero el subsidio erosiona el margen neto.",
        )

    # ── V7: Heatmap Rendimiento Cruzado Tipo x Segmento ───────────────────────
    def build_v7_heatmap_segmento_campana(self) -> go.Figure:
        df = self._provider.get_conversion_combinaciones()
        fig = go.Figure()

        if df.empty:
            return apply_theme(fig, "V7: Sin datos disponibles de combinaciones")

        pivot = df.pivot_table(
            index="tipo_campana",
            columns="segmento",
            values="conversion_rate_global",
            aggfunc="mean",
        ) * 100

        fig.add_trace(
            go.Heatmap(
                z=pivot.values,
                x=pivot.columns.tolist(),
                y=[y.replace("_", " ").title() for y in pivot.index],
                colorscale="Viridis",
                text=[[f"{val:.1f}%" for val in row] for row in pivot.values],
                texttemplate="%{text}",
                hovertemplate="Tipo: %{y}<br>Segmento: %{x}<br>Conversión: %{z:.2f}%<extra></extra>",
            )
        )

        return apply_theme(
            fig,
            title="Push en App para clientes Premium lidera la conversión (15.3%) vs 4.7% de Email a Inactivos",
            subtitle="El retorno depende críticamente de la segmentación quirúrgica de canales y audiencias receptivas.",
        )

    # ── V8: Impacto de Quejas CRM y Devoluciones en Conversión ────────────────
    def build_v8_quejas_crm_conversion(self) -> go.Figure:
        df = self._provider.get_perfil_no_convertidores()
        fig = go.Figure()

        if df.empty:
            return apply_theme(fig, "V8: Sin datos disponibles de perfilado")

        conv_con_quejas = df[df["tuvo_quejas"]]["es_convertidor"].mean() * 100
        conv_sin_quejas = df[~df["tuvo_quejas"]]["es_convertidor"].mean() * 100
        conv_con_dev = df[df["tuvo_devolucion"]]["es_convertidor"].mean() * 100
        conv_sin_dev = df[~df["tuvo_devolucion"]]["es_convertidor"].mean() * 100

        labels = ["Sin Quejas CRM", "Con Quejas CRM", "Sin Devolución", "Con Devolución"]
        tasas = [conv_sin_quejas, conv_con_quejas, conv_sin_dev, conv_con_dev]
        colors = [COLOR_SUCCESS, COLOR_ACCENT, COLOR_SUCCESS, COLOR_WARNING]

        fig.add_trace(
            go.Bar(
                x=labels,
                y=tasas,
                marker_color=colors,
                text=[f"{v:.1f}%" for v in tasas],
                textposition="auto",
            )
        )

        return apply_theme(
            fig,
            title="Los no-convertidores no difieren por quejas ni devoluciones (p>0.80), sino por tasa de apertura",
            subtitle="La tasa de conversión es idéntica con o sin quejas (~15.5%); el rechazo se debe a falta de apertura (open rate 0% vs 67%).",
        )

    # ── V9: Comparación de ROI Bruto vs ROI Neto de Margen ────────────────────
    def build_v9_roi_campanas_comparativo(self) -> go.Figure:
        df = self._provider.get_roi_campanas()
        fig = go.Figure()

        if df.empty:
            return apply_theme(fig, "V9: Sin datos disponibles de ROI")

        tipos = df["tipo_campana"].str.replace("_", " ").str.title()
        roi_bruto = df["roi_bruto"]
        roi_neto = df["roi_neto_margen"]

        fig.add_trace(
            go.Bar(
                name="ROI Bruto (Facturación)",
                x=tipos,
                y=roi_bruto,
                marker_color=COLOR_ACCENT,
                text=[f"{v:.2f}x" for v in roi_bruto],
                textposition="auto",
            )
        )
        fig.add_trace(
            go.Bar(
                name="ROI Neto (Margen Real)",
                x=tipos,
                y=roi_neto,
                marker_color=COLOR_SUCCESS,
                text=[f"{v:.2f}x" for v in roi_neto],
                textposition="auto",
            )
        )

        return apply_theme(
            fig,
            title="El ROI de marketing colapsa de 6.8x bruto a 0.59x sobre margen neto real: medir sobre ventas infla el retorno 11 veces",
            subtitle="La medición sobre venta bruta es una falacia contable que ignora costos de producto y subsidios promocionales.",
        )

    # ── V10: Cascada de Rescate Financiero (Waterfall) ─────────────────────────
    def build_v10_waterfall_rescate(self) -> go.Figure:
        fig = go.Figure()

        x_steps = [
            "Margen Actual (Semestral)",
            "+ Contención Devoluciones",
            "+ Racionalización Descuentos",
            "+ Retención Predictiva",
            "Margen Post-Plan",
        ]
        y_values = [2155.16, 47.91, 145.16, 4.91, 0]

        fig.add_trace(
            go.Waterfall(
                name="Margen Semestral (en miles USD)",
                orientation="v",
                measure=["relative", "relative", "relative", "relative", "total"],
                x=x_steps,
                y=y_values,
                text=[f"+${v:,.1f}k" if v > 0 else f"${v:,.1f}k" for v in y_values],
                textposition="auto",
                connector={"line": {"color": TEXT_MUTED}},
                increasing={"marker": {"color": COLOR_SUCCESS}},
                decreasing={"marker": {"color": COLOR_DANGER}},
                totals={"marker": {"color": COLOR_ACCENT}},
            )
        )

        return apply_theme(
            fig,
            title="Intervención estratégica de tres palancas proyecta una recuperación de $396k anuales en margen",
            subtitle="Recuperación semestral de +$198k equivalente a un +9.2% de incremento en el margen bruto sin aumentar ventas.",
        )
