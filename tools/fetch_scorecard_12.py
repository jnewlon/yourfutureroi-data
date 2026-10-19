#!/usr/bin/env python3
"""Fetch ALL schools from College Scorecard API with 12 ROI metrics + identifiers -> one JSON file."""
import os, sys, json, time, urllib.request, urllib.parse, urllib.error
BASE = "https://api.data.gov/ed/collegescorecard/v1/schools"
FIELDS = ["id","school.name","school.city","school.state",
 "latest.cost.avg_net_price.overall","latest.cost.tuition.in_state","latest.cost.tuition.out_of_state",
 "latest.cost.attendance.academic_year","latest.earnings.10_yrs_after_entry.median",
 "latest.earnings.6_yrs_after_entry.median","latest.aid.median_debt.completers.overall",
 "latest.aid.median_debt.completers.monthly_payments","latest.completion.rate_suppressed.overall",
 "latest.admissions.admission_rate.overall","latest.student.size","latest.repayment.3_yr_default_rate"]
PROG = ["latest.programs.cip_4_digit."+x for x in ("code","title","credential.level","credential.title","earnings.1_yr.overall_median_earnings","earnings.4_yr.overall_median_earnings","earnings.5_yr.overall_median_earnings")]
def get(params, retries=10):
    url = BASE + "?" + urllib.parse.urlencode(params); delay = 5
    for _ in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=120) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429,500,502,503,504):
                print(f"HTTP {e.code}, retry {delay}s", file=sys.stderr); time.sleep(delay); delay=min(delay*2,300); continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"net error {e}, retry {delay}s", file=sys.stderr); time.sleep(delay); delay=min(delay*2,300)
    raise RuntimeError("too many retries")
def main():
    key = os.environ["SCORECARD_API_KEY"]; out = sys.argv[1] if len(sys.argv)>1 else "yourfutureroi_schools.json"
    rows, page = [], 0
    while True:
        d = get({"api_key":key,"page":page,"per_page":100,"fields":",".join(FIELDS+["latest.admissions"]+PROG)})
        res = d.get("results", []); total = d["metadata"]["total"]
        rows += [dict({f: r.get(f) for f in FIELDS}, **{k:v for k,v in sorted(r.items()) if k.startswith("latest.admissions.")}, programs=r.get("latest.programs.cip_4_digit") or []) for r in res]
        page += 1; print(f"page {page}/{-(-total//100)}", file=sys.stderr)
        if not res or len(rows) >= total: break
        time.sleep(0.3)
    with open(out,"w") as f: json.dump(rows, f)
    with open(out.replace(".json","_noprograms.json"),"w") as f: json.dump([{k:v for k,v in r.items() if k!="programs"} for r in rows], f)
    print(f"done {len(rows)} schools -> {out}", file=sys.stderr)
if __name__ == "__main__": main()
