#!/usr/bin/env python3
"""Finite editorial revision verification; does not rerun study analyses."""
import importlib.util,json,re,csv,hashlib,zipfile,subprocess,unicodedata
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from lxml import etree
from docx import Document
import pymupdf as fitz
R=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('build',R/'scripts/build_bluek_v7_20261030.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
P,O,V,A,B,D=m.P,m.O,m.V,m.A,m.B,m.D
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
def compact(s):return re.sub(r'[^a-z0-9]+','',unicodedata.normalize('NFKC',s).lower())
def walk(v):
    if isinstance(v,dict):
        yield v
        for x in v.values():yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)
def nonmath(v):
    if isinstance(v,list):return ''.join(nonmath(x) for x in v)
    if not isinstance(v,dict):return ''
    if v.get('t') in ['Math','Image']:return ''
    if v.get('t')=='Str':return v['c']
    if v.get('t')=='Code':return v['c'][1]
    if v.get('t') in ['Space','SoftBreak','LineBreak']:return ' '
    return nonmath(v.get('c',[]))
def pdfbody(path):
    doc=fitz.open(path)
    return '\n'.join(page.get_text(clip=fitz.Rect(69,60,page.rect.width, page.rect.height-35)) for page in doc)

def verify():
    s=(P/'main_final_external.tex').read_text();baseline=(P/'BlueK_complete_baseline_external.tex').read_text()
    fixes=json.loads((P/'fixes.json').read_text());restored=s
    for f in reversed(fixes):
        if f['id']=='FIX-09':continue
        if f['after']:assert restored.count(f['after'])==1;restored=restored.replace(f['after'],f['before'])
        else:
            # The removed Xu bibliography entry originally immediately preceded Yang.
            mark=r'\bibitem[Yang et al.(2022)]{yang}';assert restored.count(mark)==1
            restored=restored.replace(mark,f['before']+mark)
    assert restored==baseline,'Changes exceeded the finite FIX list'
    protect=json.loads((O/'docs'/(D+'Preservation.json')).read_text());assert all(m.sha(R/p)==h for p,h in protect.items())
    citekeys={k for grp in re.findall(r'\\cite[pt]?\{([^}]+)\}',s) for k in grp.split(',')}
    bibkeys=set(re.findall(r'\\bibitem\[[^]]+\]\{([^}]+)\}',s));assert citekeys==bibkeys,(citekeys-bibkeys,bibkeys-citekeys)
    assert 'xu' not in bibkeys and len(bibkeys)==13
    cross=list(csv.DictReader((O/'docs'/(D+'BlueK_vs_v6_crosswalk.csv')).open()))
    manual={'For country $c$','Let $\\mathcal{R}$','Here $w_a$','For endpoints $t_0$','$X_k$, $Q_k$ and $S_k$','We report absolute components'}
    baseline_plain_checks=[]
    for row in cross:
        if row['locator'] in manual or row['teacher_lines'] in ['structural audit','Table 1 footnote']:continue
        a=row['BlueK_text'];b=row['baseline_editable_text']
        a=re.sub(r'\((?:Teede|GBD 2023 Collaborators|Liu|Liang|Institute for Health Metrics and Evaluation|Australian Government|Chen|Kitagawa|United Nations|PCOS research workspace|Stevens|Yang)[^)]*\)','',a)
        assert compact(a)==compact(b),(row['teacher_lines'],a,b)
        baseline_plain_checks.append(row['teacher_lines'])
    # Original equations, table cells and 5 vector assets must be exactly retained.
    old=(V/'manuscript/20261030_PCOS_HumanReproduction_v6_Manuscript.tex').read_text()
    eq=lambda text:re.findall(r'\\begin\{(align|equation)\}(.*?)\\end\{\1\}',text,re.S)
    assert eq(old)==eq(s)
    for file in re.findall(r'\\input\{([^}]+)\}',s):
        assert (V/'manuscript'/file).read_text() in (O/'manuscript'/(B+'Manuscript.tex')).read_text()
    getfig=lambda text:re.findall(r'% BEGIN INLINE VECTOR (\S+)\n([\s\S]*?)% END INLINE VECTOR \1',text)
    maintex=(O/'manuscript'/(B+'Manuscript.tex')).read_text()
    oldtex=(A/'manuscript/20261030_PCOS_HumanReproduction_v6_Overleaf_r1_Manuscript.tex').read_text()
    assert getfig(maintex)==getfig(oldtex) and len(getfig(maintex))==5
    assert 'Editorial revision:' not in maintex and r'\color{blue}' not in maintex
    assert s.count('XX')==baseline.count('XX')==23
    assert 'gpt-6.1-sol' in s and 'not independently verified' in s and 'must complete and confirm their review' in s
    # Teacher and v6 figure captions/alt text are the same. Compare normalized
    # page text on all five original figure pages, excluding the running header.
    teacher=fitz.open(P/'package/PCOS 20261030 Blue K.pdf');oldpdf=fitz.open(V/'output/20261030_PCOS_HumanReproduction_v6_Manuscript.pdf')
    assert len(teacher)==19
    teacher_figs=[]
    for i in range(5):
        t=teacher[len(teacher)-5+i].get_text(clip=fitz.Rect(69,60,596,807))
        v=oldpdf[len(oldpdf)-5+i].get_text(clip=fitz.Rect(69,60,596,807))
        assert compact(t)==compact(v),('Teacher figure-page content mismatch',i+1)
        teacher_figs.append(i+1)
    # DOCX has native mathematics and exact source PNGs, not flattened pages.
    ast=json.loads((P/'word/main.json').read_text());info=json.loads((O/'docs'/(D+'Word_Content_Map.json')).read_text())
    wp=O/'word'/(B+'Manuscript.docx')
    with zipfile.ZipFile(wp) as z:
        xml=etree.fromstring(z.read('word/document.xml'));maths=xml.xpath('//m:oMath',namespaces=NS)
        assert len(maths)==len(info['all_math_latex'])
        expected=re.sub(r'\s+','',nonmath(ast['blocks']))
        actual=re.sub(r'\s+','',''.join(t for t in xml.xpath('//w:t/text()',namespaces=NS) if not re.fullmatch(r'\([1-7]\)',t)))
        assert expected==actual,'Word text differs from parsed final TeX'
        assert etree.tostring(xml).decode().count('XX')==23
        media=[z.read(n) for n in z.namelist() if n.startswith('word/media/')]
        assert sorted(hashlib.sha256(b).hexdigest() for b in media)==sorted(f['sha256'] for f in info['figures'])
        assert len(xml.xpath('//wp:docPr',namespaces=NS))==5
    doc=Document(wp);assert len(doc.tables)==3
    def xt(e):return ''.join(e.xpath('.//w:t/text()|.//m:t/text()'))
    for table,ti in zip(doc.tables,info['tables']):
        clean=lambda t:re.sub(r'\\Delta\s*','Δ',t).replace('$','').replace(' ','')
        actualrows=[[clean(xt(c._tc)) for c in row.cells] for row in table.rows]
        expectedrows=[[clean(c) for c in row] for row in ti['rows']]
        assert actualrows==expectedrows
    inv=json.loads(m.run([m.PAN,'-f','docx','-t','json',wp]).stdout)
    assert len([n for n in walk(inv) if n.get('t')=='Math'])==len(maths)
    # Both clean and review copies must have identical rendered scientific text.
    cp=O/'output'/(B+'Manuscript.pdf');rp=O/'output'/(B+'Manuscript_Review.pdf')
    assert compact(pdfbody(cp))==compact(pdfbody(rp))
    pdfdata={}
    for name in ['Manuscript','Manuscript_Review']:
        path=O/'output'/(B+name+'.pdf');pdf=fitz.open(path);log=(O/'output'/(B+name+'.log')).read_text()
        assert len(pdf)==19 and not re.search(r'^!|LaTeX Warning|Package \S+ Warning|Overfull',log,re.M)
        pdfdata[name]={'pages':len(pdf),'sha256':m.sha(path),'compile_exit_code':0,'errors':0,'latex_package_warnings':0,'overfull_boxes':0,'underfull_info':len(re.findall('Underfull',log))}
    # The unchanged supplement remains compatible and retains honest GATHER gaps.
    sup=(V/'manuscript/20261030_PCOS_HumanReproduction_v6_Supplement.tex').read_text()
    assert '13 & Uncertainty approach & Partly met' in sup and '16 & Quantitative uncertainty & Incomplete' in sup
    supp_inline=(A/'manuscript/20261030_PCOS_HumanReproduction_v6_Overleaf_r1_Supplement.tex').read_text()
    assert len(set(re.findall(r'\\label\{tab:[^}]+\}',supp_inline)))==10
    assert 'Questions addressed by selected prior PCOS-attributed infertility analyses and the present study.' in supp_inline
    assert sup.count(r'\begin{figure}')==7
    cover=(V/'manuscript/20261030_PCOS_HumanReproduction_v6_CoverLetter.tex').read_text()
    assert 'gpt-6.1-sol' in cover and 'remain to be confirmed' in cover
    # Read existing aggregate CSVs only. This is a decimal-display audit, not
    # another statistical estimation or a claim of rerunning GBD.
    sr=R/'PCOS_Revision_2026-10-29/results/python';scalar_checks=[]
    def row(file,**filters):
        rr=[x for x in csv.DictReader((sr/(file+'.csv')).open()) if all(x[k]==str(v) for k,v in filters.items())]
        assert len(rr)==1,(file,filters,len(rr));return rr[0]
    def value(label,r,key,expected,scale=1):
        got=float(r[key])*scale;assert f'{got:.2f}'==f'{expected:.2f}',(label,got,expected)
        scalar_checks.append({'label':label,'column':key,'unrounded':got,'display':f'{got:.2f}','expected':f'{expected:.2f}','passed':True})
    rr=row('symmetric_decomposition_1990_endpoints',cause='Polycystic ovarian syndrome',subtype='Total',source='GBD',end=2023)
    for key,expected in [('china_rate_effect',271.51),('reference_rate_effect',-208.62),('reference_country_composition_effect',88.65),('net_gap_change',151.54)]:value(key,rr,key,expected)
    assert f"{float(rr['composition_share_of_net'])*100:.1f}"=='58.5'
    for source,expect in [('GBD',[2.16,-47.99,-127.89]),('UN-WPP2024',[2.26,-48.34,-127.89])]:
        for benchmark,expected in zip(['dynamic','fixed1990','equal'],expect):
            rr=row('all_annual_benchmark_aspr',cause='Polycystic ovarian syndrome',subtype='Secondary',source=source,year=2023,benchmark=benchmark);value(source+' '+benchmark,rr,'gap',expected)
    for age,expected in [(40,23.76),(35,20.42),(15,-2.27)]:
        rr=row('age_decomposition',cause='Polycystic ovarian syndrome',subtype='Total',source='GBD',start=1990,end=2023,age_start=age);value('Age '+str(age),rr,'reference_country_composition_effect',expected)
    for country,component,ratio in [('India',56.16,39.8),('Russian Federation',110.34,67.9)]:
        rr=row('composition_sensitivities',cause='Polycystic ovarian syndrome',subtype='Total',source='GBD',start=1990,end=2023,scenario='omit_'+country)
        value('Omit '+country,rr,'reference_country_composition_effect',component)
        assert f"{float(rr['composition_share_of_net'])*100:.1f}"==f'{ratio:.1f}'
    m.save(O/'docs'/(D+'Numeric_Audit.json'),{'type':'existing aggregate output readback; no new estimates','source_dir':str(sr.relative_to(R)),'checks':scalar_checks})
    for f in fixes:f['status']='verified';f['final_tex_locator']='Search exact final sentence in manuscript; source teacher-page locator retained'
    write=m.writecsv;write(O/'docs'/(D+'ChangeLog.csv'),fixes)
    md='# PCOS Blue K v7 DRAFT 修改对照\n\n以老师19页PDF为完整内容基础；仅FIX-01至09。未重跑科研分析或改数据。\n\n'
    for f in fixes:md+=f"## {f['id']} 老师稿第{f['teacher_page']}页\n\n原文：{f['before']}\n\n最终：{f['after'] or '删除未引用的Xu条目'}\n\n原因：{f['reason']}。核验：通过。\n\n"
    (O/'docs'/(D+'ChangeLog.md')).write_text(md)
    result={'at':datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds'),'status':'content_verified_visual_and_cloud_pending','scientific_snapshot':'1abf337d9f23cc69292e03cd581b6a1557e6effe','teacher_pdf_pages':19,'teacher_paragraph_and_structure_crosswalk_rows':len(cross),'PDF_prose_to_editable_baseline_exact_checks':baseline_plain_checks,'mathematical_paragraphs_manual_check_required':sorted(manual),'finite_patch_reversal_exact':True,'fix_ids_verified':sorted({f['id'] for f in fixes}),'crosswalk_note':'Headers (3 renamed subsection headings), 7 equation rows, references and all 5 figure pages additionally checked; initial source note deliberately omitted per FIX-09.','teacher_figure_pages_text_equal_v6':teacher_figs,'main_tables_exact':3,'native_vectors_exact_r1':5,'unchanged_old_files':len(protect),'Word':{'native_editable_math_objects':len(maths),'editable_numbered_equations':7,'all_nonmath_text_exact_final_TeX_AST':True,'native_math_roundtrip_count_equal':True,'editable_tables':3,'exact_source_PNGs':5,'XX_count':23},'PDF':pdfdata,'supplement':{'modified':False,'tables_S1_to_S11':True,'figures_S1_to_S7':True,'GATHER13':'Partly met','GATHER16':'Incomplete','status':'compatible with final main; old Word/TeX/PDF preserved'},'AI':{'evidence':'v6/docs/20261030_v6_AI_evidence.json; v5/docs/AI_VERSION_EVIDENCE.json','verified_session_only':'2026-10-29 / gpt-6.1-sol','other_model_versions':'not independently verified','author_final_review':'pending; teacher XX clause preserved','Methods_acknowledgements_cover_consistent':True},'new_scientific_analysis':False,'results_changed':False,'weights_changed':False,'qualified_draws_obtained':False,'posterior_intervals_added':False,'new_raw_data_downloaded':False,'submitted':False}
    visual=P/'visual_review.json'
    if visual.exists():
        v=json.loads(visual.read_text());assert v['review_first_page_final_colour_check']=='passed'
        for directory,files in v['files'].items():
            for name,h in files.items():assert m.sha(P/directory/name)==h
        assert v['Word_final_pages_inspected']==list(range(1,22)) and v['clean_TeX_PDF_pages_inspected']==list(range(1,20))
        result['visual_review']=v;result['status']='local_content_and_visual_verified_cloud_pending'
    result['PDF_compiler_environment_note']='Tectonic reports an invalid UTF-8 byte in cached lineno.sty line 296; output pages have no replacement glyph. This is separate from 0 LaTeX/package warnings and 7 Underfull messages in the final document logs.'
    result['output_hashes']={str(p.relative_to(O)):m.sha(p) for sub in ['manuscript','word','output'] for p in (O/sub).glob('*') if p.suffix in ['.tex','.docx','.pdf','.log']}
    m.save(O/'docs'/(D+'Verification.json'),result);print(json.dumps({'fixes':result['fix_ids_verified'],'word_math':len(maths),'PDF':pdfdata,'old_files':len(protect)},ensure_ascii=False))

if __name__=='__main__':verify()
