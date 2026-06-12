import pandas as pd

metrics = pd.read_csv(
    "data/metrics_output.csv"
)

print("\nTop 20 by 1Y Return\n")

print(
    metrics[
        [
            "scheme_code",
            "return_1y",
            "return_3y",
            "cagr_1y",
            "cagr_3y"
        ]
    ]
    .sort_values(
        "return_1y",
        ascending=False
    )
    .head(20)
)

print("\nSummary Statistics\n")

print(
    metrics[
        [
            "return_1y",
            "return_3y",
            "volatility",
            "sharpe_ratio",
            "sortino_ratio",
            "max_drawdown"
        ]
    ]
    .describe()
)