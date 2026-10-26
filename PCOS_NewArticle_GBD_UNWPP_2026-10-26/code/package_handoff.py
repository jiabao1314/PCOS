"""生成本地完整复核包和排除原始GBD输入的公共代码结果包。"""
from pathlib import Path
import hashlib
import json
import zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'delivery'

def public_ok(p):
    rel=p.relative_to(ROOT);s=str(rel)
    if rel.parts[0]=='source_article':
        return 'submission/SubmissionPrep_XX/deliverables/' in s and p.name in ['HumanReproduction_SubmissionDraft_XX.pdf','ReproductiveHealth_BackupDraft_XX.pdf','Supplement_ComparatorBenchmark_XX.pdf']
    if p.name=='rate_cells.csv':return False
    if rel.parts[:2]==('data','input'):return not p.name.startswith('IHME')
    if rel.parts[:2]==('data','published_expected'):return p.name in ['all_annual_benchmark_aspr.csv','symmetric_decomposition_1990_endpoints.csv','leave_one_country_out.csv','qc_summary.json']
    if rel.parts[:2] in [('results','notebook_R'),('results','notebook_python')]:return False
    return p.name!='software_environment.json'

def main():
    OUT.mkdir(exist_ok=True)
    files=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(x in p.relative_to(ROOT).parts for x in ['.venv','private_build','logs','delivery','__pycache__','.ipynb_checkpoints']):continue
        if p.suffix=='.zip' and 'source_article' in p.relative_to(ROOT).parts:continue
        files.append(p)
    records=[]
    for name,selected,raw in [('PCOS_新文章_师兄复核完整包_2026-10-26.zip',files,True),('PCOS_NewArticle_public_code_results_2026-10-26.zip',[p for p in files if public_ok(p)],False)]:
        target=OUT/name
        hashes={}
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for p in sorted(selected):
                z.write(p,p.relative_to(ROOT));hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
            z.writestr('PACKAGE_SHA256.json',json.dumps(hashes,ensure_ascii=False,indent=2))
        with zipfile.ZipFile(target) as z:assert z.testzip() is None
        records.append(dict(file=str(target.relative_to(ROOT)),bytes=target.stat().st_size,files=len(selected),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),includes_original_GBD_inputs=raw))
    (OUT/'package_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));print(json.dumps(records,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
