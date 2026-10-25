"""Exploratory China age-specific prevalence backtesting, no future counts."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import json,warnings
import numpy as np
import pandas as pd
from scipy.special import expit,logit
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
ROOT=Path(__file__).resolve().parents[1]

def predict(z,h,kind):
    if kind=='naive':return np.repeat(z[-1],h),'last_observation'
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        if kind=='ETS':
            f=ExponentialSmoothing(z,trend='add',damped_trend=True,initialization_method='estimated').fit(optimized=True)
            return np.asarray(f.forecast(h)),'damped_additive_trend'
        candidates=[]
        for p,d,q in product(range(3),range(2),range(3)):
            try:
                f=ARIMA(z,order=(p,d,q)).fit(method_kwargs={'maxiter':75})
                if not f.mle_retvals.get('converged',True):continue
                n=len(z);k=len(f.params);aicc=f.aic+2*k*(k+1)/(n-k-1) if n>k+1 else np.inf
                if np.isfinite(aicc):candidates.append((aicc,f,(p,d,q)))
            except Exception:pass
        if not candidates:raise ValueError('No converged ARIMA candidate')
        _,f,order=min(candidates,key=lambda x:x[0]);return np.asarray(f.forecast(h)),str(order)

def series_task(task):
    cause,age,years,rate=task;rate=np.array(rate);z=logit(np.clip(rate/1e5,1e-10,1-1e-10));out=[]
    # Each training set is independent of its future observations.
    splits=[('rolling',n) for n in range(20,len(z))]+[('last10_holdout',len(z)-10)]
    for split,n in splits:
        hmax=min(5 if split=='rolling' else 10,len(z)-n)
        for model in ['naive','ARIMA','ETS']:
            try:pred,order=predict(z[:n],hmax,model);status='ok'
            except Exception as e:pred=np.repeat(np.nan,hmax);order='failed';status=type(e).__name__
            pred=expit(pred)*1e5
            for h in ([x for x in [1,3,5] if x<=hmax] if split=='rolling' else range(1,hmax+1)):
                out.append(dict(cause=cause,age=age,split=split,train_end=years[n-1],horizon=h,year=years[n+h-1],model=model,order=order,observed=rate[n+h-1],predicted=pred[h-1],status=status))
    return out

def run():
    b=pd.read_csv(ROOT/'data/processed/burden.csv');b=b[(b.location_name=='China')&(b.measure_name=='Prevalence')&(b.metric_name=='Rate')]
    tasks=[(c,a,g.sort_values('year').year.tolist(),g.sort_values('year').val.tolist()) for (c,a),g in b.groupby(['cause_name','age_name'])]
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for result in pool.map(series_task,tasks):rows.extend(result);print('Completed series',result[0]['cause'],result[0]['age'],flush=True)
    r=pd.DataFrame(rows);r['absolute_error']=abs(r.predicted-r.observed);r['squared_error']=(r.predicted-r.observed)**2
    r.to_csv(ROOT/'results/tables/forecast_backtest_predictions.csv',index=False)
    s=r.groupby(['cause','age','split','model'],as_index=False).agg(mae=('absolute_error','mean'),mse=('squared_error','mean'),valid=('predicted','count'),expected=('predicted','size'));s['rmse']=np.sqrt(s.mse)
    base=s[s.model=='naive'][['cause','age','split','mae']].rename(columns={'mae':'naive_mae'});s=s.merge(base);s['mae_ratio']=s.mae/s.naive_mae
    s.to_csv(ROOT/'results/tables/forecast_backtest_summary.csv',index=False)
    # Explicit exploratory gate: >10% MAE improvement in both validation schemes,
    # all seven ages, all predictions finite. No final forecasts unless gate met.
    gates=[]
    for (c,m),g in s[s.model!='naive'].groupby(['cause','model']):
        gates.append(dict(cause=c,model=m,pass_gate=bool((g.mae_ratio<.9).all() and (g.valid==g.expected).all()),max_mae_ratio=float(g.mae_ratio.max())))
    (ROOT/'results/tables/forecast_decision.json').write_text(json.dumps({'scope':'Exploratory China prevalence only; no population projection or future case counts','criterion':'Each of 7 ages: MAE ratio <0.9 vs naive, both rolling and last10 holdout; all predictions available','gate_results':gates,'uncertainty':'Validates extrapolation against modeled GBD point series, not independent observed data; no GBD uncertainty propagation'},indent=2))
if __name__=='__main__':run()
