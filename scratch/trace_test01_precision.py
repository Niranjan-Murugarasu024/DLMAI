import yaml
import json
import math
import numpy as np
import pandas as pd

# Load configurations
with open("config/indicators.yaml", "r", encoding="utf-8") as f:
    ind_cfg = yaml.safe_load(f)
with open("config/pillars.yaml", "r", encoding="utf-8") as f:
    pil_cfg = yaml.safe_load(f)
with open("config/weights.yaml", "r", encoding="utf-8") as f:
    w_cfg = yaml.safe_load(f)

df_prod = pd.read_csv("outputs/dlmai_south_india_scores.csv")
df_data = pd.read_csv("outputs/dlmai_south_india_combined_output.csv")
scored_inds = list(ind_cfg["indicators"].keys())
codes = df_prod["lgd_district_code"].tolist()

print("=" * 70)
print("PART 1: FORENSIC NUMERICAL TRACE OF TEST-1 ERROR")
print("=" * 70)

# Stage 1: Raw data to Normalization
# Production uses: round(((v - min)/(max - min))*100, 4)
raw_dict = {c: {ind: float(df_data[df_data["lgd_district_code"] == c][ind].iloc[0]) for ind in scored_inds} for c in codes}

norm_unrounded = {c: {} for c in codes}
norm_rounded4 = {c: {} for c in codes}

for ind in scored_inds:
    direction = ind_cfg["indicators"][ind]["direction"]
    vals = [raw_dict[c][ind] for c in codes]
    x_min, x_max = min(vals), max(vals)
    r_val = x_max - x_min
    for c in codes:
        v = raw_dict[c][ind]
        if r_val == 0:
            norm_unrounded[c][ind] = 50.0
            norm_rounded4[c][ind] = 50.0
        elif direction == "NEGATIVE":
            norm_unrounded[c][ind] = ((x_max - v) / r_val) * 100.0
            norm_rounded4[c][ind] = round(((x_max - v) / r_val) * 100.0, 4)
        else:
            norm_unrounded[c][ind] = ((v - x_min) / r_val) * 100.0
            norm_rounded4[c][ind] = round(((v - x_min) / r_val) * 100.0, 4)

max_norm_diff = max(abs(norm_unrounded[c][ind] - norm_rounded4[c][ind]) for c in codes for ind in scored_inds)
print(f"Stage 1 (Normalization): Max abs difference between float64 vs round(4): {max_norm_diff:.8e}")

# Stage 2: Entropy Weights
# Compute with unrounded vs rounded
def calc_entropy(norm_dict, ind_list, round_weights=True):
    if len(ind_list) == 1:
        return {ind_list[0]: 1.0}
    m = len(codes)
    k = 1.0 / math.log(m)
    eps = 1e-6
    col_sums = {ind: sum(norm_dict[c][ind] + eps for c in codes) for ind in ind_list}
    e_dict = {}
    for ind in ind_list:
        c_sum = col_sums[ind]
        e_val = 0.0
        for c in codes:
            p_ij = (norm_dict[c][ind] + eps) / c_sum
            e_val += p_ij * math.log(p_ij)
        e_dict[ind] = -k * e_val
    d_dict = {ind: max(1.0 - e_dict[ind], 1e-6) for ind in ind_list}
    tot_d = sum(d_dict.values())
    if round_weights:
        w_dict = {ind: round(d_dict[ind] / tot_d, 6) for ind in ind_list}
        w_sum = sum(w_dict.values())
        w_dict[ind_list[0]] = round(w_dict[ind_list[0]] + (1.0 - w_sum), 6)
        return w_dict
    else:
        return {ind: d_dict[ind] / tot_d for ind in ind_list}

entropy_unrounded = {p: calc_entropy(norm_unrounded, pil_cfg["pillars"][p]["indicators"], False) for p in pil_cfg["pillars"]}
entropy_rounded6 = {p: calc_entropy(norm_rounded4, pil_cfg["pillars"][p]["indicators"], True) for p in pil_cfg["pillars"]}

max_entropy_diff = max(abs(entropy_unrounded[p][ind] - entropy_rounded6[p][ind]) for p in pil_cfg["pillars"] for ind in entropy_unrounded[p])
print(f"Stage 2 (Entropy Weights): Max abs difference between unrounded vs round(6): {max_entropy_diff:.8e}")

# Stage 3: Pillar Sub-scores
# In production: pillar scores are rounded to 4 decimal places
p_scores_prod = {c: {f"P{p}": df_prod[df_prod["lgd_district_code"] == c][f"pillar_p{p}_score"].iloc[0] for p in range(1, 8)} for c in codes}

p_scores_unrounded = {c: {} for c in codes}
p_scores_rounded4 = {c: {} for c in codes}

for p_code, p_meta in pil_cfg["pillars"].items():
    ind_list = p_meta["indicators"]
    for c in codes:
        sub_unround = sum(entropy_unrounded[p_code][ind] * norm_unrounded[c][ind] for ind in ind_list)
        sub_round = sum(entropy_rounded6[p_code][ind] * norm_rounded4[c][ind] for ind in ind_list)
        p_scores_unrounded[c][p_code] = sub_unround
        p_scores_rounded4[c][p_code] = round(sub_round, 4)

max_p_diff_prod = max(abs(p_scores_rounded4[c][p] - p_scores_prod[c][p]) for c in codes for p in pil_cfg["pillars"])
print(f"Stage 3 (Pillar Scores): Max abs diff between intermediate rounded(4) vs production CSV: {max_p_diff_prod:.8e}")

# Stage 4: Value Driver Score
driver_weights = w_cfg["value_driver_weights_renormalized"]
driver_pillars = [p for p in w_cfg["ahp_matrix"]["criteria"] if p != "P5"]
sat_lambda = float(w_cfg["saturation"]["dampener_coefficient_lambda"])

v_prod = df_prod.set_index("lgd_district_code")["value_driver_score"].to_dict()
v_recalc = {c: round(sum(driver_weights[p] * p_scores_rounded4[c][p] for p in driver_pillars), 4) for c in codes}
max_v_diff = max(abs(v_recalc[c] - v_prod[c]) for c in codes)
print(f"Stage 4 (Value Driver Score): Max abs diff vs production CSV: {max_v_diff:.8e}")

# Stage 5: Saturation Penalty
c_prod = df_prod.set_index("lgd_district_code")["saturation_penalty"].to_dict()
c_recalc = {c: round(sat_lambda * p_scores_rounded4[c]["P5"], 4) for c in codes}
max_c_diff = max(abs(c_recalc[c] - c_prod[c]) for c in codes)
print(f"Stage 5 (Saturation Penalty): Max abs diff vs production CSV: {max_c_diff:.8e}")

# Stage 6: Final DLMAI Score
dlmai_prod = df_prod.set_index("lgd_district_code")["dlmai_score"].to_dict()
dlmai_recalc_from_rounded_vc = {c: round(v_recalc[c] - c_recalc[c], 4) for c in codes}
dlmai_recalc_from_exact = {c: round(sum(driver_weights[p] * p_scores_rounded4[c][p] for p in driver_pillars) - sat_lambda * p_scores_rounded4[c]["P5"], 4) for c in codes}

diff_vc_vs_prod = {c: abs(dlmai_recalc_from_rounded_vc[c] - dlmai_prod[c]) for c in codes}
diff_exact_vs_prod = {c: abs(dlmai_recalc_from_exact[c] - dlmai_prod[c]) for c in codes}

max_diff_vc = max(diff_vc_vs_prod.values())
max_diff_exact = max(diff_exact_vs_prod.values())

print(f"Stage 6 (Final DLMAI Score):")
print(f"  Max diff when using unrounded intermediate (V - C) rounded to 4 decimals vs production: {max_diff_exact:.8e}")
print(f"  Max diff when subtracting pre-rounded V_i and C_i: {max_diff_vc:.8e}")

# Show exact districts where the 1e-4 difference occurs
discrepant_districts = [c for c in codes if diff_vc_vs_prod[c] > 0]
print(f"\nNumber of districts with 1e-4 difference between pre-rounded vs post-rounded subtraction: {len(discrepant_districts)} of 148")
if discrepant_districts:
    print("Sample discrepant districts:")
    for c in discrepant_districts[:5]:
        d_name = df_prod[df_prod["lgd_district_code"] == c]["district_name"].iloc[0]
        v = v_prod[c]
        p = c_prod[c]
        actual_prod = dlmai_prod[c]
        sub_val = round(v - p, 4)
        print(f"  District {c} ({d_name}): Value={v:.4f}, Penalty={p:.4f} -> (V - P)={v-p:.6f} -> rounded(4)={sub_val:.4f} vs Prod CSV={actual_prod:.4f} (Diff = {abs(sub_val - actual_prod):.6f})")
