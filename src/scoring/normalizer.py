"""
Direction-Aware Normalization Module for South India DLMAI.
Supports positive indicators, negative indicators, and robust scaling alternatives.
"""

from typing import Dict, Optional, Any
import numpy as np


def min_max_normalize(values: Dict[int, Optional[float]], direction: str = "POSITIVE",
                      scale_min: float = 0.0, scale_max: float = 100.0) -> Dict[int, float]:
    """
    Normalizes a dictionary of {lgd_code: value} to [scale_min, scale_max].
    Direction:
      'POSITIVE' -> higher raw value gives higher score
      'NEGATIVE' -> higher raw value gives lower score (inversion)
      'SATURATION_DAMPENER' -> higher raw value gives higher saturation intensity
    """
    valid_nums = [float(v) for v in values.values() if v is not None and not np.isnan(float(v))]
    if not valid_nums:
        return {code: 50.0 for code in values}

    x_min = min(valid_nums)
    x_max = max(valid_nums)
    range_val = x_max - x_min

    normalized = {}
    for code, val in values.items():
        if val is None or np.isnan(float(val)):
            normalized[code] = 50.0
            continue

        v = float(val)
        if range_val == 0:
            normalized[code] = 50.0
        elif direction == "NEGATIVE":
            normalized[code] = round(((x_max - v) / range_val) * (scale_max - scale_min) + scale_min, 4)
        else:  # POSITIVE or SATURATION_DAMPENER
            normalized[code] = round(((v - x_min) / range_val) * (scale_max - scale_min) + scale_min, 4)

    return normalized
