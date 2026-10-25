"""Original-record Python replication of the independent R survey calculation.

Design-based covariance only. This supplies no GBD posterior uncertainty.
Synthetic fixtures are not used to obtain research estimates.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/external'
p=ROOT/'data/external/nsfg/NSFG_2022_2023_FemRespPUFData.csv'
d=pd.read_csv(p,low_memory=False);assert len(d)==5586
w=d.WGT2022_2023.to_numpy(float);assert np.isfinite(w).all() and (w>0).all()
union=d.RMARITAL.isin([1,2]).to_numpy()
broad=(d.FECUND.isin([3,4,5])|d.INFERT.eq(2)).to_numpy()
narrow=d.INFERT.eq(2).to_numpy()
sy=(d.HLPPRG.eq(1)|d.HLPMC.eq(1)).to_numpy()
sk=sy|(d.HLPPRG.eq(5)&d.HLPMC.eq(5)).to_numpy()
rows=[];influences=[]
def add(name,num,den):
 num=np.asarray(num,float);den=np.asarray(den,float);total=w@den
 if total<=0:raise ValueError('Empty domain')
 value=(w@num)/total
 rows.append(dict(estimate_id=name,p=value,n=int(den.sum()),events=int(num.sum())))
 influences.append(w*(num-value*den)/total)
for scope,hi in [('strict_20_49',49),('sampled_20plus',50)]:
 eligible=d.AGER.between(20,hi).to_numpy()
 for dis in ['ENDO','PCOS']:
  valid=d[dis].isin([1,5]).to_numpy();yes=d[dis].eq(1).to_numpy()
  add(f'{scope}_{dis}_diagnosis',eligible&valid&yes,eligible&valid)
  for name,outcome,dom in [('current_problems_all',broad,eligible),('current_problems_union',broad,eligible&union),('infertility12_union',narrow,eligible&union&d.INFERT.isin([1,2,3]).to_numpy()),('ever_services_all',sy,eligible&sk)]:
   for value,label in [(True,'diagnosed'),(False,'not_diagnosed')]:
    mask=dom&valid&(yes==value);add(f'{scope}_{dis}_{name}_{label}',mask&outcome,mask)
U=np.column_stack(influences);z=pd.DataFrame(U);z['_stratum']=d.VEST;z['_psu']=d.VECL
sums=z.groupby(['_stratum','_psu']).sum();V=np.zeros((36,36));df=0
for _,group in sums.groupby(level=0):
 x=group.to_numpy();m=len(x)
 if m<2:raise ValueError('Singleton stratum; no silent adjustment')
 x=x-x.mean(axis=0);V+=m/(m-1)*(x.T@x);df+=m-1
assert df==60 and len(sums)==80
est=pd.DataFrame(rows).set_index('estimate_id');est['se']=np.sqrt(np.maximum(0,np.diag(V)))
r=pd.read_csv(OUT/'Rcheck/independent_R_estimates.csv').set_index('estimate_id').loc[est.index]
rv=pd.read_csv(OUT/'Rcheck/independent_R_joint_covariance.csv',index_col=0).loc[est.index,est.index]
qc={'estimates':36,'design_df':df,'max_abs_estimate_difference':float(abs(est.p-r.p).max()),'max_abs_se_difference':float(abs(est.se-r.se).max()),'max_abs_covariance_difference':float(abs(V-rv.to_numpy()).max()),'passed':bool(np.allclose(est.p,r.p,rtol=1e-10,atol=1e-12) and np.allclose(est.se,r.se,rtol=1e-10,atol=1e-12) and np.allclose(V,rv,rtol=1e-10,atol=1e-12)),'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'GBD_joint_draws_obtained':False}
assert qc['passed'];est.to_csv(OUT/'independent_Python_estimates.csv');pd.DataFrame(V,index=est.index,columns=est.index).to_csv(OUT/'independent_Python_joint_covariance.csv')
(OUT/'independent_R_verification.json').write_text(json.dumps(qc,indent=2))
refs=[]
for dis,pct,se in [('ENDO',6.2,.49),('PCOS',8.7,.51)]:
 row=est.loc[f'strict_20_49_{dis}_diagnosis']
 for quantity,actual,target,places in [('percent',100*row.p,pct,1),('SE_percent',100*row.se,se,2)]:refs.append(dict(id=f'{dis}_diagnosis',quantity=quantity,actual=actual,published=target,match=round(actual,places)==target))
for dis,out,yes,no in [('ENDO','current_problems_all',33.,18.6),('PCOS','current_problems_all',45.2,17.1),('ENDO','ever_services_all',30.7,12.7),('PCOS','ever_services_all',34.5,11.7)]:
 for group,target in [('diagnosed',yes),('not_diagnosed',no)]:
  actual=100*est.loc[f'strict_20_49_{dis}_{out}_{group}','p'];refs.append(dict(id=f'{dis}_{out}_{group}',quantity='percent',actual=actual,published=target,match=round(actual,1)==target))
pd.DataFrame(refs).to_csv(OUT/'cdc_replication_checks.csv',index=False)
assert all(x['match'] for x in refs if 'services' not in x['id'])
(OUT/'nsfg_audit.json').write_text(json.dumps({'raw_rows':len(d),'strict20_49':int(d.AGER.between(20,49).sum()),'sampled20plus':int(d.AGER.between(20,50).sum()),'strata':20,'psus':80,'design_df':60,'core_targets_reproduced':8,'services_all_reproduced':False,'status':'post hoc unadjusted survey triangulation; not held-out GBD validation'},indent=2))
print(json.dumps(qc,indent=2))
