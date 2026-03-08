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

# ── Google Material Colors ────────────────────────────────────
BLUE        = "#1976D2"
LIGHT_BLUE  = "#42A5F5"
GREEN       = "#388E3C"
LIGHT_GREEN = "#66BB6A"
ORANGE      = "#F57C00"
AMBER       = "#FFB300"
RED         = "#D32F2F"
PINK        = "#E91E63"
PURPLE      = "#7B1FA2"
TEAL        = "#00796B"
CYAN        = "#0097A7"
INDIGO      = "#303F9F"
WHITE       = "#FFFFFF"
BORDER      = "#E0E0E0"
TEXT_DARK   = "#212121"
TEXT_MID    = "#757575"
TEXT_LIGHT  = "#BDBDBD"

# Year colours — vivid distinct palette matching Power BI style
YEAR_COLORS = {
    2021: "#1976D2",   # Blue
    2022: "#E91E63",   # Pink
    2023: "#FF6F00",   # Amber dark
    2024: "#388E3C",   # Green
    2025: "#7B1FA2",   # Purple
}

CATEGORY_COLORS = {
    "Ghee":          "#1976D2",
    "Butter":        "#FFB300",
    "Palada":        "#7B1FA2",
    "UHT Milk":      "#F57C00",
    "Milk Powder":   "#00796B",
    "Instant Mixes": "#D32F2F",
}

CLUSTER_COLORS = {
    "Revenue Giants":   "#FFB300",
    "Festival Rockets": "#7B1FA2",
    "Core Portfolio":   "#1976D2",
}

ACTION_COLORS = {
    "PROTECT — Maximum stock, zero stockout tolerance":            "#388E3C",
    "INVEST — Growing high value SKU, build inventory":            "#00796B",
    "SURGE PREP — Build safety stock pre-Onam and Vishu":          "#1976D2",
    "MAINTAIN — Standard replenishment, monthly review":           "#757575",
    "SUPPORT — Recovery underway, moderate stock build":           "#FFB300",
    "MANUAL PLAN — Forecast unreliable, expert review needed":     "#F57C00",
    "DISCONTINUE REVIEW — Severely disrupted, evaluate viability": "#D32F2F",
    "FESTIVAL REVIEW — Festival SKU recovery needed":              "#7B1FA2",
    "GROW — Strong growth, increase stock allocation":             "#66BB6A",
}

# ── CSS ───────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp{{background:{WHITE};font-family:'Roboto','Segoe UI',sans-serif;}}
  section[data-testid="stSidebar"]{{background:{INDIGO};}}
  section[data-testid="stSidebar"] *{{color:{WHITE}!important;}}
  .block-container{{padding:1.5rem 2rem;}}
  .page-header{{
    background:linear-gradient(135deg,{INDIGO} 0%,{BLUE} 100%);
    padding:22px 28px;border-radius:10px;margin-bottom:24px;
  }}
  .page-header h1{{color:{WHITE}!important;font-size:1.5em;
                   font-weight:500;margin:0;letter-spacing:.3px;}}
  .page-header p{{color:rgba(255,255,255,.75);
                  margin:5px 0 0;font-size:.9em;}}
  .kpi-card{{
    background:{WHITE};border:1px solid {BORDER};
    border-radius:8px;padding:18px 22px;
    box-shadow:0 1px 4px rgba(0,0,0,.08);
    margin-bottom:16px;border-top:4px solid {BLUE};
  }}
  .kpi-card.green {{border-top-color:{GREEN};}}
  .kpi-card.amber {{border-top-color:{AMBER};}}
  .kpi-card.red   {{border-top-color:{RED};}}
  .kpi-card.purple{{border-top-color:{PURPLE};}}
  .kpi-card.teal  {{border-top-color:{TEAL};}}
  .kpi-card.orange{{border-top-color:{ORANGE};}}
  .kpi-card.pink  {{border-top-color:{PINK};}}
  .kpi-value{{font-size:1.9em;font-weight:700;
              color:{INDIGO};line-height:1.1;}}
  .kpi-label{{font-size:.78em;color:{TEXT_MID};margin-top:5px;
              font-weight:500;text-transform:uppercase;
              letter-spacing:.8px;}}
  .kpi-sub  {{font-size:.76em;color:{TEXT_LIGHT};margin-top:3px;}}
  .section-title{{
    font-size:.88em;font-weight:700;color:{INDIGO};
    border-left:3px solid {BLUE};padding-left:10px;
    margin:22px 0 12px;text-transform:uppercase;
    letter-spacing:1px;
  }}
  .insight-box{{
    background:#E3F2FD;border-left:4px solid {BLUE};
    border-radius:6px;padding:14px 18px;margin:14px 0;
    font-size:.92em;line-height:1.6;
  }}
  .insight-box.warning{{background:#FFF8E1;border-left-color:{AMBER};}}
  .insight-box.danger {{background:#FFEBEE;border-left-color:{RED};}}
  .insight-box.success{{background:#E8F5E9;border-left-color:{GREEN};}}
  .insight-box.purple {{background:#F3E5F5;border-left-color:{PURPLE};}}
  .divider{{border:none;border-top:1px solid {BORDER};margin:20px 0;}}
  .metric-big{{
    background:linear-gradient(135deg,{INDIGO},{BLUE});
    color:{WHITE};border-radius:10px;padding:20px 24px;
    text-align:center;margin-bottom:12px;
  }}
  .metric-big .val{{font-size:2.2em;font-weight:700;}}
  .metric-big .lbl{{font-size:.82em;opacity:.8;
                    text-transform:uppercase;letter-spacing:.8px;}}
  #MainMenu{{visibility:hidden;}}
  footer{{visibility:hidden;}}
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    master     = pd.read_csv("master_dairy_dataset.csv",
                              parse_dates=["Date"])
    clusters   = pd.read_csv("sku_clusters.csv")
    tournament = pd.read_csv("tournament_results.csv")
    forecast   = pd.read_csv("forecast_2026.csv",
                              parse_dates=["Date"])
    bi3        = pd.read_csv("bi3_concentration_risk.csv")
    bi7        = pd.read_csv("bi7_recovery_analysis.csv")
    recsys     = pd.read_csv("master_recommendation_table.csv")
    return master, clusters, tournament, forecast, bi3, bi7, recsys

master, clusters, tournament, forecast, bi3, bi7, recsys = load_data()


# ── Helpers ───────────────────────────────────────────────────
def kpi(value, label, sub="", color=""):
    return (f"<div class='kpi-card {color}'>"
            f"<div class='kpi-value'>{value}</div>"
            f"<div class='kpi-label'>{label}</div>"
            + (f"<div class='kpi-sub'>{sub}</div>" if sub else "")
            + "</div>")

def section(title):
    st.markdown(f"<div class='section-title'>{title}</div>",
                unsafe_allow_html=True)

def insight(text, style=""):
    st.markdown(f"<div class='insight-box {style}'>{text}</div>",
                unsafe_allow_html=True)

def fmt(fig, height=380, show_legend=True):
    fig.update_layout(
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        font=dict(color=TEXT_DARK, family="Roboto, Segoe UI"),
        height=height, showlegend=show_legend,
        legend=dict(bgcolor=WHITE, bordercolor=BORDER,
                    borderwidth=1, font=dict(size=11)),
        margin=dict(l=10, r=15, t=40, b=10),
        xaxis=dict(showgrid=True, gridcolor="#F5F5F5",
                   linecolor=BORDER, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor="#F5F5F5",
                   linecolor=BORDER, tickfont=dict(size=11)),
    )
    return fig

def hex_to_rgba(h, a=0.15):
    h = h.lstrip("#")
    r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px;'>
      <div style='font-size:2.2em;'>🥛</div>
      <div style='font-size:1.15em;font-weight:700;color:white;
                  margin-top:6px;'>MILMA</div>
      <div style='font-size:.78em;color:rgba(255,255,255,.65);'>
          Demand Intelligence System</div>
    </div>
    <hr style='border-color:rgba(255,255,255,.2);margin:12px 0;'>
    """, unsafe_allow_html=True)

    page = st.radio("Navigation", [
        "🏠  Executive Summary",
        "📊  Portfolio Overview",
        "📈  EDA — Sales Trends",
        "🔵  Clustering Results",
        "🏆  Forecasting Tournament",
        "⚠️   Portfolio Risk",
        "✅  Recommendation System",
        "🔍  Category Deep Dive",
    ], label_visibility="collapsed")

    st.markdown("""
    <hr style='border-color:rgba(255,255,255,.2);margin:16px 0 10px;'>
    <div style='font-size:.76em;color:rgba(255,255,255,.6);
                padding:0 4px;line-height:1.9;'>
      <div style='color:rgba(255,255,255,.88);font-weight:600;
                  margin-bottom:4px;'>Project Info</div>
      MSc CS Data Analytics<br>
      Malabar MILMA<br>
      46 SKUs · 6 Categories<br>
      Jan 2021 – Dec 2025<br>
      28,284 transactions
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 0 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════
if page == "🏠  Executive Summary":
    st.markdown("""
    <div class='page-header'>
      <h1>🏠 Executive Summary</h1>
      <p>MILMA Malabar · Demand Intelligence System · 
         Key findings at a glance</p>
    </div>""", unsafe_allow_html=True)

    total_rev  = master["Sales_Value"].sum()
    top3_share = bi3.nlargest(3,"Total_Revenue")["Revenue_Share_Pct"].sum()
    ghee_share = bi3[bi3["Category"]=="Ghee"]["Revenue_Share_Pct"].sum()
    growing    = len(bi7[bi7["Recovery_Status"]=="GROWING"])
    disrupted  = len(bi7[bi7["Recovery_Status"]=="DISRUPTED"])
    best_mape  = tournament["Champion_MAPE"].min()
    t1_count   = len(recsys[recsys["Planning_Tier"].str.contains("TIER 1",na=False)])
    protect    = len(recsys[recsys["Recommended_Action"].str.contains("PROTECT",na=False)])

    # Hero metrics row
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f"""
    <div class='metric-big'>
      <div class='val'>₹{total_rev/1e9:.2f}B</div>
      <div class='lbl'>5-Year Total Revenue</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown(f"""
    <div class='metric-big'>
      <div class='val'>46 SKUs</div>
      <div class='lbl'>Active Products · 6 Categories</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown(f"""
    <div class='metric-big'>
      <div class='val'>XGBoost</div>
      <div class='lbl'>Forecast Champion · 5/6 wins</div>
    </div>""", unsafe_allow_html=True)
    c4.markdown(f"""
    <div class='metric-big'>
      <div class='val'>{t1_count} SKUs</div>
      <div class='lbl'>Algorithm-Ready Forecasts</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Second row KPIs
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.markdown(kpi(f"{top3_share:.1f}%","Top 3 SKU Share",
        "Extreme concentration",color="red"),
        unsafe_allow_html=True)
    k2.markdown(kpi(f"{ghee_share:.1f}%","Ghee Dominance",
        "HHI = 0.1516",color="amber"),
        unsafe_allow_html=True)
    k3.markdown(kpi(f"{best_mape:.1f}%","Best MAPE",
        "Ghee — Excellent",color="green"),
        unsafe_allow_html=True)
    k4.markdown(kpi("0.61","Silhouette Score",
        "K-Means quality",color="teal"),
        unsafe_allow_html=True)
    k5.markdown(kpi(str(growing),"Growing SKUs",
        "At all-time peak",color="green"),
        unsafe_allow_html=True)
    k6.markdown(kpi(str(disrupted),"Disrupted SKUs",
        "Need strategic review",color="red"),
        unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    col1,col2 = st.columns([3,2], gap="large")

    with col1:
        section("5-Year Revenue Trend — All Categories")
        monthly_all = master.groupby(["Date","Category"])[
            "Sales_Value"].sum().reset_index()
        fig = px.area(monthly_all, x="Date", y="Sales_Value",
                      color="Category",
                      color_discrete_map=CATEGORY_COLORS)
        fig.update_traces(line=dict(width=1.5))
        fmt(fig, height=320)
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Monthly Revenue (₹)",
            legend=dict(orientation="h",y=-0.18,x=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Critical Findings")
        insight(f"<b style='color:{RED};'>⚠️ Concentration Risk</b><br>"
                f"3 SKUs = <b>{top3_share:.1f}%</b> of revenue. "
                "Zero stockout tolerance on Ghee 500ml, "
                "15kg Tin, 200ml Pet.",style="danger")
        insight(f"<b style='color:{PURPLE};'>🎉 Festival Dependency</b><br>"
                "Ghee and Palada spike <b>2–5×</b> during "
                "Onam (Aug) and Vishu (Apr). "
                "Surge stock 6 weeks before.",style="purple")
        insight(f"<b style='color:{GREEN};'>✅ Forecast Reliability</b><br>"
                f"<b>{t1_count} SKUs</b> have reliable forecasts "
                "(MAPE &lt;30%). Ghee 12%, Palada 19%. "
                "Use directly for procurement.",style="success")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("Three-Step Methodology")

    m1,m2,m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div style='background:#E3F2FD;border-radius:10px;
                    padding:20px;text-align:center;'>
          <div style='font-size:2em;'>🔵</div>
          <div style='font-weight:700;color:{INDIGO};
                      margin:8px 0 4px;font-size:1em;'>
            Step 1 — Clustering</div>
          <div style='font-size:.88em;color:{TEXT_MID};
                      line-height:1.6;'>
            K-Means groups 46 SKUs into 3 demand segments
            by revenue, volatility, and seasonality.<br>
            <b>Silhouette = 0.61</b>
          </div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div style='background:#E8F5E9;border-radius:10px;
                    padding:20px;text-align:center;'>
          <div style='font-size:2em;'>🏆</div>
          <div style='font-weight:700;color:{INDIGO};
                      margin:8px 0 4px;font-size:1em;'>
            Step 2 — Forecasting</div>
          <div style='font-size:.88em;color:{TEXT_MID};
                      line-height:1.6;'>
            Prophet vs XGBoost tournament on identical
            12-month holdout. XGBoost wins 5/6.<br>
            <b>Best MAPE: 12.07%</b>
          </div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div style='background:#F3E5F5;border-radius:10px;
                    padding:20px;text-align:center;'>
          <div style='font-size:2em;'>✅</div>
          <div style='font-weight:700;color:{INDIGO};
                      margin:8px 0 4px;font-size:1em;'>
            Step 3 — Recommendations</div>
          <div style='font-size:.88em;color:{TEXT_MID};
                      line-height:1.6;'>
            9 action types per SKU combining cluster,
            forecast quality, HHI, and recovery status.<br>
            <b>42 SKUs covered</b>
          </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 1 — PORTFOLIO OVERVIEW
# ══════════════════════════════════════════════════════════════
elif page == "📊  Portfolio Overview":
    st.markdown("""
    <div class='page-header'>
      <h1>📊 Portfolio Overview</h1>
      <p>Malabar MILMA · Shelf Stable Dairy · 2021–2025</p>
    </div>""", unsafe_allow_html=True)

    total_rev  = master["Sales_Value"].sum()
    total_sku  = master["Product"].nunique()
    top3_share = bi3.nlargest(3,"Total_Revenue")["Revenue_Share_Pct"].sum()
    ghee_share = bi3[bi3["Category"]=="Ghee"]["Revenue_Share_Pct"].sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi(f"₹{total_rev/1e9:.2f}B",
        "Total Portfolio Revenue","5-year 2021–2025"),
        unsafe_allow_html=True)
    c2.markdown(kpi(str(total_sku),
        "Total Active SKUs","6 categories"),
        unsafe_allow_html=True)
    c3.markdown(kpi(f"{top3_share:.1f}%",
        "Top 3 SKUs Revenue Share","Extreme concentration",
        color="amber"),unsafe_allow_html=True)
    c4.markdown(kpi(f"{ghee_share:.1f}%",
        "Ghee Category Dominance","HHI = 0.1516",
        color="red"),unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col1,col2 = st.columns(2, gap="large")

    with col1:
        section("Revenue Distribution by Category")
        cat_rev = master.groupby("Category")[
            "Sales_Value"].sum().reset_index()
        fig = px.pie(cat_rev, values="Sales_Value",
                     names="Category", hole=0.55,
                     color="Category",
                     color_discrete_map=CATEGORY_COLORS)
        fig.update_traces(
            textposition="outside",
            textinfo="percent+label", textfont_size=12,
            marker=dict(line=dict(color=WHITE,width=2)))
        fig.update_layout(
            showlegend=False, paper_bgcolor=WHITE,
            height=340, margin=dict(l=20,r=20,t=10,b=10),
            annotations=[dict(
                text=f"<b>₹{total_rev/1e9:.2f}B</b><br>Total",
                x=0.5,y=0.5,font_size=14,
                font_color=INDIGO,showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Top 10 SKUs by Revenue")
        top10 = bi3.nlargest(10,"Total_Revenue").copy()
        top10 = top10.sort_values("Total_Revenue")
        bc = [RED   if f=="CRITICAL" else
              AMBER if f=="HIGH"     else BLUE
              for f in top10["Concentration_Flag"]]
        fig2 = go.Figure(go.Bar(
            x=top10["Total_Revenue"],y=top10["Product"],
            orientation="h",
            marker_color=bc,marker_line_width=0,
            text=[f"₹{v/1e6:.0f}M"
                  for v in top10["Total_Revenue"]],
            textposition="outside",
            textfont=dict(size=11,color=TEXT_DARK)))
        fmt(fig2, height=340, show_legend=False)
        fig2.update_layout(
            xaxis_title="Total Revenue (₹)",
            yaxis=dict(tickfont=dict(size=10)),
            margin=dict(l=10,r=70,t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"""
    <div style='font-size:.8em;color:{TEXT_MID};
                margin-top:-8px;margin-bottom:16px;'>
      <span style='color:{RED};font-weight:600;'>■ CRITICAL</span> &nbsp;
      <span style='color:{AMBER};font-weight:600;'>■ HIGH</span> &nbsp;
      <span style='color:{BLUE};font-weight:600;'>■ STANDARD</span>
      &nbsp;concentration flag
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("Key Findings")
    r1,r2,r3 = st.columns(3)
    with r1:
        insight(f"<b style='color:{RED};'>⚠️ Extreme Concentration</b><br>"
                "3 SKUs generate <b>60%</b> of total revenue. "
                "Any Ghee supply disruption is a business-level risk.",
                style="danger")
    with r2:
        insight(f"<b style='color:{AMBER};'>📅 Festival Dependency</b><br>"
                "Ghee and Palada show <b>2–5× revenue spikes</b> "
                "during Onam (Aug) and Vishu (Apr).",
                style="warning")
    with r3:
        insight(f"<b style='color:{GREEN};'>📈 Growth Signal</b><br>"
                "<b>17 SKUs</b> at all-time revenue peaks. "
                "Butter and Milk Powder strongest growth in 2025.",
                style="success")


# ══════════════════════════════════════════════════════════════
# PAGE 2 — EDA
# ══════════════════════════════════════════════════════════════
elif page == "📈  EDA — Sales Trends":
    st.markdown("""
    <div class='page-header'>
      <h1>📈 Exploratory Data Analysis</h1>
      <p>Sales trends · seasonality patterns · 
         year-on-year growth · 2021–2025</p>
    </div>""", unsafe_allow_html=True)

    f1,f2,_ = st.columns([2,2,3])
    with f1:
        sel_cat = st.multiselect("Category",
            sorted(master["Category"].unique()),
            default=sorted(master["Category"].unique()))
    with f2:
        sel_year = st.multiselect("Year",
            sorted(master["Year"].unique()),
            default=sorted(master["Year"].unique()))

    df = master[master["Category"].isin(sel_cat) &
                master["Year"].isin(sel_year)]

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi(f"₹{df['Sales_Value'].sum()/1e9:.2f}B",
        "Revenue (Filtered)"),unsafe_allow_html=True)
    c2.markdown(kpi(str(df["Product"].nunique()),
        "SKUs in Selection"),unsafe_allow_html=True)
    peak_m = df.groupby("Month_Name")["Sales_Value"].mean().idxmax()
    c3.markdown(kpi(peak_m,"Peak Month (Avg)",color="amber"),
        unsafe_allow_html=True)
    best_c = df.groupby("Category")["Sales_Value"].sum().idxmax()
    c4.markdown(kpi(best_c,"Top Category",color="green"),
        unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Year-colored line chart (Power BI style) ──────────────
    section("Monthly Revenue Comparison 2021–2025  (Each line = one year)")

    # Aggregate total across selected categories, grouped by Month+Year
    df_trend = df.groupby(["Year","Month_No","Month_Name"])[
        "Sales_Value"].sum().reset_index()
    df_trend = df_trend.sort_values(["Year","Month_No"])

    MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    # Abbreviate month names if needed
    abbr = {"January":"Jan","February":"Feb","March":"Mar",
            "April":"Apr","May":"May","June":"Jun",
            "July":"Jul","August":"Aug","September":"Sep",
            "October":"Oct","November":"Nov","December":"Dec"}
    df_trend["Month_Abbr"] = df_trend["Month_Name"].map(
        lambda x: abbr.get(x, x[:3]))

    fig_yr = go.Figure()
    for yr in sorted(df_trend["Year"].unique()):
        yd = df_trend[df_trend["Year"]==yr].copy()
        yd = yd.sort_values("Month_No")
        col = YEAR_COLORS.get(int(yr), BLUE)
        fig_yr.add_trace(go.Scatter(
            x=yd["Month_Abbr"],
            y=yd["Sales_Value"],
            name=str(int(yr)),
            mode="lines+markers",
            line=dict(color=col, width=2.5),
            marker=dict(size=7, color=col,
                        line=dict(color=WHITE,width=1.5)),
            hovertemplate=(
                f"<b>{int(yr)}</b><br>"
                "%{x}: ₹%{y:,.0f}<extra></extra>")))

    fig_yr.update_layout(
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        height=360,
        font=dict(color=TEXT_DARK, family="Roboto, Segoe UI"),
        margin=dict(l=10,r=15,t=10,b=10),
        xaxis=dict(
            categoryorder="array",
            categoryarray=MONTH_ORDER,
            showgrid=True, gridcolor="#F5F5F5",
            linecolor=BORDER, tickfont=dict(size=12)),
        yaxis=dict(
            title="Monthly Revenue (₹)",
            showgrid=True, gridcolor="#F5F5F5",
            linecolor=BORDER, tickfont=dict(size=11)),
        legend=dict(
            title="Year",orientation="h",
            y=-0.18,x=0,bgcolor=WHITE,
            bordercolor=BORDER,borderwidth=1,
            font=dict(size=12)),
        showlegend=True,
        hovermode="x unified")
    st.plotly_chart(fig_yr, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col1,col2 = st.columns(2, gap="large")

    with col1:
        section("Monthly Seasonality Heatmap")
        heat = master.groupby(["Category","Month_No"])[
            "Sales_Value"].mean().reset_index()
        hp = heat.pivot(index="Category",
                        columns="Month_No",values="Sales_Value")
        mn = ["Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec"]
        fig2 = go.Figure(go.Heatmap(
            z=hp.values, x=mn, y=hp.index.tolist(),
            colorscale=[[0,"#E3F2FD"],
                        [0.5,"#1976D2"],
                        [1,"#0D47A1"]],
            text=[[f"₹{v/1e6:.1f}M" for v in row]
                  for row in hp.values],
            texttemplate="%{text}",
            textfont=dict(size=9,color=WHITE),
            showscale=False))
        fig2.update_layout(
            paper_bgcolor=WHITE,plot_bgcolor=WHITE,
            height=280,margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(tickfont=dict(size=11)),
            yaxis=dict(tickfont=dict(size=11)))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        section("Annual Revenue by Category")
        annual = master.groupby(["Year","Category"])[
            "Sales_Value"].sum().reset_index()
        fig3 = px.bar(annual,x="Year",y="Sales_Value",
                      color="Category",barmode="group",
                      color_discrete_map=CATEGORY_COLORS)
        fmt(fig3,height=280)
        fig3.update_layout(
            xaxis_title="Year",yaxis_title="Revenue (₹)",
            xaxis=dict(tickmode="linear"),
            legend=dict(orientation="h",y=-0.3,
                        x=0,font=dict(size=10)))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("Year-on-Year Revenue Growth (%) by Category")
    yoy = master.groupby(["Year","Category"])[
        "Sales_Value"].sum().reset_index()
    yoy["YoY"] = yoy.groupby("Category")[
        "Sales_Value"].pct_change()*100
    yp = yoy.pivot(index="Category",
                   columns="Year",values="YoY").round(1)
    fig4 = go.Figure(go.Heatmap(
        z=yp.values,
        x=[str(y) for y in yp.columns],
        y=yp.index.tolist(),
        colorscale=[[0,"#FFEBEE"],[0.5,"#FAFAFA"],
                    [1,"#E8F5E9"]],
        zmid=0,
        text=[[f"{v:+.1f}%" if not np.isnan(v) else "—"
               for v in row] for row in yp.values],
        texttemplate="%{text}",
        textfont=dict(size=12,color=TEXT_DARK),
        showscale=False))
    fig4.update_layout(
        paper_bgcolor=WHITE,plot_bgcolor=WHITE,
        height=240,margin=dict(l=10,r=10,t=10,b=10),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)))
    st.plotly_chart(fig4, use_container_width=True)
    insight("🟢 Green = revenue growth vs prior year · "
            "🔴 Red = revenue decline · "
            "UHT Milk shows red from 2022 onwards · "
            "Butter and Milk Powder bright green in 2025")


# ══════════════════════════════════════════════════════════════
# PAGE 3 — CLUSTERING
# ══════════════════════════════════════════════════════════════
elif page == "🔵  Clustering Results":
    st.markdown("""
    <div class='page-header'>
      <h1>🔵 K-Means Clustering — Product Segmentation</h1>
      <p>Unsupervised ML · 46 SKUs · 3 demand segments · 
         Silhouette Score 0.61</p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi("3","Clusters Found",
        "Optimal K confirmed"),unsafe_allow_html=True)
    c2.markdown(kpi("0.61","Silhouette Score",
        "Well-separated",color="green"),unsafe_allow_html=True)
    c3.markdown(kpi("3 SKUs","Revenue Giants",
        "60% of revenue",color="amber"),unsafe_allow_html=True)
    c4.markdown(kpi("4 SKUs","Festival Rockets",
        "Onam & Vishu",color="purple"),unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    sel_cl = st.multiselect("Filter Cluster",
        clusters["Cluster_Name"].dropna().unique(),
        default=list(clusters["Cluster_Name"].dropna().unique()))
    df_cl = clusters[clusters["Cluster_Name"].isin(sel_cl)]

    col1,col2 = st.columns([3,2],gap="large")
    with col1:
        section("Volatility vs Seasonality — Interactive Scatter")
        fig1 = px.scatter(df_cl,
            x="Volatility_CV",y="Seasonality_Strength",
            color="Cluster_Name",size="Total_Revenue",
            hover_name="Product",
            hover_data={"Category":True,
                        "Total_Revenue":":,.0f",
                        "Cluster_Name":False},
            color_discrete_map=CLUSTER_COLORS,size_max=55)
        fmt(fig1,height=400)
        fig1.update_layout(
            xaxis_title="Demand Volatility (CV)",
            yaxis_title="Seasonality Strength",
            legend=dict(title="Cluster",
                        orientation="h",y=-0.15,x=0))
        fig1.update_traces(marker=dict(
            line=dict(color=WHITE,width=1.5),opacity=0.85))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        section("Revenue by Cluster")
        cl_rev = clusters.groupby("Cluster_Name")[
            "Total_Revenue"].sum().reset_index()
        fig2 = px.pie(cl_rev,values="Total_Revenue",
                      names="Cluster_Name",hole=0.5,
                      color="Cluster_Name",
                      color_discrete_map=CLUSTER_COLORS)
        fig2.update_traces(
            textposition="outside",
            textinfo="percent+label",textfont_size=12,
            marker=dict(line=dict(color=WHITE,width=2)))
        fig2.update_layout(showlegend=False,
            paper_bgcolor=WHITE,height=240,
            margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)

        section("Cluster Summary")
        cs = clusters.groupby("Cluster_Name").agg(
            SKUs=("Product","count"),
            Revenue=("Total_Revenue","sum")).reset_index()
        cs["Rev %"] = (cs["Revenue"]/
            cs["Revenue"].sum()*100).round(1)
        cs["Revenue"] = cs["Revenue"].apply(
            lambda x: f"₹{x/1e6:.0f}M")
        st.dataframe(
            cs[["Cluster_Name","SKUs","Rev %","Revenue"]]
              .rename(columns={"Cluster_Name":"Cluster"}),
            hide_index=True,use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("SKU Cluster Assignment Table")
    dc = df_cl[["Product","Category","Cluster_Name",
                "Total_Revenue","Volatility_CV",
                "Seasonality_Strength"]]\
         .sort_values("Total_Revenue",ascending=False).copy()
    dc["Total_Revenue"] = dc["Total_Revenue"].apply(
        lambda x: f"₹{x/1e6:.2f}M")
    dc.columns = ["Product","Category","Cluster",
                  "Revenue","Volatility CV","Seasonality"]
    st.dataframe(dc,hide_index=True,use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    r1,r2,r3 = st.columns(3)
    with r1:
        insight(f"<b style='color:{AMBER};'>💰 Revenue Giants</b><br>"
                "3 SKUs · 60.4% of portfolio. Ghee 500ml, "
                "15kg, 200ml. <b>Zero stockout tolerance.</b>",
                style="warning")
    with r2:
        insight(f"<b style='color:{PURPLE};'>🎉 Festival Rockets</b><br>"
                "4 SKUs · extreme Onam & Vishu spikes. "
                "<b>Surge stock 6 weeks before festivals.</b>",
                style="purple")
    with r3:
        insight(f"<b style='color:{GREEN};'>📦 Core Portfolio</b><br>"
                "35 SKUs · stable predictable demand. "
                "<b>Monthly review sufficient.</b>",style="success")


# ══════════════════════════════════════════════════════════════
# PAGE 4 — FORECASTING
# ══════════════════════════════════════════════════════════════
elif page == "🏆  Forecasting Tournament":
    st.markdown("""
    <div class='page-header'>
      <h1>🏆 Prophet vs XGBoost — Forecasting Tournament</h1>
      <p>Fair comparison · identical 12-month holdout 
         Jan–Dec 2025 · 2026 demand forecasts</p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi("XGBoost","Tournament Champion",
        "Wins 5 of 6",color="green"),unsafe_allow_html=True)
    c2.markdown(kpi("12.07%","Best MAPE — Ghee",
        "Excellent accuracy",color="green"),unsafe_allow_html=True)
    c3.markdown(kpi("2 / 6","Excellent Forecasts",
        "MAPE below 20%"),unsafe_allow_html=True)
    c4.markdown(kpi("3 / 6","Need Manual Planning",
        "MAPE above 70%",color="red"),unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col1,col2 = st.columns(2,gap="large")

    with col1:
        section("Tournament Results Table")
        def q_style(v):
            if v=="Excellent":
                return f"background:#E8F5E9;color:{GREEN};font-weight:600"
            elif v=="Acceptable":
                return f"background:#FFF8E1;color:{AMBER};font-weight:600"
            return f"background:#FFEBEE;color:{RED};font-weight:600"
        def m_style(v):
            try:
                f=float(v)
                if f<20: return f"color:{GREEN};font-weight:600"
                if f<50: return f"color:{AMBER};font-weight:600"
                return f"color:{RED};font-weight:600"
            except: return ""

        ts = tournament[["Category","Prophet_MAPE",
                          "XGBoost_MAPE","Champion",
                          "Champion_MAPE","Quality"]].copy()
        ts.columns = ["Category","Prophet %","XGBoost %",
                      "Champion","Best MAPE %","Quality"]
        styled = (ts.style
            .applymap(q_style,subset=["Quality"])
            .applymap(m_style,subset=["Prophet %",
                                       "XGBoost %",
                                       "Best MAPE %"])
            .format({"Prophet %":"{:.2f}",
                     "XGBoost %":"{:.2f}",
                     "Best MAPE %":"{:.2f}"})
            .set_properties(**{"text-align":"center",
                                "font-size":"13px"}))
        st.dataframe(styled,hide_index=True,
                     use_container_width=True)

    with col2:
        section("MAPE Comparison — Prophet vs XGBoost")
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            name="Prophet",x=tournament["Category"],
            y=tournament["Prophet_MAPE"],
            marker_color=PURPLE,marker_line_width=0,
            text=tournament["Prophet_MAPE"].round(1),
            textposition="outside",
            textfont=dict(size=10)))
        fig1.add_trace(go.Bar(
            name="XGBoost",x=tournament["Category"],
            y=tournament["XGBoost_MAPE"],
            marker_color=BLUE,marker_line_width=0,
            text=tournament["XGBoost_MAPE"].round(1),
            textposition="outside",
            textfont=dict(size=10)))
        fig1.add_hline(y=20,line_dash="dot",
            line_color=GREEN,line_width=1.5,
            annotation_text="Excellent ≤20%",
            annotation_font_color=GREEN,
            annotation_font_size=10)
        fig1.add_hline(y=50,line_dash="dot",
            line_color=RED,line_width=1.5,
            annotation_text="Poor >50%",
            annotation_font_color=RED,
            annotation_font_size=10)
        fig1.update_layout(barmode="group")
        fmt(fig1,height=340)
        fig1.update_layout(
            yaxis_title="MAPE (%)",
            legend=dict(orientation="h",y=-0.2,x=0.3))
        st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("2026 Monthly Demand Forecast")
    sel_cat_f = st.multiselect(
        "Select categories",
        options=sorted(forecast["Category"].unique()),
        default=sorted(forecast["Category"].unique()))

    if sel_cat_f:
        ff = forecast[forecast["Category"].isin(sel_cat_f)].copy()
        fig2 = go.Figure()
        for cat in sel_cat_f:
            cd = ff[ff["Category"]==cat].copy()
            col = CATEGORY_COLORS.get(cat,BLUE)
            rgba_fill = hex_to_rgba(col,0.12)
            has_ci = ("Upper_95" in cd.columns and
                      "Lower_95" in cd.columns and
                      cd["Upper_95"].notna().any())
            if has_ci:
                xb = list(cd["Date"]) + \
                     list(cd["Date"].iloc[::-1])
                yb = list(cd["Upper_95"]) + \
                     list(cd["Lower_95"].iloc[::-1])
                fig2.add_trace(go.Scatter(
                    x=xb,y=yb,fill="toself",
                    fillcolor=rgba_fill,
                    line=dict(color="rgba(0,0,0,0)"),
                    showlegend=False,hoverinfo="skip",
                    mode="lines"))
            fig2.add_trace(go.Scatter(
                x=cd["Date"],y=cd["Forecast"],
                name=cat,
                line=dict(color=col,width=2.5),
                mode="lines+markers",
                marker=dict(size=7,color=col,
                            line=dict(color=WHITE,width=1.5))))
        fmt(fig2,height=400)
        fig2.update_layout(
            xaxis_title="Month (2026)",
            yaxis_title="Forecast Revenue (₹)",
            legend=dict(orientation="h",y=-0.18,x=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    r1,r2 = st.columns(2)
    with r1:
        insight(f"<b style='color:{GREEN};'>✅ Why XGBoost Won 5/6</b><br>"
                "2025 structural changes violated Prophet's decomposition "
                "assumptions. XGBoost's <b>year encoding and lag features</b> "
                "adapted better to structural demand shifts.",style="success")
    with r2:
        insight(f"<b style='color:{AMBER};'>⚠️ Why 3 Categories Failed</b><br>"
                "UHT Milk (85% collapse), Milk Powder (product expansion 2025), "
                "Instant Mixes (CV=1.998). "
                "<b>No model predicts structural breaks.</b>",style="warning")


# ══════════════════════════════════════════════════════════════
# PAGE 5 — PORTFOLIO RISK
# ══════════════════════════════════════════════════════════════
elif page == "⚠️   Portfolio Risk":
    st.markdown("""
    <div class='page-header'>
      <h1>⚠️ Portfolio Risk Analysis</h1>
      <p>Concentration risk (HHI) · demand recovery 
         classification · 46 SKUs</p>
    </div>""", unsafe_allow_html=True)

    critical  = len(bi3[bi3["Concentration_Flag"]=="CRITICAL"])
    disrupted = len(bi7[bi7["Recovery_Status"]=="DISRUPTED"])
    growing   = len(bi7[bi7["Recovery_Status"]=="GROWING"])
    top3_sh   = bi3.nlargest(3,"Total_Revenue")["Revenue_Share_Pct"].sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi(str(critical),"CRITICAL SKUs",
        "Each >10% of portfolio",color="red"),unsafe_allow_html=True)
    c2.markdown(kpi(f"{top3_sh:.1f}%","Top 3 Revenue Share",
        "3-6-40 rule",color="amber"),unsafe_allow_html=True)
    c3.markdown(kpi(str(growing),"Growing SKUs",
        "At all-time peak",color="green"),unsafe_allow_html=True)
    c4.markdown(kpi(str(disrupted),"Disrupted SKUs",
        "Below peak",color="red"),unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col1,col2 = st.columns(2,gap="large")

    with col1:
        section("Concentration Flag Distribution")
        conc = bi3["Concentration_Flag"].value_counts().reset_index()
        conc.columns = ["Flag","Count"]
        fc = {"CRITICAL":RED,"HIGH":ORANGE,"MODERATE":AMBER,"LOW":BLUE}
        fig1 = px.pie(conc,values="Count",names="Flag",hole=0.5,
                      color="Flag",color_discrete_map=fc)
        fig1.update_traces(
            textposition="outside",
            textinfo="percent+label",textfont_size=12,
            marker=dict(line=dict(color=WHITE,width=2)))
        fig1.update_layout(showlegend=False,
            paper_bgcolor=WHITE,height=280,
            margin=dict(l=20,r=20,t=10,b=10))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        section("Recovery Status Distribution")
        rec = bi7["Recovery_Status"].value_counts().reset_index()
        rec.columns = ["Status","Count"]
        rc = {"GROWING":GREEN,"STABLE":TEAL,
              "RECOVERING":AMBER,"DISRUPTED":RED}
        fig2 = px.pie(rec,values="Count",names="Status",hole=0.5,
                      color="Status",color_discrete_map=rc)
        fig2.update_traces(
            textposition="outside",
            textinfo="percent+label",textfont_size=12,
            marker=dict(line=dict(color=WHITE,width=2)))
        fig2.update_layout(showlegend=False,
            paper_bgcolor=WHITE,height=280,
            margin=dict(l=20,r=20,t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("SKU Recovery Rate vs Peak Revenue")
    rs = bi7.sort_values("Recovery_Rate_Pct")
    bc = [RED if r<50 else AMBER if r<90 else GREEN
          for r in rs["Recovery_Rate_Pct"]]
    fig3 = go.Figure(go.Bar(
        x=rs["Recovery_Rate_Pct"],y=rs["Product"],
        orientation="h",marker_color=bc,marker_line_width=0,
        text=rs["Recovery_Rate_Pct"].round(0)
              .astype(int).astype(str)+"%",
        textposition="outside",
        textfont=dict(size=9,color=TEXT_DARK)))
    fig3.add_vline(x=100,line_dash="dash",
        line_color=TEXT_MID,line_width=1,
        annotation_text="Peak 100%",
        annotation_font_size=10,
        annotation_font_color=TEXT_MID)
    fmt(fig3,height=680,show_legend=False)
    fig3.update_layout(
        xaxis_title="Recovery Rate % vs Peak Year",
        yaxis=dict(tickfont=dict(size=9)),
        margin=dict(l=10,r=70,t=20,b=10))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("Severely Disrupted SKUs")
    dd = bi7[bi7["Recovery_Status"]=="DISRUPTED"][[
        "Product","Category","Peak_Year",
        "Recovery_Rate_Pct","YoY_Growth_Pct"]].copy()
    dd.columns = ["Product","Category","Peak Year",
                  "Recovery Rate %","YoY Growth %"]
    st.dataframe(dd.sort_values("Recovery Rate %"),
                 hide_index=True,use_container_width=True)
    insight("<b>Ok Ghee 50ml</b> — Peak ₹47.3M (2021) → "
            "Current ₹1.9M (2025) · 96% collapse · "
            "Highest priority for discontinuation review.",
            style="danger")


# ══════════════════════════════════════════════════════════════
# PAGE 6 — RECOMMENDATION SYSTEM
# ══════════════════════════════════════════════════════════════
elif page == "✅  Recommendation System":
    st.markdown("""
    <div class='page-header'>
      <h1>✅ SKU Demand Planning Recommendations</h1>
      <p>Integrated output · clustering · forecasting · 
         concentration risk · recovery analysis · 42 SKUs</p>
    </div>""", unsafe_allow_html=True)

    t1 = len(recsys[recsys["Planning_Tier"].str.contains("TIER 1",na=False)])
    t2 = len(recsys[recsys["Planning_Tier"].str.contains("TIER 2",na=False)])
    t3 = len(recsys[recsys["Planning_Tier"].str.contains("TIER 3",na=False)])
    protect = len(recsys[recsys["Recommended_Action"]
        .str.contains("PROTECT",na=False)])

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi(str(t1),"Tier 1 — Algorithm",
        "Forecasts trusted",color="green"),unsafe_allow_html=True)
    c2.markdown(kpi(str(t2),"Tier 2 — Caution",
        "Validate before order",color="amber"),unsafe_allow_html=True)
    c3.markdown(kpi(str(t3),"Tier 3 — Manual",
        "Human judgment needed",color="red"),unsafe_allow_html=True)
    c4.markdown(kpi(str(protect),"PROTECT SKUs",
        "Zero stockout tolerance"),unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("Filters")
    f1,f2,f3,f4 = st.columns(4)
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
        f"<p style='color:{TEXT_MID};font-size:.85em;'>"
        f"Showing {len(dr)} of {len(recsys)} SKUs</p>",
        unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col1,col2 = st.columns(2,gap="large")

    with col1:
        section("Recommended Actions Distribution")
        ac = dr["Recommended_Action"].value_counts().reset_index()
        ac.columns = ["Action","Count"]
        ac["Short"] = ac["Action"].str.split("—").str[0].str.strip()
        ac = ac.sort_values("Count")
        fig1 = go.Figure(go.Bar(
            x=ac["Count"],y=ac["Short"],orientation="h",
            marker_color=[ACTION_COLORS.get(a,BLUE) for a in ac["Action"]],
            marker_line_width=0,
            text=ac["Count"],textposition="outside",
            textfont=dict(size=11)))
        fmt(fig1,height=320,show_legend=False)
        fig1.update_layout(xaxis_title="Number of SKUs",
                           yaxis=dict(tickfont=dict(size=10)))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        section("Planning Tier Split")
        tc = dr["Planning_Tier"].value_counts().reset_index()
        tc.columns = ["Tier","Count"]
        tc["Short"] = tc["Tier"].str.split("—").str[0].str.strip()
        tcols = [GREEN if "TIER 1" in t else
                 AMBER if "TIER 2" in t else RED
                 for t in tc["Tier"]]
        fig2 = px.pie(tc,values="Count",names="Short",hole=0.5,
                      color_discrete_sequence=tcols)
        fig2.update_traces(
            textposition="outside",
            textinfo="percent+label",textfont_size=12,
            marker=dict(line=dict(color=WHITE,width=2)))
        fig2.update_layout(showlegend=False,
            paper_bgcolor=WHITE,height=240,
            margin=dict(l=20,r=20,t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)

        section("Top 10 Priority SKUs")
        tp = dr.nlargest(10,"Priority_Score")[[
            "Product","Priority_Score","Recommended_Action"]].copy()
        tp["Action"] = tp["Recommended_Action"]\
            .str.split("—").str[0].str.strip()
        tp["Priority"] = tp["Priority_Score"].round(1)
        st.dataframe(tp[["Product","Priority","Action"]],
                     hide_index=True,use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("Master SKU Recommendation Table")
    dcols = ["Product","Category","Cluster_Name",
             "Concentration_Flag","Recovery_Status",
             "Planning_Tier","Champion_MAPE",
             "Priority_Score","Recommended_Action"]
    dcols = [c for c in dcols if c in dr.columns]
    tbl = dr[dcols].sort_values("Priority_Score",ascending=False).copy()
    if "Champion_MAPE" in tbl.columns:
        tbl["Champion_MAPE"] = tbl["Champion_MAPE"].round(2)
    if "Priority_Score" in tbl.columns:
        tbl["Priority_Score"] = tbl["Priority_Score"].round(1)

    def style_row(row):
        act   = row.get("Recommended_Action","")
        color = ACTION_COLORS.get(act,"")
        base  = f"color:{TEXT_DARK}"
        if color:
            r2=int(color[1:3],16)
            g2=int(color[3:5],16)
            b2=int(color[5:7],16)
            bg=f"rgba({r2},{g2},{b2},0.12)"
            return [f"background:{bg};color:{TEXT_DARK};font-weight:600"
                    if col=="Recommended_Action" else base
                    for col in row.index]
        return [base for _ in row.index]

    st.dataframe(
        tbl.style.apply(style_row,axis=1)
           .set_properties(**{"font-size":"12px",
                               "border":f"1px solid {BORDER}"}),
        hide_index=True,use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    r1,r2,r3 = st.columns(3)
    with r1:
        insight(f"<b style='color:{GREEN};'>✅ Tier 1 — {t1} SKUs</b><br>"
                "Use forecasts directly for procurement. "
                "Ghee, Butter, Palada.",style="success")
    with r2:
        insight(f"<b style='color:{AMBER};'>⚡ Tier 2 — {t2} SKUs</b><br>"
                "Validate before ordering. "
                "Disrupted Ghee and recovering Palada.",style="warning")
    with r3:
        insight(f"<b style='color:{RED};'>❌ Tier 3 — {t3} SKUs</b><br>"
                "Human expert review required. "
                "UHT Milk, Milk Powder, Instant Mixes.",style="danger")


# ══════════════════════════════════════════════════════════════
# PAGE 7 — CATEGORY DEEP DIVE
# ══════════════════════════════════════════════════════════════
elif page == "🔍  Category Deep Dive":
    st.markdown("""
    <div class='page-header'>
      <h1>🔍 Category Deep Dive</h1>
      <p>Select any category to explore all SKUs in detail — 
         revenue · cluster · forecast · action</p>
    </div>""", unsafe_allow_html=True)

    sel = st.selectbox("Select Category",
        sorted(master["Category"].unique()))

    cat_master   = master[master["Category"]==sel]
    cat_clusters = clusters[clusters["Category"]==sel]
    cat_bi3      = bi3[bi3["Category"]==sel]
    cat_bi7      = bi7[bi7["Category"]==sel]
    cat_recsys   = recsys[recsys["Category"]==sel]
    cat_tour     = tournament[tournament["Category"]==sel]

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Category KPIs
    cat_rev   = cat_master["Sales_Value"].sum()
    cat_skus  = cat_master["Product"].nunique()
    total_rev = master["Sales_Value"].sum()
    cat_share = cat_rev / total_rev * 100
    cat_mape  = cat_tour["Champion_MAPE"].values[0] \
                if len(cat_tour) > 0 else None
    cat_champ = cat_tour["Champion"].values[0] \
                if len(cat_tour) > 0 else "N/A"

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi(f"₹{cat_rev/1e6:.0f}M",
        "Category Revenue","5-year total"),
        unsafe_allow_html=True)
    c2.markdown(kpi(str(cat_skus),
        "SKUs in Category",""),unsafe_allow_html=True)
    c3.markdown(kpi(f"{cat_share:.1f}%",
        "Portfolio Share","",
        color="amber" if cat_share>50 else ""),
        unsafe_allow_html=True)
    mape_col = "green" if cat_mape and cat_mape<20 \
               else "amber" if cat_mape and cat_mape<50 \
               else "red"
    c4.markdown(kpi(
        f"{cat_mape:.1f}%" if cat_mape else "N/A",
        f"Best Model MAPE",f"Champion: {cat_champ}",
        color=mape_col),unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col1,col2 = st.columns(2,gap="large")

    with col1:
        section(f"{sel} — Monthly Revenue Trend by Year")
        ct = cat_master.groupby(["Year","Month_No","Month_Name"])[
            "Sales_Value"].sum().reset_index()
        abbr = {"January":"Jan","February":"Feb","March":"Mar",
                "April":"Apr","May":"May","June":"Jun",
                "July":"Jul","August":"Aug","September":"Sep",
                "October":"Oct","November":"Nov","December":"Dec"}
        ct["Month_Abbr"] = ct["Month_Name"].map(
            lambda x: abbr.get(x,x[:3]))
        fig1 = go.Figure()
        MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun",
                       "Jul","Aug","Sep","Oct","Nov","Dec"]
        for yr in sorted(ct["Year"].unique()):
            yd = ct[ct["Year"]==yr].sort_values("Month_No")
            col_yr = YEAR_COLORS.get(int(yr),BLUE)
            fig1.add_trace(go.Scatter(
                x=yd["Month_Abbr"],y=yd["Sales_Value"],
                name=str(int(yr)),mode="lines+markers",
                line=dict(color=col_yr,width=2.5),
                marker=dict(size=7,color=col_yr,
                            line=dict(color=WHITE,width=1.5)),
                hovertemplate=(f"<b>{int(yr)}</b><br>"
                               "%{x}: ₹%{y:,.0f}<extra></extra>")))
        fig1.update_layout(
            paper_bgcolor=WHITE,plot_bgcolor=WHITE,height=300,
            font=dict(color=TEXT_DARK),
            margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(categoryorder="array",
                       categoryarray=MONTH_ORDER,
                       showgrid=True,gridcolor="#F5F5F5",
                       tickfont=dict(size=11)),
            yaxis=dict(title="Revenue (₹)",showgrid=True,
                       gridcolor="#F5F5F5"),
            legend=dict(orientation="h",y=-0.25,x=0,
                        font=dict(size=11)),
            hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        section(f"{sel} — Revenue by SKU")
        sku_rev = cat_bi3.sort_values(
            "Total_Revenue",ascending=False)
        if len(sku_rev) > 0:
            fig2 = go.Figure(go.Bar(
                x=sku_rev["Total_Revenue"],
                y=sku_rev["Product"],
                orientation="h",
                marker_color=CATEGORY_COLORS.get(sel,BLUE),
                marker_line_width=0,
                text=[f"₹{v/1e6:.1f}M"
                      for v in sku_rev["Total_Revenue"]],
                textposition="outside",
                textfont=dict(size=10,color=TEXT_DARK)))
            fmt(fig2,height=300,show_legend=False)
            fig2.update_layout(
                xaxis_title="Total Revenue (₹)",
                yaxis=dict(tickfont=dict(size=10),autorange="reversed"),
                margin=dict(l=10,r=70,t=10,b=10))
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section(f"{sel} — SKU Detail Table")

    if len(cat_recsys) > 0:
        detail = cat_recsys[[
            "Product","Cluster_Name","Concentration_Flag",
            "Recovery_Status","Planning_Tier",
            "Champion_MAPE","Priority_Score",
            "Recommended_Action"]].copy()
        if "Champion_MAPE" in detail.columns:
            detail["Champion_MAPE"] = detail["Champion_MAPE"].round(2)
        if "Priority_Score" in detail.columns:
            detail["Priority_Score"] = detail["Priority_Score"].round(1)
        detail = detail.sort_values("Priority_Score",ascending=False)
        detail.columns = ["Product","Cluster","Conc. Flag",
                          "Recovery","Planning Tier",
                          "MAPE %","Priority","Action"]
        st.dataframe(detail,hide_index=True,
                     use_container_width=True)
    else:
        st.info("No recommendation data for this category.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Recovery for this category
    if len(cat_bi7) > 0:
        section(f"{sel} — SKU Recovery vs Peak")
        rb = cat_bi7.sort_values("Recovery_Rate_Pct")
        rbc = [RED if r<50 else AMBER if r<90 else GREEN
               for r in rb["Recovery_Rate_Pct"]]
        fig3 = go.Figure(go.Bar(
            x=rb["Recovery_Rate_Pct"],y=rb["Product"],
            orientation="h",marker_color=rbc,
            marker_line_width=0,
            text=rb["Recovery_Rate_Pct"].round(0)
                  .astype(int).astype(str)+"%",
            textposition="outside",
            textfont=dict(size=10,color=TEXT_DARK)))
        fig3.add_vline(x=100,line_dash="dash",
            line_color=TEXT_MID,line_width=1)
        fmt(fig3,height=max(220,len(rb)*45),show_legend=False)
        fig3.update_layout(
            xaxis_title="Recovery Rate % vs Peak",
            yaxis=dict(tickfont=dict(size=10)),
            margin=dict(l=10,r=70,t=10,b=10))
        st.plotly_chart(fig3, use_container_width=True)
