"""Figures use verified analytical outputs, never test fixtures."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.ticker import MaxNLocator

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/figures';OUT.mkdir(exist_ok=True)
T=ROOT/'results/tables';COL={'China':'#C44E52','Other 18 G20 countries':'#256B8B'}
NAMES={'Endometriosis':'Endometriosis-related infertility','Polycystic ovarian syndrome':'PCOS-related infertility'}
CAUSES=list(NAMES);AGES=['15-19','20-24','25-29','30-34','35-39','40-44','45-49']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','pdf.fonttype':42,'ps.fonttype':42,'axes.labelsize':9,'legend.frameon':False})

def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=320,bbox_inches='tight',facecolor='white')
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',facecolor='white')
    fig.savefig(OUT/(name+'.svg'),bbox_inches='tight',facecolor='white')
    plt.close(fig)

def run():
    d=pd.read_csv(T/'burden_standardized.csv');d=d[d.measure_name=='Prevalence']
    c=pd.read_csv(T/'china_reference_comparison.csv');c=c[c.measure_name=='Prevalence']
    a=pd.read_csv(T/'age_contributions_and_benchmark.csv');a=a[a.measure_name=='Prevalence']
    ac=pd.read_csv(T/'age_contributions_to_gap_change.csv');ac=ac[ac.measure_name=='Prevalence']
    dec=pd.read_csv(T/'case_change_decomposition.csv');dec=dec[dec.start==1990]
    fig,axs=plt.subplots(1,2,figsize=(11,6.4),layout='constrained')
    for ax,cause,panel in zip(axs,CAUSES,['A','B']):
        q=d[(d.year==2023)&(d.cause_name==cause)&(d.location_name!='Other 18 G20 countries')].sort_values('asr')
        y=np.arange(len(q));colors=['#C44E52' if x=='China' else '#54798B' for x in q.location_name]
        ax.hlines(y,0,q.asr,color='#D7E0E4',linewidth=1);ax.scatter(q.asr,y,c=colors,s=34,zorder=3)
        ref=float(c[(c.year==2023)&(c.cause_name==cause)].asr_reference.iloc[0]);ax.axvline(ref,color='#256B8B',ls='--',lw=1,label='Pooled reference excluding China')
        ax.set(yticks=y,yticklabels=q.location_name,xlabel='ASPR per 100,000 women aged 15-49',title=f'{panel}  {NAMES[cause]}')
        ax.grid(axis='x',alpha=.15);ax.legend(loc='lower right',fontsize=7)
    save(fig,'fig1_country_comparison_2023')
    fig,axs=plt.subplots(2,3,figsize=(11.3,6.4),layout='constrained')
    for i,cause in enumerate(CAUSES):
        q=c[c.cause_name==cause].sort_values('year')
        axs[i,0].plot(q.year,q.asr_china,color=COL['China'],lw=2,label='China');axs[i,0].plot(q.year,q.asr_reference,color=COL['Other 18 G20 countries'],lw=2,label='Other 18 G20 countries')
        axs[i,1].plot(q.year,q.rate_difference,color='#514B77',lw=2);axs[i,1].axhline(0,color='#777777',ls='--',lw=.8)
        axs[i,2].plot(q.year,q.rate_ratio,color='#267568',lw=2);axs[i,2].axhline(1,color='#777777',ls='--',lw=.8)
        for j in range(3):
            axs[i,j].set(xlabel='Year',title=f'{chr(65+i*3+j)}  '+(['Restricted-age ASPR','China minus reference','China / reference'][j]));axs[i,j].grid(alpha=.15);axs[i,j].xaxis.set_major_locator(MaxNLocator(5,integer=True))
        axs[i,0].set_ylabel(NAMES[cause]+'\nASPR per 100,000');axs[i,1].set_ylabel('Rate difference per 100,000');axs[i,2].set_ylabel('Rate ratio')
    axs[0,0].legend(fontsize=8);save(fig,'fig2_trends_and_disparities')
    fig,axs=plt.subplots(2,2,figsize=(11.2,6.5),layout='constrained')
    for i,cause in enumerate(CAUSES):
        q=a[a.cause_name==cause];h=q.pivot(index='age_name',columns='year',values='age_rate_difference').reindex(AGES)
        lim=max(np.abs(h.to_numpy()).max(),1e-6);im=axs[i,0].imshow(h,aspect='auto',origin='lower',cmap='RdBu_r',norm=TwoSlopeNorm(vmin=-lim,vcenter=0,vmax=lim),extent=[1989.5,2023.5,-.5,6.5])
        axs[i,0].set(yticks=range(7),yticklabels=AGES,xlabel='Year',ylabel='Age (years)',title=f'{chr(65+i*2)}  {NAMES[cause]}')
        fig.colorbar(im,ax=axs[i,0],label='Age-specific rate difference per 100,000',shrink=.85)
        z=ac[ac.cause_name==cause].set_index('age_name').loc[AGES].change_in_gap_contribution
        axs[i,1].barh(AGES,z,color=['#C44E52' if v>0 else '#256B8B' for v in z]);axs[i,1].axvline(0,color='#777777',lw=.8)
        axs[i,1].set(xlabel='Contribution to D(2023) - D(1990) per 100,000',title=f'{chr(66+i*2)}  Age contributions to gap change');axs[i,1].grid(axis='x',alpha=.15)
    save(fig,'fig3_age_disparities')
    fig,axs=plt.subplots(2,2,figsize=(10.5,6.3),layout='constrained')
    for i,cause in enumerate(CAUSES):
        z=dec[(dec.country=='China')&(dec.cause==cause)].iloc[0]
        vals=z[['population_size','age_composition','age_specific_prevalence']].to_numpy(float)/1000
        axs[i,0].barh(['Female population size','Age composition','Age-specific prevalence'],vals,color=['#54798B','#C6A04D','#A65C69']);axs[i,0].axvline(0,color='#777777',lw=.8)
        axs[i,0].set(xlabel='Contribution to case-count change (thousands)',title=f'{chr(65+i*2)}  {NAMES[cause]}')
        axs[i,0].text(.02,.04,f'Net change: {z.net_case_change/1000:+,.1f} thousand',transform=axs[i,0].transAxes,fontsize=8)
        q=a[(a.year==2023)&(a.cause_name==cause)].set_index('age_name').loc[AGES].benchmark_number_difference/1000
        axs[i,1].barh(AGES,q,color=['#C44E52' if v>0 else '#256B8B' for v in q]);axs[i,1].axvline(0,color='#777777',lw=.8)
        axs[i,1].set(xlabel='Signed benchmark case difference (thousands)',ylabel='Age (years)',title=f'{chr(66+i*2)}  Same Chinese population, 2023')
        for ax in axs[i]:ax.grid(axis='x',alpha=.15)
    save(fig,'fig4_decomposition_and_benchmark')
    s=pd.read_csv(T/'reference_sensitivities.csv');s=s[(s.year==2023)&(s.measure_name=='Prevalence')]
    fig,axs=plt.subplots(1,2,figsize=(11,6.6),layout='constrained')
    for ax,cause in zip(axs,CAUSES):
        z=s[s.cause_name==cause].sort_values('rate_difference');labels=z.sensitivity.str.replace('leave_out_','Exclude ',regex=False).replace({'age20_49':'Ages 20-49','fixed1990_country_weights':'Fixed 1990 country weights'})
        ax.scatter(z.rate_difference,np.arange(len(z)),c='#256B8B',s=30)
        base=float(c[(c.year==2023)&(c.cause_name==cause)].rate_difference.iloc[0]);ax.axvline(base,c='#C44E52',ls='--',label='Main reference');ax.axvline(0,c='#777777',lw=.6)
        ax.set(yticks=np.arange(len(z)),yticklabels=labels,xlabel='China minus reference, per 100,000',title=NAMES[cause]);ax.grid(axis='x',alpha=.15);ax.legend(fontsize=8)
    save(fig,'figS1_reference_sensitivity')
    # Secondary YLD series use identical age standard and comparison definition.
    y=pd.read_csv(T/'china_reference_comparison.csv');y=y[y.measure_name=='YLDs']
    fig,axs=plt.subplots(1,2,figsize=(10,3.6),layout='constrained')
    for ax,cause in zip(axs,CAUSES):
        z=y[y.cause_name==cause].sort_values('year');ax.plot(z.year,z.asr_china,c=COL['China'],label='China');ax.plot(z.year,z.asr_reference,c=COL['Other 18 G20 countries'],label='Other 18 G20 countries');ax.set(xlabel='Year',ylabel='Age-standardized YLD rate per 100,000',title=NAMES[cause]);ax.legend(fontsize=8);ax.grid(alpha=.15)
    save(fig,'figS2_yld_trends')

if __name__=='__main__':run()
