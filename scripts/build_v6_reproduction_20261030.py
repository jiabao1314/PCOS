#!/usr/bin/env python3
"""Assemble a dated v6 reproduction workspace, preserving research originals.

Raw GBD files are private; only the explicit public allowlist may be published.
This builder does not download data or perform journal submission.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys, zipfile
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'20261030_PCOS_v6_Reproduction'
SCI=ROOT/'PCOS_Revision_2026-10-29'
PRIVATE=ROOT/'.shared_context_runtime/repro_v6_20261030'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():
        assert dst.read_bytes()==src.read_bytes(),str(dst)
    else:shutil.copyfile(src,dst)

def assemble():
    for d in ['code','notebooks','data/input','data/published_expected','reference/aggregates','reference/tables','paper','docs','results/python','results/R','figures/python','figures/R','verification','logs']:(DEST/d).mkdir(parents=True,exist_ok=True)
    for p in (SCI/'data/input').iterdir():
        if p.is_file():copy(p,DEST/'data/input'/p.name)
    for p in (SCI/'data/published_expected').iterdir():
        if p.suffix in ['.csv','.json']:copy(p,DEST/'data/published_expected'/p.name)
    for p in (SCI/'results/python').iterdir():
        if p.suffix=='.csv' and p.name!='rate_cells.csv':copy(p,DEST/'reference/aggregates'/p.name)
    for n in ['PCOS_NewArticle_complete.py','extract_wpp2024.py']:copy(SCI/'code'/n,DEST/'code'/n)
    # Permit Python-only teaching first; the entry point subsequently performs
    # the complete independent R cross-check. No numerical expression changed.
    revision=(SCI/'code/revision_analysis.py').read_text().replace('def main():','def main(check_r=True):').replace('for name, keys in comparisons:','for name, keys in (comparisons if check_r else []):')
    revision=revision.replace("+ '\\n')", "+ '\\n', encoding='utf-8')")
    revpath=DEST/'code/revision_analysis.py'
    if revpath.exists():assert revpath.read_text()==revision
    else:revpath.write_text(revision)
    # Encoding only: Windows must read Türkiye and other UTF-8 names correctly.
    original=(SCI/'code/PCOS_NewArticle_complete.R').read_text()
    adapted=original.replace('stringsAsFactors=FALSE)\n  ages',"stringsAsFactors=FALSE,fileEncoding='UTF-8')\n  ages").replace("paste0(n,'.csv')),stringsAsFactors=FALSE)","paste0(n,'.csv')),stringsAsFactors=FALSE,fileEncoding='UTF-8')").replace("row.names=FALSE,na='')","row.names=FALSE,na='',fileEncoding='UTF-8')")
    adapted=adapted.replace("arg <- grep('^--file=',commandArgs(),value=TRUE)","arg <- grep('^--file=',commandArgs(),value=TRUE)\n    arg <- gsub('~+~',' ',arg,fixed=TRUE)")
    rp=DEST/'code/PCOS_NewArticle_complete.R'
    if rp.exists():assert rp.read_text()==adapted
    else:rp.write_text(adapted)
    for n in ['input_manifest.json','DATA_ACQUISITION.md','joint_draws_request.json','uncertainty_access_audit_2026-10-29.json','UN_reextraction_check.json']:copy(SCI/'docs'/n,DEST/'docs'/n)
    v6=ROOT/'PCOS_HumanReproduction_v6_2026-10-30'
    for p in (v6/'manuscript/tables').glob('*.tex'):copy(p,DEST/'reference/tables'/p.name)
    copy(ROOT/'PCOS_Revision_Preflight_2026-10-30/20261030_annual_endpoint_check.csv',DEST/'reference/aggregates/20261030_annual_endpoint_check.csv')
    r1=ROOT/'PCOS_HumanReproduction_v6_Overleaf_r1_2026-10-30'
    for kind in ['Manuscript','Supplement']:
        name='20261030_PCOS_HumanReproduction_v6_Overleaf_r1_'+kind
        copy(r1/'manuscript'/(name+'.tex'),DEST/'paper'/(name+'.tex'))
        copy(r1/'output'/(name+'_Cloud_ASCII.pdf'),DEST/'paper'/(name+'_Cloud_ASCII.pdf'))
    provenance={'created':datetime.now().isoformat(timespec='seconds'),'scientific_commit':'1abf337d9f23cc69292e03cd581b6a1557e6effe','v6_editorial_commit':'3dd7b5c3aabdc670c034c161cec4f7f6bf094a45','v6_compile_commit':'e877d47434c3aa5af5230892ba1a57db6187dca5','local_code_base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_snapshot':'PCOS_Revision_2026-10-29','R_core_changes':'Only explicit UTF-8 reading for Windows portability; numerical algorithm preserved.','original_code_sha256':{n:sha(SCI/'code'/n) for n in ['PCOS_NewArticle_complete.py','PCOS_NewArticle_complete.R','revision_analysis.py','extract_wpp2024.py']},'new_code_is_uncommitted_until_publication':True,'no_new_draws':True,'restricted_raw_input_count':4,'public_raw_input_count':3,'hospital_data_included':False,'Windows_D_drive_available_on_build_machine':False}
    (DEST/'docs/20261030_SOURCE_PROVENANCE.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
    print('Assembled current v6 paper, seven inputs, original core and reference aggregates; no original modified.')

def finalize():
    PRIVATE.mkdir(parents=True,exist_ok=True)
    old=json.loads((PRIVATE/'old_files_baseline.json').read_text())
    assert all(sha(ROOT/p)==h for p,h in old.items()),'Original files changed'
    # Publish actual derived CSV outputs as well as the prior reference tables.
    # Source-cell extracts are never copied to this reviewed aggregate snapshot.
    names=['all_annual_benchmark_aspr','symmetric_decomposition_1990_endpoints','leave_one_country_out','annual_chained_decomposition','composition_sensitivities','age_decomposition','national_annual_standardized','terminal_year_audit','endometriosis_terminal_age_type','age_weighted_reference_shifts','population_share_TVD','standard_weight_rounding','v6_annual_subtype_differences']
    for lang in ['python','R']:
        for name in names:copy(DEST/'results'/lang/(name+'.csv'),DEST/'reference'/('reproduced_'+lang)/(name+'.csv'))
    # Never publish original GBD, source cells, runtime logs, executed notebooks, or local environments.
    allow=[]
    for p in DEST.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(DEST)
        if any(x in rel.parts for x in ['__pycache__','.venv','.ipynb_checkpoints']):continue
        if rel.parts[0] in ['results','figures','tables','logs'] or 'executed' in rel.parts:continue
        if rel.parts[0]=='data' and p.name.startswith('IHME-'):continue
        if rel.parts[:2]==('data','published_expected') and p.name not in ['qc_summary.json','all_annual_benchmark_aspr.csv','symmetric_decomposition_1990_endpoints.csv','leave_one_country_out.csv']:continue
        if p.name in ['20261030_PRIVATE_MANIFEST.json','20261030_PUBLIC_MANIFEST.json']:continue
        if p.name!='.gitignore' and p.suffix not in ['.py','.R','.csv','.json','.ipynb','.tex','.pdf','.txt','.md','.ps1','.cmd','.yml','.Rproj']:continue
        allow.append(p)
    public=[]
    for p in sorted(allow):
        b=p.read_bytes()
        public.append({'path':str(p.relative_to(ROOT)),'package_path':str(p.relative_to(DEST)),'bytes':len(b),'sha256':sha(p),'git_blob':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()})
    manifest=DEST/'docs/20261030_PUBLIC_MANIFEST.json';manifest.write_text(json.dumps({'scope':'explicit reviewed code, UN/weights, aggregate references, clean notebooks, current paper, validation summaries; excludes licensed GBD and source cells','files':public},ensure_ascii=False,indent=2)+'\n')
    publicpaths=[x['path'] for x in public]+[str(manifest.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))]
    (PRIVATE/'public_paths.json').write_text(json.dumps(publicpaths,indent=2)+'\n')
    allfiles=[]
    for p in sorted(DEST.rglob('*')):
        if not p.is_file() or any(x in p.parts for x in ['__pycache__','.ipynb_checkpoints','.venv']):continue
        if p.name=='20261030_PRIVATE_MANIFEST.json':continue
        allfiles.append({'path':str(p.relative_to(DEST)),'bytes':p.stat().st_size,'sha256':sha(p),'scope':'private' if p.name.startswith('IHME-') or p.name=='rate_cells.csv' or 'logs' in p.parts else 'permitted document/aggregate'})
    (DEST/'docs/20261030_PRIVATE_MANIFEST.json').write_text(json.dumps({'files':allfiles,'private_research_use_only':True},ensure_ascii=False,indent=2)+'\n')
    archive=PRIVATE/'20261030_PCOS_v6_Reproduction_FULL_PRIVATE.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file() and not any(x in p.parts for x in ['__pycache__','.ipynb_checkpoints','.venv']):z.write(p,str(Path(DEST.name)/p.relative_to(DEST)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for item in allfiles:assert hashlib.sha256(z.read(DEST.name+'/'+item['path'])).hexdigest()==item['sha256']
    publiczip=PRIVATE/'20261030_PCOS_v6_Reproduction_PUBLIC.zip'
    with zipfile.ZipFile(publiczip,'w',zipfile.ZIP_DEFLATED) as z:
        for p in allow+[manifest]:z.write(p,str(Path(DEST.name)/p.relative_to(DEST)))
    print(json.dumps({'private_archive':str(archive),'private_bytes':archive.stat().st_size,'private_sha256':sha(archive),'public_paths':len(publicpaths),'public_archive':str(publiczip),'old_files_preserved':len(old)}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['assemble','finalize']);a=ap.parse_args();globals()[a.action]()
