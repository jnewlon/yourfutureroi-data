"""Build IPEDS outcome / retention / net-price CSVs and derived/ipeds_by_school.json.
Inputs (NCES IPEDS Complete Data Files, final release): gr2023.csv, gr200_23.csv, om2023.csv, ef2023d.csv, sfa2223.csv
usage: build_ipeds.py RAW_DIR SCHOOLS_JSON OUT_DIR
Rules: blank / not applicable (A) -> null. Values NCES imputed (flags J,K,L,N,P) -> null. Reported (R),
analyst-corrected (C), implied zero (Z) and generated (G) values are kept. Percent fields are converted to 0-1 fractions.
GR rates are computed from GR counts (completers / adjusted cohort), rounded to 4 decimals."""
import csv,json,sys,os,collections
RAW,SCH,OUT=sys.argv[1:4]
IMPUTED=set('JKLNP')
def rd(name):
    f=open(os.path.join(RAW,name),encoding='latin-1',newline='');r=csv.DictReader(f)
    r.fieldnames=[x.strip() for x in r.fieldnames];return list(r)
def val(row,var,pct=False):
    v=(row.get(var) or '').strip();flag=(row.get('X'+var) or '').strip().strip('"')
    if v=='' or flag in IMPUTED or flag=='A': return None
    try: n=float(v)
    except ValueError: return None
    if pct: return round(n/100,4)
    return int(n) if n.is_integer() else n
def ratio(n,d): return None if n is None or d in (None,0) else round(n/d,4)
def write(name,cols,rows):
    with open(os.path.join(OUT,name),'w',newline='') as f:
        w=csv.writer(f);w.writerow(cols)
        for u in sorted(rows,key=int): w.writerow([u]+['' if rows[u].get(c) is None else rows[u][c] for c in cols[1:]])
# --- Graduation rates (GR2023 + GR200_23)
g=collections.defaultdict(dict)
for r in rd('gr2023.csv'): g[r['UNITID'].strip()][r['GRTYPE'].strip()]=val(r,'GRTOTLT')
gr={}
for u,t in g.items():
    d={}
    if '8' in t:   # 4-year: bachelor's or equivalent subcohort, cohort year 2017
        c=t.get('8');d.update(level='4yr',cohort=c,gr100=ratio(t.get('13'),c),gr150=ratio(t.get('12'),c))
    elif '29' in t:  # 2-year: degree/certificate-seeking cohort, cohort year 2020
        c=t.get('29');d.update(level='2yr',cohort=c,gr100=ratio(t.get('35'),c),gr150=ratio(t.get('30'),c))
    else: continue
    gr[u]=d
for r in rd('gr200_23.csv'):
    d=gr.setdefault(r['UNITID'],{})
    if val(r,'BAAC200') is not None or val(r,'BAGR200') is not None:
        d.update(gr200=val(r,'BAGR200',True),gr200_cohort=val(r,'BAAC200'),gr200_cohort_year=2015)
    elif val(r,'L4AC200') is not None or val(r,'L4GR200') is not None:
        d.update(gr200=val(r,'L4GR200',True),gr200_cohort=val(r,'L4AC200'),gr200_cohort_year=2019)
for d in gr.values():
    if 'level' in d: d['cohort_year']=2017 if d['level']=='4yr' else 2020
GRC=['unitid','level','cohort_year','cohort','gr100','gr150','gr200_cohort_year','gr200_cohort','gr200']
write('ipeds_graduation_rates.csv',GRC,gr)
# --- Outcome measures (OM2023), 2015-16 entering cohort, status at 8 years
GROUPS={'10':'ftft','20':'ftpt','30':'nftft','40':'nftpt'}
om=collections.defaultdict(dict)
for r in rd('om2023.csv'):
    k=GROUPS.get(r['OMCHRT'].strip())
    if not k: continue
    om[r['UNITID']].update({f'{k}_cohort':val(r,'OMACHRT'),f'{k}_award8':val(r,'OMAWDP8',True),
        f'{k}_still_enrolled':val(r,'OMENRYP',True),f'{k}_transferred':val(r,'OMENRAP',True)})
OMC=['unitid']+[f'{k}_{f}' for k in GROUPS.values() for f in ('cohort','award8','still_enrolled','transferred')]
write('ipeds_outcome_measures.csv',OMC,om)
# --- Retention (EF2023D): fall 2022 cohort retained to fall 2023
ret={}
for r in rd('ef2023d.csv'):
    ret[r['UNITID']]=dict(ft_cohort=val(r,'RRFTCTA'),ft_retention=val(r,'RET_PCF',True),pt_cohort=val(r,'RRPTCTA'),pt_retention=val(r,'RET_PCP',True))
RTC=['unitid','ft_cohort','ft_retention','pt_cohort','pt_retention']
write('ipeds_retention.csv',RTC,ret)
# --- Net price (SFA2223), 2022-23, full-time first-time undergrads
B=['0_30k','30_48k','48_75k','75_110k','110k_plus']
npx={}
for r in rd('sfa2223.csv'):
    d={'public_in_state_avg':val(r,'NPIST2'),'public_in_state_n':val(r,'GIS4N2'),'private_avg':val(r,'NPGRN2'),'private_n':val(r,'GRN4N2')}
    for i,b in enumerate(B,1):
        d[f'public_in_state_{b}']=val(r,f'NPIS4{i}2');d[f'public_in_state_{b}_n']=val(r,f'GIS4N{i}2')
        d[f'private_{b}']=val(r,f'NPT4{i}2');d[f'private_{b}_n']=val(r,f'GRN4N{i}2')
    npx[r['UNITID']]=d
NPC=['unitid']+[f'{s}_{x}' for s in ('public_in_state','private') for x in ['avg','n']+[y for b in B for y in (b,b+'_n')]]
write('ipeds_net_price.csv',NPC,npx)
# --- merged, app schools only
schools=json.load(open(SCH));out={};hit=collections.Counter()
for s in schools:
    u=str(s['id']);e={}
    for name,src,cols in (('graduation',gr,GRC),('outcome_measures',om,OMC),('retention',ret,RTC),('net_price',npx,NPC)):
        if u not in src: continue
        hit[name]+=1;row=src[u]
        if name=='net_price':
            # one basis per school: public in-state (NPIST/NPIS4x) if reported, else private (NPGRN/NPT4x)
            basis=next((b for b in ('public_in_state','private') if any(row[k] is not None for k in row if k.startswith(b))),None)
            e[name]={'basis':basis,**({k[len(basis)+1:]:row[k] for k in cols[1:] if k.startswith(basis+'_')} if basis else {})}
        else: e[name]={c:row.get(c) for c in cols[1:]}
    if e: out[u]=e
meta={'source':'NCES IPEDS Complete Data Files (final release)','url':'https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx',
 'files':{'graduation':'GR2023 (2017 4-yr bachelor cohort / 2020 2-yr cohort) + GR200_23 (2015 / 2019 cohorts)','outcome_measures':'OM2023 (2015-16 entering cohort, 8-year status)',
 'retention':'EF2023D (fall 2022 cohort retained to fall 2023)','net_price':'SFA2223 (2022-23 full-time first-time undergraduates)'},
 'notes':'Rates are 0-1 fractions. Blank, not-applicable and NCES-imputed values are null. See sources/README.md.','schools':len(out)}
json.dump({'_meta':meta,**out},open(os.path.join(OUT,'ipeds_by_school.json'),'w'),separators=(',',':'))
print('app schools',len(schools),'with any IPEDS',len(out),dict(hit))
