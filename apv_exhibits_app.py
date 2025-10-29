# final_apv_with_exhibits.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="APV Calculator with Exhibits", layout="wide")
st.title("💰 Adjusted Present Value (APV) Calculator — with Exhibits 18.2–18.6")
st.caption("APV tool. All key inputs exposed; exhibits generated and labeled.")

st.divider()
st.header("📥 Project & Financial Parameters (inputs)")

col1, col2 = st.columns(2)
with col1:
    S0 = st.number_input("Current exchange rate S0 ($/€)", value=1.32, step=0.01, format="%.4f")
    pi_f = st.number_input("Foreign inflation rate π_f (%)", value=2.1, step=0.1) / 100.0
    pi_d = st.number_input("Domestic inflation rate π_d (%)", value=3.0, step=0.1) / 100.0
    C0_eur = st.number_input("Initial project cost C0 (EUR)", value=5_500_000.0, step=100_000.0, format="%.2f")
    years = st.number_input("Project life (years)", value=8, step=1)
with col2:
    tax = st.number_input("Corporate tax rate τ (%)", value=35.0, step=0.1) / 100.0
    K_ud = st.number_input("Unlevered cost of capital K_ud (%)", value=12.0, step=0.1) / 100.0
    i_c = st.number_input("Concessional loan interest rate i_c (%)", value=5.0, step=0.1) / 100.0
    i_d = st.number_input("Domestic borrowing / discount rate i_d (%)", value=8.0, step=0.1) / 100.0
    borrowing_capacity_usd = st.number_input("Borrowing capacity (USD)", value=2_904_000.0, step=100_000.0, format="%.2f")

st.divider()
st.header("📊 Operating & Market Parameters")

col3, col4 = st.columns(2)
with col3:
    units_y1 = st.number_input("Year-1 sales units (EU)", value=25_000.0, step=100.0)
    units_growth = st.number_input("Sales units growth (%)", value=12.0, step=0.1) / 100.0
    selling_price = st.number_input("Selling price per unit (€)", value=200.0, step=1.0)
    production_cost = st.number_input("Production cost per unit (€)", value=160.0, step=1.0)
    contrib_growth = st.number_input("Contribution (price) growth / euro inflation (%)", value=2.1, step=0.1) / 100.0
with col4:
    lost_units_y1 = st.number_input("Year-1  export units", value=9_600.0, step=100.0)
    lost_units_growth = st.number_input(" units growth (%)", value=5.0, step=0.1) / 100.0
    lost_margin_usd_y1 = st.number_input(" margin per unit (USD) in year1", value=35.0, step=0.1)
    lost_margin_growth = st.number_input(" margin growth (%)", value=3.0, step=0.1) / 100.0
    concession_loan_eur = st.number_input("Concessional loan (EUR)", value=4_000_000.0, step=100_000.0)

st.divider()
st.header("🏦 Affiliate / Tax Details (for Freed-up funds)")
affiliate_after_tax_retained = st.number_input("Affiliate accumulated funds (after foreign tax) (EUR)", value=750_000.0, step=10_000.0)
affiliate_prior_tax_rate = st.number_input("Affiliate prior tax rate (%) (used historically)", value=20.0, step=0.1) / 100.0

st.divider()
st.markdown("**Derived values (shown for clarity):**")
derived_col1, derived_col2 = st.columns(2)
with derived_col1:
    contribution_per_unit = selling_price - production_cost
    st.metric("Derived contribution (€/unit)", f"{contribution_per_unit:.2f}")
    st.metric("Project cost (USD) = S0 × C0 (USD)", f"{C0_eur * S0:,.2f}")
with derived_col2:
    st.metric("Loan / Project ratio (euros)", f"{concession_loan_eur / C0_eur:.4f}")
    st.metric("Project debt ratio used (λ_parent)", f"{borrowing_capacity_usd / (C0_eur * S0):.4f}")

st.divider()
st.write("Press **Calculate** to generate Exhibits 18.2–18.6 and the APV.")

def S_t(t):
    # PPP adjusted expected spot S_t = S0 * (1 + pi_d)^t / (1 + pi_f)^t
    return S0 * ((1 + pi_d) ** t) / ((1 + pi_f) ** t)

def compute_all():
    # Depreciation per year (straight-line)
    depreciation_eur = C0_eur / years

    # EXHIBIT 18.2 - After-tax operating cash flows
    rows_182 = []
    pv_operating = 0.0
    for t in range(1, int(years) + 1):
        # CM per unit in year t (euros) = (selling_price - production_cost) * (1 + contrib_growth)^(t-1)
        cm_eur = contribution_per_unit * ((1 + contrib_growth) ** (t - 1))
        qty = units_y1 * ((1 + units_growth) ** (t - 1))
        a_usd = S_t(t) * qty * cm_eur  # Sales in USD from new plant
        lost_q = lost_units_y1 * ((1 + lost_units_growth) ** t)
        lost_margin_usd_t = lost_margin_usd_y1 * ((1 + lost_margin_growth) ** t)
        b_usd = - lost_q * lost_margin_usd_t
        ocf = a_usd + b_usd
        ocf_aftertax = ocf * (1 - tax)
        pv = ocf_aftertax / ((1 + K_ud) ** t)
        pv_operating += pv
        rows_182.append({
            "Year": t,
            "S_t ($/€)": round(S_t(t), 6),
            "CM €/unit (year t)": round(cm_eur, 2),
            "Qty (year t)": int(round(qty)),
            "Sales (USD) = S_t×Qty×CM": round(a_usd, 2),
            "Lost Sales ($)": round(b_usd, 2),
            "OCF ($)": round(ocf, 2),
            "OCF(1-τ) ($)": round(ocf_aftertax, 2),
            "PV @ K_ud ($)": round(pv, 2)
        })
    df182 = pd.DataFrame(rows_182)

    # EXHIBIT 18.3 - Depreciation tax shields
    rows_183 = []
    pv_dep = 0.0
    for t in range(1, int(years) + 1):
        shield_usd = tax * depreciation_eur * S_t(t)   # S_t * τ * D_t
        pv = shield_usd / ((1 + i_d) ** t)
        pv_dep += pv
        rows_183.append({
            "Year": t,
            "S_t ($/€)": round(S_t(t), 6),
            "D_t (€)": round(depreciation_eur, 2),
            "S_t × τ × D_t ($)": round(shield_usd, 2),
            "PV @ i_d ($)": round(pv, 2)
        })
    df183 = pd.DataFrame(rows_183)

    # EXHIBIT 18.5 - Concessional loan payments (equal principal schedule)
    rows_185 = []
    principal_payment = concession_loan_eur / years
    remaining = concession_loan_eur
    pv_concess_payments = 0.0
    for t in range(1, int(years) + 1):
        interest = remaining * i_c
        payment_eur = principal_payment + interest
        payment_usd = payment_eur * S_t(t)
        pv = payment_usd / ((1 + i_d) ** t)
        pv_concess_payments += pv
        rows_185.append({
            "Year": t,
            "Remaining (€) start": round(remaining, 2),
            "Interest (€)": round(interest, 2),
            "Principal (€)": round(principal_payment, 2),
            "Payment (€)": round(payment_eur, 2),
            "S_t ($/€)": round(S_t(t), 6),
            "Payment (USD)": round(payment_usd, 2),
            "PV @ i_d (USD)": round(pv, 2)
        })
        remaining -= principal_payment
    df185 = pd.DataFrame(rows_185)
    pv_concess_payments = round(pv_concess_payments, 2)
    dollar_value_concession_loan = concession_loan_eur * S0
    loan_benefit = round(dollar_value_concession_loan - pv_concess_payments, 2)

    # EXHIBIT 18.6 - Interest tax shields
    # Compute lambda from borrowing capacity:
    # lambda_parent = borrowing_capacity_usd / (project_cost_usd)
    project_cost_usd = C0_eur * S0
    lambda_parent = borrowing_capacity_usd / project_cost_usd
    loan_ratio = concession_loan_eur / C0_eur
    lambda_project = lambda_parent / loan_ratio

    rows_186 = []
    remaining = concession_loan_eur
    pv_interest_tax = 0.0
    for t in range(1, int(years) + 1):
        interest = remaining * i_c
        shield_usd = S_t(t) * interest * lambda_project * tax
        pv = shield_usd / ((1 + i_d) ** t)
        pv_interest_tax += pv
        rows_186.append({
            "Year": t,
            "S_t ($/€)": round(S_t(t), 6),
            "I_t (€)": round(interest, 2),
            "λ / Project debt ratio": round(lambda_project, 6),
            "S_t × λ × τ × I_t ($)": round(shield_usd, 2),
            "PV @ i_d ($)": round(pv, 2)
        })
        remaining -= principal_payment
    df186 = pd.DataFrame(rows_186)

    # Freed-up affiliate funds (automatic calculation using affiliate inputs)
    # affiliate_after_tax_retained is the AFTER-foreign-tax amount in EUR (what the affiliate has on books)
    gross_eur = affiliate_after_tax_retained / (1 - affiliate_prior_tax_rate)  # gross before foreign tax
    gross_usd = gross_eur * S0
    freed_up_usd = round((tax - affiliate_prior_tax_rate) * gross_usd, 2)

    # Final APV
    pv_operating = round(pv_operating, 2)
    pv_dep = round(pv_dep, 2)
    pv_interest_tax = round(pv_interest_tax, 2)
    initial_invest_usd = round(C0_eur * S0, 2)
    apv = round(pv_operating + pv_dep + loan_benefit + pv_interest_tax + freed_up_usd - initial_invest_usd, 2)

    # Return everything
    meta = {
        "pv_operating": pv_operating,
        "pv_dep": pv_dep,
        "pv_concess_payments": pv_concess_payments,
        "loan_benefit": loan_benefit,
        "pv_interest_tax": pv_interest_tax,
        "freed_up_usd": freed_up_usd,
        "initial_invest_usd": initial_invest_usd,
        "apv": apv,
        "lambda_parent": lambda_parent,
        "lambda_project": lambda_project
    }
    return df182, df183, df185, df186, meta

if st.button("📈 Calculate Exhibits & APV"):
    df182, df183, df185, df186, meta = compute_all()

    st.success("✅ Calculation complete")

    st.subheader("📘 Exhibit 18.2 — After-Tax Operating Cash Flows")
    st.dataframe(df182, use_container_width=True)

    st.subheader("📘 Exhibit 18.3 — Depreciation Tax Shields")
    st.dataframe(df183, use_container_width=True)

    st.subheader("📘 Exhibit 18.5 — Concessional Loan Payments & Benefit (PV at i_d)")
    st.dataframe(df185, use_container_width=True)
    st.markdown(f"**Dollar value of concessionary loan at S0** = {concession_loan_eur} × {S0} = ${concession_loan_eur * S0:,.2f}")
    st.markdown(f"**PV of concessional loan payments (discounted at i_d)** = ${meta['pv_concess_payments']:,.2f}")
    st.markdown(f"**Value (benefit) of concessional financing** = ${meta['loan_benefit']:,.2f}")

    st.subheader("📘 Exhibit 18.6 — Interest Tax Shields")
    st.dataframe(df186, use_container_width=True)
    st.markdown(f"**λ_parent** (borrowing capacity / project USD cost) = {meta['lambda_parent']:.6f}")
    st.markdown(f"**λ_project** (used in exhibit) = {meta['lambda_project']:.6f}")

    st.divider()
    st.header("📊 Final APV Summary")
    summary_df = pd.DataFrame([
        ["PV (Operating CFs)", meta['pv_operating']],
        ["PV (Depreciation Shields)", meta['pv_dep']],
        ["PV (Loan Benefit)", meta['loan_benefit']],
        ["PV (Interest Shields)", meta['pv_interest_tax']],
        ["Freed-Up Affiliate Funds", meta['freed_up_usd']],
        ["Initial Investment (USD)", meta['initial_invest_usd']],
        ["Final APV", meta['apv']]
    ], columns=["Component", "Value ($)"])
    st.dataframe(summary_df, use_container_width=True)
    st.markdown(f"### 💰 Final APV = **${meta['apv']:,.2f}**")

    
    st.info("Made with ❤️ by Deepesh Pandey")

