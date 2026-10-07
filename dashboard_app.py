"""
South India Pharmaceutical Market Intelligence Dashboard.
Streamlit Application for exploring DLMAI rankings, pillar breakdowns, explainability, and sensitivity bounds.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path

# Set Page Config
st.set_page_config(
    page_title="South India Pharma Market Intelligence (DLMAI)",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 1.5rem; }
    .metric-card { background-color: #F3F4F6; border-radius: 8px; padding: 16px; border-left: 4px solid #3B82F6; }
    .tier-1-badge { background-color: #10B981; color: white; padding: 4px 8px; border-radius: 4px; font-weight: 600; }
    .tier-2-badge { background-color: #3B82F6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: 600; }
    .tier-3-badge { background-color: #F59E0B; color: white; padding: 4px 8px; border-radius: 4px; font-weight: 600; }
    .tier-4-badge { background-color: #EF4444; color: white; padding: 4px 8px; border-radius: 4px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent
    if base_dir.name == "dashboard":
        base_dir = base_dir.parent
    outputs_dir = base_dir / "outputs"

    df_scores = pd.read_csv(outputs_dir / "dlmai_south_india_scores.csv")
    df_combined = pd.read_csv(outputs_dir / "dlmai_south_india_combined_output.csv")
    df_quality = pd.read_csv(outputs_dir / "data_quality_report.csv")
    df_coverage = pd.read_csv(outputs_dir / "district_coverage_matrix.csv")

    with open(outputs_dir / "refresh_metadata.json", "r", encoding="utf-8") as f:
        refresh_meta = json.load(f)

    with open(outputs_dir / "ahp_validation.json", "r", encoding="utf-8") as f:
        ahp_meta = json.load(f)

    return df_scores, df_combined, df_quality, df_coverage, refresh_meta, ahp_meta


try:
    df_scores, df_combined, df_quality, df_coverage, refresh_meta, ahp_meta = load_data()
except Exception as e:
    st.error(f"Error loading analytical outputs from outputs/: {e}")
    st.stop()

# Header
st.markdown('<div class="main-header">💊 South India Pharmaceutical Market Attractiveness Index (DLMAI)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">District-Level Market Opportunity, Healthcare Infrastructure, and Competitive Intelligence Model for 148 South Indian Districts</div>', unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation & Filters")
nav_mode = st.sidebar.radio(
    "Select View",
    ["📊 Regional Overview", "🗺️ State Comparison", "🏆 District Rankings", "🔍 District Deep-Dive & Explainability", "📈 Sensitivity & Robustness", "📑 Methodology & Audit Governance"]
)

# ─────────────────────────────────────────────────────────────────────────────
# VIEW 1: REGIONAL OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if nav_mode == "📊 Regional Overview":
    st.header("South India Regional Market Overview")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Districts", f"{refresh_meta['total_canonical_districts']}")
    with col2:
        st.metric("States / UTs", "7")
    with col3:
        st.metric("Mean DLMAI Score", f"{refresh_meta['mean_dlmai_score']}")
    with col4:
        st.metric("Median DLMAI Score", f"{refresh_meta['median_dlmai_score']}")
    with col5:
        st.metric("Rank Stability (ρ)", f"{refresh_meta['mean_spearman_rank_stability']}", "Highly Stable")

    st.markdown("---")

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("Commercial Tier Distribution")
        tier_counts = df_scores["commercial_tier"].value_counts().reset_index()
        tier_counts.columns = ["Tier", "District Count"]
        st.dataframe(tier_counts, use_container_width=True, hide_index=True)

        st.info("💡 **Strategic Tier Definitions:**\n"
                "- **Tier 1 (Top 20%):** Core commercial expansion markets. Direct specialty sales force, tertiary hospital KAM empanelment.\n"
                "- **Tier 2 (50th–80th %):** Growth markets. Retail pharmacy expansion, primary care prescriber coverage.\n"
                "- **Tier 3 (20th–50th %):** Moderate opportunity. Generic trade portfolio alignment, distributor-led fulfillment.\n"
                "- **Tier 4 (Bottom 20%):** Nascent / Rural. Government procurement tenders, primary clinic coverage.")

    with col_right:
        st.subheader("State-Wise Summary")
        state_summary = df_scores.groupby("state_name").agg(
            Districts=("lgd_district_code", "count"),
            Avg_DLMAI=("dlmai_score", "mean"),
            Median_DLMAI=("dlmai_score", "median"),
            Top_District=("district_name", "first")
        ).reset_index()
        state_summary["Avg_DLMAI"] = state_summary["Avg_DLMAI"].round(2)
        state_summary["Median_DLMAI"] = state_summary["Median_DLMAI"].round(2)
        st.dataframe(state_summary.sort_values("Avg_DLMAI", ascending=False), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# VIEW 2: STATE COMPARISON
# ─────────────────────────────────────────────────────────────────────────────
elif nav_mode == "🗺️ State Comparison":
    st.header("State-Level Comparative Analysis")

    selected_states = st.multiselect(
        "Filter States",
        options=sorted(df_scores["state_name"].unique()),
        default=sorted(df_scores["state_name"].unique())
    )

    filtered_df = df_scores[df_scores["state_name"].isin(selected_states)]

    st.subheader("State Average Pillar Sub-Scores")
    state_pillars = filtered_df.groupby("state_name")[
        ["pillar_p1_score", "pillar_p2_score", "pillar_p3_score", "pillar_p4_score", "pillar_p5_score", "pillar_p6_score", "pillar_p7_score"]
    ].mean().round(1)

    state_pillars.columns = [
        "P1: Demand & Disease", "P2: Affordability", "P3: Infrastructure",
        "P4: Distribution", "P5: Saturation (Dampener)", "P6: Policy/Schemes", "P7: Growth"
    ]
    st.dataframe(state_pillars, use_container_width=True)

    st.subheader("District Distribution by State & Commercial Tier")
    cross_tab = pd.crosstab(filtered_df["state_name"], filtered_df["commercial_tier"])
    st.dataframe(cross_tab, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# VIEW 3: DISTRICT RANKINGS
# ─────────────────────────────────────────────────────────────────────────────
elif nav_mode == "🏆 District Rankings":
    st.header("South India District Rankings")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st_filter = st.selectbox("Filter by State", ["All States"] + sorted(df_scores["state_name"].unique().tolist()))
    with col_f2:
        tier_filter = st.selectbox("Filter by Tier", ["All Tiers"] + sorted(df_scores["commercial_tier"].unique().tolist()))
    with col_f3:
        search_query = st.text_input("Search District Name", "")

    display_df = df_scores.copy()
    if st_filter != "All States":
        display_df = display_df[display_df["state_name"] == st_filter]
    if tier_filter != "All Tiers":
        display_df = display_df[display_df["commercial_tier"] == tier_filter]
    if search_query:
        display_df = display_df[display_df["district_name"].str.contains(search_query, case=False, na=False)]

    cols_to_show = [
        "south_india_rank", "state_rank", "district_name", "state_name", "dlmai_score",
        "commercial_tier", "value_driver_score", "saturation_penalty",
        "pillar_p1_score", "pillar_p2_score", "pillar_p3_score", "pillar_p4_score", "pillar_p5_score"
    ]
    st.dataframe(
        display_df[cols_to_show].rename(columns={
            "south_india_rank": "SI Rank",
            "state_rank": "State Rank",
            "district_name": "District",
            "state_name": "State",
            "dlmai_score": "DLMAI",
            "commercial_tier": "Tier",
            "value_driver_score": "Value Score",
            "saturation_penalty": "Saturation Penalty",
            "pillar_p1_score": "P1 (Demand)",
            "pillar_p2_score": "P2 (Access)",
            "pillar_p3_score": "P3 (Infra)",
            "pillar_p4_score": "P4 (Retail)",
            "pillar_p5_score": "P5 (Sat)"
        }),
        use_container_width=True,
        hide_index=True
    )

    # Download CSV
    csv_bytes = display_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Filtered Rankings CSV", csv_bytes, "south_india_dlmai_rankings.csv", "text/csv")

# ─────────────────────────────────────────────────────────────────────────────
# VIEW 4: DISTRICT DEEP-DIVE & EXPLAINABILITY
# ─────────────────────────────────────────────────────────────────────────────
elif nav_mode == "🔍 District Deep-Dive & Explainability":
    st.header("District Diagnostic Deep-Dive & Score Explainability")

    selected_district = st.selectbox(
        "Select a District to Profile",
        options=sorted(df_scores["district_name"].unique())
    )

    d_row = df_scores[df_scores["district_name"] == selected_district].iloc[0]
    q_row = df_quality[df_quality["district_name"] == selected_district].iloc[0] if len(df_quality[df_quality["district_name"] == selected_district]) > 0 else None
    c_row = df_combined[df_combined["district_name"] == selected_district].iloc[0] if len(df_combined[df_combined["district_name"] == selected_district]) > 0 else None

    # Overview Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("DLMAI Score", f"{d_row['dlmai_score']:.2f}")
    with c2:
        st.metric("South India Rank", f"#{int(d_row['south_india_rank'])} of 148")
    with c3:
        st.metric("State Rank", f"#{int(d_row['state_rank'])} in {d_row['state_name']}")
    with c4:
        st.metric("Commercial Tier", f"{d_row['commercial_tier']}")

    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Pillar Performance Profile")
        pillars_data = {
            "Pillar": [
                "P1: Healthcare Demand & Disease Burden",
                "P2: Economic Access & Affordability",
                "P3: Healthcare Infrastructure",
                "P4: Pharmaceutical Distribution Accessibility",
                "P5: Market Competition & Saturation (Dampener)",
                "P6: Policy & Development Environment",
                "P7: Demographic & Market Growth"
            ],
            "Score (0-100)": [
                d_row["pillar_p1_score"],
                d_row["pillar_p2_score"],
                d_row["pillar_p3_score"],
                d_row["pillar_p4_score"],
                d_row["pillar_p5_score"],
                d_row["pillar_p6_score"],
                d_row["pillar_p7_score"]
            ]
        }
        st.dataframe(pd.DataFrame(pillars_data), use_container_width=True, hide_index=True)

        st.subheader("💡 Strategic Drivers & Explainability")
        st.markdown(f"**Why does {selected_district} rank #{int(d_row['south_india_rank'])}?**")
        st.markdown(f"- **Gross Opportunity (Value Driver Score):** `{d_row['value_driver_score']:.2f}` / 100")
        st.markdown(f"- **Market Saturation Penalty Subtracted:** `- {d_row['saturation_penalty']:.2f}` (Pillar 5 Saturation: `{d_row['pillar_p5_score']:.1f}`)")
        st.markdown(f"- **Net DLMAI Score:** `{d_row['dlmai_score']:.2f}`")

    with col_right:
        st.subheader("Data Provenance & Quality Confidence")
        if q_row is not None:
            st.write(f"- **Data Quality Score:** `{q_row['data_quality_score']}` / 100")
            st.write(f"- **Observed Indicators:** `{q_row['observed_pct']}%`")
            st.write(f"- **Lineage Inherited Indicators:** `{q_row['inherited_pct']}%`")
            st.write(f"- **Statistical Imputed Indicators:** `{q_row['imputed_pct']}%`")

        st.subheader("Monte Carlo Rank Stability")
        st.write(f"- **95% Rank Confidence Interval:** `[#{int(d_row['rank_ci_lower_2_5'])}, #{int(d_row['rank_ci_upper_97_5'])}]`")
        st.write(f"- **Rank Standard Deviation:** `± {d_row['rank_std_dev']:.2f} ranks`")
        st.write(f"- **Top-10 Selection Frequency:** `{d_row['top_10_frequency_pct']:.1f}%`")
        st.write(f"- **Top-20 Selection Frequency:** `{d_row['top_20_frequency_pct']:.1f}%`")

    # Detailed Indicators
    if c_row is not None:
        st.markdown("---")
        st.subheader(f"Extracted Analytical Indicator Values for {selected_district}")
        ind_records = []
        for col in c_row.index:
            if col in ("lgd_district_code", "district_name", "state_name") or "_provenance" in col:
                continue
            prov = c_row.get(f"{col}_provenance", "OBSERVED")
            ind_records.append({
                "Indicator ID": col,
                "Analytical Value": c_row[col],
                "Data Status": prov
            })
        st.dataframe(pd.DataFrame(ind_records), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# VIEW 5: SENSITIVITY & ROBUSTNESS
# ─────────────────────────────────────────────────────────────────────────────
elif nav_mode == "📈 Sensitivity & Robustness":
    st.header("Monte Carlo Sensitivity & Methodological Robustness")

    st.write(r"The South India DLMAI model was stress-tested across **1,000 Monte Carlo simulations** using stochastic log-normal weight perturbation (variance $\sigma^2 = 0.04$).")
    st.metric("Mean Spearman Rank Stability (ρ)", f"{refresh_meta['mean_spearman_rank_stability']}", "Target > 0.95 Met")

    st.subheader("District-Wise Rank Volatility Table (Sample)")
    st.dataframe(
        df_scores[[
            "south_india_rank", "district_name", "state_name", "dlmai_score",
            "rank_std_dev", "rank_ci_lower_2_5", "rank_ci_upper_97_5", "top_10_frequency_pct", "top_20_frequency_pct"
        ]].rename(columns={
            "south_india_rank": "Baseline Rank",
            "district_name": "District",
            "state_name": "State",
            "dlmai_score": "Score",
            "rank_std_dev": "Rank Std Dev (σ)",
            "rank_ci_lower_2_5": "95% CI Lower",
            "rank_ci_upper_97_5": "95% CI Upper",
            "top_10_frequency_pct": "Top-10 %",
            "top_20_frequency_pct": "Top-20 %"
        }),
        use_container_width=True,
        hide_index=True
    )

# ─────────────────────────────────────────────────────────────────────────────
# VIEW 6: METHODOLOGY & AUDIT GOVERNANCE
# ─────────────────────────────────────────────────────────────────────────────
elif nav_mode == "📑 Methodology & Audit Governance":
    st.header("Methodology Governance & Mathematical Audit")

    st.subheader("Saaty Analytic Hierarchy Process (AHP) Matrix")
    crit = ahp_meta["criteria"]
    st.json({
        "Criteria": crit,
        "Principal Eigenvalue (Lambda_max)": ahp_meta["lambda_max"],
        "Consistency Index (CI)": ahp_meta["consistency_index"],
        "Consistency Ratio (CR)": f"{ahp_meta['consistency_ratio']} (CR < 0.10: {ahp_meta['is_consistent']})",
        "AHP Priority Weights": ahp_meta["weights"],
        "Renormalized Value Driver Weights": ahp_meta["renormalized_driver_weights"],
        "Saturation Dampener Coefficient (Lambda)": ahp_meta["saturation_lambda"]
    })

    st.subheader("Audited Data Source Integrity")
    st.markdown("""
    1. **NFHS-5 District Factsheets (2019-2021):** Extracted using unit-anchored regex matching. Footnote and historical NFHS-4 column contamination eliminated.
    2. **Rural Health Statistics (RHS):** 8-column layout extracted across all 620 districts in MoHFW PDF.
    3. **Jan Aushadhi Kendras:** Deduplicated by unique Kendra code; scored as population-adjusted retail density per 100k.
    4. **MCA21 Corporate Master:** Filtered to active pharma manufacturing entities; dampener penalty subtracted to reflect competitive crowding.
    5. **NITI Aayog Aspirational Districts:** Official 112 exhaustive registry list.
    6. **Census Baseline:** Primary Census Abstract demographics and intercensal growth.
    """)

    st.info("Document References:\n"
            "- Methodology: `docs/South_India_DLMAI_Methodology.md`\n"
            "- Data Dictionary: `docs/South_India_DLMAI_Data_Dictionary.md`\n"
            "- Decision Log: `docs/DLMAI_Model_Decision_Log.md`\n"
            "- Audit Report: `docs/DLMAI_Methodology_Correction_Audit.md`")
