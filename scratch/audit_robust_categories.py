import pandas as pd

df_topn = pd.read_csv("outputs/red_team_validation_v2/test03_topn_robustness.csv")

print("=" * 70)
print("PART 3: AUDIT OF ROBUSTNESS TIERS (INVARIANT VS HIGH-ROBUSTNESS)")
print("=" * 70)

# Top 10 Invariant vs High-Robustness
t10_invariant = df_topn[df_topn["top_10_frequency_pct"] == 100.0]
t10_high_rob = df_topn[(df_topn["top_10_frequency_pct"] >= 90.0) & (df_topn["top_10_frequency_pct"] < 100.0)]
t10_mod_rob = df_topn[(df_topn["top_10_frequency_pct"] >= 70.0) & (df_topn["top_10_frequency_pct"] < 90.0)]

print(f"Top-10 Invariant (100% inclusion across all 10 variants): {len(t10_invariant)} districts")
for _, r in t10_invariant.iterrows():
    print(f"  #{int(r['baseline_rank'])} {r['district_name']} ({r['state_name']}): 100.0% (Rank Range: #{int(r['rank_min'])}-#{int(r['rank_max'])})")

print(f"\nTop-10 High-Robustness (90.0% - 99.9% inclusion): {len(t10_high_rob)} districts")
for _, r in t10_high_rob.iterrows():
    print(f"  #{int(r['baseline_rank'])} {r['district_name']} ({r['state_name']}): {r['top_10_frequency_pct']}% (Rank Range: #{int(r['rank_min'])}-#{int(r['rank_max'])})")

print(f"\nTop-10 Moderate Robustness (70.0% - 89.9% inclusion): {len(t10_mod_rob)} districts")
for _, r in t10_mod_rob.iterrows():
    print(f"  #{int(r['baseline_rank'])} {r['district_name']} ({r['state_name']}): {r['top_10_frequency_pct']}% (Rank Range: #{int(r['rank_min'])}-#{int(r['rank_max'])})")

# Overall District Robustness Classification across all 148 districts
# Strict Definitions:
# 1. Invariant: Rank Spread <= 5 AND 100% tier agreement
# 2. High-Robustness: Rank Spread <= 15 OR Inclusion >= 90%
# 3. Moderate Robustness: Rank Spread 16-24 OR Inclusion 70-89%
# 4. Volatile / Sensitive: Rank Spread >= 25 OR Inclusion < 70%

invariant_all = df_topn[df_topn["rank_spread"] <= 5]
print(f"\nOverall District Universe:")
print(f"  Strictly Invariant (Rank Spread <= 5 ranks across all 10 variants): {len(invariant_all)} districts")
