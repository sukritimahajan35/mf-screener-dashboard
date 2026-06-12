import pandas as pd

print("Loading CSV...")

df = pd.read_csv(
    "data/nav_history_clean.csv"
)

df["date"] = pd.to_datetime(
    df["date"]
)

print("Converting to Parquet...")

df.to_parquet(
    "data/nav_history.parquet",
    index=False
)

print("Done")