"""
Jan Aushadhi Kendra ingestion — DLMAI Layer 1 (Pillar 4).

PRACTICAL NOTE on the real source, confirmed by actually inspecting the
live portal: janaushadhi.gov.in/locate-kendra is a filtered SEARCH tool
(Select State -> Select District -> Search), not a one-click bulk export.
There's no "download everything" button -- the realistic collection path
is:
  1. For each of the ~36 states/UTs, run a search with State selected and
     District left blank (returns all districts in that state), then use
     the page's own "DOWNLOAD PDF" option to export that state's results.
  2. That's ~36 PDF downloads, not 700+ district-by-district queries --
     a bounded, one-time manual task, not something to script against a
     JS-rendered form (which would need browser automation, not a simple
     fetch).
  3. Run THIS parser against each of those 36 PDFs.

The real table columns, confirmed from the live page: Sr.No, Kendra Code,
Owner Name, State, District, (Pin Code also appears in the search filters
and is expected in the results table). This module is built against that
real column set, tested against a mock PDF since this sandbox can't reach
the live portal to pull an actual export.

Deliberately includes a Kendra in a district NOT present in the district
master (Wayanad) to prove unmatched districts get surfaced for manual
crosswalk review rather than silently dropped from the Pillar 4 count --
losing a real Kendra count silently would understate that district's
distribution-density score for no good reason.
"""

import re
from pathlib import Path
from collections import defaultdict

import pdfplumber

from district_crosswalk import DistrictCrosswalk


EXPECTED_HEADERS = {"sr.no", "kendra code", "owner name", "state", "district", "pin code"}


def _find_column_index(header_list, keywords, exclude=None):
    for i, h in enumerate(header_list):
        h_clean = _clean(h).lower()
        if exclude and any(e in h_clean for e in exclude):
            continue
        if any(k in h_clean for k in keywords):
            return i
    return None


def extract_kendra_rows(pdf_path: str) -> list:
    """
    Extract Kendra rows from a state-level export PDF using table-aware
    extraction. Supports multi-page tables where headers may or may not repeat.
    """
    rows = []
    active_col_map = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for table in tables:
                if not table:
                    continue
                
                # Check if first row is a header
                first_row = [_clean(c) or "" for c in table[0]]
                kendra_idx = _find_column_index(first_row, ["kendra code", "kendra_code", "kendra"])
                state_idx = _find_column_index(first_row, ["state name", "state"])
                dist_idx = _find_column_index(first_row, ["district name", "district"])
                owner_idx = _find_column_index(first_row, ["owner name", "owner", "name"], exclude=["district", "state"])

                if kendra_idx is not None and (state_idx is not None or dist_idx is not None):
                    active_col_map = {
                        "kendra": kendra_idx,
                        "state": state_idx,
                        "district": dist_idx,
                        "owner": owner_idx
                    }
                    data_rows = table[1:]
                elif active_col_map is not None:
                    data_rows = table
                else:
                    continue

                for raw_row in data_rows:
                    if not raw_row or all(c is None or str(c).strip() == "" for c in raw_row):
                        continue
                    
                    # Skip repeated header rows
                    k_val = _clean(raw_row[active_col_map["kendra"]]) if active_col_map["kendra"] < len(raw_row) else None
                    if k_val and "kendra" in k_val.lower():
                        continue
                    
                    st_val = _clean(raw_row[active_col_map["state"]]) if active_col_map["state"] is not None and active_col_map["state"] < len(raw_row) else None
                    dt_val = _clean(raw_row[active_col_map["district"]]) if active_col_map["district"] is not None and active_col_map["district"] < len(raw_row) else None
                    ow_val = _clean(raw_row[active_col_map["owner"]]) if active_col_map["owner"] is not None and active_col_map["owner"] < len(raw_row) else None
                    
                    # If state or district is empty, attempt to infer state from filename
                    if not st_val:
                        filename_state = Path(pdf_path).stem.replace("_", " ").replace("kendras", "").strip()
                        st_val = filename_state

                    if dt_val or k_val:
                        rows.append({
                            "kendra_code": k_val,
                            "owner_name": ow_val,
                            "state": st_val,
                            "district": dt_val,
                        })
    return rows



def _clean(cell):
    if cell is None:
        return None
    return re.sub(r"\s+", " ", cell).strip()


def aggregate_by_district(rows: list, crosswalk: DistrictCrosswalk) -> dict:
    """
    Groups raw Kendra rows by district, resolves each district name against
    the crosswalk (using the state column as a disambiguation hint -- this
    is exactly the real-world case the crosswalk's state_hint parameter was
    built for, e.g. a plain district name that's ambiguous without state
    context), and returns:
        { 'counts': {lgd_code: kendra_count},
          'unmatched': [(raw_district_name, raw_state, kendra_count), ...] }
    Unmatched districts are NEVER silently dropped -- their raw name, state,
    and count are preserved so a human can resolve them (likely by adding an
    alias once the real spelling/cause is identified) and re-run, rather
    than the count just vanishing from Pillar 4 with no trace.
    """
    raw_counts = defaultdict(int)
    raw_state_for = {}
    for row in rows:
        key = (row["district"], row["state"])
        raw_counts[key] += 1
        raw_state_for[key] = row["state"]

    counts = defaultdict(int)
    unmatched = []
    for (district, state), count in raw_counts.items():
        result = crosswalk.resolve(district, state_hint=state)
        if result.lgd_code:
            counts[result.lgd_code] += count
        else:
            unmatched.append((district, state, count))

    return {"counts": dict(counts), "unmatched": unmatched}
