# DLMAI — Data Source Mapping (v1.1, free/public sources only)

This is the working checklist for Phase 2 of the roadmap ("data inventory & collection"). Every indicator that survived the Section 1.1 feasibility audit is mapped here to a specific, verified portal — not a generic "check the government website" pointer. Use this alongside `DLMAI_Framework_Architecture.md`, which it complements.

**How to use this:** for each row, the "District key" column tells you what identifier the source natively uses — this is what Layer 2 (the district master crosswalk) needs to resolve against the LGD-based master table before anything else happens. Sources that hand you a clean LGD code or Census code are cheap to harmonize; sources that hand you free-text district names or street addresses are the ones to budget real data-engineering time against.

---

## 0. Cross-cutting: district master & crosswalk sources
*Build this before touching any indicator below — everything else depends on it.*

| What you need | Source & portal | Format | District key | Notes |
|---|---|---|---|---|
| Canonical district list with LGD codes | **lgdirectory.gov.in** — "View/Download Entities" → Districts; mirrored at **data.gov.in/resource/local-government-directory-lgd-districts** | CSV/Excel | LGD code (the canonical key itself) | Updated monthly; this *is* your master table's backbone |
| Pincode → district mapping | **data.gov.in** — "Local Government Directory (LGD) - Local Bodies with PIN Codes" | CSV | LGD code + PIN code | This is what resolves MCA21's free-text registered-office addresses (Pillar 5) down to a district — without it, that indicator is stuck at "state level, maybe" |
| Census 2011 district codes (for crosswalking older sources) | censusindia.gov.in — District Handbooks section | CSV/PDF | Census 2011 district code | Needed because Census, NFHS, and current admin records all partition the map differently (Section 2) |
| District boundary shapefiles (for the output/mapping layer) | **Survey of India Online Maps Portal** (onlinemaps.surveyofindia.gov.in) — "Digital Vector Data," country-level, up to district level with HQ — listed at **₹0**, i.e. free | Shapefile | Census-aligned district boundary | A community-maintained alternative that's faster to get started with: the open "India Geodata" project (CC0/CC-BY licensed) ships pre-harmonized district polygons sourced from LGD + Survey of India + Bhuvan in parquet/shapefile/GeoJSON, which saves a reconciliation step if you don't need the official SoI product specifically |

---

## Pillar 1 — Demand & disease burden

**Note:** NFHS-6 district factsheets aren't out yet (national/state tables only, as of mid-2026) — rows below use **NFHS-5 (2019-21)**, the current real district-level source, with exact field wording confirmed against the actual published indicator list. Swap to NFHS-6 once IIPS releases district tables; the field wording is expected to stay close to NFHS-5's for trend comparability.

| Indicator | Source & portal | Format | District key | Effort |
|---|---|---|---|---|
| Population, age structure, urban % | censusindia.gov.in/census.website/data/handbooks (District Census Handbooks); also a searchable catalog at censusindia.gov.in/nada | PDF (tables); some village/district tables in Excel | Census 2011 district code | Low — well-structured, one-time bulk pull |
| Population *projection* forward from 2011 | RGI population projection reports (Census-derived, published as a separate report by the Registrar General / National Commission on Population) | PDF tables | Census 2011 district code | Medium — projections are usually state-level; district-level projection requires applying state growth rates to 2011 district bases yourself |
| Child stunting / wasting / underweight | NFHS-5 district factsheets, nfhsiips.in — confirmed exact fields: "Children under 5 years who are stunted (height-for-age) (%)", equivalent wasting/underweight rows | PDF factsheet per district | District name (free text) | Medium — district factsheets to pull and parse; name-matching to LGD needed |
| Elevated blood pressure / on hypertension medication (%) | NFHS-5 district factsheet, same file — confirmed real field | PDF factsheet | District name (free text) | Same batch as stunting/wasting — same source file |
| Blood sugar high/very high or on diabetes medication (%) | NFHS-5 district factsheet, same file — confirmed real field | PDF factsheet | District name (free text) | Same batch |
| Communicable disease incidence (TB, malaria, dengue) | NVBDCP (malaria/dengue) and NTEP/NIKSHAY (TB) — published as separate program bulletins, not one unified district file; NFHS doesn't cover this at all | PDF / web dashboard | District name, inconsistent formatting | High — the most manual-assembly indicator in this pillar; budget real time or consider dropping if the rest of the pillar is sufficient |

---

## Pillar 2 — Economic access & affordability

| Indicator | Source & portal | Format | District key | Effort |
|---|---|---|---|---|
| Household amenities composite (% electricity, % clean cooking fuel, % improved drinking water, % improved sanitation) | NFHS-5 district factsheet (same file as Pillar 1's stunting/blood pressure fields) — confirmed real fields, used as the affordability/living-standards proxy | PDF | District name (free text) | Low-Medium once you're already parsing the factsheet for Pillar 1 |
| % households with health insurance / scheme coverage | NFHS-5 district factsheet — confirmed exact field: "Households with any usual member covered under a health insurance/financing scheme (%)" | PDF | District name (free text) | Same batch |
| Average out-of-pocket expenditure per delivery in a public health facility (Rs.) | NFHS-5 district factsheet — confirmed real, district-level field | PDF | District name (free text) | Same batch — note this is delivery-specific spending, not general health OOPE |

**Practical tip:** because all the fields above come from the same ~4-page PDF per district, the efficient build here is one parser that extracts every field you need from a single factsheet pull, run once across all districts, rather than separate extraction passes per indicator.

---

## Pillar 3 — Healthcare infrastructure

| Indicator | Source & portal | Format | District key | Effort |
|---|---|---|---|---|
| PHC / CHC / sub-centre counts and density | **nhm.gov.in/images/pdf/monitoring/rhs/district-wise-health-centres.pdf** — confirmed real, direct district-wise table (the actual main RHS annual bulletin on hmis.mohfw.gov.in is a much larger state-aggregated document; this NHM file is specifically the district-level breakdown and is the one to use). Confirmed real columns: State/UT, District Name, Sub Centres, PHCs, CHCs, Sub Divisional Hospital, District Hospital. **Confirmed real gap:** fully-urban districts (e.g. Mumbai City/Suburban) are entirely absent — RHS counts rural infrastructure specifically | PDF table | District name, grouped by state | Low-Medium — a single well-structured table, not the full bulletin; convert raw counts to per-capita density using Census population |
| District hospital count, public bed count | Same district-wise table above, plus National Health Profile (CBHI/NCDC) for cross-check | PDF | District name | Low-Medium |
| Doctor / nurse / pharmacist sanctioned vs vacant posts | The main annual Rural Health Statistics bulletin (hmis.mohfw.gov.in — exact URL path changes by edition) — this workforce detail is NOT in the district-wise table above, it's only in the full bulletin | PDF (large statistical tables) | District name, grouped by state | Medium-High — bigger document, state-level tables more than district-level for workforce specifically |

---

## Pillar 4 — Pharma distribution & retail density

| Indicator | Source & portal | Format | District key | Effort |
|---|---|---|---|---|
| Jan Aushadhi Kendra count per district | **janaushadhi.gov.in/locate-kendra** — confirmed real columns: Sr.No, Kendra Code, Owner Name, State, **District**, Pin Code. Confirmed by inspecting the live page: this is a filtered search (Select State → Select District → Search), **not a one-click bulk export** — practical path is ~36 state-level searches (state selected, district left blank) using the page's own "DOWNLOAD PDF" option, not a district-by-district crawl | PDF table per state | District name (free text) + state name + PIN code | Low-Medium — ~36 PDF downloads is a bounded one-time task; a ready-built parser (`jan_aushadhi_ingestion.py`) extracts and aggregates these, tested against a mock export |
| All-weather road connectivity | PMGSY's monitoring system (search current "PMGSY OMMS" — Online Management and Monitoring System — portal) and/or the open "GeoSadak" rural-road datasets that compile PMGSY data into modern geospatial formats | Dashboard export / shapefile | District name or geocoded points | Medium — treat as a stretch indicator; verify the current portal name before relying on it, as PMGSY's reporting systems have been renamed over the years |
| Retail chemist license count (bonus) | Individual state FDA/Drug Control portals (Maharashtra FDA, Gujarat FDA, Kerala Drugs Control among the more accessible ones) | Varies — searchable web registry, no bulk export in most states | State-specific, often free-text address | High — explicitly a "collect where feasible" indicator per Section 1.1, not a baseline requirement |

---

## Pillar 5 — Industry presence & supply depth

| Indicator | Source & portal | Format | District key | Effort |
|---|---|---|---|---|
| Pharma-classified company count by registered-office district | **MCA21 Company Master Data**, bulk dataset on **data.gov.in** (catalog: "Company Master Data") — confirmed real fields: CIN, Company Name, Company Status, Company Class, Company Category, Authorized/Paid-up Capital, Date of Registration, Registered State, Registrar of Companies, Principal Business Activity, Registered Office Address, Sub Category. **Confirmed real NIC-2008 codes for the pharma filter:** 21001/21002/21009 (manufacturing, all under Class 2100), 46497 (wholesale), 4772 (retail) — match on the numeric code where present in the field AND a keyword fallback ("pharmaceutical"/"medicinal"), since the field's exact real-world formatting isn't independently confirmed. **Filter to Company Status = Active only** — Struck Off/Dormant companies no longer legally exist and would overstate real presence | Bulk CSV | Free-text registered-office address (no native district field) — extract the 6-digit PIN code via regex, then resolve via the pincode-to-district LGD dataset from Section 0 | Medium-High — filtering is straightforward once the NIC codes are known; address-to-district resolution is the real effort, and some active companies will be unresolvable if their address has no clean PIN code, which is a genuine, expected loss rate, not a bug to chase to zero |
| Manufacturing unit / drug license counts (bonus) | CDSCO public licensing pages; individual state FDA portals | PDF/web, fragmented | State-specific | High — same fragmentation issue as retail licenses; collect opportunistically |

---

## Pillar 6 — Regulatory & scheme environment

| Indicator | Source & portal | Format | District key | Effort |
|---|---|---|---|---|
| Ayushman Bharat/PMJAY cards issued, hospitals empanelled | **dashboard.pmjay.gov.in/publicdashboard** (National Health Authority's public dashboard; a parallel public dashboard also exists at dashboard.nha.gov.in/public) | Interactive dashboard with state→district drill-down | District name | Medium — confirm the specific district-level export or table view works for your target states before committing this as a baseline indicator; public dashboards sometimes default to state-level summary views |
| NITI Aayog Aspirational District flag | **niti.gov.in/data-aspirational-districts-model**; live rankings dashboard at **championsofchange.gov.in** | Web list / dashboard | District name | Low — this is just a binary flag (112 of the current district count are designated), trivial to encode once you have the list |
| *(validation-only)* SDG India Index district score | NITI Aayog SDG India Index reports | PDF/report | District name | Use only to sense-check your final DLMAI ranking — see Section 1.1's note on not double-counting |

---

## Pillar 7 — Growth momentum

| Indicator | Source & portal | Format | District key | Effort |
|---|---|---|---|---|
| Decadal population growth rate | censusindia.gov.in District Census Handbooks, comparing 2001 and 2011 editions | PDF/CSV | Census district code | Low-Medium — note the next census round is now scheduled for 2027 (houselisting operations began in 2026), so 2001→2011 remains the only systematic decadal comparison available until then |
| Decadal urbanization change | Same Census handbooks | PDF/CSV | Census district code | Low-Medium |
| Literacy rate and literacy growth | Same Census handbooks | PDF/CSV | Census district code | Low-Medium — batch this with population and urbanization since they're the same source documents |

---

## Suggested collection build order

Not every source is equally cheap, so collect in this order to get a usable partial index fastest and de-risk the hardest parts early:

1. **District master + crosswalk tables** (Section 0) — must come first, everything else depends on it
2. **NFHS-5 district factsheets** — covers Pillars 1 and 2 almost entirely from one source; highest value-per-effort (swap to NFHS-6 once its district tables are released)
3. **Census handbooks** — covers Pillar 1's demographics and all of Pillar 7
4. **Jan Aushadhi Kendra locator** — cleanest single pull in the whole project, covers a chunk of Pillar 4
5. **Rural Health Statistics** — covers Pillar 3, more parsing effort than NFHS but still one well-defined source
6. **NITI Aayog Aspirational Districts list** — trivial, do it while you're already on the NITI Aayog site
7. **PMJAY/NHA public dashboard** — confirm district-level export works before committing time
8. **MCA21 company master data** — the highest one-time effort (filtering + address-to-district resolution), but it's what makes Pillar 5 exist at all in a free-sources build
9. **Everything marked "bonus" or "stretch"** (retail/wholesale licenses, communicable disease bulletins, road connectivity) — collect opportunistically after the core build works end-to-end; don't let these block your first full run
