#!/usr/bin/env python3
"""Package only code, permitted UN inputs, aggregate results and manuscripts."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]

def public_files():
    files=[ROOT/n for n in ['README.md','.gitignore','requirements.txt','requirements.lock.txt','run_revision.sh']]
    for folder in ['code','manuscript','docs']:
        files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in {'.py','.R','.tex','.pdf','.png','.json','.md','.txt'} and '__pycache__' not in p.parts and not p.name.startswith(('sync_receipt','artifact_manifest'))]
    for folder in ['results/python','results/R']:
        files += [p for p in (ROOT/folder).iterdir() if p.is_file() and p.suffix in {'.csv','.json','.txt','.pdf'} and p.name!='rate_cells.csv']
    for n in ['weights.csv','UN_WPP2024_G20_female_15_49_1990_2023.csv','UN_WPP2024_source_manifest.json']:
        files.append(ROOT/'data/input'/n)
    for n in ['qc_summary.json','all_annual_benchmark_aspr.csv','symmetric_decomposition_1990_endpoints.csv','leave_one_country_out.csv']:
        files.append(ROOT/'data/published_expected'/n)
    files += [ROOT/'output'/n for n in ['PCOS_ReproductiveHealth_Revised_2026-10-29.pdf','PCOS_Supplement_Revised_2026-10-29.pdf']]
    return sorted(set(files))

def main():
    files=public_files()
    for p in files:
        rel=p.relative_to(ROOT)
        assert 'private' not in rel.parts and 'logs' not in rel.parts
        assert not p.name.startswith('IHME-') and p.name!='rate_cells.csv'
    record=[]
    for p in files:
        b=p.read_bytes()
        record.append(dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),git_blob_sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()))
    manifest=ROOT/'docs/artifact_manifest.json'
    manifest.write_text(json.dumps(dict(date='2026-10-29',includes_licensed_raw_GBD=False,files=record),indent=2))
    archive=ROOT/'output/PCOS_Revision_Code_Results_Manuscript_2026-10-29.zip'
    with ZipFile(archive,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
        for p in files+[manifest]:
            z.write(p,str(Path(ROOT.name)/p.relative_to(ROOT)))
    with ZipFile(archive) as z:
        assert z.testzip() is None
        assert all('/private/' not in n and not Path(n).name.startswith('IHME-') and Path(n).name!='rate_cells.csv' for n in z.namelist())
    publish=record+[dict(path='docs/artifact_manifest.json',bytes=manifest.stat().st_size),dict(path='output/'+archive.name,bytes=archive.stat().st_size)]
    (ROOT/'private/publication_files.json').write_text(json.dumps(publish,indent=2))
    print(json.dumps(dict(files=len(files)+1,archive=str(archive),archive_bytes=archive.stat().st_size,archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),includes_licensed_raw_GBD=False),indent=2))

if __name__=='__main__':
    main()
