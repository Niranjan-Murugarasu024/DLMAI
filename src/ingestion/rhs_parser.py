"""
MoHFW Rural Health Statistics (RHS) Table Parser for South India DLMAI.
Extracts Sub-Centres, PHCs, CHCs, Sub-Divisional Hospitals, and District Hospitals.
Correctly handles the official 8-column layout (S.No, State, District, SC, PHC, CHC, SDH, DH).
"""

import re
import pdfplumber
from typing import Dict, List, Optional, Any


def clean_cell_text(cell: Any) -> str:
    if cell is None:
        return ""
    return re.sub(r"\s+", " ", str(cell)).strip()


def parse_numeric_cell(cell: Any) -> Optional[float]:
    c = clean_cell_text(cell)
    if not c or c.upper() == "NA" or c == "-":
        return None
    # Strip non-numeric prefixes like 'b ' or footnote markers
    c = re.sub(r"^[a-zA-Z\s]+", "", c)
    c = c.replace(",", "").strip()
    try:
        return float(c)
    except ValueError:
        return None


def extract_all_rhs_rows(pdf_path: str = "data/rhs/district-wise-health-centres.pdf") -> List[Dict[str, Any]]:
    """
    Extracts all district healthcare facility rows from the MoHFW RHS table PDF.
    Returns: list of dicts with keys: state, district, sub_centres, phcs, chcs, sdh, dh.
    """
    rows = []
    current_state = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for raw_row in table:
                    if not raw_row or len(raw_row) < 8:
                        continue

                    sno = clean_cell_text(raw_row[0])
                    state_cell = clean_cell_text(raw_row[1])
                    district_cell = clean_cell_text(raw_row[2])

                    # Update current state tracker
                    if state_cell and "state" not in state_cell.lower() and "union" not in state_cell.lower():
                        current_state = state_cell

                    # Skip headers and total rows
                    if not district_cell or "name of the district" in district_cell.lower() or "total" in district_cell.lower():
                        continue

                    sc = parse_numeric_cell(raw_row[3])
                    phc = parse_numeric_cell(raw_row[4])
                    chc = parse_numeric_cell(raw_row[5])
                    sdh = parse_numeric_cell(raw_row[6])
                    dh = parse_numeric_cell(raw_row[7])

                    if sc is None and phc is None and chc is None:
                        continue

                    rows.append({
                        "state": current_state,
                        "district": district_cell,
                        "sub_centres": sc,
                        "phcs": phc,
                        "chcs": chc,
                        "sdh": sdh,
                        "dh": dh,
                        "hospital_presence": (sdh or 0) + (dh or 0)
                    })

    return rows
