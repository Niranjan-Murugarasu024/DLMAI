"""
Generates realistic mock NFHS-5-style district factsheet PDFs for testing
nfhs_factsheet_parser.py end-to-end. Uses the REAL indicator text pulled
from the actual NFHS-5 district indicator list (not invented wording), with
plausible-but-fictional values. Includes deliberate "noise" indicators the
parser should correctly ignore, and reproduces the Women/Men dual-occurrence
quirk for hypertension and diabetes.

This stands in for an actual downloaded factsheet, which this sandbox can't
reach over the network. Swap in real PDFs from nfhsiips.in and re-run the
parser against them before trusting this for real work.
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def build_mock_factsheet(filepath, district_name, values):
    """
    values: dict with keys matching the lines below (see `lines` list) --
    just the numbers that get slotted into otherwise-fixed real indicator
    text, so the generated PDF reads like a real factsheet.
    """
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    y = height - 50

    def write(text, size=9, leading=14):
        nonlocal y
        c.setFont("Helvetica", size)
        c.drawString(40, y, text)
        y -= leading
        if y < 50:
            c.showPage()
            y = height - 50

    write(f"District Fact Sheet — National Family Health Survey-5 (2019-21)", size=11, leading=20)
    write(f"District: {district_name}", size=10, leading=20)
    write("HOUSEHOLD CHARACTERISTICS", size=10, leading=16)

    # Real indicator text, item numbers matching the actual NFHS-5 list,
    # footnote digits included where the real factsheet has them.
    lines = [
        f"7. Population living in households with electricity (%) {values['electricity_pct']}",
        f"8. Population living in households with an improved drinking-water source1 (%) {values['drinking_water_pct']}",
        f"9. Population living in households that use an improved sanitation facility2 (%) {values['sanitation_pct']}",
        f"10. Households using clean fuel for cooking3 (%) {values['clean_fuel_pct']}",
        f"11. Households using iodized salt (%) {values['iodized_salt_pct']}",   # noise -- not in our pattern list
        f"12. Households with any usual member covered under a health insurance/financing scheme (%) {values['insurance_pct']}",
        f"13. Children age 5 years who attended pre-primary school during the school year 2019-20 (%) {values['noise_preprimary_pct']}",  # noise
        f"39. Average out-of-pocket expenditure per delivery in a public health facility (Rs.) {values['oope_delivery_rs']}",
    ]
    for ln in lines:
        write(ln)

    write("", size=4, leading=10)
    write("NUTRITIONAL STATUS OF CHILDREN", size=10, leading=16)
    lines2 = [
        f"73. Children under 5 years who are stunted (height-for-age)18 (%) {values['stunting_pct']}",
        f"74. Children under 5 years who are wasted (weight-for-height)18 (%) {values['wasting_pct']}",
        f"75. Children under 5 years who are severely wasted (weight-for-height)19 (%) {values['noise_severely_wasted_pct']}",  # noise, must NOT match wasting_pct
        f"76. Children under 5 years who are underweight (weight-for-age)18 (%) {values['underweight_pct']}",
    ]
    for ln in lines2:
        write(ln)

    write("", size=4, leading=10)
    write("BLOOD SUGAR LEVEL AND BLOOD PRESSURE AMONG ADULTS", size=10, leading=16)
    write("Women age 15 years and above:", size=9, leading=14)
    lines3 = [
        f"86. Blood sugar level - high (141-160 mg/dl)23 (%) {values['noise_bsl_high_women']}",   # noise component
        f"87. Blood sugar level - very high (>160 mg/dl)23 (%) {values['noise_bsl_vhigh_women']}",  # noise component
        f"88. Blood sugar level - high or very high (>140 mg/dl) or taking medicine to control blood sugar level23 (%) {values['diabetes_combined_pct_women']}",
        f"92. Mildly elevated blood pressure (Systolic 140-159 mm of Hg and/or Diastolic 90-99 mm of Hg) (%) {values['noise_bp_mild_women']}",  # noise
        f"94. Elevated blood pressure (Systolic >=140 mm of Hg and/or Diastolic >=90 mm of Hg) or taking medicine to control blood pressure (%) {values['hypertension_combined_pct_women']}",
    ]
    for ln in lines3:
        write(ln)
    write("Men age 15 years and above:", size=9, leading=14)
    lines4 = [
        f"89. Blood sugar level - high (141-160 mg/dl)23 (%) {values['noise_bsl_high_men']}",
        f"90. Blood sugar level - very high (>160 mg/dl)23 (%) {values['noise_bsl_vhigh_men']}",
        f"91. Blood sugar level - high or very high (>140 mg/dl) or taking medicine to control blood sugar level23 (%) {values['diabetes_combined_pct_men']}",
        f"95. Mildly elevated blood pressure (Systolic 140-159 mm of Hg and/or Diastolic 90-99 mm of Hg) (%) {values['noise_bp_mild_men']}",
        f"97. Elevated blood pressure (Systolic >=140 mm of Hg and/or Diastolic >=90 mm of Hg) or taking medicine to control blood pressure (%) {values['hypertension_combined_pct_men']}",
    ]
    for ln in lines4:
        write(ln)

    c.save()


if __name__ == "__main__":
    coimbatore_values = dict(
        electricity_pct=99.4, drinking_water_pct=97.8, sanitation_pct=88.3, clean_fuel_pct=78.1,
        iodized_salt_pct=96.0, insurance_pct=52.6, noise_preprimary_pct=41.2,
        oope_delivery_rs=2840,
        stunting_pct=18.7, wasting_pct=11.2, noise_severely_wasted_pct=3.4, underweight_pct=17.9,
        noise_bsl_high_women=6.1, noise_bsl_vhigh_women=2.3, diabetes_combined_pct_women=13.8,
        noise_bp_mild_women=8.9, hypertension_combined_pct_women=19.4,
        noise_bsl_high_men=7.0, noise_bsl_vhigh_men=3.1, diabetes_combined_pct_men=16.2,
        noise_bp_mild_men=10.5, hypertension_combined_pct_men=24.7,
    )
    kurnool_values = dict(
        electricity_pct=98.2, drinking_water_pct=92.4, sanitation_pct=71.6, clean_fuel_pct=61.0,
        iodized_salt_pct=88.5, insurance_pct=64.3, noise_preprimary_pct=29.7,
        oope_delivery_rs=3510,
        stunting_pct=29.4, wasting_pct=17.8, noise_severely_wasted_pct=5.9, underweight_pct=31.2,
        noise_bsl_high_women=5.2, noise_bsl_vhigh_women=1.9, diabetes_combined_pct_women=10.5,
        noise_bp_mild_women=7.6, hypertension_combined_pct_women=16.1,
        noise_bsl_high_men=6.4, noise_bsl_vhigh_men=2.6, diabetes_combined_pct_men=13.9,
        noise_bp_mild_men=9.1, hypertension_combined_pct_men=21.3,
    )
    build_mock_factsheet("mock_Coimbatore_factsheet.pdf", "Coimbatore", coimbatore_values)
    build_mock_factsheet("mock_Kurnool_factsheet.pdf", "Kurnool", kurnool_values)
    print("Mock factsheets generated.")
