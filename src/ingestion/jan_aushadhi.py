"""
Pradhan Mantri Jan Aushadhi Kendra Ingestion Module.
Parses Kendra registry records and deduplicates by Kendra Code.
"""

import re
from typing import Dict, List, Optional, Any, Set
import pdfplumber


def extract_kendra_records_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extracts Jan Aushadhi Kendra records from state PDF exports.
    Fields: kendra_code, kendra_name, district, state, pincode.
    """
    records = []
    seen_codes: Set[str] = set()

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 3:
                        continue
                    # Check for header
                    first_cell = str(row[0]).strip().lower()
                    if "kendra" in first_cell or "s.no" in first_cell or "code" in first_cell:
                        continue

                    kendra_code = str(row[0]).strip()
                    if not kendra_code or kendra_code in seen_codes:
                        continue

                    # Look for district name and pincode across cells
                    district = str(row[1]).strip() if len(row) > 1 else ""
                    address = str(row[2]).strip() if len(row) > 2 else ""

                    # Extract PIN if present
                    pin_match = re.search(r"\b([56]\d{5})\b", address + " " + district)
                    pincode = pin_match.group(1) if pin_match else None

                    seen_codes.add(kendra_code)
                    records.append({
                        "kendra_code": kendra_code,
                        "district": district,
                        "address": address,
                        "pincode": pincode
                    })

    return records
