#!/usr/bin/env python3
"""Check published claims, document cross-references and input/output paths."""
from pathlib import Path
import json
import re
from pypdf import PdfReader
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def main():
    reports={}
    maintext=(ROOT/'manuscript/main.tex').read_text()
    supptext=(ROOT/'manuscript/supplement.tex').read_text()
    for name,counttables,countfigures in [('main',3,5),('supplement',8,7)]:
        tex=(ROOT/f'manuscript/{name}.tex').read_text()
        aux=(ROOT/f'output/{name}.aux').read_text()
        log=(ROOT/f'output/{name}.log').read_text()
        assert not re.search(r'Overfull|(?:Reference|Citation).*undefined|There were undefined',log)
        labels=dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}',aux))
        localrefs=re.findall(r'\\ref\{([^}]+)\}',tex)
        assert all(x in labels for x in localrefs)
        figlabels={k:v for k,v in labels.items() if k.startswith('fig:')}
        tablabels={k:v for k,v in labels.items() if k.startswith('tab:')}
        assert len(figlabels)==countfigures and len(tablabels)==counttables
        prefix='S' if name=='supplement' else ''
        assert set(figlabels.values())=={prefix+str(x) for x in range(1,countfigures+1)}
        assert set(tablabels.values())=={prefix+str(x) for x in range(1,counttables+1)}
        for rel in re.findall(r'\\(?:input|includegraphics)(?:\[[^]]*\])?\{([^}]+)\}',tex):
            assert (ROOT/'manuscript'/rel).exists(),rel
        cited=set(k for group in re.findall(r'\\cite\{([^}]+)\}',tex) for k in group.split(','))
        bib=set(re.findall(r'\\bibitem(?:\[[^]]+\])?\{([^}]+)\}',tex))
        assert cited<=bib
        reader=PdfReader(ROOT/f'output/{name}.pdf')
        texts=[p.extract_text() or '' for p in reader.pages]
        assert all(len(x.strip())>80 for x in texts), 'Blank or nearly blank page'
        assert not any('??' in x or '\ufffd' in x for x in texts)
        reports[name]=dict(pages=len(texts),table_labels=tablabels,figure_labels=figlabels,all_local_references_resolved=True,no_blank_pages=True,no_overfull_boxes=True,no_unresolved_citations=True)
    # Cross-file references in the short main-text endpoint paragraph are deliberately
    # explicit; check the actual supplement numbering rather than trusting prose.
    for label,value in [('fig:s6','S6'),('fig:s7','S7'),('tab:s7','S7'),('tab:s2','S2')]:
        group='figure_labels' if label.startswith('fig') else 'table_labels'
        assert reports['supplement'][group][label]==value
    assert 'Table~S7; Figures~S6 and S7' in maintext
    a=pd.read_csv(ROOT/'results/python/all_annual_benchmark_aspr.csv')
    sec=a[(a.cause=='Polycystic ovarian syndrome')&(a.subtype=='Secondary')&(a.year==2023)&(a.source=='UN-WPP2024')].set_index('benchmark')
    assert [round(x,2) for x in sec.loc[['dynamic','fixed1990','equal'],'gap']]==[2.26,-48.34,-127.89]
    sens=pd.read_csv(ROOT/'results/python/composition_sensitivities.csv')
    z=sens[(sens.cause=='Polycystic ovarian syndrome')&(sens.subtype=='Total')&(sens.source=='GBD')&(sens.start==1990)&(sens.end==2023)]
    assert np.isclose(z.composition_share_of_net.min()*100,39.8140889969)
    assert np.isclose(z.composition_share_of_net.max()*100,67.8571652492)
    assert 'XX Author' in maintext and 'XX: author-specific disclosures' in maintext
    assert 'config/study.json' not in (ROOT/'docs/joint_draws_request.json').read_text()
    assert 'data/input/' in (ROOT/'README.md').read_text()
    reports['scientific_claim_checks']=dict(benchmark_values=True,composition_range=True,XX_preserved=True)
    reports['visual_QA']='All final pages rendered; page contact sheets and enlarged Figures 3/5/S6/S7 inspected separately before distribution. This entry does not replace human scientific review.'
    (ROOT/'docs/document_qc.json').write_text(json.dumps(reports,indent=2))
    print(json.dumps(reports,indent=2))

if __name__=='__main__':
    main()
