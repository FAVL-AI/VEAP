import json,collections,sys,hashlib
cur=json.load(open('x1/step1/suite-summary.json'));old=json.load(open('artifacts/research/reexecuted-factorial.json'))
def table(d):
    t=collections.OrderedDict()
    for r in d['records']:
        k=f"{r['policy']}__gate_{'on' if r['shield'] else 'off'}";a=t.setdefault(k,[0,0,0,0])
        a[0]+=1;a[1]+=bool(r['task_completed']);a[2]+=bool(r['verified']);a[3]+=r['safety_violations']
    return {k:{'n':v[0],'completed':v[1],'verified':v[2],'violations':v[3]} for k,v in t.items()}
def cells(d):
    c=collections.defaultdict(set);n=collections.Counter()
    for r in d['records']:
        k=(r['scenario_id'],r['split'],r['policy'],'on' if r['shield'] else 'off');c[k].add(r['trace_sha256']);n[k]+=1
    return {"|".join(k):{'distinct':len(v),'n':n[k]} for k,v in sorted(c.items())}
key=lambda r:(r['scenario_id'],r['seed'],r['policy'],r['shield'])
om={key(r):r for r in old['records']}
fields=['task_completed','verified','safety_violations','interventions','steps','trace_sha256','scenario_sha256']
diff=collections.Counter()
for r in cur['records']:
    o=om.get(key(r))
    for f in fields:
        if o is None or o.get(f)!=r.get(f): diff[f]+=1
sc={};[sc.setdefault(r['scenario_id'],(r['split'],r['scenario_sha256'],om[key(r)]['scenario_sha256'])) for r in cur['records']]
cc=cells(cur);inv=sum(1 for v in cc.values() if v['distinct']==1)
out={'current_table':table(cur),'stored_table':table(old),'records_current':len(cur['records']),'records_stored':len(old['records']),
 'fields_differing_vs_stored':{f:diff[f] for f in fields},'scenarios':{k:{'split':v[0],'current_scenario_sha256':v[1],'stored_scenario_sha256':v[2]} for k,v in sc.items()},
 'cells':cc,'seed_invariant_cells':f"{inv}/{len(cc)}"}
json.dump(out,open('x1/step1/step1_analysis.json','w'),indent=1);print(json.dumps(out,indent=1))
