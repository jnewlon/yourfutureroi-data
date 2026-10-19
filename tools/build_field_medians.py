"""Build sources/scorecard/national_field_medians.csv from official College Scorecard files.
Weighted median = lower weighted median: sort program medians ascending, take the first value
whose cumulative weight reaches >= 50% of total weight. Non-numeric (PrivacySuppressed/NULL/blank) = missing."""
import csv,sys,collections
FOS,INST,OUT=sys.argv[1:4]
SRC_YEAR_FOS="Scorecard release 2026-10-15 (Most-Recent-Cohorts-Field-of-Study_10152026); earnings cohort AY2017-18+AY2018-19 completers measured CY2022+CY2023, 2024 dollars"
SRC_YEAR_INST="Scorecard release 2026-10-15 (Most-Recent-Cohorts-Institution_10152026); earnings cohort AY2011-12+AY2012-13 entrants measured CY2022+CY2023, 2024 dollars"
def num(v):
    try: return float(v)
    except: return None
def wmedian(pairs):
    pairs=sorted(pairs);tot=sum(w for _,w in pairs);c=0
    for v,w in pairs:
        c+=w
        if c>=tot/2: return v,tot
g=collections.defaultdict(list);stats=collections.Counter()
for r in csv.DictReader(open(FOS,encoding='utf-8-sig')):
    stats['fos_rows']+=1
    m,w=num(r['EARN_MDN_4YR']),num(r['EARN_COUNT_WNE_4YR'])
    if m is None or w is None or w<=0: stats['fos_missing']+=1; continue
    g[(r['CIPCODE'].zfill(4),r['CREDLEV'])].append((m,w))
rows=[]
for (cip,cl),p in sorted(g.items()):
    v,t=wmedian(p); rows.append([cip,cl,int(round(v)),int(t),SRC_YEAR_FOS])
seen={};raw=0
for r in csv.DictReader(open(INST,encoding='utf-8-sig')):
    m,w=num(r['MD_EARN_WNE_P10']),num(r['COUNT_WNE_P10'])
    if m is None or w is None or w<=0: continue
    raw+=1; seen[r['OPEID6']]=(m,w)   # branch campuses repeat their OPEID6's values; count each OPEID6 once
v,t=wmedian(list(seen.values()))
rows.append(['ALL','INST_10YR',int(round(v)),int(t),SRC_YEAR_INST])
with open(OUT,'w',newline='') as f:
    w=csv.writer(f);w.writerow(['cip4','credential_level','median_earnings','cohort','source_year']);w.writerows(rows)
print(dict(stats),'groups',len(g),'inst rows with data',raw,'opeid6 units',len(seen),'INST_10YR',v,t)
