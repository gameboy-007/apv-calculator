import streamlit as st
import pandas as pd

# ---------------------------------------
# STREAMLIT APP: Centralia APV Calculator
# ---------------------------------------
st.set_page_config(page_title="Centralia APV Calculator", layout="centered")

st.title("💰 Adjusted Present Value (APV) Calculator – Centralia Style")
st.caption("Recreates the full Centralia case with correct λ, depreciation shields, and freed-up affiliate funds.")

st.divider()

# -------------------------------
# INPUT SECTION
# -------------------------------
st.header("📥 Project Input Parameters")

col1, col2 = st.columns(2)
with col1:
    S0 = st.number_input("Current exchange rate ($/€)", value=1.32, step=0.01)
    pi_f = st.number_input("Foreign inflation rate (%)", value=2.1, step=0.1) / 100
    pi_d = st.number_input("Domestic inflation rate (%)", value=3.0, step=0.1) / 100
    C0_eur = st.number_input("Initial project cost (€)", value=5_500_000.0, step=100_000.0)
    years = st.number_input("Project duration (years)", value=8, step=1)
    K_ud = st.number_input("Unlevered cost of capital (%)", value=12.0, step=0.1) / 100

with col2:
    tax = st.number_input("Corporate tax rate (%)", value=35.0, step=0.1) / 100
    i_c = st.number_input("Concessional loan rate (%)", value=5.0, step=0.1) / 100
    i_d = st.number_input("Domestic borrowing rate (%)", value=8.0, step=0.1) / 100
    concession_loan_eur = st.number_input("Concessional loan amount (€)", value=4_000_000.0, step=100_000.0)
    borrowing_capacity_usd = st.number_input("Borrowing capacity created by project ($)", value=2_904_000.0, step=100_000.0)
    affiliate_funds_eur = st.number_input("Affiliate funds accumulated (€)", value=750_000.0, step=50_000.0)
    foreign_tax_rate = st.number_input("Foreign (Spain) tax rate (%)", value=20.0, step=0.1) / 100

st.divider()
st.header("📊 Operating Parameters")

col3, col4 = st.columns(2)
with col3:
    units_y1 = st.number_input("Year 1 sales units", value=25_000.0, step=100.0)
    units_growth = st.number_input("Annual sales unit growth (%)", value=12.0, step=0.1) / 100
    price_y1 = st.number_input("Selling price per unit (€)", value=200.0, step=1.0)
    cost_y1 = st.number_input("Cost per unit (€)", value=160.0, step=1.0)
    price_growth = pi_f  # PPP assumption for inflation parity

with col4:
    lost_units_y1 = st.number_input("Year 1 lost sales units", value=9_600.0, step=100.0)
    lost_units_growth = st.number_input("Annual growth in lost sales units (%)", value=5.0, step=0.1) / 100
    lost_margin_usd_y1 = st.number_input("Lost margin per unit ($)", value=35.0, step=0.1)
    lost_margin_growth = st.number_input("Annual growth in lost margin (%)", value=3.0, step=0.1) / 100

st.divider()

# ----------------------------------
# CALCULATE BUTTON
# ----------------------------------
if st.button("📈 Calculate APV"):

    # Helper for PPP-based exchange rate
    def S_t(t):
        return S0 * ((1 + pi_d) ** t) / ((1 + pi_f) ** t)

    # Derived variables
    depreciation_eur = C0_eur / years
    contribution_margin_eur_y1 = price_y1 - cost_y1  # €40

    # -------- Exhibit 18.2: PV of After-tax Operating CFs --------
    pv_operating = 0.0
    exhibit_182 = []

    for t in range(1, years + 1):
        cm_eur = contribution_margin_eur_y1 * ((1 + pi_f) ** (t - 1))
        qty = units_y1 * ((1 + units_growth) ** (t - 1))
        a_usd = S_t(t) * (qty * cm_eur)

        lost_q = lost_units_y1 * ((1 + lost_units_growth) ** t)
        lost_margin_usd_t = lost_margin_usd_y1 * ((1 + lost_margin_growth) ** t)
        b_usd = -lost_q * lost_margin_usd_t

        ocf_usd = a_usd + b_usd
        ocf_aftertax = ocf_usd * (1 - tax)
        pv = ocf_aftertax / ((1 + K_ud) ** t)
        pv_operating += pv

        exhibit_182.append([t, round(S_t(t),4), round(a_usd,2), round(b_usd,2), round(ocf_usd,2), round(ocf_aftertax,2), round(pv,2)])

    pv_operating = round(pv_operating, 2)

    # -------- Exhibit 18.3: Depreciation Tax Shields --------
    pv_dep = 0.0
    exhibit_183 = []

    for t in range(1, years + 1):
        shield_usd = tax * depreciation_eur * S_t(t)
        pv = shield_usd / ((1 + i_d) ** t)
        pv_dep += pv
        exhibit_183.append([t, round(S_t(t),4), round(depreciation_eur,2), round(shield_usd,2), round(pv,2)])

    pv_dep = round(pv_dep, 2)

    # -------- Exhibit 18.4–18.5: Concessional Loan Benefit --------
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

    # -------- Exhibit 18.6: Interest Tax Shields --------
    project_debt_ratio = concession_loan_eur / C0_eur  # 72.73%
    optimal_debt_ratio = borrowing_capacity_usd / (C0_eur * S0)  # 40%
    lambda_project = optimal_debt_ratio / project_debt_ratio  # 0.55

    remaining = concession_loan_eur
    pv_interest_tax = 0.0
    for t in range(1, years + 1):
        interest = remaining * i_c
        shield_usd = lambda_project * interest * tax * S_t(t)
        pv_interest_tax += shield_usd / ((1 + i_d) ** t)
        remaining -= principal_payment
    pv_interest_tax = round(pv_interest_tax, 2)

    # -------- Freed-up Affiliate Funds --------
    grossed_eur = affiliate_funds_eur / (1 - foreign_tax_rate)
    grossed_usd = grossed_eur * S0
    freed_up_usd = (tax - foreign_tax_rate) * grossed_usd
    freed_up_usd = round(freed_up_usd, 2)

    # -------- Final APV Calculation --------
    initial_invest_usd = C0_eur * S0
    apv = round(pv_operating + pv_dep + pv_loan_benefit + pv_interest_tax + freed_up_usd - initial_invest_usd, 2)

    # ----------------------------
    # DISPLAY RESULTS
    # ----------------------------
    st.success("✅ APV Calculation Completed")

    st.metric("After-tax Operating CFs (Exh. 18.2)", f"${pv_operating:,.2f}")
    st.metric("Depreciation Tax Shields (Exh. 18.3)", f"${pv_dep:,.2f}")
    st.metric("Concessional Loan Benefit (Exh. 18.5)", f"${pv_loan_benefit:,.2f}")
    st.metric("Interest Tax Shields (Exh. 18.6)", f"${pv_interest_tax:,.2f}")
    st.metric("Freed-up Affiliate Funds", f"${freed_up_usd:,.2f}")
    st.metric("Initial Investment", f"${initial_invest_usd:,.2f}")

    st.divider()
    st.markdown(f"### 🧮 **Final Adjusted Present Value (APV)** = `${apv:,.2f}`")
    st.info(" \n\n\n Created with ❤️ by Deepesh Pandey.")
