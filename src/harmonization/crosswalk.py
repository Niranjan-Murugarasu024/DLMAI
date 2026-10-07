"""
District Crosswalk Matcher for South India DLMAI.
Maps arbitrary district names, aliases, and historical spellings onto canonical LGD codes.
"""

import csv
import difflib
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def normalize_name(name: str) -> str:
    """
    Standardizes a district name: lowercase, removes diacritics, punctuation,
    and common suffixes like 'district', 'dist', etc.
    """
    if not name:
        return ""
    name = unicodedata.normalize("NFKD", str(name))
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower().strip()
    for old, new in {
        " district": "", " dist.": "", " dist": "",
        "-": " ", "_": " ", ".": "", ",": "",
    }.items():
        name = name.replace(old, new)
    return " ".join(name.split())


@dataclass
class CanonicalDistrict:
    lgd_code: int
    district_name: str
    state_lgd_code: int
    state_name: str
    census_2011_code: int = 0
    parent_lgd_code: Optional[int] = None
    parent_district_name: Optional[str] = None


@dataclass
class ResolutionResult:
    raw_input: str
    lgd_code: Optional[int] = None
    matched_name: Optional[str] = None
    state_name: Optional[str] = None
    method: str = "unmatched"  # exact | alias | historical | split | fuzzy | ambiguous | unmatched
    confidence: float = 0.0
    candidates: List[Tuple[int, str, str]] = field(default_factory=list)


class SouthDistrictCrosswalk:
    def __init__(self, master_csv_path: str = "data/master/lgd_south_india.csv",
                 crosswalk_csv_path: str = "data/master/district_crosswalk_south.csv",
                 fuzzy_threshold: float = 0.84, ambiguity_margin: float = 0.03):
        self.fuzzy_threshold = fuzzy_threshold
        self.ambiguity_margin = ambiguity_margin
        self.districts: Dict[int, CanonicalDistrict] = {}
        self.name_to_code: Dict[str, List[CanonicalDistrict]] = {}
        self.alias_map: Dict[str, Tuple[int, str, str, float]] = {}  # norm_name -> (lgd_code, canon_name, method, conf)
        self.parent_map: Dict[int, int] = {}  # child_code -> parent_code

        self._load_master(master_csv_path)
        if crosswalk_csv_path:
            self._load_crosswalk(crosswalk_csv_path)

    def _load_master(self, path: str):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = int(row["lgd_district_code"])
                d = CanonicalDistrict(
                    lgd_code=code,
                    district_name=row["district_name"],
                    state_lgd_code=int(row["state_lgd_code"]),
                    state_name=row["state_name"],
                    census_2011_code=int(row.get("census_2011_code", 0) or 0)
                )
                self.districts[code] = d
                norm_dname = normalize_name(d.district_name)
                self.name_to_code.setdefault(norm_dname, []).append(d)

    def _load_crosswalk(self, path: str):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                src_name = normalize_name(row["source_district_name"])
                c_code = int(row["canonical_lgd_code"])
                c_name = row["canonical_district_name"]
                m_type = row.get("mapping_type", "ALIAS")
                conf = float(row.get("confidence", 1.0))
                p_code = row.get("parent_lgd_code")
                if p_code and str(p_code).strip():
                    try:
                        self.parent_map[c_code] = int(p_code)
                        if c_code in self.districts:
                            self.districts[c_code].parent_lgd_code = int(p_code)
                            self.districts[c_code].parent_district_name = row.get("parent_district_name")
                    except ValueError:
                        pass
                self.alias_map[src_name] = (c_code, c_name, m_type, conf)

    def resolve(self, raw_name: str, state_hint: Optional[str] = None) -> ResolutionResult:
        if not raw_name:
            return ResolutionResult(raw_name="", method="unmatched", confidence=0.0)

        norm = normalize_name(raw_name)

        # 1. Check alias / crosswalk dictionary
        if norm in self.alias_map:
            c_code, c_name, m_type, conf = self.alias_map[norm]
            d = self.districts.get(c_code)
            if d:
                # If state hint provided, ensure it matches or is consistent
                if state_hint and normalize_name(state_hint) not in normalize_name(d.state_name) and normalize_name(d.state_name) not in normalize_name(state_hint):
                    pass  # proceed to check other matches
                else:
                    return ResolutionResult(raw_name, d.lgd_code, d.district_name, d.state_name, m_type.lower(), conf)

        # 2. Exact match against canonical names
        if norm in self.name_to_code:
            matches = self.name_to_code[norm]
            filtered = self._filter_by_state(matches, state_hint)
            if len(filtered) == 1:
                d = filtered[0]
                return ResolutionResult(raw_name, d.lgd_code, d.district_name, d.state_name, "exact", 1.0)
            elif len(filtered) > 1:
                return ResolutionResult(
                    raw_name, method="ambiguous", confidence=1.0,
                    candidates=[(c.lgd_code, c.district_name, c.state_name) for c in filtered]
                )

        # 3. Fuzzy match fallback with state filtering
        scored = []
        for d in self.districts.values():
            if state_hint and not self._matches_state(d.state_name, state_hint):
                continue
            ratio = difflib.SequenceMatcher(None, norm, normalize_name(d.district_name)).ratio()
            scored.append((ratio, d))

        if not scored:
            return ResolutionResult(raw_name, method="unmatched", confidence=0.0)

        scored.sort(key=lambda x: -x[0])
        top_score, top_d = scored[0]

        if top_score < self.fuzzy_threshold:
            return ResolutionResult(raw_name, method="unmatched", confidence=round(top_score, 3))

        # Check for ambiguity
        close = [(s, d) for s, d in scored if top_score - s <= self.ambiguity_margin]
        if len(close) > 1:
            return ResolutionResult(
                raw_name, method="ambiguous", confidence=round(top_score, 3),
                candidates=[(d.lgd_code, d.district_name, d.state_name) for _, d in close]
            )

        return ResolutionResult(raw_name, top_d.lgd_code, top_d.district_name, top_d.state_name, "fuzzy", round(top_score, 3))

    def _matches_state(self, state_a: str, state_b: str) -> bool:
        if not state_a or not state_b:
            return True
        na, nb = normalize_name(state_a), normalize_name(state_b)
        return na in nb or nb in na

    def _filter_by_state(self, districts: List[CanonicalDistrict], state_hint: Optional[str]) -> List[CanonicalDistrict]:
        if not state_hint:
            return districts
        filtered = [d for d in districts if self._matches_state(d.state_name, state_hint)]
        return filtered if filtered else districts
