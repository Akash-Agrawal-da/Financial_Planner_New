"""
Data persistence layer for the financial planner.
Everything is stored in a single local JSON file so the app remembers
your data between sessions, with no external database required.
"""

import json
import os
import io
import csv
import copy
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "financial_data.json")

DEFAULT_DATA = {
    "income": [],                # [{id, name, amount, frequency}]
    "expenses": [],              # [{id, category, name, amount, frequency}]
    "budget_limits": {},          # {category: monthly_limit}
    "net_worth_snapshots": [],    # [{id, date, assets, liabilities, totals}]
    "goals": [],                  # [{id, name, target_amount, current_amount, target_date, category}]
    "monthly_history": [],        # [{id, month, income, expenses, net}]
    "debts": [],                   # [{id, name, balance, interest_rate, min_payment}]
    "settings": {
        "currency": "Rs.",
    },
}

EXPENSE_CATEGORIES = [
    "Housing", "Food", "Transportation", "Utilities", "Insurance",
    "Healthcare", "Entertainment", "Subscriptions", "Debt payments",
    "Savings & investments", "Education", "Other",
]

FREQUENCY_TO_MONTHLY = {
    "Monthly": 1,
    "Weekly": 52 / 12,
    "Bi-weekly": 26 / 12,
    "Yearly": 1 / 12,
    "One-time": 0,
}


def _new_id(items):
    if not items:
        return 1
    return max(item.get("id", 0) for item in items) + 1


def fresh_data():
    """A brand-new, fully independent copy of the default data shape.
    Always use this (never DEFAULT_DATA directly) so that appending to one
    session's lists can never leak into another session or into the
    module-level defaults themselves."""
    return copy.deepcopy(DEFAULT_DATA)


def ensure_schema(data):
    """Self-heal a data dict that may be missing keys added by a later
    version of the app (e.g. a browser session kept alive across a
    redeploy that added new fields). Mutates and returns `data`."""
    changed = False
    for key, default_value in DEFAULT_DATA.items():
        if key not in data:
            data[key] = copy.deepcopy(default_value)
            changed = True
    return data, changed


def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(fresh_data())
        return fresh_data()

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        data, changed = ensure_schema(data)
        if changed:
            save_data(data)
        return data
    except (json.JSONDecodeError, OSError):
        if os.path.exists(DATA_FILE):
            backup_name = DATA_FILE + f".backup-{int(datetime.now().timestamp())}"
            os.rename(DATA_FILE, backup_name)
        save_data(fresh_data())
        return fresh_data()


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ---------- Income ----------

def add_income(data, name, amount, frequency):
    data["income"].append({
        "id": _new_id(data["income"]), "name": name, "amount": amount, "frequency": frequency,
    })
    save_data(data)


def delete_income(data, item_id):
    data["income"] = [i for i in data["income"] if i["id"] != item_id]
    save_data(data)


# ---------- Expenses ----------

def add_expense(data, category, name, amount, frequency):
    data["expenses"].append({
        "id": _new_id(data["expenses"]), "category": category, "name": name,
        "amount": amount, "frequency": frequency,
    })
    save_data(data)


def delete_expense(data, item_id):
    data["expenses"] = [e for e in data["expenses"] if e["id"] != item_id]
    save_data(data)


# ---------- Budget limits ----------

def set_budget_limit(data, category, limit):
    if limit and limit > 0:
        data["budget_limits"][category] = limit
    elif category in data["budget_limits"]:
        del data["budget_limits"][category]
    save_data(data)


def spending_by_category(data):
    """Return {category: monthly_spend} for every category that has expenses."""
    totals = {}
    for e in data["expenses"]:
        totals[e["category"]] = totals.get(e["category"], 0) + monthly_amount(e["amount"], e["frequency"])
    return totals


# ---------- Net worth ----------

def add_net_worth_snapshot(data, snapshot_date, assets, liabilities):
    total_assets = sum(assets.values())
    total_liabilities = sum(liabilities.values())
    data["net_worth_snapshots"].append({
        "id": _new_id(data["net_worth_snapshots"]),
        "date": str(snapshot_date),
        "assets": assets,
        "liabilities": liabilities,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "net_worth": total_assets - total_liabilities,
    })
    data["net_worth_snapshots"].sort(key=lambda s: s["date"])
    save_data(data)


def delete_net_worth_snapshot(data, item_id):
    data["net_worth_snapshots"] = [s for s in data["net_worth_snapshots"] if s["id"] != item_id]
    save_data(data)


# ---------- Goals ----------

def add_goal(data, name, target_amount, current_amount, target_date, category):
    data["goals"].append({
        "id": _new_id(data["goals"]), "name": name, "target_amount": target_amount,
        "current_amount": current_amount, "target_date": str(target_date), "category": category,
    })
    save_data(data)


def update_goal_progress(data, goal_id, new_current_amount):
    for g in data["goals"]:
        if g["id"] == goal_id:
            g["current_amount"] = new_current_amount
    save_data(data)


def delete_goal(data, goal_id):
    data["goals"] = [g for g in data["goals"] if g["id"] != goal_id]
    save_data(data)


# ---------- Monthly history ----------

def record_monthly_snapshot(data, month_str, income, expenses):
    """Upsert the income/expense totals for a given month (YYYY-MM)."""
    existing = next((m for m in data["monthly_history"] if m["month"] == month_str), None)
    if existing:
        existing["income"] = income
        existing["expenses"] = expenses
        existing["net"] = income - expenses
    else:
        data["monthly_history"].append({
            "id": _new_id(data["monthly_history"]),
            "month": month_str,
            "income": income,
            "expenses": expenses,
            "net": income - expenses,
        })
    data["monthly_history"].sort(key=lambda m: m["month"])
    save_data(data)


def delete_monthly_snapshot(data, item_id):
    data["monthly_history"] = [m for m in data["monthly_history"] if m["id"] != item_id]
    save_data(data)


# ---------- Debts ----------

def add_debt(data, name, balance, interest_rate, min_payment):
    data["debts"].append({
        "id": _new_id(data["debts"]), "name": name, "balance": balance,
        "interest_rate": interest_rate, "min_payment": min_payment,
    })
    save_data(data)


def delete_debt(data, item_id):
    data["debts"] = [d for d in data["debts"] if d["id"] != item_id]
    save_data(data)


# ---------- Derived helpers ----------

def monthly_amount(amount, frequency):
    return amount * FREQUENCY_TO_MONTHLY.get(frequency, 1)


def total_monthly_income(data):
    return sum(monthly_amount(i["amount"], i["frequency"]) for i in data["income"])


def total_monthly_expenses(data):
    return sum(monthly_amount(e["amount"], e["frequency"]) for e in data["expenses"])


def latest_net_worth(data):
    if not data["net_worth_snapshots"]:
        return None
    return data["net_worth_snapshots"][-1]


# ---------- Export ----------

def to_csv(rows, fieldnames):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return buf.getvalue()


def export_income_csv(data):
    return to_csv(data["income"], ["id", "name", "amount", "frequency"])


def export_expenses_csv(data):
    return to_csv(data["expenses"], ["id", "category", "name", "amount", "frequency"])


def export_net_worth_csv(data):
    return to_csv(data["net_worth_snapshots"], ["id", "date", "total_assets", "total_liabilities", "net_worth"])


def export_goals_csv(data):
    return to_csv(data["goals"], ["id", "name", "category", "target_amount", "current_amount", "target_date"])


def export_monthly_history_csv(data):
    return to_csv(data["monthly_history"], ["id", "month", "income", "expenses", "net"])


def export_debts_csv(data):
    return to_csv(data["debts"], ["id", "name", "balance", "interest_rate", "min_payment"])