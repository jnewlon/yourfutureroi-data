#!/usr/bin/env python3
"""Build hud_fmr.json and col_adjustments.json from yourfutureroi-data/sources."""

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

HUD_FILE = "hud/fy2026_safmrs_by_zip.csv"
OEWS_FILE = "bls/oews_m2025_state_all_occupations.csv"
RPP_FILE = "bea/bea_rpp_state_2024.csv"

RENT_COLUMNS = ("efficiency", "1br", "2br", "3br", "4br")
US_NAMES = {"us", "u.s.", "united states", "united states of america"}


def norm(header):
    return header.strip().lower().replace(" ", "_")


def read_rows(path):
    if not path.exists():
        sys.exit(f"ERROR: {path} not found")
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = [
            {norm(k): (v or "").strip() for k, v in row.items() if k}
            for row in csv.DictReader(f)
        ]
    if not rows:
        sys.exit(f"ERROR: {path} has 0 rows")
    return rows


def require(rows, columns, path):
    missing = [c for c in columns if c not in rows[0]]
    if missing:
        sys.exit(f"ERROR: {path} is missing columns {missing}; found {list(rows[0])}")


def number(text):
    t = (text or "").replace("$", "").replace(",", "").strip()
    try:
        return float(t)
    except ValueError:
        return None


def build_hud(path):
    rows = read_rows(path)
    require(rows, ["zip", *RENT_COLUMNS, "metro_area", "hud_area_code"], path)

    by_zip = {}
    skipped = []
    for i, r in enumerate(rows):
        digits = "".join(ch for ch in r["zip"] if ch.isdigit())
        rents = [number(r[c]) for c in RENT_COLUMNS]
        if not digits or len(digits) > 5 or any(v is None for v in rents):
            skipped.append(i + 2)
            continue
        by_zip.setdefault(digits.zfill(5), []).append({
            "row": i,
            "metro": r["metro_area"],
            "area": r["hud_area_code"],
            "rents": rents,
        })

    out = {}
    multi = 0
    for z in sorted(by_zip):
        cands = by_zip[z]
        areas = list(dict.fromkeys(c["area"] for c in cands))
        pick = max(cands, key=lambda c: (c["rents"][2], -c["row"]))
        s, b1, b2, b3, b4 = (int(round(v)) for v in pick["rents"])
        entry = {"m": pick["metro"], "a": pick["area"],
                 "s": s, "1": b1, "2": b2, "3": b3, "4": b4}
        if len(areas) > 1:
            multi += 1
            entry["multi_area"] = True
            entry["areas"] = len(areas)
        out[z] = entry

    if not out:
        sys.exit(f"ERROR: {path} produced 0 ZIPs")

    meta = {
        "source": "U.S. Department of Housing and Urban Development, "
                  "Small Area Fair Market Rents",
        "year": "FY2026",
        "citation": "HUD Small Area FMR FY2026",
        "url": "https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html",
        "download": "https://www.huduser.gov/portal/datasets/fmr/fmr2026/"
                    "fy2026_safmrs_revised.xlsx",
        "input_file": HUD_FILE,
        "fields": {"m": "metro_area", "a": "hud_area_code", "s": "efficiency",
                   "1": "1br", "2": "2br", "3": "3br", "4": "4br",
                   "multi_area": "true when the ZIP spans more than one HUD area",
                   "areas": "number of HUD areas listing this ZIP"},
        "multi_area_rule": "highest 2br rent among the ZIP's HUD areas "
                           "(all sizes taken from that area)",
        "input_rows": len(rows),
        "rows_skipped": len(skipped),
        "zips": len(out),
        "multi_area_zips": multi,
        "generated": date.today().isoformat(),
    }
    return {"_meta": meta, **out}, skipped


def build_salary(path, national_override):
    rows = read_rows(path)
    require(rows, ["state", "state_abbr", "a_median"], path)
    national = national_override
    medians = {}
    for r in rows:
        abbr = r["state_abbr"].upper()
        median = number(r["a_median"])
        if abbr == "US" or r["state"].lower() in US_NAMES:
            if national is None:
                national = median
            continue
        if median is not None:
            medians[abbr] = median
    if not national:
        sys.exit("ERROR: no U.S. row in the OEWS file. Pass --national-median with the "
                 "May 2025 OEWS U.S. all-occupations annual median from "
                 "https://www.bls.gov/oes/current/oes_nat.htm")
    return {k: round(v / national, 2) for k, v in medians.items()}, national


def build_rpp(path):
    rows = read_rows(path)
    require(rows, ["state", "year", "rpp_all_items"], path)
    years = sorted({r["year"] for r in rows})
    rpp = {}
    for r in rows:
        name = r["state"].strip().lower()
        value = number(r["rpp_all_items"])
        if name in US_NAMES or value is None:
            continue
        rpp[name] = round(value / 100.0, 2)
    return rpp, years


def build_col(existing_path, oews_path, rpp_path, national_override):
    with open(existing_path, encoding="utf-8") as f:
        existing = json.load(f)
    states = existing["states"] if isinstance(existing, dict) else existing

    salary, national = build_salary(oews_path, national_override)
    rpp, years = build_rpp(rpp_path)

    missing = []
    out = []
    for s in states:
        code, name = s["code"], s["name"]
        if code not in salary or name.lower() not in rpp:
            missing.append(f"{code} (OEWS: {code in salary}, RPP: {name.lower() in rpp})")
            continue
        row = dict(s)
        row["salary"] = salary[code]
        row["col"] = rpp[name.lower()]
        row["personal"] = rpp[name.lower()]
        out.append(row)

    if missing:
        sys.exit("ERROR: no value for: " + ", ".join(missing)
                 + ". Nothing written, so no state keeps an old figure under a new label.")

    meta = {
        "citation": "BLS OEWS May 2025 state wages · BEA Regional Price Parities 2024",
        "salary": {
            "source": "U.S. Bureau of Labor Statistics, Occupational Employment and "
                      "Wage Statistics, State estimates, all occupations",
            "year": "May 2025",
            "url": "https://www.bls.gov/oes/tables.htm",
            "input_file": OEWS_FILE,
            "basis": "state a_median ÷ U.S. a_median, rounded to 2 decimals",
            "us_median": national,
        },
        "col": {
            "source": "U.S. Bureau of Economic Analysis, Regional Price Parities by State",
            "year": "2024",
            "years_in_file": years,
            "url": "https://www.bea.gov/data/prices-inflation/"
                   "regional-price-parities-state-and-metro-area",
            "input_file": RPP_FILE,
            "basis": "rpp_all_items ÷ 100; also used for 'personal'",
        },
        "unchanged_fields": [k for k in out[0]
                             if k not in ("code", "name", "salary", "col", "personal")],
        "unchanged_from": str(existing_path),
        "states": len(out),
        "generated": date.today().isoformat(),
    }
    if years != ["2024"]:
        print(f"WARNING: RPP file years are {years}, expected ['2024']")
    return {"_meta": meta, "states": out}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {path} ({path.stat().st_size:,} bytes)")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sources", type=Path, default=Path("../yourfutureroi-data/sources"))
    p.add_argument("--existing-col", type=Path,
                   default=Path("assets/data/col_adjustments.json"))
    p.add_argument("--out", type=Path, default=Path("build/col_data"))
    p.add_argument("--national-median", type=float, default=None)
    a = p.parse_args()

    hud, skipped = build_hud(a.sources / HUD_FILE)
    col = build_col(a.existing_col, a.sources / OEWS_FILE, a.sources / RPP_FILE,
                    a.national_median)

    write(a.out / "hud_fmr.json", hud)
    write(a.out / "col_adjustments.json", col)

    m = hud["_meta"]
    print(f"HUD: {m['input_rows']:,} rows -> {m['zips']:,} ZIPs; "
          f"{m['multi_area_zips']:,} in more than one HUD area "
          f"(highest 2BR rent used); {m['rows_skipped']} rows skipped")
    if skipped:
        print("  skipped CSV lines (first 20):", skipped[:20])
    print(f"COL: {col['_meta']['states']} states; U.S. median "
          f"${col['_meta']['salary']['us_median']:,.0f}")


if __name__ == "__main__":
    main()
