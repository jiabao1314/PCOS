"""Conditional trend inference; no claim to propagate GBD uncertainty."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import t
from core import segmented_trend

ROOT=Path(__file__).resolve().parents[1]

def conditional_fit(x,r,knots,ar1=False):
    x=np.asarray(x);y=np.log(r)
    X=np.column_stack([np.ones(len(x)),x-x[0],*[np.maximum(x-k,0) for k in knots]])
    if ar1:
        model=sm.GLSAR(y,X,rho=1)
        fit=model.iterative_fit(maxiter=30)
        rho=float(model.rho[0])
    else:
        fit=sm.OLS(y,X).fit();rho=0.0
    # AAPC is duration-weighted segment slopes; gradient in hinge coordinates.
    g=np.array([0,1,*[(x[-1]-k)/(x[-1]-x[0]) for k in knots]])
    slope=float(g@fit.params);se=float(np.sqrt(g@fit.cov_params()@g));critical=t.ppf(.975,fit.df_resid)
    return {'aapc':float(100*np.expm1(slope)),'ci_lower':float(100*np.expm1(slope-critical*se)),
            'ci_upper':float(100*np.expm1(slope+critical*se)),'rho':rho,
            'ci_scope':'Conditional on selected knots and fixed GBD point estimates; excludes knot-selection and GBD uncertainty'}

def run():
    d=pd.read_csv(ROOT/'results/tables/burden_standardized.csv');rows=[]
    for (loc,cause,measure),s in d[d.location_name.isin(['China','Other 18 G20 countries'])].groupby(['location_name','cause_name','measure_name']):
        for start in [1990,2010]:
            q=s[s.year>=start].sort_values('year');base=segmented_trend(q.year,q.asr,max_knots=2)
            three=segmented_trend(q.year,q.asr,max_knots=3)
            for label,knots,ar1 in [('OLS_0_2',base['knots'],False),('AR1_fixed_selected_knots',base['knots'],True),('OLS_0_3',three['knots'],False)]:
                rows.append(dict(location=loc,cause=cause,measure=measure,start=start,end=2023,model=label,knots=json.dumps(knots),**conditional_fit(q.year,q.asr,knots,ar1)))
    pd.DataFrame(rows).to_csv(ROOT/'results/tables/trend_sensitivity_conditional_ci.csv',index=False)

if __name__=='__main__':run()
