#!/usr/bin/env python3
"""Finalize reviewed editorial artifacts and an explicit public allowlist."""
import csv
import difflib
import hashlib
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
NEW=ROOT/'PCOS_Revision_2026-10-29_v3'
OLD=ROOT/'PCOS_Revision_2026-10-29'
SHARED=ROOT/'00_Shared_Context'
RUNTIME=ROOT/'.shared_context_runtime'


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


def main():
    at=datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds')
    qc=json.loads((NEW/'docs/document_qc.json').read_text())
    assert qc['visual_review']=='reviewed'
    assets=json.loads((NEW/'docs/table_figure_qc.json').read_text())
    assert assets['table_count']==11 and assets['figure_count']==12
    audit=json.loads((NEW/'docs/claim_audit.json').read_text())
    assert audit['all_claims_pass'] and len(audit['claims'])==28
    for rel,h in json.loads((NEW/'docs/source_snapshot.json').read_text())['files'].items():
        assert digest(OLD/rel)==h,rel
    diffs=[]
    for name in ['main.tex','supplement.tex']:
        diffs.extend(difflib.unified_diff((OLD/'manuscript'/name).read_text().splitlines(True),
                                        (NEW/'manuscript'/name).read_text().splitlines(True),
                                        fromfile=f'{OLD.name}/manuscript/{name}',tofile=f'{NEW.name}/manuscript/{name}'))
    (NEW/'docs/EDITORIAL_CHANGES.diff').write_text(''.join(diffs))
    report=NEW/'docs/MANUSCRIPT_CLAIM_AUDIT.md'
    report.write_text(report.read_text()+f'''\n## Additional completed asset verification ({at})

The isolated archived-generator rerun reproduced all 11 table fragments (139 numerical rows) byte-for-byte and all 12 figure PDFs with identical extracted text and 108-dpi rendered pixels. See `table_figure_qc.json`. This supersedes the earlier provisional source-mapping-only scope for supplementary assets. All 184 archived source files remain unchanged. This computational agreement does not validate the upstream GBD model.

Across the 1,440 sensitivity rows the largest absolute difference was approximately 7.00e-9, including unstable signed ratios for near-zero net changes; this was below the prespecified 1e-8 numerical tolerance. Four core-table comparisons against archived R outputs had maximum difference approximately 6.25e-13. Displayed primary claims were unchanged.
''')
    literature={
        'checked_at':at,'scope':'Targeted verification of three named papers; not a systematic novelty search',
        'sources':[
            {'doi':'10.1093/humrep/dead241','authors':'Liu X, Zhang J, Wang S','issue_year':2024,
             'url':'https://pubmed.ncbi.nlm.nih.gov/38011904/','read_scope':'Author abstract and indexed citation',
             'supported_use':'GBD 2019 PCOS-attributed infertility burden, geographical and temporal descriptions'},
            {'doi':'10.3389/fpubh.2025.1693486','authors':'Liang Y, Zhong K, Huang Z, Shi W, Ou Y','issue_year':2025,
             'url':'https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2025.1693486/full',
             'read_scope':'Publisher abstract and decomposition-analysis section',
             'supported_use':'Existing burden trends and case-count decomposition into population growth, ageing and epidemiological change'},
            {'doi':'10.1016/j.rbmo.2025.105239','authors':'Liang Q','issue_year':2026,'volume_issue':'52(2):105239','online_date':'2025-09-02',
             'url':'https://pubmed.ncbi.nlm.nih.gov/41456540/','read_scope':'Author abstract and indexed citation; no full-text access claimed',
             'supported_use':'China/global GBD trend analysis with Joinpoint and ARIMA forecasting'}],
        'access_notes':'Initial DOI resolver attempts failed. Publisher and PubMed records were then opened successfully. No priority or exhaustive absence claim is made.'}
    save(NEW/'docs/LITERATURE_VERIFICATION.json',literature)
    (NEW/'README.md').write_text(f'''# PCOS independent editorial revision v3

Date: 29 October 2026 (Europe/Paris). Prepared {at}.

This is a separate revision of `PCOS_Revision_2026-10-29`; all 184 files of that archived source package were preserved. The manuscript remains a descriptive GBD/UN benchmark analysis. No clinical hospital study or new posterior uncertainty analysis is included.

## Deliverables

- `output/PCOS_Editorial_v3_2026-10-29.pdf`: 19-page main manuscript, 3 tables and 5 figures.
- `output/PCOS_Supplement_v3_2026-10-29.pdf`: 18-page supplement, 8 tables and 7 figures.
- `manuscript/`: editable TeX, all numerical table fragments and the 12 referenced vector figures.
- `docs/MANUSCRIPT_CLAIM_AUDIT.md`, `claim_audit.csv` and `claim_audit.json`: 28 central claims, code/input evidence and independent reconstruction checks.
- `docs/table_figure_qc.json`: all 11 table fragments/139 rows and 12 figure rasters matched an isolated renderer rerun.
- `docs/EDITORIAL_CHANGES.diff`: complete main/supplement source changes against the retained previous revision.
- `docs/LITERATURE_VERIFICATION.json`: targeted source verification, access scope and corrected RBMO issue year.
- `docs/EXECUTION_RECORD.json` and `logs/`: actual commands, failures/fixes, versions, code hashes and compiler logs.
- `output/PCOS_Editorial_v3_Complete_2026-10-29.zip`: sources, audits, scripts, PDFs and the required public original analysis code/aggregate evidence. Licensed GBD inputs and country-age source cells are excluded.

## Reproduction and compilation

The archive preserves repository-relative paths: this folder, `scripts/`, and the public parts of the earlier `PCOS_Revision_2026-10-29` folder. In a repository checkout, use Python 3.12, the earlier revision's pinned requirements, pypdf/Pillow, Tectonic and Poppler. The retained original README explains lawful GBD acquisition and the seven input hashes; supply those originals only in its private `data/input/` location. No new research inputs were downloaded this round.

The audit/build driver is `scripts/editorial_revision_20261029.py`; asset verification is `scripts/editorial_assets_20261029.py`. The `audit`/`all` driver deliberately refuses to overwrite an existing audit or manuscript. Reproduce creation in a fresh working copy without an existing v3 output directory. To compile the supplied source in a separate copy of this version:

```sh
cd manuscript
tectonic --keep-logs --keep-intermediates --outdir ../output main.tex
tectonic --keep-logs --keep-intermediates --outdir ../output supplement.tex
```

The archived R outputs were compared against the independent new reconstruction; R itself was not rerun in this round. Original and revised numerical assets remain identical. No GBD posterior draws were obtained. The 58.5% ratio and the 39.8%-67.9% specified scenario range retain their descriptive limitations. All intentional XX author/submission declarations are preserved.

## Storage and publication

Drive: https://drive.google.com/drive/folders/1tNldHZ1Bs2ah063jy2HuMngrr4FoMGxL

GitHub: https://github.com/jiabao1314/PCOS/tree/main/{NEW.name}

Publication status is established only by the later cloud-readback receipt in `00_Shared_Context/SYNC_CHECK.md`. This archive is a pre-publication content snapshot; a successful local build is not a cloud-synchronization receipt. No submission or external correspondence was performed.
''')
    events=[]
    for p in sorted((RUNTIME/'runs').glob('20261029_editorial_v3*.json')):
        events.append(json.loads(p.read_text()))
    execution=dict(at=at,events=events,
                   final_editorial_adjustment='Removed repeated benchmark prose while retaining the compact interpretation box; no numerical change.',
                   final_commands=[['PCOS_NewArticle_GBD_UNWPP_2026-10-26/.venv/bin/python','scripts/editorial_revision_20261029.py','build'],
                                   ['PCOS_NewArticle_GBD_UNWPP_2026-10-26/.venv/bin/python','scripts/editorial_revision_20261029.py','verify']],
                   final_compile_exit=0,final_document_check_exit=0,
                   render_commands='pdftoppm -r 80 -png on both complete PDFs; selected 140-dpi detail renders; repeated full main render after final edit',
                   visual_review='Both 37-page sets reviewed as contact sheets; benchmark box and Figures 3/5/S6/S7 detail checks; no visible clipping or overlap.',
                   build_warnings='Tectonic reports a legacy lineno.sty non-UTF8 comment and an underfull abstract hbox; no replacement characters, unresolved references or overfull boxes in final PDFs.',
                   code_base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                   publication_base_commit=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),
                   working_tree_dirty=True,
                   final_code_sha256={str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'scripts/editorial_revision_20261029.py',ROOT/'scripts/editorial_assets_20261029.py',Path(__file__)]},
                   source_file_count_unchanged=184,publication_commit='See later verified SYNC_CHECK receipt')
    save(NEW/'docs/EXECUTION_RECORD.json',execution)
    for source,target in [(RUNTIME/'20261029_editorial_v3.log',NEW/'logs/audit_build_execution.log'),
                          (RUNTIME/'20261029_editorial_v3_assets_final.log',NEW/'logs/asset_verification.log')]:
        shutil.copy2(source,target)
    # Deliberate, reviewed public paths; never recursively stage the workspace.
    files=[NEW/'README.md']
    files+=sorted((NEW/'docs').glob('*'))
    files+=sorted((NEW/'logs').glob('*.log'))
    files+=sorted((NEW/'manuscript').glob('*.tex'))
    files+=sorted((NEW/'manuscript/tables').glob('*.tex'))
    files+=sorted((NEW/'manuscript/figures').glob('*.pdf'))
    files+=[NEW/'output/PCOS_Editorial_v3_2026-10-29.pdf',NEW/'output/PCOS_Supplement_v3_2026-10-29.pdf']
    scripts=[ROOT/'scripts'/n for n in ['editorial_revision_20261029.py','editorial_assets_20261029.py','package_editorial_20261029.py']]
    # Public source evidence for a portable archive, not duplicate Git updates.
    evidence=[OLD/n for n in ['README.md','requirements.txt','requirements.lock.txt','run_revision.sh','docs/input_manifest.json','docs/DATA_ACQUISITION.md','docs/revision_analysis_qc.json','docs/R_Python_crosscheck.json']]
    evidence+=sorted((OLD/'code').glob('*.py'))+sorted((OLD/'code').glob('*.R'))
    for lang in ['python','R']:
        evidence+=[p for p in sorted((OLD/f'results/{lang}').glob('*.csv')) if p.name!='rate_cells.csv']
    evidence += [OLD/'data/input'/n for n in ['weights.csv','UN_WPP2024_G20_female_15_49_1990_2023.csv','UN_WPP2024_source_manifest.json']]
    evidence += [OLD/'data/published_expected'/n for n in ['qc_summary.json','all_annual_benchmark_aspr.csv','symmetric_decomposition_1990_endpoints.csv','leave_one_country_out.csv']]
    bundle_files=sorted(set(files+scripts+evidence))
    assert all(p.is_file() and 'private' not in p.relative_to(ROOT).parts and p.name!='rate_cells.csv' and not p.name.startswith('IHME-') for p in bundle_files)
    entries=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=digest(p)) for p in bundle_files]
    manifest=NEW/'docs/PUBLIC_ARTIFACT_MANIFEST.json'
    save(manifest,dict(at=at,licensed_raw_GBD_included=False,country_age_source_cells_included=False,patient_data_included=False,files=entries))
    archive=NEW/'output/PCOS_Editorial_v3_Complete_2026-10-29.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for p in bundle_files+[manifest]:z.write(p,str(p.relative_to(ROOT)))
    with ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(Path(n).name!='rate_cells.csv' and not Path(n).name.startswith('IHME-') and '/private/' not in n for n in z.namelist())
    files+=scripts+[manifest,archive]
    publish=[str(p.relative_to(ROOT)) for p in sorted(set(files))]
    save(RUNTIME/'editorial_publication_files.json',dict(at=at,files=publish,archive_sha256=digest(archive),raw_inputs_unchanged=True))
    print(json.dumps(dict(files=len(publish),archive_bytes=archive.stat().st_size,archive_sha256=digest(archive),bundle_entries=len(bundle_files)+1),indent=2))


if __name__=='__main__':main()
