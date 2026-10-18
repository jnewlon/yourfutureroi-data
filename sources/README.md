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
