"""Annual primary/secondary infertility; original Number, same-release population.
Original Rate is independently checked in endpoint exports. No derived GBD UI.
"""
from pathlib import Path
import json,itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyze import ROOT,STUDY,summarize
from core import shapley

def normalize(p):
 d=pd.read_csv(p).rename(columns={'age_id':'age_group_id','rei_id':'impairment_id','rei_name':'infertility_type'})
 d['age_name']=d.age_name.str.replace(' years','',regex=False);d['measure_name']=d.measure_name.replace({'YLDs (Years Lived with Disability)':'YLDs'});return d

def run():
 d=normalize(next((ROOT/'data/raw/strata_annual').glob('*.csv')));e=normalize(next((ROOT/'data/raw/strata_endpoints').glob('*.csv')))
 dims=['location_name','year','age_name','cause_name','measure_name','infertility_type']
 types=['Primary infertility','Secondary infertility'];expected=pd.MultiIndex.from_product([STUDY['countries'],range(1990,2024),STUDY['ages'],STUDY['causes'],STUDY['measures'],types],names=dims)
 assert len(d)==len(expected)==36176 and not d.duplicated(dims).any() and not len(expected.difference(pd.MultiIndex.from_frame(d[dims])))
 assert set(d.metric_name)=={'Number'} and set(d.sex_name)=={'Female'}
 assert np.isfinite(d[['val','lower','upper']]).all().all() and (d.lower<=d.val).all() and (d.val<=d.upper).all() and (d.lower>=0).all()
 assert set(d.impairment_id)=={220,221}
 p=pd.read_csv(ROOT/'data/processed/population.csv');w=pd.read_csv(ROOT/'data/processed/weights.csv');w.weight/=w.weight.sum()
 b=d.rename(columns={'val':'number'}).merge(p[['location_id','year','age_group_id','population']],on=['location_id','year','age_group_id'],validate='many_to_one').merge(w,on='age_name',validate='many_to_one');b['rate']=b.number/b.population*1e5
 # Validate source Number against endpoint Number; reconstructed Rate against original endpoint Rate.
 errors={}
 for metric,col in [('Number','number'),('Rate','rate')]:
  q=b.merge(e[e.metric_name==metric][dims+['val']],on=dims,validate='one_to_one');assert len(q)==2128
  err=float(abs(q[col]-q.val).max());assert np.allclose(q[col],q.val,rtol=1e-7,atol=1e-6);errors[metric]=err
 total=pd.read_csv(ROOT/'data/processed/burden.csv');total=total[total.metric_name=='Number']
 summed=b.groupby(dims[:-1],as_index=False).number.sum().merge(total[dims[:-1]+['val']],on=dims[:-1],validate='one_to_one')
 assert len(summed)==18088 and np.allclose(summed.number,summed.val,rtol=1e-7,atol=1e-5)
 tables=[];comps=[];gaps=[];parts=[];sens=[]
 for typ,g in b.groupby('infertility_type'):
  tab,comp,gap=summarize(g)
  for label,kw in [('age20_49',{'ages':STUDY['ages'][1:]}),('fixed1990_country_weights',{'fixed':True}),*[(f'leave_out_{c}',{'leave_out':c}) for c in STUDY['countries'] if c!='China']]:
   _,ss,_=summarize(g,**kw);ss['infertility_type']=typ;ss['sensitivity']=label;sens.append(ss)
  for frame,collection in [(tab,tables),(comp,comps),(gap,gaps)]:frame['infertility_type']=typ;collection.append(frame)
  for (loc,cause),q in g[g.measure_name=='Prevalence'].groupby(['location_name','cause_name']):
   for start in [1990,2010]:
    first=q[q.year==start].set_index('age_name').loc[STUDY['ages']];last=q[q.year==2023].set_index('age_name').loc[STUDY['ages']]
    v,net=shapley(first.population,last.population,first.rate/1e5,last.rate/1e5);parts.append(dict(location=loc,cause=cause,type=typ,start=start,end=2023,net_change=net,**v))
 pd.concat(sens).to_csv(ROOT/'results/tables/strata_reference_sensitivities.csv',index=False)
 tab=pd.concat(tables);comp=pd.concat(comps);gap=pd.concat(gaps)
 tab.to_csv(ROOT/'results/tables/strata_standardized.csv',index=False);comp.to_csv(ROOT/'results/tables/strata_comparison.csv',index=False);gap.to_csv(ROOT/'results/tables/strata_age_contributions.csv',index=False);pd.DataFrame(parts).to_csv(ROOT/'results/tables/strata_case_decomposition.csv',index=False)
 (ROOT/'docs/strata_qc.json').write_text(json.dumps({'annual_number_rows':len(d),'endpoint_number_rate_rows':len(e),'original_id_map':d[['impairment_id','infertility_type']].drop_duplicates().to_dict('records'),'endpoint_max_absolute_errors':errors,'max_primary_secondary_sum_discrepancy':float(abs(summed.number-summed.val).max()),'rate_source':'Annual strata Number divided by verified GBD2023 female population; independently verified against original Rate at both endpoints','reason':'Full combined metric request exceeded remaining release quota; downloaded Number annually and original Number/Rate at endpoints'},indent=2))
 fig,axs=plt.subplots(2,2,figsize=(10.5,7.0),layout='constrained')
 for i,cause in enumerate(STUDY['causes']):
  for j,typ in enumerate(types):
   ax=axs[i,j]
   for loc,color in [('China','#ca5963'),('Other 18 G20 countries','#397da0')]:
    q=tab[(tab.cause_name==cause)&(tab.infertility_type==typ)&(tab.location_name==loc)&(tab.measure_name=='Prevalence')].sort_values('year');ax.plot(q.year,q.asr,label=loc,color=color,lw=1.6)
   ax.set_title(('Endometriosis' if i==0 else 'PCOS')+' - '+typ.lower(),fontsize=11);ax.set_xlabel('Year');ax.set_ylabel('Restricted-age ASPR per 100,000');ax.grid(alpha=.15);ax.spines[['top','right']].set_visible(False)
   if i==j==0:ax.legend(fontsize=8,frameon=False)
 for ext in ['pdf','png','svg']:fig.savefig(ROOT/f'results/figures/figS3_infertility_strata.{ext}',dpi=320)
 print('Validated strata; complete annual coverage; type sums match total')
 print(comp[(comp.year.isin([1990,2023]))&(comp.measure_name=='Prevalence')].to_string(index=False))
if __name__=='__main__':run()
