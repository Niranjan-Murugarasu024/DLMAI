"""
Census District Handbook (DCHB) parser — DLMAI Layer 1 (Pillars 1 & 7).

Built against the REAL, verified two-table structure of a District Census
Handbook (confirmed by checking actual published DCHB tables-of-contents,
not assumed from memory):

  1. "Important Statistics" -- a compact one-page summary (total
     population, decadal growth rate, density, sex ratio, literacy rate)
     appearing early in the handbook, before the detailed tables. This is
     the cheapest table to parse and covers most of what Pillars 1 & 7
     actually need.
  2. "District Primary Census Abstract" (PCA) -- a detailed grid with
     separate Total / Rural / Urban rows, used here to derive urban
     population share and the age-0-6 population share.

CORRECTION versus the original framework draft: the PCA table publishes
population in the age-0-6 bracket ONLY (confirmed: this has been a
deliberate, stable feature of the PCA since the 1991 Census, specifically
so child literacy calculations exclude that age group). It does NOT carry
a 0-14 or 60+ breakdown -- those need a separate, less commonly bundled
Census product (the C-series single-year age tables). Pillar 1's
demographic-structure proxy should therefore be "% population age 0-6",
not "0-14% / 60+%" as originally drafted -- see the correction applied to
DLMAI_Framework_Architecture.md alongside this module.

Exact wording on the "Important Statistics" page varies slightly by
district/state edition -- unlike the NFHS patterns (pulled from a real,
verified indicator list), these patterns are keyword-based and should be
checked against an actual downloaded handbook before being trusted at
scale; that's also why parse_important_statistics cross-checks its total
population figure against the PCA table's Total row and flags a
discrepancy rather than silently picking one.
"""

import re
from dataclasses import dataclass, field

import pdfplumber


IMPORTANT_STATS_PATTERNS = {
    "total_population": r"total population",
    "decadal_growth_rate_pct": r"decadal growth rate",
    "density_per_sqkm": r"density.*sq\.?\s*km",
    "sex_ratio": r"sex ratio",
    "literacy_rate_pct": r"literacy rate",
}


@dataclass
class CensusResult:
    district_raw_name: str = None
    important_stats: dict = field(default_factory=dict)
    pca_table: dict = field(default_factory=dict)   # 'Total'/'Rural'/'Urban' -> {population, population_0_6, literates}
    derived: dict = field(default_factory=dict)       # urban_pct, population_0_6_pct, etc.
    warnings: list = field(default_factory=list)


def _clean(cell):
    if cell is None:
        return None
    return re.sub(r"\s+", " ", str(cell)).strip()


def _trailing_number(line: str):
    line_no_itemnum = re.sub(r"^\s*\d+\.\s*", "", line)
    numbers = re.findall(r"\d[\d,]*\.?\d*", line_no_itemnum)
    if not numbers:
        return None
    try:
        return float(numbers[-1].replace(",", ""))
    except ValueError:
        return None


def parse_important_statistics(lines: list) -> dict:
    stats = {}
    for line in lines:
        for indicator_id, pattern in IMPORTANT_STATS_PATTERNS.items():
            if indicator_id in stats:
                continue
            if re.search(pattern, line, re.IGNORECASE):
                value = _trailing_number(line)
                if value is not None:
                    stats[indicator_id] = value
    return stats


def parse_pca_table(pdf) -> dict:
    """
    Looks for the District Primary Census Abstract table -- a ruled table
    with a residence-type column (Total/Rural/Urban) and population
    columns, including the age-0-6 and literates columns.
    """
    pca = {}
    for page in pdf.pages:
        for table in page.extract_tables():
            if not table or len(table) < 2:
                continue
            header = [(_clean(c) or "").lower() for c in table[0]]
            if not any("population" in h for h in header):
                continue
            if not any(h in ("total", "rural", "urban", "residence") for h in header):
                # residence type might be the FIRST column with no header label,
                # or labelled differently -- fall through to row-based detection
                pass
            col_idx = {h: i for i, h in enumerate(header)}
            pop_col = next((i for h, i in col_idx.items() if "population" in h and "0-6" not in h and "0–6" not in h), None)
            pop06_col = next((i for h, i in col_idx.items() if "0-6" in h or "0–6" in h), None)
            lit_col = next((i for h, i in col_idx.items() if "literate" in h), None)
            if pop_col is None:
                continue
            for row in table[1:]:
                if not row or not row[0]:
                    continue
                label = _clean(row[0])
                if label not in ("Total", "Rural", "Urban"):
                    continue
                def _num(idx):
                    if idx is None or idx >= len(row) or row[idx] is None:
                        return None
                    digits = re.sub(r"[^\d.]", "", row[idx])
                    return float(digits) if digits else None
                pca[label] = {
                    "population": _num(pop_col),
                    "population_0_6": _num(pop06_col),
                    "literates": _num(lit_col),
                }
    return pca


def _extract_district_name(lines: list) -> str:
    for ln in lines[:20]:
        # Broadened to include digits and parentheses -- see the matching
        # fix and comment in nfhs_factsheet_parser.py for why (real
        # district names like "24 Parganas (North)" need both).
        m = re.search(r"district\s*[:\-]\s*([A-Za-z0-9 .'()\-]+)", ln, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def parse_census_handbook(pdf_path: str) -> CensusResult:
    result = CensusResult()
    with pdfplumber.open(pdf_path) as pdf:
        all_lines = []
        for page in pdf.pages:
            text = page.extract_text() or ""
            all_lines.extend(ln.strip() for ln in text.split("\n") if ln.strip())

        result.district_raw_name = _extract_district_name(all_lines)
        result.important_stats = parse_important_statistics(all_lines)
        result.pca_table = parse_pca_table(pdf)

    # --- derive Pillar 1 / Pillar 7 indicators from the PCA table ---
    total_row = result.pca_table.get("Total")
    urban_row = result.pca_table.get("Urban")
    if total_row and total_row.get("population"):
        if urban_row and urban_row.get("population") is not None:
            result.derived["urban_population_pct"] = round(
                100 * urban_row["population"] / total_row["population"], 2)
        if total_row.get("population_0_6") is not None:
            result.derived["population_age_0_6_pct"] = round(
                100 * total_row["population_0_6"] / total_row["population"], 2)
        if total_row.get("literates") is not None:
            # NOTE: this is literates / TOTAL population, which will run
            # systematically lower than the official "effective literacy
            # rate" reported on the Important Statistics page (literates /
            # population AGE 7+, since the under-7 age-0-6 bracket is
            # categorically counted as illiterate by Census convention
            # regardless of actual ability). The two numbers are NOT
            # interchangeable -- treat important_stats['literacy_rate_pct']
            # as the authoritative figure for scoring, and this PCA-derived
            # version only as a rough internal cross-check.
            result.derived["literacy_rate_pct_from_pca"] = round(
                100 * total_row["literates"] / total_row["population"], 2)

        # cross-check: Important Statistics' total population should match
        # the PCA table's Total row. A real discrepancy here usually means
        # a parsing error (wrong table matched) rather than a real data
        # conflict -- surfaced as a warning rather than silently trusting
        # one source over the other.
        is_total = result.important_stats.get("total_population")
        if is_total and abs(is_total - total_row["population"]) > max(1, 0.001 * is_total):
            result.warnings.append(
                f"Total population mismatch: Important Statistics says {is_total}, "
                f"PCA Total row says {total_row['population']}")

    return result
