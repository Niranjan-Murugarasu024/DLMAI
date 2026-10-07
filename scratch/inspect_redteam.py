import pandas as pd

df_vc = pd.read_csv('outputs/red_team_model_comparison.csv')
print("=== MODEL VARIANT COMPARISON (Phase 42) ===")
for _, r in df_vc.iterrows():
    name = r['model_variant'].replace('\u03bb', 'lambda')
    print(f"{name}: Rho={r['spearman_rho']:.4f}, Top10={r['top_10_overlap_pct']}%, Top20={r['top_20_overlap_pct']}%")

print("\n=== LEAVE-ONE-PILLAR-OUT (Phase 32) ===")
df_lopo = pd.read_csv('outputs/leave_one_pillar_out.csv')
for _, r in df_lopo.iterrows():
    print(f"{r['dropped_pillar']} ({r['pillar_name']}): Rho={r['spearman_rho']:.4f}, Disruption={r['rank_disruption']:.4f}, Top10={r['top_10_overlap']}/10")

print("\n=== TOP 5 LEAVE-ONE-INDICATOR-OUT DISRUPTIONS ===")
df_loo = pd.read_csv('outputs/leave_one_out_analysis.csv')
for _, r in df_loo.head(5).iterrows():
    print(f"{r['dropped_indicator']} ({r['pillar']}): Rho={r['spearman_rho']:.4f}, Disruption={r['rank_disruption']:.4f}, Top10={r['top_10_overlap']}/10")

print("\n=== TOP 10 ROBUST DISTRICTS ===")
df_rob = pd.read_csv('outputs/robust_districts.csv')
for _, r in df_rob.head(10).iterrows():
    print(f"#{int(r['baseline_rank'])} {r['district_name']} ({r['state_name']}): MeanRank={r['mean_rank']:.1f}, StdDev={r['std_dev_rank']:.1f}, Spread={int(r['rank_spread'])}")

print("\n=== TOP 10 MOST VOLATILE DISTRICTS ===")
df_vol = pd.read_csv('outputs/volatile_districts.csv')
for _, r in df_vol.head(10).iterrows():
    print(f"#{int(r['baseline_rank'])} {r['district_name']} ({r['state_name']}): MeanRank={r['mean_rank']:.1f}, StdDev={r['std_dev_rank']:.1f}, Spread={int(r['rank_spread'])}")
