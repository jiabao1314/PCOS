"""Build manuscript and supporting archives without raw IHME inputs or credentials."""
from pathlib import Path
import zipfile,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
README='''Additional file 2: Derived results and reproducible analysis\n\nGBD2023 female infertility attributed to endometriosis and PCOS, ages 15-49, 1990-2023.\nOriginal IHME CSVs are not bundled. Obtain them through the GBD Results Tool under its access and data-use terms. Exact filters, IDs, queries and SHA-256 input hashes are in docs/DATA_ACQUISITION.md and docs/raw_manifest.json. Place licensed originals in the documented data/raw folders. No aligned uncertainty draws were available; derived tables contain point estimates only.\n\nPython 3.12 dependencies are pinned in requirements.txt. After input retrieval, run bash run_all.sh (tectonic is additionally needed for PDFs), or the individual src scripts in the order listed there. All actual-data checks must pass; there is no synthetic research-data fallback. Unit-test fixtures verify arithmetic only. CSVs are UTF-8; rates use per 100,000 females.\n\nreference_composition_decomposition.csv: symmetric decomposition, 20 reference/age specifications, 2 causes, 3 infertility types, 2 starting years and 3 endpoints (720 rows). Components sum to change_D. reference_composition_age_type.csv adds the 7-age breakdown for the main reference (252 rows). subtype_change_robustness.csv also contains fixed-1990-share contrasts, which are path-based and are not symmetric components. Percentages of signed differences may exceed 100 or reverse signs when components offset. Do not add a subtype share to a composition share.\n\nThe manuscript, including uncertainty limitations and post hoc analysis disclosure, governs interpretation. Full source reproduction requires IHME input access; bundled result tables alone do not reconstruct the upstream GBD models.\n'''
def bundle(path,files,readme=None):
 files=sorted(set(p for p in files if p.is_file()))
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  if readme:z.writestr('README_ADDITIONAL_FILE_2.txt',readme)
  for p in files:z.write(p,p.relative_to(ROOT))
  z.writestr('FILE_SHA256.json',json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
 return {'file':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'members':len(files)+(2 if readme else 1)}
def run():
 docs=['DATA_ACQUISITION.md','raw_manifest.json','country_map.csv','pilot_validation.json','strata_qc.json','data_qc_initial.json','weights_provenance.json','standard_weights_used.csv','reference_composition_qc.json','journal_format_qc.json']
 files=[*ROOT.glob('src/*.py'),*ROOT.glob('config/*.json'),*ROOT.glob('tests/test*.py'),*[p for p in (ROOT/'results/tables').glob('*.csv')],*[p for p in (ROOT/'results/tables').glob('*.json')],*[ROOT/'docs'/n for n in docs],ROOT/'requirements.txt',ROOT/'run_all.sh']
 # run_all also builds the manuscripts, so provide their editable dependencies.
 manuscript=[*ROOT.glob('manuscript/*.tex'),*ROOT.glob('manuscript/tables/*.tex'),*ROOT.glob('manuscript/figures/*.pdf')]
 records=[bundle(OUT/'GBD2023_Reproductive_Health_Additional_file_2.zip',files+manuscript,README),bundle(OUT/'GBD2023_Reproductive_Health_TeX_sources.zip',manuscript)]
 final=[*files,*manuscript,ROOT/'docs/JOURNAL_AND_NOVELTY_AUDIT_ZH.md',ROOT/'docs/LITERATURE_AUDIT.csv',ROOT/'docs/STATUS.md',ROOT/'README.md',ROOT/'manuscript/cover_letter_Reproductive_Health.txt',*ROOT.glob('sources/journal_audit/*.json'),ROOT/'output/pdf/GBD2023_Reproductive_Health_main.pdf',ROOT/'output/pdf/GBD2023_Reproductive_Health_Additional_file_1.pdf',ROOT/'output/GBD2023_Reproductive_Health_Additional_file_2.zip',ROOT/'output/GBD2023_Reproductive_Health_TeX_sources.zip']
 records.append(bundle(OUT/'PCOS_Reproductive_Health_revision_2026-10-25.zip',final))
 (OUT/'journal_package_manifest.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':run()
