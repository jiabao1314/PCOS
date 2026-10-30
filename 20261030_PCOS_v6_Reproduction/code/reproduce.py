#!/usr/bin/env python3
"""Portable v6 entry point. All paths resolve from this file, never a Mac path."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, platform, shutil, subprocess, sys
from datetime import datetime
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
KEYS={
 'all_annual_benchmark_aspr':['cause','subtype','source','year','benchmark'],
 'symmetric_decomposition_1990_endpoints':['cause','subtype','source','end'],
 'leave_one_country_out':['cause','subtype','source','omitted_country'],
 'annual_chained_decomposition':['cause','subtype','source'],
 'composition_sensitivities':['cause','subtype','source','scenario','start','end'],
 'age_decomposition':['cause','subtype','source','start','end','age_start'],
 'national_annual_standardized':['country','cause','subtype','year'],
 'terminal_year_audit':['country','cause','subtype','year'],
 'endometriosis_terminal_age_type':['age_start','subtype'],
 'age_weighted_reference_shifts':['source','country'],
 'population_share_TVD':['age_start','year'],
 'standard_weight_rounding':['cause','subtype','source'],
}
def load_module(name,filename):
 spec=importlib.util.spec_from_file_location(name,ROOT/'code'/filename);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def verify_inputs():
 manifest=json.loads((ROOT/'docs/input_manifest.json').read_text(encoding='utf-8'))
 for rel,m in manifest.items():
  p=ROOT/rel
  if not p.exists():raise FileNotFoundError(f'Missing licensed/public input: {rel}. Full private bundle or lawful restore required; see docs/DATA_ACQUISITION.md')
  assert p.stat().st_size==m['bytes'],rel
  assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'],rel
 return {'verified_inputs':len(manifest),'GBD_raw_inputs':4,'UN_weights_provenance_inputs':3,'synthetic_inputs':False}
def run_python():
 before=verify_inputs()
 core=load_module('pcos_core','PCOS_NewArticle_complete.py');core.main(ROOT)
 revision=load_module('pcos_revision','revision_analysis.py');revision.TEX=ROOT/'tables/python';revision.FIG=ROOT/'figures/python';revision.main(check_r=False)
 annual=pd.read_csv(ROOT/'results/python/all_annual_benchmark_aspr.csv')
 keys=['cause','source','benchmark','year'];wide=annual.pivot(index=keys,columns='subtype',values='gap').reset_index()
 wide['sum_residual']=wide['Total']-wide['Primary']-wide['Secondary'];assert len(wide)==408 and wide.sum_residual.abs().max()<1e-8
 wide.to_csv(ROOT/'results/python/v6_annual_subtype_differences.csv',index=False)
 e=wide[(wide.cause=='Endometriosis')&(wide.benchmark=='dynamic')&(wide.year.isin([2021,2022,2023]))].sort_values(['source','year'])
 e.to_csv(ROOT/'tables/python/TableS10.csv',index=False)
 rows=[f"{int(r.year)} & {'GBD' if r.source=='GBD' else 'UN WPP'} & {r.Primary:+.6f} & {r.Secondary:+.6f} & {r.Total:+.6f}\\\\" for _,r in e.iterrows()]
 (ROOT/'tables/python/s10_endometriosis_endpoints.tex').write_text('\n'.join(rows)+'\n\\bottomrule\n',encoding='utf-8')
 assert verify_inputs()==before
 return {'python_core_and_sensitivities':'passed','annual_subtype_rows':408,'no_joint_draws':True}
def find_r():
 exe=shutil.which('Rscript')
 if exe:return exe
 # Standard Windows installation, when R is not on PATH.
 if sys.platform=='win32':
  import os
  roots=[Path(os.environ.get('ProgramFiles','C:/Program Files'))/'R',Path(os.environ.get('LOCALAPPDATA','C:/Users/Default/AppData/Local'))/'Programs/R']
  candidates=[p for base in roots if base.exists() for p in base.glob('R-*/bin/Rscript.exe')]
  if candidates:return str(sorted(candidates)[-1])
 raise RuntimeError('Rscript not found. Install R and add R/bin to PATH, or use RStudio: source("code/reproduce_all.R", encoding="UTF-8").')
def run_r():
 verify_inputs();log=ROOT/'logs/R_run.log';log.parent.mkdir(exist_ok=True)
 proc=subprocess.run([find_r(),str(ROOT/'code/reproduce_all.R')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
 log.write_text(proc.stdout+'\n'+proc.stderr,encoding='utf-8')
 if proc.returncode:raise RuntimeError(f'R failed ({proc.returncode}). See {log}')
 return {'R_core_and_all_sensitivities':'passed','Rscript':Path(find_r()).name}
def compare_tables(left,right,keys):
 a=pd.read_csv(left);b=pd.read_csv(right)
 assert len(a)==len(b),str(left)
 assert not a.duplicated(keys).any() and not b.duplicated(keys).any()
 a=a.set_index(keys).sort_index();b=b.set_index(keys).sort_index();assert a.index.equals(b.index),str(left)
 assert set(a.columns)==set(b.columns),(left,set(a.columns)^set(b.columns))
 nums=a.select_dtypes('number').columns;maxerr=0.0;errors={}
 for c in nums:
  x=a[c].to_numpy(float);y=b[c].to_numpy(float)
  assert np.array_equal(np.isnan(x),np.isnan(y)),(left,c,'NA mismatch')
  err=float(np.nanmax(abs(x-y))) if np.any(np.isfinite(x)) else 0.
  assert err<1e-8,(str(left),c,err);maxerr=max(maxerr,err)
  errors[c]={'max_absolute_difference':err,'max_scaled_difference':float(np.nanmax(abs(x-y)/np.maximum(1,abs(x)))) if np.any(np.isfinite(x)) else 0.}
 for c in set(a.columns)-set(nums):assert a[c].fillna('').equals(b[c].fillna('')),(left,c)
 return {'table':left.stem,'rows':len(a),'numeric_columns':len(nums),'max_absolute_difference':maxerr,'per_column':errors}
def check(require_r=True):
 verify_inputs();archive=[];cross=[]
 for n,k in KEYS.items():
  archive.append(compare_tables(ROOT/'results/python'/f'{n}.csv',ROOT/'reference/aggregates'/f'{n}.csv',k))
  if require_r:cross.append(compare_tables(ROOT/'results/python'/f'{n}.csv',ROOT/'results/R'/f'{n}.csv',k))
 if require_r:
  cross.append(compare_tables(ROOT/'results/python/v6_annual_subtype_differences.csv',ROOT/'results/R/v6_annual_subtype_differences.csv',['cause','source','benchmark','year']))
 # Exact table bodies for the 11 original numerical tables. v6 S10 is numerically checked below.
 tables=[]
 for p in sorted((ROOT/'tables/python').glob('*.tex')):
  ref=ROOT/'reference/tables'/('20261030_v6_'+p.name)
  if ref.exists() and p.name!='s10_endometriosis_endpoints.tex':
   assert p.read_text(encoding='utf-8')==ref.read_text(encoding='utf-8'),p.name;tables.append(p.name)
 assert len(tables)==11
 expected=pd.read_csv(ROOT/'reference/aggregates/20261030_annual_endpoint_check.csv')
 got=pd.read_csv(ROOT/'results/python/v6_annual_subtype_differences.csv')
 # The archived v6 table uses explicit *_gap columns; do not use it as an input estimate.
 mapping={'primary_gap':'Primary','secondary_gap':'Secondary','total_gap':'Total','subtype_sum_residual':'sum_residual'}
 expected=expected.rename(columns=mapping)
 ek=['cause','source','benchmark','year'];x=expected.set_index(ek).sort_index();y=got.set_index(ek).sort_index()
 assert x.index.equals(y.index)
 for c in ['Primary','Secondary','Total']:assert np.nanmax(abs(x[c]-y[c]))<1e-8
 record={'status':'passed','run_at':datetime.now().astimezone().isoformat(timespec='seconds'),'platform':platform.platform(),'python':sys.version,'raw_inputs':verify_inputs(),'historical_aggregate_checks':archive,'independent_R_Python_checks':cross,'exact_original_numeric_TeX_table_bodies':tables,'v6_annual_subtype_rows':len(got),'main_figures':5,'supplement_figures':7,'new_joint_draws':False,'upstream_GBD_refit':False,'Windows_native_execution':'not performed on this macOS machine','path_portability':'all paths resolved from package root; separate relocation check recorded in delivery report'}
 out=ROOT/'verification/20261030_REPRODUCTION_CHECK.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 # Replace the legacy script's intentionally deferred empty R audit with the
 # completed independent cross-check; retain its original algorithm date.
 if require_r:
  (ROOT/'docs/R_Python_crosscheck.json').write_text(json.dumps(cross,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  qp=ROOT/'docs/revision_analysis_qc.json'
  q=json.loads(qp.read_text(encoding='utf-8'));q['source_algorithm_date']=q.pop('date',q.get('source_algorithm_date','2026-10-29'));q['reproduced_at']=record['run_at'];q['R_Python_crosscheck']=cross;q['original_numeric_supplement_tables']=q.pop('tables_supplement',8);q['current_v6_numeric_supplement_tables']=9;q['method_tables_not_estimated']=['GATHER','S9','S11'];qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return record
def all_steps():
 run_python();run_r();return check()
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['all','python','r','check','inputs']);a=ap.parse_args()
 result={'all':all_steps,'python':run_python,'r':run_r,'check':check,'inputs':verify_inputs}[a.action]()
 print(json.dumps(result,ensure_ascii=False,indent=2))
