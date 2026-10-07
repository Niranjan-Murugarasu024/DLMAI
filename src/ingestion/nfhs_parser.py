"""
Robust NFHS-5 District Factsheet Parser for South India.
Extracts health, nutrition, and household amenity indicators using unit-anchored regex.
Distinguishes NFHS-5 (2019-21) values from historical NFHS-4 columns and footnote superscripts.
"""

import re
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import pdfplumber


NFHS_INDICATOR_PATTERNS = {
    # Pillar 1
    "stunting_pct": r"stunted\s*\(height-for-age\)",
    "wasting_pct": r"wasted\s*\(weight-for-height\)",
    "underweight_pct": r"underweight\s*\(weight-for-age\)",
    "hypertension_combined_pct": r"elevated blood pressure.*taking medicine|control blood pressure\s*\(%\)",
    "diabetes_combined_pct": r"blood sugar level.*taking medicine|control blood sugar level",
    # Pillar 2
    "clean_fuel_pct": r"clean fuel for cooking",
    "sanitation_pct": r"improved sanitation facility",
    "insurance_pct": r"health insurance/financing scheme",
    "oope_delivery_rs": r"out-of-pocket expenditure per delivery",
}

EXCLUSIONS = {
    "wasting_pct": r"severely",
}

DUAL_INDICATORS = {"hypertension_combined_pct", "diabetes_combined_pct"}


@dataclass
class NFHSFactsheetResult:
    district_raw_name: str
    state_raw_name: Optional[str] = None
    values: Dict[str, float] = field(default_factory=dict)
    found_indicators: Set[str] = field(default_factory=set)
    missing_indicators: Set[str] = field(default_factory=set)
    provenance_file: Optional[str] = None


def extract_pdf_lines(pdf_path: str) -> List[str]:
    """Extracts text lines from PDF using pypdfium2 with pdfplumber fallback."""
    lines = []
    try:
        import pypdfium2
        doc = pypdfium2.PdfDocument(pdf_path)
        for page in doc:
            tp = page.get_textpage()
            txt = tp.get_text_range() or ""
            lines.extend(txt.split("\n"))
    except Exception:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text() or ""
                lines.extend(txt.split("\n"))
    return [l.strip() for l in lines if l.strip()]


def parse_nfhs_line_value(line: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extracts (nfhs5_value, nfhs4_value) from a table line by anchoring on the unit marker.
    Matches: ... (%) <nfhs5_val> <nfhs4_val>
    """
    # Look for unit marker: (%), (Rs.), etc.
    m = re.search(r"\(\s*(?:%|Rs\.|females[^\)]*)\s*\)\s*([0-9,]+(?:\.[0-9]+)?|\*|\([0-9.]+\)|na)\s*([0-9,]+(?:\.[0-9]+)?|\*|\([0-9.]+\)|na)?", line, re.IGNORECASE)
    if m:
        def to_float(val_str):
            if not val_str or val_str in ("*", "na", "None"):
                return None
            val_str = val_str.replace("(", "").replace(")", "").replace(",", "")
            try:
                return float(val_str)
            except ValueError:
                return None

        v5 = to_float(m.group(1))
        v4 = to_float(m.group(2)) if m.group(2) else None
        return v5, v4

    # Fallback: find trailing numbers
    numbers = re.findall(r"\d[\d,]*\.?\d*", line)
    if numbers:
        raw = numbers[-1].replace(",", "")
        try:
            return float(raw), None
        except ValueError:
            return None, None
    return None, None


def extract_district_state_from_header(lines: List[str], pdf_path: str = None) -> Tuple[Optional[str], Optional[str]]:
    """Extracts district name and state name from factsheet header or file stem."""
    # 1. Check 'District Fact Sheet' block on Page 1
    for i, ln in enumerate(lines[:15]):
        if re.search(r"district\s*fact\s*she\s*et", ln, re.IGNORECASE):
            if i + 1 < len(lines):
                d_candidate = lines[i + 1].strip()
                s_candidate = lines[i + 2].strip() if i + 2 < len(lines) else None
                if d_candidate and not any(k in d_candidate.lower() for k in ["ministry", "survey", "health", "india", "population"]):
                    return d_candidate, s_candidate

    # 2. Filename parser: NFHS-5_DistFact_<State>_<District>__<District>.pdf
    if pdf_path:
        filename = Path(pdf_path).stem
        m = re.search(r"DistFact_([^_]+)_([^_]+)__", filename)
        if m:
            return m.group(2).strip(), m.group(1).strip()
        m = re.search(r"DistFact_([^_]+)_(.+)", filename)
        if m:
            return m.group(2).strip(), m.group(1).strip()

    return None, None


def parse_nfhs_factsheet(pdf_path: str) -> NFHSFactsheetResult:
    lines = extract_pdf_lines(pdf_path)
    d_name, s_name = extract_district_state_from_header(lines, pdf_path)
    result = NFHSFactsheetResult(district_raw_name=d_name or Path(pdf_path).stem, state_raw_name=s_name, provenance_file=pdf_path)

    occurrence_count = {k: 0 for k in DUAL_INDICATORS}

    for line in lines:
        for ind_id, pattern in NFHS_INDICATOR_PATTERNS.items():
            if not re.search(pattern, line, re.IGNORECASE):
                continue
            excl = EXCLUSIONS.get(ind_id)
            if excl and re.search(excl, line, re.IGNORECASE):
                continue

            v5, _ = parse_nfhs_line_value(line)
            if v5 is None:
                continue

            if ind_id in DUAL_INDICATORS:
                occurrence_count[ind_id] += 1
                suffix = "women" if occurrence_count[ind_id] == 1 else "men"
                key = f"{ind_id}_{suffix}"
            else:
                key = ind_id

            result.values[key] = v5
            result.found_indicators.add(ind_id)

    # Calculate combined hypertension & diabetes mean if both genders found
    if "hypertension_combined_pct_women" in result.values and "hypertension_combined_pct_men" in result.values:
        result.values["nfhs_hypertension_combined_pct"] = round(
            (result.values["hypertension_combined_pct_women"] + result.values["hypertension_combined_pct_men"]) / 2.0, 2
        )
    elif "hypertension_combined_pct_women" in result.values:
        result.values["nfhs_hypertension_combined_pct"] = result.values["hypertension_combined_pct_women"]

    if "diabetes_combined_pct_women" in result.values and "diabetes_combined_pct_men" in result.values:
        result.values["nfhs_diabetes_combined_pct"] = round(
            (result.values["diabetes_combined_pct_women"] + result.values["diabetes_combined_pct_men"]) / 2.0, 2
        )
    elif "diabetes_combined_pct_women" in result.values:
        result.values["nfhs_diabetes_combined_pct"] = result.values["diabetes_combined_pct_women"]

    # Remap base indicator keys to standard names
    for base_key in ["stunting_pct", "wasting_pct", "underweight_pct", "clean_fuel_pct", "sanitation_pct", "insurance_pct", "oope_delivery_rs"]:
        if base_key in result.values:
            result.values[f"nfhs_{base_key}"] = result.values[base_key]

    result.missing_indicators = set(NFHS_INDICATOR_PATTERNS) - result.found_indicators
    return result
