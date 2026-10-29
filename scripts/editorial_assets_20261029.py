#!/usr/bin/env python3
"""Regenerate numerical tables/plots in a private scratch directory and compare.

The independently reconstructed source-to-estimand audit is a prerequisite.
This check then exercises the actual archived renderer without altering it.
"""
import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'PCOS_Revision_2026-10-29'
DEST=ROOT/'PCOS_Revision_2026-10-29_v3'


def main():
    assert json.loads((DEST/'docs/claim_audit.json').read_text())['all_claims_pass']
    scratch=Path(tempfile.mkdtemp(prefix='editorial_assets_',dir=ROOT/'.shared_context_runtime'))
    (scratch/'data').mkdir()
    (scratch/'data/input').symlink_to(SOURCE/'data/input',target_is_directory=True)
    (scratch/'docs').mkdir()
    shutil.copy2(SOURCE/'docs/input_manifest.json',scratch/'docs/input_manifest.json')
    for language in ['python','R']:
        target=scratch/f'results/{language}'
        target.mkdir(parents=True)
        for p in (SOURCE/f'results/{language}').glob('*.csv'):
            shutil.copy2(p,target/p.name)
    spec=importlib.util.spec_from_file_location('archived_revision',SOURCE/'code/revision_analysis.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    mod.ROOT=scratch;mod.OUT=scratch/'results/python'
    mod.TEX=scratch/'manuscript/tables';mod.FIG=scratch/'manuscript/figures'
    mod.main()
    tables=[]
    for p in sorted((scratch/'manuscript/tables').glob('*.tex')):
        old=SOURCE/'manuscript/tables'/p.name
        new=DEST/'manuscript/tables'/p.name
        assert p.read_bytes()==old.read_bytes()==new.read_bytes(),p.name
        tables.append(dict(table=p.name,rows=p.read_text().count(r'\\'),regenerated_bytes_equal=True))
    figures=[]
    for p in sorted((scratch/'manuscript/figures').glob('*.pdf')):
        old=SOURCE/'manuscript/figures'/p.name
        new=DEST/'manuscript/figures'/p.name
        assert old.read_bytes()==new.read_bytes()
        assert PdfReader(p).pages[0].extract_text()==PdfReader(old).pages[0].extract_text(),p.name
        rendered=[]
        for label,source in [('regenerated',p),('archived',old)]:
            prefix=scratch/(p.stem+'_'+label)
            subprocess.run(['pdftoppm','-r','108','-singlefile','-png',str(source),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            with Image.open(str(prefix)+'.png') as im:
                rendered.append((im.size,im.convert('RGB').tobytes()))
        assert rendered[0]==rendered[1],p.name
        figures.append(dict(figure=p.name,regenerated_text_equal=True,regenerated_raster_equal=True))
    result=dict(tables=tables,figures=figures,table_count=len(tables),figure_count=len(figures),
                numerical_table_rows=sum(t['rows'] for t in tables),
                archived_generator_reexecuted=True,old_assets_unchanged=True,
                scope='All 11 table fragments and 12 figure PDFs compared with an isolated rerun of the archived generator; independent raw-input audit in claim_audit.json',
                no_new_estimates_adopted=True)
    assert len(tables)==11 and len(figures)==12
    (DEST/'docs/table_figure_qc.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
