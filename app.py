import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime

import data_manager as dm
import calculators as calc

st.set_page_config(
    page_title="Finly — Personal Financial Planner",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
# A medium-dark theme: not pure black (easier on the eyes, per request),
# with every text/background pairing checked against WCAG AA contrast
# (>=4.5:1) so values stay legible on a phone screen, not just on a
# calibrated desktop monitor.
BG = "#161B26"                # page canvas — dark slate, not black
SURFACE = "#232C3F"            # card background, one step lighter than bg
BORDER = "#3C4863"
NAVY = "#10141D"               # sidebar — one step darker, for separation
NAVY_ELEVATED = "#1B212E"      # sidebar quick-stat cards
NAVY_BORDER = "#2E3750"
TEXT_PRIMARY = "#F1F5F9"       # 15.7:1 on bg
TEXT_SECONDARY = "#B7C0D1"     # 9.4:1 on bg / 8.3:1 on surface
TEXT_TERTIARY = "#8E9AB3"      # 6.1:1 on bg / 5.4:1 on surface
ACCENT = "#34D399"             # 7.9:1 on surface
ACCENT_TEXT_ON = "#06281C"     # dark text for use ON TOP of accent-colored buttons (8.2:1)
ACCENT_HOVER = "#2BBD89"
POSITIVE = "#4ADE80"           # 8.7:1 on surface
POSITIVE_BG = "rgba(74,222,128,0.14)"
NEGATIVE = "#F87171"           # 5.5:1 on surface
NEGATIVE_BG = "rgba(248,113,113,0.14)"
WARN = "#FBBF24"               # 9.1:1 on surface
WARN_BG = "rgba(251,191,36,0.14)"
INFO = "#60A5FA"               # 6.0:1 on surface
INFO_BG = "rgba(96,165,250,0.14)"
PALETTE = ["#34D399", "#60A5FA", "#FBBF24", "#F87171", "#A78BFA", "#22D3EE", "#A3E635", "#F472B6"]

# ---------------------------------------------------------------------------
# Styling — light, professional "fintech dashboard" look: dark navy sidebar
# for navigation/branding, clean white cards on a soft gray canvas for content.
# A light Streamlit theme base is used (see .streamlit/config.toml) so native
# widgets (selects, date pickers, menus) keep correct contrast automatically.
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background-color: {BG}; }}
    [data-testid="stAppViewContainer"] {{ background-color: {BG}; }}
    [data-testid="stHeader"] {{ background-color: transparent; }}

    h1, h2, h3, h4, h5 {{ font-family: 'Inter', sans-serif; color: {TEXT_PRIMARY}; }}
    p, span, label {{ color: {TEXT_PRIMARY}; }}
    [data-testid="stCaptionContainer"] {{ color: {TEXT_SECONDARY} !important; }}

    /* ---- Sidebar (one shade darker, for navigation / brand identity) ---- */
    [data-testid="stSidebar"] {{
        background-color: {NAVY};
        border-right: 1px solid {NAVY_BORDER};
    }}
    [data-testid="stSidebar"] * {{ color: #EDF1F7 !important; }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{ color: #9AA7C2 !important; }}
    [data-testid="stSidebar"] hr {{ border-color: {NAVY_BORDER} !important; }}
    [data-testid="stSidebar"] [data-testid="stMetric"] {{
        background-color: {NAVY_ELEVATED};
        border: 1px solid {NAVY_BORDER};
        border-radius: 10px;
        padding: 12px 14px;
    }}
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {{ font-size: 0.78rem; }}
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {{
        font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem;
    }}
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] {{ gap: 2px; }}
    [data-testid="stSidebar"] .stRadio label {{
        padding: 10px 12px; border-radius: 8px; width: 100%;
    }}
    [data-testid="stSidebar"] .stRadio label:hover {{ background-color: {NAVY_ELEVATED}; }}
    .brand-mark {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.35rem; font-weight: 700; color: #FFFFFF !important;
        letter-spacing: -0.01em; margin-bottom: 0;
    }}
    .brand-sub {{ color: #9AA7C2 !important; font-size: 0.82rem; margin-top: -4px; }}

    /* ---- Page header ---- */
    .finly-eyebrow {{ color: {ACCENT}; font-weight: 600; font-size: 0.82rem; margin-bottom: 2px; }}
    .finly-title {{
        font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 600;
        color: {TEXT_PRIMARY}; margin: 0 0 2px 0;
    }}
    .finly-subtitle {{ color: {TEXT_SECONDARY}; margin-bottom: 18px; font-size: 0.97rem; }}

    /* ---- KPI cards (custom, with colored accent bar) ---- */
    .kpi-card {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-left: 4px solid {ACCENT};
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(16,24,40,0.04);
        height: 100%;
    }}
    .kpi-label {{ color: {TEXT_SECONDARY}; font-size: 0.82rem; font-weight: 500; margin-bottom: 6px; }}
    .kpi-value {{
        font-family: 'Space Grotesk', sans-serif; font-size: 1.55rem; font-weight: 600;
        color: {TEXT_PRIMARY}; font-feature-settings: "tnum"; letter-spacing: -0.01em;
    }}
    .kpi-sublabel {{ color: {TEXT_TERTIARY}; font-size: 0.8rem; margin-top: 4px; }}

    /* ---- Native metric cards elsewhere in main content ---- */
    .main [data-testid="stMetric"] {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(16,24,40,0.04);
    }}

    /* ---- Containers / cards ---- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {SURFACE};
        border: 1px solid {BORDER} !important;
        border-radius: 12px;
        box-shadow: 0 1px 2px rgba(16,24,40,0.04);
    }}

    .goal-badge {{
        display: inline-block; padding: 3px 11px; border-radius: 999px;
        background-color: {INFO_BG}; color: {INFO}; font-size: 0.76rem;
        font-weight: 600; margin-bottom: 8px;
    }}
    .status-ok {{ background-color: {POSITIVE_BG}; color: {POSITIVE}; }}
    .status-warn {{ background-color: {WARN_BG}; color: {WARN}; }}
    .status-over {{ background-color: {NEGATIVE_BG}; color: {NEGATIVE}; }}
    .status-pill {{
        display: inline-block; padding: 3px 11px; border-radius: 999px;
        font-size: 0.76rem; font-weight: 700;
    }}

    /* ---- Buttons ---- */
    .stButton button {{
        border-radius: 8px; font-weight: 500;
        background-color: {SURFACE}; border: 1px solid {BORDER}; color: {TEXT_PRIMARY};
    }}
    .stButton button:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}
    .stFormSubmitButton button {{
        background-color: {ACCENT} !important; border-color: {ACCENT} !important;
        color: {ACCENT_TEXT_ON} !important; font-weight: 700; border-radius: 8px;
    }}
    .stFormSubmitButton button:hover {{ background-color: {ACCENT_HOVER} !important; }}

    /* ---- Inputs / selects ---- */
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input, [data-baseweb="select"] > div,
    [data-baseweb="base-input"] {{
        background-color: {SURFACE} !important;
        border-color: {BORDER} !important;
        color: {TEXT_PRIMARY} !important;
    }}

    /* ---- Progress bars ---- */
    .stProgress > div > div > div {{ background-color: {ACCENT}; }}
    .stProgress > div {{ background-color: {BORDER} !important; }}

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab"] {{ font-weight: 500; color: {TEXT_SECONDARY}; }}
    .stTabs [aria-selected="true"] {{ color: {ACCENT} !important; }}

    /* ---- Expander ---- */
    [data-testid="stExpander"] summary {{
        background-color: {SURFACE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
        color: {TEXT_PRIMARY} !important;
    }}

    /* ---- Dataframe ---- */
    [data-testid="stDataFrame"] {{ background-color: {SURFACE}; }}

    hr {{ border-color: {BORDER} !important; }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* ---- Mobile tweaks ---- */
    @media (max-width: 640px) {{
        .finly-title {{ font-size: 1.5rem; }}
        .kpi-value {{ font-size: 1.35rem; }}
        .kpi-card {{ padding: 14px 16px; }}
        .main [data-testid="stMetric"] {{ padding: 14px 16px; }}
        div.block-container {{ padding-left: 1rem; padding-right: 1rem; padding-top: 2rem; }}
        .stButton button, .stFormSubmitButton button {{ min-height: 44px; }}
        [data-testid="stNumberInput"] input, [data-baseweb="select"] > div {{ min-height: 44px; }}
    }}
</style>
""", unsafe_allow_html=True)


def kpi_card(label, value, sublabel=None, color=ACCENT):
    sub_html = f'<div class="kpi-sublabel">{sublabel}</div>' if sublabel else ""
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)


def status_pill(text, level="ok"):
    cls = {"ok": "status-ok", "warn": "status-warn", "over": "status-over"}[level]
    return f'<span class="status-pill {cls}">{text}</span>'


def style_fig(fig, height=320, legend=False):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_PRIMARY, family="Inter, sans-serif", size=12),
        height=height,
        margin=dict(l=10, r=10, t=30 if legend else 10, b=10),
        showlegend=legend,
        legend=dict(orientation="h", y=1.12, x=0, font=dict(color=TEXT_PRIMARY)) if legend else None,
    )
    # Explicit tickfont color: relying only on the layout-level font color
    # left axis tick labels too faint to read on some renderers/screens.
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER, showline=False, tickfont=dict(color=TEXT_SECONDARY))
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER, showline=False, tickfont=dict(color=TEXT_SECONDARY))
    return fig


def clean_date_axis(fig, dates):
    """Force exactly one tick per data point, cleanly formatted (e.g. "Oct 1,
    2026"). Without this, Plotly can auto-subdivide a short date range down
    to millisecond-level ticks, which is unreadable (and was the cause of
    the stray "23:59:59.999" labels some users saw on a 1-2 point chart)."""
    unique_dates = sorted(pd.to_datetime(dates).unique())
    fig.update_xaxes(
        tickmode="array",
        tickvals=unique_dates,
        ticktext=[pd.Timestamp(d).strftime("%b %d, %Y") for d in unique_dates],
    )
    return fig


if "data" not in st.session_state:
    st.session_state.data = dm.load_data()

# Self-heal: if this browser session has been open since before a schema
# change (new fields added in an app update), backfill them now instead of
# crashing with a KeyError on an old, cached session_state dict.
st.session_state.data, _schema_changed = dm.ensure_schema(st.session_state.data)
if _schema_changed:
    dm.save_data(st.session_state.data)

data = st.session_state.data
currency = data["settings"].get("currency", "Rs.")
CURRENCIES = ["Rs.", "$", "€", "£", "¥"]


def fmt(amount):
    sep = "" if currency in ("$", "€", "£", "¥") else " "
    return f"{currency}{sep}{amount:,.2f}"


def page_header(eyebrow, title, subtitle):
    st.markdown(f'<div class="finly-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="finly-title">{title}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="finly-subtitle">{subtitle}</p>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<p class="brand-mark">💠 Finly</p>', unsafe_allow_html=True)
    st.markdown('<p class="brand-sub">Personal financial planner</p>', unsafe_allow_html=True)
    st.write("")
    page = st.radio(
        "Navigate",
        ["Dashboard", "Budget", "Net Worth", "Goals", "Calculators", "Settings"],
        label_visibility="collapsed",
    )
    st.divider()
    monthly_income = dm.total_monthly_income(data)
    monthly_expenses = dm.total_monthly_expenses(data)
    cash_flow = monthly_income - monthly_expenses
    st.caption("Quick snapshot")
    st.metric("Monthly cash flow", fmt(cash_flow))
    nw = dm.latest_net_worth(data)
    if nw:
        st.metric("Net worth", fmt(nw["net_worth"]))
    st.caption(f"Updated {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------
if page == "Dashboard":
    page_header("Overview", "Dashboard", "A snapshot of where things stand today")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Monthly income", fmt(monthly_income), color=POSITIVE)
    with c2:
        kpi_card("Monthly expenses", fmt(monthly_expenses), color=NEGATIVE)
    with c3:
        savings_rate = f"{(cash_flow / monthly_income * 100):.0f}% savings rate" if monthly_income > 0 else "Add income to calculate"
        kpi_card("Cash flow", fmt(cash_flow), sublabel=savings_rate, color=INFO if cash_flow >= 0 else WARN)
    with c4:
        kpi_card("Net worth", fmt(nw["net_worth"]) if nw else "No data yet", color=ACCENT)

    st.write("")
    left, right = st.columns([1.3, 1])

    with left:
        st.markdown("#### Net worth over time")
        if data["net_worth_snapshots"]:
            df = pd.DataFrame(data["net_worth_snapshots"])
            df["date"] = pd.to_datetime(df["date"])
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["date"], y=df["net_worth"], mode="lines+markers",
                line=dict(color=ACCENT, width=3), fill="tozeroy",
                fillcolor="rgba(15,118,110,0.08)", name="Net worth",
            ))
            st.plotly_chart(clean_date_axis(style_fig(fig), df["date"]), width='stretch')
        else:
            st.info("Add a net worth snapshot to see your trend here.")

    with right:
        st.markdown("#### Spending by category")
        if data["expenses"]:
            exp_df = pd.DataFrame(data["expenses"])
            exp_df["monthly"] = exp_df.apply(lambda r: dm.monthly_amount(r["amount"], r["frequency"]), axis=1)
            cat_df = exp_df.groupby("category")["monthly"].sum().reset_index()
            fig = px.pie(cat_df, values="monthly", names="category", hole=0.55, color_discrete_sequence=PALETTE)
            st.plotly_chart(style_fig(fig, legend=True), width='stretch')
        else:
            st.info("Add expenses in the Budget tab to see the breakdown.")

    if data["monthly_history"]:
        st.markdown("#### Income vs. expenses over time")
        hist_df = pd.DataFrame(data["monthly_history"])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=hist_df["month"], y=hist_df["income"], name="Income", marker_color=POSITIVE))
        fig.add_trace(go.Bar(x=hist_df["month"], y=hist_df["expenses"], name="Expenses", marker_color=NEGATIVE))
        fig.add_trace(go.Scatter(x=hist_df["month"], y=hist_df["net"], name="Net", mode="lines+markers", line=dict(color=ACCENT, width=3)))
        fig.update_layout(barmode="group", xaxis_title="Month", yaxis_title=f"Amount ({currency})")
        st.plotly_chart(style_fig(fig, height=320, legend=True), width='stretch')

    # Budget health alerts
    if data["budget_limits"]:
        st.markdown("#### Budget health")
        spend = dm.spending_by_category(data)
        over_budget = []
        for cat, limit in data["budget_limits"].items():
            spent = spend.get(cat, 0)
            pct = spent / limit if limit else 0
            if pct >= 1:
                over_budget.append((cat, spent, limit, pct))
        if over_budget:
            for cat, spent, limit, pct in over_budget:
                st.markdown(
                    f"{status_pill('Over budget', 'over')} **{cat}** — spent {fmt(spent)} of {fmt(limit)} limit ({pct*100:.0f}%)",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(status_pill("All categories within budget", "ok"), unsafe_allow_html=True)

    st.markdown("#### Goal progress")
    if data["goals"]:
        gcols = st.columns(min(3, len(data["goals"])))
        for i, g in enumerate(data["goals"]):
            pct = min(g["current_amount"] / g["target_amount"], 1.0) if g["target_amount"] else 0
            with gcols[i % len(gcols)]:
                with st.container(border=True):
                    st.markdown(f'<span class="goal-badge">{g["category"]}</span>', unsafe_allow_html=True)
                    st.markdown(f"**{g['name']}**")
                    st.progress(pct)
                    st.caption(f"{fmt(g['current_amount'])} of {fmt(g['target_amount'])} · {pct*100:.0f}%")
    else:
        st.info("Set a savings goal in the Goals tab to track progress here.")

# ---------------------------------------------------------------------------
# BUDGET
# ---------------------------------------------------------------------------
elif page == "Budget":
    page_header("Plan", "Budget", "Track income and expenses, and set spending limits by category")

    tab1, tab2, tab3 = st.tabs(["Income", "Expenses", "Budget limits"])

    with tab1:
        with st.expander("➕ Add income source", expanded=len(data["income"]) == 0):
            with st.form("add_income_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                name = c1.text_input("Source", placeholder="e.g. Salary")
                amount = c2.number_input("Amount", min_value=0.0, step=50.0)
                frequency = c3.selectbox("Frequency", list(dm.FREQUENCY_TO_MONTHLY.keys()))
                if st.form_submit_button("Add income", width='stretch'):
                    if name and amount > 0:
                        dm.add_income(data, name, amount, frequency)
                        st.rerun()
                    else:
                        st.warning("Enter a name and an amount greater than 0.")

        if data["income"]:
            for item in data["income"]:
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                c1.write(f"**{item['name']}**")
                c2.write(fmt(item["amount"]))
                c3.write(item["frequency"])
                if c4.button("🗑️", key=f"del_income_{item['id']}"):
                    dm.delete_income(data, item["id"])
                    st.rerun()
            st.metric("Total monthly income", fmt(monthly_income))
        else:
            st.caption("No income sources yet.")

    with tab2:
        with st.expander("➕ Add expense", expanded=len(data["expenses"]) == 0):
            with st.form("add_expense_form", clear_on_submit=True):
                c1, c2, c3, c4 = st.columns(4)
                category = c1.selectbox("Category", dm.EXPENSE_CATEGORIES)
                name = c2.text_input("Description", placeholder="e.g. Rent")
                amount = c3.number_input("Amount", min_value=0.0, step=10.0, key="exp_amount")
                frequency = c4.selectbox("Frequency", list(dm.FREQUENCY_TO_MONTHLY.keys()), key="exp_freq")
                if st.form_submit_button("Add expense", width='stretch'):
                    if name and amount > 0:
                        dm.add_expense(data, category, name, amount, frequency)
                        st.rerun()
                    else:
                        st.warning("Enter a description and an amount greater than 0.")

        if data["expenses"]:
            exp_df = pd.DataFrame(data["expenses"])
            for cat in exp_df["category"].unique():
                st.markdown(f"**{cat}**")
                sub = exp_df[exp_df["category"] == cat]
                for _, item in sub.iterrows():
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    c1.write(item["name"])
                    c2.write(fmt(item["amount"]))
                    c3.write(item["frequency"])
                    if c4.button("🗑️", key=f"del_exp_{item['id']}"):
                        dm.delete_expense(data, int(item["id"]))
                        st.rerun()
            st.metric("Total monthly expenses", fmt(monthly_expenses))
        else:
            st.caption("No expenses yet.")

    with tab3:
        st.caption("Set a monthly spending limit per category to get an over-budget alert on your dashboard.")
        spend = dm.spending_by_category(data)
        categories_with_data = sorted(set(list(spend.keys()) + list(data["budget_limits"].keys())) or dm.EXPENSE_CATEGORIES)

        with st.form("set_limit_form"):
            c1, c2 = st.columns(2)
            limit_cat = c1.selectbox("Category", dm.EXPENSE_CATEGORIES)
            limit_amount = c2.number_input("Monthly limit (0 to remove)", min_value=0.0, step=50.0,
                                            value=float(data["budget_limits"].get(limit_cat, 0)))
            if st.form_submit_button("Save limit", width='stretch'):
                dm.set_budget_limit(data, limit_cat, limit_amount)
                st.rerun()

        if data["budget_limits"]:
            st.write("")
            for cat, limit in data["budget_limits"].items():
                spent = spend.get(cat, 0)
                pct = min(spent / limit, 1.2) if limit else 0
                level = "over" if pct >= 1 else ("warn" if pct >= 0.8 else "ok")
                label = "Over budget" if level == "over" else ("Near limit" if level == "warn" else "On track")
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{cat}** &nbsp; {status_pill(label, level)}", unsafe_allow_html=True)
                    st.progress(min(pct, 1.0))
                    st.caption(f"{fmt(spent)} of {fmt(limit)} monthly limit")
                with c2:
                    st.write("")
                    if st.button("Remove", key=f"rm_limit_{cat}"):
                        dm.set_budget_limit(data, cat, 0)
                        st.rerun()
        else:
            st.caption("No budget limits set yet.")

    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Income", fmt(monthly_income))
    c2.metric("Expenses", fmt(monthly_expenses))
    if cash_flow >= 0:
        st.success(f"You're cash-flow positive by {fmt(cash_flow)} per month.")
    else:
        st.error(f"You're spending {fmt(-cash_flow)} more than you earn each month.")

    st.write("")
    with st.expander("📌 Log this month to your trend history"):
        st.caption("Save this month's totals so you can track income vs. expenses over time on the Dashboard.")
        month_choice = st.date_input("Month", value=date.today(), key="history_month_picker")
        month_str = month_choice.strftime("%Y-%m")
        if st.button("Save this month's totals", key="save_month_btn"):
            dm.record_monthly_snapshot(data, month_str, monthly_income, monthly_expenses)
            st.success(f"Saved totals for {month_choice.strftime('%B %Y')}.")
            st.rerun()

# ---------------------------------------------------------------------------
# NET WORTH
# ---------------------------------------------------------------------------
elif page == "Net Worth":
    page_header("Track", "Net Worth", "Log a snapshot of what you own and owe to track your trend")

    with st.expander("➕ Add a snapshot", expanded=len(data["net_worth_snapshots"]) == 0):
        with st.form("add_snapshot_form", clear_on_submit=True):
            snap_date = st.date_input("Snapshot date", value=date.today())
            st.markdown("**Assets**")
            a1, a2, a3, a4 = st.columns(4)
            cash = a1.number_input("Cash & checking", min_value=0.0, step=100.0)
            savings = a2.number_input("Savings", min_value=0.0, step=100.0)
            investments = a3.number_input("Investments", min_value=0.0, step=100.0)
            property_val = a4.number_input("Property / other", min_value=0.0, step=100.0)

            st.markdown("**Liabilities**")
            l1, l2, l3, l4 = st.columns(4)
            credit_card = l1.number_input("Credit cards", min_value=0.0, step=50.0)
            student_loan = l2.number_input("Student / education loan", min_value=0.0, step=50.0)
            mortgage = l3.number_input("Home loan", min_value=0.0, step=100.0)
            other_debt = l4.number_input("Other debt", min_value=0.0, step=50.0)

            if st.form_submit_button("Save snapshot", width='stretch'):
                assets = {"Cash & checking": cash, "Savings": savings, "Investments": investments, "Property / other": property_val}
                liabilities = {"Credit cards": credit_card, "Student / education loan": student_loan, "Home loan": mortgage, "Other debt": other_debt}
                dm.add_net_worth_snapshot(data, snap_date, assets, liabilities)
                st.rerun()

    if data["net_worth_snapshots"]:
        df = pd.DataFrame(data["net_worth_snapshots"])
        df["date"] = pd.to_datetime(df["date"])

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["date"], y=df["total_assets"], name="Assets", marker_color=POSITIVE))
        fig.add_trace(go.Bar(x=df["date"], y=-df["total_liabilities"], name="Liabilities", marker_color=NEGATIVE))
        fig.add_trace(go.Scatter(x=df["date"], y=df["net_worth"], name="Net worth", mode="lines+markers", line=dict(color=ACCENT, width=3)))
        fig.update_layout(barmode="relative")
        st.plotly_chart(clean_date_axis(style_fig(fig, height=380, legend=True), df["date"]), width='stretch')

        latest = data["net_worth_snapshots"][-1]
        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("Total assets", fmt(latest["total_assets"]), color=POSITIVE)
        with c2:
            kpi_card("Total liabilities", fmt(latest["total_liabilities"]), color=NEGATIVE)
        with c3:
            kpi_card("Net worth", fmt(latest["net_worth"]), color=ACCENT)

        st.write("")
        asset_items = {k: v for k, v in latest["assets"].items() if v > 0}
        if asset_items:
            st.markdown("#### Asset allocation (latest snapshot)")
            alloc_df = pd.DataFrame({"category": list(asset_items.keys()), "amount": list(asset_items.values())})
            fig = px.pie(alloc_df, values="amount", names="category", hole=0.55, color_discrete_sequence=PALETTE)
            st.plotly_chart(style_fig(fig, height=300, legend=True), width='stretch')

        st.markdown("#### History")
        for snap in reversed(data["net_worth_snapshots"]):
            c1, c2, c3 = st.columns([2, 3, 1])
            c1.write(snap["date"])
            c2.write(f"Net worth: {fmt(snap['net_worth'])}")
            if c3.button("🗑️", key=f"del_snap_{snap['id']}"):
                dm.delete_net_worth_snapshot(data, snap["id"])
                st.rerun()
    else:
        st.info("No snapshots yet — add one above to start your trend line.")

# ---------------------------------------------------------------------------
# GOALS
# ---------------------------------------------------------------------------
elif page == "Goals":
    page_header("Plan", "Savings Goals", "Set targets and track your progress toward them")

    with st.expander("➕ Add a goal", expanded=len(data["goals"]) == 0):
        with st.form("add_goal_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Goal name", placeholder="e.g. Emergency fund")
            category = c2.selectbox("Category", ["Emergency fund", "Travel", "Home", "Vehicle", "Retirement", "Debt payoff", "Other"])
            c3, c4, c5 = st.columns(3)
            target_amount = c3.number_input("Target amount", min_value=0.0, step=100.0)
            current_amount = c4.number_input("Current amount saved", min_value=0.0, step=50.0)
            target_date = c5.date_input("Target date", value=date.today())
            if st.form_submit_button("Add goal", width='stretch'):
                if name and target_amount > 0:
                    dm.add_goal(data, name, target_amount, current_amount, target_date, category)
                    st.rerun()
                else:
                    st.warning("Enter a goal name and a target amount greater than 0.")

    if data["goals"]:
        for g in data["goals"]:
            pct = min(g["current_amount"] / g["target_amount"], 1.0) if g["target_amount"] else 0
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f'<span class="goal-badge">{g["category"]}</span>', unsafe_allow_html=True)
                    st.markdown(f"**{g['name']}**")
                    st.progress(pct)
                    days_left = (datetime.strptime(g["target_date"], "%Y-%m-%d").date() - date.today()).days
                    due = f"{days_left} days left" if days_left >= 0 else "target date passed"
                    st.caption(f"{fmt(g['current_amount'])} of {fmt(g['target_amount'])} ({pct*100:.0f}%) · due {g['target_date']} · {due}")
                with c2:
                    new_amount = st.number_input(
                        "Update saved", min_value=0.0, value=float(g["current_amount"]),
                        step=50.0, key=f"goal_update_{g['id']}", label_visibility="collapsed",
                    )
                    bcol1, bcol2 = st.columns(2)
                    if bcol1.button("Save", key=f"save_goal_{g['id']}", width='stretch'):
                        dm.update_goal_progress(data, g["id"], new_amount)
                        st.rerun()
                    if bcol2.button("🗑️", key=f"del_goal_{g['id']}", width='stretch'):
                        dm.delete_goal(data, g["id"])
                        st.rerun()
    else:
        st.info("No goals yet — add one above to start tracking.")

# ---------------------------------------------------------------------------
# CALCULATORS
# ---------------------------------------------------------------------------
elif page == "Calculators":
    page_header("Plan ahead", "Financial Calculators", "Run the numbers on loans, investments, and retirement")

    calc_tab = st.selectbox(
        "Choose a calculator",
        ["Loan / EMI calculator", "SIP & lump sum growth", "Retirement planner", "Goal-based SIP", "Debt payoff planner"],
    )
    st.write("")

    # ---- Loan / EMI ----
    if calc_tab == "Loan / EMI calculator":
        c1, c2, c3 = st.columns(3)
        principal = c1.number_input("Loan amount", min_value=0.0, value=1000000.0, step=10000.0)
        rate = c2.number_input("Annual interest rate (%)", min_value=0.0, value=9.0, step=0.1)
        tenure_years = c3.number_input("Tenure (years)", min_value=0.0, value=20.0, step=1.0)

        result = calc.emi_schedule(principal, rate, int(tenure_years * 12))

        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("Monthly EMI", fmt(result["emi"]), color=ACCENT)
        with c2:
            kpi_card("Total interest payable", fmt(result["total_interest"]), color=NEGATIVE)
        with c3:
            kpi_card("Total payment", fmt(result["total_payment"]), color=INFO)

        if result["schedule"]:
            sched_df = pd.DataFrame(result["schedule"])
            yearly = sched_df.copy()
            yearly["year"] = ((yearly["month"] - 1) // 12) + 1
            yearly_sum = yearly.groupby("year")[["principal", "interest"]].sum().reset_index()

            fig = go.Figure()
            fig.add_trace(go.Bar(x=yearly_sum["year"], y=yearly_sum["principal"], name="Principal", marker_color=ACCENT))
            fig.add_trace(go.Bar(x=yearly_sum["year"], y=yearly_sum["interest"], name="Interest", marker_color=WARN))
            fig.update_layout(barmode="stack", xaxis_title="Year", yaxis_title=f"Amount ({currency})")
            st.markdown("#### Principal vs. interest, by year")
            st.plotly_chart(style_fig(fig, height=360, legend=True), width='stretch')

            with st.expander("View full amortization schedule"):
                display_df = sched_df.copy()
                for col in ["emi", "principal", "interest", "balance"]:
                    display_df[col] = display_df[col].round(2)
                st.dataframe(display_df, width='stretch', hide_index=True)
        st.caption("Estimates only, based on a fixed interest rate — actual bank terms may vary.")

    # ---- SIP & lump sum growth ----
    elif calc_tab == "SIP & lump sum growth":
        mode = st.radio("Investment type", ["Monthly SIP", "One-time lump sum", "Both combined"], horizontal=True)
        c1, c2, c3 = st.columns(3)
        monthly_inv = 0.0
        lumpsum = 0.0
        if mode in ("Monthly SIP", "Both combined"):
            monthly_inv = c1.number_input("Monthly investment", min_value=0.0, value=10000.0, step=500.0)
        if mode in ("One-time lump sum", "Both combined"):
            lumpsum = c1.number_input("Lump sum amount", min_value=0.0, value=100000.0, step=10000.0, key="lumpsum_amt")
        rate = c2.number_input("Expected annual return (%)", min_value=0.0, value=12.0, step=0.5, key="sip_rate")
        years = c3.number_input("Time horizon (years)", min_value=1, value=10, step=1, key="sip_years")

        sip_result = calc.sip_future_value(monthly_inv, rate, years) if monthly_inv > 0 else None
        lumpsum_fv = calc.lumpsum_future_value(lumpsum, rate, years) if lumpsum > 0 else 0

        total_invested = (sip_result["invested"] if sip_result else 0) + lumpsum
        total_future_value = (sip_result["future_value"] if sip_result else 0) + lumpsum_fv
        total_gains = total_future_value - total_invested

        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("Total invested", fmt(total_invested), color=INFO)
        with c2:
            kpi_card("Estimated gains", fmt(total_gains), color=POSITIVE)
        with c3:
            kpi_card("Future value", fmt(total_future_value), color=ACCENT)

        if sip_result and sip_result["yearly"]:
            yearly_df = pd.DataFrame(sip_result["yearly"])
            if lumpsum > 0:
                yearly_df["value"] = yearly_df.apply(
                    lambda r: r["value"] + calc.lumpsum_future_value(lumpsum, rate, r["year"]), axis=1
                )
                yearly_df["invested"] = yearly_df["invested"] + lumpsum
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=yearly_df["year"], y=yearly_df["invested"], name="Invested", line=dict(color=TEXT_SECONDARY, dash="dot")))
            fig.add_trace(go.Scatter(x=yearly_df["year"], y=yearly_df["value"], name="Portfolio value", fill="tonexty", line=dict(color=ACCENT, width=3)))
            fig.update_layout(xaxis_title="Year", yaxis_title=f"Amount ({currency})")
            st.markdown("#### Growth over time")
            st.plotly_chart(style_fig(fig, height=360, legend=True), width='stretch')
        st.caption("Estimates only — actual investment returns are not guaranteed and will vary.")

    # ---- Retirement planner ----
    elif calc_tab == "Retirement planner":
        c1, c2, c3 = st.columns(3)
        current_age = c1.number_input("Current age", min_value=18, max_value=80, value=30)
        retirement_age = c2.number_input("Retirement age", min_value=current_age + 1, max_value=90, value=60)
        life_expectancy = c3.number_input("Life expectancy", min_value=retirement_age + 1, max_value=110, value=85)

        c1, c2, c3 = st.columns(3)
        monthly_expense = c1.number_input("Current monthly expenses", min_value=0.0, value=50000.0, step=1000.0)
        inflation = c2.number_input("Expected inflation (%)", min_value=0.0, value=6.0, step=0.5)
        pre_return = c3.number_input("Expected return before retirement (%)", min_value=0.0, value=12.0, step=0.5)
        post_return = st.number_input("Expected return during retirement (%)", min_value=0.0, value=7.0, step=0.5)

        result = calc.retirement_corpus(current_age, retirement_age, monthly_expense, inflation, pre_return, post_return, life_expectancy)

        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("Monthly expense at retirement", fmt(result["monthly_expense_at_retirement"]), color=WARN)
        with c2:
            kpi_card("Retirement corpus needed", fmt(result["corpus_required"]), color=ACCENT)
        with c3:
            kpi_card("Required monthly SIP today", fmt(result["required_monthly_sip"]), color=INFO)

        st.caption(
            f"Based on {result['years_to_retirement']} years to retirement and a "
            f"{result['years_in_retirement']}-year retirement horizon. Estimates only — actual needs depend on "
            "lifestyle, healthcare costs, and market conditions."
        )

    # ---- Goal-based SIP ----
    elif calc_tab == "Goal-based SIP":
        c1, c2, c3 = st.columns(3)
        target_amount = c1.number_input("Target amount", min_value=0.0, value=500000.0, step=10000.0)
        years = c2.number_input("Time horizon (years)", min_value=0.5, value=5.0, step=0.5, key="goal_years")
        rate = c3.number_input("Expected annual return (%)", min_value=0.0, value=10.0, step=0.5, key="goal_rate")

        required = calc.required_sip_for_goal(target_amount, years, rate)
        kpi_card("Required monthly investment", fmt(required), color=ACCENT)
        st.caption("This is how much you'd need to invest each month, assuming the stated rate of return, to reach your target. Estimates only.")

    # ---- Debt payoff planner ----
    elif calc_tab == "Debt payoff planner":
        st.caption("Add your debts below, then compare the avalanche (highest interest first) and snowball (smallest balance first) payoff strategies.")

        with st.expander("➕ Add a debt", expanded=len(data["debts"]) == 0):
            with st.form("add_debt_form", clear_on_submit=True):
                c1, c2, c3, c4 = st.columns(4)
                d_name = c1.text_input("Debt name", placeholder="e.g. Credit card")
                d_balance = c2.number_input("Current balance", min_value=0.0, step=1000.0)
                d_rate = c3.number_input("Annual interest rate (%)", min_value=0.0, step=0.5, value=18.0)
                d_min = c4.number_input("Minimum monthly payment", min_value=0.0, step=100.0)
                if st.form_submit_button("Add debt", width='stretch'):
                    if d_name and d_balance > 0:
                        dm.add_debt(data, d_name, d_balance, d_rate, d_min)
                        st.rerun()
                    else:
                        st.warning("Enter a debt name and a balance greater than 0.")

        if data["debts"]:
            for d in data["debts"]:
                c1, c2, c3, c4, c5 = st.columns([2.5, 1.5, 1.5, 1.5, 0.5])
                c1.write(f"**{d['name']}**")
                c2.write(fmt(d["balance"]))
                c3.write(f"{d['interest_rate']:.1f}%")
                c4.write(f"Min {fmt(d['min_payment'])}")
                if c5.button("🗑️", key=f"del_debt_{d['id']}"):
                    dm.delete_debt(data, d["id"])
                    st.rerun()

            st.write("")
            extra_payment = st.number_input("Extra monthly payment (beyond minimums)", min_value=0.0, step=500.0, value=0.0)

            col1, col2 = st.columns(2)
            avalanche = calc.debt_payoff_plan(data["debts"], extra_payment, "avalanche")
            snowball = calc.debt_payoff_plan(data["debts"], extra_payment, "snowball")

            with col1:
                st.markdown("##### Avalanche (highest interest first)")
                kpi_card("Debt-free in", f"{avalanche['months']} months", color=ACCENT)
                st.write("")
                kpi_card("Total interest paid", fmt(avalanche["total_interest"]), color=NEGATIVE)
                st.caption("Payoff order: " + " → ".join(p["name"] for p in avalanche["payoff_order"]))

            with col2:
                st.markdown("##### Snowball (smallest balance first)")
                kpi_card("Debt-free in", f"{snowball['months']} months", color=ACCENT)
                st.write("")
                kpi_card("Total interest paid", fmt(snowball["total_interest"]), color=NEGATIVE)
                st.caption("Payoff order: " + " → ".join(p["name"] for p in snowball["payoff_order"]))

            interest_diff = snowball["total_interest"] - avalanche["total_interest"]
            if abs(interest_diff) > 1:
                cheaper = "avalanche" if interest_diff > 0 else "snowball"
                st.info(f"The {cheaper} method saves you {fmt(abs(interest_diff))} in interest, "
                        f"{'though snowball can feel more motivating by clearing small debts first.' if cheaper == 'avalanche' else ''}")

            fig = go.Figure()
            av_df = pd.DataFrame(avalanche["monthly_log"])
            sn_df = pd.DataFrame(snowball["monthly_log"])
            fig.add_trace(go.Scatter(x=av_df["month"], y=av_df["total_balance"], name="Avalanche", line=dict(color=ACCENT, width=3)))
            fig.add_trace(go.Scatter(x=sn_df["month"], y=sn_df["total_balance"], name="Snowball", line=dict(color=INFO, width=3, dash="dot")))
            fig.update_layout(xaxis_title="Month", yaxis_title=f"Remaining balance ({currency})")
            st.markdown("#### Remaining balance over time")
            st.plotly_chart(style_fig(fig, height=320, legend=True), width='stretch')
        else:
            st.info("Add a debt above to see your payoff plan.")
        st.caption("Estimates only — assumes payments are made consistently and rates stay fixed.")

# ---------------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------------
elif page == "Settings":
    page_header("Preferences", "Settings", "Currency, data export, and reset options")

    st.markdown("#### Currency")
    new_currency = st.selectbox(
        "Symbol", CURRENCIES,
        index=CURRENCIES.index(currency) if currency in CURRENCIES else 0,
    )
    if new_currency != currency:
        data["settings"]["currency"] = new_currency
        dm.save_data(data)
        st.rerun()

    st.write("")
    st.markdown("#### Export your data")
    st.caption(f"Stored locally at `{dm.DATA_FILE}` — nothing leaves your machine.")

    ec1, ec2, ec3 = st.columns(3)
    ec1.download_button("⬇️ Income (CSV)", data=dm.export_income_csv(data), file_name="income.csv", mime="text/csv", width='stretch')
    ec2.download_button("⬇️ Expenses (CSV)", data=dm.export_expenses_csv(data), file_name="expenses.csv", mime="text/csv", width='stretch')
    ec3.download_button("⬇️ Net worth (CSV)", data=dm.export_net_worth_csv(data), file_name="net_worth.csv", mime="text/csv", width='stretch')
    ec4, ec5, ec6 = st.columns(3)
    ec4.download_button("⬇️ Goals (CSV)", data=dm.export_goals_csv(data), file_name="goals.csv", mime="text/csv", width='stretch')
    ec5.download_button("⬇️ Monthly history (CSV)", data=dm.export_monthly_history_csv(data), file_name="monthly_history.csv", mime="text/csv", width='stretch')
    ec6.download_button("⬇️ Debts (CSV)", data=dm.export_debts_csv(data), file_name="debts.csv", mime="text/csv", width='stretch')

    st.write("")
    import os as _os
    st.download_button(
        "⬇️ Full backup (JSON)",
        data=open(dm.DATA_FILE, "r").read() if _os.path.exists(dm.DATA_FILE) else "{}",
        file_name="financial_data.json",
        mime="application/json",
    )

    st.write("")
    st.markdown("#### Reset")
    if st.button("🗑️ Reset all data", type="secondary"):
        st.session_state["confirm_reset"] = True

    if st.session_state.get("confirm_reset"):
        st.warning("This will permanently delete all income, expenses, net worth snapshots, goals, and budget limits.")
        c1, c2 = st.columns(2)
        if c1.button("Yes, delete everything", type="primary", width='stretch'):
            dm.save_data(dm.fresh_data())
            st.session_state.data = dm.load_data()
            st.session_state["confirm_reset"] = False
            st.rerun()
        if c2.button("Cancel", width='stretch'):
            st.session_state["confirm_reset"] = False
            st.rerun()