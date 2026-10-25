"""Post-QC endpoint and published-weight rounding sensitivities; not prespecified."""
from pathlib import Path
from itertools import product
import json
import numpy as np
import pandas as pd
from analyze import load_validate,summarize,STUDY
from core import shapley,segmented_trend
ROOT=Path(__file__).resolve().parents[1]
def run():
 b,w,_=load_validate(ROOT/'data/processed',json.loads((ROOT/'config/data_review.json').read_text()));tables,comp,gap=summarize(b)
 out=[];changes=[]
 for cause in STUDY['causes']:
  for end in [2021,2022,2023]:
   a=comp[(comp.cause_name==cause)&(comp.measure_name=='Prevalence')&(comp.year==1990)].iloc[0]
   z=comp[(comp.cause_name==cause)&(comp.measure_name=='Prevalence')&(comp.year==end)].iloc[0]
   row=dict(cause=cause,end=end,aspr_china=z.asr_china,aspr_reference=z.asr_reference,D=z.rate_difference,RR=z.rate_ratio,change_D=z.rate_difference-a.rate_difference)
   for loc,prefix in [('China','china'),('Other 18 G20 countries','reference')]:
    q=tables[(tables.location_name==loc)&(tables.cause_name==cause)&(tables.measure_name=='Prevalence')&(tables.year<=end)].sort_values('year');fit=segmented_trend(q.year,q.asr)
    row[prefix+'_aapc']=fit['aapc_percent'];row[prefix+'_knots']=str(fit['knots'])
   out.append(row)
   q=b[(b.location_name=='China')&(b.cause_name==cause)&(b.measure_name=='Prevalence')]
   first=q[q.year==1990].set_index('age_name').loc[STUDY['ages']];last=q[q.year==end].set_index('age_name').loc[STUDY['ages']]
   parts,net=shapley(first.population,last.population,first.rate/1e5,last.rate/1e5)
   changes.append(dict(cause=cause,end=end,net_case_change=net,**parts))
 pd.DataFrame(out).to_csv(ROOT/'results/tables/endpoint_sensitivity.csv',index=False)
 pd.DataFrame(changes).to_csv(ROOT/'results/tables/endpoint_decomposition.csv',index=False)
 original=pd.read_csv(ROOT/'data/processed/weights.csv').set_index('age_name').loc[STUDY['ages']].weight.to_numpy()
 vertices=original+np.array(list(product([-.5e-6,.5e-6],repeat=7)));vertices/=vertices.sum(axis=1)[:,None]
 rounded=[]
 for (year,cause,measure),g in gap.groupby(['year','cause_name','measure_name']):
  d=g.set_index('age_name').loc[STUDY['ages']].age_rate_difference.to_numpy();values=vertices@d
  rounded.append(dict(year=year,cause=cause,measure=measure,lower_rounding_bound=values.min(),upper_rounding_bound=values.max(),scope='Deterministic six-decimal weight rounding envelope; not a confidence or uncertainty interval'))
 pd.DataFrame(rounded).to_csv(ROOT/'results/tables/weight_rounding_sensitivity.csv',index=False)
if __name__=='__main__':run()
