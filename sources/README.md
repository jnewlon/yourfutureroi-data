# Official source files

All files are unmodified official downloads, plus CSVs extracted directly from them (no values were added or estimated). Retrieved 2026-10-18.

## HUD Small Area Fair Market Rents, FY2026 (revised)
- Source page: https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html
- Download: https://www.huduser.gov/portal/datasets/fmr/fmr2026/fy2026_safmrs_revised.xlsx
- Data year: FY2026. HUD published both `fy2026_safmrs.xlsx` and `fy2026_safmrs_revised.xlsx`; the revised file supersedes the original. (FY2027 SAFMRs are also published but not included.)
- `hud/fy2026_safmrs_revised.xlsx`: original workbook (SAFMRs at 100%, 90% and 110% payment standards).
- `hud/fy2026_safmrs_by_zip.csv`: 51,895 rows, 38,601 unique ZIPs. A ZIP can appear more than once when it spans multiple HUD FMR areas; all rows are kept.
  - Cleanup (2026-10-18): line breaks inside `metro_area` values (from wrapped cells in HUD's workbook) were replaced with a single space and repeated whitespace was collapsed (3,190 fields with line breaks, plus 184 "Cincinnati, OH-KY-IN  HUD Metro FMR Area" double spaces). No other values changed; the original workbook is unmodified.
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
  - Method: lower weighted median across schools (sort program medians, take the first whose cumulative weight reaches 50% of total). This covers only programs with published (unsuppressed) medians. The file also publishes official national values per group (`EARN_MDN_4YR_NAT`, `EARN_COUNT_WNE_4YR_NAT`, 2,569 groups), which include suppressed programs; those are not used here.
  - Row `ALL,INST_10YR`: `MD_EARN_WNE_P10` (median earnings of students working and not enrolled 10 years after entry) from the institution file, weighted by `COUNT_WNE_P10`. Cohort: AY2011-12 + AY2012-13 entrants, measured CY2022 + CY2023, 2024 dollars. Branch campuses repeat their OPEID6's earnings, so each OPEID6 is counted once (5,293 institution rows with values -> 4,079 OPEID6 units). PS/NA values skipped.

## OEWS May 2025 state by occupation
- Built from `bls/state_M2025_dl.xlsx` (above).
- `bls/oews_m2025_state_by_occupation.csv`: 35,223 rows, 829 SOC codes, 50 states + DC (Puerto Rico, Guam, Virgin Islands excluded).
  - Fields: `soc` (OCC_CODE), `state_abbr` (PRIM_STATE), `a_median` (annual median wage, USD).
  - Detailed occupations only (O_GROUP = detailed; OEWS publishes some combined codes such as 29-2010, 13-1020 as detailed). Major groups and the total are excluded.
  - Suppressed values are left empty: 607 rows `*` (not available; 145 of them are hourly-only occupations with no annual wage), 92 rows `#` (annual wage at or above $239,200).

## NCES IPEDS outcomes, retention and net price
- Source page: https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx (retrieved 2026-10-18). Newest final-release files at retrieval: GR 2023, GR200 2023, OM 2023, EF 2023 (part D), SFA 2022-23. (2024 / 2023-24 files are provisional and not used.)
- Raw downloads (not committed): https://nces.ed.gov/ipeds/datacenter/data/GR2023.zip, GR200_23.zip, OM2023.zip, EF2023D.zip, SFA2223.zip (dictionaries: same names with `_Dict.zip`).
- Built by `tools/build_ipeds.py`. All IPEDS institutions are included in the CSVs; `unitid` = IPEDS UNITID.
- Null rules: blank, not applicable (flag A) and NCES-imputed values (flags J, K, L, N, P) are empty. Reported (R), analyst-corrected (C), implied-zero (Z) values are kept. Rates are 0-1 fractions (IPEDS whole-percent rates divided by 100).
- `ipeds/ipeds_graduation_rates.csv` (GR2023, GR200_23): `level` (4yr = bachelor's-or-equivalent subcohort of a 4-year institution, cohort year 2017; 2yr = degree/certificate-seeking cohort of a 2-year institution, cohort year 2020), `cohort_year`, `cohort` (adjusted cohort, GRTYPE 8 or 29), `gr100` (bachelor's completers in 4 years, GRTYPE 13 / 8; 2-yr: completers within 100%, GRTYPE 35 / 29), `gr150` (bachelor's completers within 150%, GRTYPE 12 / 8; 2-yr: GRTYPE 30 / 29), `gr200_cohort_year` (2015 4-yr / 2019 2-yr), `gr200_cohort` (BAAC200 / L4AC200), `gr200` (BAGR200 / L4GR200). gr100 and gr150 are computed from the published GRTOTLT counts and rounded to 4 decimals.
- `ipeds/ipeds_outcome_measures.csv` (OM2023, 2015-16 entering cohort, status at 8 years, Aug 31 2023): prefixes `ftft` first-time full-time, `ftpt` first-time part-time, `nftft` non-first-time full-time, `nftpt` non-first-time part-time; suffixes `_cohort` (OMACHRT adjusted cohort), `_award8` (OMAWDP8 award at 8 years), `_still_enrolled` (OMENRYP still enrolled at the institution), `_transferred` (OMENRAP enrolled subsequently at another institution).
- `ipeds/ipeds_retention.csv` (EF2023D, fall 2022 cohort retained to fall 2023): `ft_cohort` (RRFTCTA), `ft_retention` (RET_PCF), `pt_cohort` (RRPTCTA), `pt_retention` (RET_PCP).
- `ipeds/ipeds_net_price.csv` (SFA2223, 2022-23 full-time first-time undergraduates awarded aid): `public_in_state_*` from NPIST2 / NPIS4{1-5}2 with counts GIS4N2 / GIS4N{1-5}2 (public institutions, in-state); `private_*` from NPGRN2 / NPT4{1-5}2 with counts GRN4N2 / GRN4N{1-5}2 (private institutions). `_avg` = average net price, students awarded grant/scholarship aid; bands `0_30k`, `30_48k`, `48_75k`, `75_110k`, `110k_plus` = average net price by family income, Title IV aid recipients; `_n` = number of students in that income level. Negative values (grant aid above cost) are as published.
- `../derived/ipeds_by_school.json`: the four topics merged for the 6,273 schools in `yourfutureroi_schools.json`, keyed by UNITID (schools with no IPEDS record are omitted). `net_price` keeps one basis per school (`basis` = public_in_state if reported, else private).

## ZIP to state
- `geo/zip_to_state.csv`: 41,166 rows, fields `zip` (5-digit), `state_abbr` (USPS 2-letter; includes DC, PR, GU, VI, MP, AS, MH). Built by `tools/build_zip_to_state.py`, retrieved 2026-10-19.
- Primary source (33,791 ZIPs): U.S. Census Bureau 2020 ZCTA-to-county relationship file, https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt. State = the county's state FIPS; the 137 ZCTAs that cross a state line take the state with the most land area.
- Fallback for ZIPs that are not ZCTAs (PO-box, unique and similar ZIPs; 7,337 rows): GeoNames US postal codes, https://download.geonames.org/export/zip/US.zip (CC BY 4.0).
- Last fallback (38 Puerto Rico ZIPs): HUD FY2026 SAFMR area names that name exactly one state (all ", PR").
- Covers 38,600 of the 38,601 ZIPs in `derived/hud_fmr.json`; only 88888 (HUD area DC-VA-MD, multi-state) is left out. Military APO/FPO ZIPs (AA/AE/AP) are not included.
- 12 border ZIPs where Census (land area) and GeoNames (mailing state) disagree keep the Census state: 03579 (ME vs NH), 42223 (TN vs KY), 56219 (SD vs MN), 57648 (ND vs SD), 72338 (TN vs AR), 79837 (NM vs TX), 82063 (CO vs WY), 82930 (UT vs WY), 83120 (ID vs WY), 86515 (NM vs AZ), 89421 (OR vs NV), 97635 (CA vs OR); first state = Census, kept.
