import csv, sys, json, collections
cat={'121590000':'Commercial','121590001':'Employment','121590002':'Property','121590003':'Dispute','121590004':'Other'}
rows=[]
with open(sys.argv[1],newline='',encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        if r['cr_runtype']!='121590001': continue
        lab=r['cr_newcolumn'].split(); r['id']=lab[0]; r['ver']=r['cr_promptversion']
        raw=json.loads(r['cr_rawresponse'])
        r['legal']=raw.get('legal_matter',True)
        r['conf']=float(r['cr_confidence']); r['ctx']=r['cr_contextsufficient']=='True'
        r['amb']=r['cr_ambiguous']=='True'; r['rule']=r['cr_ruletriggered']; r['alt']=r['cr_alternativecategory']
        r['exp']=cat[r['cr_expectedcategory']]; r['pred']=cat[r['cr_predictedcategory']]
        r['need']=r['cr_expectedescalation']=='True'
        r['logged']=(r['cr_escalated']=='True') if r['ver'] in('v2','v3') else (r['conf']<0.7)
        rows.append(r)
sets={
 'DEV v1':[r for r in rows if r['id'].startswith('EV') and r['ver']=='v1'],
 'DEV v2':[r for r in rows if r['id'].startswith('EV') and r['ver']=='v2'],
 'DEV v3':[r for r in rows if r['id'].startswith('EV') and r['ver']=='v3'],
 'HOLDOUT1 v2 (seen, informed v3)':[r for r in rows if r['id'].startswith('HO') and r['ver']=='v2'],
 'HOLDOUT2 v3 (fresh)':[r for r in rows if r['id'].startswith('H2') and r['ver']=='v3'],
}
for k,v in sets.items(): print(k,len(v))
def gates(r):
    g={'logged':r['logged']}
    if r['ver']=='v3':
        comp = r['alt'] not in ('None','Other','')
        g['committed (logged OR alt competitor)']=r['logged'] or comp
        g['logged OR alt!=None']=r['logged'] or r['alt'] not in('None','')
    return g
def rep(name,rs,gname):
    f=lambda r: gates(r).get(gname,None)
    if any(f(r) is None for r in rs): return
    need=[r for r in rs if r['need']]; no=[r for r in rs if not r['need']]
    ok=sum(r['exp']==r['pred'] for r in rs)
    esc=sum(bool(f(r)) for r in rs)
    caught=sum(bool(f(r)) for r in need); fa=[r['id'] for r in no if f(r)]
    silent=[r['id'] for r in rs if not f(r) and r['exp']!=r['pred']]
    missed=[r['id'] for r in need if not f(r)]
    print(f"{name} | gate={gname}\n   acc {ok}/{len(rs)} ({100*ok/len(rs):.1f}%)  esc rate {esc}/{len(rs)} ({100*esc/len(rs):.0f}%)  caught {caught}/{len(need)} ({100*caught/len(need):.0f}%)  false esc {len(fa)}/{len(no)} {fa}\n   silent wrong {silent}  missed {missed}")
for name,rs in sets.items():
    for gname in ['logged','committed (logged OR alt competitor)','logged OR alt!=None']:
        rep(name,rs,gname)
print("\nmisclassified (category) v3 dev:",[(r['id'],r['exp'],r['pred']) for r in sets['DEV v3'] if r['exp']!=r['pred']])
print("misclassified H2:",[(r['id'],r['exp'],r['pred']) for r in sets['HOLDOUT2 v3 (fresh)'] if r['exp']!=r['pred']])
print("legal_matter false ids v3:",[r['id'] for r in rows if r['ver']=='v3' and not r['legal']])
print("clear v3 (dev+H2) alt breakdown:",[(r['id'],r['alt']) for r in rows if r['ver']=='v3' and not r['need'] and r['alt'] not in('None','')])
dup=[k for k,c in collections.Counter((r['id'],r['ver']) for r in rows).items() if c>1]; print("dupes",dup)
# logged escalated consistency for v3
bad=[r['id'] for r in rows if r['ver']=='v3' and r['logged']!=(bool(r['rule']) or (not r['legal']) or r['amb'] or (not r['ctx']) or r['conf']<0.7)]
print("v3 Escalated mismatches:",bad)
