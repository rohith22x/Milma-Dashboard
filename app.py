import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="MILMA Demand Intelligence",
    page_icon="🥛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Design Tokens ─────────────────────────────────────────────
PRIMARY        = "#2563EB"
SUCCESS        = "#16A34A"
WARNING        = "#F59E0B"
DANGER         = "#DC2626"

BG_MAIN        = "#F5F7FB"
CARD_BG        = "#FFFFFF"

TEXT_PRIMARY   = "#111827"
TEXT_SECONDARY = "#6B7280"

BORDER         = "#E5E7EB"

YEAR_COLORS = {
    2021: "#2563EB",
    2022: "#16A34A",
    2023: "#F59E0B",
    2024: "#DC2626",
    2025: "#7C3AED",
}

CATEGORY_COLORS = {
    "Ghee":          "#2563EB",
    "Butter":        "#F59E0B",
    "Palada":        "#7C3AED",
    "UHT Milk":      "#F97316",
    "Milk Powder":   "#16A34A",
    "Instant Mixes": "#DC2626",
}

CLUSTER_COLORS = {
    "Revenue Giants":   "#F59E0B",
    "Festival Rockets": "#7C3AED",
    "Core Portfolio":   "#2563EB",
}

ACTION_COLORS = {
    "PROTECT — Maximum stock, zero stockout tolerance":            "#16A34A",
    "INVEST — Growing high value SKU, build inventory":            "#2563EB",
    "SURGE PREP — Build safety stock pre-Onam and Vishu":          "#2563EB",
    "MAINTAIN — Standard replenishment, monthly review":           "#6B7280",
    "SUPPORT — Recovery underway, moderate stock build":           "#F59E0B",
    "MANUAL PLAN — Forecast unreliable, expert review needed":     "#F97316",
    "DISCONTINUE REVIEW — Severely disrupted, evaluate viability": "#DC2626",
    "FESTIVAL REVIEW — Festival SKU recovery needed":              "#7C3AED",
    "GROW — Strong growth, increase stock allocation":             "#16A34A",
}

# ── Lucide SVG icon library ───────────────────────────────────
# Each returns a self-contained inline SVG string.
# size: pixel dimension  color: stroke color
def _svg(path_d: str, size: int = 16, color: str = "currentColor",
         extra_tags: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        f'style="vertical-align:middle;flex-shrink:0;">'
        f'{path_d}{extra_tags}</svg>'
    )

def icon_home(size=16, color="currentColor"):
    return _svg('<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
                '<polyline points="9 22 9 12 15 12 15 22"/>', size, color)

def icon_bar_chart(size=16, color="currentColor"):
    return _svg('<line x1="18" y1="20" x2="18" y2="10"/>'
                '<line x1="12" y1="20" x2="12" y2="4"/>'
                '<line x1="6"  y1="20" x2="6"  y2="14"/>', size, color)

def icon_trending_up(size=16, color="currentColor"):
    return _svg('<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
                '<polyline points="16 7 22 7 22 13"/>', size, color)

def icon_scatter(size=16, color="currentColor"):
    return _svg('<circle cx="7.5" cy="7.5" r="1.5"/>'
                '<circle cx="18.5" cy="5.5" r="1.5"/>'
                '<circle cx="11.5" cy="11.5" r="1.5"/>'
                '<circle cx="7.5" cy="16.5" r="1.5"/>'
                '<circle cx="17.5" cy="14.5" r="1.5"/>', size, color)

def icon_trophy(size=16, color="currentColor"):
    return _svg('<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>'
                '<path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>'
                '<path d="M4 22h16"/>'
                '<path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>'
                '<path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>'
                '<path d="M18 2H6v7a6 6 0 0 0 12 0V2z"/>', size, color)

def icon_alert_triangle(size=16, color="currentColor"):
    return _svg('<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16'
                'a2 2 0 0 0 1.73-3z"/>'
                '<line x1="12" y1="9" x2="12" y2="13"/>'
                '<line x1="12" y1="17" x2="12.01" y2="17"/>', size, color)

def icon_check_circle(size=16, color="currentColor"):
    return _svg('<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
                '<polyline points="22 4 12 14.01 9 11.01"/>', size, color)

def icon_search(size=16, color="currentColor"):
    return _svg('<circle cx="11" cy="11" r="8"/>'
                '<line x1="21" y1="21" x2="16.65" y2="16.65"/>', size, color)

def icon_git_branch(size=16, color="currentColor"):
    return _svg('<line x1="6" y1="3" x2="6" y2="15"/>'
                '<circle cx="18" cy="6" r="3"/>'
                '<circle cx="6"  cy="18" r="3"/>'
                '<path d="M18 9a9 9 0 0 1-9 9"/>', size, color)

def icon_cpu(size=16, color="currentColor"):
    return _svg('<rect x="4" y="4" width="16" height="16" rx="2" ry="2"/>'
                '<rect x="9" y="9" width="6" height="6"/>'
                '<line x1="9"  y1="1" x2="9"  y2="4"/>'
                '<line x1="15" y1="1" x2="15" y2="4"/>'
                '<line x1="9"  y1="20" x2="9"  y2="23"/>'
                '<line x1="15" y1="20" x2="15" y2="23"/>'
                '<line x1="20" y1="9"  x2="23" y2="9"/>'
                '<line x1="20" y1="14" x2="23" y2="14"/>'
                '<line x1="1"  y1="9"  x2="4"  y2="9"/>'
                '<line x1="1"  y1="14" x2="4"  y2="14"/>', size, color)

def icon_shield_alert(size=16, color="currentColor"):
    return _svg('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
                '<line x1="12" y1="8" x2="12" y2="12"/>'
                '<line x1="12" y1="16" x2="12.01" y2="16"/>', size, color)

def icon_list_checks(size=16, color="currentColor"):
    return _svg('<path d="m3 17 2 2 4-4"/>'
                '<path d="m3 7 2 2 4-4"/>'
                '<line x1="13" y1="8" x2="21" y2="8"/>'
                '<line x1="13" y1="16" x2="21" y2="16"/>', size, color)

def icon_layers(size=16, color="currentColor"):
    return _svg('<polygon points="12 2 2 7 12 12 22 7 12 2"/>'
                '<polyline points="2 17 12 22 22 17"/>'
                '<polyline points="2 12 12 17 22 12"/>', size, color)

def icon_info(size=16, color="currentColor"):
    return _svg('<circle cx="12" cy="12" r="10"/>'
                '<line x1="12" y1="8" x2="12" y2="12"/>'
                '<line x1="12" y1="16" x2="12.01" y2="16"/>', size, color)

def icon_activity(size=16, color="currentColor"):
    return _svg('<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>', size, color)

def icon_calendar(size=16, color="currentColor"):
    return _svg('<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>'
                '<line x1="16" y1="2" x2="16" y2="6"/>'
                '<line x1="8"  y1="2" x2="8"  y2="6"/>'
                '<line x1="3"  y1="10" x2="21" y2="10"/>', size, color)

def icon_package(size=16, color="currentColor"):
    return _svg('<line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/>'
                '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4'
                'A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4'
                'A2 2 0 0 0 21 16z"/>'
                '<polyline points="3.27 6.96 12 12.01 20.73 6.96"/>'
                '<line x1="12" y1="22.08" x2="12" y2="12"/>', size, color)

def icon_dollar(size=16, color="currentColor"):
    return _svg('<line x1="12" y1="1" x2="12" y2="23"/>'
                '<path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>', size, color)

def icon_milk(size=16, color="currentColor"):
    # milk bottle / droplet silhouette
    return _svg('<path d="M8 2h8l1 4H7z"/>'
                '<path d="M7 6v14a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V6"/>'
                '<path d="M10 10h4"/>', size, color)

def icon_zap(size=16, color="currentColor"):
    return _svg('<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>', size, color)

def icon_x_circle(size=16, color="currentColor"):
    return _svg('<circle cx="12" cy="12" r="10"/>'
                '<line x1="15" y1="9" x2="9" y2="15"/>'
                '<line x1="9"  y1="9" x2="15" y2="15"/>', size, color)

def icon_arrow_up_right(size=16, color="currentColor"):
    return _svg('<line x1="7" y1="17" x2="17" y2="7"/>'
                '<polyline points="7 7 17 7 17 17"/>', size, color)


# ── Sidebar nav page keys (no emoji) ─────────────────────────
# We keep the radio value strings clean; icons are rendered separately.
PAGE_KEYS = [
    "Executive Summary",
    "Portfolio Overview",
    "EDA — Sales Trends",
    "Clustering Results",
    "Forecasting Tournament",
    "Portfolio Risk",
    "Recommendation System",
    "Category Deep Dive",
]

PAGE_ICONS = {
    "Executive Summary":     icon_home,
    "Portfolio Overview":    icon_bar_chart,
    "EDA — Sales Trends":    icon_trending_up,
    "Clustering Results":    icon_scatter,
    "Forecasting Tournament":icon_trophy,
    "Portfolio Risk":        icon_alert_triangle,
    "Recommendation System": icon_list_checks,
    "Category Deep Dive":    icon_search,
}

# ── CSS ───────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{
    background: {BG_MAIN};
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  }}
  .block-container {{
    padding: 1.5rem 2rem 2rem;
    max-width: 1400px;
  }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background: #0F172A;
    border-right: 1px solid #1E293B;
  }}
  section[data-testid="stSidebar"] * {{ color: #CBD5E1 !important; }}

  /* Style sidebar buttons as nav items */
  section[data-testid="stSidebar"] .stButton button {{
    background: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    color: #94A3B8 !important;
    font-size: .87em !important;
    font-weight: 400 !important;
    padding: 8px 12px !important;
    text-align: left !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: background .15s !important;
  }}
  section[data-testid="stSidebar"] .stButton button:hover {{
    background: #1E293B !important;
    color: #F1F5F9 !important;
  }}
  section[data-testid="stSidebar"] .stButton button:focus {{
    box-shadow: none !important;
    outline: none !important;
  }}
  /* Active nav button — highlight the currently selected page */
  section[data-testid="stSidebar"] div.nav-btn-wrap[style*="background:#1E3A5F"] .stButton button {{
    background: #1E3A5F !important;
    color: #93C5FD !important;
    font-weight: 600 !important;
  }}

  /* Header */
  .dashboard-header {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 20px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
  }}
  .dashboard-header .hdr-icon {{
    width: 40px; height: 40px;
    background: #EFF6FF;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }}
  .dashboard-header h1 {{
    color: {TEXT_PRIMARY} !important;
    font-size: 1.25em;
    font-weight: 700;
    margin: 0 0 3px;
    letter-spacing: -.3px;
  }}
  .dashboard-header p {{
    color: {TEXT_SECONDARY};
    margin: 0;
    font-size: .85em;
  }}

  /* KPI Cards */
  .kpi-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 16px;
  }}
  .kpi-value {{
    font-size: 1.85em;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    line-height: 1.1;
  }}
  .kpi-label {{
    font-size: .75em;
    color: {TEXT_SECONDARY};
    margin-top: 6px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: .7px;
  }}
  .kpi-sub {{
    font-size: .75em;
    color: {TEXT_SECONDARY};
    margin-top: 2px;
    opacity: .75;
  }}

  /* Section title */
  .section-title {{
    font-size: .78em;
    font-weight: 700;
    color: {TEXT_SECONDARY};
    margin: 0 0 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}

  /* Insight boxes */
  .insight-box {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-left: 4px solid {PRIMARY};
    border-radius: 6px;
    padding: 13px 16px;
    margin: 10px 0;
    font-size: .88em;
    line-height: 1.65;
    color: {TEXT_PRIMARY};
  }}
  .insight-box.warning {{ border-left-color: {WARNING}; }}
  .insight-box.danger  {{ border-left-color: {DANGER};  }}
  .insight-box.success {{ border-left-color: {SUCCESS}; }}

  /* Insight title row with SVG icon */
  .insight-title {{
    display: flex;
    align-items: center;
    gap: 7px;
    font-weight: 700;
    margin-bottom: 5px;
    font-size: 1em;
  }}

  /* Step cards */
  .step-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 22px 20px 18px;
    text-align: center;
    height: 100%;
  }}
  .step-card .step-icon-wrap {{
    width: 44px; height: 44px;
    background: #EFF6FF;
    border-radius: 10px;
    display: inline-flex;
    align-items: center; justify-content: center;
    margin-bottom: 12px;
  }}
  .step-card .step-name {{
    font-weight: 700;
    color: {TEXT_PRIMARY};
    font-size: .95em;
    margin-bottom: 6px;
  }}
  .step-card .step-body {{
    font-size: .84em;
    color: {TEXT_SECONDARY};
    line-height: 1.6;
  }}

  .divider {{
    border: none;
    border-top: 1px solid {BORDER};
    margin: 18px 0;
  }}

  #MainMenu {{ visibility: hidden; }}
  footer    {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)


# ── Reusable UI components ────────────────────────────────────

def create_header(title: str, subtitle: str = "", icon_fn=None):
    icon_html = ""
    if icon_fn:
        svg = icon_fn(size=20, color=PRIMARY)
        icon_html = f"<div class='hdr-icon'>{svg}</div>"
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"<div class='dashboard-header'>{icon_html}"
        f"<div><h1>{title}</h1>{sub_html}</div></div>",
        unsafe_allow_html=True)

def create_kpi(value, label, sub=""):
    sub_html = f"<div class='kpi-sub'>{sub}</div>" if sub else ""
    return (f"<div class='kpi-card'>"
            f"<div class='kpi-value'>{value}</div>"
            f"<div class='kpi-label'>{label}</div>"
            f"{sub_html}</div>")

def create_section(title: str):
    st.markdown(f"<div class='section-title'>{title}</div>",
                unsafe_allow_html=True)

def create_insight(title: str, body: str, style: str = "",
                   icon_fn=None, icon_color: str = TEXT_PRIMARY):
    icon_html = ""
    if icon_fn:
        icon_html = icon_fn(size=14, color=icon_color)
    title_block = (f"<div class='insight-title'>{icon_html}{title}</div>"
                   if title else "")
    st.markdown(
        f"<div class='insight-box {style}'>{title_block}{body}</div>",
        unsafe_allow_html=True)

def create_step_card(icon_fn, name: str, body: str,
                     icon_color: str = PRIMARY, bg: str = "#EFF6FF"):
    svg = icon_fn(size=20, color=icon_color)
    return (f"<div class='step-card'>"
            f"<div class='step-icon-wrap' style='background:{bg};'>{svg}</div>"
            f"<div class='step-name'>{name}</div>"
            f"<div class='step-body'>{body}</div>"
            f"</div>")

def chart_fmt(fig, height=360, show_legend=True):
    fig.update_layout(
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_PRIMARY, family="Inter, Segoe UI, system-ui"),
        height=height,
        showlegend=show_legend,
        legend=dict(bgcolor=CARD_BG, bordercolor=BORDER, borderwidth=1,
                    font=dict(size=11)),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=True, gridcolor="#F3F4F6", gridwidth=1,
                   linecolor=BORDER, tickfont=dict(size=11), zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", gridwidth=1,
                   linecolor=BORDER, tickfont=dict(size=11), zeroline=False),
    )
    return fig

def fmt_pie(fig, height=300, center_text=""):
    """
    Clean donut chart: percent labels inside slices,
    readable legend below, no outside scattered labels.
    """
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(size=11, color=CARD_BG),
        insidetextorientation="radial",
        marker=dict(line=dict(color=CARD_BG, width=2)))
    layout = dict(
        paper_bgcolor=CARD_BG,
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(
            orientation="h",
            y=-0.15, x=0.5, xanchor="center",
            font=dict(size=11, color=TEXT_PRIMARY),
            bgcolor=CARD_BG,
            borderwidth=0))
    if center_text:
        layout["annotations"] = [dict(
            text=center_text, x=0.5, y=0.5,
            font_size=13, font_color=TEXT_PRIMARY,
            showarrow=False)]
    fig.update_layout(**layout)
    return fig

def hex_to_rgba(h, a=0.12):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


# ── Data ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    master     = pd.read_csv("master_dairy_dataset.csv",   parse_dates=["Date"])
    clusters   = pd.read_csv("sku_clusters.csv")
    tournament = pd.read_csv("tournament_results.csv")
    forecast   = pd.read_csv("forecast_2026.csv",          parse_dates=["Date"])
    bi3        = pd.read_csv("bi3_concentration_risk.csv")
    bi7        = pd.read_csv("bi7_recovery_analysis.csv")
    recsys     = pd.read_csv("master_recommendation_table.csv")
    return master, clusters, tournament, forecast, bi3, bi7, recsys

master, clusters, tournament, forecast, bi3, bi7, recsys = load_data()


# ── Session state for navigation ─────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Executive Summary"

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    milk_svg = icon_milk(size=18, color="#93C5FD")
    st.markdown(f"""
    <div style='padding:20px 16px 14px;display:flex;align-items:center;gap:10px;'>
      <div style='width:34px;height:34px;background:#1E3A5F;border-radius:8px;
                  display:flex;align-items:center;justify-content:center;flex-shrink:0;'>
        {milk_svg}
      </div>
      <div>
        <div style='font-size:.95em;font-weight:700;color:#F1F5F9;
                    letter-spacing:-.2px;'>MILMA</div>
        <div style='font-size:.7em;color:#64748B;margin-top:1px;'>
          Demand Intelligence</div>
      </div>
    </div>
    <hr style='border:none;border-top:1px solid #1E293B;margin:0 0 6px;'>
    """, unsafe_allow_html=True)

    for key in PAGE_KEYS:
        is_active = (st.session_state.page == key)
        icon_svg  = PAGE_ICONS[key](size=15,
                        color="#93C5FD" if is_active else "#64748B")
        label_color = "#93C5FD" if is_active else "#94A3B8"
        bg_style    = "background:#1E3A5F;" if is_active else ""
        fw_style    = "font-weight:600;" if is_active else ""

        # Render icon + label as the button face via markdown trick:
        # wrap in a container div for styling, use st.button for interactivity
        st.markdown(
            f"<div class='nav-btn-wrap' style='{bg_style}border-radius:6px;"
            f"margin:1px 4px;'>",
            unsafe_allow_html=True)
        if st.button(
            f"{key}",
            key=f"nav_{key}",
            use_container_width=True,
        ):
            st.session_state.page = key
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <hr style='border:none;border-top:1px solid #1E293B;margin:10px 0;'>
    <div style='font-size:.72em;color:#475569;padding:0 16px 16px;line-height:2;'>
      <div style='color:#94A3B8;font-weight:600;margin-bottom:4px;font-size:.9em;
                  text-transform:uppercase;letter-spacing:.6px;'>Project Info</div>
      MSc CS Data Analytics<br>
      Malabar MILMA<br>
      46 SKUs · 6 Categories<br>
      Jan 2021 – Dec 2025<br>
      28,284 transactions
    </div>
    """, unsafe_allow_html=True)

page = st.session_state.page


# ══════════════════════════════════════════════════════════════
# PAGE 0 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════
if page == "Executive Summary":
    create_header("Executive Summary",
        "MILMA Malabar · Demand Intelligence System · Key findings at a glance",
        icon_fn=icon_home)

    total_rev  = master["Sales_Value"].sum()
    top3_share = bi3.nlargest(3, "Total_Revenue")["Revenue_Share_Pct"].sum()
    ghee_share = bi3[bi3["Category"] == "Ghee"]["Revenue_Share_Pct"].sum()
    growing    = len(bi7[bi7["Recovery_Status"] == "GROWING"])
    disrupted  = len(bi7[bi7["Recovery_Status"] == "DISRUPTED"])
    best_mape  = tournament["Champion_MAPE"].min()
    t1_count   = len(recsys[recsys["Planning_Tier"].str.contains("TIER 1", na=False)])

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(create_kpi(f"₹{total_rev/1e9:.2f}B", "5-Year Total Revenue", "2021–2025"), unsafe_allow_html=True)
    c2.markdown(create_kpi("46 SKUs", "Active Products", "6 categories"), unsafe_allow_html=True)
    c3.markdown(create_kpi("XGBoost", "Forecast Champion", "5 of 6 category wins"), unsafe_allow_html=True)
    c4.markdown(create_kpi(f"{t1_count} SKUs", "Algorithm-Ready Forecasts", "MAPE < 30%"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.markdown(create_kpi(f"{top3_share:.1f}%", "Top 3 SKU Share", "Extreme concentration"), unsafe_allow_html=True)
    k2.markdown(create_kpi(f"{ghee_share:.1f}%", "Ghee Dominance", "HHI = 0.1516"), unsafe_allow_html=True)
    k3.markdown(create_kpi(f"{best_mape:.1f}%", "Best MAPE", "Ghee — Excellent"), unsafe_allow_html=True)
    k4.markdown(create_kpi("0.61", "Silhouette Score", "K-Means quality"), unsafe_allow_html=True)
    k5.markdown(create_kpi(str(growing), "Growing SKUs", "At all-time peak"), unsafe_allow_html=True)
    k6.markdown(create_kpi(str(disrupted), "Disrupted SKUs", "Need strategic review"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        create_section("5-Year Revenue Trend — All Categories")
        monthly_all = master.groupby(["Date", "Category"])["Sales_Value"].sum().reset_index()
        fig = px.area(monthly_all, x="Date", y="Sales_Value",
                      color="Category", color_discrete_map=CATEGORY_COLORS)
        fig.update_traces(line=dict(width=1.5))
        chart_fmt(fig, height=320)
        fig.update_layout(xaxis_title="", yaxis_title="Monthly Revenue (₹)",
                          legend=dict(orientation="h", y=-0.2, x=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        create_section("Critical Findings")
        create_insight(
            "Concentration Risk",
            f"3 SKUs = <b>{top3_share:.1f}%</b> of revenue. "
            "Zero stockout tolerance on Ghee 500ml, 15kg Tin, 200ml Pet.",
            style="danger", icon_fn=icon_alert_triangle, icon_color=DANGER)
        create_insight(
            "Festival Dependency",
            "Ghee and Palada spike <b>2–5×</b> during Onam (Aug) and Vishu (Apr). "
            "Surge stock 6 weeks before.",
            style="warning", icon_fn=icon_calendar, icon_color=WARNING)
        create_insight(
            "Forecast Reliability",
            f"<b>{t1_count} SKUs</b> have reliable forecasts (MAPE &lt;30%). "
            "Ghee 12%, Palada 19%. Use directly for procurement.",
            style="success", icon_fn=icon_check_circle, icon_color=SUCCESS)

    st.markdown("<br>", unsafe_allow_html=True)
    create_section("Three-Step Methodology")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(create_step_card(
            icon_layers, "Step 1 — Clustering",
            "K-Means groups 46 SKUs into 3 demand segments "
            "by revenue, volatility, and seasonality.<br><b>Silhouette = 0.61</b>",
            icon_color=PRIMARY, bg="#EFF6FF"), unsafe_allow_html=True)
    with m2:
        st.markdown(create_step_card(
            icon_trophy, "Step 2 — Forecasting",
            "Prophet vs XGBoost tournament on identical "
            "12-month holdout. XGBoost wins 5/6.<br><b>Best MAPE: 12.07%</b>",
            icon_color="#7C3AED", bg="#F5F3FF"), unsafe_allow_html=True)
    with m3:
        st.markdown(create_step_card(
            icon_list_checks, "Step 3 — Recommendations",
            "9 action types per SKU combining cluster, "
            "forecast quality, HHI, and recovery status.<br><b>42 SKUs covered</b>",
            icon_color=SUCCESS, bg="#F0FDF4"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 1 — PORTFOLIO OVERVIEW
# ══════════════════════════════════════════════════════════════
elif page == "Portfolio Overview":
    create_header("Portfolio Overview",
        "Malabar MILMA · Shelf Stable Dairy · 2021–2025",
        icon_fn=icon_bar_chart)

    total_rev  = master["Sales_Value"].sum()
    total_sku  = master["Product"].nunique()
    top3_share = bi3.nlargest(3, "Total_Revenue")["Revenue_Share_Pct"].sum()
    ghee_share = bi3[bi3["Category"] == "Ghee"]["Revenue_Share_Pct"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(create_kpi(f"₹{total_rev/1e9:.2f}B", "Total Portfolio Revenue", "5-year 2021–2025"), unsafe_allow_html=True)
    c2.markdown(create_kpi(str(total_sku), "Total Active SKUs", "6 categories"), unsafe_allow_html=True)
    c3.markdown(create_kpi(f"{top3_share:.1f}%", "Top 3 SKUs Revenue Share", "Extreme concentration"), unsafe_allow_html=True)
    c4.markdown(create_kpi(f"{ghee_share:.1f}%", "Ghee Category Dominance", "HHI = 0.1516"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        create_section("Revenue Distribution by Category")
        cat_rev = master.groupby("Category")["Sales_Value"].sum().reset_index()
        fig = px.pie(cat_rev, values="Sales_Value", names="Category", hole=0.55,
                     color="Category", color_discrete_map=CATEGORY_COLORS)
        fmt_pie(fig, height=340,
                center_text=f"<b>₹{total_rev/1e9:.2f}B</b><br>Total")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        create_section("Top 10 SKUs by Revenue")
        top10 = bi3.nlargest(10, "Total_Revenue").copy().sort_values("Total_Revenue")
        bc = [DANGER if f == "CRITICAL" else WARNING if f == "HIGH" else PRIMARY
              for f in top10["Concentration_Flag"]]
        fig2 = go.Figure(go.Bar(
            x=top10["Total_Revenue"], y=top10["Product"], orientation="h",
            marker_color=bc, marker_line_width=0,
            text=[f"₹{v/1e6:.0f}M" for v in top10["Total_Revenue"]],
            textposition="outside", textfont=dict(size=11, color=TEXT_PRIMARY)))
        chart_fmt(fig2, height=340, show_legend=False)
        fig2.update_layout(xaxis_title="Total Revenue (₹)",
                           yaxis=dict(tickfont=dict(size=10)),
                           margin=dict(l=10, r=70, t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        f"<div style='font-size:.8em;color:{TEXT_SECONDARY};margin:-4px 0 14px;'>"
        f"<span style='color:{DANGER};font-weight:600;'>■ CRITICAL</span> &nbsp;"
        f"<span style='color:{WARNING};font-weight:600;'>■ HIGH</span> &nbsp;"
        f"<span style='color:{PRIMARY};font-weight:600;'>■ STANDARD</span>"
        f" &nbsp;concentration flag</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    create_section("Key Findings")
    r1, r2, r3 = st.columns(3)
    with r1:
        create_insight("Extreme Concentration",
            "3 SKUs generate <b>60%</b> of total revenue. "
            "Any Ghee supply disruption is a business-level risk.",
            style="danger", icon_fn=icon_alert_triangle, icon_color=DANGER)
    with r2:
        create_insight("Festival Dependency",
            "Ghee and Palada show <b>2–5× revenue spikes</b> "
            "during Onam (Aug) and Vishu (Apr).",
            style="warning", icon_fn=icon_calendar, icon_color=WARNING)
    with r3:
        create_insight("Growth Signal",
            "<b>17 SKUs</b> at all-time revenue peaks. "
            "Butter and Milk Powder strongest growth in 2025.",
            style="success", icon_fn=icon_arrow_up_right, icon_color=SUCCESS)


# ══════════════════════════════════════════════════════════════
# PAGE 2 — EDA
# ══════════════════════════════════════════════════════════════
elif page == "EDA — Sales Trends":
    create_header("Exploratory Data Analysis",
        "Sales trends · seasonality patterns · year-on-year growth · 2021–2025",
        icon_fn=icon_trending_up)

    f1, f2, _ = st.columns([2, 2, 3])
    with f1:
        sel_cat = st.multiselect("Category",
            sorted(master["Category"].unique()),
            default=sorted(master["Category"].unique()))
    with f2:
        sel_year = st.multiselect("Year",
            sorted(master["Year"].unique()),
            default=sorted(master["Year"].unique()))

    df = master[master["Category"].isin(sel_cat) & master["Year"].isin(sel_year)]

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(create_kpi(f"₹{df['Sales_Value'].sum()/1e9:.2f}B", "Revenue (Filtered)"), unsafe_allow_html=True)
    c2.markdown(create_kpi(str(df["Product"].nunique()), "SKUs in Selection"), unsafe_allow_html=True)
    peak_m = df.groupby("Month_Name")["Sales_Value"].mean().idxmax()
    c3.markdown(create_kpi(peak_m, "Peak Month (Avg)"), unsafe_allow_html=True)
    best_c = df.groupby("Category")["Sales_Value"].sum().idxmax()
    c4.markdown(create_kpi(best_c, "Top Category"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    create_section("Monthly Revenue Comparison 2021–2025 — Each Line = One Year")

    df_trend = df.groupby(["Year", "Month_No", "Month_Name"])["Sales_Value"].sum().reset_index()
    df_trend = df_trend.sort_values(["Year", "Month_No"])
    MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    abbr = {"January":"Jan","February":"Feb","March":"Mar","April":"Apr","May":"May",
            "June":"Jun","July":"Jul","August":"Aug","September":"Sep",
            "October":"Oct","November":"Nov","December":"Dec"}
    df_trend["Month_Abbr"] = df_trend["Month_Name"].map(lambda x: abbr.get(x, x[:3]))

    fig_yr = go.Figure()
    for yr in sorted(df_trend["Year"].unique()):
        yd  = df_trend[df_trend["Year"] == yr].copy().sort_values("Month_No")
        col = YEAR_COLORS.get(int(yr), PRIMARY)
        fig_yr.add_trace(go.Scatter(
            x=yd["Month_Abbr"], y=yd["Sales_Value"],
            name=str(int(yr)), mode="lines+markers",
            line=dict(color=col, width=2.5),
            marker=dict(size=7, color=col, line=dict(color=CARD_BG, width=1.5)),
            hovertemplate=f"<b>{int(yr)}</b><br>%{{x}}: ₹%{{y:,.0f}}<extra></extra>"))

    fig_yr.update_layout(
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG, height=360,
        font=dict(color=TEXT_PRIMARY),
        margin=dict(l=10, r=15, t=10, b=10),
        xaxis=dict(categoryorder="array", categoryarray=MONTH_ORDER,
                   showgrid=True, gridcolor="#F3F4F6", linecolor=BORDER, tickfont=dict(size=12)),
        yaxis=dict(title="Monthly Revenue (₹)", showgrid=True, gridcolor="#F3F4F6",
                   linecolor=BORDER, tickfont=dict(size=11)),
        legend=dict(title="Year", orientation="h", y=-0.2, x=0,
                    bgcolor=CARD_BG, bordercolor=BORDER, borderwidth=1, font=dict(size=12)),
        showlegend=True, hovermode="x unified")
    st.plotly_chart(fig_yr, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        create_section("Monthly Seasonality Heatmap")
        heat = master.groupby(["Category", "Month_No"])["Sales_Value"].mean().reset_index()
        hp   = heat.pivot(index="Category", columns="Month_No", values="Sales_Value")
        mn   = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        fig2 = go.Figure(go.Heatmap(
            z=hp.values, x=mn, y=hp.index.tolist(),
            colorscale=[[0, "#EFF6FF"], [0.5, "#93C5FD"], [1, "#1D4ED8"]],
            text=[[f"₹{v/1e6:.1f}M" for v in row] for row in hp.values],
            texttemplate="%{text}", textfont=dict(size=9, color=CARD_BG),
            showscale=False))
        fig2.update_layout(paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
            height=280, margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(tickfont=dict(size=11)), yaxis=dict(tickfont=dict(size=11)))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        create_section("Annual Revenue by Category")
        annual = master.groupby(["Year", "Category"])["Sales_Value"].sum().reset_index()
        fig3   = px.bar(annual, x="Year", y="Sales_Value", color="Category",
                        barmode="group", color_discrete_map=CATEGORY_COLORS)
        chart_fmt(fig3, height=280)
        fig3.update_layout(xaxis_title="Year", yaxis_title="Revenue (₹)",
                           xaxis=dict(tickmode="linear"),
                           legend=dict(orientation="h", y=-0.32, x=0, font=dict(size=10)))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    create_section("Year-on-Year Revenue Growth (%) by Category")
    yoy = master.groupby(["Year", "Category"])["Sales_Value"].sum().reset_index()
    yoy["YoY"] = yoy.groupby("Category")["Sales_Value"].pct_change() * 100
    yp = yoy.pivot(index="Category", columns="Year", values="YoY").round(1)
    fig4 = go.Figure(go.Heatmap(
        z=yp.values, x=[str(y) for y in yp.columns], y=yp.index.tolist(),
        colorscale=[[0, "#FEF2F2"], [0.5, "#F9FAFB"], [1, "#F0FDF4"]],
        zmid=0,
        text=[[f"{v:+.1f}%" if not np.isnan(v) else "—" for v in row] for row in yp.values],
        texttemplate="%{text}", textfont=dict(size=12, color=TEXT_PRIMARY),
        showscale=False))
    fig4.update_layout(paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        height=240, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(tickfont=dict(size=12)), yaxis=dict(tickfont=dict(size=12)))
    st.plotly_chart(fig4, use_container_width=True)
    create_insight("",
        "Green cells = revenue growth vs prior year · "
        "Red cells = revenue decline · "
        "UHT Milk shows red from 2022 onwards · "
        "Butter and Milk Powder bright green in 2025",
        icon_fn=icon_info, icon_color=TEXT_SECONDARY)


# ══════════════════════════════════════════════════════════════
# PAGE 3 — CLUSTERING
# ══════════════════════════════════════════════════════════════
elif page == "Clustering Results":
    create_header("K-Means Clustering — Product Segmentation",
        "Unsupervised ML · 46 SKUs · 3 demand segments · Silhouette Score 0.61",
        icon_fn=icon_scatter)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(create_kpi("3",      "Clusters Found",  "Optimal K confirmed"), unsafe_allow_html=True)
    c2.markdown(create_kpi("0.61",   "Silhouette Score","Well-separated"),       unsafe_allow_html=True)
    c3.markdown(create_kpi("3 SKUs", "Revenue Giants",  "60% of revenue"),       unsafe_allow_html=True)
    c4.markdown(create_kpi("4 SKUs", "Festival Rockets","Onam & Vishu"),          unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sel_cl = st.multiselect("Filter Cluster",
        clusters["Cluster_Name"].dropna().unique(),
        default=list(clusters["Cluster_Name"].dropna().unique()))
    df_cl = clusters[clusters["Cluster_Name"].isin(sel_cl)]

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        create_section("Volatility vs Seasonality — Interactive Scatter")
        fig1 = px.scatter(df_cl, x="Volatility_CV", y="Seasonality_Strength",
            color="Cluster_Name", size="Total_Revenue",
            hover_name="Product",
            hover_data={"Category": True, "Total_Revenue": ":,.0f", "Cluster_Name": False},
            color_discrete_map=CLUSTER_COLORS, size_max=55)
        chart_fmt(fig1, height=400)
        fig1.update_layout(xaxis_title="Demand Volatility (CV)",
                           yaxis_title="Seasonality Strength",
                           legend=dict(title="Cluster", orientation="h", y=-0.18, x=0))
        fig1.update_traces(marker=dict(line=dict(color=CARD_BG, width=1.5), opacity=0.85))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        create_section("Revenue by Cluster")
        cl_rev = clusters.groupby("Cluster_Name")["Total_Revenue"].sum().reset_index()
        fig2 = px.pie(cl_rev, values="Total_Revenue", names="Cluster_Name", hole=0.5,
                      color="Cluster_Name", color_discrete_map=CLUSTER_COLORS)
        fmt_pie(fig2, height=260)
        st.plotly_chart(fig2, use_container_width=True)

        create_section("Cluster Summary")
        cs = clusters.groupby("Cluster_Name").agg(
            SKUs=("Product", "count"), Revenue=("Total_Revenue", "sum")).reset_index()
        cs["Rev %"] = (cs["Revenue"] / cs["Revenue"].sum() * 100).round(1)
        cs["Revenue"] = cs["Revenue"].apply(lambda x: f"₹{x/1e6:.0f}M")
        st.dataframe(cs[["Cluster_Name", "SKUs", "Rev %", "Revenue"]]
                       .rename(columns={"Cluster_Name": "Cluster"}),
                     hide_index=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    create_section("SKU Cluster Assignment Table")
    dc = df_cl[["Product", "Category", "Cluster_Name",
                "Total_Revenue", "Volatility_CV", "Seasonality_Strength"]]\
         .sort_values("Total_Revenue", ascending=False).copy()
    dc["Total_Revenue"] = dc["Total_Revenue"].apply(lambda x: f"₹{x/1e6:.2f}M")
    dc.columns = ["Product", "Category", "Cluster", "Revenue", "Volatility CV", "Seasonality"]
    st.dataframe(dc, hide_index=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    with r1:
        create_insight("Revenue Giants",
            "3 SKUs · 60.4% of portfolio. Ghee 500ml, 15kg, 200ml. "
            "<b>Zero stockout tolerance.</b>",
            style="danger", icon_fn=icon_dollar, icon_color=DANGER)
    with r2:
        create_insight("Festival Rockets",
            "4 SKUs · extreme Onam & Vishu spikes. "
            "<b>Surge stock 6 weeks before festivals.</b>",
            style="warning", icon_fn=icon_zap, icon_color=WARNING)
    with r3:
        create_insight("Core Portfolio",
            "35 SKUs · stable predictable demand. "
            "<b>Monthly review sufficient.</b>",
            style="success", icon_fn=icon_package, icon_color=SUCCESS)


# ══════════════════════════════════════════════════════════════
# PAGE 4 — FORECASTING
# ══════════════════════════════════════════════════════════════
elif page == "Forecasting Tournament":
    create_header("Prophet vs XGBoost — Forecasting Tournament",
        "Fair comparison · identical 12-month holdout Jan–Dec 2025 · 2026 demand forecasts",
        icon_fn=icon_trophy)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(create_kpi("XGBoost", "Tournament Champion",  "Wins 5 of 6"),       unsafe_allow_html=True)
    c2.markdown(create_kpi("12.07%",  "Best MAPE — Ghee",    "Excellent accuracy"), unsafe_allow_html=True)
    c3.markdown(create_kpi("2 / 6",   "Excellent Forecasts",  "MAPE below 20%"),    unsafe_allow_html=True)
    c4.markdown(create_kpi("3 / 6",   "Need Manual Planning", "MAPE above 70%"),    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        create_section("Tournament Results Table")
        def q_style(v):
            if v == "Excellent":  return f"background:#F0FDF4;color:{SUCCESS};font-weight:600"
            elif v == "Acceptable": return f"background:#FFFBEB;color:{WARNING};font-weight:600"
            return f"background:#FEF2F2;color:{DANGER};font-weight:600"
        def m_style(v):
            try:
                f = float(v)
                if f < 20:  return f"color:{SUCCESS};font-weight:600"
                if f < 50:  return f"color:{WARNING};font-weight:600"
                return f"color:{DANGER};font-weight:600"
            except: return ""

        ts = tournament[["Category", "Prophet_MAPE", "XGBoost_MAPE",
                          "Champion", "Champion_MAPE", "Quality"]].copy()
        ts.columns = ["Category", "Prophet %", "XGBoost %", "Champion", "Best MAPE %", "Quality"]
        styled = (ts.style
            .applymap(q_style, subset=["Quality"])
            .applymap(m_style, subset=["Prophet %", "XGBoost %", "Best MAPE %"])
            .format({"Prophet %": "{:.2f}", "XGBoost %": "{:.2f}", "Best MAPE %": "{:.2f}"})
            .set_properties(**{"text-align": "center", "font-size": "13px"}))
        st.dataframe(styled, hide_index=True, use_container_width=True)

    with col2:
        create_section("MAPE Comparison — Prophet vs XGBoost")
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(name="Prophet", x=tournament["Category"],
            y=tournament["Prophet_MAPE"],
            marker_color="#7C3AED", marker_line_width=0,
            text=tournament["Prophet_MAPE"].round(1),
            textposition="outside", textfont=dict(size=10)))
        fig1.add_trace(go.Bar(name="XGBoost", x=tournament["Category"],
            y=tournament["XGBoost_MAPE"],
            marker_color=PRIMARY, marker_line_width=0,
            text=tournament["XGBoost_MAPE"].round(1),
            textposition="outside", textfont=dict(size=10)))
        fig1.add_hline(y=20, line_dash="dot", line_color=SUCCESS, line_width=1.5,
                       annotation_text="Excellent ≤20%",
                       annotation_font_color=SUCCESS, annotation_font_size=10)
        fig1.add_hline(y=50, line_dash="dot", line_color=DANGER, line_width=1.5,
                       annotation_text="Poor >50%",
                       annotation_font_color=DANGER, annotation_font_size=10)
        fig1.update_layout(barmode="group")
        chart_fmt(fig1, height=340)
        fig1.update_layout(yaxis_title="MAPE (%)",
                           legend=dict(orientation="h", y=-0.2, x=0.3))
        st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    create_section("2026 Monthly Demand Forecast")
    sel_cat_f = st.multiselect("Select categories",
        options=sorted(forecast["Category"].unique()),
        default=sorted(forecast["Category"].unique()))

    if sel_cat_f:
        ff   = forecast[forecast["Category"].isin(sel_cat_f)].copy()
        fig2 = go.Figure()
        for cat in sel_cat_f:
            cd  = ff[ff["Category"] == cat].copy()
            col = CATEGORY_COLORS.get(cat, PRIMARY)
            rgba_fill = hex_to_rgba(col, 0.12)
            has_ci = ("Upper_95" in cd.columns and "Lower_95" in cd.columns
                      and cd["Upper_95"].notna().any())
            if has_ci:
                xb = list(cd["Date"]) + list(cd["Date"].iloc[::-1])
                yb = list(cd["Upper_95"]) + list(cd["Lower_95"].iloc[::-1])
                fig2.add_trace(go.Scatter(x=xb, y=yb, fill="toself",
                    fillcolor=rgba_fill, line=dict(color="rgba(0,0,0,0)"),
                    showlegend=False, hoverinfo="skip", mode="lines"))
            fig2.add_trace(go.Scatter(x=cd["Date"], y=cd["Forecast"], name=cat,
                line=dict(color=col, width=2.5), mode="lines+markers",
                marker=dict(size=7, color=col, line=dict(color=CARD_BG, width=1.5))))
        chart_fmt(fig2, height=400)
        fig2.update_layout(xaxis_title="Month (2026)",
                           yaxis_title="Forecast Revenue (₹)",
                           legend=dict(orientation="h", y=-0.18, x=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        create_insight("Why XGBoost Won 5/6",
            "2025 structural changes violated Prophet's decomposition assumptions. "
            "XGBoost's <b>year encoding and lag features</b> adapted better to "
            "structural demand shifts.",
            style="success", icon_fn=icon_cpu, icon_color=SUCCESS)
    with r2:
        create_insight("Why 3 Categories Failed",
            "UHT Milk (85% collapse), Milk Powder (product expansion 2025), "
            "Instant Mixes (CV=1.998). "
            "<b>No model predicts structural breaks.</b>",
            style="warning", icon_fn=icon_alert_triangle, icon_color=WARNING)


# ══════════════════════════════════════════════════════════════
# PAGE 5 — PORTFOLIO RISK
# ══════════════════════════════════════════════════════════════
elif page == "Portfolio Risk":
    create_header("Portfolio Risk Analysis",
        "Concentration risk (HHI) · demand recovery classification · 46 SKUs",
        icon_fn=icon_shield_alert)

    critical  = len(bi3[bi3["Concentration_Flag"] == "CRITICAL"])
    disrupted = len(bi7[bi7["Recovery_Status"] == "DISRUPTED"])
    growing   = len(bi7[bi7["Recovery_Status"] == "GROWING"])
    top3_sh   = bi3.nlargest(3, "Total_Revenue")["Revenue_Share_Pct"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(create_kpi(str(critical),      "CRITICAL SKUs",        "Each >10% of portfolio"), unsafe_allow_html=True)
    c2.markdown(create_kpi(f"{top3_sh:.1f}%",  "Top 3 Revenue Share",  "3-6-40 rule"),            unsafe_allow_html=True)
    c3.markdown(create_kpi(str(growing),       "Growing SKUs",         "At all-time peak"),       unsafe_allow_html=True)
    c4.markdown(create_kpi(str(disrupted),     "Disrupted SKUs",       "Below peak"),             unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        create_section("Concentration Flag Distribution")
        conc = bi3["Concentration_Flag"].value_counts().reset_index()
        conc.columns = ["Flag", "Count"]
        fc   = {"CRITICAL": DANGER, "HIGH": "#F97316", "MODERATE": WARNING, "LOW": PRIMARY}
        fig1 = px.pie(conc, values="Count", names="Flag", hole=0.5,
                      color="Flag", color_discrete_map=fc)
        fmt_pie(fig1, height=300)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        create_section("Recovery Status Distribution")
        rec = bi7["Recovery_Status"].value_counts().reset_index()
        rec.columns = ["Status", "Count"]
        rc  = {"GROWING": SUCCESS, "STABLE": "#0D9488", "RECOVERING": WARNING, "DISRUPTED": DANGER}
        fig2 = px.pie(rec, values="Count", names="Status", hole=0.5,
                      color="Status", color_discrete_map=rc)
        fmt_pie(fig2, height=300)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    create_section("SKU Recovery Rate vs Peak Revenue")
    rs = bi7.sort_values("Recovery_Rate_Pct")
    bc = [DANGER if r < 50 else WARNING if r < 90 else SUCCESS
          for r in rs["Recovery_Rate_Pct"]]
    fig3 = go.Figure(go.Bar(
        x=rs["Recovery_Rate_Pct"], y=rs["Product"],
        orientation="h", marker_color=bc, marker_line_width=0,
        text=rs["Recovery_Rate_Pct"].round(0).astype(int).astype(str) + "%",
        textposition="outside", textfont=dict(size=9, color=TEXT_PRIMARY)))
    fig3.add_vline(x=100, line_dash="dash", line_color=TEXT_SECONDARY, line_width=1,
                   annotation_text="Peak 100%", annotation_font_size=10,
                   annotation_font_color=TEXT_SECONDARY)
    chart_fmt(fig3, height=680, show_legend=False)
    fig3.update_layout(xaxis_title="Recovery Rate % vs Peak Year",
                       yaxis=dict(tickfont=dict(size=9)),
                       margin=dict(l=10, r=70, t=20, b=10))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    create_section("Severely Disrupted SKUs")
    dd = bi7[bi7["Recovery_Status"] == "DISRUPTED"][[
        "Product", "Category", "Peak_Year", "Recovery_Rate_Pct", "YoY_Growth_Pct"]].copy()
    dd.columns = ["Product", "Category", "Peak Year", "Recovery Rate %", "YoY Growth %"]
    st.dataframe(dd.sort_values("Recovery Rate %"), hide_index=True, use_container_width=True)
    create_insight("Highest Priority SKU",
        "<b>Ok Ghee 50ml</b> — Peak ₹47.3M (2021) → "
        "Current ₹1.9M (2025) · 96% collapse · "
        "Highest priority for discontinuation review.",
        style="danger", icon_fn=icon_alert_triangle, icon_color=DANGER)


# ══════════════════════════════════════════════════════════════
# PAGE 6 — RECOMMENDATION SYSTEM
# ══════════════════════════════════════════════════════════════
elif page == "Recommendation System":
    create_header("SKU Demand Planning Recommendations",
        "Integrated output · clustering · forecasting · concentration risk · recovery analysis · 42 SKUs",
        icon_fn=icon_list_checks)

    t1 = len(recsys[recsys["Planning_Tier"].str.contains("TIER 1", na=False)])
    t2 = len(recsys[recsys["Planning_Tier"].str.contains("TIER 2", na=False)])
    t3 = len(recsys[recsys["Planning_Tier"].str.contains("TIER 3", na=False)])
    protect = len(recsys[recsys["Recommended_Action"].str.contains("PROTECT", na=False)])

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(create_kpi(str(t1),      "Tier 1 — Algorithm", "Forecasts trusted"),      unsafe_allow_html=True)
    c2.markdown(create_kpi(str(t2),      "Tier 2 — Caution",   "Validate before order"),  unsafe_allow_html=True)
    c3.markdown(create_kpi(str(t3),      "Tier 3 — Manual",    "Human judgment needed"),  unsafe_allow_html=True)
    c4.markdown(create_kpi(str(protect), "PROTECT SKUs",        "Zero stockout tolerance"),unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    create_section("Filters")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        s_cat = st.multiselect("Category",
            recsys["Category"].dropna().unique(),
            default=list(recsys["Category"].dropna().unique()))
    with f2:
        s_cl = st.multiselect("Cluster",
            recsys["Cluster_Name"].dropna().unique(),
            default=list(recsys["Cluster_Name"].dropna().unique()))
    with f3:
        s_tier = st.multiselect("Planning Tier",
            recsys["Planning_Tier"].dropna().unique(),
            default=list(recsys["Planning_Tier"].dropna().unique()))
    with f4:
        s_act = st.multiselect("Action",
            recsys["Recommended_Action"].dropna().unique(),
            default=list(recsys["Recommended_Action"].dropna().unique()))

    dr = recsys[
        recsys["Category"].isin(s_cat) &
        recsys["Cluster_Name"].isin(s_cl) &
        recsys["Planning_Tier"].isin(s_tier) &
        recsys["Recommended_Action"].isin(s_act)]

    st.markdown(
        f"<p style='color:{TEXT_SECONDARY};font-size:.85em;'>"
        f"Showing {len(dr)} of {len(recsys)} SKUs</p>",
        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        create_section("Recommended Actions Distribution")
        ac = dr["Recommended_Action"].value_counts().reset_index()
        ac.columns = ["Action", "Count"]
        ac["Short"] = ac["Action"].str.split("—").str[0].str.strip()
        ac = ac.sort_values("Count")
        fig1 = go.Figure(go.Bar(
            x=ac["Count"], y=ac["Short"], orientation="h",
            marker_color=[ACTION_COLORS.get(a, PRIMARY) for a in ac["Action"]],
            marker_line_width=0,
            text=ac["Count"], textposition="outside", textfont=dict(size=11)))
        chart_fmt(fig1, height=320, show_legend=False)
        fig1.update_layout(xaxis_title="Number of SKUs",
                           yaxis=dict(tickfont=dict(size=10)))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        create_section("Planning Tier Split")
        tc = dr["Planning_Tier"].value_counts().reset_index()
        tc.columns = ["Tier", "Count"]
        tc["Short"] = tc["Tier"].str.split("—").str[0].str.strip()
        tcols = [SUCCESS if "TIER 1" in t else WARNING if "TIER 2" in t else DANGER
                 for t in tc["Tier"]]
        fig2 = px.pie(tc, values="Count", names="Short", hole=0.5,
                      color_discrete_sequence=tcols)
        fmt_pie(fig2, height=260)
        st.plotly_chart(fig2, use_container_width=True)

        create_section("Top 10 Priority SKUs")
        tp = dr.nlargest(10, "Priority_Score")[
            ["Product", "Priority_Score", "Recommended_Action"]].copy()
        tp["Action"]   = tp["Recommended_Action"].str.split("—").str[0].str.strip()
        tp["Priority"] = tp["Priority_Score"].round(1)
        st.dataframe(tp[["Product", "Priority", "Action"]],
                     hide_index=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    create_section("Master SKU Recommendation Table")
    dcols = ["Product", "Category", "Cluster_Name", "Concentration_Flag",
             "Recovery_Status", "Planning_Tier", "Champion_MAPE",
             "Priority_Score", "Recommended_Action"]
    dcols = [c for c in dcols if c in dr.columns]
    tbl   = dr[dcols].sort_values("Priority_Score", ascending=False).copy()
    if "Champion_MAPE"  in tbl.columns: tbl["Champion_MAPE"]  = tbl["Champion_MAPE"].round(2)
    if "Priority_Score" in tbl.columns: tbl["Priority_Score"] = tbl["Priority_Score"].round(1)

    def style_row(row):
        act   = row.get("Recommended_Action", "")
        color = ACTION_COLORS.get(act, "")
        base  = f"color:{TEXT_PRIMARY}"
        if color:
            r2 = int(color[1:3], 16); g2 = int(color[3:5], 16); b2 = int(color[5:7], 16)
            bg = f"rgba({r2},{g2},{b2},0.10)"
            return [f"background:{bg};color:{TEXT_PRIMARY};font-weight:600"
                    if col == "Recommended_Action" else base for col in row.index]
        return [base for _ in row.index]

    st.dataframe(
        tbl.style.apply(style_row, axis=1)
               .set_properties(**{"font-size": "12px", "border": f"1px solid {BORDER}"}),
        hide_index=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    with r1:
        create_insight(f"Tier 1 — {t1} SKUs",
            "Use forecasts directly for procurement. Ghee, Butter, Palada.",
            style="success", icon_fn=icon_check_circle, icon_color=SUCCESS)
    with r2:
        create_insight(f"Tier 2 — {t2} SKUs",
            "Validate before ordering. Disrupted Ghee and recovering Palada.",
            style="warning", icon_fn=icon_activity, icon_color=WARNING)
    with r3:
        create_insight(f"Tier 3 — {t3} SKUs",
            "Human expert review required. UHT Milk, Milk Powder, Instant Mixes.",
            style="danger", icon_fn=icon_x_circle, icon_color=DANGER)


# ══════════════════════════════════════════════════════════════
# PAGE 7 — CATEGORY DEEP DIVE
# ══════════════════════════════════════════════════════════════
elif page == "Category Deep Dive":
    create_header("Category Deep Dive",
        "Select any category to explore all SKUs in detail — revenue · cluster · forecast · action",
        icon_fn=icon_search)

    sel = st.selectbox("Select Category", sorted(master["Category"].unique()))

    cat_master  = master[master["Category"] == sel]
    cat_bi3     = bi3[bi3["Category"] == sel]
    cat_bi7     = bi7[bi7["Category"] == sel]
    cat_recsys  = recsys[recsys["Category"] == sel]
    cat_tour    = tournament[tournament["Category"] == sel]

    st.markdown("<br>", unsafe_allow_html=True)

    cat_rev   = cat_master["Sales_Value"].sum()
    cat_skus  = cat_master["Product"].nunique()
    total_rev = master["Sales_Value"].sum()
    cat_share = cat_rev / total_rev * 100
    cat_mape  = cat_tour["Champion_MAPE"].values[0] if len(cat_tour) > 0 else None
    cat_champ = cat_tour["Champion"].values[0]       if len(cat_tour) > 0 else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(create_kpi(f"₹{cat_rev/1e6:.0f}M", "Category Revenue", "5-year total"), unsafe_allow_html=True)
    c2.markdown(create_kpi(str(cat_skus), "SKUs in Category", ""), unsafe_allow_html=True)
    c3.markdown(create_kpi(f"{cat_share:.1f}%", "Portfolio Share", ""), unsafe_allow_html=True)
    c4.markdown(create_kpi(
        f"{cat_mape:.1f}%" if cat_mape else "N/A",
        "Best Model MAPE", f"Champion: {cat_champ}"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        create_section(f"{sel} — Monthly Revenue Trend by Year")
        ct = cat_master.groupby(["Year", "Month_No", "Month_Name"])["Sales_Value"].sum().reset_index()
        abbr = {"January":"Jan","February":"Feb","March":"Mar","April":"Apr","May":"May",
                "June":"Jun","July":"Jul","August":"Aug","September":"Sep",
                "October":"Oct","November":"Nov","December":"Dec"}
        ct["Month_Abbr"] = ct["Month_Name"].map(lambda x: abbr.get(x, x[:3]))
        fig1 = go.Figure()
        MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        for yr in sorted(ct["Year"].unique()):
            yd     = ct[ct["Year"] == yr].sort_values("Month_No")
            col_yr = YEAR_COLORS.get(int(yr), PRIMARY)
            fig1.add_trace(go.Scatter(
                x=yd["Month_Abbr"], y=yd["Sales_Value"],
                name=str(int(yr)), mode="lines+markers",
                line=dict(color=col_yr, width=2.5),
                marker=dict(size=7, color=col_yr, line=dict(color=CARD_BG, width=1.5)),
                hovertemplate=f"<b>{int(yr)}</b><br>%{{x}}: ₹%{{y:,.0f}}<extra></extra>"))
        fig1.update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG, height=300,
            font=dict(color=TEXT_PRIMARY),
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(categoryorder="array", categoryarray=MONTH_ORDER,
                       showgrid=True, gridcolor="#F3F4F6", tickfont=dict(size=11)),
            yaxis=dict(title="Revenue (₹)", showgrid=True, gridcolor="#F3F4F6"),
            legend=dict(orientation="h", y=-0.28, x=0, font=dict(size=11)),
            hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        create_section(f"{sel} — Revenue by SKU")
        sku_rev = cat_bi3.sort_values("Total_Revenue", ascending=False)
        if len(sku_rev) > 0:
            fig2 = go.Figure(go.Bar(
                x=sku_rev["Total_Revenue"], y=sku_rev["Product"], orientation="h",
                marker_color=CATEGORY_COLORS.get(sel, PRIMARY), marker_line_width=0,
                text=[f"₹{v/1e6:.1f}M" for v in sku_rev["Total_Revenue"]],
                textposition="outside", textfont=dict(size=10, color=TEXT_PRIMARY)))
            chart_fmt(fig2, height=300, show_legend=False)
            fig2.update_layout(xaxis_title="Total Revenue (₹)",
                               yaxis=dict(tickfont=dict(size=10), autorange="reversed"),
                               margin=dict(l=10, r=70, t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    create_section(f"{sel} — SKU Detail Table")

    if len(cat_recsys) > 0:
        detail = cat_recsys[[
            "Product", "Cluster_Name", "Concentration_Flag",
            "Recovery_Status", "Planning_Tier",
            "Champion_MAPE", "Priority_Score",
            "Recommended_Action"]].copy()
        if "Champion_MAPE"  in detail.columns: detail["Champion_MAPE"]  = detail["Champion_MAPE"].round(2)
        if "Priority_Score" in detail.columns: detail["Priority_Score"] = detail["Priority_Score"].round(1)
        detail = detail.sort_values("Priority_Score", ascending=False)
        detail.columns = ["Product", "Cluster", "Conc. Flag",
                          "Recovery", "Planning Tier", "MAPE %", "Priority", "Action"]
        st.dataframe(detail, hide_index=True, use_container_width=True)
    else:
        st.info("No recommendation data for this category.")

    if len(cat_bi7) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        create_section(f"{sel} — SKU Recovery vs Peak")
        rb  = cat_bi7.sort_values("Recovery_Rate_Pct")
        rbc = [DANGER if r < 50 else WARNING if r < 90 else SUCCESS
               for r in rb["Recovery_Rate_Pct"]]
        fig3 = go.Figure(go.Bar(
            x=rb["Recovery_Rate_Pct"], y=rb["Product"],
            orientation="h", marker_color=rbc, marker_line_width=0,
            text=rb["Recovery_Rate_Pct"].round(0).astype(int).astype(str) + "%",
            textposition="outside", textfont=dict(size=10, color=TEXT_PRIMARY)))
        fig3.add_vline(x=100, line_dash="dash", line_color=TEXT_SECONDARY, line_width=1)
        chart_fmt(fig3, height=max(220, len(rb) * 45), show_legend=False)
        fig3.update_layout(xaxis_title="Recovery Rate % vs Peak",
                           yaxis=dict(tickfont=dict(size=10)),
                           margin=dict(l=10, r=70, t=10, b=10))
        st.plotly_chart(fig3, use_container_width=True)
