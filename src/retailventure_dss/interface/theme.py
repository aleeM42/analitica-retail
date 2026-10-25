"""Theme configuration, design tokens, and Plotly styling for the Executive Dashboard."""

from __future__ import annotations

from typing import Any
import plotly.graph_objects as go

# ── Color Palette ─────────────────────────────────────────────────────────────
BG_APP = "#090d16"
BG_CARD = "#111827"
BORDER_CARD = "#1f2937"
TEXT_PRIMARY = "#f8fafc"
TEXT_MUTED = "#94a3b8"

COLOR_ACCENT = "#38bdf8"
COLOR_DANGER = "#f43f5e"
COLOR_SUCCESS = "#10b981"
COLOR_WARNING = "#f59e0b"
COLOR_PURPLE = "#a855f7"

GRID_COLOR = "#1e293b"
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def get_card_style(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Base CSS dictionary for dashboard cards."""
    base = {
        "backgroundColor": BG_CARD,
        "borderRadius": "10px",
        "border": f"1px solid {BORDER_CARD}",
        "padding": "20px",
        "marginBottom": "20px",
        "boxShadow": "0 4px 6px -1px rgba(0, 0, 0, 0.3)",
    }
    if extra:
        base.update(extra)
    return base


def apply_theme(
    fig: go.Figure,
    title: str,
    subtitle: str | None = None,
    height: int = 420,
) -> go.Figure:
    """Applies executive dark theme and insight title hierarchy to a Plotly figure."""
    formatted_title = f"<b>{title}</b>"
    if subtitle:
        formatted_title += f"<br><span style='font-size:12px;color:{TEXT_MUTED};font-weight:normal'>{subtitle}</span>"

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY, size=12),
        title=dict(
            text=formatted_title,
            x=0.02,
            y=0.95,
            xanchor="left",
            yanchor="top",
            font=dict(size=14, color=TEXT_PRIMARY),
        ),
        margin=dict(l=40, r=40, t=70, b=40),
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False)
    return fig
