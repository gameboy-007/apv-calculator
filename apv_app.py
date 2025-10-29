import streamlit as st
import pandas as pd

# --------------------------------------------------
# FINAL STREAMLIT APP: APV CALCULATOR
# --------------------------------------------------

st.set_page_config(page_title="APV Calculator (Style)", layout="centered")

st.title("💰 Adjusted Present Value (APV) Calculator")
st.caption("APV computation app with automated lambda and freed-up funds logic.")

st.divider()
st.header("📥 Project Input Parameters")

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
    borrowing_capacity_usd = st.number_input("Borrowing capacity (USD)", value=2_904_000.0, step=100_000.0)

st.divider()
st.header("📊 Operating Parameters")

col3, col4 = st.columns(2)
with col3:
    units_y1 = st.number_input("Year 1 sales units", value=25000.0, step=100.0)
    units_growth = st.number_input("Annual sales unit growth (%)", value=12.0, step=0.1) / 100
    selling_price = st.number_input("Selling price per unit (€)", value=200.0, step=1.0)
    production_cost = st.number_input("Production cost per unit (€)", value=160.0, step=1.0)
    contrib_growth = st.number_input("Annual price inflation (%)", value=2.1, step=0.1) / 100

with col4:
    lost_units_y1 = st.number_input("Year 1 sales units", value=9600.0, step=100.0)
    lost_units_growth = st.number_input("Annual growth in sales units (%)", value=5.0, step=0.1) / 100
    lost_margin_usd_y1 = st.number_input("margin per unit ($)", value=35.0, step=0.1)
    lost_margin_growth = st.number_input("Annual growth in margin (%)", value=3.0, step=0.1) / 100
    concession_loan_eur = st.number_input("Concessional loan amount (€)", value=4_000_000.0, step=100_000.0)

st.divider()
st.header("🏦 Affiliate and Tax Parameters")
affiliate_eur = st.number_input("Affiliate accumulated funds (€)", value=750_000.0, step=10_000.0)
affiliate_tax_rate = st.number_input("Affiliate prior tax rate (%)", value=20.0, step=0.1) / 100

# --------------------------------------------------
# COMPUTATION SECTION
# --------------------------------------------------
if st.button("📈 Calculate APV"):

    def S_t(t):
        return S0 * ((1 + pi_d) ** t) / ((1 + pi_f) ** t)

    depreciation_eur = C0_eur / years

    # Exhibit 18.2 - After-tax Operating CFs
    pv_operating = 0.0
    for t in range(1, years + 1):
        cm_eur = (selling_price - production_cost) * ((1 + contrib_growth) ** (t - 1))
        qty = units_y1 * ((1 + units_growth) ** (t - 1))
        a_usd = S_t(t) * qty * cm_eur
        lost_q = lost_units_y1 * ((1 + lost_units_growth) ** t)
        lost_margin_usd_t = lost_margin_usd_y1 * ((1 + lost_margin_growth) ** t)
        b_usd = -lost_q * lost_margin_usd_t
        ocf_aftertax = (a_usd + b_usd) * (1 - tax)
        pv_operating += ocf_aftertax / ((1 + K_ud) ** t)
    pv_operating = round(pv_operating, 2)

    # Exhibit 18.3 - Depreciation Tax Shields
    pv_dep = 0.0
    for t in range(1, years + 1):
        shield_usd = tax * depreciation_eur * S_t(t)
        pv_dep += shield_usd / ((1 + i_d) ** t)
    pv_dep = round(pv_dep, 2)

    # Exhibit 18.4–18.5 - Concessional Loan Benefit
    principal_payment = concession_loan_eur / years
    remaining = concession_loan_eur
    pv_concess_payments = 0.0
    for t in range(1, years + 1):
        interest = remaining * i_c
        payment_usd = (principal_payment + interest) * S_t(t)
        pv_concess_payments += payment_usd / ((1 + i_d) ** t)
        remaining -= principal_payment
    pv_concess_payments = round(pv_concess_payments, 2)
    pv_loan_benefit = round(concession_loan_eur * S0 - pv_concess_payments, 2)

    # Exhibit 18.6 - Interest Tax Shields
    project_cost_usd = C0_eur * S0
    loan_ratio = concession_loan_eur / C0_eur
    lambda_parent = borrowing_capacity_usd / project_cost_usd
    lambda_project = lambda_parent / loan_ratio

    remaining = concession_loan_eur
    pv_interest_tax = 0.0
    for t in range(1, years + 1):
        interest = remaining * i_c
        shield_usd = S_t(t) * interest * lambda_project * tax
        pv_interest_tax += shield_usd / ((1 + i_d) ** t)
        remaining -= principal_payment
    pv_interest_tax = round(pv_interest_tax, 2)

    # Freed-up affiliate funds (automatically calculated)
    grossed_eur = affiliate_eur / (1 - affiliate_tax_rate)
    grossed_usd = grossed_eur * S0
    extra_us_tax = (tax - affiliate_tax_rate) * grossed_usd
    freed_up_usd = round(extra_us_tax, 2)

    # Final APV Calculation
    initial_invest_usd = C0_eur * S0
    apv = round(pv_operating + pv_dep + pv_loan_benefit + pv_interest_tax + freed_up_usd - initial_invest_usd, 2)

    # --------------------------------------------------
    # OUTPUT SECTION
    # --------------------------------------------------
    st.success("✅ APV Calculation Completed Successfully")
    st.subheader("📘 Summary of Results")

    st.metric("PV (After-tax operating CFs)", f"${pv_operating:,.2f}")
    st.metric("PV (Depreciation tax shields)", f"${pv_dep:,.2f}")
    st.metric("PV (Concessional loan benefit)", f"${pv_loan_benefit:,.2f}")
    st.metric("PV (Interest tax shields)", f"${pv_interest_tax:,.2f}")
    st.metric("Freed-up affiliate funds", f"${freed_up_usd:,.2f}")
    st.metric("Initial investment (USD)", f"${initial_invest_usd:,.2f}")
    st.metric("Final Adjusted Present Value (APV)", f"${apv:,.2f}")

    st.info("💡 Tip: All values (λ, freed-up funds, exchange rates) are calculated dynamically using case logic.")
    st.info("Made with ❤️ by Deepesh Pandey")
