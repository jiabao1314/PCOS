#!/usr/bin/env python3
"""Make standalone paper TeX with inline tables and genuine native PGF charts.

Reuses only existing public aggregate results and the unchanged figure function;
does not refit, read raw GBD cells, encode images, or touch earlier manuscripts.
"""
import argparse,hashlib,importlib.util,json,re,subprocess
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1]
OLD=R/'PCOS_HumanReproduction_v6_2026-10-30'
OUT=R/'PCOS_HumanReproduction_v6_Overleaf_r1_2026-10-30'
P=R/'.shared_context_runtime/overleaf_v6_compile'
SCI=R/'PCOS_Revision_2026-10-29'
BASE='20261030_PCOS_HumanReproduction_v6_Overleaf_r1_'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def build():
    import numpy as np,pandas as pd,matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import RendererAgg
    from matplotlib.backends.backend_pgf import RendererPgf
    from matplotlib.lines import Line2D
    from matplotlib.collections import Collection
    from matplotlib.patches import Rectangle
    assert not list((OUT/'manuscript').glob('*.tex')),'Use another revision path rather than overwrite completed papers'
    (OUT/'manuscript').mkdir(parents=True,exist_ok=True);(OUT/'output').mkdir(exist_ok=True);(OUT/'docs').mkdir(exist_ok=True);(P/'pgf').mkdir(exist_ok=True)
    original={str(p.relative_to(R)):sha(p) for p in OLD.rglob('*') if p.is_file()}
    save(OUT/'docs/20261030_v6_Overleaf_original_preservation.json',original)
    code=SCI/'code/revision_analysis.py'
    spec=importlib.util.spec_from_file_location('original_revision_figures',code);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    names=['all_annual_benchmark_aspr','symmetric_decomposition_1990_endpoints','composition_sensitivities','age_weighted_reference_shifts','terminal_year_audit','endometriosis_terminal_age_type']
    paths=[SCI/'results/python'/(n+'.csv') for n in names]
    for p in [code,*paths]:
        committed=subprocess.check_output(['git','show','1abf337d9f23cc69292e03cd581b6a1557e6effe:'+str(p.relative_to(R))],cwd=R)
        assert committed==p.read_bytes(),p
    tables=[pd.read_csv(p) for p in paths]
    a,d,sens,shifts,end,ec=tables
    dyn=a[(a.source=='GBD')&(a.benchmark=='dynamic')]
    ez=end[(end.cause=='Endometriosis')&(end.subtype=='Total')]
    ec=ec.set_index(['age_start','subtype'])
    # PGF emits real paths and TeX text, not an encoded/raster/PDF file.
    # Agg supplies deterministic text metrics at the same dpi; final TeX is
    # compiled and visually checked separately using actual TeX fonts.
    def metrics(self,s,prop,ismath):
        agg=RendererAgg(max(1,int(self.figure.bbox.width)),max(1,int(self.figure.bbox.height)),self.dpi)
        return agg.get_text_width_height_descent(s,prop,ismath)
    RendererPgf.get_text_width_height_descent=metrics
    matplotlib.rcParams.update({'pgf.texsystem':'pdflatex','pgf.rcfonts':False,'axes.unicode_minus':False})
    figures={};evidence=[]
    def data_signature(fig):
        items=[]
        for ax in fig.axes:
            for line in ax.lines:items.append(['line',np.asarray(line.get_xdata()).tolist(),np.asarray(line.get_ydata()).tolist()])
            for patch in ax.patches:
                if isinstance(patch,Rectangle):items.append(['bar',patch.get_x(),patch.get_y(),patch.get_width(),patch.get_height()])
            for coll in ax.collections:items.append(['collection',np.asarray(coll.get_offsets()).tolist()])
        return hashlib.sha256(json.dumps(items,sort_keys=True,allow_nan=True,default=lambda x:x.item()).encode()).hexdigest()
    def pgf_save(fig,name):
        before=data_signature(fig)
        # Use a generic sans family resolved by both Agg and TeX.
        path=P/'pgf'/(name+'.pgf');fig.savefig(path,format='pgf',bbox_inches='tight')
        assert before==data_signature(fig)
        text=path.read_text();text='\n'.join(x for x in text.splitlines() if not x.startswith('%%'))+'\n'
        text=clean_pgf(text)
        assert not re.search(r'\\(?:includegraphics|pgfimage|input|write18|pdfobj)\b',text)
        figures[name]=text;evidence.append({'figure':name,'data_artist_sha256_before_and_after':before,'pgf_sha256':sha(path),'native_vector_TeX':True,'external_image_references':0})
        plt.close(fig)
    mod.savefig=pgf_save
    mod.figures(a,d,sens,shifts,ez,ec,dyn)
    assert len(figures)==12
    for kind in ['Manuscript','Supplement']:
        src=OLD/'manuscript'/('20261030_PCOS_HumanReproduction_v6_'+kind+'.tex');text=src.read_text()
        text=text.replace(r'\usepackage[T1]{fontenc}',r'\usepackage[T1]{fontenc}'+'\n'+r'\usepackage{pgf}'+'\n'+r'\providecommand{\mathdefault}[1]{#1}')
        inline=[]
        def table(m):
            path=OLD/'manuscript'/m[1];inline.append({'table':m[1],'sha256':sha(path)});return '% INLINE TABLE '+m[1]+'\n'+path.read_text()
        text=re.sub(r'\\input\{([^}]+)\}',table,text)
        replaced=[]
        def chart(m):
            name=Path(m[2]).stem.removeprefix('20261030_v6_');replaced.append(name)
            opts=m[1];size=r'\textwidth' if kind=='Manuscript' else r'.92\textwidth'
            # Original figures already have bounded aspect ratios; retain width.
            return '% BEGIN INLINE VECTOR '+name+'\n'+r'\makeatletter'+'\n'+r'\resizebox{'+size+r'}{!}{%'+'\n'+figures[name]+'}%\n'+r'\makeatother'+'\n% END INLINE VECTOR '+name
        text=re.sub(r'\\includegraphics\[([^]]+)\]\{([^}]+)\}',chart,text)
        assert len(replaced)==(5 if kind=='Manuscript' else 7)
        assert len(inline)==(3 if kind=='Manuscript' else 9)
        text=fix_longtable_header(text)
        text='% Standalone Overleaf compilation revision r1, 30 October 2026; scientific text and aggregate chart data unchanged.\n'+text
        target=OUT/'manuscript'/(BASE+kind+'.tex');target.write_text(text)
        assert text.count('XX')==src.read_text().count('XX')
        save(OUT/'docs'/('20261030_v6_Overleaf_'+kind+'_dependencies.json'),{'source':str(src.relative_to(R)),'source_sha256':sha(src),'output_sha256':sha(target),'inline_tables':inline,'native_PGF_figures':replaced,'XX_preserved':True})
    save(OUT/'docs/20261030_v6_Overleaf_build_provenance.json',{'at':datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds'),'code_sha256':sha(Path(__file__)),'reused_figure_code':{'path':str(code.relative_to(R)),'sha256':sha(code)},'aggregate_inputs':{str(p.relative_to(R)):sha(p) for p in paths},'figures':evidence,'raw_data_read':False,'new_scientific_analysis':False,'old_files':len(original),'submitted':False})
    print(json.dumps({'standalone_papers':2,'native_PGF_figures':12,'inline_tables':12,'old_files_preserved':len(original)}))

def compile_papers():
    papers=sorted((OUT/'manuscript').glob('*.tex'));assert len(papers)==2,'Both paper sources must exist before compilation'
    for p in papers:
        result=subprocess.run(['/opt/homebrew/bin/tectonic','--keep-logs','--outdir',str(OUT/'output'),str(p)],cwd=OUT/'manuscript',capture_output=True,text=True)
        stamp=datetime.now(ZoneInfo('Europe/Paris')).strftime('%Y%m%d_%H%M%S')
        (P/(p.stem+'_compile_'+stamp+'.log')).write_text(result.stdout+'\n'+result.stderr)
        assert result.returncode==0,result.stderr[-6000:]
    print('Both standalone paper TeX files compiled with Tectonic.')

def clean_pgf(text):
    # PGF's per-text active-% definitions cannot be tokenized inside resizebox.
    # These chart labels contain no math caret expressions; escape literal %.
    prefix=r'\catcode`\^=\active\def^{\ifmmode\sp\else\^{}\fi}\catcode`\%=\active\def%{\%}'
    text=text.replace(prefix,'{}').replace('(%)',r'(\%)')
    text=re.sub(r'\\selectfont(?=[A-Za-z])',lambda m:m[0]+'{}',text)
    return text.replace(r'\fontfamily{\familydefault}',r'\fontfamily{\sfdefault}')

def repair_pgf():
    for p in (OUT/'manuscript').glob('*.tex'):
        backup=P/(p.stem+'_initial_catcode_failure.tex')
        if not backup.exists():backup.write_bytes(p.read_bytes())
        text=clean_pgf(p.read_text())
        text=re.sub(r'(?<!\\makeatletter\n)(\\resizebox\{(?:\\textwidth|\.92\\textwidth)\})',lambda m:'\\makeatletter\n'+m[1],text)
        text=text.replace('}%\n% END INLINE VECTOR','}%\n\\makeatother\n% END INLINE VECTOR')
        p.write_text(text)
    print('Escaped PGF label percent signs and removed active-character setup for inline use.')

def fix_longtable_header(text):
    pattern=r'(\\caption\{([^\n]+)\}\\label\{tab:s11\}\\\\\n)([^\n]+)\\endhead'
    def fix(m):
        return m[1]+m[3]+'\\endfirsthead\n\\caption[]{'+m[2]+'}\\\\\n'+m[3]+'\\endhead'
    return re.sub(pattern,fix,text)

def repair_s11():
    p=OUT/'manuscript'/(BASE+'Supplement.tex')
    (P/'20261030_Supplement_before_s11_header_fix.tex').write_bytes(p.read_bytes())
    text=fix_longtable_header(p.read_text());assert text.count('\\label{tab:s11}')==1
    p.write_text(text);print('Table S11 label is now in the first-page header only; continuation caption retained without duplicate label.')

def verify():
    from pypdf import PdfReader
    baseline=json.loads((OUT/'docs/20261030_v6_Overleaf_original_preservation.json').read_text())
    assert all(sha(R/p)==h for p,h in baseline.items())
    results={}
    for kind in ['Manuscript','Supplement']:
        orig=OLD/'manuscript'/('20261030_PCOS_HumanReproduction_v6_'+kind+'.tex');target=OUT/'manuscript'/(BASE+kind+'.tex')
        src=orig.read_text();out=target.read_text()
        expected=re.sub(r'\\input\{([^}]+)\}',lambda m:'% INLINE TABLE '+m[1]+'\n'+(OLD/'manuscript'/m[1]).read_text(),src)
        restored=out.split('\n',1)[1].replace('\\usepackage{pgf}\n\\providecommand{\\mathdefault}[1]{#1}\n','')
        assets={Path(m[2]).stem.removeprefix('20261030_v6_'):m[0] for m in re.finditer(r'\\includegraphics\[([^]]+)\]\{([^}]+)\}',src)}
        for name,command in assets.items():
            restored,n=re.subn(r'% BEGIN INLINE VECTOR '+re.escape(name)+r'\n[\s\S]*?% END INLINE VECTOR '+re.escape(name),lambda m:command,restored)
            assert n==1
        assert restored==fix_longtable_header(expected),(kind,'paper text/notation/table content changed')
        uncommented='\n'.join(re.split(r'(?<!\\)%',line)[0] for line in out.splitlines())
        assert not re.search(r'\\(?:input|includegraphics|pgfimage|write18|pdfobj)\b',uncommented)
        assert not re.search(r'base64|data:image|stream\s+endstream',out,re.I)
        pdf=OUT/'output'/(BASE+kind+'.pdf');reader=PdfReader(pdf);text='\n'.join(p.extract_text() or '' for p in reader.pages)
        assert '\ufffd' not in text
        log=(OUT/'output'/(BASE+kind+'.log')).read_text(errors='replace')
        assert not re.search(r'(?:undefined references|undefined citations|Citation .*undefined|Reference .*undefined|Undefined control sequence|Missing character|Overfull \\hbox)',log,re.I)
        assert 'XX' in text
        depfile=OUT/'docs'/('20261030_v6_Overleaf_'+kind+'_dependencies.json');dep=json.loads(depfile.read_text());dep['output_sha256']=sha(target);save(depfile,dep)
        results[kind]={'tex_sha256':sha(target),'tex_bytes':target.stat().st_size,'pdf_sha256':sha(pdf),'pages':len(reader.pages),'paper_text_equations_tables_exactly_preserved':True,'original_XX_count_preserved':out.count('XX'),'native_PGF_figures':len(assets),'no_external_asset_dependency':True,'unresolved_citations_references_missing_glyphs_overfull_boxes':0,'visual_check':'pending','Overleaf_compile':'pending'}
    save(OUT/'docs/20261030_v6_Overleaf_local_verification.json',{'verified_at':datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds'),'documents':results,'original_v6_files_preserved':len(baseline),'submitted':False})
    print(json.dumps(results))

def finalize():
    verify()
    local=json.loads((OUT/'docs/20261030_v6_Overleaf_local_verification.json').read_text())
    qa=json.loads((OUT/'docs/20261030_v6_Overleaf_visual_QA.json').read_text())
    cloud=json.loads((P/'cloud_compile_evidence.json').read_text())
    assert qa['unresolved_visible_defects']==0 and qa['local_pages_covered_by_visual_review']==40
    for kind in ['Manuscript','Supplement']:
        src=OUT/'manuscript'/(BASE+kind+'.tex')
        assert src.read_bytes()==(Path.home()/'Downloads'/src.name).read_bytes()
        assert cloud[kind]['errors']==0 and cloud[kind]['warnings']==0
        assert cloud[kind]['pages']==local['documents'][kind]['pages']
        local['documents'][kind].update(visual_check='passed',Overleaf_compile='passed',Overleaf_tex_download_bytes_sha256_verified=True,Overleaf_log_errors=0,Overleaf_log_warnings=0,Overleaf_typesetting_info=cloud[kind]['typesetting_info'])
    local.update(compiler='Overleaf XeLaTeX / TeX Live 2026; local Tectonic cross-check',default_main_document=BASE+'Manuscript.tex',technical_revision_only=True,new_scientific_analysis=False,source_code_sha256=sha(Path(__file__)),old_Overleaf_files_retained=12,new_Overleaf_regular_paper_tex_documents=2,non_tex_files_uploaded_to_Overleaf=False,cloud_compile_evidence=cloud,visual_QA=qa,submitted=False)
    save(OUT/'docs/20261030_v6_Overleaf_FINAL_VERIFICATION.json',local)
    print('Final standalone source, native figures/tables, cloud compilation and source-download verification passed.')

def ascii_pdfs():
    """Valid lossless ASCII PDF streams for UTF-8-only publication transport."""
    import io
    from pypdf import PdfReader,PdfWriter
    from pypdf.generic import StreamObject,NameObject,ArrayObject,NullObject
    import pypdfium2 as F
    reports=[]
    for src in sorted((OUT/'output').glob('*.pdf')):
        if src.stem.endswith('_ASCII'):continue
        writer=PdfWriter(clone_from=src)
        for obj in writer._objects:
            if not isinstance(obj,StreamObject):continue
            old=obj.get('/Filter');filters=list(old) if isinstance(old,ArrayObject) else ([old] if old else [])
            params=obj.get('/DecodeParms')
            obj._data=obj._data.hex().encode('ascii')+b'>'
            obj[NameObject('/Filter')]=ArrayObject([NameObject('/ASCIIHexDecode'),*filters])
            if params:
                existing=list(params) if isinstance(params,ArrayObject) else [params]
                obj[NameObject('/DecodeParms')]=ArrayObject([NullObject(),*existing])
        out=io.BytesIO();writer.write(out);data=out.getvalue().replace(b'%\xe2\xe3\xcf\xd3\n',b'%ABCD\n',1)
        assert all(x<128 for x in data),'Output must itself be a valid ASCII PDF, not a transport wrapper'
        target=src.with_stem(src.stem+'_ASCII');target.write_bytes(data)
        a,b=PdfReader(src),PdfReader(target);assert [x.extract_text() for x in a.pages]==[x.extract_text() for x in b.pages]
        x,y=F.PdfDocument(src),F.PdfDocument(target)
        for i in range(len(x)):
            u=x[i].render(scale=1).to_pil().convert('RGB');v=y[i].render(scale=1).to_pil().convert('RGB');assert u.size==v.size and u.tobytes()==v.tobytes()
        reports.append({'source_path':str(src.relative_to(R)),'source_sha256':sha(src),'ASCII_PDF_path':str(target.relative_to(R)),'ASCII_PDF_sha256':sha(target),'pages':len(x),'all_pages_text_and_pixels_identical':True,'binary_sources_preserved':True})
    save(OUT/'docs/20261030_v6_Overleaf_ASCII_PDF_verification.json',{'files':reports,'reason':'GitHub base64 blob endpoint internal errors; valid ASCII PDF permits ordinary UTF-8 transport without changing rendering','not_an_embedded_or_renamed_non_PDF':True,'uploaded_to_Overleaf':False})
    print(json.dumps({'valid_ASCII_PDFs':len(reports),'all_rendering_and_text_preserved':True}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['build','compile','repair_pgf','repair_s11','verify','finalize','ascii_pdfs']);args=parser.parse_args();P.mkdir(exist_ok=True,parents=True)
    {'build':build,'compile':compile_papers,'repair_pgf':repair_pgf,'repair_s11':repair_s11,'verify':verify,'finalize':finalize,'ascii_pdfs':ascii_pdfs}[args.action]()
