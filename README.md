# 📈 Real-Time Mutual Fund Screener Dashboard

## Overview

The Real-Time Mutual Fund Screener is an interactive Streamlit dashboard built to help Mutual Fund Distributors identify the best-performing mutual fund schemes using a transparent, risk-adjusted scoring framework.

The application computes all performance and risk metrics directly from raw NAV history and ranks schemes only within their respective categories.

The dashboard provides:

- Market Context Overview
- Fund Screening & Ranking
- Composite Score Breakdown
- NAV Trend Analysis
- Live NAV Tracking
- Fund Comparison Mode

---

## Project Structure

```text
mf_screener/
│
├── compute_metrics.py
├── score_schemes.py
├── dashboard.py
├── convert_parquet.py
├── download_nifty.py
├── validate_metrics.py
├── requirements.txt
│
├── data/
│   ├── schemes_clean.csv
│   ├── nav_history_clean.csv
│   ├── nav_history.parquet
│   ├── nifty50.csv
│   ├── market_context.csv
│   ├── metrics_output.csv
│   ├── metrics_checkpoint.csv
│   └── scored_schemes.csv
│
└── README.md
```

---

# Objective

Build an interactive dashboard that helps mutual fund distributors:

- Identify top-performing schemes
- Understand ranking logic
- Compare funds objectively
- Analyze risk-adjusted performance
- Monitor NAV trends
- Access live NAV data

---

# Data Sources

## 1. NAV History

Source:
AMFI Historical NAV Data

Used For:

- Returns
- CAGR
- Volatility
- Sharpe Ratio
- Sortino Ratio
- Drawdown

---

## 2. Nifty 50 Historical Data

File:

```text
data/nifty50.csv
```

Used For:

- Beta Calculation
- Market Benchmarking

---

## 3. Live NAV API

```text
https://api.mfapi.in/mf/{scheme_code}
```

Used For:

- Latest NAV
- Latest NAV Date

---

## 4. Market Context Data

File:

```text
data/market_context.csv
```

Contains:

- Nifty 50 1Y Return
- Midcap 150 1Y Return
- Smallcap 250 1Y Return
- Repo Rate
- CPI Inflation
- Industry AUM

---

# Metric Definitions

## Absolute Returns

Calculated For:

- 1 Month
- 3 Months
- 6 Months
- 1 Year
- 3 Years

Formula:

```text
Return (%) =
((Ending NAV - Starting NAV) / Starting NAV) × 100
```

---

## CAGR

Calculated For:

- 1 Year
- 3 Years
- 5 Years

Formula:

```text
CAGR =
((Ending NAV / Starting NAV) ^ (1 / Years) - 1) × 100
```

---

## Annualized Volatility

Measures variation in daily returns.

Formula:

```text
Volatility =
Daily Return Standard Deviation × √252
```

---

## Sharpe Ratio

Measures return earned per unit of risk.

Risk-Free Rate Used:

```text
6.5%
```

Formula:

```text
Sharpe Ratio =
(Annual Return − Risk Free Rate)
/
Annualized Volatility
```

---

## Sortino Ratio

Measures return earned per unit of downside risk.

Formula:

```text
Sortino Ratio =
(Annual Return − Risk Free Rate)
/
Downside Volatility
```

---

## Maximum Drawdown

Measures largest historical decline from peak NAV.

Formula:

```text
Drawdown =
(NAV / Rolling Peak NAV) − 1
```

Lower drawdown indicates better capital preservation.

---

## Beta

Measures sensitivity to Nifty 50.

Interpretation:

| Beta | Meaning |
|--------|----------|
| < 1 | Less Volatile Than Market |
| = 1 | Similar To Market |
| > 1 | More Volatile Than Market |

Calculated for equity-oriented schemes.

---

# Risk Classification

| Volatility | Risk Level |
|------------|------------|
| < 8% | Low |
| 8% – 18% | Moderate |
| > 18% | High |

---

# Investment Horizon Classification

| History Available | Horizon |
|------------------|----------|
| < 3 Years | Short Term |
| 3 – 5 Years | Medium Term |
| > 5 Years | Long Term |

---

# Composite Scoring Methodology

All schemes are ranked only within their own category.

Examples:

- Large Cap vs Large Cap
- Mid Cap vs Mid Cap
- Debt vs Debt
- Hybrid vs Hybrid

Cross-category ranking is never performed.

---

## Score Weights

| Metric | Weight |
|----------|----------|
| 1Y Return | 25% |
| 3Y Return | 20% |
| Sharpe Ratio | 25% |
| Sortino Ratio | 15% |
| Maximum Drawdown | 15% |

---

## Normalization

Every metric is normalized to a:

```text
0 – 100 Scale
```

Where:

```text
100 = Best Scheme In Category

0 = Worst Scheme In Category
```

For Drawdown:

```text
Lower Drawdown = Higher Score
```

Hence:

```python
drawdown_score =
100 - normalized_drawdown
```

---

## Composite Score Formula

```text
Composite Score =

(25% × 1Y Return Score)

+ (20% × 3Y Return Score)

+ (25% × Sharpe Score)

+ (15% × Sortino Score)

+ (15% × Drawdown Score)
```

Final Score Range:

```text
0 – 100
```

Higher score indicates stronger risk-adjusted performance.

---

# Dashboard Features

## 1. Market Context Bar

Always Visible

Displays:

- Nifty 50 Return
- Midcap 150 Return
- Smallcap 250 Return
- Repo Rate
- CPI Inflation
- Industry AUM

---

## 2. Screener Panel

Filters:

- Category
- AMC
- Plan Type
- Risk Level
- Horizon

Features:

- Real-Time Filtering
- Sortable Fund Table
- Composite Score Ranking
- Top 3 Schemes Per Category Badged

---

## 3. Score Breakdown

Displays:

- Composite Score
- Category Rank
- Radar Chart
- Metric Rankings
- Beta Interpretation
- Strengths & Weaknesses Summary

---

## 4. NAV Trend Analysis

Displays:

- Historical NAV Trend
- Category Average Comparison
- Rolling 3-Month Return
- Live NAV
- NAV Statistics
- NAV Insights

---

## 5. Compare Mode

Compare 2–3 Mutual Funds

Includes:

- Metrics Comparison Table
- Composite Score Chart
- NAV Comparison Chart
- Top Ranked Fund Identification

---

# Installation

Clone Repository

```bash
git clone https://github.com/your-username/mf_screener.git
```

Move Into Project Folder

```bash
cd mf_screener
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run Dashboard

```bash
streamlit run dashboard.py
```

---

# Requirements

Main Libraries:

```text
streamlit
pandas
numpy
plotly
requests
pyarrow
tqdm
```

---

# Deployment

Deployed on:

Streamlit Community Cloud

Deployment Steps:

1. Push project to GitHub
2. Open https://share.streamlit.io
3. Connect GitHub Repository
4. Select:

```text
dashboard.py
```

5. Deploy

---

# Acceptance Criteria Coverage

✅ Metrics computed from raw NAV history

✅ Live NAV polling using MFAPI

✅ Category-wise ranking

✅ Composite scoring engine

✅ Real-time filtering

✅ Top 3 schemes per category badged

✅ Score breakdown visualization

✅ NAV trend analysis

✅ Rolling 3M return chart

✅ Compare mode for 2–3 schemes

✅ Streamlit Cloud deployment ready

✅ GitHub repository documentation

---

# Built With

- Python
- Pandas
- NumPy
- Plotly
- Streamlit
- Requests
- MFAPI

---

## Author

Sukriti Mahajan

Real-Time Mutual Fund Screener Dashboard
(Task 2)
