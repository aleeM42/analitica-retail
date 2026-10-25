"""Plotly Dash Executive Dashboard application for RetailVenture DSS."""

from __future__ import annotations

import sys
from dash import Dash, dcc, html

from retailventure_dss.interface.charts import ChartFactory
from retailventure_dss.interface.data_provider import DashboardDataProvider
from retailventure_dss.interface.theme import (
    BG_APP,
    COLOR_ACCENT,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_WARNING,
    FONT_FAMILY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    get_card_style,
)


def _build_kpi_card(title: str, value: str, note: str, color: str = COLOR_ACCENT) -> html.Div:
    """Builds a single executive metric KPI card."""
    return html.Div(
        style=get_card_style({"flex": "1", "minWidth": "220px", "borderLeft": f"4px solid {color}"}),
        children=[
            html.Div(title, style={"fontSize": "12px", "color": TEXT_MUTED, "textTransform": "uppercase", "letterSpacing": "0.05em"}),
            html.Div(value, style={"fontSize": "26px", "fontWeight": "bold", "color": color, "margin": "8px 0"}),
            html.Div(note, style={"fontSize": "11px", "color": TEXT_MUTED}),
        ],
    )


def create_app() -> Dash:
    """Initializes and configures the Dash application."""
    provider = DashboardDataProvider()
    factory = ChartFactory(provider)
    kpis = provider.get_executive_kpis()

    app = Dash(__name__, title="RetailVenture C.A. | Executive DSS")

    tab_style = {
        "backgroundColor": "#1e293b",
        "color": TEXT_MUTED,
        "padding": "12px 20px",
        "border": "none",
        "borderRadius": "6px",
        "marginRight": "8px",
        "cursor": "pointer",
    }
    selected_tab_style = {
        "backgroundColor": COLOR_ACCENT,
        "color": "#090d16",
        "fontWeight": "bold",
        "padding": "12px 20px",
        "border": "none",
        "borderRadius": "6px",
        "marginRight": "8px",
    }

    app.layout = html.Div(
        style={
            "backgroundColor": BG_APP,
            "minHeight": "100vh",
            "padding": "24px 36px",
            "fontFamily": FONT_FAMILY,
            "color": TEXT_PRIMARY,
        },
        children=[
            # ── Header ───────────────────────────────────────────────────────
            html.Div(
                style={"marginBottom": "24px", "display": "flex", "justifyContent": "space-between", "alignItems": "flex-end"},
                children=[
                    html.Div([
                        html.H1("RetailVenture C.A. — Sistema de Soporte de Decisiones (DSS)", style={"margin": "0 0 6px 0", "fontSize": "24px", "fontWeight": "700"}),
                        html.P("Márgenes en Crisis: Storytelling Ejecutivo y Plan de Rescate Financiero | Tópicos Especiales para la Gestión de Datos", style={"margin": "0", "color": TEXT_MUTED, "fontSize": "13px"}),
                    ]),
                    html.Div([
                        html.Span("Auditoría A1-A5 | 24 Meses", style={"backgroundColor": "#1e293b", "color": COLOR_ACCENT, "padding": "6px 12px", "borderRadius": "4px", "fontSize": "12px", "fontWeight": "600"}),
                    ]),
                ],
            ),

            # ── Headline KPIs ─────────────────────────────────────────────────
            html.Div(
                style={"display": "flex", "gap": "16px", "marginBottom": "24px", "flexWrap": "wrap"},
                children=[
                    _build_kpi_card("Facturación 24M", kpis["ingreso_total"], "50,000 transacciones operativas", COLOR_ACCENT),
                    _build_kpi_card("Margen Bruto", kpis["margen_bruto"], "$4.31M sobre ventas brutas", COLOR_SUCCESS),
                    _build_kpi_card("Fuga Anual Identificada", kpis["fuga_recuperable"], "Devoluciones + Descuentos inelásticos", COLOR_DANGER),
                    _build_kpi_card("Cuentas Clave en Churn", kpis["clientes_en_riesgo"], "Silencio extremo (S(t) < 0.10)", COLOR_WARNING),
                ],
            ),

            # ── Storytelling Tabs ─────────────────────────────────────────────
            dcc.Tabs(
                id="story-tabs",
                value="tab-diagnostico",
                style={"marginBottom": "20px"},
                children=[
                    dcc.Tab(
                        label="1. Diagnóstico & Rescate",
                        value="tab-diagnostico",
                        style=tab_style,
                        selected_style=selected_tab_style,
                        children=[
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(480px, 1fr))", "gap": "20px", "marginTop": "20px"},
                                children=[
                                    html.Div(children=[dcc.Graph(figure=factory.build_v1_devoluciones_exceso())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v2_margen_por_canal())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v10_waterfall_rescate())], style=get_card_style({"gridColumn": "1 / -1"})),
                                ],
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="2. Precios & Elasticidad",
                        value="tab-precios",
                        style=tab_style,
                        selected_style=selected_tab_style,
                        children=[
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(480px, 1fr))", "gap": "20px", "marginTop": "20px"},
                                children=[
                                    html.Div(children=[dcc.Graph(figure=factory.build_v3_elasticidad_descuento())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v6_curva_logistica_descuento())], style=get_card_style()),
                                ],
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="3. Clientes & Churn",
                        value="tab-clientes",
                        style=tab_style,
                        selected_style=selected_tab_style,
                        children=[
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(480px, 1fr))", "gap": "20px", "marginTop": "20px"},
                                children=[
                                    html.Div(children=[dcc.Graph(figure=factory.build_v4_clv_y_churn())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v8_quejas_crm_conversion())], style=get_card_style()),
                                ],
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="4. Marketing & ROI Real",
                        value="tab-marketing",
                        style=tab_style,
                        selected_style=selected_tab_style,
                        children=[
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(480px, 1fr))", "gap": "20px", "marginTop": "20px"},
                                children=[
                                    html.Div(children=[dcc.Graph(figure=factory.build_v5_conversion_por_tipo())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v9_roi_campanas_comparativo())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v7_heatmap_segmento_campana())], style=get_card_style({"gridColumn": "1 / -1"})),
                                ],
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="5. Las 10 Visualizaciones",
                        value="tab-todas",
                        style=tab_style,
                        selected_style=selected_tab_style,
                        children=[
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(480px, 1fr))", "gap": "20px", "marginTop": "20px"},
                                children=[
                                    html.Div(children=[dcc.Graph(figure=factory.build_v1_devoluciones_exceso())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v2_margen_por_canal())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v3_elasticidad_descuento())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v4_clv_y_churn())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v5_conversion_por_tipo())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v6_curva_logistica_descuento())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v7_heatmap_segmento_campana())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v8_quejas_crm_conversion())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v9_roi_campanas_comparativo())], style=get_card_style()),
                                    html.Div(children=[dcc.Graph(figure=factory.build_v10_waterfall_rescate())], style=get_card_style()),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    return app


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8050
    print(f"Iniciando RetailVenture DSS Executive Dashboard en http://127.0.0.1:{port} ...")
    app = create_app()
    app.run(host="127.0.0.1", port=port, debug=False)
