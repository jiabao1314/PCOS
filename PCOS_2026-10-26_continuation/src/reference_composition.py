"""Post hoc exact rate/reference-composition decomposition; GBD point estimates.

Symmetric two-factor product identity within each reference country and age.
This decomposes a descriptive contrast, not causes of infertility.
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyze import ROOT, STUDY
from analyze_strata import normalize


def run():
    d=normalize(next((ROOT/'data/raw/strata_annual').glob('*.csv')))
    p=pd.read_csv(ROOT/'data/processed/population.csv')
    w=pd.read_csv(ROOT/'data/processed/weights.csv').set_index('age_name').weight
    w=w/w.sum()
    d=d[d.measure_name=='Prevalence'].merge(p[['location_id','year','age_group_id','population']],on=['location_id','year','age_group_id'],validate='many_to_one')
    d['rate']=d.val/d.population*1e5
    total=d.groupby(['location_name','year','age_name','cause_name'],as_index=False).agg(rate=('rate','sum'),population=('population','first'))
    total['infertility_type']='Total'
    d=pd.concat([d,total],ignore_index=True)
    out=[];cells=[];contrast=[]
    variants=[('main',None,STUDY['ages']),('age20_49',None,STUDY['ages'][1:])]+[(f'leave_out_{c}',c,STUDY['ages']) for c in STUDY['countries'] if c!='China']
    for variant,exclude,ages in variants:
      weights=w.loc[ages]/w.loc[ages].sum()
      for (cause,typ),g in d[d.age_name.isin(ages)&(d.location_name!=exclude)].groupby(['cause_name','infertility_type']):
        ref=g[g.location_name!='China'].copy()
        ref['share']=ref.population/ref.groupby(['year','age_name']).population.transform('sum')
        cn=g[g.location_name=='China'].set_index(['year','age_name']).rate
        for start in [1990,2010]:
          for end in [2021,2022,2023]:
            q=ref[ref.year==start].set_index(['location_name','age_name'])[['rate','share']].join(ref[ref.year==end].set_index(['location_name','age_name'])[['rate','share']],lsuffix='_0',rsuffix='_1',validate='one_to_one')
            q['w']=q.index.get_level_values('age_name').map(weights)
            q['reference_rate_component']=-q.w*(q.share_0+q.share_1)/2*(q.rate_1-q.rate_0)
            q['reference_composition_component']=-q.w*(q.rate_0+q.rate_1)/2*(q.share_1-q.share_0)
            china=float(((cn.loc[end]-cn.loc[start])*weights).sum())
            D={t:float((cn.loc[t]*weights).sum()-(ref[ref.year==t].assign(z=lambda x:x.rate*x.share*x.age_name.map(weights))).z.sum()) for t in [start,end]}
            rate=float(q.reference_rate_component.sum());comp=float(q.reference_composition_component.sum())
            assert np.isclose(china+rate+comp,D[end]-D[start],atol=1e-8)
            row=dict(variant=variant,cause=cause,type=typ,start=start,end=end,D_start=D[start],D_end=D[end],change_D=D[end]-D[start],china_rate_component=china,reference_rate_component=rate,reference_composition_component=comp)
            out.append(row)
            if variant=='main':
              for age in ages:
                qa=q.xs(age,level='age_name')
                cells.append({**{k:row[k] for k in ['cause','type','start','end']},'age':age,'china_rate_component':float((cn.loc[end,age]-cn.loc[start,age])*weights[age]),'reference_rate_component':float(qa.reference_rate_component.sum()),'reference_composition_component':float(qa.reference_composition_component.sum()),'change_D':float(weights[age]*(cn.loc[end,age]-cn.loc[start,age]) + qa.reference_rate_component.sum()+qa.reference_composition_component.sum())})
    out=pd.DataFrame(out);cells=pd.DataFrame(cells)
    # Independently check new estimates against the previous comparison pipeline.
    old=pd.read_csv(ROOT/'results/tables/strata_comparison.csv');old=old[old.measure_name=='Prevalence']
    new=out[(out.variant=='main')&(out.start==1990)&(out.type!='Total')]
    chk=new.merge(old,left_on=['cause','type','end'],right_on=['cause_name','infertility_type','year'],validate='one_to_one')
    assert np.allclose(chk.D_end,chk.rate_difference,atol=1e-8)
    # Additivity over infertility type, each component and sensitivity variant.
    keys=['variant','cause','start','end'];cols=['D_start','D_end','change_D','china_rate_component','reference_rate_component','reference_composition_component']
    sums=out[out.type!='Total'].groupby(keys)[cols].sum().sort_index()
    totals=out[out.type=='Total'].set_index(keys)[cols].sort_index()
    assert np.allclose(sums,totals,atol=1e-8)
    shares=out.pivot(index=keys,columns='type',values='change_D')
    shares['secondary_share_percent']=100*shares['Secondary infertility']/shares.Total
    shares['share_interpretation']=np.where(abs(shares.Total)<1,'small signed denominator; prefer absolute components','signed accounting share; not causal')
    out.to_csv(ROOT/'results/tables/reference_composition_decomposition.csv',index=False)
    cells.to_csv(ROOT/'results/tables/reference_composition_age_type.csv',index=False)
    # Fixed-1990 shares are a distinct path-based sensitivity, not the symmetric S.
    fixed=pd.read_csv(ROOT/'results/tables/strata_reference_sensitivities.csv')
    fixed=fixed[(fixed.sensitivity=='fixed1990_country_weights')&(fixed.measure_name=='Prevalence')]
    fixed_rows=[]
    for cause,z in fixed.groupby('cause_name'):
      q=z.pivot(index='year',columns='infertility_type',values='rate_difference')
      for start in [1990,2010]:
        for end in [2021,2022,2023]:
          v=q.loc[end]-q.loc[start];net=float(v.sum())
          fixed_rows.append(dict(variant='fixed1990_country_weights',cause=cause,start=start,end=end,**v.to_dict(),Total=net,secondary_share_percent=100*v['Secondary infertility']/net,share_interpretation='signed accounting share; not causal'))
    pd.concat([shares.reset_index(),pd.DataFrame(fixed_rows)],ignore_index=True).to_csv(ROOT/'results/tables/subtype_change_robustness.csv',index=False)
    main=out[(out.variant=='main')&(out.start==1990)&(out.end==2023)]
    table=[]
    for _,r in main.iterrows():
      cause='PCOS' if r.cause.startswith('Poly') else 'Endometriosis'
      typ=r.type.replace(' infertility','').replace('Total','Total')
      table.append(f"{cause} & {typ} & {r.change_D:+.2f} & {r.china_rate_component:+.2f} & {r.reference_rate_component:+.2f} & {r.reference_composition_component:+.2f} \\\\")
    (ROOT/'manuscript/tables/reference_composition.tex').write_text('\n'.join(table)+'\n'+r'\bottomrule'+'\n')
    fig,axs=plt.subplots(1,2,figsize=(10.5,4.5),layout='constrained')
    for ax,cause in zip(axs,STUDY['causes']):
      q=main[main.cause==cause].set_index('type').loc[['Primary infertility','Secondary infertility','Total']]
      names=['China rates','Reference rates','Reference country shares'];columns=['china_rate_component','reference_rate_component','reference_composition_component']
      pos=np.zeros(3);neg=np.zeros(3)
      for label,col,color in zip(names,columns,['#b64863','#377ca2','#c3902f']):
        vals=q[col].to_numpy();base=np.where(vals>=0,pos,neg)
        ax.barh(np.arange(3),vals,left=base,label=label,color=color,height=.62)
        pos+=np.maximum(vals,0);neg+=np.minimum(vals,0)
      ax.scatter(q.change_D,np.arange(3),color='#161e2c',marker='D',s=30,label='Net change',zorder=3)
      ax.set_yticks(np.arange(3),['Primary','Secondary','Total']);ax.invert_yaxis();ax.axvline(0,color='gray',lw=.7)
      ax.set_title('PCOS' if cause.startswith('Poly') else cause)
      ax.set_xlabel('Contribution to change in China minus reference\n(per 100,000 females), 1990-2023');ax.spines[['top','right']].set_visible(False)
    axs[0].legend(frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(0,-.25),ncol=2)
    for ext in ['pdf','png','svg']:fig.savefig(ROOT/f'results/figures/fig5_reference_composition.{ext}',dpi=300,bbox_inches='tight')
    report={'rows':len(out),'age_type_rows':len(cells),'checks':['symmetric identity equals independent endpoint difference','primary + secondary = total for all components','previous pipeline endpoint agreement'],'analysis_status':'post hoc after review; not preregistered','derived_uncertainty':'none; point estimates only'}
    (ROOT/'docs/reference_composition_qc.json').write_text(json.dumps(report,indent=2))
    print(main.to_string(index=False))
    print(shares.loc[('main',slice(None),1990,slice(None)),:].to_string())

if __name__=='__main__':run()
