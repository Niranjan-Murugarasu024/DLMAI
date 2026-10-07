"""
Fixed-point Multi-generation District Lineage Inheritance Resolver.
Fills missing indicator observations for newly created child districts from their parent districts.
"""

from typing import Dict, Tuple, Any, Optional
from src.harmonization.crosswalk import SouthDistrictCrosswalk


class SouthInheritanceResolver:
    def __init__(self, crosswalk: SouthDistrictCrosswalk):
        self.parent_map = dict(crosswalk.parent_map)
        self.districts = crosswalk.districts

    def fill_missing(self, values_by_lgd: Dict[int, Any]) -> Tuple[Dict[int, Any], Dict[int, str]]:
        """
        Takes {lgd_code: value_or_None}.
        Returns (filled_dict, status_mask) where status_mask maps:
        lgd_code -> 'OBSERVED' | 'INHERITED_FROM_<parent_code>' | 'STILL_MISSING'
        """
        filled = dict(values_by_lgd)
        mask = {}

        for code, val in values_by_lgd.items():
            if val is not None and val != "":
                mask[code] = "OBSERVED"
            else:
                mask[code] = "STILL_MISSING"

        # Fixed-point loop for multi-generation chains (grandchild -> child -> parent)
        max_iterations = len(self.parent_map) + 2
        for _ in range(max_iterations):
            progress = False
            for child_code, parent_code in self.parent_map.items():
                child_val = filled.get(child_code)
                parent_val = filled.get(parent_code)

                if (child_val is None or child_val == "") and (parent_val is not None and parent_val != ""):
                    filled[child_code] = parent_val
                    mask[child_code] = f"INHERITED_FROM_{parent_code}"
                    progress = True

            if not progress:
                break

        return filled, mask
