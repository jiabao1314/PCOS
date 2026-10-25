from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'manuscript/tables'
def run():
 d=pd.read_csv(ROOT/'results/tables/table1.csv')
 for measure,name in [('Prevalence','prevalence'),('YLDs','yld')]:
  rows=[]
  for _,r in d[d.measure_name==measure].sort_values(['cause_name','year']).iterrows():
   rows.append(f"{'Endometriosis' if r.cause_name=='Endometriosis' else 'PCOS'} & {r.year} & {r.number_china/1000:,.1f} & {r.number_reference/1000:,.1f} & {r.asr_china:.2f} & {r.asr_reference:.2f} & {r.rate_difference:.2f} & {r.rate_ratio:.3f} \\\\")
  (OUT/f'{name}.tex').write_text('\n'.join(rows)+'\n'+r'\bottomrule'+'\n')
 d=pd.read_csv(ROOT/'results/tables/case_change_decomposition.csv');rows=[]
 for _,r in d[d.country=='China'].iterrows():
  rows.append(f"{'Endometriosis' if r.cause=='Endometriosis' else 'PCOS'} & {r.start}--{r.end} & {r.net_case_change/1000:,.1f} & {r.population_size/1000:,.1f} & {r.age_composition/1000:,.1f} & {r.age_specific_prevalence/1000:,.1f} \\\\")
 (OUT/'decomposition.tex').write_text('\n'.join(rows)+'\n'+r'\bottomrule'+'\n')
 d=pd.read_csv(ROOT/'results/tables/endpoint_sensitivity.csv');rows=[]
 for _,r in d.iterrows():
  rows.append(f"{'Endometriosis' if r.cause=='Endometriosis' else 'PCOS'} & {r.end} & {r.aspr_china:.2f} & {r.aspr_reference:.2f} & {r.D:.2f} & {r.RR:.3f} & {r.change_D:.2f} \\\\")
 (OUT/'endpoint.tex').write_text('\n'.join(rows)+'\n'+r'\bottomrule'+'\n')
 d=pd.read_csv(ROOT/'results/tables/trend_sensitivity_conditional_ci.csv');rows=[]
 for _,r in d[(d.start==1990)&(d.measure=='Prevalence')].iterrows():
  label={'OLS_0_2':'OLS, 0--2 knots','AR1_fixed_selected_knots':'AR(1), fixed knots','OLS_0_3':'OLS, 0--3 knots'}[r.model]
  rows.append(f"{'China' if r.location=='China' else 'Reference'} & {'Endometriosis' if r.cause=='Endometriosis' else 'PCOS'} & {label} & {r.aapc:.2f} & ({r.ci_lower:.2f}, {r.ci_upper:.2f}) \\\\")
 (OUT/'trends.tex').write_text('\n'.join(rows)+'\n'+r'\bottomrule'+'\n')
 d=pd.read_csv(ROOT/'results/tables/forecast_backtest_summary.csv');rows=[]
 for (c,m),g in d[d.model!='naive'].groupby(['cause','model']):
  rolling=g[g.split=='rolling'].mae_ratio;hold=g[g.split=='last10_holdout'].mae_ratio
  rows.append(f"{'Endometriosis' if c=='Endometriosis' else 'PCOS'} & {m} & {rolling.min():.2f}--{rolling.max():.2f} & {hold.min():.2f}--{hold.max():.2f} & No \\\\")
 (OUT/'forecast.tex').write_text('\n'.join(rows)+'\n'+r'\bottomrule'+'\n')
def strata_table():
 d=pd.read_csv(ROOT/'results/tables/strata_comparison.csv');rows=[]
 for _,r in d[(d.year.isin([1990,2023]))&(d.measure_name=='Prevalence')].sort_values(['cause_name','infertility_type','year']).iterrows():
  cause='Endometriosis' if r.cause_name=='Endometriosis' else 'PCOS';typ=r.infertility_type.split()[0]
  rows.append(f"{cause} & {typ} & {r.year} & {r.asr_china:.2f} & {r.asr_reference:.2f} & {r.rate_difference:.2f} & {r.rate_ratio:.3f} "+chr(92)*2)
 (OUT/'strata.tex').write_text('\n'.join(rows)+'\n'+r'\bottomrule'+'\n')
if __name__=='__main__':
 run();strata_table()
