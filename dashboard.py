# ==================================================
# PART 1 : Market Context Bar & Screener Panel
# ==================================================

# ==================================================
# IMPORTS
# ==================================================

import streamlit as st
import pandas as pd
import numpy as np

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="MF Screener",
    page_icon="📈",
    layout="wide"
)

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.main {
    padding-top: 0.5rem;
}

.block-container{
    padding-top:1rem;
    max-width:95%;
}

section[data-testid="stSidebar"]{
    background:#f8fafc;
    border-right:1px solid #e5e7eb;
    width:300px !important;
}

.stButton button{
    width:100%;
    border-radius:10px;
}

div[data-testid="metric-container"]{
    background:white;
    border:1px solid #e5e7eb;
    border-radius:12px;
    padding:12px;
    box-shadow:0px 2px 6px rgba(0,0,0,0.04);
}

[data-testid="stDataFrame"]{
    border:1px solid #e5e7eb;
    border-radius:12px;
}

thead tr th{
    font-size:12px !important;
    font-weight:600 !important;
}

tbody tr td{
    font-size:12px !important;
}         

</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================

st.markdown("""
<h1 style="
font-size:32px;
font-weight:700;
margin-bottom:0px;
">
📈 Real-Time Mutual Fund Screener
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style="
font-size:16px;
color:#6b7280;
margin-top:-8px;
margin-bottom:20px;
">
Rank mutual funds using Returns, Sharpe Ratio,
Sortino Ratio, Drawdown Analysis and Composite Scoring.
</p>
""", unsafe_allow_html=True)

# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data
def load_data():

    scored = pd.read_csv(
        "data/scored_schemes.csv"
    )

    nav = pd.read_parquet(
        "data/nav_history.parquet"
    )

    market = pd.read_csv(
        "data/market_context.csv"
    )

    return scored, nav, market


scored, nav, market = load_data()

# ==================================================
# MARKET CONTEXT
# ==================================================

st.markdown("""
<h2 style="
font-size:20px;
font-weight:600;
margin-bottom:10px;
">
🌍 Market Context
</h2>
""", unsafe_allow_html=True)

market_names = {

    "Nifty50_1Y_Return":"Nifty 50",
    "Midcap150_1Y_Return":"Midcap 150",
    "Smallcap250_1Y_Return":"Smallcap 250",
    "Repo_Rate":"Repo Rate",
    "CPI_Inflation":"Inflation",
    "Industry_AUM":"Industry AUM"

}

market_icons = {

    "Nifty50_1Y_Return":"📊",
    "Midcap150_1Y_Return":"📈",
    "Smallcap250_1Y_Return":"🚀",
    "Repo_Rate":"🏦",
    "CPI_Inflation":"🔥",
    "Industry_AUM":"💰"

}

market_cols = st.columns(6)

for col, (_, row) in zip(
    market_cols,
    market.iterrows()
):

    metric = row["metric"]

    with col:

        st.markdown(
            f"""
            <div style="
            background:white;
            border:1px solid #e5e7eb;
            border-radius:15px;
            padding:14px;
            height:110px;
            box-shadow:0 2px 6px rgba(0,0,0,0.04);
            ">

            <div style="
            font-size:15px;
            ">
            {market_icons.get(metric,'📊')}
            </div>

            <div style="
            color:#6b7280;
            font-size:12px;
            margin-top:5px;
            ">
            {market_names.get(metric,metric)}
            </div>

            <div style="
            font-size:22px;
            font-weight:700;
            margin-top:8px;
            ">
            {row["value"]}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.markdown("""
<h3 style="
font-size:18px;
font-weight:600;
">
🔎 Fund Filters
</h3>
""", unsafe_allow_html=True)

if st.sidebar.button(
    "🗑️ Clear All Filters",
    width="stretch"
):

    st.session_state["category"] = []
    st.session_state["amc"] = []
    st.session_state["plan"] = []
    st.session_state["risk"] = []
    st.session_state["horizon"] = []

    st.rerun()

# ==================================================
# FILTERS
# ==================================================

category_filter = st.sidebar.multiselect(
    "Category",
    sorted(
        scored["category"]
        .dropna()
        .unique()
    ),
    key="category"
)

amc_filter = st.sidebar.multiselect(
    "AMC",
    sorted(
        scored["amc"]
        .dropna()
        .unique()
    ),
    key="amc"
)

plan_filter = st.sidebar.multiselect(
    "Plan Type",
    sorted(
        scored["plan_type"]
        .dropna()
        .unique()
    ),
    key="plan"
)

risk_filter = st.sidebar.multiselect(
    "Risk Level",
    sorted(
        scored["risk_level"]
        .dropna()
        .unique()
    ),
    key="risk"
)

horizon_filter = st.sidebar.multiselect(
    "Horizon",
    sorted(
        scored["horizon"]
        .dropna()
        .unique()
    ),
    key="horizon"
)

st.sidebar.markdown("---")

st.sidebar.info(
"""
💡 Tip

Use filters to narrow down funds
based on category, AMC,
risk profile and investment horizon.
"""
)

# ==================================================
# APPLY FILTERS
# ==================================================

filtered = scored.copy()

if category_filter:
    filtered = filtered[
        filtered["category"]
        .isin(category_filter)
    ]

if amc_filter:
    filtered = filtered[
        filtered["amc"]
        .isin(amc_filter)
    ]

if plan_filter:
    filtered = filtered[
        filtered["plan_type"]
        .isin(plan_filter)
    ]

if risk_filter:
    filtered = filtered[
        filtered["risk_level"]
        .isin(risk_filter)
    ]

if horizon_filter:
    filtered = filtered[
        filtered["horizon"]
        .isin(horizon_filter)
    ]

# ==================================================
# EMPTY RESULT HANDLING
# ==================================================

if len(filtered) == 0:

    st.warning(
        "No schemes match selected filters."
    )

    st.stop()

# ==================================================
# TOP RANKED FUND
# ==================================================

best = filtered.loc[
    filtered["composite_score"]
    .idxmax()
]

st.markdown("""
<h3 style="
font-size:20px;
font-weight:600;
margin-bottom:10px;
">
🏆 Top Ranked Fund
</h3>
""", unsafe_allow_html=True)

st.markdown(
f"""
<div style="
background:#f0fdf4;
border-left:4px solid #22c55e;
padding:12px 18px;
border-radius:10px;
">

<div style="
font-size:14px;
font-weight:600;
color:#15803d;
">
🏅 {best['scheme_name']}
</div>

<div style="
font-size:13px;
margin-top:8px;
color:#374151;
">
📂 {best['category']}
</div>

<div style="
font-size:14px;
font-weight:600;
margin-top:8px;
color:#15803d;
">
⭐ Score: {best['composite_score']:.2f}
</div>

</div>
""",
unsafe_allow_html=True
)

st.markdown(
"<hr style='margin:12px 0;'>",
unsafe_allow_html=True
)

# ==================================================
# QUICK STATS
# ==================================================

stats = st.columns(4)

items = [

("📋","Funds",len(filtered)),
("📈","Avg Score",round(filtered["composite_score"].mean(),2)),
("🎯","Top Score",round(filtered["composite_score"].max(),2)),
("🏢","AMCs",filtered["amc"].nunique())

]

for col,(icon,title,val) in zip(stats,items):

    with col:

        st.markdown(f"""
        <div style="
        background:white;
        border:1px solid #e5e7eb;
        border-radius:10px;
        padding:10px;
        ">

        <div style="
        font-size:12px;
        color:#6b7280;
        ">
        {icon} {title}
        </div>

        <div style="
        font-size:20px;
        font-weight:600;
        margin-top:4px;
        ">
        {val}
        </div>

        </div>
        """,
        unsafe_allow_html=True)

# ==================================================
# FUND SCREENER TABLE
# ==================================================

st.markdown("""
<h3 style="
font-size:20px;
font-weight:600;
margin-bottom:10px;
">
🏆 Fund Screener
</h3>
""", unsafe_allow_html=True)

display_cols = [

    "badge",
    "scheme_name",
    "amc",
    "category",

    "return_1y",
    "return_3y",

    "cagr_1y",
    "cagr_3y",
    "cagr_5y",

    "beta",

    "sharpe_ratio",
    "sortino_ratio",
    "max_drawdown",

    "composite_score"
]

table = (

    filtered[
        display_cols
    ]

    .sort_values(
        "composite_score",
        ascending=False
    )

    .copy()
)

table.columns = [

    "🏅",
    "Scheme",
    "AMC",
    "Category",

    "1Y Return",
    "3Y Return",

    "1Y CAGR",
    "3Y CAGR",
    "5Y CAGR",

    "Beta",

    "Sharpe",
    "Sortino",
    "Max DD",

    "Score"
]

# ==================================================
# TOP 3 BADGES PER CATEGORY
# ==================================================

table["🏅"] = ""

for category in table["Category"].unique():

    category_idx = (

        table[
            table["Category"]
            ==
            category
        ]

        .sort_values(
            "Score",
            ascending=False
        )

        .index
    )

    if len(category_idx) >= 1:
        table.loc[
            category_idx[0],
            "🏅"
        ] = "🥇"

    if len(category_idx) >= 2:
        table.loc[
            category_idx[1],
            "🏅"
        ] = "🥈"

    if len(category_idx) >= 3:
        table.loc[
            category_idx[2],
            "🏅"
        ] = "🥉"

table[
    [
        "1Y Return",
        "3Y Return",
        "Sharpe",
        "Sortino",
        "Max DD",
        "Score"
    ]
] = table[
    [
        "1Y Return",
        "3Y Return",
        "Sharpe",
        "Sortino",
        "Max DD",
        "Score"
    ]
].round(2)

table["1Y Return"] = (
    table["1Y Return"]
    .astype(str)
    + "%"
)

table["3Y Return"] = (
    table["3Y Return"]
    .astype(str)
    + "%"
)

table["Max DD"] = (
    table["Max DD"]
    .astype(str)
    + "%"
)

rows = len(table)

table_height = min(
    380,
    max(120, rows * 38 + 40)
)

st.dataframe(
    table,
    width="stretch",
    height=table_height,
    hide_index=True
)

# ==================================================
# SUMMARY
# ==================================================

st.markdown("---")

s1,s2,s3 = st.columns(3)

summary = [

("📋","Schemes",len(filtered)),
("📂","Categories",filtered["category"].nunique()),
("🏢","AMCs",filtered["amc"].nunique())

]

for col,(icon,title,val) in zip(
[s1,s2,s3],
summary
):

    with col:

        st.markdown(f"""
        <div style="
        background:white;
        border:1px solid #e5e7eb;
        border-radius:10px;
        padding:12px;
        ">

        <div style="
        font-size:12px;
        color:#6b7280;
        ">
        {icon} {title}
        </div>

        <div style="
        font-size:20px;
        font-weight:600;
        margin-top:4px;
        ">
        {val}
        </div>

        </div>
        """,
        unsafe_allow_html=True)

# ==================================================
# PART 2 : SCORE BREAKDOWN & FUND ANALYSIS
# ==================================================

import plotly.graph_objects as go

st.markdown("---")

st.markdown("""
<h2 style="
font-size:24px;
font-weight:700;
margin-top:20px;
margin-bottom:15px;
">
📝 Fund Analysis
</h2>
""",
unsafe_allow_html=True)

# ==================================================
# FUND SELECTOR
# ==================================================

selected_scheme = st.selectbox(
    "🔍 Select Mutual Fund",
    filtered["scheme_name"]
    .sort_values()
    .unique()
)

# ==================================================
# GET SELECTED FUND
# ==================================================

scheme = filtered[
    filtered["scheme_name"]
    == selected_scheme
].iloc[0]

# ==================================================
# TOP METRICS CARDS
# ==================================================

metric_cols = st.columns(4)

metrics = [

    (
        "⭐ Composite Score",
        round(
            scheme["composite_score"],
            2
        )
    ),

    (
        "🏆 Category Rank",
        "NA"
        if pd.isna(
            scheme["category_rank"]
        )
        else
        int(
            scheme["category_rank"]
        )
    ),

    (
        "📈 1Y Return",
        f"{scheme['return_1y']:.2f}%"
    ),

    (
        "⚖️ Sharpe Ratio",
        round(
            scheme["sharpe_ratio"],
            2
        )
    )

]

for col, (title, value) in zip(
    metric_cols,
    metrics
):

    with col:

        st.markdown(
            f"""
            <div style="
            background:white;
            border:1px solid #e5e7eb;
            border-radius:12px;
            padding:14px;
            box-shadow:0px 2px 6px rgba(0,0,0,0.04);
            ">

            <div style="
            color:#6b7280;
            font-size:13px;
            ">
            {title}
            </div>

            <div style="
            font-size:22px;
            font-weight:700;
            margin-top:6px;
            ">
            {value}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ==================================================
# RADAR CHART + RANKINGS
# ==================================================

left, right = st.columns([2, 1])

# ==================================================
# RADAR CHART
# ==================================================

with left:

    st.markdown("""
    <h3 style="
    font-size:18px;
    font-weight:600;
    ">
    📈 Performance Score Radar
    </h3>
    """,
    unsafe_allow_html=True)

    radar = go.Figure()

    radar.add_trace(

        go.Scatterpolar(

            r=[

                scheme["return_1y_score"],
                scheme["return_3y_score"],
                scheme["sharpe_score"],
                scheme["sortino_score"],
                scheme["drawdown_score"]

            ],

            theta=[

                "1Y Return",
                "3Y Return",
                "Sharpe",
                "Sortino",
                "Drawdown"

            ],

            fill="toself",

            name="Score"

        )
    )

    radar.update_layout(

        polar=dict(

            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )

        ),

        showlegend=False,

        height=400

    )

    st.plotly_chart(
        radar,
        width="stretch"
    )

# ==================================================
# METRIC RANK TABLE
# ==================================================

with right:

    st.markdown("""
    <h3 style="
    font-size:18px;
    font-weight:600;
    ">
    🏅 Metric Rankings
    </h3>
    """,
    unsafe_allow_html=True)

    rank_df = pd.DataFrame({
        "Metric":[
            "1Y Return",
            "3Y Return",
            "Sharpe",
            "Sortino",
            "Drawdown"
        ],
        
        "Rank":[
            scheme["return_1y_rank"],
            scheme["return_3y_rank"],
            scheme["sharpe_rank"],
            scheme["sortino_rank"],
            scheme["drawdown_rank"]
        ]
    })
    
    rank_df["Rank"] = (
        rank_df["Rank"]
        .fillna("-")
        .astype(str)
)

    st.dataframe(
    rank_df,
    width="stretch",
    hide_index=True,
    height=185
)

# ==================================================
# FUND ANALYSIS SECTION
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<h3 style="
font-size:22px;
font-weight:700;
">
📝 Fund Analysis
</h3>
""",
unsafe_allow_html=True)

# ==================================================
# STRENGTH / WEAKNESS ENGINE
# ==================================================

strengths = []
weaknesses = []

# Recent Performance

if scheme["return_1y_score"] > 75:

    strengths.append(
        "Strong recent performance"
    )

elif scheme["return_1y_score"] < 40:

    weaknesses.append(
        "Weak recent performance"
    )

# Sharpe Ratio

if scheme["sharpe_score"] > 75:

    strengths.append(
        "Excellent risk-adjusted returns"
    )

elif scheme["sharpe_score"] < 40:

    weaknesses.append(
        "Poor risk-adjusted returns"
    )

# Sortino Ratio

if scheme["sortino_score"] > 75:

    strengths.append(
        "Strong downside protection"
    )

elif scheme["sortino_score"] < 40:

    weaknesses.append(
        "Weak downside protection"
    )

# Drawdown

if scheme["drawdown_score"] > 75:

    strengths.append(
        "Low historical drawdowns"
    )

elif scheme["drawdown_score"] < 40:

    weaknesses.append(
        "High historical drawdowns"
    )

# ==================================================
# GENERATE ANALYSIS
# ==================================================
if pd.notna(
    scheme["beta"]
):

    if scheme["beta"] > 1:

        beta_text = (
            "More volatile than Nifty 50"
        )

    elif scheme["beta"] < 1:

        beta_text = (
            "Less volatile than Nifty 50"
        )

    else:

        beta_text = (
            "Moves similar to Nifty 50"
        )

else:

    beta_text = "NA"
analysis = f"""
<b>Beta Interpretation:</b>
{beta_text}
<b>{scheme['scheme_name']}</b>

<br><br>

<b>Composite Score:</b>
{scheme['composite_score']:.2f}

<br>

<b>Risk Level:</b>
{scheme['risk_level']}

<br>

<b>Investment Horizon:</b>
{scheme['horizon']}

<b>Beta:</b>
{scheme['beta']:.2f}
"""

if strengths:

    analysis += "<br><br><b>✅ Strengths</b><br>"

    for s in strengths:

        analysis += f"• {s}<br>"

if weaknesses:

    analysis += "<br><br><b>⚠️ Weaknesses</b><br>"

    for w in weaknesses:

        analysis += f"• {w}<br>"

# ==================================================
# DISPLAY ANALYSIS CARD
# ==================================================

st.markdown(
f"""
<div style="
background:linear-gradient(135deg,#f0fdf4,#ecfeff);
border:1px solid #d1fae5;
border-left:5px solid #22c55e;
border-radius:12px;
padding:14px 18px;
box-shadow:0px 2px 6px rgba(0,0,0,0.04);
">

<div style="
font-size:15px;
font-weight:600;
color:#166534;
margin-bottom:8px;
">
🏆 {scheme['scheme_name']}
</div>

<div style="
font-size:13px;
color:#374151;
line-height:1.5;
">

⭐ <b>Composite Score:</b> {scheme['composite_score']:.2f}
&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
⚠️ <b>Risk:</b> {scheme['risk_level']}
&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
🎯 <b>Horizon:</b> {scheme['horizon']}
📊 <b>Beta:</b> {scheme['beta']:.2f}
📈 <b>Market Sensitivity:</b> {beta_text}

</div>

{"<hr style='margin:10px 0;border:none;border-top:1px solid #d1d5db;'>" if strengths or weaknesses else ""}

{"<div style='color:#15803d;font-size:13px;font-weight:600;'>✅ Strengths</div>" if strengths else ""}

{"".join([f"<div style='font-size:12px;color:#374151;'>• {s}</div>" for s in strengths])}

{"<div style='margin-top:8px;color:#dc2626;font-size:13px;font-weight:600;'>⚠️ Weaknesses</div>" if weaknesses else ""}

{"".join([f"<div style='font-size:12px;color:#374151;'>• {w}</div>" for w in weaknesses])}

</div>
""",
unsafe_allow_html=True
)

# ==================================================
# PART 3 : NAV TREND ANALYSIS
# ==================================================

import requests
import plotly.express as px
import plotly.graph_objects as go

st.markdown("---")

st.markdown("""
<h2 style="
font-size:24px;
font-weight:700;
margin-top:20px;
margin-bottom:15px;
">
📈 NAV Trend Analysis
</h2>
""", unsafe_allow_html=True)

# ==================================================
# GET SCHEME DETAILS
# ==================================================

scheme_code = str(
    int(
        scheme["scheme_code"]
    )
)

scheme_category = (
    scheme["category"]
)

# ==================================================
# PREPARE NAV DATA
# ==================================================

nav["scheme_code"] = (
    nav["scheme_code"]
    .astype(str)
)

nav["date"] = pd.to_datetime(
    nav["date"]
)

scheme_nav = nav[
    nav["scheme_code"]
    == scheme_code
].copy()

scheme_nav.sort_values(
    "date",
    inplace=True
)

# ==================================================
# CATEGORY AVERAGE NAV
# ==================================================

category_lookup = scored[
    [
        "scheme_code",
        "category"
    ]
].copy()

category_lookup[
    "scheme_code"
] = category_lookup[
    "scheme_code"
].astype(str)

nav_category = nav.merge(
    category_lookup,
    on="scheme_code",
    how="left"
)

category_nav = nav_category[
    nav_category["category"]
    ==
    scheme_category
]

category_avg = (
    category_nav
    .groupby("date")["nav"]
    .mean()
    .reset_index()
)

category_avg = category_avg[
    category_avg["nav"] > 1
]

category_avg = category_avg[
    category_avg["nav"]
    <
    category_avg["nav"].quantile(0.99)
]

category_avg.rename(
    columns={
        "nav":
        "category_avg_nav"
    },
    inplace=True
)

# ==================================================
# NAV COMPARISON CHART
# ==================================================

st.markdown("""
<h3 style="
font-size:18px;
font-weight:600;
margin-bottom:10px;
">
📊 NAV Trend vs Category Average
</h3>
""", unsafe_allow_html=True)

# Normalize NAVs for fair comparison

scheme_nav["norm_nav"] = (
    scheme_nav["nav"]
    /
    scheme_nav["nav"].iloc[0]
) * 100

category_avg["norm_nav"] = (
    category_avg["category_avg_nav"]
    /
    category_avg["category_avg_nav"].iloc[0]
) * 100

fig_nav = go.Figure()

fig_nav.add_trace(
    go.Scatter(
        x=scheme_nav["date"],
        y=scheme_nav["norm_nav"],
        mode="lines",
        name="Selected Fund",
        line=dict(width=3)
    )
)

fig_nav.add_trace(
    go.Scatter(
        x=category_avg["date"],
        y=category_avg["norm_nav"],
        mode="lines",
        name="Category Average",
        line=dict(width=3)
    )
)

fig_nav.update_layout(
    template="plotly_white",
    height=350,
    title="Growth Comparison (Base = 100)",
    xaxis_title="Date",
    yaxis_title="Normalized NAV (Base = 100)",
    hovermode="x unified",
    margin=dict(
        l=20,
        r=20,
        t=50,
        b=20
    ),
    legend=dict(
        orientation="h",
        y=1.1
    )
)



st.plotly_chart(
    fig_nav,
    width="stretch"
)

# ==================================================
# ROLLING 3 MONTH RETURN
# ==================================================

scheme_nav[
    "rolling_3m_return"
] = (

    scheme_nav[
        "nav"
    ]

    .pct_change(
        63
    )

    * 100
)

st.markdown("""
<h3 style="
font-size:18px;
font-weight:600;
margin-bottom:10px;
">
📈 Rolling 3-Month Return
</h3>
""", unsafe_allow_html=True)

fig_roll = px.line(
    scheme_nav,
    x="date",
    y="rolling_3m_return"
)

fig_roll.update_traces(
    line_width=3
)

fig_roll.add_hline(
    y=0,
    line_dash="dash"
)

fig_roll.update_layout(
    template="plotly_white",
    height=300,
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    )
)

st.plotly_chart(
    fig_roll,
    width="stretch"
)

# ==================================================
# LIVE NAV POLLING
# ==================================================

@st.cache_data(ttl=300)
def get_live_nav(code):

    try:

        url = (
            f"https://api.mfapi.in/mf/{code}"
        )

        headers = {
            "User-Agent":
            "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if "data" not in data:
            return None

        return data

    except Exception:
        return None

live_nav = get_live_nav(
    scheme_code
)

# ==================================================
# LIVE NAV SECTION
# ==================================================

st.markdown("""
<h3 style="
font-size:18px;
font-weight:600;
margin-bottom:10px;
">
⚡ Live NAV
</h3>
""", unsafe_allow_html=True)

if (

    live_nav is not None

    and

    "data" in live_nav

    and

    len(
        live_nav["data"]
    ) > 0

):

    latest = live_nav[
        "data"
    ][0]

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
            <div style="
            background:white;
            border:1px solid #e5e7eb;
            border-radius:12px;
            padding:10px;
            ">

            <div style="
            font-size:11px;
            color:#6b7280;
            ">
            Latest NAV
            </div>

            <div style="
            font-size:18px;
            font-weight:700;
            margin-top:5px;
            ">
            ₹ {float(latest['nav']):.2f}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div style="
            background:white;
            border:1px solid #e5e7eb;
            border-radius:12px;
            padding:10px;
            ">

            <div style="
            font-size:11px;
            color:#6b7280;
            ">
            NAV Date
            </div>

            <div style="
            font-size:18px;
            font-weight:700;
            margin-top:5px;
            ">
            {latest['date']}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

else:

    st.warning(
        "Live NAV currently unavailable."
    )

# ==================================================
# NAV STATISTICS
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<h3 style="
font-size:18px;
font-weight:600;
margin-bottom:10px;
">
📊 NAV Statistics
</h3>
""", unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)

stats = [

    (
        "💰 Current NAV",
        round(
            scheme_nav[
                "nav"
            ].iloc[-1],
            2
        )
    ),

    (
        "📈 Highest NAV",
        round(
            scheme_nav[
                "nav"
            ].max(),
            2
        )
    ),

    (
        "📉 Lowest NAV",
        round(
            scheme_nav[
                "nav"
            ].min(),
            2
        )
    )

]

for col, (title, value) in zip(
    [s1, s2, s3],
    stats
):

    with col:

        st.markdown(
            f"""
            <div style="
            background:white;
            border:1px solid #e5e7eb;
            border-radius:12px;
            padding:12px;
            ">

            <div style="
            font-size:11px;
            color:#6b7280;
            ">
            {title}
            </div>

            <div style="
            font-size:20px;
            font-weight:700;
            margin-top:5px;
            ">
            {value}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

# ==================================================
# NAV INSIGHT
# ==================================================

# ==================================================
# NAV INSIGHT
# ==================================================

latest_nav = round(scheme_nav["nav"].iloc[-1], 2)
highest_nav = round(scheme_nav["nav"].max(), 2)
lowest_nav = round(scheme_nav["nav"].min(), 2)

peak_pct = round(
    (latest_nav / highest_nav) * 100,
    1
)

st.markdown(
f"""
<div style="
background:#eff6ff;
border-left:4px solid #3b82f6;
border-radius:10px;
padding:14px;
margin-top:10px;
">

<div style="
font-size:15px;
font-weight:600;
color:#1e40af;
margin-bottom:8px;
">
📌 NAV Insight
</div>

<div style="
font-size:13px;
line-height:1.7;
color:#374151;
">

💰 Current NAV: <b>₹{latest_nav}</b>

📈 Highest NAV Recorded: <b>₹{highest_nav}</b>

📉 Lowest NAV Recorded: <b>₹{lowest_nav}</b>

The fund is currently trading at
<b style="color:#16a34a;">
{peak_pct}%
</b>
of its historical peak NAV.

</div>

</div>
""",
unsafe_allow_html=True
)

# ==================================================
# PART 4 : COMPARE MODE
# ==================================================

st.markdown("---")

st.markdown("""
<h2 style="
font-size:24px;
font-weight:700;
margin-top:20px;
margin-bottom:15px;
">
⚖️ Compare Mutual Funds
</h2>
""", unsafe_allow_html=True)

# ==================================================
# FUND SELECTION
# ==================================================

compare_funds = st.multiselect(
    "🔍 Select 2–3 Funds for Comparison",
    options=filtered["scheme_name"].sort_values().unique(),
    default=[selected_scheme],
    max_selections=3
)

if len(compare_funds) >= 2:

    compare_df = filtered[
        filtered["scheme_name"].isin(compare_funds)
    ].copy()

    # ==================================================
    # METRIC COMPARISON TABLE
    # ==================================================

    st.markdown("""
    <h3 style="
    font-size:18px;
    font-weight:600;
    margin-bottom:10px;
    ">
    📋 Fund Metrics Comparison
    </h3>
    """, unsafe_allow_html=True)

    comparison_table = compare_df[
    [
        "scheme_name",
        "category",

        "return_1y",
        "return_3y",

        "cagr_1y",
        "cagr_3y",
        "cagr_5y",

        "beta",

        "sharpe_ratio",
        "sortino_ratio",

        "max_drawdown",

        "composite_score"
    ]
].copy()

    comparison_table.columns = [

    "Fund",
    "Category",

    "1Y Return (%)",
    "3Y Return (%)",

    "1Y CAGR (%)",
    "3Y CAGR (%)",
    "5Y CAGR (%)",

    "Beta",

    "Sharpe",
    "Sortino",

    "Max Drawdown (%)",

    "Composite Score"
]

    st.dataframe(
        comparison_table.round(2),
        width="stretch",
        hide_index=True
    )

    # ==================================================
    # COMPOSITE SCORE BAR CHART
    # ==================================================

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <h3 style="
    font-size:18px;
    font-weight:600;
    margin-bottom:10px;
    ">
    🏆 Composite Score Comparison
    </h3>
    """, unsafe_allow_html=True)

    fig_score = px.bar(
        compare_df.sort_values(
            "composite_score",
            ascending=False
        ),
        x="scheme_name",
        y="composite_score",
        text="composite_score"
    )

    fig_score.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_score.update_layout(
        template="plotly_white",
        height=400,
        xaxis_title="Fund",
        yaxis_title="Composite Score",
        showlegend=False
    )

    st.plotly_chart(
        fig_score,
        width='stretch'
    )

    # ==================================================
    # NAV COMPARISON CHART
    # ==================================================

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <h3 style="
    font-size:18px;
    font-weight:600;
    margin-bottom:10px;
    ">
    📈 NAV Trend Comparison
    </h3>
    """, unsafe_allow_html=True)

    fig_nav_compare = go.Figure()

    for fund in compare_funds:

        fund_code = str(
            filtered[
                filtered["scheme_name"] == fund
            ]["scheme_code"].iloc[0]
        )

        fund_nav = nav[
            nav["scheme_code"].astype(str)
            == fund_code
        ].copy()

        fund_nav.sort_values(
            "date",
            inplace=True
        )

        if len(fund_nav) > 0:

            base_nav = (
                fund_nav["nav"]
                .iloc[0]
            )

            fund_nav["normalized_nav"] = (
                fund_nav["nav"]
                / base_nav
            ) * 100

            fig_nav_compare.add_trace(

                go.Scatter(
                    x=fund_nav["date"],
                    y=fund_nav["normalized_nav"],
                    mode="lines",
                    name=fund
                )
            )

    fig_nav_compare.update_layout(
        template="plotly_white",
        height=450,
        title="Normalized NAV Performance (Base = 100)",
        xaxis_title="Date",
        yaxis_title="Normalized NAV",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_nav_compare,
        width='stretch'
    )

    # ==================================================
    # WINNER CARD
    # ==================================================

    winner = compare_df.loc[
        compare_df["composite_score"].idxmax()
    ]

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
    f"""
    <div style="
    background:#f0fdf4;
    border-left:4px solid #22c55e;
    border-radius:12px;
    padding:16px;
    ">

    <div style="
    font-size:16px;
    font-weight:600;
    color:#15803d;
    ">
    🏆 Top Ranked Fund in Comparison
    </div>

    <div style="
    margin-top:8px;
    font-size:14px;
    color:#374151;
    ">
    <b>{winner['scheme_name']}</b>
    has the highest Composite Score of
    <b>{winner['composite_score']:.2f}</b>
    among the selected funds.
    </div>

    </div>
    """,
    unsafe_allow_html=True
    )

else:

    st.info(
        "Select at least 2 funds to enable comparison mode."
    )

# ==================================================
# PROFESSIONAL FOOTER
# ==================================================

st.markdown("---")

st.markdown("""
<div style="
background:#ffffff;
border:1px solid #e5e7eb;
border-radius:14px;
padding:14px 18px;
box-shadow:0 2px 8px rgba(0,0,0,0.04);
">

<div style="
display:flex;
flex-wrap:wrap;
gap:10px;
margin-bottom:10px;
">

<span style="
background:#eff6ff;
color:#1d4ed8;
padding:6px 12px;
border-radius:999px;
font-size:12px;
font-weight:600;
">
🏦 AMFI India
</span>

<span style="
background:#ecfeff;
color:#0f766e;
padding:6px 12px;
border-radius:999px;
font-size:12px;
font-weight:600;
">
📡 MFAPI
</span>

<span style="
background:#fef3c7;
color:#b45309;
padding:6px 12px;
border-radius:999px;
font-size:12px;
font-weight:600;
">
📈 Nifty 50 Data
</span>

</div>

<div style="
display:flex;
flex-wrap:wrap;
gap:10px;
margin-bottom:10px;
">

<span style="
background:#f0fdf4;
color:#15803d;
padding:6px 12px;
border-radius:999px;
font-size:12px;
font-weight:600;
">
Returns & CAGR
</span>

<span style="
background:#f5f3ff;
color:#6d28d9;
padding:6px 12px;
border-radius:999px;
font-size:12px;
font-weight:600;
">
Sharpe Ratio
</span>

<span style="
background:#fdf2f8;
color:#be185d;
padding:6px 12px;
border-radius:999px;
font-size:12px;
font-weight:600;
">
Sortino Ratio
</span>

<span style="
background:#fef2f2;
color:#dc2626;
padding:6px 12px;
border-radius:999px;
font-size:12px;
font-weight:600;
">
Max Drawdown
</span>

<span style="
background:#eef2ff;
color:#4338ca;
padding:6px 12px;
border-radius:999px;
font-size:12px;
font-weight:600;
">
Beta
</span>

</div>

<div style="
background:#f8fafc;
border:1px solid #e2e8f0;
border-radius:10px;
padding:10px;
font-size:12px;
color:#475569;
">

⚖️ <b>Composite Score:</b>
•
1Y Return (25%) •
3Y Return (20%) •
Sharpe Ratio (25%) •
Sortino Ratio (15%) •
Maximum Drawdown (15%)
<br>
📌 Rankings are calculated from raw NAV history and compared only within the same mutual fund category.

</div>

</div>
""", unsafe_allow_html=True)