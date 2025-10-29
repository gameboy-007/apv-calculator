import streamlit as st
import pandas as pd

# -----------------------------------
# FINAL STREAMLIT APP: APV WITH EXHIBITS 18.2–18.6
# -----------------------------------

st.set_page_config(page_title="APV Calculator with Exhibits", layout="wide")

st.title("💰 Adjusted Present Value (APV) Calculator — Case")
st.caption("Includes Exhibits 18.2 to 18.6 with labeled columns and formulas.")
st.divider()

# -----------------------------------
# INPUT SECTION
# -----------------------------------

st.header("📥 Project & Financial Parameters")
col1, col2 = st.columns(2)
with col1:
    S0 = st.number_input("Current exchange rate ($/€)", value=1.32, step=0.01)
    pi_f = st.number_input("Foreign inflation rate (%)", value=2.1, step=0.1)/100
    pi_d = st.number_input("Domestic inflation rate (%)", value=3.0, step=0.1)/100
    C0_eur = st.number_input("Initial project cost (€)", value=5_500_000.0, step=100_000.0)
    years = st.number_input("Project duration (years)", value=8, step=1)
with col2:
    tax = st.number_input("Corporate tax rate (%)", value=35.0, step=0.1)/100
    K_ud = st.number_input("Unlevered cost of capital (%)", value=12.0, step=0.1)/100
    i_c = st.number_input("Concessional loan rate (%)", value=5.0, step=0.1)/100
    i_d = st.number_input("Domestic borrowing rate (%)", value=8.0, step=0.1)/100
    affiliate_tax = st.number_input("Affiliate prior tax rate (%)", value=20.0, step=0.1)/100

st.divider()

st.header("📊 Operating Parameters")
col3, col4 = st.columns(2)
with col3:
    units_y1 = st.number_input("Year 1 sales units", value=25000.0, step=100.0)
    units_growth = st.number_input("Annual sales unit growth (%)", value=12.0, step=0.1)/100
    contrib_per_unit_eur_y1 = st.number_input("Contribution margin per unit (€)", value=40.0, step=0.1)
    contrib_growth = st.number_input("Annual growth in contribution margin (%)", value=2.1, step=0.1)/100
with col4:
    lost_units_y1 = st.number_input("Year 1 sales units", value=9600.0, step=100.0)
    lost_units_growth = st.number_input("Annual growth in sales units (%)", value=5.0, step=0.1)/100
    lost_margin_usd_y1 = st.number_input("Year 1 margin per unit ($)", value=35.0, step=0.1)
    lost_margin_growth = st.number_input("Annual growth in margin per unit (%)", value=3.0, step=0.1)/100
    concession_loan_eur = st.number_input("Concessional loan amount (€)", value=4_000_000.0, step=100_000.0)

# -----------------------------------
# COMPUTATION SECTION
# -----------------------------------

def S_t(t):
    return S0 * ((1 + pi_d) ** t) / ((1 + pi_f) ** t)

def compute_exhibits():
    depreciation_eur = C0_eur / years

    # Exhibit 18.2 – After-tax Operating CFs
    ex182, pv_operating = [], 0
    for t in range(1, years + 1):
        cm_eur = contrib_per_unit_eur_y1 * ((1 + contrib_growth) ** (t - 1))
        qty = units_y1 * ((1 + units_growth) ** (t - 1))
        a_usd = S_t(t) * qty * cm_eur

        lost_q = lost_units_y1 * ((1 + lost_units_growth) ** t)
        lost_margin_usd_t = lost_margin_usd_y1 * ((1 + lost_margin_growth) ** t)
        b_usd = -lost_q * lost_margin_usd_t

        ocf_usd = a_usd + b_usd
        ocf_aftertax = ocf_usd * (1 - tax)
        pv = ocf_aftertax / ((1 + K_ud) ** t)
        pv_operating += pv

        ex182.append([t, round(S_t(t), 4), round(qty, 2), round(cm_eur, 2), round(a_usd, 2), round(lost_q, 2), round(lost_margin_usd_t, 2), round(b_usd, 2), round(ocf_usd, 2), round(ocf_aftertax, 2), round(pv, 2)])

    df182 = pd.DataFrame(ex182, columns=["Year", "Sₜ ($/€)", "Qty", "CM €/unit", "Sales ($)", "Lost Qty", "Lost Margin $/unit", "Lost Sales ($)", "OCF ($)", "After-tax OCF ($)", "PV OCF ($)"])

    # Exhibit 18.3 – Depreciation Tax Shields
    ex183, pv_dep = [], 0
    for t in range(1, years + 1):
        shield_usd = tax * depreciation_eur * S_t(t)
        pv = shield_usd / ((1 + i_d) ** t)
        pv_dep += pv
        ex183.append([t, round(S_t(t),4), round(depreciation_eur,2), round(shield_usd,2), round(pv,2)])

    df183 = pd.DataFrame(ex183, columns=["Year", "Sₜ ($/€)", "Depreciation (€)", "Tax Shield ($)", "PV @ i_d ($)"])

    # Exhibit 18.5 – Concessional Loan Benefit
    principal_payment = concession_loan_eur / years
    remaining = concession_loan_eur
    ex185, pv_concess_payments = [], 0
    for t in range(1, years + 1):
        interest = remaining * i_c
        payment_eur = principal_payment + interest
        payment_usd = payment_eur * S_t(t)
        pv = payment_usd / ((1 + i_d) ** t)
        pv_concess_payments += pv
        ex185.append([t, round(remaining,2), round(interest,2), round(principal_payment,2), round(payment_eur,2), round(S_t(t),4), round(payment_usd,2), round(pv,2)])
        remaining -= principal_payment

    df185 = pd.DataFrame(ex185, columns=["Year", "Remaining (€)", "Interest (€)", "Principal (€)", "Payment (€)", "Sₜ ($/€)", "Payment ($)", "PV @ i_d ($)"])

    dollar_value_concession_loan = concession_loan_eur * S0
    pv_loan_benefit = round(dollar_value_concession_loan - pv_concess_payments, 2)

    # Exhibit 18.6 – Interest Tax Shields
    remaining = concession_loan_eur
    project_debt_ratio = concession_loan_eur / C0_eur
    lambda_value = 0.40 / project_debt_ratio
    ex186, pv_interest_tax = [], 0
    for t in range(1, years + 1):
        interest = remaining * i_c
        shield_usd = lambda_value * interest * tax * S_t(t)
        pv = shield_usd / ((1 + i_d) ** t)
        pv_interest_tax += pv
        ex186.append([t, round(S_t(t),4), round(interest,2), round(lambda_value,2), round(shield_usd,2), round(pv,2)])
        remaining -= principal_payment

    df186 = pd.DataFrame(ex186, columns=["Year", "Sₜ ($/€)", "Interest (€)", "Lambda", "Shield ($)", "PV @ i_d ($)"])

    # Freed-up affiliate funds (automatic)
    affiliate_after_tax_retained = 550_000
    freed_up_usd = (tax - affiliate_tax) * (affiliate_after_tax_retained / (1 - affiliate_tax)) * S0

    # Final APV
    initial_invest_usd = C0_eur * S0
    apv = pv_operating + pv_dep + pv_loan_benefit + pv_interest_tax + freed_up_usd - initial_invest_usd

    return df182, df183, df185, df186, pv_operating, pv_dep, pv_loan_benefit, pv_interest_tax, freed_up_usd, initial_invest_usd, apv

if st.button("📈 Calculate and Show Exhibits"):
    df182, df183, df185, df186, pv_operating, pv_dep, pv_loan_benefit, pv_interest_tax, freed_up_usd, initial_invest_usd, apv = compute_exhibits()

    st.success("✅ All Exhibits Calculated Successfully")

    st.subheader("📘 Exhibit 18.2 — After-tax Operating Cash Flows")
    st.dataframe(df182, use_container_width=True)

    st.subheader("📘 Exhibit 18.3 — Depreciation Tax Shields")
    st.dataframe(df183, use_container_width=True)

    st.subheader("📘 Exhibit 18.5 — Concessional Loan Payments and Benefit")
    st.dataframe(df185, use_container_width=True)

    st.subheader("📘 Exhibit 18.6 — Interest Tax Shields")
    st.dataframe(df186, use_container_width=True)

    st.divider()

    st.header("📊 Final APV Summary")
    summary = {
        "PV (Operating CFs)": pv_operating,
        "PV (Depreciation Shields)": pv_dep,
        "PV (Loan Benefit)": pv_loan_benefit,
        "PV (Interest Shields)": pv_interest_tax,
        "Freed-Up Affiliate Funds": freed_up_usd,
        "Initial Investment (USD)": initial_invest_usd,
        "Final APV": apv
    }
    st.dataframe(pd.DataFrame(summary.items(), columns=["Component", "Value ($)"]), use_container_width=True)
    st.markdown(f"### 💰 **Final Adjusted Present Value (APV): ${apv:,.2f}**")

    st.out("Made with ❤️ by Deepesh Pandey")