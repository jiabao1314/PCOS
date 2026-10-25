#!/usr/bin/env python3
"""Independent WPP benchmark sensitivity using existing GBD 2023 age-specific rates.

UN WPP changes only comparator country share, never disease rate or denominator.
All differences are model-conditioned descriptive point estimates, NOT 95% UIs.
"""
import pandas as pd, numpy as np, json, hashlib
from pathlib import Path
from itertools import product
HERE=Path(__file__).resolve().parent
GBD=HERE/'raw_gbd'; SOURCE=HERE/'source'; OUT=HERE/'results';OUT.mkdir(exist_ok=True)
TOTAL=GBD/'IHME-GBD_2023_DATA-1b13e337-1.csv'
STRATA=GBD/'IHME-GBD_2023_DATA-416daf73-1.csv'
POP=GBD/'IHME-GBD_2023_DATA-916826fb-1.csv'
WEIGHTS=GBD/'weights.csv'
UN=SOURCE/'UN_WPP2024_G20_female_15_49_1990_2023.csv'
YEARS=list(range(1990,2024)); AGES=list(range(15,50,5));N=19*34*7
COUNTRIES=['Argentina','Australia','Brazil','Canada','China','France','Germany','India','Indonesia','Italy','Japan','Mexico','Republic of Korea','Russian Federation','Saudi Arabia','South Africa','Türkiye','United Kingdom','United States of America']
CAUSES=['Polycystic ovarian syndrome','Endometriosis']; TYPES=['Total','Primary','Secondary']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(d):
 d=d.copy();d['age_start']=d.age_id.astype(int).map(lambda x: (x-5)*5)
 assert set(d.age_start)==set(AGES),d.age_start.unique()
 return d

pop=clean(pd.read_csv(POP));assert len(pop)==N
assert set(pop.location_name)==set(COUNTRIES)
assert pop[['location_name','age_start','year']].duplicated().sum()==0
pop=pop.rename(columns={'location_name':'country','val':'gbd_pop'})[['country','age_start','year','gbd_pop']]
assert (pop.gbd_pop>0).all()
un=pd.read_csv(UN).rename(columns={'gbd_country':'country'})
assert len(un)==N and set(un.country)==set(COUNTRIES) and un[['country','age_start','year']].duplicated().sum()==0
pop=pop.merge(un[['country','year','age_start','un_female_pop']],on=['country','year','age_start'],how='left',validate='1:1')
assert pop.un_female_pop.notna().all()
wd=pd.read_csv(WEIGHTS)
wd['age_start']=wd.age_name.str.extract(r'(\d+)').astype(int)
w=wd.set_index('age_start')['weight'];w=w/w.sum()
assert abs(w.sum()-1)<1e-12 and set(w.index)==set(AGES)

# GBD2023 modeled case numbers, not imputing missing or mixing YLD with prevalence.
base=clean(pd.read_csv(TOTAL))
base=base.query('measure_id==5 and metric_id==1 and rei_id==198 and sex_id==2').copy();base['subtype']='Total'
other=clean(pd.read_csv(STRATA))
other=other.query('measure_id==5 and metric_id==1 and rei_id in [220,221] and sex_id==2').copy()
other['subtype']=other.rei_id.map({220:'Primary',221:'Secondary'})
df=pd.concat([base,other],ignore_index=True)
df=df.rename(columns={'location_name':'country','cause_name':'cause','val':'gbd_cases'})
assert len(df)==N*2*3,len(df)
assert set(df.cause)==set(CAUSES) and set(df.subtype)==set(TYPES)
assert df[['country','year','age_start','cause','subtype']].duplicated().sum()==0
r=df[['country','year','age_start','cause','subtype','gbd_cases']].merge(pop,on=['country','year','age_start'],how='left',validate='m:1')
assert r.gbd_pop.notna().all()
r['gbd_rate']=1e5*r.gbd_cases/r.gbd_pop
piv=r.pivot(index=['country','year','age_start','cause'],columns='subtype',values='gbd_cases')
assert (piv.Total-piv.Primary-piv.Secondary).abs().max()<1e-6, (piv.Total-piv.Primary-piv.Secondary).abs().max()

# Define time-and-age dependent shares independently for each source.
ref=r[r.country!='China'].copy();china=r[r.country=='China'].copy()
for source,pc in [('GBD','gbd_pop'),('UN-WPP2024','un_female_pop')]:
 denom=pop[pop.country!='China'].groupby(['year','age_start'])[pc].sum()
 ref[f's_{source}']=ref[pc]/ref.set_index(['year','age_start']).index.map(denom).to_numpy()
 assert np.allclose(ref.groupby(['year','age_start','cause','subtype'])[f's_{source}'].sum().to_numpy(),1,rtol=0,atol=1e-12)

annual=[]; decomposition=[]; ycompare=[]; loo=[]

def summary(sub, source, y, benchmark='dynamic', missing=None):
 tmp=sub[sub.year==y].copy()
 if missing:tmp=tmp[tmp.country!=missing]
 k=f's_{source}'
 if benchmark=='equal':
  tmp['_s']=1/tmp.groupby('age_start').country.transform('count')
 elif benchmark=='fixed1990':
  baseref=ref[(ref.year==1990)&(ref.cause==sub.cause.iloc[0])&(ref.subtype==sub.subtype.iloc[0])][['country','age_start',k]].rename(columns={k:'_s'})
  tmp=tmp.merge(baseref,on=['country','age_start'],how='left',validate='1:1')
  if missing:tmp['_s']/=tmp.groupby('age_start')._s.transform('sum')
 elif benchmark=='dynamic':
  if missing:tmp['_s']=tmp[k]/tmp.groupby('age_start')[k].transform('sum')
  else:tmp['_s']=tmp[k]
 else:raise ValueError(benchmark)
 assert len(tmp)==7*(17 if missing else 18)
 agerate=(tmp.assign(prod=tmp.gbd_rate*tmp._s).groupby('age_start')['prod'].sum())
 assert np.isclose(tmp.groupby('age_start')['_s'].sum().to_numpy(),np.ones(7),rtol=0,atol=1e-12).all()
 c=china[(china.year==y)&(china.cause==sub.cause.iloc[0])&(china.subtype==sub.subtype.iloc[0])].set_index('age_start').gbd_rate
 ref_aspr=float((agerate*w).sum()); china_aspr=float((c*w).sum())
 return dict(china_aspr=china_aspr,ref_aspr=ref_aspr,gap=china_aspr-ref_aspr,ratio=china_aspr/ref_aspr)

for (cause,t),sub in ref.groupby(['cause','subtype'],sort=True):
 for source in ('GBD','UN-WPP2024'):
  for y in YEARS:
   for bench in ['dynamic','fixed1990','equal']:
    s=summary(sub,source,y,bench)
    annual.append(dict(cause=cause,subtype=t,source=source,year=y,benchmark=bench,**s))
  for end in [2021,2022,2023]:
   a=summary(sub,source,1990);b=summary(sub,source,end)
   d0=sub[sub.year==1990].set_index(['country','age_start'])
   d1=sub[sub.year==end].set_index(['country','age_start'])
   merged=d0[['gbd_rate',f's_{source}']].rename(columns={'gbd_rate':'r0',f's_{source}':'s0'}).join(d1[['gbd_rate',f's_{source}']].rename(columns={'gbd_rate':'r1',f's_{source}':'s1'}),validate='1:1')
   ww=merged.index.get_level_values('age_start').map(w).astype(float)
   ref_rate_effect=float((-ww*((merged.s0+merged.s1)/2)*(merged.r1-merged.r0)).sum())
   ref_comp_effect=float((-ww*((merged.r0+merged.r1)/2)*(merged.s1-merged.s0)).sum())
   china_rate_effect=b['china_aspr']-a['china_aspr']; net=b['gap']-a['gap']
   assert np.isclose(china_rate_effect+ref_rate_effect+ref_comp_effect,net,rtol=0,atol=1e-8),(cause,t,source,end,net,china_rate_effect+ref_rate_effect+ref_comp_effect)
   decomposition.append(dict(cause=cause,subtype=t,source=source,end=end,initial_gap=a['gap'],end_gap=b['gap'],net_gap_change=net,china_rate_effect=china_rate_effect,reference_rate_effect=ref_rate_effect,reference_country_composition_effect=ref_comp_effect,composition_share_of_net=ref_comp_effect/net if abs(net)>1e-10 else np.nan))
  for country in sorted(set(ref.country)):
   a=summary(sub,source,1990,missing=country);b=summary(sub,source,2023,missing=country)
   loo.append(dict(cause=cause,subtype=t,source=source,omitted_country=country,initial_gap=a['gap'],gap_2023=b['gap'],change=b['gap']-a['gap']))

annual=pd.DataFrame(annual);annual.to_csv(OUT/'all_annual_benchmark_aspr.csv',index=False)
decomp=pd.DataFrame(decomposition);decomp.to_csv(OUT/'symmetric_decomposition_1990_endpoints.csv',index=False)
loo=pd.DataFrame(loo);loo.to_csv(OUT/'leave_one_country_out.csv',index=False)

# Compare the composition itself, not only its effects on disease-specific rates.
tmp=ref.drop_duplicates(['country','year','age_start'])[['country','year','age_start','gbd_pop','un_female_pop','s_GBD','s_UN-WPP2024']].copy()
tmp['pop_ratio_UN_over_GBD']=tmp.un_female_pop/tmp.gbd_pop
tmp.to_csv(OUT/'population_country_age_crosswalk.csv',index=False)
TVD=(tmp.assign(absdiff=(tmp['s_UN-WPP2024']-tmp.s_GBD).abs()).groupby(['year','age_start'])['absdiff'].sum()/2).reset_index(name='total_variation_distance')
TVD.to_csv(OUT/'reference_share_source_difference_tvd.csv',index=False)

countryshare=tmp.copy()
countryshare['w']=countryshare.age_start.map(w)
countryshare['ws_un']=countryshare['s_UN-WPP2024']*countryshare.w
countryshare['ws_gbd']=countryshare['s_GBD']*countryshare.w
agg=countryshare.groupby(['country','year'],as_index=False)[['ws_un','ws_gbd']].sum()
share0=agg[agg.year==1990].set_index('country');share1=agg[agg.year==2023].set_index('country')
share_summary=pd.DataFrame({'country':share0.index,'UN_share_1990':share0.ws_un,'UN_share_2023':share1.ws_un,'GBD_share_1990':share0.ws_gbd,'GBD_share_2023':share1.ws_gbd})
share_summary['UN_share_change_1990_2023']=share_summary.UN_share_2023-share_summary.UN_share_1990
share_summary['GBD_share_change_1990_2023']=share_summary.GBD_share_2023-share_summary.GBD_share_1990
share_summary.reset_index(drop=True).to_csv(OUT/'reference_country_shares_1990_2023.csv',index=False)

# Existing exact benchmark reproduction using original GBD reference country shares.
q=annual.query("cause=='Polycystic ovarian syndrome' and subtype=='Total' and source=='GBD' and year==2023 and benchmark=='dynamic'").iloc[0]
assert abs(q.gap-(-121.3762163263026))<1e-6, q.gap
q2=decomp.query("cause=='Polycystic ovarian syndrome' and subtype=='Total' and source=='GBD' and end==2023").iloc[0]
assert abs(q2.reference_country_composition_effect-88.65)<.05,q2.reference_country_composition_effect

# Uncertainty caveat and pre-registered vs exploratory labels explicit.
res={
 'study':'GBD 2023 age-specific modeled infertility rates with independent UN WPP 2024 reference-country population shares',
 'population_weighing_only':True,
 'WPP_source_SHA256':sha(SOURCE/'WPP2024_PopulationByAge5GroupSex_Medium.csv.gz'),
 'WPP_subset_SHA256':sha(UN),
 'GBD_source_SHA256':{p.name:sha(p) for p in [TOTAL,POP,STRATA,WEIGHTS]},
 'record_count':{'UNWPP_country_year_age':len(un),'GBD_population_country_year_age':len(pop),'GBD_rate_country_year_age_cause_subtype':len(r)},
 'weights':{str(age):float(v) for age,v in w.items()},
 'population_shares_tvd':{'mean':TVD.total_variation_distance.mean(),'max':TVD.total_variation_distance.max(),'2023_age_mean':TVD[TVD.year==2023].total_variation_distance.mean()},
 'GBD_reference_2023_pcos_gap':float(q.gap),
 'national_marginal_UIs_not_joint_draws':True,
 'GBD_draws':False,
 'interpretation':'Descriptive point estimates, scenario sensitivity not posterior uncertainty, no independent disease-rate validation by UN population.'}
(OUT/'qc_summary.json').write_text(json.dumps(res,indent=2,ensure_ascii=False),encoding='utf-8')
for ca in CAUSES:
 print('\n==== '+ca+' ====')
 for typ in TYPES:
  print('SUBTYPE',typ)
  for source in ['GBD','UN-WPP2024']:
   for y in [1990,2022,2023]:
    v=annual.query('cause==@ca and subtype==@typ and source==@source and year==@y and benchmark=="dynamic"').iloc[0]
    print(source,y,'china %.4f'%v.china_aspr,'ref %.4f'%v.ref_aspr,'gap %.4f'%v.gap,'ratio %.4f'%v.ratio)
   z=decomp.query('cause==@ca and subtype==@typ and source==@source and end==2023').iloc[0]
   print('DECOMP',source,'net %.4f'%z.net_gap_change,'cn_rate %.4f'%z.china_rate_effect,'ref_rate %.4f'%z.reference_rate_effect,'composition %.4f'%z.reference_country_composition_effect,'share %.3f'%z.composition_share_of_net)
 print('TVD',res['population_shares_tvd'])
print('\nWRITTEN',len(list(OUT.iterdir())),'files')
