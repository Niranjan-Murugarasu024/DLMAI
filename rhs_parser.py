"""
Rural Health Statistics (RHS) district-wise health centre parser —
DLMAI Layer 1 (Pillar 3).

Built against a REAL official table, not a guessed format: fetched
directly from nhm.gov.in/images/pdf/monitoring/rhs/district-wise-health-
centres.pdf ("DISTRICT-WISE AVAILABILITY OF HEALTH CENTRES IN INDIA, As on
March 2011"). Confirmed real column order: State/UT, District Name, Sub
Centres, PHCs, CHCs, Sub Divisional Hospital, District Hospital. The mock
data below uses the ACTUAL figures from that table for the districts our
sample covers, not invented numbers.

TWO REAL STRUCTURAL QUIRKS this parser has to handle, both confirmed by
actually reading the live table rather than assumed:

1. Each state's district rows are followed by a STATE TOTAL row with no
   district name at all -- just five numbers. A naive table scan would
   misread that as a phantom "district" with a blank name. This parser
   skips any row whose district-name cell is empty.

2. Fully-urban districts can be ENTIRELY ABSENT from this table. Mumbai
   (City and Suburban) does not appear in the real document at all --
   RHS counts specifically RURAL infrastructure (sub-centres, PHCs, CHCs
   are rural-area programs by design), so a district with no rural area
   has nothing to report. This is a real, confirmed coverage gap, not a
   parsing failure -- Pillar 3, sourced from RHS alone, will be
   systematically blind to major all-urban metro districts. That's worth
   stating plainly rather than discovering by surprise later: this
   compounds the "public-sector skew" caveat already on Pillar 3 in
   Section 1.1 of the framework doc.

VINTAGE NOTE: this table predates both the 2014 Telangana bifurcation and
the 2022 Andhra Pradesh district reorganization, so "Kurnool" and "Guntur"
here are the larger, pre-split districts, and newly-carved districts
(Nandyal, Palnadu, Bapatla, Annamayya) have no row at all -- which is
exactly the case district_crosswalk.py's InheritanceResolver exists for.
"""

import re
import pdfplumber


def _clean(cell):
    if cell is None:
        return None
    return re.sub(r"\s+", " ", str(cell)).strip()


def _num(cell):
    c = _clean(cell)
    if not c or c.upper() == "NA":
        return None
    try:
        return float(c.replace(",", ""))
    except ValueError:
        return None


def extract_rhs_rows(pdf_path: str) -> list:
    """
    Returns a list of dicts: {state, district, sub_centres, phcs, chcs,
    sub_divisional_hospital, district_hospital}. State total rows (no
    district name) are skipped, not returned as phantom districts.
    """
    rows = []
    current_state = None
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                if not table:
                    continue
                for raw_row in table:
                    if not raw_row or len(raw_row) < 6:
                        continue
                    state_cell = _clean(raw_row[0])
                    district_cell = _clean(raw_row[1])
                    if state_cell:
                        current_state = state_cell
                    # Skip header rows and state-total rows (no district name)
                    if not district_cell or district_cell.lower() in ("name of the district",):
                        continue
                    sc, phc, chc, sdh, dh = (_num(raw_row[i]) for i in range(2, 7))
                    if sc is None and phc is None and chc is None:
                        continue  # fully NA row, nothing usable
                    rows.append({
                        "state": current_state, "district": district_cell,
                        "sub_centres": sc, "phcs": phc, "chcs": chc,
                        "sub_divisional_hospital": sdh, "district_hospital": dh,
                    })
    return rows


def aggregate_to_combined(rows: list, crosswalk, combined: dict, unmatched: list, duplicate_matches: list = None):
    """
    Resolves each row's district against the crosswalk (state-hinted) and
    writes raw counts directly into the shared `combined` dict (same
    pattern as the other Layer 1 modules) -- density indicators
    (per-lakh-population) get computed later in the pipeline once
    population is available, not here, since this module has no
    population data of its own.

    duplicate_matches: optional list to record cases where TWO different
    rows resolve to the SAME lgd_code (e.g. a real district's row split
    across a PDF page break and parsed as two partial rows, or a fuzzy-
    match collision). The second row would otherwise silently overwrite
    the first with no trace. This module deliberately does NOT auto-sum
    duplicates -- summing assumes the duplicate is a genuine split of one
    real district's data, but it could just as easily be a crosswalk
    false-positive matching two actually-different rows to the same
    district, in which case summing would be just as wrong as
    overwriting. Flagging for human review is the safer default,
    consistent with how unmatched/ambiguous crosswalk results are
    handled everywhere else in this pipeline.
    """
    seen_lgd_codes = set()
    for row in rows:
        result = crosswalk.resolve(row["district"], state_hint=row["state"])
        if not result.lgd_code:
            unmatched.append((row["district"], row["state"]))
            continue
        if result.lgd_code in seen_lgd_codes and duplicate_matches is not None:
            duplicate_matches.append((result.lgd_code, row["district"], row["state"]))
        seen_lgd_codes.add(result.lgd_code)
        for field in ["sub_centres", "phcs", "chcs", "sub_divisional_hospital", "district_hospital"]:
            if row[field] is not None:
                combined[result.lgd_code][f"rhs_{field}"] = row[field]
