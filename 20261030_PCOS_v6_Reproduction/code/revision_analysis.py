#!/usr/bin/env python3
"""Recompute reviewer-requested sensitivities and all revised tables/figures.

Run after PCOS_NewArticle_complete.py and PCOS_NewArticle_complete.R.
Country-age input cells remain local; only aggregate outputs are distributed.
"""
from pathlib import Path
from itertools import product
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/python'
TEX = ROOT / 'manuscript/tables'
FIG = ROOT / 'manuscript/figures'
PCOS = 'Polycystic ovarian syndrome'
CAUSES = [PCOS, 'Endometriosis']
TYPES = ['Total', 'Primary', 'Secondary']
AGES = list(range(15, 50, 5))
YEARS = list(range(1990, 2024))
COLORS = ['#19566c', '#ba572a', '#6b8990']

def signed(x, digits=2):
    return f'{x:+.{digits}f}'

def texrows(name, rows):
    (TEX / f'{name}.tex').write_text(''.join(' & '.join(map(str, r)) + r'\\' + '\n' for r in rows) + r'\bottomrule' + '\n', encoding='utf-8')

def savefig(fig, name):
    fig.savefig(FIG / f'{name}.pdf', bbox_inches='tight')
    fig.savefig(FIG / f'{name}.png', dpi=180, bbox_inches='tight')
    plt.close(fig)

def main(check_r=True):
    for directory in [OUT, TEX, FIG]:
        directory.mkdir(exist_ok=True, parents=True)
    # Every original input is checked, including the separately exported endpoint rates.
    manifest = json.loads((ROOT/'docs/input_manifest.json').read_text())
    for rel, meta in manifest.items():
        p = ROOT / rel
        assert p.stat().st_size == meta['bytes']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == meta['sha256'], rel
    audit = []
    comparisons = [
        ('all_annual_benchmark_aspr', ['cause','subtype','source','year','benchmark']),
        ('symmetric_decomposition_1990_endpoints', ['cause','subtype','source','end']),
        ('leave_one_country_out', ['cause','subtype','source','omitted_country']),
        ('annual_chained_decomposition', ['cause','subtype','source']),
    ]
    for name, keys in (comparisons if check_r else []):
        py = pd.read_csv(OUT/f'{name}.csv').set_index(keys).sort_index()
        rr = pd.read_csv(ROOT/f'results/R/{name}.csv').set_index(keys).sort_index()
        assert py.index.equals(rr.index)
        cols = py.select_dtypes('number').columns
        err = float(np.nanmax(np.abs(py[cols].to_numpy()-rr[cols].to_numpy())))
        assert err < 1e-8
        audit.append(dict(table=name, rows=len(py), max_abs_R_python_difference=err))
    (ROOT/'docs/R_Python_crosscheck.json').write_text(json.dumps(audit, indent=2))
    cells = pd.read_csv(OUT/'rate_cells.csv')
    a = pd.read_csv(OUT/'all_annual_benchmark_aspr.csv')
    d = pd.read_csv(OUT/'symmetric_decomposition_1990_endpoints.csv')
    refs = sorted(set(cells.country)-{'China'})
    idx = pd.MultiIndex.from_product([refs, AGES, YEARS], names=['country','age_start','year'])
    raww = pd.read_csv(ROOT/'data/input/weights.csv').weight.to_numpy()
    w = raww/raww.sum()
    pop = cells.drop_duplicates(['country','age_start','year'])
    pp = pop.set_index(['country','age_start','year']).reindex(idx)
    shares = {}
    for source, col in [('GBD','gbd_pop'), ('UN-WPP2024','un_female_pop')]:
        p = pp[col].to_numpy().reshape(18,7,34)
        shares[source] = p/p.sum(axis=0,keepdims=True)
    sensitivity, age_rows = [], []
    for cause, subtype in product(CAUSES,TYPES):
        z = cells[(cells.cause==cause)&(cells.subtype==subtype)]
        rr = z.set_index(['country','age_start','year']).reindex(idx).gbd_rate.to_numpy().reshape(18,7,34)
        cc = z[z.country=='China'].set_index(['age_start','year']).reindex(pd.MultiIndex.from_product([AGES,YEARS])).gbd_rate.to_numpy().reshape(7,34)
        for source, sh in shares.items():
            scenarios = [('main',sh,w),('ages20_49',sh,np.r_[0,w[1:]/w[1:].sum()])]
            for k, country in enumerate(refs):
                ss = sh.copy(); ss[k]=0; ss/=ss.sum(axis=0,keepdims=True)
                scenarios.append(('omit_'+country,ss,w))
            for scenario, s, ww in scenarios:
                for start,end in product([1990,2010],[2021,2022,2023]):
                    i,j = YEARS.index(start),YEARS.index(end)
                    r0,r1,s0,s1 = rr[:,:,i],rr[:,:,j],s[:,:,i],s[:,:,j]
                    xage = ww*(cc[:,j]-cc[:,i])
                    qage = -ww*(((s0+s1)/2)*(r1-r0)).sum(axis=0)
                    sage = -ww*(((r0+r1)/2)*(s1-s0)).sum(axis=0)
                    initial = float((ww*(cc[:,i]-(s0*r0).sum(axis=0))).sum())
                    last = float((ww*(cc[:,j]-(s1*r1).sum(axis=0))).sum())
                    net = last-initial
                    x,q,sc = xage.sum(),qage.sum(),sage.sum()
                    residual = float(x+q+sc-net)
                    assert abs(residual)<1e-8
                    sensitivity.append(dict(cause=cause,subtype=subtype,source=source,scenario=scenario,start=start,end=end,initial_gap=initial,end_gap=last,net_gap_change=net,china_rate_effect=x,reference_rate_effect=q,reference_country_composition_effect=sc,composition_share_of_net=sc/net if abs(net)>1e-10 else np.nan,identity_residual=residual))
                    if scenario=='main' and start==1990:
                        for k,age in enumerate(AGES):
                            age_rows.append(dict(cause=cause,subtype=subtype,source=source,start=start,end=end,age_start=age,china_rate_effect=xage[k],reference_rate_effect=qage[k],reference_country_composition_effect=sage[k],net_gap_change=xage[k]+qage[k]+sage[k]))
    sens=pd.DataFrame(sensitivity); age=pd.DataFrame(age_rows)
    sens.to_csv(OUT/'composition_sensitivities.csv',index=False)
    age.to_csv(OUT/'age_decomposition.csv',index=False)
    # Verify the full-grid accounting, subtype additivity and agreement with the core run.
    columns=['net_gap_change','china_rate_effect','reference_rate_effect','reference_country_composition_effect']
    for _,z in sens.groupby(['cause','source','scenario','start','end']):
        v=z.set_index('subtype')[columns]
        assert np.max(abs(v.loc['Total']-v.loc['Primary']-v.loc['Secondary']))<1e-8
    mainrows=sens[(sens.scenario=='main')&(sens.start==1990)]
    check=mainrows.merge(d,on=['cause','subtype','source','end'],suffixes=('_new','_core'),validate='1:1')
    assert max(float(abs(check[c+'_new']-check[c+'_core']).max()) for c in columns)<1e-8
    # All 19 national standardized annual trajectories for the terminal-year audit.
    national=cells.assign(weight=cells.age_start.map(dict(zip(AGES,w))))
    national['weighted_rate']=national.gbd_rate*national.weight
    national=national.groupby(['country','cause','subtype','year'],as_index=False).agg(aspr=('weighted_rate','sum'),cases=('gbd_cases','sum'))
    national=national.sort_values(['country','cause','subtype','year'])
    national['yoy_percent']=national.groupby(['country','cause','subtype']).aspr.pct_change()*100
    national.to_csv(OUT/'national_annual_standardized.csv',index=False)
    end=national[national.year==2023].merge(national[national.year.between(1991,2022)].groupby(['country','cause','subtype'],as_index=False).yoy_percent.max().rename(columns={'yoy_percent':'historical_max_yoy'}),on=['country','cause','subtype'])
    end.to_csv(OUT/'terminal_year_audit.csv',index=False)
    ec=cells[(cells.country=='China')&(cells.cause=='Endometriosis')&(cells.subtype!='Total')&(cells.year.isin([2022,2023]))].pivot(index=['age_start','subtype'],columns='year',values='gbd_rate')
    ec['weighted_increment']=(ec[2023]-ec[2022])*ec.index.get_level_values('age_start').map(dict(zip(AGES,w)))
    ec.reset_index().to_csv(OUT/'endometriosis_terminal_age_type.csv',index=False)
    shifts=[]
    for source,s in shares.items():
        for k,country in enumerate(refs):
            shifts.append(dict(source=source,country=country,share1990=(s[k,:,0]*w).sum(),share2023=(s[k,:,-1]*w).sum(),share_change=((s[k,:,-1]-s[k,:,0])*w).sum()))
    shifts=pd.DataFrame(shifts); shifts.to_csv(OUT/'age_weighted_reference_shifts.csv',index=False)
    # Rounding sensitivity uses all 128 corners, never as a confidence interval.
    corners=np.array([raww+np.array(signs)*.5e-6 for signs in product([-1,1],repeat=7)])
    corners=corners/corners.sum(axis=1,keepdims=True)
    roundrows=[]
    for cause,subtype,source in product(CAUSES,TYPES,shares):
        z=cells[(cells.cause==cause)&(cells.subtype==subtype)]
        rr=z.set_index(['country','age_start','year']).reindex(idx).gbd_rate.to_numpy().reshape(18,7,34)
        cc=z[z.country=='China'].set_index(['age_start','year']).reindex(pd.MultiIndex.from_product([AGES,YEARS])).gbd_rate.to_numpy().reshape(7,34)
        s=shares[source]
        g=cc[:,-1]-(s[:,:,-1]*rr[:,:,-1]).sum(axis=0)
        netage=g-(cc[:,0]-(s[:,:,0]*rr[:,:,0]).sum(axis=0))
        sage=-((rr[:,:,0]+rr[:,:,-1])/2*(s[:,:,-1]-s[:,:,0])).sum(axis=0)
        gaps=corners@g; sc=corners@sage; net=corners@netage
        roundrows.append(dict(cause=cause,subtype=subtype,source=source,gap_min=gaps.min(),gap_max=gaps.max(),share_effect_min=sc.min(),share_effect_max=sc.max(),fraction_min=(sc/net).min(),fraction_max=(sc/net).max()))
    rounding=pd.DataFrame(roundrows);rounding.to_csv(OUT/'standard_weight_rounding.csv',index=False)
    # Tables for the manuscript, always generated from this run.
    dyn=a[(a.source=='GBD')&(a.benchmark=='dynamic')]
    texrows('prevalence',[(t,y,f'{r.china_aspr:.2f}',f'{r.ref_aspr:.2f}',signed(r.gap),f'{r.ratio:.3f}') for t in TYPES for y in [1990,2023] for _,r in dyn[(dyn.cause==PCOS)&(dyn.subtype==t)&(dyn.year==y)].iterrows()])
    dd=d[(d.cause==PCOS)&(d.end==2023)]
    texrows('decomposition',[(r.subtype, 'GBD' if r.source=='GBD' else 'UN WPP',signed(r.china_rate_effect),signed(r.reference_rate_effect),signed(r.reference_country_composition_effect),signed(r.net_gap_change)) for t in TYPES for _,r in dd[dd.subtype==t].iterrows()])
    sec=a[(a.cause==PCOS)&(a.subtype=='Secondary')&(a.year==2023)]
    policyrows=[]
    for source in shares:
        for bench,label in [('dynamic','Current-year shares'),('fixed1990','Fixed-1990 shares'),('equal','Equal countries')]:
            r=sec[(sec.source==source)&(sec.benchmark==bench)].iloc[0]
            policyrows.append(('GBD' if source=='GBD' else 'UN WPP',label,f'{r.ref_aspr:.2f}',signed(r.gap)))
    texrows('benchmark',policyrows)
    endpoints=dyn[(dyn.subtype=='Total')&(dyn.year.isin([1990,2021,2022,2023]))]
    texrows('s1_endpoints', [('PCOS' if r.cause==PCOS else 'Endometriosis',r.year,f'{r.china_aspr:.2f}',f'{r.ref_aspr:.2f}',signed(r.gap)) for _,r in endpoints.iterrows()])
    ss=sens[(sens.cause==PCOS)&(sens.subtype=='Total')&(sens.start==1990)&(sens.end==2023)]
    texrows('s2_sensitivity', [('GBD' if r.source=='GBD' else 'UN WPP',r.scenario.replace('omit_','Without ').replace('ages20_49','Ages 20--49').replace('main','Main'),signed(r.net_gap_change),signed(r.reference_country_composition_effect),f'{100*r.composition_share_of_net:.1f}') for _,r in ss.iterrows()])
    az=age[(age.cause==PCOS)&(age.source=='GBD')&(age.end==2023)]
    texrows('s3_age', [(r.subtype,f'{int(r.age_start)}--{int(r.age_start)+4}',signed(r.china_rate_effect),signed(r.reference_rate_effect),signed(r.reference_country_composition_effect),signed(r.net_gap_change)) for _,r in az.iterrows()])
    chain=pd.read_csv(OUT/'annual_chained_decomposition.csv')
    texrows('s4_chained', [('PCOS' if r.cause==PCOS else 'Endometriosis',r.subtype,'GBD' if r.source=='GBD' else 'UN WPP',signed(r.reference_rate_effect),signed(r.reference_country_composition_effect),signed(r.net_gap_change)) for _,r in chain.iterrows()])
    tvd=pd.read_csv(OUT/'population_share_TVD.csv')
    texrows('s5_population', [(f'{age0}--{age0+4}',f'{100*z.total_variation_distance.mean():.3f}',f'{100*z[z.year==2023].total_variation_distance.iloc[0]:.3f}') for age0,z in tvd.groupby('age_start')])
    nz=national[(national.country=='China')&(national.cause=='Endometriosis')&(national.subtype=='Total')&(national.year.isin([1990,2023]))]
    texrows('s6_rate_conventions', [(r.year,f'{r.cases:,.2f}',f'{r.aspr:.3f}',f'{r.aspr*raww.sum():.3f}') for _,r in nz.iterrows()])
    ez=end[(end.cause=='Endometriosis')&(end.subtype=='Total')]
    texrows('s7_terminal', [(r.country,signed(r.yoy_percent),signed(r.historical_max_yoy)) for _,r in ez.iterrows()])
    texrows('s8_rounding', [('PCOS' if r.cause==PCOS else 'Endometriosis',r.subtype,'GBD' if r.source=='GBD' else 'UN WPP',f'{r.gap_min:.5f}',f'{r.gap_max:.5f}') for _,r in rounding.iterrows()])
    figures(a,d,sens,shifts,ez,ec,dyn)
    # Machine-readable values used in the reviewer response and manuscript checks.
    base=ss[ss.source=='GBD']
    core=d[(d.cause==PCOS)&(d.subtype=='Total')&(d.source=='GBD')&(d.end==2023)].iloc[0]
    summary=dict(date='2026-10-29',R_Python_crosscheck=audit,sensitivity_rows=len(sens),max_identity_residual=float(abs(sens.identity_residual).max()),GBD_PCOS_composition_fraction_range=[float(base.composition_share_of_net.min()),float(base.composition_share_of_net.max())],GBD_PCOS_components={c:float(core[c]) for c in columns},figures_main=5,figures_supplement=7,tables_main=3,tables_supplement=8,original_weight_sum=float(raww.sum()),analysis_used_existing_inputs=True,no_joint_draws=True)
    (ROOT/'docs/revision_analysis_qc.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

def figures(a,d,sens,shifts,ez,ec,dyn):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    p=dyn[(dyn.cause==PCOS)&(dyn.subtype=='Total')]
    fig,ax=plt.subplots(1,2,figsize=(10,3.5),layout='constrained')
    ax[0].plot(p.year,p.china_aspr,label='China',color=COLORS[0]);ax[0].plot(p.year,p.ref_aspr,label='18-country reference',color=COLORS[1]);ax[0].legend(frameon=False);ax[0].set(title='A  PCOS-attributed total infertility',ylabel='Standardized rate per 100,000',xlabel='Year')
    ax[1].plot(p.year,p.gap,color=COLORS[0]);ax[1].axhline(0,color='0.6',lw=.7);ax[1].set(title='B  China minus reference',ylabel='Rate difference per 100,000',xlabel='Year');savefig(fig,'Figure1_PCOS_trends')
    fig,ax=plt.subplots(1,2,figsize=(10,3.5),layout='constrained')
    for k,t in enumerate(['Primary','Secondary']):
        z=dyn[(dyn.cause==PCOS)&(dyn.subtype==t)]
        ax[k].plot(z.year,z.china_aspr,color=COLORS[0],label='China');ax[k].plot(z.year,z.ref_aspr,color=COLORS[1],label='18-country reference');ax[k].legend(frameon=False);ax[k].set(title=t+' infertility',xlabel='Year',ylabel='Standardized rate per 100,000')
    savefig(fig,'Figure2_PCOS_subtypes')
    fig,ax=plt.subplots(figsize=(9,4.4),layout='constrained');xx=np.arange(3)
    for k,(c,lab) in enumerate(zip(['china_rate_effect','reference_rate_effect','reference_country_composition_effect'],['China rates (X)','Reference rates (Q)','Reference shares (S)'])):
        z=d[(d.cause==PCOS)&(d.source=='GBD')&(d.end==2023)].set_index('subtype').loc[TYPES]
        bars=ax.bar(xx+(k-1)*.24,z[c],width=.24,color=COLORS[k],label=lab);ax.bar_label(bars,fmt='%+.2f',fontsize=8,padding=3)
    ax.scatter(xx,z.net_gap_change,color='#202c33',marker='D',s=35,label='Net change',zorder=5);ax.axhline(0,color='0.5',lw=.7);ax.set(xticks=xx,xticklabels=TYPES,ylabel='Contribution per 100,000',ylim=(-270,340));ax.legend(ncol=2,frameon=False,loc='upper right',fontsize=9);savefig(fig,'Figure3_decomposition')
    fig,ax=plt.subplots(1,2,figsize=(10,3.8),layout='constrained')
    for k,source in enumerate(['GBD','UN-WPP2024']):
        z=a[(a.cause==PCOS)&(a.subtype=='Total')&(a.source==source)&(a.benchmark=='dynamic')]
        ax[0].plot(z.year,z.gap,label=source,color=COLORS[k],ls=['-','--'][k],lw=2)
        v=d[(d.cause==PCOS)&(d.subtype=='Total')&(d.source==source)&(d.end==2023)].iloc[0]
        ax[1].bar(np.arange(3)+(k-.5)*.32,[v.china_rate_effect,v.reference_rate_effect,v.reference_country_composition_effect],width=.32,label=source,color=COLORS[k])
    ax[0].set(xlabel='Year',ylabel='China minus reference, per 100,000',title='A  Population-source comparison');ax[0].legend(frameon=False)
    ax[1].axhline(0,color='0.5',lw=.7);ax[1].set(xticks=range(3),xticklabels=['China\nrates','Reference\nrates','Reference\nshares'],ylabel='Contribution per 100,000',title='B  Symmetric decomposition');ax[1].legend(frameon=False);savefig(fig,'Figure4_population_source')
    fig,ax=plt.subplots(figsize=(9,4.1),layout='constrained')
    labels=['Current-year population shares','Fixed-1990 population shares','Equal country weights']
    for k,source in enumerate(['GBD','UN-WPP2024']):
        z=a[(a.cause==PCOS)&(a.subtype=='Secondary')&(a.source==source)&(a.year==2023)].set_index('benchmark').loc[['dynamic','fixed1990','equal']]
        bars=ax.barh(np.arange(3)+(k-.5)*.3,z.gap,height=.3,label=source,color=COLORS[k]);ax.bar_label(bars,labels=[signed(x) for x in z.gap],padding=5,fontsize=9)
    ax.axvline(0,color='0.5',lw=.8);ax.set(yticks=range(3),yticklabels=labels,xlim=(-155,40),xlabel='China minus reference, per 100,000');ax.invert_yaxis();ax.legend(frameon=False,loc='lower center',bbox_to_anchor=(0.5,1.01),ncol=2);savefig(fig,'Figure5_benchmark_sensitivity')
    # S1 country exclusions, S2 annual benchmark trajectories, S3 component sensitivity.
    ss=sens[(sens.cause==PCOS)&(sens.subtype=='Total')&(sens.start==1990)&(sens.end==2023)&(sens.source=='GBD')]
    fig,ax=plt.subplots(figsize=(8,6.5),layout='constrained');labs=ss.scenario.str.replace('omit_','Without ',regex=False).replace({'main':'Main','ages20_49':'Ages 20-49'});ax.barh(labs,ss.end_gap,color=COLORS[0]);ax.invert_yaxis();ax.axvline(0,color='0.5',lw=.7);ax.set(xlabel='2023 total PCOS difference per 100,000');savefig(fig,'FigureS1_reference_exclusions')
    fig,ax=plt.subplots(1,2,figsize=(10,3.8),layout='constrained')
    for k,t in enumerate(['Primary','Secondary']):
        for j,(bench,lab) in enumerate([('dynamic','Current-year'),('fixed1990','Fixed 1990'),('equal','Equal countries')]):
            z=a[(a.cause==PCOS)&(a.subtype==t)&(a.source=='UN-WPP2024')&(a.benchmark==bench)]
            ax[k].plot(z.year,z.gap,label=lab,color=COLORS[j])
        ax[k].axhline(0,color='0.5',lw=.7);ax[k].legend(frameon=False,fontsize=8);ax[k].set(title=t+' infertility',xlabel='Year',ylabel='Difference per 100,000')
    savefig(fig,'FigureS2_benchmark_trajectories')
    fig,ax=plt.subplots(figsize=(8,6.5),layout='constrained');ax.barh(labs,ss.composition_share_of_net*100,color=COLORS[2]);ax.axvline(50,color='0.4',ls='--',lw=.7);ax.invert_yaxis();ax.set(xlabel='100 x S / signed net change (%)',xlim=(0,80));savefig(fig,'FigureS3_composition_sensitivity')
    fig,ax=plt.subplots(figsize=(8,3.8),layout='constrained');z=dyn[(dyn.cause=='Endometriosis')&(dyn.subtype=='Total')];ax.plot(z.year,z.gap,color=COLORS[0]);ax.axhline(0,color='0.5',lw=.7);ax.scatter(z[z.year.isin([2021,2022,2023])].year,z[z.year.isin([2021,2022,2023])].gap,color=COLORS[1]);ax.set(xlabel='Year',ylabel='China minus reference per 100,000');savefig(fig,'FigureS4_endometriosis_trajectory')
    fig,ax=plt.subplots(figsize=(8,6),layout='constrained');z=shifts[shifts.source=='UN-WPP2024'].sort_values('share_change');ax.barh(z.country,z.share_change*100,color=COLORS[0]);ax.axvline(0,color='0.5',lw=.7);ax.set(xlabel='Change in age-weighted reference share, percentage points');savefig(fig,'FigureS5_country_shifts')
    fig,ax=plt.subplots(figsize=(8,6),layout='constrained');z=ez.sort_values('yoy_percent');ax.barh(z.country,z.yoy_percent,color=COLORS[1]);ax.axvline(0,color='0.5',lw=.7);ax.set(xlabel='2022-2023 modeled endometriosis rate change (%)');savefig(fig,'FigureS6_terminal_country')
    fig,ax=plt.subplots(figsize=(8,4),layout='constrained')
    for k,t in enumerate(['Primary','Secondary']):
        z=ec.xs(t,level='subtype').reindex(AGES);ax.bar(np.arange(7)+(k-.5)*.35,z.weighted_increment,width=.35,label=t,color=COLORS[k])
    ax.set(xticks=range(7),xticklabels=[f'{x}-{x+4}' for x in AGES],xlabel='Age group',ylabel='Contribution per 100,000');ax.legend(frameon=False);savefig(fig,'FigureS7_terminal_age_type')

if __name__ == '__main__':
    main()
