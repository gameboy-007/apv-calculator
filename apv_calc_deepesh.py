
import streamlit as st
import numpy as np

st.title("Adjusted Present Value (APV) Calculator")

st.header("Project Inputs")
project_life = st.number_input("Project Life (years)", min_value=1, value=8)
initial_investment = st.number_input("Initial Investment ($ million)", min_value=0.0, value=80.0)
contribution_margin = st.number_input("Contribution Margin per unit ($)", min_value=0.0, value=40.0)
growth_rate = st.number_input("Growth rate in Contribution Margin (%)", min_value=0.0, value=2.1) / 100
units_sold = st.number_input("Initial Units Sold (million)", min_value=0.0, value=1.0)
fixed_costs = st.number_input("Annual Fixed Costs ($ million)", min_value=0.0, value=20.0)
tax_rate = st.number_input("Corporate Tax Rate (%)", min_value=0.0, value=35.0) / 100
unlevered_cost_of_equity = st.number_input("Unlevered Cost of Equity (%)", min_value=0.0, value=10.0) / 100
debt_ratio = st.number_input("Debt-to-Value Ratio (%)", min_value=0.0, value=40.0) / 100
cost_of_debt = st.number_input("Cost of Debt (%)", min_value=0.0, value=6.0) / 100

# Step 1: Calculate after-tax cash flows
st.header("Exhibit 1: Unlevered Free Cash Flow Calculation")
cash_flows = []
for t in range(1, int(project_life)+1):
    revenue = contribution_margin * (1 + growth_rate)**(t-1) * units_sold
    ebit = revenue - fixed_costs
    taxes = ebit * tax_rate
    ufcf = ebit - taxes
    cash_flows.append(ufcf)

cf_table = {f"Year {t+1}": round(cash_flows[t], 2) for t in range(len(cash_flows))}
st.write(cf_table)

# Step 2: Base case NPV (unlevered)
discount_factors = [(1 + unlevered_cost_of_equity)**t for t in range(1, len(cash_flows)+1)]
pv_unlevered = [cash_flows[t] / discount_factors[t] for t in range(len(cash_flows))]
base_case_npv = sum(pv_unlevered) - initial_investment

# Step 3: PV of Tax Shield
st.header("Exhibit 2: Present Value of Tax Shield")
interest_tax_shield = (initial_investment * debt_ratio * cost_of_debt * tax_rate)
pv_tax_shield = interest_tax_shield * (1 - (1 + cost_of_debt)**(-project_life)) / cost_of_debt

# Step 4: Final APV
apv = base_case_npv + pv_tax_shield

st.subheader("Results Summary")
st.write(f"**Base Case (Unlevered) NPV:** ${base_case_npv:.2f} million")
st.write(f"**Present Value of Tax Shield:** ${pv_tax_shield:.2f} million")
st.write(f"**Adjusted Present Value (APV):** ${apv:.2f} million")
