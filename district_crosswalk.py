"""
District Master Crosswalk Engine — DLMAI Layer 2

Resolves any incoming dataset's district reference (free-text name, an
older/historical name, or a partial/misspelled name) onto the canonical
LGD-based district master table. See Section 2 of
DLMAI_Framework_Architecture.md for why this layer exists and has to run
before any indicator data is touched.

IMPORTANT: sample_lgd_seed.csv (bundled alongside this file) is a small,
clearly-illustrative seed of ~20 districts with deliberately tricky real
cases (renames, 2022 Andhra Pradesh bifurcations, ambiguous short names).
It is NOT the real ~780-district LGD master table. Before using this for
real work:
  1. Download the actual district list from lgdirectory.gov.in
     ("View/Download Entities" -> Districts) or the mirrored dataset at
     data.gov.in/resource/local-government-directory-lgd-districts
  2. Reshape it to match the columns below (lgd_code, state_lgd_code,
     state_name, current_name, historical_names, parent_lgd_code,
     effective_from) — historical_names and parent_lgd_code will need to
     be filled in manually/incrementally as you encounter mismatches;
     LGD does not ship a "renamed-from" field directly.
  3. Point DistrictCrosswalk at that file instead of the sample.

Design principle carried over from the framework doc: when a match is
uncertain, this engine flags it rather than silently guessing. An index
that quietly mismatches 10% of rows is worse than one that visibly asks
for 10% of rows to be reviewed by a human.
"""

import csv
import difflib
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path


def normalize(name: str) -> str:
    """Lowercase, strip accents/punctuation, collapse whitespace, drop
    common boilerplate words that differ across Indian government
    datasets ('district', 'dist.', urban/rural markers in parentheses)."""
    if not name:
        return ""
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower().strip()
    for old, new in {
        " district": "", " dist.": "", " dist": "",
        "-": " ", "_": " ", ".": "", ",": "",
    }.items():
        name = name.replace(old, new)
    return " ".join(name.split())


@dataclass
class District:
    lgd_code: str
    state_lgd_code: str
    state_name: str
    current_name: str
    historical_names: list = field(default_factory=list)
    parent_lgd_code: str = None  # set only if carved from another district
    effective_from: str = None


@dataclass
class ResolutionResult:
    raw_input: str
    lgd_code: str = None
    matched_name: str = None
    method: str = "unmatched"   # exact | historical | manual_alias | fuzzy | ambiguous | unmatched
    confidence: float = 0.0
    candidates: list = field(default_factory=list)  # populated when ambiguous


class DistrictCrosswalk:
    def __init__(self, master_csv_path, alias_csv_path=None,
                 fuzzy_threshold=0.84, ambiguity_margin=0.03):
        """
        fuzzy_threshold: minimum similarity score to auto-accept a fuzzy match
        ambiguity_margin: if a second candidate scores within this margin of
            the top score, treat the match as ambiguous rather than picking
            one — this is what catches cases like plain 'Bangalore' being
            equally close to both Bengaluru Urban and Bengaluru Rural.
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.ambiguity_margin = ambiguity_margin
        self.districts = self._load_master(master_csv_path)
        self.manual_aliases = self._load_aliases(alias_csv_path) if alias_csv_path else {}
        self._build_index()

    def _load_master(self, path):
        out = []
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                hist = [h.strip() for h in row.get("historical_names", "").split("|") if h.strip()]
                out.append(District(
                    lgd_code=row["lgd_code"],
                    state_lgd_code=row["state_lgd_code"],
                    state_name=row["state_name"],
                    current_name=row["current_name"],
                    historical_names=hist,
                    parent_lgd_code=row.get("parent_lgd_code") or None,
                    effective_from=row.get("effective_from") or None,
                ))
        return out

    def _load_aliases(self, path):
        aliases = {}
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                aliases[normalize(row["raw_name"])] = (row["lgd_code"], row.get("note", ""))
        return aliases

    def _build_index(self):
        # norm_name -> list of (lgd_code, current_name, state_name) — a list
        # because more than one district can normalize to a near-identical key
        self.index = {}
        self.by_code = {}
        for d in self.districts:
            self.by_code[d.lgd_code] = d
            for name in [d.current_name] + d.historical_names:
                key = normalize(name)
                self.index.setdefault(key, []).append(d)

    def resolve(self, raw_name, state_hint=None) -> ResolutionResult:
        norm = normalize(raw_name)

        # 1. Manual alias table — for true renames a fuzzy matcher won't
        #    catch because the strings share little or no overlap
        #    (e.g. an old "Bombay City" -> current "Mumbai City").
        if norm in self.manual_aliases:
            code, note = self.manual_aliases[norm]
            d = self.by_code.get(code)
            if d:
                return ResolutionResult(raw_name, d.lgd_code, d.current_name, "manual_alias", 1.0)


        # 2. Exact match against current or historical names
        candidates = self.index.get(norm)
        if candidates:
            candidates = self._filter_by_state(candidates, state_hint)
            if len(candidates) == 1:
                d = candidates[0]
                method = "exact" if normalize(d.current_name) == norm else "historical"
                return ResolutionResult(raw_name, d.lgd_code, d.current_name, method, 1.0)
            elif len(candidates) > 1:
                return ResolutionResult(raw_name, method="ambiguous", confidence=1.0,
                                         candidates=[(c.lgd_code, c.current_name, c.state_name) for c in candidates])

        # 3. Fuzzy fallback, with ambiguity detection
        scored = []
        for key, ds in self.index.items():
            ds_filtered = self._filter_by_state(ds, state_hint)
            if not ds_filtered:
                continue
            score = difflib.SequenceMatcher(None, norm, key).ratio()
            for d in ds_filtered:
                scored.append((score, d))
        if not scored:
            return ResolutionResult(raw_name, method="unmatched", confidence=0.0)

        scored.sort(key=lambda x: -x[0])
        top_score, top_d = scored[0]
        close = [(s, d) for s, d in scored if top_score - s <= self.ambiguity_margin]
        # dedupe by lgd_code while preserving order
        seen, close_unique = set(), []
        for s, d in close:
            if d.lgd_code not in seen:
                seen.add(d.lgd_code)
                close_unique.append((s, d))

        if top_score < self.fuzzy_threshold:
            return ResolutionResult(raw_name, method="unmatched", confidence=round(top_score, 3))

        if len(close_unique) > 1:
            return ResolutionResult(raw_name, method="ambiguous", confidence=round(top_score, 3),
                                     candidates=[(d.lgd_code, d.current_name, d.state_name) for _, d in close_unique])

        return ResolutionResult(raw_name, top_d.lgd_code, top_d.current_name, "fuzzy", round(top_score, 3))

    def _filter_by_state(self, districts, state_hint):
        if not state_hint:
            return districts
        sh = normalize(state_hint)
        filtered = [d for d in districts if normalize(d.state_name) == sh]
        return filtered if filtered else districts  # fall back if hint doesn't narrow anything

    def resolve_batch(self, raw_names, state_hints=None):
        state_hints = state_hints or [None] * len(raw_names)
        return [self.resolve(n, s) for n, s in zip(raw_names, state_hints)]


class InheritanceResolver:
    """
    For districts created after a given source's vintage, fills missing
    indicator values from the parent (pre-split) district and flags them
    as inherited — never leaves a silent null and never invents a number
    that isn't traceable to a real source.
    """
    def __init__(self, crosswalk: DistrictCrosswalk):
        self.parent_map = {d.lgd_code: d.parent_lgd_code
                            for d in crosswalk.districts if d.parent_lgd_code}

    def fill_missing(self, values_by_lgd_code: dict):
        """
        values_by_lgd_code: {lgd_code: value_or_None}
        Returns (filled_dict, confidence_mask) where confidence_mask maps
        lgd_code -> 'native' | 'inherited_from_<parent_code>' | 'still_missing'

        Runs as a FIXPOINT loop, not a single pass: a grandchild district
        (carved from a district that was itself carved from another) only
        inherits correctly if its immediate parent has ALREADY been
        filled by the time it's checked -- and that depends entirely on
        row order in the district master CSV, which has no guaranteed
        relationship to actual district lineage (e.g. "Bapatla" sorts
        alphabetically before its own parent "Guntur"). A single pass
        silently leaves multi-generation chains unresolved whenever a
        child happens to be listed before its parent. Looping until no
        more fills occur resolves any chain depth correctly regardless of
        row order, capped at a sane iteration limit as a defensive
        guard against a malformed/cyclic parent_map (which would
        indicate a real data error in the master table, not something to
        silently loop forever on).
        """
        filled = dict(values_by_lgd_code)
        mask = {}
        for code, value in values_by_lgd_code.items():
            mask[code] = "native" if value not in (None, "") else "still_missing"

        max_passes = len(self.parent_map) + 1   # a correct chain can be at most this deep
        for _ in range(max_passes):
            made_progress = False
            for code, parent_code in self.parent_map.items():
                if filled.get(code) in (None, "") and parent_code in filled and filled[parent_code] not in (None, ""):
                    filled[code] = filled[parent_code]
                    mask[code] = f"inherited_from_{parent_code}"
                    made_progress = True
            if not made_progress:
                break
        return filled, mask
