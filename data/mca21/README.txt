MCA21 COMPANY MASTER DATA — BULK CSV
======================================
Place the downloaded CSV here:

  company_master_data.csv     — full bulk download (~1GB+)
    Download from: https://www.data.gov.in/catalog/company-master-data
    Requires free registration on data.gov.in

  pharma_filtered.csv         — pre-filtered to pharma companies only
    Create this by running from the project root:
      grep -i "pharmaceutical\|21001\|21002\|21009\|46497\|4772" \
        data/mca21/company_master_data.csv > data/mca21/pharma_filtered.csv
    This reduces the file from ~1GB to ~20-50MB for faster processing.
    Point run_pipeline.py at pharma_filtered.csv, not the full file.

The mca21_ingestion.py module handles parsing this CSV automatically.
See docs/DLMAI_Data_Download_Procedure.md Part 3, Change 5 for the
one-line update needed in run_pipeline.py.
