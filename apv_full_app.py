
# apv_full_app.py
# Generic Streamlit App for APV Computation with All Exhibits (18.2–18.6)

import streamlit as st
import pandas as pd

st.set_page_config(page_title="APV Calculator", layout="wide")

st.title("💰 Adjusted Present Value (APV) Calculator")
st.caption("A comprehensive APV calculator with all key exhibits (18.2–18.6) based on user inputs.")

st.divider()
st.header("📥 Project Inputs")

col1, col2 = st.columns(2)
with col1:
    S0 = st.number_input("Exchange rate ($/€)", value=1.32, step=0.01)
    pi_f = st.number_input("Foreign inflation rate (%)", value=2.1) / 100
    pi_d = st.number_input("Domestic inflation rate (%)", value=3.0) / 100
    C0_eur = st.number_input("Initial project cost (€)", value=5_500_000.0, step=100_000.0)
    years = st.number_input("Project duration (years)", value=8, step=1)

with col2:
    tax = st.number_input("Corporate tax rate (%)", value=35.0) / 100
    K_ud = st.number_input("Unlevered cost of capital (%)", value=12.0) / 100
    i_c = st.number_input("Concessional loan rate (%)", value=5.0) / 100
    i_d = st.number_input("Domestic borrowing rate (%)", value=8.0) / 100

st.divider()
st.header("📊 Operating Parameters")

col3, col4 = st.columns(2)
with col3:
    units_y1 = st.number_input("Year 1 sales units", value=25000.0)
    units_growth = st.number_input("Annual sales unit growth (%)", value=12.0) / 100
    contrib_per_unit_eur_y1 = st.number_input("Contribution margin per unit (€)", value=40.0)
    contrib_growth = st.number_input("Annual growth in contribution margin (%)", value=2.1) / 100

with col4:
    lost_units_y1 = st.number_input("Year 1 lost sales units", value=9600.0)
    lost_units_growth = st.number_input("Annual growth in lost sales units (%)", value=5.0) / 100
    lost_margin_usd_y1 = st.number_input("Lost margin per unit ($)", value=35.0)
    lost_margin_growth = st.number_input("Annual growth in lost margin per unit (%)", value=3.0) / 100
    concession_loan_eur = st.number_input("Concessional loan amount (€)", value=4_000_000.0)

st.divider()

if st.button("📈 Calculate APV"):
    def S_t(t): return S0 * ((1 + pi_d) ** t) / ((1 + pi_f) ** t)
    depreciation_eur = C0_eur / years

    exhibit_182 = []
    pv_operating = 0.0
    for t in range(1, years + 1):
        cm_eur = contrib_per_unit_eur_y1 * ((1 + contrib_growth) ** (t - 1))
        qty = units_y1 * ((1 + units_growth) ** (t - 1))
        a_usd = S_t(t) * (qty * cm_eur)
        lost_q = lost_units_y1 * ((1 + lost_units_growth) ** t)
        lost_margin_usd_t = lost_margin_usd_y1 * ((1 + lost_margin_growth) ** t)
        b_usd = -lost_q * lost_margin_usd_t
        ocf = a_usd + b_usd
        ocf_aftertax = ocf * (1 - tax)
        pv = ocf_aftertax / ((1 + K_ud) ** t)
        pv_operating += pv
        exhibit_182.append([t, round(S_t(t), 3), round(cm_eur, 2), round(qty, 0), round(a_usd, 2),
                            round(lost_q, 0), round(b_usd, 2), round(ocf_aftertax, 2), round(pv, 2)])
    pv_operating = round(pv_operating, 2)
    df_182 = pd.DataFrame(exhibit_182, columns=[
        "Year", "Exchange Rate (Sₜ)", "€ Contribution/unit", "Quantity", "Revenue ($)",
        "Lost Units", "Lost Margin ($)", "After-tax OCF", "PV"
    ])

    exhibit_183 = []
    pv_dep = 0.0
    for t in range(1, years + 1):
        shield_usd = tax * depreciation_eur * S_t(t)
        pv = shield_usd / ((1 + i_d) ** t)
        pv_dep += pv
        exhibit_183.append([t, round(S_t(t), 3), round(shield_usd, 2), round(pv, 2)])
    pv_dep = round(pv_dep, 2)
    df_183 = pd.DataFrame(exhibit_183, columns=["Year", "Exchange Rate (Sₜ)", "Tax Shield ($)", "PV"])

    principal_payment = concession_loan_eur / years
    remaining = concession_loan_eur
    exhibit_185 = []
    pv_concess_payments = 0.0
    for t in range(1, years + 1):
        interest = remaining * i_c
        payment_usd = (principal_payment + interest) * S_t(t)
        pv = payment_usd / ((1 + i_d) ** t)
        pv_concess_payments += pv
        exhibit_185.append([t, round(remaining, 2), round(interest, 2),
                            round(payment_usd, 2), round(pv, 2)])
        remaining -= principal_payment
    pv_concess_payments = round(pv_concess_payments, 2)
    pv_loan_benefit = round(concession_loan_eur * S0 - pv_concess_payments, 2)
    df_185 = pd.DataFrame(exhibit_185, columns=[
        "Year", "Remaining Loan (€)", "Interest (€)", "Payment ($)", "PV"
    ])

    optimal_debt_ratio = (concession_loan_eur / C0_eur)
    lambda_project = optimal_debt_ratio / 0.40
    exhibit_186 = []
    remaining = concession_loan_eur
    pv_interest_tax = 0.0
    for t in range(1, years + 1):
        interest = remaining * i_c
        shield_usd = lambda_project * interest * tax * S_t(t)
        pv = shield_usd / ((1 + i_d) ** t)
        pv_interest_tax += pv
        exhibit_186.append([t, round(remaining, 2), round(interest, 2),
                            round(shield_usd, 2), round(pv, 2)])
        remaining -= principal_payment
    pv_interest_tax = round(pv_interest_tax, 2)
    df_186 = pd.DataFrame(exhibit_186, columns=[
        "Year", "Remaining Loan (€)", "Interest (€)", "Shield ($)", "PV"
    ])

    grossed_up = 750_000 / (1 - 0.20)
    freed_up_usd = (0.35 - 0.20) * grossed_up * S0

    initial_invest_usd = C0_eur * S0
    apv = round(pv_operating + pv_dep + pv_loan_benefit + pv_interest_tax + freed_up_usd - initial_invest_usd, 2)

    st.success("✅ APV Calculation Completed")
    st.subheader("💹 Exhibit 18.2 – After-Tax Operating Cash Flows")
    st.dataframe(df_182, use_container_width=True)
    st.markdown(f"**Total PV (Exhibit 18.2)**: `${pv_operating:,.2f}`")

    st.subheader("💹 Exhibit 18.3 – Depreciation Tax Shields")
    st.dataframe(df_183, use_container_width=True)
    st.markdown(f"**Total PV (Exhibit 18.3)**: `${pv_dep:,.2f}`")

    st.subheader("💹 Exhibit 18.5 – Benefit of Concessional Loan")
    st.dataframe(df_185, use_container_width=True)
    st.markdown(f"**Total PV of Concessional Loan Payments**: `${pv_concess_payments:,.2f}`")
    st.markdown(f"**Benefit (Exhibit 18.5)**: `${pv_loan_benefit:,.2f}`")

    st.subheader("💹 Exhibit 18.6 – Interest Tax Shields")
    st.dataframe(df_186, use_container_width=True)
    st.markdown(f"**Total PV (Exhibit 18.6)**: `${pv_interest_tax:,.2f}`")
    st.markdown(f"**Lambda (λ) calculated:** `{lambda_project:.2f}`")

    st.divider()
    st.subheader("📊 Final APV Summary")
    st.metric("After-tax Operating CFs", f"${pv_operating:,.2f}")
    st.metric("Depreciation Tax Shields", f"${pv_dep:,.2f}")
    st.metric("Concessional Loan Benefit", f"${pv_loan_benefit:,.2f}")
    st.metric("Interest Tax Shields", f"${pv_interest_tax:,.2f}")
    st.metric("Freed-up Affiliate Funds", f"${freed_up_usd:,.2f}")
    st.metric("Initial Investment (USD)", f"${initial_invest_usd:,.2f}")
    st.divider()
    st.markdown(f"### 🧮 **Final Adjusted Present Value (APV)** = `${apv:,.2f}`")
