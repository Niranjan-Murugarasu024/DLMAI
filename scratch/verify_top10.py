import pandas as pd
df_s = pd.read_csv('outputs/dlmai_south_india_scores.csv')

top10 = df_s.head(10)
for _, r in top10.iterrows():
    v = r['value_driver_score']
    p = r['saturation_penalty']
    d = r['dlmai_score']
    diff = abs((v - p) - d)
    print(f"#{int(r['south_india_rank'])} {r['district_name']} ({r['state_name']}): ValueScore={v:.4f} - Penalty={p:.4f} = DLMAI={d:.4f} (Residual={diff:.6f})")
