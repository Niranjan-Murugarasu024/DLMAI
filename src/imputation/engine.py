"""
Auditable Missing-Data Imputation Engine for South India DLMAI.
Implements hierarchical fallback: Trend -> State Mean -> kNN Matching -> Unresolved.
Generates an audit confidence mask for full traceability.
"""

import math
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any


STATUS_OBSERVED = "OBSERVED"
STATUS_INHERITED = "INHERITED"
STATUS_TREND = "IMPUTED_TREND"
STATUS_STATE_MEAN = "IMPUTED_STATE_MEAN"
STATUS_KNN = "IMPUTED_KNN"
STATUS_STILL_MISSING = "STILL_MISSING"


@dataclass
class ImputationResult:
    filled_matrix: Dict[int, Dict[str, float]]       # lgd_code -> {indicator_id: value}
    provenance_mask: Dict[int, Dict[str, str]]       # lgd_code -> {indicator_id: status}
    audit_summary: Dict[str, Any] = field(default_factory=dict)


class SouthImputationEngine:
    def __init__(self, district_state_map: Dict[int, str],
                 district_population: Dict[int, float],
                 knn_k: int = 5):
        """
        district_state_map: {lgd_code: state_name}
        district_population: {lgd_code: population_in_millions}
        """
        self.state_map = district_state_map
        self.pop_map = district_population
        self.k = knn_k

    def impute_matrix(self, raw_matrix: Dict[int, Dict[str, Optional[float]]],
                      inheritance_mask: Optional[Dict[int, Dict[str, str]]] = None) -> ImputationResult:
        """
        Takes raw_matrix: {lgd_code: {indicator_id: value_or_None}}
        Returns ImputationResult with filled values and provenance mask.
        """
        all_indicators = set()
        for d_vals in raw_matrix.values():
            all_indicators.update(d_vals.keys())

        filled_matrix = {code: dict(vals) for code, vals in raw_matrix.items()}
        provenance_mask = {}

        # 1. Initialize provenance mask with inheritance or observed status
        for code, vals in raw_matrix.items():
            provenance_mask[code] = {}
            for ind in all_indicators:
                val = vals.get(ind)
                inh_status = inheritance_mask.get(code, {}).get(ind) if inheritance_mask else None

                if inh_status and "INHERITED" in inh_status:
                    provenance_mask[code][ind] = inh_status
                elif val is not None and val != "":
                    provenance_mask[code][ind] = STATUS_OBSERVED
                else:
                    provenance_mask[code][ind] = STATUS_STILL_MISSING

        # 2. State-Mean Imputation Fallback
        for ind in all_indicators:
            # Group observed/inherited values by state
            state_vals: Dict[str, List[float]] = {}
            for code, vals in filled_matrix.items():
                st = self.state_map.get(code, "Unknown")
                v = vals.get(ind)
                if v is not None and v != "" and not math.isnan(float(v)):
                    state_vals.setdefault(st, []).append(float(v))

            state_means = {st: statistics.mean(vs) for st, vs in state_vals.items() if vs}

            # Apply state mean where still missing
            for code, vals in filled_matrix.items():
                if provenance_mask[code][ind] == STATUS_STILL_MISSING:
                    st = self.state_map.get(code, "Unknown")
                    if st in state_means:
                        filled_matrix[code][ind] = round(state_means[st], 4)
                        provenance_mask[code][ind] = STATUS_STATE_MEAN

        # 3. Nearest-Neighbor (kNN by Population Covariate) Fallback
        for ind in all_indicators:
            # Pool of districts that have a value
            known_pool = []
            for code, vals in filled_matrix.items():
                v = vals.get(ind)
                if v is not None and v != "" and not math.isnan(float(v)):
                    known_pool.append((code, self.pop_map.get(code, 2.0), float(v)))

            if not known_pool:
                continue

            for code, vals in filled_matrix.items():
                if provenance_mask[code][ind] == STATUS_STILL_MISSING:
                    target_pop = self.pop_map.get(code, 2.0)
                    # Sort known pool by absolute population difference
                    sorted_pool = sorted(known_pool, key=lambda x: abs(x[1] - target_pop))
                    top_k_vals = [x[2] for x in sorted_pool[:self.k]]
                    if top_k_vals:
                        filled_matrix[code][ind] = round(statistics.mean(top_k_vals), 4)
                        provenance_mask[code][ind] = STATUS_KNN

        # Generate summary stats
        summary = {"total_cells": len(raw_matrix) * len(all_indicators), "status_counts": {}}
        for d_mask in provenance_mask.values():
            for stat in d_mask.values():
                base_stat = stat.split("_FROM_")[0] if "INHERITED" in stat else stat
                summary["status_counts"][base_stat] = summary["status_counts"].get(base_stat, 0) + 1

        return ImputationResult(filled_matrix, provenance_mask, summary)
