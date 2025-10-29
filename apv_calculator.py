
import streamlit as st

st.set_page_config(page_title="APV Calculator", page_icon="💰")

st.title("💰 Adjusted Present Value (APV) Calculator")
st.write("Use this tool to compute the Adjusted Present Value (APV) for international investment projects using given inflation and PPP-based spot rates.")

# ---- INPUTS ----
st.header("📥 Project Inputs")

col1, col2 = st.columns(2)

with col1:
    project_life = st.number_input("Project Life (years)", value=8)
    unlevered_discount_rate = st.number_input("Unlevered Cost of Capital (%)", value=11.0) / 100
    tax_rate = st.number_input("Corporate Tax Rate (%)", value=35.0) / 100
    domestic_inflation = st.number_input("Home Inflation Rate (%)", value=3.0) / 100
    foreign_inflation = st.number_input("Foreign Inflation Rate (%)", value=3.1) / 100

with col2:
    initial_spot_rate = st.number_input("Current Spot Rate (Home per Foreign)", value=0.90)
    price_per_unit = st.number_input("Selling Price per Unit (foreign currency)", value=200.0)
    cost_per_unit = st.number_input("Cost per Unit (foreign currency)", value=160.0)
    units_sold = st.number_input("Units Sold (Year 1)", value=28000)
    investment_cost = st.number_input("Initial Investment (foreign currency)", value=4920000.0)

st.header("🏦 Financing Details")
col3, col4 = st.columns(2)

with col3:
    concessionary_loan = st.number_input("Concessionary Loan Amount (foreign currency)", value=3500000.0)
    concessionary_interest_rate = st.number_input("Concessionary Loan Interest Rate (%)", value=6.0) / 100

with col4:
    market_interest_rate = st.number_input("Market Interest Rate on Comparable Debt (%)", value=9.0) / 100
    salvage_value = st.number_input("Salvage Value at End (foreign currency)", value=0.0)

# ---- CALCULATE ----
if st.button("Calculate APV"):
    # Revenue and cost in foreign currency
    annual_revenue_fc = price_per_unit * units_sold
    annual_cost_fc = cost_per_unit * units_sold

    # PPP-adjusted expected spot rate
    expected_spot_rate = initial_spot_rate * ((1 + domestic_inflation) / (1 + foreign_inflation)) ** project_life

    # Convert to home currency
    annual_revenue_home = annual_revenue_fc * initial_spot_rate
    annual_cost_home = annual_cost_fc * initial_spot_rate
    depreciation = investment_cost / project_life
    ebit = annual_revenue_home - annual_cost_home - (depreciation * initial_spot_rate)
    tax = ebit * tax_rate
    after_tax_cf = ebit - tax + (depreciation * initial_spot_rate)

    # PV of base case cash flows
    base_pv = after_tax_cf * ((1 - (1 + unlevered_discount_rate) ** -project_life) / unlevered_discount_rate)

    # Tax shield from concessionary loan
    annual_interest = concessionary_loan * concessionary_interest_rate
    tax_shield = annual_interest * tax_rate
    pv_tax_shield = tax_shield * ((1 - (1 + unlevered_discount_rate) ** -project_life) / unlevered_discount_rate)

    # APV calculation
    apv = base_pv + pv_tax_shield - (investment_cost * initial_spot_rate)

    # ---- OUTPUT ----
    st.header("📊 Results Summary")
    st.write(f"**Expected Spot Rate (PPP-adjusted):** {expected_spot_rate:.4f}")
    st.write(f"**Annual Revenue (Home Currency):** ${annual_revenue_home:,.2f}")
    st.write(f"**Annual Cost (Home Currency):** ${annual_cost_home:,.2f}")
    st.write(f"**Depreciation (Home Currency):** ${depreciation * initial_spot_rate:,.2f}")
    st.write(f"**EBIT (Year 1):** ${ebit:,.2f}")
    st.write(f"**After-Tax Cash Flow (Year 1):** ${after_tax_cf:,.2f}")
    st.write(f"**Present Value of Base Case Cash Flows:** ${base_pv:,.2f}")
    st.write(f"**PV of Tax Shield:** ${pv_tax_shield:,.2f}")
    st.success(f"### ✅ Adjusted Present Value (APV): ${apv:,.2f}")

    if apv > 0:
        st.success("💡 The project is **financially viable** (positive APV).")
    else:
        st.error("⚠️ The project is **not financially viable** (negative APV).")
