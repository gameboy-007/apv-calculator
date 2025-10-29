import streamlit as st
import pandas as pd

st.set_page_config(page_title="APV Calculator with Exhibits", layout="wide")
st.title("💰 Adjusted Present Value (APV) Calculator — Full Exhibits Edition")

st.caption("This app replicates a full APV computation model including Exhibits 18.2 through 18.6 with dynamic input handling.")

st.divider()
st.header("📥 Input Parameters")

col1, col2 = st.columns(2)
with col1:
    S0 = st.number_input("Current exchange rate ($/€)", value=1.32, step=0.01)
    pi_f = st.number_input("Foreign inflation rate (%)", value=2.1, step=0.1) / 100
    pi_d = st.number_input("Domestic inflation rate (%)", value=3.0, step=0.1) / 100
    C0_eur = st.number_input("Initial project cost (€)", value=5_500_000.0, step=100_000.0)
    years = st.number_input("Project duration (years)", value=8, step=1)
    equity_cost = st.number_input("All-equity cost of capital (%)", value=12.0, step=0.1) / 100

with col2:
    tax = st.number_input("Corporate tax rate (%)", value=35.0, step=0.1) / 100
    i_c = st.number_input("Concessional loan rate (%)", value=5.0, step=0.1) / 100
    i_d = st.number_input("Domestic borrowing rate (%)", value=8.0, step=0.1) / 100
    concessional_loan_eur = st.number_input("Concessional loan amount (€)", value=4_000_000.0, step=100_000.0)
    borrowing_capacity_usd = st.number_input("Borrowing capacity created by project ($)", value=2_904_000.0, step=100_000.0)
    accumulated_funds_eur = st.number_input("Accumulated funds (€)", value=750_000.0, step=10_000.0)

st.divider()
st.header("📊 Operating Parameters")

col3, col4 = st.columns(2)
with col3:
    units_y1 = st.number_input("Year 1 sales units", value=25000.0, step=100.0)
    units_growth = st.number_input("Annual sales unit growth (%)", value=12.0, step=0.1) / 100
    price_y1 = st.number_input("Selling price per unit (€)", value=200.0, step=1.0)
    cost_y1 = st.number_input("Production cost per unit (€)", value=160.0, step=1.0)
    cost_growth = st.number_input("Annual cost growth rate (%)", value=2.1, step=0.1) / 100

with col4:
    lost_units_y1 = st.number_input("Year 1 lost sales units", value=9600.0, step=100.0)
    lost_units_growth = st.number_input("Lost sales growth rate (%)", value=5.0, step=0.1) / 100
    lost_margin_y1 = st.number_input("Lost sales margin per unit ($)", value=35.0, step=0.1)
    lost_margin_growth = st.number_input("Lost margin growth rate (%)", value=3.0, step=0.1) / 100

st.divider()
if st.button("📈 Calculate APV with Full Exhibits"):

    def S_t(t):
        return S0 * ((1 + pi_d) ** t) / ((1 + pi_f) ** t)

    depreciation_eur = C0_eur / years
    initial_invest_usd = S0 * C0_eur

    project_debt_ratio = concessional_loan_eur / C0_eur
    optimal_debt_ratio = borrowing_capacity_usd / (S0 * C0_eur)
    lambda_ratio = optimal_debt_ratio / project_debt_ratio

    exhibit_182 = []
    pv_operating = 0
    for t in range(1, years + 1):
        contrib_margin_eur = (price_y1 - cost_y1) * ((1 + cost_growth) ** (t - 1))
        qty = units_y1 * ((1 + units_growth) ** (t - 1))
        lost_units = lost_units_y1 * ((1 + lost_units_growth) ** t)
        lost_margin = lost_margin_y1 * ((1 + lost_margin_growth) ** t)
        revenue_usd = S_t(t) * (qty * contrib_margin_eur)
        lost_sales_usd = -lost_units * lost_margin
        ocf_usd = revenue_usd + lost_sales_usd
        ocf_after_tax = ocf_usd * (1 - tax)
        pv = ocf_after_tax / ((1 + equity_cost) ** t)
        pv_operating += pv
        exhibit_182.append([t, round(S_t(t),4), round(qty,0), round(contrib_margin_eur,2), round(lost_sales_usd,2), round(ocf_after_tax,2), round(pv,2)])

    exhibit_182_df = pd.DataFrame(exhibit_182, columns=["Year", "Sₜ", "Units", "CM/unit (€)", "Lost Sales ($)", "After-tax OCF ($)", "PV ($)"])

    exhibit_183 = []
    pv_dep = 0
    for t in range(1, years + 1):
        shield_usd = tax * depreciation_eur * S_t(t)
        pv = shield_usd / ((1 + i_d) ** t)
        pv_dep += pv
        exhibit_183.append([t, round(S_t(t),4), round(depreciation_eur,2), round(pv,2)])
    exhibit_183_df = pd.DataFrame(exhibit_183, columns=["Year", "Sₜ", "Depreciation (€)", "PV($)"])

    principal_payment = concessional_loan_eur / years
    remaining = concessional_loan_eur
    pv_concess_payments = 0
    for t in range(1, years + 1):
        interest = remaining * i_c
        payment_usd = (principal_payment + interest) * S_t(t)
        pv_concess_payments += payment_usd / ((1 + i_d) ** t)
        remaining -= principal_payment
    dollar_value_concession_loan = concessional_loan_eur * S0
    pv_loan_benefit = dollar_value_concession_loan - pv_concess_payments

    remaining = concessional_loan_eur
    exhibit_186 = []
    pv_interest_tax = 0
    for t in range(1, years + 1):
        interest = remaining * i_c
        shield_usd = S_t(t) * lambda_ratio * tax * interest
        pv = shield_usd / ((1 + i_d) ** t)
        pv_interest_tax += pv
        exhibit_186.append([t, round(S_t(t),4), round(interest,2), round(lambda_ratio,2), round(shield_usd,2), round(pv,2)])
        remaining -= principal_payment
    exhibit_186_df = pd.DataFrame(exhibit_186, columns=["Year","Sₜ","Interest (€)","λ/Project Debt","Shield ($)","PV($)"])

    gross_value = accumulated_funds_eur / (1 - 0.20)
    dollar_value = gross_value * S0
    freed_up_usd = 0.35 * (1 - 0.20) * dollar_value

    apv = pv_operating + pv_dep + pv_loan_benefit + pv_interest_tax + freed_up_usd - initial_invest_usd

    st.success("✅ APV Calculation Completed Successfully")

    st.subheader("📘 Exhibit 18.2 — Present Value of After-Tax Operating Cash Flows")
    st.dataframe(exhibit_182_df, hide_index=True)

    st.subheader("📘 Exhibit 18.3 — Depreciation Tax Shield")
    st.dataframe(exhibit_183_df, hide_index=True)

    st.subheader("📘 Exhibit 18.6 — Present Value of Interest Tax Shields")
    st.dataframe(exhibit_186_df, hide_index=True)

    st.markdown("### 💵 **Summary of Key Values**")
    st.write(f"- PV of Operating Cash Flows: **${pv_operating:,.0f}**")
    st.write(f"- PV of Depreciation Tax Shield: **${pv_dep:,.0f}**")
    st.write(f"- PV of Loan Benefit: **${pv_loan_benefit:,.0f}**")
    st.write(f"- PV of Interest Tax Shield: **${pv_interest_tax:,.0f}**")
    st.write(f"- Freed-up Funds: **${freed_up_usd:,.0f}**")
    st.write(f"- Initial Investment: **${initial_invest_usd:,.0f}**")

    st.markdown(f"## 🧮 Final Adjusted Present Value (APV) = **${apv:,.0f}**")
