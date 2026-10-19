"""Refresh the Scorecard earnings medians in yourfutureroi_schools.json from the bulk "Most Recent" files.
School:   latest.earnings.10_yrs_after_entry.median <- MD_EARN_WNE_P10
          latest.earnings.6_yrs_after_entry.median  <- MD_EARN_WNE_P6   (Institution file, match UNITID)
Programs: earnings.{1_yr,4_yr,5_yr}.overall_median_earnings <- EARN_MDN_{1YR,4YR,5YR}
          (Field of Study file, match UNITID+CIPCODE+CREDLEV)
Suppressed (PS/PrivacySuppressed/NULL/NA/blank) -> null. Programs or schools absent from the release -> null
(kept in the file; no stale values). All other fields, key order and compact formatting are unchanged.
usage: refresh_earnings.py schools.json fos.csv inst.csv out.json"""
import csv,json,sys
SCH,FOS,INST,OUT=sys.argv[1:5]
def num(v):
    try: f=float(v)
    except (TypeError,ValueError): return None
    return int(f) if f.is_integer() else f
P={'1_yr':'EARN_MDN_1YR','4_yr':'EARN_MDN_4YR','5_yr':'EARN_MDN_5YR'}
S={'latest.earnings.10_yrs_after_entry.median':'MD_EARN_WNE_P10','latest.earnings.6_yrs_after_entry.median':'MD_EARN_WNE_P6'}
fos={}
for r in csv.DictReader(open(FOS,encoding='utf-8-sig')):
    if not r['UNITID'].isdigit(): continue
    fos[(int(r['UNITID']),r['CIPCODE'].zfill(4),int(r['CREDLEV']))]={y:num(r[c]) for y,c in P.items()}
inst={int(r['UNITID']):{k:num(r[c]) for k,c in S.items()} for r in csv.DictReader(open(INST,encoding='utf-8-sig'))}
schools=json.load(open(SCH))
for s in schools:
    i=inst.get(s['id'],{})
    for k in S: s[k]=i.get(k)
    for p in s['programs']:
        f=fos.get((s['id'],p['code'],p['credential']['level']),{})
        for y in P: p['earnings'][y]['overall_median_earnings']=f.get(y)
json.dump(schools,open(OUT,'w'),separators=(',',':'))
