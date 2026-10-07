"""
Generates a mock District Census Handbook PDF -- an "Important Statistics"
page followed by a "District Primary Census Abstract" table -- using the
real, verified two-table structure. Stands in for an actual downloaded
handbook, which this sandbox can't reach.

Mock figures for Coimbatore and Kurnool are internally consistent (Rural +
Urban sums exactly equal the Total row, matching how a real PCA table
must reconcile) so the test can check the parser's derived percentages
exactly, not just "did it run."
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

DISTRICTS = {
    "Coimbatore": {
        "important_stats": {
            "total_population": 3458045,
            "decadal_growth_rate_pct": 15.42,
            "density_per_sqkm": 818,
            "sex_ratio": 957,
            "literacy_rate_pct": 83.98,
        },
        "pca": {
            "Total": {"population": 3458045, "population_0_6": 298000, "literates": 2658000},
            "Rural": {"population": 1245000, "population_0_6": 115000, "literates": 920000},
            "Urban": {"population": 2213045, "population_0_6": 183000, "literates": 1738000},
        },
    },
    "Kurnool": {
        "important_stats": {
            "total_population": 1187586,
            "decadal_growth_rate_pct": 11.23,
            "density_per_sqkm": 259,
            "sex_ratio": 983,
            "literacy_rate_pct": 60.74,
        },
        "pca": {
            "Total": {"population": 1187586, "population_0_6": 145000, "literates": 635000},
            "Rural": {"population": 850000, "population_0_6": 110000, "literates": 430000},
            "Urban": {"population": 337586, "population_0_6": 35000, "literates": 205000},
        },
    },
}


def build_mock_handbook(filepath, district_name, data):
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f"District Census Handbook 2011 — {district_name}", styles["Title"]),
        Paragraph(f"District: {district_name}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("IMPORTANT STATISTICS", styles["Heading2"]),
    ]
    stats = data["important_stats"]
    important_stats_lines = [
        f"1. Total Population {stats['total_population']}",
        f"2. Decadal Growth Rate (2001-2011) (%) {stats['decadal_growth_rate_pct']}",
        f"3. Density (Persons per sq. km) {stats['density_per_sqkm']}",
        f"4. Sex Ratio (females per 1000 males) {stats['sex_ratio']}",
        f"5. Literacy Rate (%) {stats['literacy_rate_pct']}",
    ]
    for line in important_stats_lines:
        elements.append(Paragraph(line, styles["Normal"]))

    elements.append(Spacer(1, 18))
    elements.append(Paragraph("SECTION I — DISTRICT PRIMARY CENSUS ABSTRACT", styles["Heading2"]))

    table_data = [["Residence", "Population", "Population age 0-6", "Literates"]]
    for label in ["Total", "Rural", "Urban"]:
        row = data["pca"][label]
        table_data.append([label, str(row["population"]), str(row["population_0_6"]), str(row["literates"])])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(table)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    doc.build(elements)


if __name__ == "__main__":
    for name, data in DISTRICTS.items():
        build_mock_handbook(f"mock_{name}_census_handbook.pdf", name, data)
    print("Mock Census handbooks generated.")
