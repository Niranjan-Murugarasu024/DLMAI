"""
MCA21 Company Master Data ingestion — DLMAI Layer 1 (Pillar 5).

Built against the REAL, verified bulk dataset structure (data.gov.in's
"Company Master Data" catalog page, confirmed fields): CIN, Company Name,
Company Status, Company Class, Company Category, Authorized Capital in
INR, Paid-up Capital in INR, Date of Registration, Registered State,
Registrar of Companies, Principal Business Activity, Registered Office
Address, Sub Category.

Confirmed real NIC-2008 codes used for pharma classification (verified,
not guessed):
  21001 - Manufacture of medicinal substances (antibiotics, vitamins, etc.)
  21002 - Manufacture of allopathic pharmaceutical preparations
  21009 - Manufacture of other pharmaceutical & botanical products
  (all three are Class 2100, Division 21 -- "Manufacture of
  pharmaceuticals, medicinal chemical and botanical products")
  46497 - Wholesale of pharmaceutical and medical goods
  4772   - Retail sale of pharmaceutical and medical goods (specialized stores)

Matching is done on BOTH the numeric code (however it's formatted in the
real field -- "21002" or "2100" or embedded in a longer string) and a
keyword fallback ("pharmaceutical", "medicinal", "pharma"), since the
exact real-world formatting of the Principal Business Activity field
isn't independently confirmed and shouldn't be over-trusted to one form.

ONLY ACTIVE companies count as genuine current industry presence --
Struck Off and Dormant companies are excluded. A struck-off company no
longer legally exists; counting it would overstate real presence.

The registered office address is free text with NO separate district
field -- this module extracts the 6-digit PIN code from the address text
and resolves it to a district via a pincode-prefix crosswalk (the real
version of this comes from the LGD "Local Bodies with PIN Codes" dataset
on data.gov.in; this module ships a small illustrative prefix map for the
sample districts, clearly NOT the full real dataset). PIN-code-to-district
resolution is itself an approximation -- the first 3 digits of an Indian
PIN code identify a postal sorting region that usually, but not always,
aligns exactly with one administrative district.
"""

import csv
import re

PHARMA_NIC_CODES = ["21001", "21002", "21009", "2100", "46497", "4772"]
PHARMA_KEYWORDS = ["pharmaceutical", "medicinal", "pharma"]

# Illustrative pincode-prefix -> LGD code map (first 3 digits). NOT the
# real LGD pincode dataset -- a stand-in covering only this sample's
# districts, built from well-known PIN code ranges for these cities.
PINCODE_PREFIX_TO_LGD = {
    "641": "SAMPLE-TN-01",   # Coimbatore
    "600": "SAMPLE-TN-02",   # Chennai
    "560": "SAMPLE-KA-01",   # Bengaluru Urban
    "411": "SAMPLE-MH-03",   # Pune
    "400": "SAMPLE-MH-01",   # Mumbai City (Mumbai Suburban also uses 400-prefix in reality;
                              # this sample map can't distinguish them from PIN alone --
                              # a real build needs the actual LGD pincode table, which does)
    "500": "SAMPLE-TS-01",   # Hyderabad
    "518": "SAMPLE-AP-01",   # Kurnool
    "522": "SAMPLE-AP-03",   # Guntur
    "380": "SAMPLE-GJ-01",   # Ahmedabad
}


def is_pharma_activity(principal_business_activity: str) -> bool:
    """
    Matches a real NIC pharma code as a whole token, not a bare substring.
    The previous version checked `code in principal_business_activity`,
    which would match "2100" inside an unrelated numeric string (e.g. a
    capital-amount figure that ended up concatenated into the same field
    in a messy real-world export) just as readily as inside a genuine
    NIC code. \\b word-boundary matching requires the code to stand alone
    (surrounded by non-digit characters or string edges), not be a
    substring of a longer number.
    """
    if not principal_business_activity:
        return False
    if any(re.search(rf"\b{code}\b", principal_business_activity) for code in PHARMA_NIC_CODES):
        return True
    text = principal_business_activity.lower()
    return any(kw in text for kw in PHARMA_KEYWORDS)


def extract_pincode(address: str):
    if not address:
        return None
    m = re.search(r"\b(\d{6})\b", address)
    return m.group(1) if m else None


def resolve_pincode_to_lgd(pincode: str):
    if not pincode or len(pincode) < 3:
        return None
    return PINCODE_PREFIX_TO_LGD.get(pincode[:3])


def extract_pharma_companies(csv_path: str) -> list:
    """
    Returns active, pharma-classified companies with their resolved
    district (where resolvable). Each result includes WHY it was excluded
    when it was -- struck off, non-pharma, or unresolvable pincode --
    rather than just silently dropping rows, so the exclusions are
    auditable.
    """
    kept, excluded = [], []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            status = (row.get("Company Status") or "").strip().lower()
            activity = row.get("Principal Business Activity", "")
            address = row.get("Registered Office Address", "")

            if not is_pharma_activity(activity):
                excluded.append((row.get("CIN"), "not_pharma_activity"))
                continue
            if status != "active":
                excluded.append((row.get("CIN"), f"not_active (status={status})"))
                continue

            pincode = extract_pincode(address)
            lgd_code = resolve_pincode_to_lgd(pincode)
            if not lgd_code:
                excluded.append((row.get("CIN"), f"unresolvable_pincode ({pincode})"))
                continue

            kept.append({
                "cin": row.get("CIN"), "company_name": row.get("Company Name"),
                "principal_business_activity": activity, "pincode": pincode,
                "lgd_code": lgd_code,
            })
    return kept, excluded


def aggregate_by_district(companies: list) -> dict:
    counts = {}
    for c in companies:
        counts[c["lgd_code"]] = counts.get(c["lgd_code"], 0) + 1
    return counts
