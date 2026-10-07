"""
Generates a mock RHS district-wise health centre PDF using REAL figures
pulled directly from nhm.gov.in's official table (As on March 2011) --
not invented numbers. Deliberately includes:
  - a state-total row with a blank district name (tests the skip logic)
  - Mumbai's real absence (no rows for Mumbai City/Suburban at all,
    matching the actual document)
  - pre-bifurcation Kurnool/Guntur and pre-Telangana-split Hyderabad,
    matching this table's real 2011 vintage -- Nandyal/Palnadu/Bapatla/
    Annamayya correctly get NO row, exactly as in the real source
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

HEADER = ["State/UT", "Name of the District", "Sub Centres", "PHCs", "CHCs",
          "Sub Divisional Hospital", "District Hospital"]

# Real figures, As on March 2011, from nhm.gov.in's district-wise table.
ROWS = [
    HEADER,
    ["Andhra Pradesh", "Guntur", "689", "74", "16", "2", "1"],
    ["Andhra Pradesh", "Hyderabad", "53", "10", "0", "4", "1"],
    ["Andhra Pradesh", "Kurnool", "576", "88", "18", "1", "1"],
    ["Andhra Pradesh", "", "12522", "1624", "281", "58", "17"],   # real state-total row, blank district name
    ["Karnataka", "Bangalore Urban", "195", "75", "3", "3", "3"],
    ["Karnataka", "Bangalore Rural", "167", "47", "1", "4", "0"],
    ["Karnataka", "", "8870", "2310", "180", "146", "31"],         # real state-total row
    ["Maharashtra", "Pune", "539", "96", "21", "3", "1"],
    # NOTE: Mumbai City and Mumbai Suburban are deliberately absent here --
    # they are absent from the real document too, not omitted by mistake.
    ["Maharashtra", "", "10580", "1809", "365", "81", "23"],       # real state-total row
]


def build_mock_rhs_pdf(filepath):
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
    build_mock_rhs_pdf("mock_rhs_district_table.pdf")
    print("Mock RHS table generated (using real 2011 figures).")
