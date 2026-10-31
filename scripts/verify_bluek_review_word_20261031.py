#!/usr/bin/env python3
"""Read-only manuscript comparison and real rendered Word acceptance audit."""
import importlib.util,json,re,zipfile,hashlib,subprocess,unicodedata,sys
from pathlib import Path
from lxml import etree as E
import pymupdf as fitz
R=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('builder',R/'scripts/build_bluek_review_word_20261031.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
def norm(t):return re.sub(r'\s+','',unicodedata.normalize('NFKC',t).replace('’',"'").replace('–','--'))
def audit():
    source=zipfile.ZipFile(b.SOURCE);dest=zipfile.ZipFile(b.O/'word'/(b.B+'.docx'))
    assert dest.testzip() is None
    a=E.fromstring(source.read('word/document.xml'));c=E.fromstring(dest.read('word/document.xml'))
    main=c.find(b.q('body'))[:len(a.find(b.q('body')))-1]
    maintext=''.join(b.text(e) for e in main)
    assert maintext==''.join(b.text(e) for e in a.find(b.q('body'))[:-1])
    assert maintext.count('XX')==23
    assert [E.tostring(x) for x in c.xpath('//m:oMath',namespaces=b.NS)]==[E.tostring(x) for x in a.xpath('//m:oMath',namespaces=b.NS)]
    assert len(c.xpath('//m:oMath',namespaces=b.NS))==32
    assert [E.tostring(x) for x in c.xpath('//w:tbl',namespaces=b.NS)]==[E.tostring(x) for x in a.xpath('//w:tbl',namespaces=b.NS)]
    unaffected=[n for n in source.namelist() if n not in ['word/document.xml','docProps/core.xml']]
    assert all(source.read(n)==dest.read(n) for n in unaffected)
    # Independently extract balanced blue TeX groups and compare visible Word
    # blue text in the main manuscript (the appendix is not included).
    tex=(b.OLD/'manuscript/20261030_PCOS_HumanReproduction_BlueK_v7_DRAFT_Manuscript_Review.tex').read_text()
    expected=[]
    for m in re.finditer(r'\{\\color\{blue\}\s*',tex):
        start=m.end();i=start;depth=1
        while depth:
            if tex[i]=='{' and tex[i-1]!='\\':depth+=1
            if tex[i]=='}' and tex[i-1]!='\\':depth-=1
            i+=1
        prose=re.sub(r'\\(?:subsection|section)\*?\{[^}]*\}\s*','',tex[start:i-1])
        expected.append(norm(b.plain(prose)))
    blue=[]
    for p in main:
        if p.tag!=b.q('p'):continue
        t=''.join(b.text(r) for r in p.xpath('.//w:r[w:rPr/w:color[@w:val="0000FF"]]',namespaces=b.NS))
        # Pandoc's isolated TeX snippet omits natbib citation labels. Full
        # manuscript text including citations is already checked exactly above.
        t=t.replace('(Yang et al., 2022)','').replace('(Teede et al., 2023)','')
        if t:blue.append(norm(t))
    assert len(expected)==len(blue)==8 and sorted(expected)==sorted(blue)
    names=c.xpath('//w:bookmarkStart/@w:name',namespaces=b.NS)
    links=c.xpath('//w:hyperlink/@w:anchor',namespaces=b.NS)
    assert len([n for n in names if n.startswith('PCOS_FIX')])==10 and len(links)==10
    assert all(n in names for n in links)
    protect=json.loads((b.P/'preservation.json').read_text());assert all(b.sha(R/p)==h for p,h in protect.items())
    render=b.P/'render_final_v2';pdf=fitz.open(next(render.glob('*.pdf')))
    assert len(pdf)==25 and len(list(render.glob('page-*.png')))==25
    indextext=''.join(p.get_text() for p in pdf[21:])
    assert all(f'FIX-{i:02d}' in indextext for i in range(1,10))
    assert all('修正核对索引' in p.get_text() for p in pdf[21:])
    goto=[l for p in pdf[21:] for l in p.get_links() if l['kind']==1]
    assert len(goto)==10 and all(0<=l['page']<21 for l in goto)
    assert any('NotoSansCJKsc' in str(f) for f in pdf[21].get_fonts())
    att=json.loads((b.P/'visual_review.json').read_text())
    for n,h in att['final_page_png_sha256'].items():assert b.sha(render/n)==h
    assert att['all_pages_passed']==list(range(1,26))
    info={'date':'2026-10-31','status':'local_content_visual_and_internal_links_verified','Word_pages':25,'main_pages':21,'separate_index_pages':4,'main_text_exact_clean_Word':True,'main_XX_count':23,'native_OMML_exact':32,'editable_tables_exact':3,'image_bytes_exact':5,'blue_prose_groups_equal_Review_TeX':8,'colour_scope_note':'Word preserves black heading styles; eight blue prose groups match Review TeX. Isolated Pandoc snippets omit two natbib labels; full Word main including citations independently equals the clean Word.','nine_fix_ids_present':True,'index_rows_and_working_internal_links':10,'all_25_pages_rendered_and_visually_passed':True,'CJK_font_embedded_in_QA_render':True,'all335_old_files_unchanged':len(protect)==335,'output_sha256':b.sha(b.O/'word'/(b.B+'.docx')),'source_hashes':{str(b.SOURCE.relative_to(R)):b.sha(b.SOURCE)},'visual_evidence':att,'new_analysis':False,'submitted':False,'cloud_sync':'separate final SYNC_RECEIPT after actual cloud byte verification'}
    f=b.O/'docs'/(b.D+'Verification.json');data=json.loads(f.read_text());data.update(info);b.save(f,data)
    if len(sys.argv)>1:
        out=Path(sys.argv[1]);assert not out.exists();b.save(out,{'actual_command':sys.argv,'checks_passed':{k:v for k,v in info.items() if k!='visual_evidence'}})
    print(json.dumps({k:v for k,v in info.items() if k not in ['visual_evidence','source_hashes']},ensure_ascii=False))
if __name__=='__main__':audit()
