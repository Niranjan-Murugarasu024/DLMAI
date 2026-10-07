"""
Generates a mock MCA21 Company Master Data CSV using the real confirmed
column set (CIN, Company Name, Company Status, Principal Business
Activity, Registered Office Address, Registered State). Company names are
fictional. Deliberately includes:
  - active pharma manufacturers and a wholesaler/retailer across several
    districts (the real signal Pillar 5 wants)
  - a non-pharma company (textiles) -- must be excluded by activity
  - a Struck Off pharma company -- must be excluded by status despite
    having a pharma NIC code, since it no longer legally exists
  - a Dormant pharma company -- same exclusion logic
  - one company whose address has NO 6-digit PIN code at all -- tests the
    unresolvable-pincode exclusion path
"""

import csv

ROWS = [
    {"CIN": "U24232TN2010PLC001001", "Company Name": "Kaveri Pharma Manufacturing Pvt Ltd",
     "Company Status": "Active", "Principal Business Activity": "21002 - Manufacture of allopathic pharmaceutical preparations",
     "Registered Office Address": "Plot 14, SIDCO Industrial Estate, Coimbatore, Tamil Nadu 641021", "Registered State": "Tamil Nadu"},
    {"CIN": "U24232TN2015PLC001002", "Company Name": "Nila Biosciences Pvt Ltd",
     "Company Status": "Active", "Principal Business Activity": "21001 - Manufacture of medicinal substances",
     "Registered Office Address": "44 Avinashi Road, Coimbatore, Tamil Nadu 641018", "Registered State": "Tamil Nadu"},
    {"CIN": "U51900TG2008PLC001003", "Company Name": "Krishna Drugs and Formulations Ltd",
     "Company Status": "Active", "Principal Business Activity": "46497 - Wholesale of pharmaceutical and medical goods",
     "Registered Office Address": "Genome Valley, Shamirpet, Hyderabad, Telangana 500078", "Registered State": "Telangana"},
    {"CIN": "U24239TG2012PLC001004", "Company Name": "Deccan Therapeutics Ltd",
     "Company Status": "Active", "Principal Business Activity": "21009 - Manufacture of other pharmaceutical and botanical products",
     "Registered Office Address": "Plot 22, Pharma City, Hyderabad, Telangana 500037", "Registered State": "Telangana"},
    {"CIN": "U24232TG2016PLC001005", "Company Name": "Charminar Lifesciences Pvt Ltd",
     "Company Status": "Active", "Principal Business Activity": "21002 - Manufacture of allopathic pharmaceutical preparations",
     "Registered Office Address": "Road No. 3, Banjara Hills, Hyderabad, Telangana 500034", "Registered State": "Telangana"},
    {"CIN": "U24230GJ2009PLC001006", "Company Name": "Sabarmati Pharmachem Ltd",
     "Company Status": "Active", "Principal Business Activity": "21001 - Manufacture of medicinal substances",
     "Registered Office Address": "GIDC Estate, Ahmedabad, Gujarat 380015", "Registered State": "Gujarat"},
    {"CIN": "U52321MH2014PLC001007", "Company Name": "Mula Mutha Pharma Retail Pvt Ltd",
     "Company Status": "Active", "Principal Business Activity": "4772 - Retail sale of pharmaceutical and medical goods",
     "Registered Office Address": "FC Road, Pune, Maharashtra 411004", "Registered State": "Maharashtra"},
    {"CIN": "U17110TN2011PLC001008", "Company Name": "Noyyal Textiles Pvt Ltd",
     "Company Status": "Active", "Principal Business Activity": "13911 - Manufacture of knitted and crocheted fabrics",
     "Registered Office Address": "Tidel Park, Coimbatore, Tamil Nadu 641014", "Registered State": "Tamil Nadu"},
    {"CIN": "U24232AP2007PLC001009", "Company Name": "Tungabhadra Pharma Labs Ltd",
     "Company Status": "Struck Off", "Principal Business Activity": "21002 - Manufacture of allopathic pharmaceutical preparations",
     "Registered Office Address": "Industrial Area, Kurnool, Andhra Pradesh 518004", "Registered State": "Andhra Pradesh"},
    {"CIN": "U24239AP2013PLC001010", "Company Name": "Krishnaveni Biotech Ltd",
     "Company Status": "Dormant", "Principal Business Activity": "21009 - Manufacture of other pharmaceutical and botanical products",
     "Registered Office Address": "Brodipet, Guntur, Andhra Pradesh 522002", "Registered State": "Andhra Pradesh"},
    {"CIN": "U24232DL2010PLC001011", "Company Name": "Yamuna Pharmaceuticals Ltd",
     "Company Status": "Active", "Principal Business Activity": "21002 - Manufacture of allopathic pharmaceutical preparations",
     "Registered Office Address": "Okhla Industrial Area, Phase II, New Delhi", "Registered State": "Delhi"},   # no PIN code at all
]


def build_mock_csv(filepath):
    fieldnames = ["CIN", "Company Name", "Company Status", "Principal Business Activity",
                  "Registered Office Address", "Registered State"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ROWS)


if __name__ == "__main__":
    build_mock_csv("mock_mca21_company_master.csv")
    print("Mock MCA21 company master CSV generated.")
