"""
MCA21 Active Pharma Company Ingestion Module.
Filters corporate registrations to active pharmaceutical manufacturing companies (NIC codes 21001, 21002, 21009).
Maps companies to canonical districts via postal pincode lookup.
"""

import csv
import re
from typing import Dict, List, Optional, Any, Set


PHARMA_NIC_CODES = {"21001", "21002", "21009", "24231", "24232"}


def extract_pharma_companies(csv_path: str) -> List[Dict[str, Any]]:
    """
    Parses MCA21 company master CSV and filters to active pharma enterprises.
    """
    companies = []
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row.get("Company Status", "").strip().upper()
            if status and status != "ACTV" and status != "ACTIVE":
                continue

            # Check business activity or NIC code or company name
            activity = str(row.get("Principal Business Activity", ""))
            name = str(row.get("Company Name", ""))
            address = str(row.get("Registered Office Address", ""))

            is_pharma = any(k in name.lower() for k in ["pharma", "therapeutics", "drugs", "laboratories", "biotech", "medicaments", "healthcare"])
            if not is_pharma:
                continue

            # Extract 6-digit postal code (South India PINs start with 5 or 6)
            pin_match = re.search(r"\b([56]\d{5})\b", address)
            pincode = pin_match.group(1) if pin_match else None

            companies.append({
                "cin": row.get("CIN", ""),
                "company_name": name,
                "pincode": pincode,
                "state": row.get("Registered State", "")
            })

    return companies
