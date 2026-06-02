"""Reusable lightweight UI helpers for Streamlit pages."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

ACCENT = "#FF4433"
DARK = "#1A0400"
TEXT = "#FFFFFF"


def inject_global_css() -> None:
    """Inject lightweight global CSS for consistent spacing and readability."""
    st.markdown(
        f"""
        <style>
            :root {{
                --accent: {ACCENT};
                --dark: {DARK};
                --text: {TEXT};
            }}

            .stApp {{
                background: var(--dark);
                color: var(--text);
                font-family: "Segoe UI", sans-serif !important;
            }}

            [data-testid="stSidebar"] {{
                background: var(--dark);
                border-right: 1px solid var(--accent);
            }}

            [data-testid="stSidebar"] * {{
                color: var(--text);
            }}

            h1, h2, h3, h4, h5, h6,
            p, li, label,
            [data-testid="stMarkdownContainer"],
            [data-testid="stCaptionContainer"] {{
                color: var(--text) !important;
            }}

            .stMarkdown a {{
                color: var(--text);
                text-decoration: underline;
            }}

            .stAlert {{
                border: 1px solid var(--accent);
                background: rgba(255, 68, 51, 0.08);
                border-radius: 12px;
            }}

            .stMetric {{
                border: 1px solid var(--accent);
                border-radius: 12px;
                padding: 0.6rem;
                background: rgba(255, 68, 51, 0.04);
            }}

            [data-testid="stMetricLabel"],
            [data-testid="stMetricValue"],
            [data-testid="stMetricDelta"] {{
                color: var(--text) !important;
            }}

            .stButton > button,
            .stDownloadButton > button {{
                background: var(--accent);
                color: var(--text);
                border: 1px solid var(--accent);
                border-radius: 10px;
                font-weight: 700;
                transition: all 0.2s ease;
            }}

            .stButton > button:hover,
            .stDownloadButton > button:hover {{
                background: var(--dark);
                color: var(--text);
                border: 1px solid var(--accent);
            }}

            .stTextArea textarea,
            .stTextInput input,
            .stNumberInput input,
            .stDateInput input,
            .stSelectbox div[data-baseweb="select"] > div,
            .stMultiSelect div[data-baseweb="select"] > div {{
                background: var(--dark);
                color: var(--text);
                border: 1px solid var(--accent);
                border-radius: 10px;
            }}

            .stTextArea textarea::placeholder,
            input::placeholder {{
                color: rgba(255,255,255,0.7) !important;
            }}

            .stCheckbox label,
            .stRadio label {{
                color: var(--text) !important;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.5rem;
                border-bottom: 1px solid var(--accent);
            }}

            .stTabs [data-baseweb="tab"] {{
                background: var(--dark);
                color: var(--text);
                border: 1px solid var(--accent);
                border-radius: 10px 10px 0 0;
            }}

            .stTabs [aria-selected="true"] {{
                background: var(--accent);
                color: var(--text);
            }}

            [data-testid="stExpander"] {{
                border: 1px solid var(--accent);
                border-radius: 10px;
                background: rgba(255, 68, 51, 0.03);
                margin-bottom: 0.5rem;
            }}

            [data-testid="stDataFrame"] {{
                border: 1px solid var(--accent);
                border-radius: 10px;
            }}

            [data-testid="stToolbar"] {{
                right: 1rem;
            }}

            hr {{
                border-color: var(--accent);
            }}

            code {{
                color: var(--text);
                background: rgba(255, 68, 51, 0.12);
            }}

            .block-container {{
                padding-top: 1.25rem;
                padding-bottom: 2.5rem;
                max-width: 1280px;
            }}

            .app-info-box {{
                border: 1px solid var(--accent);
                border-radius: 12px;
                padding: 0.75rem 0.9rem;
                margin: 0.4rem 0 0.9rem 0;
                background: rgba(255, 68, 51, 0.06);
            }}

            .app-status-badge {{
                display: inline-block;
                border: 1px solid var(--accent);
                border-radius: 999px;
                padding: 0.12rem 0.5rem;
                font-size: 0.8rem;
                background: rgba(255, 68, 51, 0.10);
                color: var(--text);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str | None = None) -> None:
    """Render a consistent page header with optional subtitle."""
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.markdown("---")


def render_info_box(title: str, body: str) -> None:
    """Render a small styled information container."""
    st.markdown(
        f"""
        <div class="app-info-box">
            <div style="font-weight:700; margin-bottom:0.25rem;">{title}</div>
            <div>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(text: str) -> str:
    """Return a compact status badge HTML snippet."""
    return f"<span class='app-status-badge'>{text}</span>"


def apply_global_theme() -> None:
    """Backward-compatible wrapper to apply global CSS."""
    inject_global_css()


def render_brand_header(app_name: str, subtitle: str, logo_mark: str = "split_orbit") -> None:
    """Backward-compatible branded header block for existing pages."""
    if logo_mark == "split_orbit":
        logo_html = (
            f"<div style='font-size:30px; line-height:1; color:{ACCENT}; font-weight:800;'>◜●◝</div>"
        )
    else:
        logo_html = f"<div style='font-size:28px; line-height:1;'>{logo_mark}</div>"

    st.markdown(
        f"""
        <div style="
            border:1px solid {ACCENT};
            border-radius:16px;
            padding:14px 16px;
            margin-bottom:12px;
            background:rgba(255,68,51,0.08);
        ">
            <div style="display:flex; align-items:center; gap:10px;">
                {logo_html}
                <div>
                    <div style="font-size:1.2rem; font-weight:800; color:{TEXT};">{app_name}</div>
                    <div style="font-size:0.95rem; color:{TEXT}; opacity:0.92;">{subtitle}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_plotly_figure(fig: go.Figure) -> go.Figure:
    """Apply consistent dual-color style to Plotly figures."""
    accent_soft = "rgba(255, 68, 51, 0.45)"
    accent_faint = "rgba(255, 68, 51, 0.15)"

    fig.update_layout(
        paper_bgcolor=DARK,
        plot_bgcolor=DARK,
        font={"color": TEXT},
        title_font={"color": TEXT},
        legend={"font": {"color": TEXT}},
        xaxis={
            "color": TEXT,
            "gridcolor": accent_faint,
            "zerolinecolor": accent_faint,
        },
        yaxis={
            "color": TEXT,
            "gridcolor": accent_faint,
            "zerolinecolor": accent_faint,
        },
        colorway=[ACCENT, accent_soft, DARK],
    )

    for idx, trace in enumerate(fig.data):
        color = ACCENT if idx % 2 == 0 else accent_soft

        if hasattr(trace, "marker") and trace.marker is not None:
            trace.marker.color = color
            trace.marker.line = {"color": ACCENT, "width": 1}

        if trace.type == "pie":
            size = len(trace.labels) if getattr(trace, "labels", None) is not None else 2
            pie_colors = [ACCENT if i % 2 == 0 else accent_soft for i in range(size)]
            trace.marker = {
                "colors": pie_colors,
                "line": {"color": ACCENT, "width": 1},
            }
            if not getattr(trace, "hole", None):
                trace.hole = 0.45

        if trace.type == "heatmap":
            trace.colorscale = [
                [0.0, DARK],
                [0.5, accent_soft],
                [1.0, ACCENT],
            ]
            trace.colorbar = {"title": {"font": {"color": TEXT}}, "tickfont": {"color": TEXT}}

    return fig
