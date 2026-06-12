# 📈 Real-Time Mutual Fund Screener Dashboard

## Overview

This project is an interactive Streamlit dashboard that ranks mutual fund schemes using performance and risk metrics computed directly from historical NAV data. The dashboard enables users to filter schemes, analyze rankings, compare funds, and understand the logic behind each score.

---

# Setup

## Clone Repository

```bash
git clone <repository-url>
cd mf_screener
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Dashboard

```bash
streamlit run dashboard.py
```

---

# Data Sources

### Mutual Fund NAV Data

* AMFI India
* MFAPI

### Market Benchmark Data

* Nifty 50 Historical Data

### Market Context Indicators

* Repo Rate
* CPI Inflation
* Industry AUM

All performance and risk metrics are derived from raw NAV history. No third-party rating or ranking services are used.

---

# Metric Definitions

## Return Metrics

### 1M Return

Percentage change in NAV over the last 1 month.

### 3M Return

Percentage change in NAV over the last 3 months.

### 6M Return

Percentage change in NAV over the last 6 months.

### 1Y Return

Percentage change in NAV over the last 1 year.

### 3Y Return

Percentage change in NAV over the last 3 years.

---

## CAGR Metrics

### 1Y CAGR

Annualized growth rate over 1 year.

### 3Y CAGR

Annualized growth rate over 3 years.

### 5Y CAGR

Annualized growth rate over 5 years where sufficient history is available.

---

## Risk Metrics

### Annualized Standard Deviation

Measures volatility of fund returns.

### Sharpe Ratio

Measures excess return earned per unit of total risk.

Risk-Free Rate Used:

```text
6.5%
```

### Sortino Ratio

Measures excess return earned per unit of downside risk.

### Maximum Drawdown

Largest historical decline from peak NAV to trough NAV.

Lower drawdown indicates better capital preservation.

### Beta

Measures sensitivity of a fund relative to Nifty 50.

* Beta > 1 : More volatile than market
* Beta < 1 : Less volatile than market
* Beta = 1 : Similar market movement

---

# Scoring Logic

Funds are ranked only against schemes within the same category.

Cross-category comparisons are not performed.

Each metric is normalized to a 0–100 scale before scoring.

## Composite Score Formula

| Metric           | Weight |
| ---------------- | ------ |
| 1Y Return        | 25%    |
| 3Y Return        | 20%    |
| Sharpe Ratio     | 25%    |
| Sortino Ratio    | 15%    |
| Maximum Drawdown | 15%    |

### Weight Rationale

* 1Y Return rewards recent performance.
* 3Y Return rewards consistency.
* Sharpe Ratio measures risk-adjusted return.
* Sortino Ratio evaluates downside risk management.
* Maximum Drawdown rewards capital preservation.

### Final Score

```text
Composite Score =
0.25 × Return Score
+ 0.20 × 3Y Return Score
+ 0.25 × Sharpe Score
+ 0.15 × Sortino Score
+ 0.15 × Drawdown Score
```

The final score ranges from 0 to 100.

Higher scores indicate stronger overall performance after considering both returns and risk.

---

# Dashboard Features

### Market Context

Displays:

* Nifty 50 (1Y Return)
* Midcap 150 (1Y Return)
* Smallcap 250 (1Y Return)
* Repo Rate
* CPI Inflation
* Industry AUM

### Fund Screener

* Category Filter
* AMC Filter
* Plan Type Filter
* Risk Filter
* Horizon Filter
* Top 3 Funds per Category Badged

### Score Breakdown

* Radar Chart
* Metric Rankings
* Strength & Weakness Analysis
* Category Rank Explanation

### NAV Trend Analysis

* Historical NAV Trend
* Category Average Comparison
* Rolling 3-Month Return
* Live NAV Tracking

### Compare Mode

* Compare 2–3 Funds
* Metrics Comparison Table
* Composite Score Comparison
* NAV Trend Comparison

---

# Technology Stack

* Python
* Pandas
* NumPy
* Streamlit
* Plotly
* Requests
