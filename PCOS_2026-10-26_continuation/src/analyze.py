"""Data-gated main analysis. No artificial data fallback is permitted."""
from pathlib import Path
import argparse, json, hashlib, itertools, platform, sys
import numpy as np
import pandas as pd
from core import standardize, shapley, segmented_trend

ROOT = Path(__file__).resolve().parents[1]
STUDY = json.loads((ROOT / 'config/study.json').read_text())
KEY = ['gbd_version','location_id','year','sex_id','age_group_id','cause_id',
       'impairment_id','infertility_type','measure_name','metric_name']
REQUIRED = KEY + ['location_name','age_name','sex_name','cause_name','impairment_name','val','lower','upper']


def read_table(path, cols):
    if not path.exists():
        raise ValueError(f'Missing required input: {path.name}')
    frame = pd.read_csv(path)
    missing = set(cols) - set(frame.columns)
    if missing:
        raise ValueError(f'{path.name}: missing columns {sorted(missing)}')
    if frame.empty or frame[cols].isna().any().any():
        raise ValueError(f'{path.name}: empty file or missing required values')
    return frame


def load_validate(folder, review):
    gates = ['approved','pilot_verified','case_definition_verified','denominator_verified',
             'weights_source_verified','infertility_labels_and_ids_verified','type_total_verified','raw_manifest_verified']
    if not all(review.get(k) is True for k in gates):
        raise ValueError('DATA GATE CLOSED: official pilot and source metadata not verified')
    version = review.get('gbd_version')
    if version not in STUDY['version_preference']:
        raise ValueError('Version must be locked to GBD 2023 or GBD 2021')
    end = int(version[-4:])
    d = read_table(folder/'burden.csv', REQUIRED)
    pop = read_table(folder/'population.csv', ['gbd_version','location_id','year','sex_id','age_group_id','population'])
    w = read_table(folder/'weights.csv', ['age_name','weight'])
    if set(d.gbd_version) != {version} or set(pop.gbd_version) != {version}:
        raise ValueError('Mixed or mismatched GBD versions')
    if d.duplicated(KEY).any():
        raise ValueError('Duplicate burden keys')
    if set(d.sex_name) != {'Female'} or d.sex_id.nunique()!=1:
        raise ValueError('Female-only data required')
    if not d.impairment_name.str.contains('infertility',case=False,regex=False).all():
        raise ValueError('Target infertility impairment missing')
    if set(d.infertility_type) != {'Total'}:
        raise ValueError('Main input must contain verified Total infertility only; strata stored separately')
    for idcol, namecol in [('location_id','location_name'),('age_group_id','age_name'),('cause_id','cause_name')]:
        if d.groupby(idcol)[namecol].nunique().max()!=1 or d.groupby(namecol)[idcol].nunique().max()!=1:
            raise ValueError(f'Inconsistent ID map: {idcol}')
    allowed = [('location_name','countries'),('age_name','ages'),('cause_name','causes'),('measure_name','measures'),('metric_name','metrics')]
    for col, setting in allowed:
        if set(d[col]) != set(STUDY[setting]):
            raise ValueError(f'Incomplete/unexpected dimension {col}')
    if set(d.year) != set(range(1990,end+1)):
        raise ValueError('Incomplete annual coverage')
    dims = ['location_name','year','age_name','cause_name','measure_name','metric_name']
    expected = pd.MultiIndex.from_product([STUDY['countries'],range(1990,end+1),STUDY['ages'],STUDY['causes'],STUDY['measures'],STUDY['metrics']],names=dims)
    if d.duplicated(dims).any() or len(expected.difference(pd.MultiIndex.from_frame(d[dims]))):
        raise ValueError('Missing or repeated analytical cells')
    values = d[['val','lower','upper']].to_numpy(float)
    if not np.isfinite(values).all() or np.any(values<0) or (d.lower>d.val).any() or (d.val>d.upper).any():
        raise ValueError('Invalid or unordered official uncertainty intervals')
    pr = d[(d.measure_name=='Prevalence') & (d.metric_name=='Rate')]
    if (pr.val>100000).any() or (pr.upper>100000).any():
        raise ValueError('Prevalence rate outside probability bounds')
    pk = ['gbd_version','location_id','year','sex_id','age_group_id']
    if pop.duplicated(pk).any() or not np.isfinite(pop.population).all() or (pop.population<=0).any():
        raise ValueError('Invalid population denominator')
    for col in ['measure_name','metric_name']:
        if d.groupby(dims[:4])[col].nunique().min()!=2:
            raise ValueError('Incomplete measures or metrics')
    numbers = d[d.metric_name=='Number'].drop(columns=['metric_name']).rename(columns={'val':'number','lower':'number_lower','upper':'number_upper'})
    rates = d[d.metric_name=='Rate'][dims[:-1]+['val']].rename(columns={'val':'rate'})
    b = numbers.merge(rates,on=dims[:-1],validate='one_to_one').merge(pop[pk+['population']],on=pk,how='left',validate='many_to_one')
    if b.population.isna().any():
        raise ValueError('Missing matched population')
    if not np.allclose(b.number/b.population*100000,b.rate,rtol=STUDY['number_rate_rtol'],atol=STUDY['number_rate_atol']):
        raise ValueError('Number / population does not reproduce rate; inspect units and denominator')
    if w.age_name.duplicated().any() or set(w.age_name)!=set(STUDY['ages']) or not np.isfinite(w.weight).all() or (w.weight<=0).any():
        raise ValueError('Invalid or incomplete standard weights')
    w['weight'] = w.weight/w.weight.sum()
    b = b.merge(w,on='age_name',validate='many_to_one')
    return b,w,end


def summarize(b, ages=None, leave_out=None, fixed=False):
    q = b[b.age_name.isin(ages or STUDY['ages'])].copy()
    weights = q[['age_name','weight']].drop_duplicates().set_index('age_name').weight
    weights = weights/weights.sum()
    q['weight'] = q.age_name.map(weights)
    country = q.assign(weighted=q.rate*q.weight).groupby(['location_name','year','cause_name','measure_name'],as_index=False).agg(asr=('weighted','sum'),number=('number','sum'))
    ref = q[(q.location_name!='China') & (q.location_name!=leave_out)].copy()
    by = ['year','age_name','cause_name','measure_name']
    if fixed:
        base = ref[ref.year==1990][['location_name','age_name','cause_name','measure_name','population']].copy()
        base['fixed_weight'] = base.population/base.groupby(['age_name','cause_name','measure_name']).population.transform('sum')
        ref = ref.merge(base.drop(columns='population'),on=['location_name','age_name','cause_name','measure_name'],validate='many_to_one')
        ref['weighted_rate'] = ref.rate*ref.fixed_weight
        refage = ref.groupby(by,as_index=False).agg(rate=('weighted_rate','sum'))
        refage['number'] = np.nan  # No population total corresponds to the fixed-weight estimator.
    else:
        refage = ref.groupby(by,as_index=False).agg(number=('number','sum'),population=('population','sum'))
        refage['rate'] = refage.number/refage.population*100000
    refage['weight'] = refage.age_name.map(weights)
    refage['weighted'] = refage.rate*refage.weight
    rs = refage.groupby(['year','cause_name','measure_name'],as_index=False).agg(asr=('weighted','sum'),number=('number',lambda s:s.sum(min_count=1)))
    rs['location_name'] = 'Other 18 G20 countries' if leave_out is None else f'G20 reference excluding {leave_out}'
    cn = q[q.location_name=='China'][by+['rate','population','weight']]
    gap = cn.merge(refage[by+['rate']],on=by,suffixes=('_china','_reference'),validate='one_to_one')
    gap['age_rate_difference'] = gap.rate_china-gap.rate_reference
    gap['asr_gap_contribution'] = gap.weight*gap.age_rate_difference
    gap['benchmark_number_difference'] = gap.population*gap.age_rate_difference/100000
    comp = country[country.location_name=='China'].merge(rs,on=['year','cause_name','measure_name'],suffixes=('_china','_reference'),validate='one_to_one')
    comp['rate_difference'] = comp.asr_china-comp.asr_reference
    comp['rate_ratio'] = np.divide(comp.asr_china,comp.asr_reference,where=comp.asr_reference>0,out=np.full(len(comp),np.nan))
    checks = gap.groupby(['year','cause_name','measure_name']).asr_gap_contribution.sum().reset_index()
    checks = checks.merge(comp,on=['year','cause_name','measure_name'])
    if not np.allclose(checks.asr_gap_contribution,checks.rate_difference,atol=1e-8):
        raise ArithmeticError('Age contributions do not sum to ASR gap')
    return pd.concat([country,rs],ignore_index=True),comp,gap


def run(folder, output, review):
    b,w,end = load_validate(folder,review)
    output.mkdir(parents=True,exist_ok=True)
    tables, comp, gap = summarize(b)
    tables.to_csv(output/'burden_standardized.csv',index=False)
    comp.to_csv(output/'china_reference_comparison.csv',index=False)
    gap.to_csv(output/'age_contributions_and_benchmark.csv',index=False)
    w.to_csv(output/'normalized_weights.csv',index=False)
    for name,col in [('table1',comp),('country_end_year',tables)]:
        col[col.year.isin([1990,end] if name=='table1' else [end])].to_csv(output/f'{name}.csv',index=False)
    delta = gap[gap.year==end].merge(gap[gap.year==1990],on=['age_name','cause_name','measure_name'],suffixes=('_end','_start'))
    delta['change_in_gap_contribution'] = delta.asr_gap_contribution_end-delta.asr_gap_contribution_start
    delta.to_csv(output/'age_contributions_to_gap_change.csv',index=False)
    decomposition = []
    prev = b[b.measure_name=='Prevalence']
    for (country,cause), grp in prev.groupby(['location_name','cause_name']):
        for first in [1990,2010]:
            a = grp[grp.year==first].set_index('age_name').loc[STUDY['ages']]
            z = grp[grp.year==end].set_index('age_name').loc[STUDY['ages']]
            parts,change = shapley(a.population,z.population,a.rate/100000,z.rate/100000)
            decomposition.append(dict(country=country,cause=cause,start=first,end=end,net_case_change=change,**parts))
    pd.DataFrame(decomposition).to_csv(output/'case_change_decomposition.csv',index=False)
    sensitivities = []
    for label, kw in [('age20_49',{'ages':STUDY['ages'][1:]}),('fixed1990_country_weights',{'fixed':True}),*[(f'leave_out_{c}',{'leave_out':c}) for c in STUDY['countries'] if c!='China']]:
        _,s,_ = summarize(b,**kw)
        s['sensitivity'] = label
        sensitivities.append(s)
    pd.concat(sensitivities).to_csv(output/'reference_sensitivities.csv',index=False)
    trends = []
    for (loc,cause,measure),grp in tables.groupby(['location_name','cause_name','measure_name']):
        for first in [1990,2010]:
            g = grp[grp.year>=first].sort_values('year')
            fit = segmented_trend(g.year,g.asr)
            trends.append(dict(location=loc,cause=cause,measure=measure,start=first,end=end,**fit))
    (output/'segmented_trends_point_estimates.json').write_text(json.dumps(trends,indent=2,allow_nan=False))
    manifest = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.csv')}
    (output/'run_provenance.json').write_text(json.dumps({'inputs_sha256':manifest,'review':review,'python':platform.python_version(),'rows':len(b),'version':review['gbd_version'],'derived_intervals':'None; no jointly aligned draws supplied','module_scope':'Core analysis; additional executed modules and scientific limitations are documented in docs/STATUS.md'},indent=2))
    return len(b)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=ROOT/'data/processed')
    parser.add_argument('--output',type=Path,default=ROOT/'results/tables')
    args=parser.parse_args()
    try:
        rows=run(args.input,args.output,json.loads((ROOT/'config/data_review.json').read_text()))
        print(f'Core analysis completed: {rows} age-specific measure cells. See provenance for remaining modules.')
    except (ValueError,ArithmeticError) as exc:
        print(str(exc),file=sys.stderr)
        sys.exit(2)
