import yfinance as yf

print(
    "Downloading Nifty 50..."
)

nifty = yf.download(
    "^NSEI",
    start="2015-01-01",
    progress=False
)

nifty.reset_index(
    inplace=True
)

nifty = nifty[
    [
        "Date",
        "Close"
    ]
]

nifty.columns = [
    "date",
    "close"
]

nifty.to_csv(
    "data/nifty50.csv",
    index=False
)

print(
    "Nifty saved"
)