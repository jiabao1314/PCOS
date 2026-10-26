"""Submission figures designed at 170 mm with embedded TrueType fonts."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];T=ROOT/'results/tables';OUT=ROOT/'manuscript/figures'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,'axes.titlesize':9,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'legend.fontsize':7.5,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42,'lines.linewidth':1.2,'axes.linewidth':.6,'legend.frameon':False})
CAUSES=['Endometriosis','Polycystic ovarian syndrome'];COLORS=['#b64863','#377ca2']
def save(fig,name):
 for ext in ['pdf','png']:fig.savefig(OUT/f'{name}.{ext}',dpi=350,bbox_inches='tight',pad_inches=.03)
 plt.close(fig)
def run():
 c=pd.read_csv(T/'china_reference_comparison.csv');c=c[c.measure_name=='Prevalence']
 fig,axes=plt.subplots(2,3,figsize=(170/25.4,5.2),layout='constrained')
 for i,cause in enumerate(CAUSES):
  q=c[c.cause_name==cause].sort_values('year')
  for j,ax in enumerate(axes[i]):
   if j==0:
    ax.plot(q.year,q.asr_china,color=COLORS[0],label='China');ax.plot(q.year,q.asr_reference,color=COLORS[1],label='Reference')
   elif j==1:ax.plot(q.year,q.rate_difference,color='#514b77');ax.axhline(0,c='gray',ls='--',lw=.6)
   else:ax.plot(q.year,q.rate_ratio,color='#267568');ax.axhline(1,c='gray',ls='--',lw=.6)
   ax.set_xticks([1990,2000,2010,2023]);ax.tick_params(axis='x',rotation=35);ax.set_xlabel('Year');ax.grid(alpha=.13)
   ax.set_title(chr(65+3*i+j)+'  '+['Standardized rate','Difference','Ratio'][j],loc='left')
  axes[i,0].set_ylabel(('Endometriosis' if i==0 else 'PCOS')+'\nRate per 100,000');axes[i,1].set_ylabel('China - reference');axes[i,2].set_ylabel('China / reference')
 axes[0,0].legend(loc='best');save(fig,'RH_Figure1')
 s=pd.read_csv(T/'strata_standardized.csv');s=s[s.measure_name=='Prevalence']
 fig,axes=plt.subplots(2,2,figsize=(170/25.4,5.5),layout='constrained')
 for i,cause in enumerate(CAUSES):
  for j,typ in enumerate(['Primary infertility','Secondary infertility']):
   ax=axes[i,j]
   for loc,color,label in zip(['China','Other 18 G20 countries'],COLORS,['China','Reference']):
    q=s[(s.cause_name==cause)&(s.infertility_type==typ)&(s.location_name==loc)].sort_values('year');ax.plot(q.year,q.asr,color=color,label=label)
   ax.set_title(chr(65+2*i+j)+'  '+('Endometriosis' if i==0 else 'PCOS')+' - '+typ.split()[0].lower(),loc='left')
   ax.set_xlabel('Year');ax.set_ylabel('Rate per 100,000');ax.set_xticks([1990,2000,2010,2023]);ax.grid(alpha=.13)
 axes[0,0].legend();save(fig,'RH_Figure2')
 s=pd.read_csv(T/'reference_composition_decomposition.csv');s=s[(s.variant=='main')&(s.start==1990)&(s.end==2023)]
 fig,axes=plt.subplots(1,2,figsize=(170/25.4,3.5),layout='constrained')
 for ax,cause,letter in zip(axes,CAUSES,['A','B']):
  q=s[s.cause==cause].set_index('type').loc[['Primary infertility','Secondary infertility','Total']]
  pos=np.zeros(3);neg=np.zeros(3)
  for label,col,color in zip(['China rates','Reference rates','Reference country shares'],['china_rate_component','reference_rate_component','reference_composition_component'],['#b64863','#377ca2','#c3902f']):
   vals=q[col].to_numpy();base=np.where(vals>=0,pos,neg);ax.barh(range(3),vals,left=base,color=color,label=label,height=.62);pos+=np.maximum(vals,0);neg+=np.minimum(vals,0)
  ax.scatter(q.change_D,range(3),c='#161e2c',s=22,marker='D',label='Net change',zorder=3);ax.set_yticks(range(3),['Primary','Secondary','Total']);ax.invert_yaxis();ax.axvline(0,c='gray',lw=.6)
  ax.set_title(letter+'  '+('Endometriosis' if cause==CAUSES[0] else 'PCOS'),loc='left');ax.set_xlabel('Contribution to difference change\n(per 100,000), 1990-2023')
 handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=2);save(fig,'RH_Figure3')
if __name__=='__main__':run()
