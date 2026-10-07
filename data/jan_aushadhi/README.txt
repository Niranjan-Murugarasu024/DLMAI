JAN AUSHADHI KENDRA EXPORTS — ONE PDF PER STATE
=================================================
Place one PDF per state, named exactly as shown:

  Andhra_Pradesh_kendras.pdf
  Tamil_Nadu_kendras.pdf
  Maharashtra_kendras.pdf
  ... (~36 files total, one per state/UT)

How to download each one:
  1. Go to: https://janaushadhi.gov.in/near-by-kendra
  2. Select a state from the dropdown
  3. Leave district empty (returns all districts in the state)
  4. Click Search
  5. Click "DOWNLOAD PDF" on the results page
  6. Rename to [StateName]_kendras.pdf (use underscores, not spaces)

jan_aushadhi_ingestion.py will parse all PDFs in this directory when
run_pipeline.py is updated to scan the folder. See Part 3, Change 3.

Priority order: Maharashtra, Karnataka, Tamil Nadu, Gujarat, Telangana,
Andhra Pradesh, Uttar Pradesh, Rajasthan, West Bengal first.
