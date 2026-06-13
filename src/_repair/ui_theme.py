"""Reusable UI helpers and CareerCompass theme for Streamlit pages."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src.brand_constants import APP_NAME, APP_TAGLINE, APP_VERSION

ACCENT = "#FF4433"
ACCENT_SOFT = "rgba(255, 68, 51, 0.45)"
ACCENT_FAINT = "rgba(255, 68, 51, 0.12)"
DARK = "#120608"
DARK_SURFACE = "#1A0A0C"
TEXT = "#FFFFFF"
TEXT_MUTED = "rgba(255,255,255,0.72)"


def inject_global_css() -> None:
    """Inject global CSS for CareerCompass."""
    st.markdown(
        f"""
        <style>
            :root {{
                --accent: {ACCENT};
                --accent-soft: {ACCENT_SOFT};
                --dark: {DARK};
                --dark-surface: {DARK_SURFACE};
                --text: {TEXT};
                --text-muted: {TEXT_MUTED};
            }}

            .stApp {{
                background: linear-gradient(180deg, {DARK} 0%, {DARK_SURFACE} 100%);
                color: var(--text);
                font-family: "Inter", "Segoe UI", sans-serif !important;
            }}

            [data-testid="stSidebar"] {{
                background: {DARK_SURFACE};
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
                border-radius: 14px;
            }}

            .stMetric {{
                border: 1px solid var(--accent);
                border-radius: 14px;
                padding: 0.75rem;
                background: rgba(255, 68, 51, 0.05);
                box-shadow: 0 8px 24px rgba(0,0,0,0.18);
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
                border-radius: 12px;
                font-weight: 700;
                padding: 0.55rem 1rem;
                transition: all 0.2s ease;
            }}

            .stButton > button:hover,
            .stDownloadButton > button:hover {{
                background: var(--dark);
                color: var(--text);
                border: 1px solid var(--accent);
                transform: translateY(-1px);
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
                border-radius: 12px;
            }}

            .stTextArea textarea::placeholder,
            input::placeholder {{
                color: rgba(255,255,255,0.55) !important;
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
                border-radius: 12px 12px 0 0;
            }}

            .stTabs [aria-selected="true"] {{
                background: var(--accent);
                color: var(--text);
            }}

            [data-testid="stExpander"] {{
                border: 1px solid var(--accent);
                border-radius: 14px;
                background: rgba(255, 68, 51, 0.03);
                margin-bottom: 0.6rem;
            }}

            [data-testid="stDataFrame"] {{
                border: 1px solid var(--accent);
                border-radius: 14px;
            }}

            hr {{
                border-color: var(--accent);
                opacity: 0.35;
            }}

            code {{
                color: var(--text);
                background: rgba(255, 68, 51, 0.14);
                border-radius: 6px;
                padding: 0.1rem 0.35rem;
            }}

            .block-container {{
                padding-top: 1rem;
                padding-bottom: 2.5rem;
                max-width: 1320px;
            }}

            .cc-hero {{
                border: 1px solid var(--accent);
                border-radius: 20px;
                padding: 1.4rem 1.6rem;
                margin-bottom: 1rem;
                background: linear-gradient(135deg, rgba(255,68,51,0.16) 0%, rgba(18,6,8,0.9) 55%);
                box-shadow: 0 16px 40px rgba(0,0,0,0.25);
            }}

            .cc-hero-title {{
                font-size: 1.65rem;
                font-weight: 800;
                color: var(--text);
                margin-bottom: 0.35rem;
            }}

            .cc-hero-subtitle {{
                font-size: 1rem;
                color: var(--text-muted);
                line-height: 1.5;
            }}

            .cc-badge {{
                display: inline-block;
                border: 1px solid var(--accent);
                border-radius: 999px;
                padding: 0.18rem 0.65rem;
                font-size: 0.78rem;
                background: rgba(255, 68, 51, 0.12);
                color: var(--text);
                margin-right: 0.35rem;
                margin-bottom: 0.35rem;
            }}

            .cc-card {{
                border: 1px solid var(--accent);
                border-radius: 16px;
                padding: 1rem 1.1rem;
                background: rgba(255, 68, 51, 0.05);
                min-height: 130px;
                margin-bottom: 0.75rem;
            }}

            .cc-card-title {{
                font-weight: 700;
                font-size: 1rem;
                margin-bottom: 0.35rem;
            }}

            .cc-card-body {{
                color: var(--text-muted);
                font-size: 0.92rem;
                line-height: 1.45;
            }}

            .cc-info-box {{
                border: 1px solid var(--accent);
                border-radius: 14px;
                padding: 0.85rem 1rem;
                margin: 0.5rem 0 0.9rem 0;
                background: rgba(255, 68, 51, 0.06);
            }}

            .cc-path-card {{
                border-left: 4px solid var(--accent);
                border-radius: 12px;
                padding: 0.9rem 1rem;
                background: rgba(255, 68, 51, 0.04);
                margin-bottom: 0.75rem;
            }}

            .cc-footer {{
                color: var(--text-muted);
                font-size: 0.85rem;
                margin-top: 1.5rem;
                padding-top: 1rem;
                border-top: 1px solid rgba(255, 68, 51, 0.25);
                text-align: center;
                line-height: 1.6;
            }}

            .cc-footer a {{
                color: var(--text) !important;
                text-decoration: underline;
                font-weight: 600;
            }}

            .cc-footer a:hover {{
                color: var(--accent) !important;
            }}

            .cc-wizard-box {{
                border: 2px solid var(--accent);
                border-radius: 18px;
                padding: 1.2rem 1.4rem;
                margin: 0.5rem 0 1.2rem 0;
                background: linear-gradient(135deg, rgba(255,68,51,0.14) 0%, rgba(18,6,8,0.95) 60%);
                box-shadow: 0 12px 32px rgba(0,0,0,0.25);
            }}

            .cc-wizard-step {{
                display: inline-block;
                border: 1px solid var(--accent);
                border-radius: 999px;
                padding: 0.2rem 0.75rem;
                font-size: 0.82rem;
                margin-right: 0.4rem;
                background: rgba(255, 68, 51, 0.12);
            }}

            .cc-wizard-step-active {{
                background: var(--accent);
                font-weight: 700;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str | None = None) -> None:
    """Render a consistent page header."""
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.markdown("---")


def render_brand_header(
    app_name: str | None = None,
    subtitle: str | None = None,
    logo_mark: str = "compass",
) -> None:
    """Render the CareerCompass hero header."""
    name = app_name or APP_NAME
    tagline = subtitle or APP_TAGLINE

    if logo_mark in {"compass", "split_orbit", "◜●◝"}:
        logo_html = (
            f"<div style='font-size:2rem; line-height:1; color:{ACCENT}; font-weight:800;'>🧭</div>"
        )
    else:
        logo_html = f"<div style='font-size:1.8rem; line-height:1;'>{logo_mark}</div>"

    st.markdown(
        f"""
        <div class="cc-hero">
            <div style="display:flex; align-items:center; gap:14px;">
                {logo_html}
                <div>
                    <div class="cc-hero-title">{name}</div>
                    <div class="cc-hero-subtitle">{tagline}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_box(title: str, body: str) -> None:
    """Render a styled info container."""
    st.markdown(
        f"""
        <div class="cc-info-box">
            <div style="font-weight:700; margin-bottom:0.3rem;">{title}</div>
            <div style="color:{TEXT_MUTED}; line-height:1.5;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_card(title: str, body: str, badge: str | None = None) -> None:
    """Render a compact feature card."""
    badge_html = f"<span class='cc-badge'>{badge}</span>" if badge else ""
    st.markdown(
        f"""
        <div class="cc-card">
            {badge_html}
            <div class="cc-card-title">{title}</div>
            <div class="cc-card-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_path_card(title: str, body: str) -> None:
    """Render a pathway explanation card."""
    st.markdown(
        f"""
        <div class="cc-path-card">
            <div style="font-weight:700; margin-bottom:0.25rem;">{title}</div>
            <div style="color:{TEXT_MUTED}; line-height:1.45;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(text: str) -> str:
    """Return HTML for a compact status badge."""
    return f"<span class='cc-badge'>{text}</span>"


def render_sidebar_navigation(extra_note: str | None = None) -> str:
    """Render sidebar navigation and language selector. Returns language code."""
    from src.i18n_utils import SUPPORTED_LANGUAGES, get_language_code, t
    from src.progress_tracker_utils import increment_stat

    if "ui_language_label" not in st.session_state:
        st.session_state["ui_language_label"] = "English"

    with st.sidebar:
        lang_label = st.selectbox(
            t("language", "en", "Language"),
            options=list(SUPPORTED_LANGUAGES.keys()),
            key="ui_language_label",
        )
        lang_code = get_language_code(lang_label)
        if lang_code == "bn":
            increment_stat("language_bn_used", 0)  # no-op unless first time
            if not st.session_state.get("_bn_badge_tracked"):
                increment_stat("language_bn_used", 1)
                st.session_state["_bn_badge_tracked"] = True

        st.markdown(f"### 🧭 {t('app_name', lang_code, APP_NAME)}")
        st.caption(t("app_tagline", lang_code, APP_TAGLINE))
        st.markdown("---")
        st.markdown(
            f"""
            **Explore**
            - 🗺️ {t('nav_overview', lang_code, 'Job Market Overview')}
            - 🔬 {t('nav_skills', lang_code, 'Skill Demand Analysis')}
            - 📄 {t('nav_cv_gap', lang_code, 'CV Skill Gap Analyzer')}
            - 🚀 {t('nav_recommendations', lang_code, 'Project & Career Actions')}
            - 🎯 {t('nav_job_match', lang_code, 'Job Match Dashboard')}
            - 🛠️ {t('nav_toolkit', lang_code, 'Career Toolkit')}
            - 🧠 {t('nav_intelligence', lang_code, 'Career Intelligence Hub')}
            - 🧠 {t('nav_clustering', lang_code, 'Role Clustering')}
            - 📥 {t('nav_import', lang_code, 'Data Import')}
            - 🌍 {t('nav_explorer', lang_code, 'Career Explorer')}
            """
        )
        if extra_note:
            st.markdown("---")
            st.caption(extra_note)

    return lang_code


def render_app_footer(show_tech_line: bool = True) -> None:
    """Render global app footer with copyright and portfolio link."""
    tech_line = (
        f"<div style='margin-bottom:0.35rem; opacity:0.85;'>Built with Python · Streamlit · scikit-learn · Plotly · {APP_VERSION}</div>"
        if show_tech_line
        else ""
    )
    html = (
        f'<div class="cc-footer">{tech_line}'
        "© 2026 All rights reserved by "
        '<a href="https://fzn011.github.io/portfolio/" target="_blank" rel="noopener noreferrer">Faiaz Zahin</a>'
        "</div>"
    )
    st.html(html)


def apply_global_theme() -> None:
    """Apply global CSS theme."""
    inject_global_css()


def style_plotly_figure(fig: go.Figure) -> go.Figure:
    """Apply consistent styling to Plotly figures."""
    fig.update_layout(
        paper_bgcolor=DARK,
        plot_bgcolor=DARK,
        font={"color": TEXT},
        title_font={"color": TEXT},
        legend={"font": {"color": TEXT}},
        xaxis={
            "color": TEXT,
            "gridcolor": ACCENT_FAINT,
            "zerolinecolor": ACCENT_FAINT,
        },
        yaxis={
            "color": TEXT,
            "gridcolor": ACCENT_FAINT,
            "zerolinecolor": ACCENT_FAINT,
        },
        colorway=[ACCENT, ACCENT_SOFT, DARK_SURFACE],
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
    )

    for idx, trace in enumerate(fig.data):
        color = ACCENT if idx % 2 == 0 else ACCENT_SOFT

        if trace.type == "pie":
            size = len(trace.labels) if getattr(trace, "labels", None) is not None else 2
            pie_colors = [ACCENT if i % 2 == 0 else ACCENT_SOFT for i in range(size)]
            trace.marker = {
                "colors": pie_colors,
                "line": {"color": ACCENT, "width": 1},
            }
            if not getattr(trace, "hole", None):
                trace.hole = 0.45
        elif hasattr(trace, "marker") and trace.marker is not None:
            if getattr(trace.marker, "color", None) is None:
                trace.marker.color = color
            trace.marker.line = {"color": ACCENT, "width": 1}

        if trace.type == "heatmap":
            trace.colorscale = [
                [0.0, DARK],
                [0.5, ACCENT_SOFT],
                [1.0, ACCENT],
            ]
            trace.colorbar = {"title": {"font": {"color": TEXT}}, "tickfont": {"color": TEXT}}

    return fig
