MASTER DISTRICT REFERENCE FILES
================================
Files to place here (see docs/DLMAI_Data_Download_Procedure.md Step 1):

  lgd_districts.csv     — Download from:
                          https://www.data.gov.in/resource/local-government-directory-lgd-districts
                          Updated monthly. Required columns after reshaping:
                          lgd_code, state_lgd_code, state_name, current_name,
                          historical_names, parent_lgd_code, effective_from

  lgd_pincodes.csv      — Download from lgdirectory.gov.in:
                          View/Download Entities → Local Bodies with PIN Codes
                          Used to resolve MCA21 registered-office addresses to districts.

  manual_aliases.csv    — ALREADY PRESENT. Add to this file whenever the crosswalk
                          engine returns an unmatched result that turns out to be a
                          historical name or spelling variant (see the existing entries
                          for format examples). Do not delete existing entries.
