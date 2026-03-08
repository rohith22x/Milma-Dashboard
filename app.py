import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="MILMA Demand Intelligence",
    page_icon="🥛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Color Palette ─────────────────────────────────────────────
BG_DARK    = "#051122"
BG_CARD    = "#0A1F3D"
CYAN       = "#00D4FF"
GOLD       = "#FFD740"
PURPLE     = "#B388FF"
GREEN      = "#00E676"
RED        = "#FF3D57"
ORANGE     = "#FF9100"
GREY       = "#B0BEC5"
WHITE      = "#FFFFFF"

CATEGORY_COLORS = {
    "Ghee":         CYAN,
    "Butter":       GOLD,
    "Palada":       PURPLE,
    "UHT Milk":     ORANGE,
    "Milk Powder":  GREEN,
    "Instant Mixes":RED,
}

CLUSTER_COLORS = {
    "Revenue Giants":   GOLD,
    "Festival Rockets": PURPLE,
    "Core Portfolio":   CYAN,
}

ACTION_COLORS = {
    "PROTECT — Maximum stock, zero stockout tolerance":          "#27ae60",
    "INVEST — Growing high value SKU, build inventory":          "#2ecc71",
    "SURGE PREP — Build safety stock pre-Onam and Vishu":        "#3498db",
    "MAINTAIN — Standard replenishment, monthly review":         "#95a5a6",
    "SUPPORT — Recovery underway, moderate stock build":         "#f39c12",
    "MANUAL PLAN — Forecast unreliable, expert review needed":   "#e67e22",
    "DISCONTINUE REVIEW — Severely disrupted, evaluate viability":"#e74c3c",
    "FESTIVAL REVIEW — Festival SKU recovery needed":            "#9b59b6",
    "GROW — Strong growth, increase stock allocation":           "#1abc9c",
}

TIER_COLORS = {
    "TIER 1 — Algorithm Driven":          GREEN,
    "TIER 2 — Algorithm with Caution":    ORANGE,
    "TIER 3 — Manual Planning Required":  RED,
}

# ── Global CSS ────────────────────────────────────────────────
st.markdown(f"""
<style>
    .stApp {{ background-color: {BG_DARK}; }}
    section[data-testid="stSidebar"] {{
        background-color: {BG_CARD};
        border-right: 1px solid {CYAN};
    }}
    .stSelectbox label, .stMultiSelect label {{
        color: {WHITE} !important;
    }}
    div[data-testid="metric-container"] {{
        background-color: {BG_CARD};
        border: 1px solid {CYAN};
        border-radius: 8px;
        padding: 12px;
    }}
    div[data-testid="metric-container"] label {{
        color: {GREY} !important;
    }}
    div[data-testid="metric-container"] div {{
        color: {CYAN} !important;
    }}
    h1, h2, h3, h4 {{ color: {WHITE} !important; }}
    p, li {{ color: {GREY}; }}
    .kpi-card {{
        background-color: {BG_CARD};
        border: 1px solid {CYAN};
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 5px;
    }}
    .kpi-value {{
        font-size: 2em;
        font-weight: bold;
        color: {CYAN};
    }}
    .kpi-label {{
        font-size: 0.9em;
        color: {GREY};
        margin-top: 4px;
    }}
    .insight-box {{
        background-color: {BG_CARD};
        border-left: 4px solid {GOLD};
        border-radius: 6px;
        padding: 15px;
        margin: 10px 0;
    }}
    .stDataFrame {{ background-color: {BG_CARD}; }}
    .page-title {{
        font-size: 1.8em;
        font-weight: bold;
        color: {WHITE};
        border-bottom: 2px solid {CYAN};
        padding-bottom: 8px;
        margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# ── Data Loading ──────────────────────────────────────────────
@st.cache_data
def load_data():
    master    = pd.read_csv("master_dairy_dataset.csv", parse_dates=["Date"])
    clusters  = pd.read_csv("sku_clusters.csv")
    tournament= pd.read_csv("tournament_results.csv")
    forecast  = pd.read_csv("forecast_2026.csv", parse_dates=["Date"])
    bi3       = pd.read_csv("bi3_concentration_risk.csv")
    bi7       = pd.read_csv("bi7_recovery_analysis.csv")
    recsys    = pd.read_csv("master_recommendation_table.csv")
    return master, clusters, tournament, forecast, bi3, bi7, recsys

master, clusters, tournament, forecast, bi3, bi7, recsys = load_data()

# ── Sidebar Navigation ────────────────────────────────────────
st.sidebar.markdown(f"""
<div style='text-align:center; padding: 15px 0;'>
    <div style='font-size:1.4em; font-weight:bold; color:{CYAN};'>🥛 MILMA</div>
    <div style='font-size:0.85em; color:{GREY};'>Demand Intelligence System</div>
    <div style='font-size:0.75em; color:{GREY}; margin-top:4px;'>Malabar Region • 2021–2026</div>
</div>
<hr style='border-color:{CYAN}; margin: 10px 0;'>
""", unsafe_allow_html=True)

pages = [
    "📊 Portfolio Overview",
    "📈 EDA — Sales Trends",
    "🔵 Clustering Results",
    "🏆 Forecasting Tournament",
    "⚠️ Portfolio Risk",
    "✅ Recommendation System",
]
page = st.sidebar.radio("Navigation", pages, label_visibility="collapsed")

st.sidebar.markdown(f"""
<hr style='border-color:{CYAN}; margin: 15px 0;'>
<div style='font-size:0.75em; color:{GREY}; padding: 8px;'>
    <b style='color:{WHITE};'>Project Info</b><br>
    MSc CS Data Analytics<br>
    Org: Malabar MILMA<br>
    Dataset: 46 SKUs • 6 Categories<br>
    Period: 2021–2025<br>
    Records: 28,284 transactions
</div>
""", unsafe_allow_html=True)

# ── Helper ────────────────────────────────────────────────────
def card(value, label, color=CYAN, border=CYAN):
    return f"""
    <div class='kpi-card' style='border-color:{border};'>
        <div class='kpi-value' style='color:{color};'>{value}</div>
        <div class='kpi-label'>{label}</div>
    </div>"""

def plotly_dark(fig, title="", height=400):
    fig.update_layout(
        title=dict(text=title, font=dict(color=WHITE, size=14)),
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        font=dict(color=GREY),
        height=height,
        xaxis=dict(gridcolor="#1a2f4a", linecolor="#1a2f4a",
                   tickfont=dict(color=GREY)),
        yaxis=dict(gridcolor="#1a2f4a", linecolor="#1a2f4a",
                   tickfont=dict(color=GREY)),
        legend=dict(bgcolor=BG_CARD, font=dict(color=WHITE)),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig

# ══════════════════════════════════════════════════════════════
# PAGE 1 — PORTFOLIO OVERVIEW
# ══════════════════════════════════════════════════════════════
if page == "📊 Portfolio Overview":
    st.markdown("<div class='page-title'>📊 MILMA Demand Intelligence — Portfolio Overview</div>",
                unsafe_allow_html=True)

    # KPI Row
    total_rev = master["Sales_Value"].sum()
    total_sku = master["Product"].nunique()
    total_cat = master["Category"].nunique()
    top_sku_share = bi3["Revenue_Share_Pct"].max()

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(card(f"₹{total_rev/1e9:.2f}B", "Total Portfolio Revenue"), unsafe_allow_html=True)
    c2.markdown(card(f"{total_sku}", "Total SKUs"), unsafe_allow_html=True)
    c3.markdown(card(f"{total_cat}", "Product Categories"), unsafe_allow_html=True)
    c4.markdown(card("0.1516", "Portfolio HHI Score", color=ORANGE, border=ORANGE), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        # Donut chart
        cat_rev = master.groupby("Category")["Sales_Value"].sum().reset_index()
        fig = px.pie(cat_rev, values="Sales_Value", names="Category",
                     hole=0.55,
                     color="Category",
                     color_discrete_map=CATEGORY_COLORS)
        fig.update_traces(textposition="outside",
                          textinfo="percent+label",
                          textfont_color=WHITE)
        plotly_dark(fig, "Revenue by Category", height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Top 10 SKUs
        top10 = bi3.nlargest(10, "Total_Revenue")
        colors = [GOLD if f == "CRITICAL" else
                  ORANGE if f == "HIGH" else CYAN
                  for f in top10["Concentration_Flag"]]
        fig2 = go.Figure(go.Bar(
            x=top10["Total_Revenue"],
            y=top10["Product"],
            orientation="h",
            marker_color=colors,
            text=[f"₹{v/1e6:.1f}M" for v in top10["Total_Revenue"]],
            textposition="outside",
            textfont=dict(color=WHITE, size=10)
        ))
        plotly_dark(fig2, "Top 10 SKUs by Revenue", height=380)
        fig2.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)

    # Key Insights
    st.markdown(f"""
    <div class='insight-box'>
        <b style='color:{GOLD};'>🔑 Key Portfolio Insights</b><br>
        <span style='color:{WHITE};'>•</span> <b style='color:{CYAN};'>3 SKUs</b> generate <b style='color:{GOLD};'>60%</b> of total portfolio revenue (Ghee 500ml, Ghee 15kg, Ghee 200ml)<br>
        <span style='color:{WHITE};'>•</span> <b style='color:{CYAN};'>Ghee category</b> accounts for <b style='color:{GOLD};'>92.39%</b> of all shelf stable dairy revenue<br>
        <span style='color:{WHITE};'>•</span> <b style='color:{RED};'>7 products</b> are severely disrupted and require strategic review<br>
        <span style='color:{WHITE};'>•</span> Portfolio HHI of <b style='color:{ORANGE};'>0.1516</b> indicates moderate concentration risk
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 2 — EDA
# ══════════════════════════════════════════════════════════════
elif page == "📈 EDA — Sales Trends":
    st.markdown("<div class='page-title'>📈 Exploratory Data Analysis — Sales Trends (2021–2025)</div>",
                unsafe_allow_html=True)

    # Filters
    f1, f2 = st.columns(2)
    with f1:
        sel_cat = st.multiselect("Filter by Category",
                                  options=master["Category"].unique(),
                                  default=list(master["Category"].unique()))
    with f2:
        sel_year = st.multiselect("Filter by Year",
                                   options=sorted(master["Year"].unique()),
                                   default=sorted(master["Year"].unique()))

    filtered = master[
        master["Category"].isin(sel_cat) &
        master["Year"].isin(sel_year)
    ]

    # Revenue trend
    monthly = filtered.groupby(["Date", "Category"])["Sales_Value"].sum().reset_index()
    fig1 = px.line(monthly, x="Date", y="Sales_Value",
                   color="Category",
                   color_discrete_map=CATEGORY_COLORS)
    fig1.update_traces(line=dict(width=2))
    plotly_dark(fig1, "Monthly Revenue Trend by Category (2021–2025)", height=350)
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Seasonality heatmap
        heat = master.groupby(["Category", "Month_No"])["Sales_Value"].mean().reset_index()
        heat_pivot = heat.pivot(index="Category", columns="Month_No", values="Sales_Value")
        month_names = ["Jan","Feb","Mar","Apr","May","Jun",
                       "Jul","Aug","Sep","Oct","Nov","Dec"]
        fig2 = go.Figure(go.Heatmap(
            z=heat_pivot.values,
            x=month_names,
            y=heat_pivot.index,
            colorscale=[[0, BG_DARK], [0.5, CYAN], [1, GOLD]],
            text=[[f"{v/1e6:.1f}M" for v in row] for row in heat_pivot.values],
            texttemplate="%{text}",
            textfont=dict(size=9, color=WHITE),
        ))
        plotly_dark(fig2, "Monthly Seasonality Heatmap (Avg Revenue)", height=300)
        fig2.update_layout(
            xaxis=dict(title="Month"),
            yaxis=dict(title="")
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Annual revenue by category
        annual = master.groupby(["Year", "Category"])["Sales_Value"].sum().reset_index()
        fig3 = px.bar(annual, x="Year", y="Sales_Value",
                      color="Category",
                      barmode="group",
                      color_discrete_map=CATEGORY_COLORS)
        plotly_dark(fig3, "Annual Revenue by Category", height=300)
        st.plotly_chart(fig3, use_container_width=True)

    # YoY Growth heatmap
    st.markdown(f"<b style='color:{WHITE};'>Year on Year Revenue Growth by Category</b>",
                unsafe_allow_html=True)
    yoy = master.groupby(["Year","Category"])["Sales_Value"].sum().reset_index()
    yoy["YoY"] = yoy.groupby("Category")["Sales_Value"].pct_change() * 100
    yoy_pivot = yoy.pivot(index="Category", columns="Year", values="YoY").round(1)
    fig4 = go.Figure(go.Heatmap(
        z=yoy_pivot.values,
        x=[str(y) for y in yoy_pivot.columns],
        y=yoy_pivot.index,
        colorscale=[[0, RED], [0.5, BG_CARD], [1, GREEN]],
        zmid=0,
        text=[[f"{v:.1f}%" if not np.isnan(v) else "—"
               for v in row] for row in yoy_pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=11, color=WHITE),
    ))
    plotly_dark(fig4, "Year on Year Growth % by Category", height=280)
    st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 3 — CLUSTERING
# ══════════════════════════════════════════════════════════════
elif page == "🔵 Clustering Results":
    st.markdown("<div class='page-title'>🔵 K-Means Clustering — Product Segmentation Analysis</div>",
                unsafe_allow_html=True)

    # Cluster summary cards
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(card("3", "Total Clusters Found"), unsafe_allow_html=True)
    c2.markdown(card("0.61", "Silhouette Score", color=GREEN, border=GREEN), unsafe_allow_html=True)
    c3.markdown(card("3 SKUs", "Revenue Giants — 60% Revenue", color=GOLD, border=GOLD), unsafe_allow_html=True)
    c4.markdown(card("4 SKUs", "Festival Rockets — Seasonal", color=PURPLE, border=PURPLE), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Cluster filter
    sel_cluster = st.multiselect("Filter by Cluster",
                                  options=clusters["Cluster_Name"].unique(),
                                  default=list(clusters["Cluster_Name"].unique()))
    filtered_cl = clusters[clusters["Cluster_Name"].isin(sel_cluster)]

    col1, col2 = st.columns([3, 2])

    with col1:
        # Scatter plot
        fig1 = px.scatter(filtered_cl,
                          x="Volatility_CV",
                          y="Seasonality_Strength",
                          color="Cluster_Name",
                          size="Total_Revenue",
                          hover_name="Product",
                          hover_data={"Category": True,
                                      "Total_Revenue": ":.0f",
                                      "Volatility_CV": ":.2f",
                                      "Seasonality_Strength": ":.2f"},
                          color_discrete_map=CLUSTER_COLORS,
                          size_max=60)
        plotly_dark(fig1,
                    "Product Segmentation — Volatility vs Seasonality",
                    height=420)
        fig1.update_layout(
            xaxis_title="Demand Volatility (CV)",
            yaxis_title="Seasonality Strength"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Cluster donut
        cl_rev = clusters.groupby("Cluster_Name")["Total_Revenue"].sum().reset_index()
        fig2 = px.pie(cl_rev, values="Total_Revenue", names="Cluster_Name",
                      hole=0.5,
                      color="Cluster_Name",
                      color_discrete_map=CLUSTER_COLORS)
        fig2.update_traces(textposition="outside",
                           textinfo="percent+label",
                           textfont_color=WHITE)
        plotly_dark(fig2, "Revenue Share by Cluster", height=280)
        st.plotly_chart(fig2, use_container_width=True)

        # Cluster counts
        cl_counts = clusters.groupby("Cluster_Name").agg(
            SKUs=("Product","count"),
            Revenue=("Total_Revenue","sum")
        ).reset_index()
        cl_counts["Revenue_Share"] = (
            cl_counts["Revenue"] / cl_counts["Revenue"].sum() * 100
        ).round(1)
        st.dataframe(
            cl_counts[["Cluster_Name","SKUs","Revenue_Share"]].rename(
                columns={"Cluster_Name":"Cluster",
                         "Revenue_Share":"Rev Share %"}),
            hide_index=True,
            use_container_width=True
        )

    # SKU table
    st.markdown(f"<b style='color:{WHITE};'>SKU Cluster Assignment</b>",
                unsafe_allow_html=True)
    display_cl = filtered_cl[[
        "Product","Category","Cluster_Name",
        "Total_Revenue","Volatility_CV","Seasonality_Strength"
    ]].sort_values("Total_Revenue", ascending=False)
    display_cl["Total_Revenue"] = display_cl["Total_Revenue"].apply(
        lambda x: f"₹{x/1e6:.2f}M")
    display_cl.columns = ["Product","Category","Cluster",
                           "Revenue","Volatility CV","Seasonality"]
    st.dataframe(display_cl, hide_index=True, use_container_width=True)

    # Insight
    st.markdown(f"""
    <div class='insight-box'>
        <b style='color:{GOLD};'>🔑 Clustering Insights</b><br>
        <b style='color:{GOLD};'>Revenue Giants</b> — 3 SKUs generating 60% of portfolio revenue. Zero stockout tolerance required.<br>
        <b style='color:{PURPLE};'>Festival Rockets</b> — 4 SKUs with extreme Onam and Vishu seasonality. Surge planning critical.<br>
        <b style='color:{CYAN};'>Core Portfolio</b> — 35 SKUs with stable predictable demand. Standard replenishment sufficient.<br>
        <b style='color:{GREEN};'>Silhouette Score 0.61</b> confirms clusters are well separated and statistically valid.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 4 — FORECASTING TOURNAMENT
# ══════════════════════════════════════════════════════════════
elif page == "🏆 Forecasting Tournament":
    st.markdown("<div class='page-title'>🏆 Prophet vs XGBoost — Model Tournament Results</div>",
                unsafe_allow_html=True)

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(card("XGBoost", "Tournament Champion", color=GOLD, border=GOLD), unsafe_allow_html=True)
    c2.markdown(card("5 / 6", "Categories Won by XGBoost", color=GREEN, border=GREEN), unsafe_allow_html=True)
    c3.markdown(card("12.07%", "Best MAPE — Ghee (Excellent)", color=CYAN, border=CYAN), unsafe_allow_html=True)
    c4.markdown(card("3 / 6", "Categories Need Manual Planning", color=RED, border=RED), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        # Tournament table
        st.markdown(f"<b style='color:{WHITE};'>Model Tournament Results</b>",
                    unsafe_allow_html=True)

        def quality_color(val):
            if val == "Excellent": return f"background-color: #1a4a2a; color: {GREEN}"
            elif val == "Acceptable": return f"background-color: #4a3a10; color: {GOLD}"
            else: return f"background-color: #4a1a1a; color: {RED}"

        def mape_color(val):
            try:
                v = float(val)
                if v < 30: return f"color: {GREEN}"
                elif v < 50: return f"color: {GOLD}"
                else: return f"color: {RED}"
            except:
                return ""

        t_display = tournament[[
            "Category","Prophet_MAPE","XGBoost_MAPE",
            "Champion","Champion_MAPE","Quality"
        ]].copy()
        t_display.columns = ["Category","Prophet %","XGBoost %",
                              "Champion","Best MAPE %","Quality"]

        styled = t_display.style\
            .applymap(quality_color, subset=["Quality"])\
            .applymap(mape_color, subset=["Best MAPE %","Prophet %","XGBoost %"])\
            .set_properties(**{"background-color": BG_CARD,
                               "color": WHITE,
                               "border": f"1px solid {BG_DARK}"})\
            .format({"Prophet %": "{:.2f}", "XGBoost %": "{:.2f}",
                     "Best MAPE %": "{:.2f}"})
        st.dataframe(styled, hide_index=True, use_container_width=True)

    with col2:
        # MAPE comparison chart
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            name="Prophet",
            x=tournament["Category"],
            y=tournament["Prophet_MAPE"],
            marker_color=PURPLE,
            text=tournament["Prophet_MAPE"].round(1),
            textposition="outside",
            textfont=dict(color=WHITE)
        ))
        fig1.add_trace(go.Bar(
            name="XGBoost",
            x=tournament["Category"],
            y=tournament["XGBoost_MAPE"],
            marker_color=CYAN,
            text=tournament["XGBoost_MAPE"].round(1),
            textposition="outside",
            textfont=dict(color=WHITE)
        ))
        fig1.add_hline(y=20, line_dash="dash",
                       line_color=GREEN,
                       annotation_text="Excellent ≤20%",
                       annotation_font_color=GREEN)
        fig1.add_hline(y=50, line_dash="dash",
                       line_color=RED,
                       annotation_text="Poor >50%",
                       annotation_font_color=RED)
        fig1.update_layout(barmode="group")
        plotly_dark(fig1, "Prophet vs XGBoost MAPE by Category", height=350)
        st.plotly_chart(fig1, use_container_width=True)

    # 2026 Forecast
    st.markdown(f"<b style='color:{WHITE};'>2026 Monthly Demand Forecast</b>",
                unsafe_allow_html=True)

    sel_cat = st.multiselect("Select Categories",
                              options=forecast["Category"].unique(),
                              default=list(forecast["Category"].unique()))
    f_filtered = forecast[forecast["Category"].isin(sel_cat)]

    fig2 = go.Figure()
    for cat in sel_cat:
        cat_data = f_filtered[f_filtered["Category"] == cat]
        color = CATEGORY_COLORS.get(cat, CYAN)
        fig2.add_trace(go.Scatter(
            x=cat_data["Date"],
            y=cat_data["Forecast"],
            name=cat,
            line=dict(color=color, width=2.5),
            mode="lines+markers",
            marker=dict(size=6)
        ))
        if "Upper_95" in cat_data.columns and "Lower_95" in cat_data.columns:
            fig2.add_trace(go.Scatter(
                x=pd.concat([cat_data["Date"], cat_data["Date"].iloc[::-1]]),
                y=pd.concat([cat_data["Upper_95"], cat_data["Lower_95"].iloc[::-1]]),
                fill="toself",
                fillcolor=color.replace(")", ",0.1)").replace("rgb", "rgba")
                              if "rgb" in color else color + "1a",
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False,
                hoverinfo="skip"
            ))

    plotly_dark(fig2, "2026 Monthly Demand Forecast by Category", height=380)
    fig2.update_layout(xaxis_title="Month", yaxis_title="Forecast Revenue (₹)")
    st.plotly_chart(fig2, use_container_width=True)

    # Why XGBoost won
    st.markdown(f"""
    <div class='insight-box'>
        <b style='color:{GOLD};'>🏆 Why XGBoost Won</b><br>
        XGBoost outperformed Prophet in 5 of 6 categories because 2025 contained structural demand changes
        that violated Prophet's decomposition assumptions. XGBoost's lag features and year encoding
        captured these structural shifts more effectively. The only Prophet win was UHT Milk where
        a continuous monotonic decline since 2022 favoured trend decomposition over lag-based learning.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 5 — PORTFOLIO RISK
# ══════════════════════════════════════════════════════════════
elif page == "⚠️ Portfolio Risk":
    st.markdown("<div class='page-title'>⚠️ Portfolio Concentration and Demand Recovery Analysis</div>",
                unsafe_allow_html=True)

    # KPI
    critical = len(bi3[bi3["Concentration_Flag"] == "CRITICAL"])
    disrupted = len(bi7[bi7["Recovery_Status"] == "DISRUPTED"])
    growing = len(bi7[bi7["Recovery_Status"] == "GROWING"])
    top3_share = bi3.nlargest(3,"Total_Revenue")["Revenue_Share_Pct"].sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(card(f"{critical}", "CRITICAL SKUs", color=RED, border=RED), unsafe_allow_html=True)
    c2.markdown(card(f"{top3_share:.1f}%", "Top 3 SKUs Revenue Share", color=GOLD, border=GOLD), unsafe_allow_html=True)
    c3.markdown(card(f"{growing}", "Growing SKUs", color=GREEN, border=GREEN), unsafe_allow_html=True)
    c4.markdown(card(f"{disrupted}", "Disrupted SKUs", color=RED, border=RED), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        # Concentration flag donut
        conc_counts = bi3["Concentration_Flag"].value_counts().reset_index()
        conc_counts.columns = ["Flag","Count"]
        flag_colors = {"CRITICAL": RED, "HIGH": ORANGE,
                       "MODERATE": GOLD, "LOW": CYAN}
        fig1 = px.pie(conc_counts, values="Count", names="Flag",
                      hole=0.5,
                      color="Flag",
                      color_discrete_map=flag_colors)
        fig1.update_traces(textposition="outside",
                           textinfo="percent+label",
                           textfont_color=WHITE)
        plotly_dark(fig1, "SKU Concentration Flag Distribution", height=300)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Recovery status donut
        rec_counts = bi7["Recovery_Status"].value_counts().reset_index()
        rec_counts.columns = ["Status","Count"]
        rec_colors = {"GROWING": GREEN, "STABLE": CYAN,
                      "RECOVERING": ORANGE, "DISRUPTED": RED,
                      "DECLINING": "#FF6B6B"}
        fig2 = px.pie(rec_counts, values="Count", names="Status",
                      hole=0.5,
                      color="Status",
                      color_discrete_map=rec_colors)
        fig2.update_traces(textposition="outside",
                           textinfo="percent+label",
                           textfont_color=WHITE)
        plotly_dark(fig2, "SKU Recovery Status Distribution", height=300)
        st.plotly_chart(fig2, use_container_width=True)

    # Recovery rate bar chart
    rec_sorted = bi7.sort_values("Recovery_Rate_Pct")
    bar_colors = [RED if r < 50 else ORANGE if r < 90 else GREEN
                  for r in rec_sorted["Recovery_Rate_Pct"]]
    fig3 = go.Figure(go.Bar(
        x=rec_sorted["Recovery_Rate_Pct"],
        y=rec_sorted["Product"],
        orientation="h",
        marker_color=bar_colors,
        text=rec_sorted["Recovery_Rate_Pct"].round(1).astype(str) + "%",
        textposition="outside",
        textfont=dict(color=WHITE, size=9)
    ))
    fig3.add_vline(x=100, line_dash="dash",
                   line_color=WHITE,
                   annotation_text="Peak (100%)",
                   annotation_font_color=WHITE)
    plotly_dark(fig3, "SKU Recovery Rate vs Peak Revenue", height=700)
    fig3.update_layout(
        xaxis_title="Recovery Rate %",
        yaxis=dict(tickfont=dict(size=9))
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Disrupted SKUs table
    st.markdown(f"<b style='color:{RED};'>⚠️ Severely Disrupted SKUs — Require Strategic Review</b>",
                unsafe_allow_html=True)
    disrupted_df = bi7[bi7["Recovery_Status"] == "DISRUPTED"][[
        "Product","Category","Peak_Year",
        "Recovery_Rate_Pct","YoY_Growth_Pct"
    ]].copy()
    disrupted_df.columns = ["Product","Category","Peak Year",
                             "Recovery Rate %","YoY Growth %"]
    st.dataframe(disrupted_df.sort_values("Recovery Rate %"),
                 hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 6 — RECOMMENDATION SYSTEM
# ══════════════════════════════════════════════════════════════
elif page == "✅ Recommendation System":
    st.markdown("<div class='page-title'>✅ SKU Level Demand Planning Recommendations</div>",
                unsafe_allow_html=True)

    # KPI
    t1 = len(recsys[recsys["Planning_Tier"].str.contains("TIER 1", na=False)])
    t2 = len(recsys[recsys["Planning_Tier"].str.contains("TIER 2", na=False)])
    t3 = len(recsys[recsys["Planning_Tier"].str.contains("TIER 3", na=False)])
    protect = len(recsys[recsys["Recommended_Action"].str.contains("PROTECT", na=False)])

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(card(f"{t1}", "Tier 1 — Algorithm Driven", color=GREEN, border=GREEN), unsafe_allow_html=True)
    c2.markdown(card(f"{t2}", "Tier 2 — Algorithm with Caution", color=ORANGE, border=ORANGE), unsafe_allow_html=True)
    c3.markdown(card(f"{t3}", "Tier 3 — Manual Planning", color=RED, border=RED), unsafe_allow_html=True)
    c4.markdown(card(f"{protect}", "PROTECT SKUs — Zero Stockout", color=GOLD, border=GOLD), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filters
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sel_cat = st.multiselect("Category",
                                  recsys["Category"].dropna().unique(),
                                  default=list(recsys["Category"].dropna().unique()))
    with f2:
        sel_cluster = st.multiselect("Cluster",
                                      recsys["Cluster_Name"].dropna().unique(),
                                      default=list(recsys["Cluster_Name"].dropna().unique()))
    with f3:
        tier_opts = recsys["Planning_Tier"].dropna().unique()
        sel_tier = st.multiselect("Planning Tier", tier_opts, default=list(tier_opts))
    with f4:
        action_opts = recsys["Recommended_Action"].dropna().unique()
        sel_action = st.multiselect("Action", action_opts, default=list(action_opts))

    filtered_r = recsys[
        recsys["Category"].isin(sel_cat) &
        recsys["Cluster_Name"].isin(sel_cluster) &
        recsys["Planning_Tier"].isin(sel_tier) &
        recsys["Recommended_Action"].isin(sel_action)
    ]

    col1, col2 = st.columns(2)

    with col1:
        # Action distribution
        action_counts = filtered_r["Recommended_Action"].value_counts().reset_index()
        action_counts.columns = ["Action","Count"]
        action_counts["Short"] = action_counts["Action"].str.split("—").str[0].str.strip()
        bar_colors_a = [ACTION_COLORS.get(a, CYAN)
                        for a in action_counts["Action"]]
        fig1 = go.Figure(go.Bar(
            x=action_counts["Count"],
            y=action_counts["Short"],
            orientation="h",
            marker_color=bar_colors_a,
            text=action_counts["Count"],
            textposition="outside",
            textfont=dict(color=WHITE)
        ))
        plotly_dark(fig1, "Recommended Actions Distribution", height=350)
        fig1.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Planning tier donut
        tier_counts = filtered_r["Planning_Tier"].value_counts().reset_index()
        tier_counts.columns = ["Tier","Count"]
        tier_counts["Short"] = tier_counts["Tier"].str.split("—").str[0].str.strip()
        t_colors = [TIER_COLORS.get(t, CYAN) for t in tier_counts["Tier"]]
        fig2 = px.pie(tier_counts, values="Count", names="Short",
                      hole=0.5,
                      color_discrete_sequence=t_colors)
        fig2.update_traces(textposition="outside",
                           textinfo="percent+label",
                           textfont_color=WHITE)
        plotly_dark(fig2, "Planning Tier Distribution", height=350)
        st.plotly_chart(fig2, use_container_width=True)

    # Priority score chart
    top15 = filtered_r.nlargest(15, "Priority_Score")
    p_colors = [TIER_COLORS.get(t, CYAN) for t in top15["Planning_Tier"]]
    fig3 = go.Figure(go.Bar(
        x=top15["Priority_Score"],
        y=top15["Product"],
        orientation="h",
        marker_color=p_colors,
        text=top15["Priority_Score"].round(1),
        textposition="outside",
        textfont=dict(color=WHITE, size=9)
    ))
    plotly_dark(fig3, "Top 15 Priority SKUs (Higher = Needs More Attention)", height=420)
    fig3.update_layout(yaxis=dict(autorange="reversed",
                                   tickfont=dict(size=9)))
    st.plotly_chart(fig3, use_container_width=True)

    # Master table
    st.markdown(f"<b style='color:{WHITE};'>Master SKU Recommendation Table</b>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='color:{GREY}; font-size:0.85em;'>Showing {len(filtered_r)} of {len(recsys)} SKUs based on filters</p>",
                unsafe_allow_html=True)

    display_cols = [
        "Product","Category","Cluster_Name",
        "Concentration_Flag","Recovery_Status",
        "Planning_Tier","Champion_MAPE",
        "Priority_Score","Recommended_Action"
    ]
    display_cols = [c for c in display_cols if c in filtered_r.columns]
    table_df = filtered_r[display_cols].sort_values(
        "Priority_Score", ascending=False).copy()

    if "Champion_MAPE" in table_df.columns:
        table_df["Champion_MAPE"] = table_df["Champion_MAPE"].round(2)

    def highlight_action(row):
        action = row.get("Recommended_Action", "")
        color = ACTION_COLORS.get(action, "")
        if color:
            bg = color + "33"
            return [f"background-color: {bg}; color: {WHITE}"
                    if col == "Recommended_Action"
                    else f"color: {WHITE}; background-color: {BG_CARD}"
                    for col in row.index]
        return [f"color: {WHITE}; background-color: {BG_CARD}"
                for _ in row.index]

    styled_table = table_df.style\
        .apply(highlight_action, axis=1)\
        .set_properties(**{"border": f"1px solid {BG_DARK}"})

    st.dataframe(styled_table, hide_index=True, use_container_width=True)

    # Final insight
    st.markdown(f"""
    <div class='insight-box'>
        <b style='color:{GOLD};'>✅ Recommendation System Summary</b><br>
        <b style='color:{GREEN};'>Tier 1 — {t1} SKUs:</b> Forecasts are reliable. Use directly for procurement planning.<br>
        <b style='color:{ORANGE};'>Tier 2 — {t2} SKUs:</b> Forecasts are acceptable but validate before ordering.<br>
        <b style='color:{RED};'>Tier 3 — {t3} SKUs:</b> Forecasts unreliable. Human judgment required for all ordering decisions.
    </div>
    """, unsafe_allow_html=True)
