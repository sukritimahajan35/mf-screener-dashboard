import pandas as pd
import numpy as np

# ==================================================
# TASK 2
# SCORE SCHEMES
#
# Composite Score (0-100)
#
# Weight Rationale
#
# 1Y Return     = 25%
# Recent performance
#
# 3Y Return     = 20%
# Consistency
#
# Sharpe Ratio  = 25%
# Risk-adjusted return
#
# Sortino Ratio = 15%
# Downside risk protection
#
# Max Drawdown  = 15%
# Capital preservation
#
# Schemes ranked ONLY
# within their category.
# ==================================================

print("Loading files...")

metrics = pd.read_csv(
    "data/metrics_output.csv"
)

schemes = pd.read_csv(
    "data/schemes_clean.csv"
)

# ==================================================
# FORMAT
# ==================================================

metrics["scheme_code"] = (
    metrics["scheme_code"]
    .astype(str)
)

schemes["scheme_code"] = (
    schemes["scheme_code"]
    .astype(str)
)

# ==================================================
# MERGE
# ==================================================

df = metrics.merge(

    schemes[
        [
            "scheme_code",
            "scheme_name",
            "amc",
            "category",
            "plan_type"
        ]
    ],

    on="scheme_code",

    how="left"
)

print(
    f"Records merged: {len(df):,}"
)

# ==================================================
# NORMALIZATION
# ==================================================

def normalize(series):

    valid = series.dropna()

    if len(valid) == 0:

        return pd.Series(
            50,
            index=series.index
        )

    if valid.max() == valid.min():

        return pd.Series(
            50,
            index=series.index
        )

    return (

        (
            series
            -
            valid.min()
        )

        /

        (
            valid.max()
            -
            valid.min()
        )

    ) * 100

# ==================================================
# CATEGORY SCORING
# ==================================================

scored_categories = []

categories = (

    df["category"]

    .dropna()

    .unique()
)

print(
    f"Scoring {len(categories)} categories..."
)

for category in categories:

    temp = df[
        df["category"]
        ==
        category
    ].copy()

    if len(temp) == 0:
        continue

    # ==========================================
    # NORMALIZED SCORES
    # ==========================================

    temp[
        "return_1y_score"
    ] = normalize(
        temp["return_1y"]
    )

    temp[
        "return_3y_score"
    ] = normalize(
        temp["return_3y"]
    )

    temp[
        "sharpe_score"
    ] = normalize(
        temp["sharpe_ratio"]
    )

    temp[
        "sortino_score"
    ] = normalize(
        temp["sortino_ratio"]
    )

    # Lower drawdown is better

    temp[
    "drawdown_score"
    ] = (
        100
        -
        normalize(
            temp[
                "max_drawdown"
            ]
        )
    )
    # ==========================================
    # METRIC RANKS
    # ==========================================

    temp["return_1y_rank"] = (
        temp["return_1y"].rank(
            ascending=False,
            method="dense"
        )
        )
    
    temp["return_3y_rank"] = (
        temp["return_3y"].rank(
            ascending=False,
            method="dense"))
    
    temp["sharpe_rank"] = (
        temp["sharpe_ratio"].rank(
            ascending=False,
            method="dense"
            ))
    
    temp["sortino_rank"] = (
        temp["sortino_ratio"].rank(
            ascending=False,
            method="dense"
            ))
    temp["drawdown_rank"] = (
        temp["max_drawdown"].rank(
            ascending=False,
            method="dense"
            ))


    # ==========================================
    # FILL MISSING SCORES
    # ==========================================

    score_cols = [

        "return_1y_score",
        "return_3y_score",
        "sharpe_score",
        "sortino_score",
        "drawdown_score"
    ]

    for col in score_cols:

        median_value = (
        temp[col]
        .median()
        )
        if pd.isna(
        median_value
        ):
            median_value = 50
        temp[col] = temp[col].fillna(
            median_value
        )

    # ==========================================
    # COMPOSITE SCORE
    # ==========================================

    temp[
        "composite_score"
    ] = (

        (
            0.25
            *
            temp[
                "return_1y_score"
            ]
        )

        +

        (
            0.20
            *
            temp[
                "return_3y_score"
            ]
        )

        +

        (
            0.25
            *
            temp[
                "sharpe_score"
            ]
        )

        +

        (
            0.15
            *
            temp[
                "sortino_score"
            ]
        )

        +

        (
            0.15
            *
            temp[
                "drawdown_score"
            ]
        )

    )

    # ==========================================
    # CATEGORY RANK
    # ==========================================

    temp[
        "category_rank"
    ] = (

        temp[
            "composite_score"
        ]

        .rank(
            ascending=False,
            method="dense"
        )

        .astype(int)
    )

    # ==========================================
    # BADGES
    # ==========================================

    def badge(rank):

        if rank == 1:
            return "🥇"

        elif rank == 2:
            return "🥈"

        elif rank == 3:
            return "🥉"

        return ""

    temp[
        "badge"
    ] = temp[
        "category_rank"
    ].apply(
        badge
    )

    scored_categories.append(
        temp
    )

# ==================================================
# FINAL OUTPUT
# ==================================================

if len(scored_categories) == 0:

    raise ValueError(
        "No categories scored."
    )

scored = pd.concat(
    scored_categories,
    ignore_index=True
)

# ==================================================
# SORT
# ==================================================
scored[
    "composite_score"
] = (

    scored[
        "composite_score"
    ]

    .clip(
        0,
        100
    )
)

scored.sort_values(

    by=[
        "category",
        "category_rank"
    ],

    inplace=True
)

# ==================================================
# ROUNDING
# ==================================================

numeric_cols = scored.select_dtypes(
    include=np.number
).columns

scored[
    numeric_cols
] = scored[
    numeric_cols
].round(4)

# ==================================================
# SAVE
# ==================================================

scored.to_csv(

    "data/scored_schemes.csv",

    index=False
)

print("\nScoring Complete")

print(
    f"Schemes Scored: {len(scored):,}"
)

print(
    "\nSaved:"
)

print(
    "data/scored_schemes.csv"
)

print(
    "\nOutput columns:"
)

print(
    scored.columns.tolist()
)