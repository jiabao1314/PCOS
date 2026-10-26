"""External NSFG triangulation with Taylor survey variances (not GBD validation).

Public survey weights, all 20 strata and 80 nested PSUs retained in domain
estimation. Direct standardization sums respondent linearized influences before
variance computation, retaining covariance across age groups. No invented draws.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from scipy.special import expit,logit
from scipy.stats import t
from analyze_strata import normalize
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw/nsfg_2022_2023/NSFG_2022_2023_FemRespPUFData.csv'

class Survey:
 def __init__(self,d):
  self.d=d;self.w=d.WGT2022_2023.to_numpy(float)
  self.index=pd.MultiIndex.from_frame(d[['VEST','VECL']]);self.psus=self.index.unique();self.df=len(self.psus)-d.VEST.nunique()
  assert len(d)==5586 and len(self.psus)==80 and self.df==60 and np.isfinite(self.w).all() and (self.w>0).all()
 def variance(self,u):
  s=pd.Series(np.asarray(u,float),index=self.index).groupby(level=[0,1]).sum();v=0
  for _,g in s.groupby(level=0):
   n=len(g);assert n==4;v+=n/(n-1)*np.sum((g-g.mean())**2)
  return float(v)
 def ratio(self,y,domain):
  y=np.asarray(y,float);domain=np.asarray(domain,bool);assert np.isfinite(y[domain]).all()
  den=float(self.w[domain].sum());assert den>0
  yy=np.where(domain,y,0);p=float((self.w*yy).sum()/den)
  u=self.w*np.where(domain,y-p,0)/den
  return p,u
 def standardized(self,y,domain,ages,weights):
  val=0;u=np.zeros(len(self.d))
  for age,wa in weights.items():
   p,z=self.ratio(y,np.asarray(domain)&(ages==age));val+=wa*p;u+=wa*z
  return float(val),u
 def record(self,cause,metric,standard,p,u,domain,y):
  se=np.sqrt(self.variance(u));q=t.ppf(.975,self.df)
  if 0<p<1:
   lo,hi=expit(logit(p)+np.array([-1,1])*q*se/(p*(1-p)))
  else:lo=hi=np.nan
  n=int(np.asarray(domain).sum());events=int(np.asarray(y)[np.asarray(domain)].sum())
  return dict(cause=cause,metric=metric,standard=standard,estimate_percent=p*100,se_percent=se*100,lower_percent=lo*100,upper_percent=hi*100,n_denominator=n,n_events=events,design_df=self.df,interval='Taylor variance; logit-t 95% CI; no GBD uncertainty',small_event_caution=events<30)

def run():
 d=pd.read_csv(RAW,low_memory=False).rename(columns={'CaseID':'CASEID'})
 assert d.CASEID.nunique()==len(d)
 # Check public-codebook frequencies before constructing any analytical variables.
 expected={'FECUND':{1:737,2:189,3:346,4:608,5:42,6:3664},'ENDO':{1:294,5:5245,8:38,9:8},'PCOS':{1:441,5:5086,8:42,9:16}}
 for c,counts in expected.items():assert d[c].value_counts().sort_index().to_dict()==counts
 s=Survey(d);eligible=d.AGER.between(20,49).to_numpy();assert eligible.sum()==4855
 problem=(d.FECUND.isin([3,4,5])|d.INFERT.eq(2)).to_numpy(float)
 no_birth=d.PARITY.eq(0).to_numpy()
 age5=(d.AGER//5*5).astype(str)+'-'+(d.AGER//5*5+4).astype(str)
 w=pd.read_csv(ROOT/'data/processed/weights.csv').set_index('age_name').weight.iloc[1:];w=w/w.sum()
 rows=[];checks=[];birthshares=[];agechecks=[];sens=[]
 # Inputs to independent R/survey validation contain only non-identifying derived variables.
 # They are temporary and are not published at respondent level.
 validation=d[['VEST','VECL','WGT2022_2023','AGER','PARITY','CONSTAT1','FECUND','INFERT','ENDO','PCOS']].copy()
 validation.to_csv(ROOT/'tmp/nsfg_validator_inputs.csv',index=False)
 for c,cause in [('ENDO','Endometriosis'),('PCOS','Polycystic ovarian syndrome')]:
  valid=eligible & d[c].isin([1,5]).to_numpy();diagnosed=d[c].eq(1).to_numpy(float);joint=diagnosed*problem
  metrics=[('ever_diagnosed',diagnosed,valid),('current_problem_if_diagnosed',problem,valid & (diagnosed==1)),('current_problem_if_not_diagnosed',problem,valid & (diagnosed==0)),('cooccurring_diagnosis_and_problem',joint,valid),('cooccurrence_no_prior_live_birth',joint*no_birth,valid),('cooccurrence_at_least_one_live_birth',joint*(~no_birth),valid)]
  vals={}
  for metric,y,domain in metrics:
   for standard in ['survey_weighted_crude','GBD_weights_20_49']:
    if standard=='GBD_weights_20_49' and metric.startswith('current_problem_if_'):continue
    p,u=s.ratio(y,domain) if standard=='survey_weighted_crude' else s.standardized(y,domain,age5,w.to_dict())
    row=s.record(cause,metric,standard,p,u,domain,y);rows.append(row);vals[(metric,standard)]=(p,u)
  # Birth-history accounting is performed on co-occurrence out of all women, not
  # on a conditional infertility denominator or as GBD primary/secondary labels.
  for standard in ['survey_weighted_crude','GBD_weights_20_49']:
   total,u=vals[('cooccurring_diagnosis_and_problem',standard)];none,un=vals[('cooccurrence_no_prior_live_birth',standard)];one,uo=vals[('cooccurrence_at_least_one_live_birth',standard)]
   assert np.isclose(none+one,total,atol=1e-12) and np.allclose(un+uo,u,atol=1e-12)
   share=none/total;us=(un-share*u)/total
   birthshares.append(s.record(cause,'no_prior_live_birth_share_of_cooccurrence',standard,share,us,valid & (joint==1),no_birth.astype(float)))
  for metric,expectedval in [('ever_diagnosed',6.2 if c=='ENDO' else 8.7),('current_problem_if_diagnosed',33.0 if c=='ENDO' else 45.2),('current_problem_if_not_diagnosed',18.6 if c=='ENDO' else 17.1)]:
   actual=vals[(metric,'survey_weighted_crude')][0]*100;assert abs(actual-expectedval)<.05
   checks.append(dict(cause=cause,metric=metric,cdc_published_percent=expectedval,reproduced_percent=actual,rounded_match=True))
  # Reproduce the official diagnosis SEs to their two decimal places.
  se=np.sqrt(s.variance(vals[('ever_diagnosed','survey_weighted_crude')][1]))*100
  assert abs(se-(.49 if c=='ENDO' else .51))<.005
  for a in w.index:
   domain=valid&(age5==a);p,u=s.ratio(joint,domain)
   agechecks.append(s.record(cause,'cooccurring_diagnosis_and_problem',a,p,u,domain,joint))
  # Definition sensitivity: 12-month infertility only in the survey's
  # married/cohabiting universe; denominators differ from the main survey arm.
  for state in [1,5]:
   domain=valid & d.RMARITAL.isin([1,2]).to_numpy() & d[c].eq(state).to_numpy()
   y=d.INFERT.eq(2).to_numpy(float);pp,uu=s.ratio(y,domain)
   sens.append(s.record(cause,'12month_infertility_in_union_'+('diagnosed' if state==1 else 'not_diagnosed'),'survey_weighted_crude',pp,uu,domain,y))
  # Weighted classification bounds for missing diagnosis responses. These are
  # deterministic point-estimate sensitivity limits, not confidence intervals.
  missing=~d[c].isin([1,5]).to_numpy()
  for label,yy in [('lower',joint),('upper',np.maximum(diagnosed,missing)*problem)]:
   pp,_=s.standardized(yy,eligible,age5,w.to_dict())
   sens.append(dict(cause=cause,metric='missing_diagnosis_cooccurrence_'+label,standard='GBD_weights_20_49',estimate_percent=100*pp,interval='classification sensitivity point limit, not CI'))
 pd.DataFrame(rows).to_csv(ROOT/'results/tables/nsfg_external_estimates.csv',index=False)
 pd.DataFrame(birthshares).to_csv(ROOT/'results/tables/nsfg_birth_history_shares.csv',index=False)
 pd.DataFrame(checks).to_csv(ROOT/'results/tables/nsfg_cdc_replication.csv',index=False)
 # Small age-cell event counts are an analytical diagnostic, not plotted as
 # reliable independent age estimates.
 pd.DataFrame(agechecks).to_csv(ROOT/'results/tables/nsfg_age_cell_diagnostics.csv',index=False)
 pd.DataFrame(sens).to_csv(ROOT/'results/tables/nsfg_definition_missingness_sensitivity.csv',index=False)
 # Matched age range for descriptive model comparison; no calibration ratio.
 b=normalize(next((ROOT/'data/raw/strata_annual').glob('*.csv')))
 p=pd.read_csv(ROOT/'data/processed/population.csv');b=b[(b.location_name=='United States of America')&(b.year==2022)&(b.measure_name=='Prevalence')&(b.age_name.isin(w.index))].merge(p[['location_id','year','age_group_id','population']],on=['location_id','year','age_group_id'],validate='many_to_one')
 b['weighted_rate']=b.val/b.population*1e5*b.age_name.map(w)
 gb=b.groupby(['cause_name','infertility_type']).weighted_rate.sum().reset_index(name='restricted_age_rate_per_100000');gb['year']=2022;gb['location']='United States of America';gb['propagated_ui']='unavailable'
 gb.to_csv(ROOT/'results/tables/gbd_us_2022_age20_49_comparator.csv',index=False)
 Path(ROOT/'docs/external_validation_qc.json').write_text(json.dumps({'raw_rows':len(d),'raw_columns':len(d.columns),'age_20_49_respondents':int(eligible.sum()),'published_report_eligible_n':4856,'eligible_n_explanation':'One respondent was 49 at screening and 50 at interview; strict 20-49 excludes her. Her disease questions are inapplicable, so known-diagnosis domains are unaffected.','strata':20,'nested_psus':80,'design_df':s.df,'source_codebook_frequencies_match':True,'cdc_six_point_estimates_rounded_match':True,'cdc_two_diagnosis_ses_rounded_match':True,'population_birth_history_components_add':True,'independent_R_validation':'pending','interpretation':'External observational triangulation; not validation of GBD etiologic attribution, China-G20 contrasts, trend or joint uncertainty','nonresponse':'Female response rate 23.4%; survey mode and ascertainment may bias estimates','input_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest()},indent=2))
 print(pd.DataFrame(rows).to_string(index=False));print(pd.DataFrame(birthshares).to_string(index=False));print(gb.to_string(index=False))
if __name__=='__main__':run()
