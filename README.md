# Finly — Personal Financial Planner

A modern, professional, mobile-friendly financial planner built with Streamlit: budget, net worth, savings goals, debt payoff, and a set of financial calculators — all saved locally.

## Features

- **Dashboard** — income/expense/cash-flow KPIs, net worth trend, spending breakdown, income-vs-expenses trend over time, budget-health alerts, and goal progress at a glance
- **Budget** — income sources and categorized expenses (any frequency), **per-category budget limits** with on-track / near-limit / over-budget status, and one-click monthly history logging
- **Net Worth** — log snapshots of assets and liabilities over time, see your net worth trend and an asset allocation breakdown
- **Goals** — set savings targets with deadlines and update progress as you go
- **Calculators** —
  - Loan / EMI calculator with a full amortization schedule
  - SIP & lump-sum investment growth projector
  - Retirement corpus planner (accounts for inflation and pre/post-retirement returns)
  - Goal-based required-SIP calculator
  - **Debt payoff planner** — compares avalanche (highest interest first) vs. snowball (smallest balance first) strategies, with months-to-debt-free, total interest, and a balance-over-time chart
- **Settings** — switch currency (Rs., $, €, £, ¥), export data as CSV (per section) or a full JSON backup, or reset everything

## Design notes

The app uses a light theme with a dark navy sidebar. This isn't just a style choice — Streamlit's native dropdowns, date pickers, and menus render in an overlay that custom CSS can't always reach, so a light theme base is what guarantees those components keep correct, readable contrast (rather than fighting it with overrides). Every text/background color pairing in the custom styling has been checked against WCAG AA contrast requirements (4.5:1 minimum) so values and labels stay legible on a phone screen, not just on a calibrated desktop monitor.

## Setup

1. Make sure you have Python 3.9+ installed.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   streamlit run app.py
   ```
4. It'll open at `http://localhost:8501` in your browser. On mobile, the sidebar opens as a drawer — tap the `«` at the top to collapse it once you've picked a page.

## Data storage

All data is saved locally in `financial_data.json` next to the app — nothing is sent anywhere else. Export a CSV or full JSON backup anytime from Settings, or reset everything for a clean start.

## Notes on the calculators

The Loan/EMI, SIP, retirement, goal, and debt-payoff calculators use standard financial formulas (not personalized investment advice). Actual loan terms and investment returns will vary — treat the outputs as planning estimates.

## Project structure

- `app.py` — UI, navigation, styling, and page layout
- `data_manager.py` — local JSON persistence and derived calculations (totals, category spend, monthly history, CSV export)
- `calculators.py` — standalone financial formulas (EMI, SIP/lump-sum growth, retirement corpus, goal SIP, debt payoff)
- `.streamlit/config.toml` — light, professional theme with accessible contrast
