"""
Generates a mock Jan Aushadhi state-export PDF -- a genuine ruled table,
matching the real portal's confirmed column structure (Sr.No, Kendra Code,
Owner Name, State, District). Stands in for an actual exported PDF, which
this sandbox can't pull from the live JS-driven locator.

Deliberately mixes in:
  - a renamed district (Bangalore Urban -- the old name, to prove the
    crosswalk's historical-name matching works here too, not just in the
    Layer 2 demo)
  - multiple Kendras per district (to test counting/aggregation, not just
    single-row matching)
  - one district (Wayanad) that doesn't exist in our sample master at all,
    to prove it surfaces as unmatched rather than disappearing
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

ROWS = [
    ("Sr.No", "Kendra Code", "Owner Name", "State", "District", "Pin Code"),
    ("1", "TN-CBE-014", "S. Murugan", "Tamil Nadu", "Coimbatore", "641001"),
    ("2", "TN-CBE-027", "K. Lakshmi", "Tamil Nadu", "Coimbatore", "641004"),
    ("3", "TN-CBE-031", "R. Venkat", "Tamil Nadu", "Coimbatore", "641018"),
    ("4", "TN-CHN-009", "A. Priya", "Tamil Nadu", "Chennai", "600028"),
    ("5", "TN-CHN-052", "M. Saravanan", "Tamil Nadu", "Chennai", "600040"),
    ("6", "KA-BLR-101", "N. Suresh", "Karnataka", "Bangalore Urban", "560001"),   # old name
    ("7", "KA-BLR-118", "P. Anitha", "Karnataka", "Bangalore Urban", "560034"),
    ("8", "KA-BLR-122", "T. Ravi", "Karnataka", "Bangalore Urban", "560066"),
    ("9", "KA-BLR-140", "G. Deepa", "Karnataka", "Bangalore Urban", "560078"),
    ("10", "MH-PUN-008", "V. Joshi", "Maharashtra", "Pune", "411001"),
    ("11", "MH-PUN-019", "S. Patil", "Maharashtra", "Pune", "411038"),
    ("12", "KL-WYD-003", "B. Thomas", "Kerala", "Wayanad", "673121"),   # not in our sample master
]

def build_mock_kendra_pdf(filepath):
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    table = Table(ROWS, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    doc.build([table])


if __name__ == "__main__":
    build_mock_kendra_pdf("mock_kendra_export.pdf")
    print("Mock Kendra export PDF generated.")
