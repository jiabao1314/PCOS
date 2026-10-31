#!/usr/bin/env python3
"""Colour-only copy of the verified v7 Word, plus an editable nine-fix index.

No statistics, scientific text, figures, equations or existing files are changed.
Run with the document workspace's bundled Python (python-docx/lxml available).
"""
from pathlib import Path
from copy import deepcopy,copy
from datetime import datetime,timezone
import csv,json,hashlib,re,subprocess,unicodedata,zipfile
from lxml import etree as E

R=Path(__file__).resolve().parents[1]
OLD=R/'PCOS_HumanReproduction_BlueK_Editorial_v7_DRAFT_2026-10-30'
O=R/'PCOS_HumanReproduction_BlueK_v7_ReviewWord_2026-10-31'
P=R/'.shared_context_runtime/bluek_review_word_20261031'
B='20261031_PCOS_HumanReproduction_BlueK_v7_DRAFT_Manuscript_Review'
D='20261031_PCOS_BlueK_v7_ReviewWord_'
SOURCE=OLD/'word/20261030_PCOS_HumanReproduction_BlueK_v7_DRAFT_Manuscript.docx'
PAN=R/'.shared_context_runtime/tools/pandoc-3.13'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
NS={'w':W,'m':M}
def q(n):return '{'+W+'}'+n
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('’',"'").replace('–','--'))
def text(p):return ''.join(p.xpath('.//w:t/text()',namespaces=NS))
def plain(s):
    if s.startswith('\\bibitem'):s=re.sub(r'^\\bibitem\[[^]]+\]\{[^}]+\}','',s)
    return subprocess.check_output([str(PAN),'-f','latex','-t','plain','--wrap=none'],input=s,text=True).strip()
def child(e,n):
    x=e.find(q(n))
    if x is None:x=E.Element(q(n));e.insert(0,x)
    return x
def colour(run,value):
    c=child(child(run,'rPr'),'color');c.attrib.clear();c.set(q('val'),value)
def addrun(p,s,colourval='000000',strike=False,bold=False,size=21):
    r=E.SubElement(p,q('r'));rp=E.SubElement(r,q('rPr'))
    fonts=E.SubElement(rp,q('rFonts'))
    for a,v in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia','Noto Sans CJK SC')]:fonts.set(q(a),v)
    E.SubElement(rp,q('lang')).set(q('eastAsia'),'zh-CN')
    E.SubElement(rp,q('sz')).set(q('val'),str(size))
    E.SubElement(rp,q('szCs')).set(q('val'),str(size))
    E.SubElement(rp,q('color')).set(q('val'),colourval)
    if strike:E.SubElement(rp,q('strike'))
    if bold:E.SubElement(rp,q('b'))
    t=E.SubElement(r,q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=s
    return r
def paragraph(s='',style=None,colourval='000000',strike=False,bold=False,pagebreak=False,keep=False):
    p=E.Element(q('p'));pp=E.SubElement(p,q('pPr'))
    if style:E.SubElement(pp,q('pStyle')).set(q('val'),style)
    E.SubElement(pp,q('suppressLineNumbers'))
    if pagebreak:E.SubElement(pp,q('pageBreakBefore'))
    if keep:E.SubElement(pp,q('keepNext'))
    E.SubElement(pp,q('keepLines'))
    sp=E.SubElement(pp,q('spacing'));sp.set(q('after'),'40');sp.set(q('line'),'264');sp.set(q('lineRule'),'auto')
    addrun(p,s,colourval,strike,bold)
    return p
def bookmark(p,name,num):
    st=E.Element(q('bookmarkStart'));st.set(q('id'),str(num));st.set(q('name'),name)
    end=E.Element(q('bookmarkEnd'));end.set(q('id'),str(num))
    p.insert(1 if len(p) and p[0].tag==q('pPr') else 0,st);p.append(end)
def link(p,label,anchor):
    h=E.SubElement(p,q('hyperlink'));h.set(q('anchor'),anchor)
    r=addrun(h,label,'0000FF');E.SubElement(child(r,'rPr'),q('u')).set(q('val'),'single')

def build():
    out=O/'word'/(B+'.docx');assert not out.exists(),'Preserve the existing dated result'
    for sub in ['word','docs']:(O/sub).mkdir(parents=True,exist_ok=True)
    P.mkdir(parents=True,exist_ok=True)
    # Protect every old manuscript/science file, including the completed v7.
    protected={str(p.relative_to(R)):sha(p) for root in [OLD,R/'PCOS_HumanReproduction_v6_2026-10-30',R/'PCOS_HumanReproduction_v6_Overleaf_r1_2026-10-30',R/'PCOS_Revision_2026-10-29'] for p in root.rglob('*') if p.is_file()}
    rows=list(csv.DictReader((OLD/'docs/20261030_PCOS_BlueK_v7_DRAFT_ChangeLog.csv').open()))
    assert {r['id'] for r in rows}=={f'FIX-{i:02d}' for i in range(1,10)}
    z=zipfile.ZipFile(SOURCE);original=E.fromstring(z.read('word/document.xml'));root=deepcopy(original)
    body=root.find(q('body'));paras=body.findall(q('p'));original_children=len(body)-1
    changed=[];anchors={};nextid=max([int(x) for x in root.xpath('//w:bookmarkStart/@w:id',namespaces=NS)]or[0])+1
    def anchor(p,name):
        nonlocal nextid
        bookmark(p,name,nextid);nextid+=1
        return name
    for ix,row in enumerate(rows):
        if row['id'] in ['FIX-05','FIX-09']:continue
        after=plain(row['after']);matches=[p for p in paras if norm(after) in norm(text(p))]
        assert len(matches)==1,(row['id'],after,len(matches))
        p=matches[0];before_bytes=E.tostring(p)
        # Match the existing review TeX: whole changed paragraph, except that
        # the unchanged STUDY QUESTION heading stays black.
        for run in p.xpath('.//w:r',namespaces=NS):
            if row['id']=='FIX-02' and 'STUDY QUESTION:' in text(run):continue
            if text(run):colour(run,'0000FF')
        suffix='a' if row['id']=='FIX-08' and 'age-specific' in row['after'] else ('b' if row['id']=='FIX-08' else '')
        a=anchor(p,'PCOS_'+row['id'].replace('-','')+suffix);anchors[ix]=a
        changed.append({'id':row['id'],'paragraph_index':paras.index(p),'anchor':a,'marked_plain_text':text(p),'teacher_page':row['teacher_page']})
        assert E.tostring(p)!=before_bytes
    assert len(changed)==8
    ref=next(p for p in paras if text(p).strip()=='References')
    anchors[next(i for i,r in enumerate(rows) if r['id']=='FIX-05')]=anchor(ref,'PCOS_FIX05')
    anchors[next(i for i,r in enumerate(rows) if r['id']=='FIX-09')]=anchor(paras[0],'PCOS_FIX09')
    # Separate review index: not part of the manuscript, with all nine IDs.
    # Four explicit pages avoid splitting the long AI declaration comparison.
    groups=[['FIX-01','FIX-02','FIX-03'],['FIX-04'],['FIX-05','FIX-06'],['FIX-07','FIX-08','FIX-09']]
    titles={'FIX-01':'绝对差距表述','FIX-02':'摘要主估计目标','FIX-03':'人口来源比较表述','FIX-04':'AI会话版本与作者核查','FIX-05':'删除未引用文献','FIX-06':'公开库与私人原始输入','FIX-07':'2020年中国调查口径','FIX-08':'两处限定用语','FIX-09':'清稿与审阅标记'}
    index=[];new=[]
    for page,ids in enumerate(groups,1):
        new.append(paragraph('本轮9项修正核对索引' if page==1 else f'修正核对索引 第{page}页',style='Heading1',bold=True,pagebreak=True,keep=True))
        if page==1:
            new.append(paragraph('2026年10月31日生成。本索引供作者和老师审阅，不属于论文正文。正文蓝字与既有标色TeX和PDF对应；文末逐项列出修改前后，点击“定位正文”可跳转。',keep=True))
            new.append(paragraph('本索引中红色删除线表示原文，蓝色表示修订后；这是可编辑字体标记，不是Word修订模式。原统计结果、图表、公式和XX保持不变。'))
        for fixid in ids:
            new.append(paragraph(fixid+' '+titles[fixid],style='Heading2',bold=True,keep=True))
            for ix,row in [(i,r) for i,r in enumerate(rows) if r['id']==fixid]:
                loc=paragraph('老师稿第'+row['teacher_page'].replace('--','–')+'页  ' ,keep=True)
                link(loc,'定位正文',anchors[ix]);new.append(loc)
                if fixid=='FIX-09':
                    before='Editorial revision: blue text marks additions or replacements relative to the supplied 30 October 2026 source. Numerical results and plotted data have not been re-estimated.'
                    after='clean论文正文移出上述内部编辑说明；本轮审阅稿仅标示这9项修正，老师原始蓝字稿和所有旧版本另行保留。此项不改变科学正文。'
                else:
                    before=plain(row['before']);after=plain(row['after']) if row['after'] else '删除此未被Blue K正文引用的文献条目；未新增替代引文或研究主张。'
                new.append(paragraph('原文',bold=True,keep=True));new.append(paragraph(before,colourval='A61C00',strike=True))
                new.append(paragraph('修订后',bold=True,keep=True));new.append(paragraph(after,colourval='0000FF'))
                new.append(paragraph('核对说明：'+row['reason']+'。'))
                index.append({'id':fixid,'teacher_page':row['teacher_page'],'main_bookmark':anchors[ix],'before_display':before,'after_display':after,'reason':row['reason']})
    sect=body.find(q('sectPr'));at=body.index(sect)
    for p in new:body.insert(at,p);at+=1
    # Unaffected ZIP members remain exact, including all style/relationship,
    # equation, image, table and header dependencies.
    core=E.fromstring(z.read('docProps/core.xml'))
    for prop in ['created','modified']:
        core.find('{http://purl.org/dc/terms/}'+prop).text=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with zipfile.ZipFile(out,'w') as dest:
        for info in z.infolist():
            value=z.read(info.filename)
            if info.filename=='word/document.xml':value=E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
            if info.filename=='docProps/core.xml':value=E.tostring(core,encoding='UTF-8',xml_declaration=True,standalone=True)
            dest.writestr(copy(info),value)
    # Independently strip only allowed formatting/bookmarks from the original
    # body portion, then require exact XML equality with the clean main.
    final=zipfile.ZipFile(out);back=E.fromstring(final.read('word/document.xml'));bb=back.find(q('body'))
    for e in list(bb)[original_children:-1]:bb.remove(e)
    for e in list(back.xpath('//w:bookmarkStart[starts-with(@w:name,"PCOS_FIX")]',namespaces=NS)):
        id=e.get(q('id'));e.getparent().remove(e)
        for x in back.xpath('//w:bookmarkEnd[@w:id="'+id+'"]',namespaces=NS):x.getparent().remove(x)
    for change in changed:
        pi=change['paragraph_index'];fp=bb.findall(q('p'))[pi];op=paras[pi]
        # Restore the source run properties only; text must independently match.
        for fr,orr in zip(fp.xpath('.//w:r',namespaces=NS),original.find(q('body')).findall(q('p'))[pi].xpath('.//w:r',namespaces=NS)):
            rp=fr.find(q('rPr'))
            if rp is not None:fr.remove(rp)
            oldrp=orr.find(q('rPr'))
            if oldrp is not None:fr.insert(0,deepcopy(oldrp))
    assert E.tostring(back)==E.tostring(original),'Main manuscript XML changed beyond colour/bookmarks'
    unchanged=[n for n in z.namelist() if n not in ['word/document.xml','docProps/core.xml']]
    assert all(final.read(n)==z.read(n) for n in unchanged)
    eq=lambda rt:[E.tostring(x) for x in rt.xpath('//m:oMath',namespaces=NS)]
    assert eq(root)==eq(original) and len(eq(root))==32
    tables=lambda rt:[E.tostring(t) for t in rt.xpath('//w:tbl',namespaces=NS)]
    assert tables(root)==tables(original) and len(tables(root))==3
    assert all(sha(R/p)==h for p,h in protected.items())
    with (O/'docs'/(D+'Change_Index.csv')).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(index[0]));w.writeheader();w.writerows(index)
    inputs={str(p.relative_to(R)):sha(p) for p in [SOURCE,OLD/'manuscript/20261030_PCOS_HumanReproduction_BlueK_v7_DRAFT_Manuscript_Review.tex',OLD/'output/20261030_PCOS_HumanReproduction_BlueK_v7_DRAFT_Manuscript_Review.pdf',OLD/'docs/20261030_PCOS_BlueK_v7_DRAFT_ChangeLog.csv']}
    result={'date':'2026-10-31','status':'content_verified_render_and_cloud_pending','source_hashes':inputs,'output_docx':str(out.relative_to(R)),'output_sha256':sha(out),'main_exact_XML_after_restoring_only_source_run_properties_and_removing_new_bookmarks':True,'main_text_statistics_and_XX_preserved':True,'native_math_objects_exact':32,'editable_main_tables_exact':3,'original_image_parts_exact':5,'unchanged_zip_parts_exact':unchanged,'blue_main_paragraphs':changed,'fix_ids':sorted({r['id'] for r in index}),'index_rows':len(index),'index_pages_planned':4,'index_is_separate_from_paper':True,'old_file_count_unchanged':len(protected),'overleaf_status':'not_applicable_word_only_no_TeX_change; no Word upload','new_scientific_analysis':False,'submitted':False}
    save(O/'docs'/(D+'Verification.json'),result);save(P/'preservation.json',protected)
    (O/'20261031_README_ZH.txt').write_text('本轮仅新增v7九项修正的可编辑标色Word，不修改任何论文科学内容。\n正文蓝色与既有Review TeX/PDF对应；文末附四页核对索引，红色删除线为原文，蓝色为修订后，支持点击定位正文。FIX-08含两处，共9项10行。\n索引是作者审阅材料，不属于论文正文；颜色是直接字体格式，不是Word修订模式。公式、三表、五图与XX保留，旧v6/v7及老师原稿不覆盖。\n本文件生成日2026年10月31日，论文正文仍保留既有30 October 2026版本日期。\n仅同步Drive与GitHub。Overleaf永远只收论文TeX，本轮未改TeX，不上传Word。暂不投稿。\n实际格式核验与同步状态见docs中的Verification及SYNC_RECEIPT。\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['blue_main_paragraphs','unchanged_zip_parts_exact','source_hashes']},ensure_ascii=False))

if __name__=='__main__':build()
