# YourFutureROI data

College Scorecard data (U.S. Dept. of Education), all 6,273 schools.

## yourfutureroi_schools.json: earnings refresh and cohort counts (2026-10-18)
Originally built from the College Scorecard API with `tools/fetch_scorecard_12.py` (before the 10/15/2026 data refresh). Earnings were then refreshed and cohort counts added from the bulk files released 10/15/2026:
https://ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Field-of-Study_10152026.zip and
https://ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Institution_10152026.zip

1. `tools/refresh_earnings.py` sets
   - `latest.earnings.10_yrs_after_entry.median` <- `MD_EARN_WNE_P10`, `latest.earnings.6_yrs_after_entry.median` <- `MD_EARN_WNE_P6` (match on UNITID = `id`)
   - `programs[].earnings.{1_yr,4_yr,5_yr}.overall_median_earnings` <- `EARN_MDN_1YR`, `EARN_MDN_4YR`, `EARN_MDN_5YR` (match on UNITID + CIPCODE + CREDLEV)
2. `tools/add_cohort_counts.py` adds
   - `latest.earnings.10_yrs_after_entry.count` <- `COUNT_WNE_P10` (placed right after the 10-year median)
   - `programs[].earnings.{1_yr,4_yr,5_yr}.count` <- `EARN_COUNT_WNE_1YR`, `EARN_COUNT_WNE_4YR`, `EARN_COUNT_WNE_5YR`

Suppressed values (PrivacySuppressed/PS/NULL/NA/blank) are null. 13,375 programs and 1 school (Selma University, 102058) are not in the 10/15/2026 files; they are kept with earnings and counts set to null. Everything else (costs, admissions, min_gpa, key order, compact JSON) is unchanged.
