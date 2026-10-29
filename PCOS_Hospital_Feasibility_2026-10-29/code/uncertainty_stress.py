#!/usr/bin/env python3
"""Non-probabilistic stress test using original marginal GBD rate limits.

This is NOT posterior propagation, a simultaneous 95% interval, or an identified
set containing the truth with known coverage. It explores a Cartesian box of
published marginal limits, conditional on fixed demographic shares/age weights.
Cross-cell dependence and joint subtype constraints are not recovered.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',required=True);ap.add_argument('--output-dir',required=True);args=ap.parse_args()
    ip=Path(args.input_dir);op=Path(args.output_dir);op.mkdir(exist_ok=True,parents=True)
    total=pd.read_csv(ip/'IHME-GBD_2023_DATA-1b13e337-1.csv')
    sub=pd.read_csv(ip/'IHME-GBD_2023_DATA-76c5523c-1.csv')
    pop=pd.read_csv(ip/'IHME-GBD_2023_DATA-916826fb-1.csv')
    un=pd.read_csv(ip/'UN_WPP2024_G20_female_15_49_1990_2023.csv')
    w=pd.read_csv(ip/'weights.csv').weight.to_numpy();w=w/w.sum()
    x=total.query('cause_id==605 and rei_id==198 and sex_id==2 and measure_id==5 and metric_id==3 and year in [1990,2023]').copy();x['subtype']='Total'
    y=sub.query('cause_id==605 and rei_id in [220,221] and sex_id==2 and measure_id==5 and metric_id==3').copy();y['subtype']=y.rei_id.map({220:'Primary',221:'Secondary'})
    raw=pd.concat([x,y]);raw['age_start']=(raw.age_id-5)*5
    assert len(raw)==798
    countries=['China']+sorted(set(raw.location_name)-{'China'});ages=list(range(15,50,5));years=[1990,2023]
    idx=pd.MultiIndex.from_product([years,countries,ages],names=['year','country','age_start'])
    pop=pop.rename(columns={'location_name':'country','val':'gbd_pop'});pop['age_start']=(pop.age_id-5)*5
    pop=pop.merge(un.rename(columns={'gbd_country':'country'})[['year','country','age_start','un_female_pop']],on=['year','country','age_start'],validate='1:1')
    out=[];tipping=[]
    for source,col in [('GBD','gbd_pop'),('UN-WPP2024','un_female_pop')]:
        p=pop.set_index(['year','country','age_start']).reindex(idx)[col].to_numpy().reshape(2,19,7)
        shares=p[:,1:,:]/p[:,1:,:].sum(axis=1,keepdims=True)
        for typ in ['Total','Primary','Secondary']:
            z=raw[raw.subtype==typ].rename(columns={'location_name':'country'}).set_index(['year','country','age_start']).reindex(idx)
            vals={k:z[k].to_numpy().reshape(2,19,7) for k in ['val','lower','upper']}
            assert all(np.isfinite(v).all() for v in vals.values())
            assert np.all(vals['lower']<=vals['val']) and np.all(vals['val']<=vals['upper'])
            coeff={k:np.zeros((2,19,7)) for k in ['D1990','D2023','X','Q','S']}
            for t,key in [(0,'D1990'),(1,'D2023')]:
                coeff[key][t,0,:]=w;coeff[key][t,1:,:]=-shares[t]*w
            coeff['X'][1,0,:]=w;coeff['X'][0,0,:]=-w
            avg=(shares[0]+shares[1])/2;diff=shares[1]-shares[0]
            coeff['Q'][0,1:,:]=avg*w;coeff['Q'][1,1:,:]=-avg*w
            coeff['S'][:,1:,:]=-diff*w/2
            coeff['Net_change']=coeff['D2023']-coeff['D1990']
            assert np.max(abs(coeff['X']+coeff['Q']+coeff['S']-coeff['Net_change']))<1e-12
            for key,c in coeff.items():
                point=float((c*vals['val']).sum())
                low=float(np.where(c>=0,c*vals['lower'],c*vals['upper']).sum())
                high=float(np.where(c>=0,c*vals['upper'],c*vals['lower']).sum())
                assert low-1e-8<=point<=high+1e-8
                out.append(dict(source=source,subtype=typ,target=key,point_estimate=point,marginal_limit_box_min=low,marginal_limit_box_max=high,box_crosses_zero=bool(low<=0<=high),not_a_confidence_interval=True))
            ar=float((w*(shares[1]*vals['val'][1,1:,:]).sum(axis=0)).sum());cr=float((w*vals['val'][1,0,:]).sum());gap=cr-ar
            tipping.append(dict(source=source,subtype=typ,china_2023=cr,reference_2023=ar,gap_2023=gap,reference_uniform_relative_change_to_zero=gap/ar,china_uniform_relative_change_to_zero=-gap/cr,not_probability=True))
    result=pd.DataFrame(out);result.to_csv(op/'GBD_marginal_limit_stress.csv',index=False)
    pd.DataFrame(tipping).to_csv(op/'GBD_reference_tipping_points.csv',index=False)
    # Cross-check against previously independently reproduced core estimates.
    expected=pd.read_csv(ip.parent.parent/'results/python/symmetric_decomposition_1990_endpoints.csv')
    for source in ['GBD','UN-WPP2024']:
        e=expected[(expected.cause=='Polycystic ovarian syndrome')&(expected.subtype=='Total')&(expected.source==source)&(expected.end==2023)].iloc[0]
        s=result[(result.source==source)&(result.subtype=='Total')].set_index('target')
        assert abs(s.loc['S','point_estimate']-e.reference_country_composition_effect)<1e-8
        assert abs(s.loc['Net_change','point_estimate']-e.net_gap_change)<1e-8
    meta={'scope':'Preliminary PCOS marginal-limit Cartesian-box stress test; not a simultaneous posterior interval, no claimed 95% coverage, no inferred joint draws.','rate_cells':798,'population_shares_fixed':True,'subtype_joint_additivity_not_imposed_on_box_corners':True,'point_result_matches_reproduced_core':True,'interpretation':'Corners may not be jointly plausible. A zero-crossing box establishes scenario sensitivity only; it does not show non-significance or a posterior probability. A net-change box crossing zero can make an unconstrained percentage box unstable or unbounded, so no percentage interval is calculated.'}
    (op/'GBD_stress_metadata.json').write_text(json.dumps(meta,indent=2))
    print(result[(result.source=='GBD')].to_string(index=False));print(pd.DataFrame(tipping).to_string(index=False))

if __name__=='__main__':main()
