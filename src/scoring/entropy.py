"""
Intra-Pillar Shannon Information Entropy Weighting Module.
Assigns objective weights to indicators based on discriminatory variance across districts.
"""

import math
from typing import Dict, List, Tuple
import numpy as np


def calculate_entropy_weights(normalized_matrix: Dict[int, Dict[str, float]],
                              indicator_list: List[str],
                              epsilon: float = 1e-6) -> Dict[str, float]:
    """
    Computes Shannon Information Entropy weights for indicator_list across all districts.
    normalized_matrix: {lgd_code: {indicator_id: score_0_to_100}}
    Returns: {indicator_id: weight} such that weights sum to 1.0.
    """
    if not indicator_list:
        return {}
    if len(indicator_list) == 1:
        return {indicator_list[0]: 1.0}

    m = len(normalized_matrix)  # number of districts
    if m <= 1:
        eq = 1.0 / len(indicator_list)
        return {ind: eq for ind in indicator_list}

    k = 1.0 / math.log(m)

    # 1. Construct probability matrix p_ij
    col_sums = {ind: sum(normalized_matrix[code].get(ind, 50.0) + epsilon for code in normalized_matrix)
                for ind in indicator_list}

    entropy_e = {}
    for ind in indicator_list:
        c_sum = col_sums[ind]
        e_val = 0.0
        for code in normalized_matrix:
            val = normalized_matrix[code].get(ind, 50.0) + epsilon
            p_ij = val / c_sum
            e_val += p_ij * math.log(p_ij)
        entropy_e[ind] = -k * e_val

    # 2. Compute utility degree d_j = 1 - e_j
    utility_d = {ind: max(1.0 - entropy_e[ind], 1e-6) for ind in indicator_list}
    total_d = sum(utility_d.values())

    # 3. Normalized weights w_j
    if total_d == 0:
        eq = 1.0 / len(indicator_list)
        return {ind: eq for ind in indicator_list}

    weights = {ind: round(utility_d[ind] / total_d, 6) for ind in indicator_list}
    # Ensure exact sum to 1.0
    w_sum = sum(weights.values())
    first_key = indicator_list[0]
    weights[first_key] = round(weights[first_key] + (1.0 - w_sum), 6)

    return weights
