# apv_streamlit_final.py
# Streamlit App: APV Calculator (Centralia-style) with auto-calculated freed-up funds

import streamlit as st

# ----------------------------------------
# STREAMLIT APP CONFIG
# ----------------------------------------
st.set_page_config(page_title="APV Calculator (Centralia Style)", layout="centered")

st.title("💰 Adjusted Present Value (APV) Calculator")
st.caption("Centralia-style APV computation app with automatic freed-up fund calculation.")

st.divider()

# ----------------------------------------
# INPUT SECTION
# ----------------------------------------
st.header("📥 Project Input Parameters")

col1, col2 = st.columns(2)
with col1:
    S0 = st.number_input("Current exchange rate ($/€)", value=1.32, step=0.01)
    pi_f = st.number_input("Foreign inflation rate (%)", value=2.1, step=0.1) / 100
    pi_d = st.number_input("Domestic inflation rate (%)", value=3.0, step=0.1) / 100
    C0_eur = st.number_input("Initial project cost (€)", value=5_500_000.0, step=100_000.0)
    years = st.number_input("Project duration (years)", value=8, step=1)

with col2:
    tax_us = st.number_input("US (Parent) tax rate (%)", value=35.0, step=0.1) / 100
    tax_foreign = st.number_input("Foreign (Affiliate) tax rate (%)", value=20.0, step=0.1) / 100
    K_ud = st.number_input("Unlevered cost of capital (%)", value=12.0, step=0.1) / 100
    i_c = st.number_input("Concessional loan rate (%)", value=5.0, step=0.1) / 100
    i_d = st.number_input("Domestic borrowing rate (%)", value=8.0, step=0.1) / 100
    lambda_project = st.number_input("Lambda (interest tax shield fraction)", value=0.55, step=0.01)

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
    lost_margin_growth = st.number_input("Annual growth in lost margin per unit (%)", value=3.0, step=0.1) / 100
    concession_loan_eur = st.number_input("Concessional loan amount (€)", value=4_000_000.0, step=100_000.0)

affiliate_amount = st.number_input("After-tax affiliate amount (€)", value=750_000.0, step=10_000.0)

# ----------------------------------------
# COMPUTATION SECTION
# ----------------------------------------
st.divider()
if st.button("📈 Calculate APV"):

    def S_t(t):
        return S0 * ((1 + pi_d) ** t) / ((1 + pi_f) ** t)

    depreciation_eur = C0_eur / years

    # Exhibit 18.2 - PV of after-tax operating CF
    pv_operating = 0.0
    for t in range(1, years + 1):
        cm_eur = contrib_per_unit_eur_y1 * ((1 + contrib_growth) ** (t - 1))
        qty = units_y1 * ((1 + units_growth) ** (t - 1))
        a_usd = S_t(t) * (qty * cm_eur)
        lost_q = lost_units_y1 * ((1 + lost_units_growth) ** t)
        lost_margin_usd_t = lost_margin_usd_y1 * ((1 + lost_margin_growth) ** t)
        b_usd = -lost_q * lost_margin_usd_t
        ocf_usd = a_usd + b_usd
        ocf_aftertax = ocf_usd * (1 - tax_us)
        pv_operating += ocf_aftertax / ((1 + K_ud) ** t)
    pv_operating = round(pv_operating, 2)

    # Exhibit 18.3 - Depreciation tax shield
    pv_dep = 0.0
    for t in range(1, years + 1):
        shield_usd = tax_us * depreciation_eur * S_t(t)
        pv_dep += shield_usd / ((1 + i_d) ** t)
    pv_dep = round(pv_dep, 2)

    # Exhibit 18.4/5 - Concessional loan benefit
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

    # Exhibit 18.6 - Interest tax shield
    remaining = concession_loan_eur
    pv_interest_tax = 0.0
    for t in range(1, years + 1):
        interest = remaining * i_c
        shield_usd = lambda_project * interest * tax_us * S_t(t)
        pv_interest_tax += shield_usd / ((1 + i_d) ** t)
        remaining -= principal_payment
    pv_interest_tax = round(pv_interest_tax, 2)

    # Freed-up affiliate funds (automatically calculated)
    gross_affiliate_value = affiliate_amount / (1 - tax_foreign)
    freed_up_usd = (tax_us - tax_foreign) * S0 * gross_affiliate_value
    freed_up_usd = round(freed_up_usd, 2)

    # Final APV
    initial_invest_usd = C0_eur * S0
    apv = round(pv_operating + pv_dep + pv_loan_benefit + pv_interest_tax + freed_up_usd - initial_invest_usd, 2)

    # ----------------------------------------
    # RESULTS SECTION
    # ----------------------------------------
    st.success("✅ APV Calculation Completed")

    st.subheader("💹 Summary of Results")

    colA, colB, colC = st.columns(3)
    colA.metric("After-tax Operating CFs", f"${pv_operating:,.2f}")
    colB.metric("Depreciation Tax Shields", f"${pv_dep:,.2f}")
    colC.metric("Concessional Loan Benefit", f"${pv_loan_benefit:,.2f}")

    colD, colE, colF = st.columns(3)
    colD.metric("Interest Tax Shields", f"${pv_interest_tax:,.2f}")
    colE.metric("Freed-up Affiliate Funds", f"${freed_up_usd:,.2f}")
    colF.metric("Initial Investment", f"${initial_invest_usd:,.2f}")

    st.divider()
    st.markdown(f"### 🧮 **Final Adjusted Present Value (APV)** = `${apv:,.2f}`")

    st.info("💡 Tip: You can test sensitivity by adjusting inflation, growth, and interest rates.")
