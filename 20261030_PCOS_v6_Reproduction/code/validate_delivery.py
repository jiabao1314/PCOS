#!/usr/bin/env python3
"""Build-time validation. Teacher entry point remains reproduce.py all."""
from pathlib import Path
import hashlib,json,platform,sys
from datetime import datetime
import nbformat
from nbclient import NotebookClient
import reproduce as rep

ROOT=Path(__file__).resolve().parents[1]
def main():
    target=ROOT/'verification/20261030_FINAL_VALIDATION.json'
    if target.exists():raise RuntimeError('Preserve the previous final validation; create a new dated revision.')
    versions={}
    import importlib.metadata
    for n in ['numpy','pandas','matplotlib','nbformat','nbclient','jupyterlab','ipykernel']:
        versions[n]=importlib.metadata.version(n)
    outputs=ROOT/'notebooks/executed';outputs.mkdir(exist_ok=True)
    notebook_checks=[]
    for p in sorted((ROOT/'notebooks').glob('*.ipynb')):
        n=nbformat.read(p,as_version=4)
        assert all(not c.get('outputs') and c.get('execution_count') is None for c in n.cells if c.cell_type=='code')
        print('Executing',p.name,flush=True)
        NotebookClient(n,timeout=900,kernel_name='pcos-v6',resources={'metadata':{'path':str(ROOT/'notebooks')}}).execute()
        nbformat.write(n,outputs/p.name)
        errors=[o for c in n.cells if c.cell_type=='code' for o in c.outputs if o.output_type=='error'];assert not errors
        notebook_checks.append({'notebook':p.name,'clean_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'executed_sha256':hashlib.sha256((outputs/p.name).read_bytes()).hexdigest(),'code_cells':sum(c.cell_type=='code' for c in n.cells),'image_outputs':sum('image/png' in o.get('data',{}) for c in n.cells if c.cell_type=='code' for o in c.outputs),'errors':0})
    assert len(notebook_checks)==3 and sum(x['image_outputs'] for x in notebook_checks)==12
    report=rep.check(require_r=True)
    figs=list((ROOT/'figures/python').glob('Figure*.png'));rfigs=list((ROOT/'figures/R').glob('Figure*.png'));assert len(figs)==len(rfigs)==12
    # Explicit aggregate-only learning mode is separate from raw reproduction.
    from notebook_support import figure_inputs
    assert len(figure_inputs(ROOT,source='reference')[0])==1224
    record={'status':'passed','run_at':datetime.now().astimezone().isoformat(timespec='seconds'),'platform':platform.platform(),'python':sys.version,'python_packages':versions,'notebooks':notebook_checks,'raw_input_sha256_checks':rep.verify_inputs(),'independent_numeric_tables':len(report['independent_R_Python_checks']),'historical_numeric_tables':len(report['historical_aggregate_checks']),'Python_figures':len(figs),'R_figures':len(rfigs),'no_joint_draws':True,'paper_unchanged':True,'Windows_native_execution':False,'teacher_Windows_reproduction':'pending on teacher machine','submitted':False}
    target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in record.items() if k not in ['notebooks','python_packages']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()

