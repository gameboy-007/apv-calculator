
import streamlit as st
import pandas as pd

# -------------------------------------------------
# APV Calculator (Full Exhibits)
# -------------------------------------------------
st.set_page_config(page_title="APV Calculator (Full Exhibits)", layout="wide")
st.title("💰 Adjusted Present Value (APV) Calculator — Full Exhibits")
st.caption("Includes Exhibits 18.2–18.6 with automatic Freed-Up Affiliate Fund computation.")

st.divider()
st.header("📥 Input Parameters")

# --- Input Section ---
col1, col2 = st.columns(2)
with col1:
    S0 = st.number_input("Current exchange rate ($/€)", value=1.32, step=0.01)
    pi_f = st.number_input("Foreign inflation rate (%)", value=2.1, step=0.1) / 100
    pi_d = st.number_input("Domestic inflation rate (%)", value=3.0, step=0.1) / 100
    C0_eur = st.number_input("Initial project cost (€)", value=5500000.0, step=100000.0)
    years = st.number_input("Project duration (years)", value=8, step=1)
    contrib_per_unit_eur_y1 = st.number_input("Contribution per unit (€)", value=40.0, step=0.1)
    current_cost_per_unit_eur = st.number_input("Production cost per unit (€)", value=160.0, step=1.0)

with col2:
    tax_us = st.number_input("US corporate tax rate (%)", value=35.0, step=0.1) / 100
    tax_foreign = st.number_input("Affiliate (foreign) tax rate (%)", value=20.0, step=0.1) / 100
    K_ud = st.number_input("Unlevered cost of capital (%)", value=12.0, step=0.1) / 100
    i_c = st.number_input("Concessional loan rate (%)", value=6.0, step=0.1) / 100
    i_d = st.number_input("Domestic borrowing rate (%)", value=8.0, step=0.1) / 100
    concession_loan_eur = st.number_input("Concessional loan (€)", value=4000000.0, step=100000.0)

st.divider()
st.header("📊 Operating Assumptions")

col3, col4 = st.columns(2)
with col3:
    units_y1 = st.number_input("Year 1 Sales Units", value=28000.0, step=500.0)
    units_growth = st.number_input("Annual Unit Growth (%)", value=12.0, step=0.1) / 100
    contrib_growth = st.number_input("Annual Contribution Growth (%)", value=3.1, step=0.1) / 100

with col4:
    lost_units_y1 = st.number_input("Year 1 Export Units", value=9600.0, step=100.0)
    lost_units_growth = st.number_input("Export Growth (%)", value=5.0, step=0.1) / 100
    lost_margin_usd_y1 = st.number_input("Year 1 Margin per Unit ($)", value=35.0, step=0.1)
    lost_margin_growth = st.number_input("Margin Growth (%)", value=3.0, step=0.1) / 100

if st.button("📈 Calculate Full APV"):

    def S_t(t):
        return S0 * ((1 + pi_d) ** t) / ((1 + pi_f) ** t)

    depreciation_eur = C0_eur / years

    # ---------- Exhibit 18.2 ----------
    exhibit_182 = []
    pv_operating = 0.0
    for t in range(1, years + 1):
        cm_eur = contrib_per_unit_eur_y1 * ((1 + contrib_growth) ** (t - 1))
        qty = units_y1 * ((1 + units_growth) ** (t - 1))
        lost_q = lost_units_y1 * ((1 + lost_units_growth) ** t)
        lost_margin_usd_t = lost_margin_usd_y1 * ((1 + lost_margin_growth) ** t)
        a_usd = S_t(t) * (qty * cm_eur)
        b_usd = -lost_q * lost_margin_usd_t
        ocf_usd = a_usd + b_usd
        ocf_aftertax = ocf_usd * (1 - tax_us)
        pv = ocf_aftertax / ((1 + K_ud) ** t)
        exhibit_182.append([t, round(S_t(t),4), round(cm_eur,2), int(qty), round(a_usd,2), round(b_usd,2), round(ocf_usd,2), round(ocf_aftertax,2), round(pv,2)])
        pv_operating += pv

    df_182 = pd.DataFrame(exhibit_182, columns=["Year","S_t ($/€)","€CM/unit","Qty","Sales(USD)=S_t×Qty×CM","Lost Sales","OCF","OCF(1−t)","PV@Kud"])

    # ---------- Exhibit 18.3 ----------
    exhibit_183 = []
    pv_dep = 0.0
    for t in range(1, years + 1):
        shield_usd = tax_us * depreciation_eur * S_t(t)
        pv = shield_usd / ((1 + i_d) ** t)
        exhibit_183.append([t, round(S_t(t),4), round(depreciation_eur,2), round(shield_usd,2), round(pv,2)])
        pv_dep += pv
    df_183 = pd.DataFrame(exhibit_183, columns=["Year","S_t ($/€)","Depreciation (€)","Tax Shield ($)","PV @ 8% ($)"])

    # ---------- Exhibit 18.5 ----------
    exhibit_185 = []
    principal_payment = concession_loan_eur / years
    remaining = concession_loan_eur
    pv_concess_payments = 0.0
    for t in range(1, years + 1):
        interest = remaining * i_c
        payment_eur = principal_payment + interest
        payment_usd = payment_eur * S_t(t)
        pv = payment_usd / ((1 + i_d) ** t)
        exhibit_185.append([t, round(remaining,2), round(interest,2), round(principal_payment,2), round(payment_eur,2), round(S_t(t),4), round(payment_usd,2), round(pv,2)])
        pv_concess_payments += pv
        remaining -= principal_payment
    df_185 = pd.DataFrame(exhibit_185, columns=["Year","Remaining (€)","Interest (€)","Principal (€)","Payment (€)","S_t ($/€)","Payment ($)","PV @ 8% ($)"])

    dollar_value_concession_loan = concession_loan_eur * S0
    pv_loan_benefit = round(dollar_value_concession_loan - pv_concess_payments, 2)

    # ---------- Exhibit 18.6 ----------
    optimal_debt_ratio = concession_loan_eur / C0_eur
    lambda_project = 0.40 / optimal_debt_ratio
    exhibit_186 = []
    remaining = concession_loan_eur
    pv_interest_tax = 0.0
    for t in range(1, years + 1):
        interest = remaining * i_c
        shield_usd = lambda_project * interest * tax_us * S_t(t)
        pv = shield_usd / ((1 + i_d) ** t)
        exhibit_186.append([t, round(S_t(t),4), round(interest,2), round(shield_usd,2), round(pv,2)])
        pv_interest_tax += pv
        remaining -= principal_payment
    df_186 = pd.DataFrame(exhibit_186, columns=["Year","S_t ($/€)","Interest (€)","Tax Shield ($)=λ×Interest×t×S_t","PV @ 8% ($)"])

    # ---------- Freed-up Affiliate Funds ----------
    affiliate_retained = 550000.0
    gross = affiliate_retained / (1 - tax_foreign)
    freed_up_usd = (tax_us - tax_foreign) * S0 * gross

    # ---------- Final APV ----------
    pv_operating = round(pv_operating, 2)
    pv_dep = round(pv_dep, 2)
    pv_interest_tax = round(pv_interest_tax, 2)
    initial_invest_usd = C0_eur * S0
    apv = round(pv_operating + pv_dep + pv_loan_benefit + pv_interest_tax + freed_up_usd - initial_invest_usd, 2)

    # ---------- Display Results ----------
    st.success("✅ APV Calculation Completed")

    st.subheader("Exhibit 18.2 — After-Tax Operating Cash Flows")
    st.dataframe(df_182, use_container_width=True)

    st.subheader("Exhibit 18.3 — Depreciation Tax Shields")
    st.dataframe(df_183, use_container_width=True)

    st.subheader("Exhibit 18.5 — Concessional Loan Benefit")
    st.dataframe(df_185, use_container_width=True)

    st.subheader("Exhibit 18.6 — Interest Tax Shields")
    st.dataframe(df_186, use_container_width=True)

    st.divider()
    st.subheader("📊 Final APV Summary")
    st.metric("PV (Operating CFs)", f"${pv_operating:,.2f}")
    st.metric("PV (Depreciation Shields)", f"${pv_dep:,.2f}")
    st.metric("PV (Loan Benefit)", f"${pv_loan_benefit:,.2f}")
    st.metric("PV (Interest Shields)", f"${pv_interest_tax:,.2f}")
    st.metric("Freed-Up Affiliate Funds", f"${freed_up_usd:,.2f}")
    st.metric("Initial Investment (USD)", f"${initial_invest_usd:,.2f}")
    st.metric("💰 Final APV", f"${apv:,.2f}")

    
    st.info("Made with ❤️ by Deepesh Pandey")
