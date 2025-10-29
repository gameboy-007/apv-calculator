import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# Streamlit App: Centralia-style Adjusted Present Value (APV)
# ------------------------------------------------------------
st.set_page_config(page_title="APV with Exhibits", layout="wide")
st.title("💰 Adjusted Present Value (APV) Calculator — Style")
st.caption("Interactive computation with automatically generated Exhibits 18.2–18.6")

# ---------------- Input Section ----------------
st.header("📥 Input Parameters")

col1, col2 = st.columns(2)
with col1:
    S0 = st.number_input("Current exchange rate ($/€)", value=1.32)
    pi_f = st.number_input("Foreign inflation rate (%)", value=2.1) / 100
    pi_d = st.number_input("Domestic inflation rate (%)", value=3.0) / 100
    C0_eur = st.number_input("Initial project cost (€)", value=5_500_000.0)
    borrow_capacity_usd = st.number_input("Borrowing capacity created ($)", value=2_904_000.0)
    years = st.number_input("Project duration (years)", value=8, step=1)
with col2:
    tax = st.number_input("Corporate tax rate (%)", value=35.0) / 100
    tax_foreign = st.number_input("Foreign tax rate (%)", value=20.0) / 100
    K_ud = st.number_input("Unlevered cost of capital (%)", value=12.0) / 100
    i_c = st.number_input("Concessional loan rate (%)", value=5.0) / 100
    i_d = st.number_input("Domestic borrowing rate (%)", value=8.0) / 100

st.divider()
st.header("📊 Operating Assumptions")

col3, col4 = st.columns(2)
with col3:
    units_y1 = st.number_input("Units sold in Year 1", value=25_000.0)
    units_growth = st.number_input("Annual growth in sales units (%)", value=12.0) / 100
    contrib_per_unit_y1 = st.number_input("Initial contribution margin per unit (€)", value=40.0)
    contrib_growth = st.number_input("Annual growth in contribution margin (%)", value=2.1) / 100
with col4:
    lost_units_y1 = st.number_input("Year 1 sales units", value=9_600.0)
    lost_units_growth = st.number_input("Annual growth in sales (%)", value=5.0) / 100
    lost_margin_y1 = st.number_input("margin per unit ($)", value=35.0)
    lost_margin_growth = st.number_input("Annual growth in margin (%)", value=3.0) / 100
    concessional_loan_eur = st.number_input("Concessional loan (€)", value=4_000_000.0)

if st.button("📈 Compute APV and Generate Exhibits"):
    # PPP exchange rate logic
    def S_t(t):
        return S0 * ((1 + pi_d) ** t) / ((1 + pi_f) ** t)

    depreciation_eur = C0_eur / years

    # Calculate λ and λ/project ratio
    initial_invest_usd = C0_eur * S0
    optimal_debt_ratio = borrow_capacity_usd / initial_invest_usd
    project_debt_ratio = concessional_loan_eur * S0 / initial_invest_usd
    lambda_ratio = round(optimal_debt_ratio / project_debt_ratio, 4)

    # ---------------- Exhibit 18.2 ----------------
    rows_182 = []
    pv_operating = 0.0
    for t in range(1, years + 1):
        cm_eur = contrib_per_unit_y1 * ((1 + contrib_growth) ** (t - 1))
        qty = units_y1 * ((1 + units_growth) ** (t - 1))
        a_usd = S_t(t) * qty * cm_eur

        lost_q = lost_units_y1 * ((1 + lost_units_growth) ** t)
        lost_margin_t = lost_margin_y1 * ((1 + lost_margin_growth) ** t)
        b_usd = -lost_q * lost_margin_t
        ocf_usd = a_usd + b_usd
        after_tax = ocf_usd * (1 - tax)
        pv = after_tax / ((1 + K_ud) ** t)
        pv_operating += pv
        rows_182.append([t, round(S_t(t),4), int(qty), round(a_usd,2), int(lost_q), round(b_usd,2), round(after_tax,2), round(pv,2)])
    df_182 = pd.DataFrame(rows_182, columns=["Year (t)", "S̄t", "Quantity", "S̄t × Quantity × CM(€)", "Lost Units", "Lost Sales ($)", "(1-τ)OCF", "(1-τ)OCF/(1+K_ud)^t"])

    # ---------------- Exhibit 18.3 ----------------
    rows_183, pv_dep = [], 0.0
    for t in range(1, years + 1):
        shield_usd = tax * depreciation_eur * S_t(t)
        pv = shield_usd / ((1 + i_d) ** t)
        pv_dep += pv
        rows_183.append([t, round(S_t(t),4), round(depreciation_eur,2), round(shield_usd,2), round(pv,2)])
    df_183 = pd.DataFrame(rows_183, columns=["Year (t)", "S̄t", "Dt (€)", "S̄tτDt ($)", "S̄tτDt/(1+i_d)^t"])

    # ---------------- Exhibit 18.6 ----------------
    principal_payment = concessional_loan_eur / years
    remaining, pv_interest_tax, rows_186 = concessional_loan_eur, 0.0, []
    for t in range(1, years + 1):
        interest = remaining * i_c
        shield_usd = S_t(t) * tax * lambda_ratio * interest
        pv = shield_usd / ((1 + i_d) ** t)
        pv_interest_tax += pv
        rows_186.append([t, round(S_t(t),4), round(interest,2), round(lambda_ratio,2), round(shield_usd,2), round(pv,2)])
        remaining -= principal_payment
    df_186 = pd.DataFrame(rows_186, columns=["Year (t)", "S̄t", "Interest (€)", "λ/Proj Ratio", "S̄tτλIt ($)", "S̄tτλIt/(1+i_d)^t"])

    # Freed-up affiliate funds logic
    affiliate_eur = 750_000
    grossup = affiliate_eur / (1 - tax_foreign)
    dollar_val = grossup * S0
    freed_up_usd = (tax - tax_foreign) * dollar_val

    # Final APV computation
    pv_operating, pv_dep, pv_interest_tax = round(pv_operating,2), round(pv_dep,2), round(pv_interest_tax,2)
    apv = round(pv_operating + pv_dep + pv_interest_tax + freed_up_usd - initial_invest_usd, 2)

    # ---------------- Output ----------------
    st.success("✅ APV and Exhibits Generated")

    st.subheader("📘 Exhibit 18.2 — PV of After-Tax Operating Cash Flows")
    st.dataframe(df_182, use_container_width=True)

    st.subheader("📘 Exhibit 18.3 — PV of Depreciation Tax Shields")
    st.dataframe(df_183, use_container_width=True)

    st.subheader("📘 Exhibit 18.6 — PV of Interest Tax Shields")
    st.dataframe(df_186, use_container_width=True)

    st.divider()
    st.markdown(f"### **Freed-up Affiliate Funds (USD):** ${freed_up_usd:,.2f}")
    st.markdown(f"### **Final Adjusted Present Value (APV):** ${apv:,.2f}")
    
    
    st.info("Made with ❤️ by Deepesh Pandey")
