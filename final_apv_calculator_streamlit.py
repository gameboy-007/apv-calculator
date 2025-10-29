import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# Streamlit App: APV Calculator (Centralia-style, full logic)
# ------------------------------------------------------------

st.set_page_config(page_title="APV Calculator (Centralia Case)", layout="centered")
st.title("💰 Adjusted Present Value (APV) Calculator — Centralia Style")
st.caption("Recreates the APV computation logic from the Centralia case with full exhibit-based breakdown.")

st.divider()

# -------------------------
# Input Section
# -------------------------
st.header("📥 Input Parameters")

col1, col2 = st.columns(2)
with col1:
    S0 = st.number_input("Current exchange rate ($/€)", value=1.32, step=0.01)
    pi_f = st.number_input("Foreign inflation rate (%)", value=2.1, step=0.1) / 100
    pi_d = st.number_input("Domestic inflation rate (%)", value=3.0, step=0.1) / 100
    C0_eur = st.number_input("Initial project cost (€)", value=5_500_000.0, step=100_000.0)
    years = st.number_input("Project duration (years)", value=8, step=1)

with col2:
    tax = st.number_input("Corporate tax rate (%)", value=35.0, step=0.1) / 100
    K_ud = st.number_input("Unlevered cost of capital (%)", value=12.0, step=0.1) / 100
    i_c = st.number_input("Concessional loan rate (%)", value=5.0, step=0.1) / 100
    i_d = st.number_input("Domestic borrowing rate (%)", value=8.0, step=0.1) / 100
    concession_loan_eur = st.number_input("Concessional loan amount (€)", value=4_000_000.0, step=100_000.0)

st.divider()
st.header("📊 Operating Parameters")

col3, col4 = st.columns(2)
with col3:
    units_y1 = st.number_input("Year 1 sales units", value=25000.0, step=100.0)
    units_growth = st.number_input("Annual sales unit growth (%)", value=12.0, step=0.1) / 100
    contrib_per_unit_eur_y1 = st.number_input("Contribution margin per unit (€)", value=40.0, step=0.1)
    contrib_growth = st.number_input("Annual growth in contribution margin (%)", value=2.1, step=0.1) / 100

with col4:
    lost_units_y1 = st.number_input("Year 1 lost sales units", value=9600.0, step=100.0)
    lost_units_growth = st.number_input("Annual growth in lost sales units (%)", value=5.0, step=0.1) / 100
    lost_margin_usd_y1 = st.number_input("Lost margin per unit ($)", value=35.0, step=0.1)
    lost_margin_growth = st.number_input("Annual growth in lost margin (%)", value=3.0, step=0.1) / 100

st.divider()

# -------------------------
# Compute button
# -------------------------
if st.button("📈 Calculate APV"):

    def S_t(t):
        return S0 * ((1 + pi_d) ** t) / ((1 + pi_f) ** t)

    depreciation_eur = C0_eur / years

    # Exhibit 18.2 — PV of after-tax operating CFs
    pv_operating = 0.0
    for t in range(1, years + 1):
        cm_eur = contrib_per_unit_eur_y1 * ((1 + contrib_growth) ** (t - 1))
        qty = units_y1 * ((1 + units_growth) ** (t - 1))
        a_usd = S_t(t) * (qty * cm_eur)
        lost_q = lost_units_y1 * ((1 + lost_units_growth) ** t)
        lost_margin_usd_t = lost_margin_usd_y1 * ((1 + lost_margin_growth) ** t)
        b_usd = -lost_q * lost_margin_usd_t
        ocf_usd = a_usd + b_usd
        ocf_aftertax = ocf_usd * (1 - tax)
        pv_operating += ocf_aftertax / ((1 + K_ud) ** t)
    pv_operating = round(pv_operating, 2)

    # Exhibit 18.3 — Depreciation tax shields
    pv_dep = 0.0
    for t in range(1, years + 1):
        shield_usd = tax * depreciation_eur * S_t(t)
        pv_dep += shield_usd / ((1 + i_d) ** t)
    pv_dep = round(pv_dep, 2)

    # Exhibit 18.4/18.5 — Concessional loan benefit
    principal_payment = concession_loan_eur / years
    remaining = concession_loan_eur
    pv_concess_payments = 0.0
    for t in range(1, years + 1):
        interest = remaining * i_c
        payment_usd = (principal_payment + interest) * S_t(t)
        pv_concess_payments += payment_usd / ((1 + i_d) ** t)
        remaining -= principal_payment
    pv_concess_payments = round(pv_concess_payments, 2)
    dollar_value_concession_loan = concession_loan_eur * S0
    pv_loan_benefit = round(dollar_value_concession_loan - pv_concess_payments, 2)

    # Exhibit 18.6 — Interest tax shields (lambda derived, not input)
    loan_ratio = concession_loan_eur / C0_eur
    borrowing_capacity_usd = 2_904_000  # from book logic (or can be parameterized)
    project_cost_usd = C0_eur * S0
    optimal_debt_ratio = borrowing_capacity_usd / project_cost_usd
    lambda_project = optimal_debt_ratio / loan_ratio

    remaining = concession_loan_eur
    pv_interest_tax = 0.0
    rows_186 = []
    for t in range(1, years + 1):
        interest = remaining * i_c
        shield_usd = S_t(t) * interest * lambda_project * tax
        pv = shield_usd / ((1 + i_d) ** t)
        rows_186.append([t, round(S_t(t), 4), interest, lambda_project, shield_usd, pv])
        pv_interest_tax += pv
        remaining -= principal_payment
    pv_interest_tax = round(pv_interest_tax, 2)

    # Freed-up affiliate funds (calculated)
    gross_up_eur = 750_000 / (1 - 0.20)
    dollar_value = gross_up_eur * S0
    extra_tax = (0.35 - 0.20) * dollar_value
    freed_up_usd = round(extra_tax, 2)

    # Final APV
    initial_invest_usd = C0_eur * S0
    apv = round(pv_operating + pv_dep + pv_loan_benefit + pv_interest_tax + freed_up_usd - initial_invest_usd, 2)

    # -------------------------
    # Results Section
    # -------------------------
    st.success("✅ APV Calculation Completed")

    st.subheader("💹 Summary of Results")
    colA, colB, colC = st.columns(3)
    colA.metric("After-tax Operating CFs", f"${pv_operating:,.2f}")
    colB.metric("Depreciation Tax Shields", f"${pv_dep:,.2f}")
    colC.metric("Concessional Loan Benefit", f"${pv_loan_benefit:,.2f}")
    colD, colE, colF = st.columns(3)
    colD.metric("Interest Tax Shields", f"${pv_interest_tax:,.2f}")
    colE.metric("Freed-up Funds", f"${freed_up_usd:,.2f}")
    colF.metric("Initial Investment", f"${initial_invest_usd:,.2f}")

    st.divider()
    st.markdown(f"### 🧮 **Final Adjusted Present Value (APV)** = `${apv:,.2f}`")

    df_186 = pd.DataFrame(rows_186, columns=["Year (t)", "S_t ($/€)", "Interest (€)", "λ/Project Debt Ratio", "Shield ($)", "PV ($)"])
    st.dataframe(df_186.style.format({"S_t ($/€)": "{:.4f}", "Interest (€)": "{:,.0f}", "Shield ($)": "{:,.0f}", "PV ($)": "{:,.0f}"}))

    st.info("💡 λ (project) is now dynamically calculated from optimal and actual debt ratios (no manual input).")

