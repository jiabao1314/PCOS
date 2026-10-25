"""Post hoc endpoint versus annual-chained descriptive decomposition.

Both allocations sum to the same contrast change; neither is causal or uncertain-
ty propagation. This script needs the same licensed source inputs as the main run.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from analyze_strata import normalize
ROOT=Path(__file__).resolve().parents[1]

def run():
 d=normalize(next((ROOT/'data/raw/strata_annual').glob('*.csv')))
 p=pd.read_csv(ROOT/'data/processed/population.csv')
 d=d[d.measure_name.eq('Prevalence')].merge(p[['location_id','year','age_group_id','population']],on=['location_id','year','age_group_id'],validate='many_to_one')
 d['rate']=d.val/d.population*1e5
 w=pd.read_csv(ROOT/'data/processed/weights.csv').set_index('age_name').weight
 out=[];country=[]
 for minage in [15,20]:
  ages=[a for a in w.index if int(a[:2])>=minage];wa=w.loc[ages]/w.loc[ages].sum()
  for (cause,typ),g in d[d.age_name.isin(ages)].groupby(['cause_name','infertility_type']):
   ref=g[g.location_name.ne('China')].copy()
   ref['share']=ref.population/ref.groupby(['year','age_name']).population.transform('sum')
   cn=g[g.location_name.eq('China')].pivot(index='year',columns='age_name',values='rate').loc[:,ages]@wa
   ref['weighted_rate']=ref.rate*ref.share*ref.age_name.map(wa);ar=ref.groupby('year').weighted_rate.sum()
   for start in [1990,2010]:
    for end in [2021,2022,2023]:
     for path in ['endpoint','annual_chain']:
      breaks=[start,end] if path=='endpoint' else list(range(start,end+1));rates=0.;shares=0.
      for t0,t1 in zip(breaks[:-1],breaks[1:]):
       x=ref[ref.year.eq(t0)].set_index(['location_name','age_name'])[['rate','share']].join(ref[ref.year.eq(t1)].set_index(['location_name','age_name'])[['rate','share']],lsuffix='_0',rsuffix='_1',validate='one_to_one')
       weights=x.index.get_level_values('age_name').map(wa).to_numpy()
       rc=-weights*(x.share_0+x.share_1)/2*(x.rate_1-x.rate_0)
       sc=-weights*(x.rate_0+x.rate_1)/2*(x.share_1-x.share_0)
       rates+=rc.sum();shares+=sc.sum()
       if minage==15 and start==1990 and end==2023:
        for name in x.index.get_level_values(0).unique():country.append(dict(cause=cause,type=typ,path=path,start=t0,end=t1,country=name,rate_component=rc.xs(name).sum(),share_component=sc.xs(name).sum()))
      cc=cn.loc[end]-cn.loc[start];delta=(cn.loc[end]-ar.loc[end])-(cn.loc[start]-ar.loc[start])
      if not np.isclose(cc+rates+shares,delta,atol=1e-8):raise AssertionError('Additivity failure')
      out.append(dict(min_age=minage,cause=cause,type=typ,start=start,end=end,path=path,change_D=delta,china_rates=cc,reference_rates=rates,reference_shares=shares))
 out=pd.DataFrame(out);keys=['min_age','cause','start','end','path'];nums=['change_D','china_rates','reference_rates','reference_shares']
 totals=out.groupby(keys,as_index=False)[nums].sum();totals['type']='Total';out=pd.concat([out,totals],ignore_index=True)
 out['share_percent_of_signed_change']=100*out.reference_shares/out.change_D
 old=pd.read_csv(ROOT/'results/tables/reference_composition_decomposition.csv')
 a=out[(out.path=='endpoint')&(out.min_age==15)]
 c=a.merge(old[old.variant.eq('main')],on=['cause','type','start','end'],suffixes=('_new','_old'),validate='one_to_one')
 assert np.allclose(c.reference_shares,c.reference_composition_component,atol=1e-8)
 dest=ROOT/'results/tables';out.to_csv(dest/'chained_composition_sensitivity.csv',index=False)
 pd.DataFrame(country).to_csv(dest/'chained_country_components.csv',index=False)
 audit={'status':'completed; post hoc time-path sensitivity; not a new method','rows':len(out),'max_endpoint_difference':float(abs(c.reference_shares-c.reference_composition_component).max()),'maximum_identity_error':float(abs(out.china_rates+out.reference_rates+out.reference_shares-out.change_D).max()),'uncertainty':'point estimates only, not design CIs or GBD uncertainty intervals'}
 (ROOT/'docs/chained_composition_qc.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
if __name__=='__main__':run()
