# Official source files

All files are unmodified official downloads, plus CSVs extracted directly from them (no values were added or estimated). Retrieved 2026-10-18.

## HUD Small Area Fair Market Rents, FY2026 (revised)
- Source page: https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html
- Download: https://www.huduser.gov/portal/datasets/fmr/fmr2026/fy2026_safmrs_revised.xlsx
- Data year: FY2026. HUD published both `fy2026_safmrs.xlsx` and `fy2026_safmrs_revised.xlsx`; the revised file supersedes the original. (FY2027 SAFMRs are also published but not included.)
- `hud/fy2026_safmrs_revised.xlsx`: original workbook (SAFMRs at 100%, 90% and 110% payment standards).
- `hud/fy2026_safmrs_by_zip.csv`: 51,895 rows, 38,601 unique ZIPs. A ZIP can appear more than once when it spans multiple HUD FMR areas; all rows are kept.
  - Fields: `zip` (5-digit, zero-padded), `efficiency` (SAFMR 0BR), `1br`, `2br`, `3br`, `4br` (100% SAFMR, monthly USD), `metro_area` (HUD Fair Market Rent Area Name), `hud_area_code`.

## BLS OEWS state wages, May 2025
- Source page: https://www.bls.gov/oes/tables.htm
- Download: https://www.bls.gov/oes/special-requests/oesm25st.zip (contains `state_M2025_dl.xlsx`)
- Data year: May 2025 estimates.
- `bls/state_M2025_dl.xlsx`: original workbook (all occupations, all states; includes the BLS Field Descriptions sheet).
- `bls/oews_m2025_state_all_occupations.csv`: OCC_CODE 00-0000 (All Occupations), AREA_TYPE 2 (state), 51 rows (50 states + DC).
  - Fields: `area_fips`, `state`, `state_abbr`, `tot_emp`, `a_median`, `a_mean` (annual USD), `h_median`, `h_mean` (hourly USD).

## BEA Regional Price Parities by state, 2024
- Source page: https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area
- Download: https://apps.bea.gov/regional/zip/SARPP.zip (table SARPP, last updated February 19, 2026; 2024 is the latest year, 2008-2023 revised)
- Data year: 2024.
- `bea/SARPP_STATE_2008_2024.csv`, `bea/SARPP__Footnotes.html`, `bea/SARPP__definition.xml`: original files from the zip (all line codes, 2008-2024).
- `bea/bea_rpp_state_2024.csv`: 52 rows (United States + 50 states + DC).
  - Fields: `geofips`, `state`, `year`, `rpp_all_items` (SARPP line 1, "RPPs: All items"), `rpp_rents_housing` (SARPP line 3, "RPPs: Services: Housing"; BEA's housing RPP is the rents parity, US = 100).

## College Scorecard national field-of-study medians
- Source page: https://collegescorecard.ed.gov/data/ (retrieved 2026-10-18)
- Downloads (not committed; ~198 MB and ~102 MB unzipped):
  - https://ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Field-of-Study_10152026.zip
  - https://ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Institution_10152026.zip
  - Data dictionary / cohort map: https://collegescorecard.ed.gov/files/CollegeScorecardDataDictionary.xlsx
- `scorecard/national_field_medians.csv` (built by `tools/build_field_medians.py`), 1,223 rows.
  - Fields: `cip4`, `credential_level` (Scorecard CREDLEV code), `median_earnings` (USD, 2024 dollars), `cohort` (sum of weights), `source_year`.
  - Field-of-study rows: earnings field `EARN_MDN_4YR` (median earnings of graduates working and not enrolled 4 years after completing), weight `EARN_COUNT_WNE_4YR`. Cohort: AY2017-18 + AY2018-19 completers, measured CY2022 + CY2023, 2024 dollars. 1,222 CIPCODE x CREDLEV groups from 55,624 programs with both values; 167,963 program rows had a suppressed (PrivacySuppressed/PS/NULL/blank) median or count and were skipped.
  - Method: lower weighted median across schools (sort program medians, take the first whose cumulative weight reaches 50% of total). This covers only programs with published (unsuppressed) medians. The file also publishes BLS-independent official national values per group (`EARN_MDN_4YR_NAT`, `EARN_COUNT_WNE_4YR_NAT`, 2,569 groups), which include suppressed programs; those are not used here.
  - Row `ALL,INST_10YR`: `MD_EARN_WNE_P10` (median earnings of students working and not enrolled 10 years after entry) from the institution file, weighted by `COUNT_WNE_P10`. Cohort: AY2011-12 + AY2012-13 entrants, measured CY2022 + CY2023, 2024 dollars. Branch campuses repeat their OPEID6's earnings, so each OPEID6 is counted once (5,293 institution rows with values -> 4,079 OPEID6 units). PS/NA values skipped.

## OEWS May 2025 state by occupation
- Built from `bls/state_M2025_dl.xlsx` (above).
- `bls/oews_m2025_state_by_occupation.csv`: 35,223 rows, 829 SOC codes, 50 states + DC (Puerto Rico, Guam, Virgin Islands excluded).
  - Fields: `soc` (OCC_CODE), `state_abbr` (PRIM_STATE), `a_median` (annual median wage, USD).
  - Detailed occupations only (O_GROUP = detailed; OEWS publishes some combined codes such as 29-2010, 13-1020 as detailed). Major groups and the total are excluded.
  - Suppressed values are left empty: 607 rows `*` (not available; 145 of them are hourly-only occupations with no annual wage), 92 rows `#` (annual wage at or above $239,200).
