# Finly — Personal Financial Planner

A modern, all-in-one financial planner built with Streamlit. Tracks your budget, net worth, and savings goals, with everything saved locally so your data persists between sessions.

## Features

- **Dashboard** — monthly cash flow, net worth trend, spending breakdown, and goal progress at a glance
- **Budget** — add income sources and categorized expenses (any frequency: weekly, monthly, yearly, one-time)
- **Net Worth** — log snapshots of assets and liabilities over time and see your net worth trend
- **Goals** — set savings targets with deadlines and update progress as you go
- **Settings** — switch currency, export your data, or reset it

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
4. It'll open at `http://localhost:8501` in your browser.

## Data storage

All your data is saved locally in `financial_data.json` in the same folder as the app — nothing is sent anywhere else. You can export a copy anytime from the Settings page, or reset everything if you want a clean start.

## Notes

- The sidebar always shows a quick snapshot of your monthly cash flow and net worth.
- Expense categories are preset (Housing, Food, Transportation, etc.) but you can add as many individual expenses under each as you like.
- Net worth snapshots are manual — add one whenever you want to log where things stand (e.g. monthly or quarterly).
