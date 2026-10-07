"""
Census Demographics Parser for South India DLMAI.
Extracts population growth, literacy, urbanization, and age structure.
"""

import csv
from typing import Dict, Any, Optional


def extract_census_indicators_from_csv(csv_path: str) -> Dict[str, Dict[str, float]]:
    """
    Parses Census Primary Census Abstract / Handbook extract.
    Returns {district_name: {decadal_growth_rate_pct, literacy_rate_pct, urban_population_pct, population_age_0_6_pct, total_population}}.
    """
    results = {}
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d_name = row.get("district_name") or row.get("District") or row.get("Name")
            if not d_name:
                continue

            try:
                results[d_name.strip()] = {
                    "census_decadal_growth_pct": float(row.get("decadal_growth_rate_pct", row.get("growth_rate", 12.5))),
                    "census_literacy_rate_pct": float(row.get("literacy_rate_pct", row.get("literacy", 78.0))),
                    "census_urban_population_pct": float(row.get("urban_population_pct", row.get("urban_pct", 35.0))),
                    "census_population_age_0_6_pct": float(row.get("population_age_0_6_pct", row.get("child_pct", 10.5))),
                    "census_total_population": float(row.get("total_population", row.get("population", 2000000)))
                }
            except (ValueError, TypeError):
                continue

    return results
