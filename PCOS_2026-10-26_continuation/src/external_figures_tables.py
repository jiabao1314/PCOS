"""Journal figure and tables for the independent NSFG survey arm."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def run():
 d=pd.read_csv(ROOT/'results/tables/nsfg_external_estimates.csv')
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,'axes.titlesize':9,'xtick.labelsize':7.5,'ytick.labelsize':8,'legend.fontsize':7.5,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42,'lines.linewidth':1.1,'axes.linewidth':.6,'legend.frameon':False})
 fig,axes=plt.subplots(1,2,figsize=(170/25.4,3.7),layout='constrained')
 causes=['Endometriosis','Polycystic ovarian syndrome'];labels=['Endometriosis','PCOS']
 for i,cause in enumerate(causes):
  for metric,offset,color,mark,label in [('current_problem_if_diagnosed',-.10,'#b64863','o','Ever diagnosed'),('current_problem_if_not_diagnosed',.10,'#377ca2','s','Not diagnosed')]:
   r=d[(d.cause==cause)&(d.metric==metric)].iloc[0];axes[0].errorbar(r.estimate_percent,i+offset,xerr=[[r.estimate_percent-r.lower_percent],[r.upper_percent-r.estimate_percent]],fmt=mark,color=color,capsize=2,label=label if i==0 else None)
  for metric,offset,color,mark,label in [('cooccurring_diagnosis_and_problem',-.18,'#161e2c','D','All birth histories'),('cooccurrence_no_prior_live_birth',0,'#b64863','o','No prior live birth'),('cooccurrence_at_least_one_live_birth',.18,'#377ca2','s','At least one live birth')]:
   r=d[(d.cause==cause)&(d.metric==metric)&(d.standard=='GBD_weights_20_49')].iloc[0];axes[1].errorbar(r.estimate_percent,i+offset,xerr=[[r.estimate_percent-r.lower_percent],[r.upper_percent-r.estimate_percent]],fmt=mark,color=color,capsize=2,label=label if i==0 else None)
 for ax in axes:
  ax.set_yticks(range(2),labels);ax.invert_yaxis();ax.set_ylim(1.6,-.7);ax.grid(axis='x',alpha=.15)
 axes[0].set_title('A  Problems by diagnosis',loc='left');axes[0].set_xlabel('Current fertility problems (%)\nWithin each diagnosis group');axes[0].set_xlim(0,60)
 axes[1].set_title('B  Population co-occurrence',loc='left');axes[1].set_xlabel('Diagnosis and current problems (%)\nAge-standardized, all women aged 20-49');axes[1].set_xlim(0,5.2)
 axes[0].legend(loc='upper left',bbox_to_anchor=(0,-.28));axes[1].legend(loc='upper left',bbox_to_anchor=(0,-.28))
 for ext in ['pdf','png']:fig.savefig(ROOT/f'manuscript/figures/RH_Figure4.{ext}',dpi=350,bbox_inches='tight',pad_inches=.03)
 rows=[]
 for cause in causes:
  for metric,label in [('cooccurring_diagnosis_and_problem','Total co-occurrence'),('cooccurrence_no_prior_live_birth','No prior live birth'),('cooccurrence_at_least_one_live_birth','At least one live birth')]:
   r=d[(d.cause==cause)&(d.metric==metric)&(d.standard=='GBD_weights_20_49')].iloc[0]
   rows.append(f"{'PCOS' if cause.startswith('Poly') else cause} & {label} & {r.n_events:d} & {r.estimate_percent:.2f} & ({r.lower_percent:.2f}, {r.upper_percent:.2f}) "+chr(92)*2)
 (ROOT/'manuscript/tables/nsfg_external.tex').write_text('\n'.join(rows)+'\n'+r'\bottomrule'+'\n')
 # Extended survey estimates, with explicit standard/denominator distinctions.
 rows=[]
 for _,r in d.iterrows():
  label={'ever_diagnosed':'Ever diagnosed','current_problem_if_diagnosed':'Problems, diagnosed','current_problem_if_not_diagnosed':'Problems, not diagnosed','cooccurring_diagnosis_and_problem':'Co-occurrence','cooccurrence_no_prior_live_birth':'Co-occurrence, no birth','cooccurrence_at_least_one_live_birth':'Co-occurrence, 1+ births'}[r.metric]
  rows.append(f"{'PCOS' if r.cause.startswith('Poly') else 'Endometriosis'} & {label} & {'Crude' if r.standard=='survey_weighted_crude' else 'Std.'} & {r.n_denominator:d} & {r.estimate_percent:.2f} & {r.se_percent:.2f} & ({r.lower_percent:.2f}, {r.upper_percent:.2f}) "+chr(92)*2)
 (ROOT/'manuscript/tables/nsfg_extended.tex').write_text('\n'.join(rows)+'\n'+r'\bottomrule'+'\n')
 qc=json.loads((ROOT/'docs/external_validation_qc.json').read_text());r=pd.read_csv(ROOT/'results/tables/nsfg_R_crosscheck.csv');qc['independent_R_validation']={'rows':len(r),'survey_package':'4.5','max_point_discrepancy_percent':float(r.absolute_point_difference.max()),'max_se_discrepancy_percent':float(r.absolute_se_difference.max()),'additional_narrow_definition_rows':len(pd.read_csv(ROOT/'results/tables/nsfg_R_definition_crosscheck.csv'))};(ROOT/'docs/external_validation_qc.json').write_text(json.dumps(qc,indent=2))
if __name__=='__main__':run()
