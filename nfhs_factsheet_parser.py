"""
NFHS district factsheet parser — DLMAI Layer 1 (ingestion) for Pillars 1 & 2.

Extracts the Pillar 1 / Pillar 2 indicators from an NFHS district factsheet
PDF. The indicator text patterns below are NOT guessed — they're built from
the real NFHS-5 (2019-21) district indicator list, pulled directly from the
official factsheet-derived dataset (pratapvardhan/NFHS-5 on GitHub, itself
sourced from rchiips.org/nfhs/) and checked line by line. See the
"VERIFIED AGAINST REAL DATA" note in DLMAI_Framework_Architecture.md
Section 1.1 for what changed as a result.

CURRENT SOURCE: use NFHS-5 (2019-21) factsheets — NFHS-6 (2023-24) was
fielded across 715 districts but its district-level factsheets are not yet
published as of mid-2026 (national/state tables only so far). Swap the
source PDFs for NFHS-6's once district tables are released; the patterns
below should keep working since NFHS rounds reuse near-identical wording
for trend comparability, but re-verify a handful of factsheets after the
swap rather than assuming.

KNOWN QUIRK this parser handles: a few indicators (hypertension, diabetes)
are printed TWICE in the factsheet under separate "Women" and "Men"
sub-headings, using IDENTICAL indicator text both times. A text-only
scan (no access to the PDF's visual sub-headings) can't always tell which
occurrence is which from wording alone -- this parser captures both, in
the order encountered, and labels them by position (first = Women, second
= Men, matching standard NFHS factsheet ordering). VERIFY this against an
actual downloaded factsheet's section headers before trusting the labels
blindly; it's a reasonable assumption, not a certainty.
"""

import re
import os
from pathlib import Path
from dataclasses import dataclass, field

import pdfplumber


INDICATOR_PATTERNS = {
    # --- Pillar 1: nutrition / disease burden ---
    "stunting_pct": r"stunted\s*\(height-for-age\)",
    "wasting_pct": r"wasted\s*\(weight-for-height\)",
    "underweight_pct": r"underweight\s*\(weight-for-age\)",
    "hypertension_combined_pct": r"elevated blood pressure.*taking medicine|control blood pressure\s*\(%\)",
    "diabetes_combined_pct": r"blood sugar level.*taking medicine",

    # --- Pillar 2: affordability proxy (household amenities + insurance + OOPE) ---
    "electricity_pct": r"households with electricity",
    "clean_fuel_pct": r"clean fuel for cooking",
    "drinking_water_pct": r"improved drinking-water source",
    "sanitation_pct": r"improved sanitation facility",
    "insurance_pct": r"health insurance/financing scheme",
    "oope_delivery_rs": r"out-of-pocket expenditure per delivery",
}

EXCLUSION_PATTERNS = {
    "wasting_pct": r"severely",
}

DUAL_OCCURRENCE_INDICATORS = {"hypertension_combined_pct", "diabetes_combined_pct"}


@dataclass
class FactsheetResult:
    district_raw_name: str = None
    values: dict = field(default_factory=dict)        # indicator_id -> value (or _women/_men suffixed)
    found: set = field(default_factory=set)
    missing: set = field(default_factory=set)
    unparsed_lines: list = field(default_factory=list)  # lines that matched a pattern but yielded no number


def extract_text_lines(pdf_path: str) -> list:
    """Pull every line of text from every page, in order using fast pypdfium2 with pdfplumber fallback."""
    lines = []
    try:
        import pypdfium2
        doc = pypdfium2.PdfDocument(pdf_path)
        for page in doc:
            textpage = page.get_textpage()
            text = textpage.get_text_range() or ""
            lines.extend(text.split("\n"))
    except Exception:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                lines.extend(text.split("\n"))
    return [ln.strip() for ln in lines if ln.strip()]



def _extract_trailing_number(line: str):
    """
    Pull the value off the end of a factsheet line.
    """
    line_no_itemnum = re.sub(r"^\s*\d+\.\s*", "", line)
    numbers = re.findall(r"\d[\d,]*\.?\d*", line_no_itemnum)
    if not numbers:
        return None
    raw = numbers[-1].replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None


def _extract_district_name(lines: list, pdf_path: str = None) -> str:
    """
    Extracts the district name from the factsheet header or filename.
    """
    # 1. Look for explicit 'District: <Name>'
    for ln in lines[:20]:
        m = re.search(r"district\s*:\s*([A-Za-z0-9 .'()\-]+)", ln, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    # 2. Look for 'District Fact Sheet' header followed by District Name on next line
    for i, ln in enumerate(lines[:10]):
        if re.search(r"district\s*fact\s*she\s*et", ln, re.IGNORECASE):
            if i + 1 < len(lines):
                candidate = lines[i + 1].strip()
                if candidate and not any(k in candidate.lower() for k in ["ministry", "survey", "health", "india"]):
                    return candidate

    # 3. Extract from filename (e.g. NFHS-5_DistFact_Tamil Nadu_Coimbatore__Coimbatore.pdf or Coimbatore.pdf)
    if pdf_path:
        filename = Path(pdf_path).stem
        m = re.search(r"DistFact_[^_]+_([^_]+)__", filename)
        if m:
            return m.group(1).strip()
        # Pattern: DistFact_State_District.pdf
        m = re.search(r"DistFact_[^_]+_(.+)", filename)
        if m:
            return m.group(1).strip()
        # Fallback to plain filename without 'mock_' prefix
        plain = filename.replace("mock_", "").replace("_factsheet", "").replace("_", " ").strip()
        return plain

    return None


def parse_factsheet_pdf(pdf_path: str) -> FactsheetResult:
    lines = extract_text_lines(pdf_path)
    result = FactsheetResult(district_raw_name=_extract_district_name(lines, pdf_path))

    occurrence_count = {k: 0 for k in DUAL_OCCURRENCE_INDICATORS}

    for line in lines:
        for indicator_id, pattern in INDICATOR_PATTERNS.items():
            if not re.search(pattern, line, re.IGNORECASE):
                continue
            exclusion = EXCLUSION_PATTERNS.get(indicator_id)
            if exclusion and re.search(exclusion, line, re.IGNORECASE):
                continue
            value = _extract_trailing_number(line)
            if value is None:
                result.unparsed_lines.append((indicator_id, line))
                continue
            if indicator_id in DUAL_OCCURRENCE_INDICATORS:
                occurrence_count[indicator_id] += 1
                suffix = "women" if occurrence_count[indicator_id] == 1 else "men"
                key = f"{indicator_id}_{suffix}"
            else:
                key = indicator_id
            result.values[key] = value
            result.found.add(indicator_id)

    result.missing = set(INDICATOR_PATTERNS) - result.found
    return result


def parse_factsheet_batch(pdf_paths: list) -> list:
    results = []
    for path in pdf_paths:
        r = parse_factsheet_pdf(path)
        results.append(r)
        if r.missing:
            print(f"[warn] {path}: missing {len(r.missing)}/{len(INDICATOR_PATTERNS)} "
                  f"indicators -> {sorted(r.missing)}")
        if r.unparsed_lines:
            print(f"[warn] {path}: matched but couldn't extract a number on "
                  f"{len(r.unparsed_lines)} line(s) -- inspect these manually")
    return results

