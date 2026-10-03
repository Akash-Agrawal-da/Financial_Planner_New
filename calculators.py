"""
Standard financial calculator formulas: loan/EMI, compound growth (SIP/lump
sum), retirement corpus, and goal-based required savings. These are generic
textbook formulas, not personalized investment advice.
"""


def emi_schedule(principal, annual_rate_pct, tenure_months):
    """Equated Monthly Installment loan calculator with full amortization schedule."""
    monthly_rate = annual_rate_pct / 12 / 100
    if tenure_months <= 0:
        return {"emi": 0, "total_payment": 0, "total_interest": 0, "schedule": []}

    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months / \
              ((1 + monthly_rate) ** tenure_months - 1)

    schedule = []
    balance = principal
    for month in range(1, tenure_months + 1):
        interest_payment = balance * monthly_rate
        principal_payment = emi - interest_payment
        balance = max(balance - principal_payment, 0)
        schedule.append({
            "month": month,
            "emi": emi,
            "principal": principal_payment,
            "interest": interest_payment,
            "balance": balance,
        })

    total_payment = emi * tenure_months
    return {
        "emi": emi,
        "total_payment": total_payment,
        "total_interest": total_payment - principal,
        "schedule": schedule,
    }


def sip_future_value(monthly_investment, annual_rate_pct, years):
    """Future value of a recurring monthly investment (SIP-style), with a
    year-by-year breakdown of invested amount vs. portfolio value."""
    monthly_rate = annual_rate_pct / 12 / 100
    months = int(years * 12)

    yearly = []
    balance = 0.0
    for m in range(1, months + 1):
        # Investment made at the start of each month (standard SIP convention),
        # so it compounds for the full month.
        balance = (balance + monthly_investment) * (1 + monthly_rate)
        if m % 12 == 0:
            yearly.append({
                "year": m // 12,
                "invested": monthly_investment * m,
                "value": balance,
            })

    invested = monthly_investment * months
    gains = balance - invested
    return {"future_value": balance, "invested": invested, "gains": gains, "yearly": yearly}


def lumpsum_future_value(principal, annual_rate_pct, years, compounds_per_year=1):
    """Future value of a one-time lump sum investment under compound interest."""
    rate = annual_rate_pct / 100
    return principal * (1 + rate / compounds_per_year) ** (compounds_per_year * years)


def retirement_corpus(current_age, retirement_age, monthly_expense_today,
                       inflation_pct, expected_return_pre_pct, expected_return_post_pct,
                       life_expectancy):
    """Estimate the retirement corpus needed, and the monthly SIP required
    today to reach it by the target retirement age."""
    years_to_retirement = max(retirement_age - current_age, 0)
    years_in_retirement = max(life_expectancy - retirement_age, 1)

    monthly_expense_at_retirement = monthly_expense_today * (1 + inflation_pct / 100) ** years_to_retirement
    annual_expense_at_retirement = monthly_expense_at_retirement * 12

    real_return = ((1 + expected_return_post_pct / 100) / (1 + inflation_pct / 100)) - 1
    if abs(real_return) < 1e-9:
        corpus = annual_expense_at_retirement * years_in_retirement
    else:
        corpus = annual_expense_at_retirement * (1 - (1 + real_return) ** (-years_in_retirement)) / real_return

    months = years_to_retirement * 12
    monthly_rate = expected_return_pre_pct / 12 / 100
    if months <= 0:
        required_sip = corpus
    elif monthly_rate == 0:
        required_sip = corpus / months
    else:
        required_sip = corpus / ((((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate))

    return {
        "years_to_retirement": years_to_retirement,
        "years_in_retirement": years_in_retirement,
        "monthly_expense_at_retirement": monthly_expense_at_retirement,
        "corpus_required": corpus,
        "required_monthly_sip": required_sip,
    }


def debt_payoff_plan(debts, extra_monthly_payment=0, strategy="avalanche"):
    """
    Simulate paying off multiple debts using the avalanche (highest interest
    rate first) or snowball (smallest balance first) method. `debts` is a
    list of dicts with name, balance, interest_rate (annual %), min_payment.
    Returns months to debt-free, total interest paid, and a payoff order.
    """
    working = [dict(d) for d in debts if d["balance"] > 0]
    if not working:
        return {"months": 0, "total_interest": 0, "payoff_order": [], "monthly_log": []}

    if strategy == "avalanche":
        working.sort(key=lambda d: -d["interest_rate"])
    else:  # snowball
        working.sort(key=lambda d: d["balance"])

    total_interest = 0.0
    month = 0
    payoff_order = []
    monthly_log = []
    extra_pool = extra_monthly_payment

    while working and month < 1200:  # 100-year safety cap
        month += 1
        month_interest = 0.0
        freed_up = 0.0  # min payments from debts paid off this month, added to next month's extra pool

        # Accrue interest and apply minimum payments first
        for d in working:
            interest = d["balance"] * (d["interest_rate"] / 12 / 100)
            month_interest += interest
            d["balance"] += interest
            pay = min(d["min_payment"], d["balance"])
            d["balance"] -= pay

        # Apply extra payment to the top-priority (first) debt in the sorted order
        pool = extra_pool
        for d in working:
            if pool <= 0:
                break
            pay_extra = min(pool, d["balance"])
            d["balance"] -= pay_extra
            pool -= pay_extra

        total_interest += month_interest

        still_owing = []
        for d in working:
            if d["balance"] <= 0.01:
                payoff_order.append({"name": d["name"], "month_paid_off": month})
                freed_up += d["min_payment"]
            else:
                still_owing.append(d)
        working = still_owing
        extra_pool += freed_up  # roll freed-up minimums into the extra payment pool

        monthly_log.append({
            "month": month,
            "total_balance": sum(d["balance"] for d in working),
            "interest_paid": month_interest,
        })

    return {
        "months": month,
        "total_interest": total_interest,
        "payoff_order": payoff_order,
        "monthly_log": monthly_log,
    }


def required_sip_for_goal(target_amount, years, annual_rate_pct):
    """Monthly investment required to reach a target amount by a given time,
    at an assumed rate of return."""
    months = int(years * 12)
    monthly_rate = annual_rate_pct / 12 / 100
    if months <= 0:
        return target_amount
    if monthly_rate == 0:
        return target_amount / months
    return target_amount / ((((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate))