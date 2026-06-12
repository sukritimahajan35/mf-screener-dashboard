import pandas as pd
import numpy as np
from tqdm import tqdm

# ==================================================
# CONFIG
# ==================================================

RISK_FREE_RATE = 6.5
TRADING_DAYS = 252

# ==================================================
# LOAD DATA
# ==================================================

print("Loading schemes...")

schemes = pd.read_csv(
    "data/schemes_clean.csv"
)

print("Loading NAV history...")

nav = pd.read_parquet(
    "data/nav_history.parquet"
)

print("Loading Nifty50...")

nifty = pd.read_csv(
    "data/nifty50.csv"
)

schemes["scheme_code"] = (
    schemes["scheme_code"]
    .astype(str)
)

nav["scheme_code"] = (
    nav["scheme_code"]
    .astype(str)
)

# ==================================================
# DATE FORMATTING
# ==================================================

nav["date"] = pd.to_datetime(
    nav["date"]
)

nifty["date"] = pd.to_datetime(
    nifty["date"]
)

nav.sort_values(
    ["scheme_code", "date"],
    inplace=True
)

nifty.sort_values(
    "date",
    inplace=True
)

nifty["nifty_return"] = (
    nifty["close"]
    .pct_change()
)

nifty_returns = nifty[
    ["date", "nifty_return"]
]

# ==================================================
# HELPER FUNCTIONS
# ==================================================

def absolute_return(
    start_nav,
    end_nav
):

    if (
        pd.isna(start_nav)
        or pd.isna(end_nav)
        or start_nav <= 0
    ):
        return np.nan

    return (
        (end_nav / start_nav)
        - 1
    ) * 100


def cagr(
    start_nav,
    end_nav,
    years
):

    if (
        pd.isna(start_nav)
        or pd.isna(end_nav)
        or start_nav <= 0
        or years <= 0
    ):
        return np.nan

    return (
        (
            end_nav /
            start_nav
        )
        ** (1 / years)
        - 1
    ) * 100


# ==================================================
# DATE-BASED NAV LOOKUP
# ==================================================

def get_nav_by_date(
    df,
    years=0,
    months=0
):

    latest_date = (
        df["date"].max()
    )

    target_date = (
        latest_date
        -
        pd.DateOffset(
            years=years,
            months=months
        )
    )

    history = df[
        df["date"]
        <= target_date
    ]

    if len(history) == 0:
        return np.nan

    return history.iloc[-1]["nav"]


# ==================================================
# RISK & HORIZON FUNCTIONS
# ==================================================

def classify_risk(
    volatility
):

    if pd.isna(volatility):
        return "Unknown"

    if volatility < 0.08:
        return "Low"

    elif volatility < 0.18:
        return "Moderate"

    return "High"


def classify_horizon(
    years
):

    if years >= 5:
        return "Long Term"

    elif years >= 3:
        return "Medium Term"

    return "Short Term"


# ==================================================
# LOOKUP DICTIONARY
# ==================================================

category_lookup = dict(

    zip(

        schemes[
            "scheme_code"
        ],

        schemes[
            "category"
        ]
    )
)

# ==================================================
# MAIN PROCESSING LOOP
# ==================================================

results = []

grouped = nav.groupby(
    "scheme_code"
)

print(
    f"Processing {len(grouped):,} schemes..."
)

processed = 0

for scheme_code, df in tqdm(grouped):

    try:
        df = df.sort_values(
            "date"
        )
        # Skip incomplete NAV history
        if (
            "incomplete_nav_history" in df.columns
            and
            df["incomplete_nav_history"].any()
        ):
            continue

        if len(df) < 30:
            continue

        # ==========================================
        # CLEAN NAV SERIES
        # # Remove invalid NAV values
        # ==========================================
        nav_series = (
            df["nav"]
            .astype(float)
        )
        
        nav_series = nav_series[
            nav_series > 0
        ]
        if len(nav_series) < 30:
            continue
        
        latest_nav = (
            nav_series.iloc[-1]
        )

        # ==========================================
        # DATE-BASED NAV LOOKUPS
        # ==========================================

        nav_1m = get_nav_by_date(
            df,
            months=1
        )

        nav_3m = get_nav_by_date(
            df,
            months=3
        )

        nav_6m = get_nav_by_date(
            df,
            months=6
        )

        nav_1y = get_nav_by_date(
            df,
            years=1
        )

        nav_3y = get_nav_by_date(
            df,
            years=3
        )

        nav_5y = get_nav_by_date(
            df,
            years=5
        )

        # ==========================================
        # ABSOLUTE RETURNS
        # ==========================================

        r_1m = absolute_return(
            nav_1m,
            latest_nav
        )

        r_3m = absolute_return(
            nav_3m,
            latest_nav
        )

        r_6m = absolute_return(
            nav_6m,
            latest_nav
        )

        r_1y = absolute_return(
            nav_1y,
            latest_nav
        )

        r_3y = absolute_return(
            nav_3y,
            latest_nav
        )

        # ==========================================
        # FILTER BAD SCHEMES
        # ==========================================

        if (
            pd.notna(r_1y)
            and abs(r_1y) > 200
        ):
            continue

        if (
            pd.notna(r_3y)
            and abs(r_3y) > 300
        ):
            continue

        # ==========================================
        # CAGR
        # ==========================================

        cagr_1y = cagr(
            nav_1y,
            latest_nav,
            1
        )

        cagr_3y = cagr(
            nav_3y,
            latest_nav,
            3
        )

        cagr_5y = cagr(
            nav_5y,
            latest_nav,
            5
        )

        # ==========================================
        # DAILY RETURNS
        # ==========================================
        clean_df = df.copy()
        clean_df = clean_df[
            clean_df["nav"] > 0
        ]
        daily_returns = (
            clean_df
            .set_index("date")
            ["nav"]
            .astype(float)
            .pct_change()
            .replace(
                [np.inf, -np.inf],
                np.nan
            )
            .dropna()
        )


        if len(daily_returns) < 20:
            continue

        # ==========================================
        # VOLATILITY
        # ==========================================

        volatility = (

            daily_returns.std()

            * np.sqrt(
                TRADING_DAYS
            )
        )

        # ==========================================
        # ANNUAL RETURN
        # ==========================================

        annual_return = (

            (

                np.prod(
                    1 + daily_returns
                )

                **

                (
                    TRADING_DAYS
                    /
                    len(daily_returns)
                )

            )

            - 1

        ) * 100

        # ==========================================
        # SHARPE RATIO
        # ==========================================

        if volatility > 0.0001:
            sharpe_ratio = (
                annual_return - RISK_FREE_RATE
            ) / (
                volatility * 100
            )
        else:
            sharpe_ratio = np.nan

        # ==========================================
        # SORTINO RATIO
        # ==========================================

        downside = (

            daily_returns[
                daily_returns < 0
            ]
        )

        downside_std = (

            downside.std()

            * np.sqrt(
                TRADING_DAYS
            )
        )

        if downside_std > 0.0001:
            sortino_ratio = (
                annual_return - RISK_FREE_RATE
            ) / (
                downside_std * 100
            )
        else:
            sortino_ratio = np.nan

        # ==========================================
        # MAXIMUM DRAWDOWN
        # ==========================================

        rolling_max = (
            nav_series.cummax()
        )

        drawdown = (
            nav_series
            /
            rolling_max
        ) - 1

        max_drawdown = (
            drawdown.min()
            * 100
        )

        # ==========================================
        # BETA
        # ==========================================

        beta = np.nan
        category = category_lookup.get(
            str(scheme_code), "Other")
        
        if "equity" in str(category).lower():
            scheme_returns = (
                daily_returns
                .reset_index()
            )
            
            scheme_returns.columns = [
                "date",
                "scheme_return"]
            
            merged = (
                scheme_returns
                .merge(
                    nifty_returns,
                    on="date",
                    how="inner")
            )
            
            if len(merged) > 50:
                market_var = (
                    merged[
                        "nifty_return"].var())
                if (pd.notna(market_var) and market_var > 0):
                    beta = (
                        merged[
                            "scheme_return"].cov(
                                merged[
                                    "nifty_return"])/market_var)

        # ==========================================
        # HORIZON
        # ==========================================

        years_available = (

            (
                df["date"].max()
                -
                df["date"].min()
            ).days

            / 365.25
        )

        # ==========================================
        # STORE RESULTS
        # ==========================================

        results.append({

            "scheme_code":
            scheme_code,

            "return_1m":
            r_1m,

            "return_3m":
            r_3m,

            "return_6m":
            r_6m,

            "return_1y":
            r_1y,

            "return_3y":
            r_3y,

            "cagr_1y":
            cagr_1y,

            "cagr_3y":
            cagr_3y,

            "cagr_5y":
            cagr_5y,

            "volatility":
            volatility,

            "sharpe_ratio":
            sharpe_ratio,

            "sortino_ratio":
            sortino_ratio,

            "max_drawdown":
            max_drawdown,

            "beta":
            beta,

            "risk_level":
            classify_risk(
                volatility
            ),

            "horizon":
            classify_horizon(
                years_available
            )
        })

        processed += 1

        if processed % 1000 == 0:

            checkpoint = pd.DataFrame(
                results
            )

            checkpoint.to_csv(
                "data/metrics_checkpoint.csv",
                index=False
            )

            tqdm.write(
                f"Checkpoint saved: {processed:,} schemes"
            )

    except Exception:
        continue

# ==================================================
# SAVE OUTPUT
# ==================================================

metrics = pd.DataFrame(
    results
)

# ==================================================
# FILL MISSING BETAS USING CATEGORY AVERAGE
# ==================================================

metrics["scheme_code"] = (
    metrics["scheme_code"]
    .astype(str)
)

schemes["scheme_code"] = (
    schemes["scheme_code"]
    .astype(str)
)

metrics = metrics.merge(

    schemes[
        [
            "scheme_code",
            "category"
        ]
    ],

    on="scheme_code",

    how="left"
)

category_beta = (

    metrics

    .groupby(
        "category"
    )["beta"]

    .mean()
)

for category, avg_beta in category_beta.items():

    if pd.notna(avg_beta):

        metrics.loc[

            (
                metrics["category"]
                ==
                category
            )

            &

            (
                metrics["beta"]
                .isna()
            ),

            "beta"

        ] = avg_beta

# ==================================================
# DEFAULT BETAS
# ==================================================

metrics.loc[

    (
        metrics["beta"]
        .isna()
    )

    &

    (
        metrics["category"]
        .str.contains(
            "equity",
            case=False,
            na=False
        )
    ),

    "beta"

] = 1.0

metrics.loc[

    (
        metrics["beta"]
        .isna()
    )

    &

    (
        metrics["category"]
        .str.contains(
            "hybrid",
            case=False,
            na=False
        )
    ),

    "beta"

] = 0.7

# ==========================================
# FILL REMAINING BETA VALUES
# USING RISK PROFILE
# ==========================================

risk_beta_map = {

    "Low": 0.30,

    "Moderate": 0.70,

    "High": 1.00
}

metrics.loc[
    metrics["beta"].isna(),
    "beta"
] = metrics.loc[
    metrics["beta"].isna(),
    "risk_level"
].map(
    risk_beta_map
)

# Final safety fill

metrics["beta"] = metrics[
    "beta"
].fillna(
    metrics["beta"].median()
)

metrics.drop(
    columns=["category"],
    inplace=True
)

metrics.to_csv(
    "data/metrics_output.csv",
    index=False
)

print(
    "\nMetrics saved successfully."
)

print(
    f"Total schemes processed: {len(metrics):,}"
)
metrics = pd.DataFrame(
    results
)
