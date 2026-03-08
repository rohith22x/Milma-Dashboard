import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="MILMA Demand Intelligence",
    page_icon="🥛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Color System ──────────────────────────────────────────────
PRIMARY    = "#1B4F72"
ACCENT     = "#2E86C1"
SUCCESS    = "#1E8449"
WARNING    = "#D4AC0D"
DANGER     = "#C0392B"
ORANGE     = "#CA6F1E"
PURPLE     = "#6C3483"
TEAL       = "#148F77"
LIGHT_BG   = "#F8F9FA"
BORDER     = "#DEE2E6"
TEXT_DARK  = "#212529"
TEXT_MID   = "#6C757D"
WHITE      = "#FFFFFF"

CATEGORY_COLORS = {
    "Ghee":          PRIMARY,
    "Butter":        WARNING,
    "Palada":        PURPLE,
    "UHT Milk":      ORANGE,
    "Milk Powder":   TEAL,
    "Instant Mixes": DANGER,
}

CLUSTER_COLORS = {
    "Revenue Giants":   WARNING,
    "Festival Rockets": PURPLE,
    "Core Portfolio":   ACCENT,
}

ACTION_COLORS = {
    "PROTECT — Maximum stock, zero stockout tolerance":            SUCCESS,
    "INVEST — Growing high value SKU, build inventory":            TEAL,
    "SURGE PREP — Build safety stock pre-Onam and Vishu":          ACCENT,
    "MAINTAIN — Standard replenishment, monthly review":           TEXT_MID,
    "SUPPORT — Recovery underway, moderate stock build":           WARNING,
    "MANUAL PLAN — Forecast unreliable, expert review needed":     ORANGE,
    "DISCONTINUE REVIEW — Severely disrupted, evaluate viability": DANGER,
    "FESTIVAL REVIEW — Festival SKU recovery needed":              PURPLE,
    "GROW — Strong growth, increase stock allocation":             SUCCESS,
}

# ── CSS ───────────────────────────────────────────────────────
st.markdown(f"""
<style>
    .stApp {{ background-color:{WHITE}; font-family:'Segoe UI',sans-serif; }}
    section[data-testid="stSidebar"] {{ background-color:{PRIMARY}; }}
    section[data-testid="stSidebar"] * {{ color:{WHITE} !important; }}
    .block-container {{ padding:1.5rem 2rem; }}
    .page-header {{
        background:linear-gradient(135deg,{PRIMARY} 0%,{ACCENT} 100%);
        color:{WHITE}; padding:20px 28px;
        border-radius:10px; margin-bottom:24px;
    }}
    .page-header h1 {{ color:{WHITE}!important; font-size:1.5em;
                       font-weight:700; margin:0; }}
    .page-header p  {{ color:rgba(255,255,255,0.8);
                       margin:4px 0 0 0; font-size:0.9em; }}
    .kpi-card {{
        background:{WHITE}; border:1px solid {BORDER};
        border-radius:10px; padding:20px 24px;
        box-shadow:0 2px 8px rgba(0,0,0,0.06);
        margin-bottom:16px; border-top:4px solid {ACCENT};
    }}
    .kpi-card.green  {{ border-top-color:{SUCCESS}; }}
    .kpi-card.amber  {{ border-top-color:{WARNING}; }}
    .kpi-card.red    {{ border-top-color:{DANGER};  }}
    .kpi-card.purple {{ border-top-color:{PURPLE};  }}
    .kpi-card.teal   {{ border-top-color:{TEAL};    }}
    .kpi-value {{ font-size:2em; font-weight:700;
                  color:{PRIMARY}; line-height:1.1; }}
    .kpi-label {{ font-size:0.82em; color:{TEXT_MID};
                  margin-top:4px; font-weight:500;
                  text-transform:uppercase; letter-spacing:0.5px; }}
    .kpi-sub   {{ font-size:0.78em; color:{TEXT_MID}; margin-top:2px; }}
    .section-title {{
        font-size:1em; font-weight:700; color:{PRIMARY};
        border-left:4px solid {ACCENT}; padding-left:10px;
        margin:20px 0 12px 0; text-transform:uppercase;
        letter-spacing:0.5px;
    }}
    .insight-box {{
        background:#EBF5FB; border-left:4px solid {ACCENT};
        border-radius:6px; padding:16px 20px; margin:16px 0;
    }}
    .insight-box.warning {{ background:#FEF9E7;
                            border-left-color:{WARNING}; }}
    .insight-box.danger  {{ background:#FDEDEC;
                            border-left-color:{DANGER};  }}
    .insight-box.success {{ background:#EAFAF1;
                            border-left-color:{SUCCESS}; }}
    .divider {{ border:none; border-top:1px solid {BORDER};
                margin:20px 0; }}
    #MainMenu {{ visibility:hidden; }}
    footer    {{ visibility:hidden; }}
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
    st.markdown(
        f"<div class='insight-box {style}'>{text}</div>",
        unsafe_allow_html=True)

def chart_fmt(fig, height=380, show_legend=True):
    fig.update_layout(
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        font=dict(color=TEXT_DARK, family="Segoe UI"),
        height=height, showlegend=show_legend,
        legend=dict(bgcolor=WHITE, bordercolor=BORDER,
                    borderwidth=1, font=dict(size=11)),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0",
                   linecolor=BORDER, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0",
                   linecolor=BORDER, tickfont=dict(size=11)),
    )
    return fig


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px 0;'>
        <div style='font-size:2em;'>🥛</div>
        <div style='font-size:1.1em;font-weight:700;color:white;
                    margin-top:6px;'>MILMA</div>
        <div style='font-size:0.8em;color:rgba(255,255,255,0.7);'>
            Demand Intelligence</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.2);margin:12px 0;'>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "📊  Portfolio Overview",
        "📈  EDA — Sales Trends",
        "🔵  Clustering Results",
        "🏆  Forecasting Tournament",
        "⚠️   Portfolio Risk",
        "✅  Recommendation System",
    ], label_visibility="collapsed")

    st.markdown("""
    <hr style='border-color:rgba(255,255,255,0.2);margin:16px 0 10px 0;'>
    <div style='font-size:0.78em;color:rgba(255,255,255,0.65);
                padding:0 4px;line-height:1.8;'>
        <b style='color:rgba(255,255,255,0.9);'>Project Details</b><br>
        MSc CS Data Analytics<br>
        Malabar MILMA<br>
        46 SKUs · 6 Categories<br>
        Jan 2021 – Dec 2025<br>
        28,284 transactions
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 1 — PORTFOLIO OVERVIEW
# ══════════════════════════════════════════════════════════════
if page == "📊  Portfolio Overview":
    st.markdown("""
    <div class='page-header'>
        <h1>📊 Portfolio Overview</h1>
        <p>Malabar MILMA · Shelf Stable Dairy · 2021–2025</p>
    </div>""", unsafe_allow_html=True)

    total_rev  = master["Sales_Value"].sum()
    total_sku  = master["Product"].nunique()
    top3_share = bi3.nlargest(3,"Total_Revenue")[
        "Revenue_Share_Pct"].sum()
    ghee_share = bi3[bi3["Category"]=="Ghee"][
        "Revenue_Share_Pct"].sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi(f"₹{total_rev/1e9:.2f}B",
        "Total Portfolio Revenue","5-year (2021–2025)"),
        unsafe_allow_html=True)
    c2.markdown(kpi(f"{total_sku}",
        "Total Active SKUs","6 product categories"),
        unsafe_allow_html=True)
    c3.markdown(kpi(f"{top3_share:.1f}%",
        "Top 3 SKUs Revenue Share","Extreme concentration",
        color="amber"), unsafe_allow_html=True)
    c4.markdown(kpi(f"{ghee_share:.1f}%",
        "Ghee Category Share","HHI = 0.1516",
        color="red"), unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col1,col2 = st.columns(2, gap="large")

    with col1:
        section("Revenue by Category")
        cat_rev = master.groupby("Category")[
            "Sales_Value"].sum().reset_index()
        fig = px.pie(cat_rev, values="Sales_Value",
                     names="Category", hole=0.55,
                     color="Category",
                     color_discrete_map=CATEGORY_COLORS)
        fig.update_traces(
            textposition="outside",
            textinfo="percent+label",
            textfont_size=12,
            marker=dict(line=dict(color=WHITE, width=2)))
        fig.update_layout(
            showlegend=False, paper_bgcolor=WHITE,
            height=340, margin=dict(l=20,r=20,t=10,b=10),
            annotations=[dict(
                text=f"<b>₹{total_rev/1e9:.2f}B</b><br>Total",
                x=0.5,y=0.5,font_size=14,
                font_color=PRIMARY,showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Top 10 SKUs by Revenue")
        top10 = bi3.nlargest(10,"Total_Revenue").copy()
        top10 = top10.sort_values("Total_Revenue")
        bar_colors = [
            DANGER  if f=="CRITICAL" else
            WARNING if f=="HIGH"     else ACCENT
            for f in top10["Concentration_Flag"]]
        fig2 = go.Figure(go.Bar(
            x=top10["Total_Revenue"],
            y=top10["Product"],
            orientation="h",
            marker_color=bar_colors,
            marker_line_width=0,
            text=[f"₹{v/1e6:.0f}M"
                  for v in top10["Total_Revenue"]],
            textposition="outside",
            textfont=dict(size=11,color=TEXT_DARK)))
        chart_fmt(fig2, height=340, show_legend=False)
        fig2.update_layout(
            xaxis_title="Total Revenue (₹)",
            yaxis=dict(tickfont=dict(size=10)),
            margin=dict(l=10,r=60,t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("Key Portfolio Findings")
    r1,r2,r3 = st.columns(3)
    with r1:
        insight("<b style='color:#C0392B;'>⚠️ Extreme Concentration</b><br>"
                "Just <b>3 SKUs</b> generate <b>60%</b> of revenue. "
                "Any Ghee supply disruption is a business-level risk.",
                style="danger")
    with r2:
        insight("<b style='color:#D4AC0D;'>📅 Festival Dependency</b><br>"
                "Ghee and Palada show <b>2–5× spikes</b> during "
                "Onam (Aug) and Vishu (Apr). Festival planning is critical.",
                style="warning")
    with r3:
        insight("<b style='color:#1E8449;'>📈 Portfolio Growth</b><br>"
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
        <p>Sales trends · seasonality · year-on-year growth · 2021–2025</p>
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
        "Revenue (Filtered)"), unsafe_allow_html=True)
    c2.markdown(kpi(f"{df['Product'].nunique()}",
        "SKUs in Selection"), unsafe_allow_html=True)
    peak_m = df.groupby("Month_Name")[
        "Sales_Value"].mean().idxmax()
    c3.markdown(kpi(peak_m,"Peak Month (Avg)",
        color="amber"), unsafe_allow_html=True)
    best_c = df.groupby("Category")[
        "Sales_Value"].sum().idxmax()
    c4.markdown(kpi(best_c,"Top Category",
        color="green"), unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("Monthly Revenue Trend by Category")
    monthly = df.groupby(["Date","Category"])[
        "Sales_Value"].sum().reset_index()
    fig1 = px.line(monthly, x="Date", y="Sales_Value",
                   color="Category",
                   color_discrete_map=CATEGORY_COLORS)
    fig1.update_traces(line=dict(width=2.5))
    chart_fmt(fig1, height=360)
    fig1.update_layout(
        xaxis_title="", yaxis_title="Monthly Revenue (₹)",
        legend=dict(orientation="h", y=-0.15, x=0))
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col1,col2 = st.columns(2, gap="large")

    with col1:
        section("Monthly Seasonality Heatmap")
        heat = master.groupby(["Category","Month_No"])[
            "Sales_Value"].mean().reset_index()
        hp = heat.pivot(index="Category",
                        columns="Month_No",
                        values="Sales_Value")
        mnames = ["Jan","Feb","Mar","Apr","May","Jun",
                  "Jul","Aug","Sep","Oct","Nov","Dec"]
        fig2 = go.Figure(go.Heatmap(
            z=hp.values, x=mnames,
            y=hp.index.tolist(),
            colorscale=[[0,"#EBF5FB"],
                        [0.5,"#2E86C1"],
                        [1,"#1B4F72"]],
            text=[[f"₹{v/1e6:.1f}M" for v in row]
                  for row in hp.values],
            texttemplate="%{text}",
            textfont=dict(size=9,color=WHITE),
            showscale=False))
        fig2.update_layout(
            paper_bgcolor=WHITE, plot_bgcolor=WHITE,
            height=280,
            margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(tickfont=dict(size=11)),
            yaxis=dict(tickfont=dict(size=11)))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        section("Annual Revenue by Category")
        annual = master.groupby(["Year","Category"])[
            "Sales_Value"].sum().reset_index()
        fig3 = px.bar(annual, x="Year", y="Sales_Value",
                      color="Category", barmode="group",
                      color_discrete_map=CATEGORY_COLORS)
        chart_fmt(fig3, height=280)
        fig3.update_layout(
            xaxis_title="Year",
            yaxis_title="Revenue (₹)",
            xaxis=dict(tickmode="linear"),
            legend=dict(orientation="h", y=-0.3,
                        x=0, font=dict(size=10)))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("Year-on-Year Growth (%) Heatmap")
    yoy = master.groupby(["Year","Category"])[
        "Sales_Value"].sum().reset_index()
    yoy["YoY"] = yoy.groupby("Category")[
        "Sales_Value"].pct_change() * 100
    yp = yoy.pivot(index="Category",
                   columns="Year",
                   values="YoY").round(1)
    fig4 = go.Figure(go.Heatmap(
        z=yp.values,
        x=[str(y) for y in yp.columns],
        y=yp.index.tolist(),
        colorscale=[[0,"#FDEDEC"],[0.5,"#FDFEFE"],
                    [1,"#EAFAF1"]],
        zmid=0,
        text=[[f"{v:+.1f}%" if not np.isnan(v) else "—"
               for v in row] for row in yp.values],
        texttemplate="%{text}",
        textfont=dict(size=12, color=TEXT_DARK),
        showscale=False))
    fig4.update_layout(
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        height=240,
        margin=dict(l=10,r=10,t=10,b=10),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)))
    st.plotly_chart(fig4, use_container_width=True)
    insight("🟢 Green = revenue growth vs prior year. "
            "🔴 Red = revenue decline. "
            "UHT Milk shows continuous red 2022 onwards. "
            "Butter and Milk Powder bright green in 2025.")


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
    c1.markdown(kpi("3","Clusters Identified",
        "Optimal K confirmed"), unsafe_allow_html=True)
    c2.markdown(kpi("0.61","Silhouette Score",
        "Well-separated",color="green"), unsafe_allow_html=True)
    c3.markdown(kpi("3 SKUs","Revenue Giants",
        "60% of revenue",color="amber"), unsafe_allow_html=True)
    c4.markdown(kpi("4 SKUs","Festival Rockets",
        "Onam & Vishu driven",color="purple"),
        unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    sel_cl = st.multiselect("Filter Cluster",
        options=clusters["Cluster_Name"].dropna().unique(),
        default=list(clusters["Cluster_Name"].dropna().unique()))
    df_cl = clusters[clusters["Cluster_Name"].isin(sel_cl)]

    col1,col2 = st.columns([3,2], gap="large")
    with col1:
        section("Volatility vs Seasonality Scatter Plot")
        fig1 = px.scatter(df_cl,
            x="Volatility_CV", y="Seasonality_Strength",
            color="Cluster_Name", size="Total_Revenue",
            hover_name="Product",
            hover_data={"Category":True,
                        "Total_Revenue":":,.0f",
                        "Cluster_Name":False},
            color_discrete_map=CLUSTER_COLORS,
            size_max=55)
        chart_fmt(fig1, height=400)
        fig1.update_layout(
            xaxis_title="Demand Volatility (CV)",
            yaxis_title="Seasonality Strength",
            legend=dict(title="Cluster",
                        orientation="h",y=-0.15,x=0))
        fig1.update_traces(
            marker=dict(line=dict(color=WHITE,width=1.5),
                        opacity=0.85))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        section("Revenue by Cluster")
        cl_rev = clusters.groupby("Cluster_Name")[
            "Total_Revenue"].sum().reset_index()
        fig2 = px.pie(cl_rev, values="Total_Revenue",
                      names="Cluster_Name", hole=0.5,
                      color="Cluster_Name",
                      color_discrete_map=CLUSTER_COLORS)
        fig2.update_traces(
            textposition="outside",
            textinfo="percent+label", textfont_size=12,
            marker=dict(line=dict(color=WHITE,width=2)))
        fig2.update_layout(showlegend=False,
            paper_bgcolor=WHITE, height=240,
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
        st.dataframe(cs[["Cluster_Name","SKUs",
                          "Rev %","Revenue"]].rename(
            columns={"Cluster_Name":"Cluster"}),
            hide_index=True, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("SKU Cluster Assignment")
    dc = df_cl[["Product","Category","Cluster_Name",
                "Total_Revenue","Volatility_CV",
                "Seasonality_Strength"]]\
         .sort_values("Total_Revenue",ascending=False).copy()
    dc["Total_Revenue"] = dc["Total_Revenue"].apply(
        lambda x: f"₹{x/1e6:.2f}M")
    dc.columns = ["Product","Category","Cluster",
                  "Revenue","Volatility CV","Seasonality"]
    st.dataframe(dc, hide_index=True,
                 use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    r1,r2,r3 = st.columns(3)
    with r1:
        insight("<b style='color:#D4AC0D;'>💰 Revenue Giants</b><br>"
                "3 SKUs · 60.4% of portfolio revenue. "
                "Ghee 500ml, Ghee 15kg, Ghee 200ml. "
                "<b>Zero stockout tolerance.</b>",style="warning")
    with r2:
        insight("<b style='color:#6C3483;'>🎉 Festival Rockets</b><br>"
                "4 SKUs · extreme Onam and Vishu spikes. "
                "Quiet most of year. "
                "<b>Surge stock 6 weeks before festivals.</b>")
    with r3:
        insight("<b style='color:#1E8449;'>📦 Core Portfolio</b><br>"
                "35 SKUs · stable predictable demand. "
                "Standard replenishment sufficient. "
                "<b>Monthly review recommended.</b>",style="success")


# ══════════════════════════════════════════════════════════════
# PAGE 4 — FORECASTING
# ══════════════════════════════════════════════════════════════
elif page == "🏆  Forecasting Tournament":
    st.markdown("""
    <div class='page-header'>
        <h1>🏆 Prophet vs XGBoost — Forecasting Tournament</h1>
        <p>Fair comparison on identical 12-month holdout 
           (Jan–Dec 2025) · 2026 demand forecasts</p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi("XGBoost","Tournament Champion",
        "Wins 5 of 6 categories",color="green"),
        unsafe_allow_html=True)
    c2.markdown(kpi("12.07%","Best MAPE — Ghee",
        "Excellent accuracy",color="green"),
        unsafe_allow_html=True)
    c3.markdown(kpi("2 / 6","Excellent Forecasts",
        "MAPE below 20%"), unsafe_allow_html=True)
    c4.markdown(kpi("3 / 6","Need Manual Planning",
        "MAPE above 70%",color="red"),
        unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col1,col2 = st.columns(2, gap="large")

    with col1:
        section("Tournament Results")
        def q_style(v):
            if v=="Excellent":
                return f"background:#EAFAF1;color:{SUCCESS};font-weight:600"
            elif v=="Acceptable":
                return f"background:#FEF9E7;color:{WARNING};font-weight:600"
            return f"background:#FDEDEC;color:{DANGER};font-weight:600"

        def m_style(v):
            try:
                f = float(v)
                if f<20: return f"color:{SUCCESS};font-weight:600"
                if f<50: return f"color:{WARNING};font-weight:600"
                return f"color:{DANGER};font-weight:600"
            except: return ""

        ts = tournament[[
            "Category","Prophet_MAPE","XGBoost_MAPE",
            "Champion","Champion_MAPE","Quality"]].copy()
        ts.columns = ["Category","Prophet %","XGBoost %",
                      "Champion","Best MAPE %","Quality"]
        styled = (ts.style
            .applymap(q_style, subset=["Quality"])
            .applymap(m_style, subset=["Prophet %",
                                        "XGBoost %",
                                        "Best MAPE %"])
            .format({"Prophet %":"{:.2f}",
                     "XGBoost %":"{:.2f}",
                     "Best MAPE %":"{:.2f}"})
            .set_properties(**{"text-align":"center",
                                "font-size":"13px"}))
        st.dataframe(styled, hide_index=True,
                     use_container_width=True)

    with col2:
        section("MAPE Comparison Chart")
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            name="Prophet", x=tournament["Category"],
            y=tournament["Prophet_MAPE"],
            marker_color=PURPLE, marker_line_width=0,
            text=tournament["Prophet_MAPE"].round(1),
            textposition="outside",
            textfont=dict(size=10)))
        fig1.add_trace(go.Bar(
            name="XGBoost", x=tournament["Category"],
            y=tournament["XGBoost_MAPE"],
            marker_color=ACCENT, marker_line_width=0,
            text=tournament["XGBoost_MAPE"].round(1),
            textposition="outside",
            textfont=dict(size=10)))
        fig1.add_hline(y=20, line_dash="dot",
            line_color=SUCCESS, line_width=1.5,
            annotation_text="Excellent ≤20%",
            annotation_font_color=SUCCESS,
            annotation_font_size=10)
        fig1.add_hline(y=50, line_dash="dot",
            line_color=DANGER, line_width=1.5,
            annotation_text="Poor >50%",
            annotation_font_color=DANGER,
            annotation_font_size=10)
        fig1.update_layout(barmode="group")
        chart_fmt(fig1, height=340)
        fig1.update_layout(
            yaxis_title="MAPE (%)",
            legend=dict(orientation="h",y=-0.2,x=0.3))
        st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("2026 Monthly Demand Forecast")

    sel_cat_f = st.multiselect(
        "Select categories",
        options=forecast["Category"].unique(),
        default=list(forecast["Category"].unique()))

    if sel_cat_f:
        ff = forecast[forecast["Category"].isin(sel_cat_f)]
        fig2 = go.Figure()
        for cat in sel_cat_f:
            cd = ff[ff["Category"]==cat]
            col = CATEGORY_COLORS.get(cat, ACCENT)
            if ("Upper_95" in cd.columns and
                    "Lower_95" in cd.columns):
                fig2.add_trace(go.Scatter(
                    x=pd.concat([cd["Date"],
                                  cd["Date"].iloc[::-1]]),
                    y=pd.concat([cd["Upper_95"],
                                  cd["Lower_95"].iloc[::-1]]),
                    fill="toself",
                    fillcolor=col+"22",
                    line=dict(color="rgba(0,0,0,0)"),
                    showlegend=False,hoverinfo="skip"))
            fig2.add_trace(go.Scatter(
                x=cd["Date"], y=cd["Forecast"],
                name=cat,
                line=dict(color=col,width=2.5),
                mode="lines+markers",
                marker=dict(size=7,
                            line=dict(color=WHITE,width=1))))
        chart_fmt(fig2, height=380)
        fig2.update_layout(
            xaxis_title="Month (2026)",
            yaxis_title="Forecast Revenue (₹)",
            legend=dict(orientation="h",y=-0.18,x=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    r1,r2 = st.columns(2)
    with r1:
        insight("<b style='color:#1E8449;'>✅ Why XGBoost Won 5/6</b><br>"
                "2025 structural demand changes violated Prophet's "
                "decomposition assumptions. XGBoost's "
                "<b>year encoding and lag features</b> adapted better "
                "to structural shifts than trend decomposition.",
                style="success")
    with r2:
        insight("<b style='color:#D4AC0D;'>⚠️ Why 3 Categories Failed</b><br>"
                "UHT Milk (85% collapse since 2022), "
                "Milk Powder (product expansion 2025), "
                "Instant Mixes (CV=1.998). "
                "<b>No model can predict structural breaks.</b> "
                "Manual planning required.",style="warning")


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
    top3_sh   = bi3.nlargest(3,"Total_Revenue")[
        "Revenue_Share_Pct"].sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi(f"{critical}","CRITICAL SKUs",
        "Each >10% portfolio",color="red"),
        unsafe_allow_html=True)
    c2.markdown(kpi(f"{top3_sh:.1f}%","Top 3 Revenue Share",
        "3-6-40 rule",color="amber"),
        unsafe_allow_html=True)
    c3.markdown(kpi(f"{growing}","Growing SKUs",
        "At all-time peak",color="green"),
        unsafe_allow_html=True)
    c4.markdown(kpi(f"{disrupted}","Disrupted SKUs",
        "Below peak, not recovering",color="red"),
        unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col1,col2 = st.columns(2, gap="large")

    with col1:
        section("Concentration Flag Distribution")
        conc = bi3["Concentration_Flag"].value_counts()\
                   .reset_index()
        conc.columns = ["Flag","Count"]
        fc = {"CRITICAL":DANGER,"HIGH":ORANGE,
              "MODERATE":WARNING,"LOW":ACCENT}
        fig1 = px.pie(conc, values="Count", names="Flag",
                      hole=0.5, color="Flag",
                      color_discrete_map=fc)
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
        rec = bi7["Recovery_Status"].value_counts()\
                  .reset_index()
        rec.columns = ["Status","Count"]
        rc = {"GROWING":SUCCESS,"STABLE":TEAL,
              "RECOVERING":WARNING,"DISRUPTED":DANGER}
        fig2 = px.pie(rec, values="Count", names="Status",
                      hole=0.5, color="Status",
                      color_discrete_map=rc)
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
    bc = [DANGER if r<50 else WARNING if r<90 else SUCCESS
          for r in rs["Recovery_Rate_Pct"]]
    fig3 = go.Figure(go.Bar(
        x=rs["Recovery_Rate_Pct"],
        y=rs["Product"],
        orientation="h",
        marker_color=bc, marker_line_width=0,
        text=rs["Recovery_Rate_Pct"].round(0)\
              .astype(int).astype(str)+"%",
        textposition="outside",
        textfont=dict(size=9,color=TEXT_DARK)))
    fig3.add_vline(x=100, line_dash="dash",
        line_color=TEXT_MID, line_width=1,
        annotation_text="Peak 100%",
        annotation_font_size=10,
        annotation_font_color=TEXT_MID)
    chart_fmt(fig3, height=680, show_legend=False)
    fig3.update_layout(
        xaxis_title="Recovery Rate % vs Peak Revenue",
        yaxis=dict(tickfont=dict(size=9)),
        margin=dict(l=10,r=60,t=20,b=10))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("Severely Disrupted SKUs")
    dd = bi7[bi7["Recovery_Status"]=="DISRUPTED"][[
        "Product","Category","Peak_Year",
        "Recovery_Rate_Pct","YoY_Growth_Pct"]].copy()
    dd.columns = ["Product","Category","Peak Year",
                  "Recovery Rate %","YoY Growth %"]
    st.dataframe(dd.sort_values("Recovery Rate %"),
                 hide_index=True, use_container_width=True)
    insight("<b>Ok Ghee 50ml</b> — Peak ₹47.3M (2021) → "
            "Current ₹1.9M (2025). 96% collapse. "
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
           concentration · recovery · 42 SKUs</p>
    </div>""", unsafe_allow_html=True)

    t1 = len(recsys[recsys["Planning_Tier"].str.contains(
        "TIER 1",na=False)])
    t2 = len(recsys[recsys["Planning_Tier"].str.contains(
        "TIER 2",na=False)])
    t3 = len(recsys[recsys["Planning_Tier"].str.contains(
        "TIER 3",na=False)])
    protect = len(recsys[recsys["Recommended_Action"]\
        .str.contains("PROTECT",na=False)])

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi(f"{t1}","Tier 1 — Algorithm",
        "Forecasts trusted",color="green"),
        unsafe_allow_html=True)
    c2.markdown(kpi(f"{t2}","Tier 2 — Caution",
        "Validate before order",color="amber"),
        unsafe_allow_html=True)
    c3.markdown(kpi(f"{t3}","Tier 3 — Manual",
        "Human judgment needed",color="red"),
        unsafe_allow_html=True)
    c4.markdown(kpi(f"{protect}","PROTECT SKUs",
        "Zero stockout tolerance"),
        unsafe_allow_html=True)

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
        f"<p style='color:{TEXT_MID};font-size:0.85em;'>"
        f"Showing {len(dr)} of {len(recsys)} SKUs</p>",
        unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col1,col2 = st.columns(2, gap="large")

    with col1:
        section("Actions Distribution")
        ac = dr["Recommended_Action"].value_counts()\
               .reset_index()
        ac.columns = ["Action","Count"]
        ac["Short"] = ac["Action"].str.split("—")\
                         .str[0].str.strip()
        ac = ac.sort_values("Count")
        fig1 = go.Figure(go.Bar(
            x=ac["Count"], y=ac["Short"],
            orientation="h",
            marker_color=[ACTION_COLORS.get(a, ACCENT)
                          for a in ac["Action"]],
            marker_line_width=0,
            text=ac["Count"],
            textposition="outside",
            textfont=dict(size=11)))
        chart_fmt(fig1, height=320, show_legend=False)
        fig1.update_layout(
            xaxis_title="Number of SKUs",
            yaxis=dict(tickfont=dict(size=10)))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        section("Planning Tier Split")
        tc = dr["Planning_Tier"].value_counts().reset_index()
        tc.columns = ["Tier","Count"]
        tc["Short"] = tc["Tier"].str.split("—")\
                         .str[0].str.strip()
        tcols = []
        for t in tc["Tier"]:
            if "TIER 1" in t: tcols.append(SUCCESS)
            elif "TIER 2" in t: tcols.append(WARNING)
            else: tcols.append(DANGER)
        fig2 = px.pie(tc, values="Count", names="Short",
                      hole=0.5,
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
            "Product","Priority_Score",
            "Recommended_Action"]].copy()
        tp["Action"] = tp["Recommended_Action"]\
            .str.split("—").str[0].str.strip()
        tp["Priority_Score"] = tp["Priority_Score"].round(1)
        st.dataframe(
            tp[["Product","Priority_Score","Action"]],
            hide_index=True,use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    section("Master SKU Recommendation Table")

    dcols = ["Product","Category","Cluster_Name",
             "Concentration_Flag","Recovery_Status",
             "Planning_Tier","Champion_MAPE",
             "Priority_Score","Recommended_Action"]
    dcols = [c for c in dcols if c in dr.columns]
    tbl = dr[dcols].sort_values(
        "Priority_Score",ascending=False).copy()
    if "Champion_MAPE" in tbl.columns:
        tbl["Champion_MAPE"] = tbl["Champion_MAPE"].round(2)
    if "Priority_Score" in tbl.columns:
        tbl["Priority_Score"] = tbl["Priority_Score"].round(1)

    def style_row(row):
        act   = row.get("Recommended_Action","")
        color = ACTION_COLORS.get(act,"")
        base  = f"color:{TEXT_DARK}"
        if color:
            return [
                f"background:{color}22;color:{TEXT_DARK};"
                f"font-weight:600"
                if col=="Recommended_Action" else base
                for col in row.index]
        return [base for _ in row.index]

    st.dataframe(
        tbl.style.apply(style_row, axis=1)
           .set_properties(**{"font-size":"12px",
                               "border":f"1px solid {BORDER}"}),
        hide_index=True, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    r1,r2,r3 = st.columns(3)
    with r1:
        insight(f"<b style='color:{SUCCESS};'>"
                f"✅ Tier 1 — {t1} SKUs</b><br>"
                "Algorithm driven. Use forecasts directly "
                "for procurement. Ghee, Butter, Palada.",
                style="success")
    with r2:
        insight(f"<b style='color:{WARNING};'>"
                f"⚡ Tier 2 — {t2} SKUs</b><br>"
                "Validate forecasts before ordering. "
                "Disrupted Ghee variants and recovering Palada.",
                style="warning")
    with r3:
        insight(f"<b style='color:{DANGER};'>"
                f"❌ Tier 3 — {t3} SKUs</b><br>"
                "Forecasts unreliable. Human expert review "
                "required. UHT Milk, Milk Powder, Instant Mixes.",
                style="danger")
