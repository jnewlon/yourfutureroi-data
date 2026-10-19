"""Add College Scorecard cohort counts to yourfutureroi_schools.json.
programs[].earnings.{1_yr,4_yr,5_yr}.count <- EARN_COUNT_WNE_{1YR,4YR,5YR} (Field of Study file; match UNITID+CIPCODE+CREDLEV)
latest.earnings.10_yrs_after_entry.count  <- COUNT_WNE_P10 (Institution file; match UNITID), inserted right after ...median
Suppressed/missing (PS, PrivacySuppressed, NULL, NA, blank) or unmatched -> null. Nothing else changes.
--only-4yr: add only programs[].earnings.4_yr.count (the one field whose medians match the 10/15/2026 release).
usage: add_cohort_counts.py schools.json fos.csv inst.csv out.json [--only-4yr]"""
import csv,json,sys
SCH,FOS,INST,OUT=sys.argv[1:5]
ONLY4='--only-4yr' in sys.argv
YRS=('4_yr',) if ONLY4 else ('1_yr','4_yr','5_yr')
def num(v):
    try: f=float(v)
    except (TypeError,ValueError): return None
    return int(f) if f.is_integer() else f
fos={}
for r in csv.DictReader(open(FOS,encoding='utf-8-sig')):
    if not r['UNITID'].isdigit(): continue  # rows with UNITID=NA cannot be matched by UNITID
    fos[(int(r['UNITID']),r['CIPCODE'].zfill(4),int(r['CREDLEV']))]={y:num(r['EARN_COUNT_WNE_'+y.replace('_yr','YR')]) for y in YRS}
inst={int(r['UNITID']):num(r['COUNT_WNE_P10']) for r in csv.DictReader(open(INST,encoding='utf-8-sig'))}
schools=json.load(open(SCH))
K='latest.earnings.10_yrs_after_entry.median'
for s in schools:
    if not ONLY4:
        items=list(s.items()); s.clear()
        for a,b in items:
            s[a]=b
            if a==K: s['latest.earnings.10_yrs_after_entry.count']=inst.get(s['id'])
    for p in s['programs']:
        f=fos.get((s['id'],p['code'],p['credential']['level']))
        for y in YRS: p['earnings'][y]['count']=f[y] if f else None
json.dump(schools,open(OUT,'w'),separators=(',',':'))
