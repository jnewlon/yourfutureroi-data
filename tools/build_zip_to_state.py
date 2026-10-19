"""ZIP -> state. Primary: Census 2020 ZCTA-to-county relationship file (state = county FIPS state; ZCTAs spanning
states take the state with the most land area). Fallback for ZIPs that are not ZCTAs (PO box / unique / military):
GeoNames US postal codes (CC BY 4.0). Last fallback: HUD FY2026 SAFMR ZIPs whose HUD area name names exactly one state. usage: build_zip_to_state.py zcta_county.txt US.txt hud_fmr.json out.csv"""
import csv,sys,json,collections,re
Z,G,H,OUT=sys.argv[1:5]
F={'01':'AL','02':'AK','04':'AZ','05':'AR','06':'CA','08':'CO','09':'CT','10':'DE','11':'DC','12':'FL','13':'GA','15':'HI','16':'ID','17':'IL','18':'IN','19':'IA','20':'KS','21':'KY','22':'LA','23':'ME','24':'MD','25':'MA','26':'MI','27':'MN','28':'MS','29':'MO','30':'MT','31':'NE','32':'NV','33':'NH','34':'NJ','35':'NM','36':'NY','37':'NC','38':'ND','39':'OH','40':'OK','41':'OR','42':'PA','44':'RI','45':'SC','46':'SD','47':'TN','48':'TX','49':'UT','50':'VT','51':'VA','53':'WA','54':'WV','55':'WI','56':'WY','60':'AS','66':'GU','69':'MP','72':'PR','78':'VI'}
area=collections.defaultdict(lambda:collections.Counter())
for r in csv.DictReader(open(Z,encoding='utf-8-sig'),delimiter='|'):
    z=r['GEOID_ZCTA5_20'];c=r['GEOID_COUNTY_20']
    if not z or not c: continue
    area[z][F[c[:2]]]+=int(r['AREALAND_PART'] or 0)+int(r['AREAWATER_PART'] or 0)*0  # land area
census={z:a.most_common(1)[0][0] for z,a in area.items()}
multi={z:dict(a) for z,a in area.items() if len(a)>1}
geo={}
for r in csv.reader(open(G,encoding='utf-8'),delimiter='\t'):
    if r[4]: geo[r[1]]=r[4]
out=dict(census)
for z,s in geo.items(): out.setdefault(z,s)
hud=json.load(open(H));hud.pop('_meta',None);fromhud=[]
for z,v in hud.items():
    m=re.search(r', ([A-Z]{2}(?:-[A-Z]{2})*) ',v['m']+' ')
    if z not in out and m and '-' not in m.group(1): out[z]=m.group(1);fromhud.append(z)
print('added from HUD single-state names',len(fromhud),fromhud[:5])
with open(OUT,'w',newline='') as f:
    w=csv.writer(f);w.writerow(['zip','state_abbr'])
    for z in sorted(out): w.writerow([z,out[z]])
# audit
conf=[(z,census[z],geo[z]) for z in census if z in geo and census[z]!=geo[z]]
single=re.compile(r', ([A-Z]{2}) ')
hc=[]
for z,v in hud.items():
    m=re.search(r', ([A-Z]{2}(?:-[A-Z]{2})*) ',v['m']+' ')
    sts=m.group(1).split('-') if m else []
    if z in out and sts and out[z] not in sts: hc.append((z,out[z],v['m']))
print('census zctas',len(census),'multi-state zctas',len(multi),'geonames',len(geo),'added from geonames',len(out)-len(census),'total',len(out))
print('census vs geonames conflicts',len(conf),conf[:10])
print('HUD zips',len(hud),'missing',len(set(hud)-set(out)),sorted(set(hud)-set(out))[:20])
print('state not in HUD area name',len(hc),hc[:15])
print('states',len(set(out.values())),collections.Counter(out.values()).most_common()[-8:])
json.dump({'multi':multi,'conf':conf,'hud_conf':hc},open('audit.json','w'))
