#!/usr/bin/env python3
"""Convert the preserved HR v4 TeX to editable Word, with native OMML mathematics.

Requires bundled Python (python-docx/lxml/Pillow) and official Pandoc >=3.
No statistics are reestimated. No submission, Git mutation or cloud write occurs here.
"""
import argparse, copy, hashlib, json, re, subprocess, zipfile
from pathlib import Path
from datetime import datetime
from docx import Document
from docx.shared import Mm, Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

ROOT=Path(__file__).resolve().parents[1]
V4=ROOT/'PCOS_HumanReproduction_v4_2026-10-29'
SOURCE=V4/'manuscript'
OUT=V4/'word_2026-10-29'
PRIVATE=ROOT/'.shared_context_runtime/word_v4'
PANDOC=ROOT/'.shared_context_runtime/tools/pandoc-3.13'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','a':'http://schemas.openxmlformats.org/drawingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
MAIN='PCOS_HumanReproduction_v4_Manuscript.docx'
SUPP='PCOS_HumanReproduction_v4_Supplement.docx'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2))
def run(args,**kw):return subprocess.run([str(x) for x in args],check=True,capture_output=True,text=True,**kw)
def braces(s,start):
    assert s[start]=='{';depth=0
    for i in range(start,len(s)):
        if s[i] in '{}' and (i==0 or s[i-1]!='\\'):
            depth+=1 if s[i]=='{' else -1
            if depth==0:return s[start+1:i],i+1
    raise ValueError('Unbalanced TeX group')
def command_groups(s,command):
    found=[]
    for m in re.finditer(re.escape(command)+r'\s*\{',s):
        value,end=braces(s,m.end()-1);found.append((m.start(),end,value))
    return found
def walk(v):
    if isinstance(v,dict):
        yield v
        for x in v.values():yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)
def plain(v):
    if isinstance(v,list):return ''.join(plain(x) for x in v)
    if not isinstance(v,dict):return ''
    t=v.get('t');c=v.get('c')
    if t=='Str':return c
    if t in ['Space','SoftBreak','LineBreak']:return ' '
    if t=='Math':return c[1]
    if t in ['Link','Image']:return plain(c[1])
    return plain(c) if isinstance(c,(dict,list)) else ''
def xml_text(e):return ''.join(n.text or '' for n in e.iter() if n.tag in [qn('w:t'),qn('m:t')])
def norm(s):return re.sub(r'\s+',' ',s).replace('\u00a0',' ').strip()
def nonmath_stream(v):
    if isinstance(v,list):return ''.join(nonmath_stream(x) for x in v)
    if not isinstance(v,dict):return ''
    if v.get('t') in ['Math','Image']:return ''
    if v.get('t')=='Str':return v['c']
    if v.get('t')=='Code':return v['c'][1]
    if v.get('t') in ['Space','SoftBreak','LineBreak']:return ' '
    return nonmath_stream(v.get('c',[]))
def para(inlines):return {'t':'Para','c':inlines}
def inline(s):return [{'t':'Str','c':s}]
def styled(s,style):return {'t':'Div','c':[['',[],[['custom-style',style]]],[para(s if isinstance(s,list) else inline(s))]]}

def prepare(kind):
    original=(SOURCE/(kind+'.tex')).read_text();s=original
    s=re.sub(r'\\input\{([^}]+)\}',lambda m:(SOURCE/m[1]).read_text(),s)
    refs=[];labels={}
    if kind=='main':
        b=re.search(r'\\begin\{thebibliography\}\{99\}(.*?)\\end\{thebibliography\}',s,re.S)
        for m in re.finditer(r'\\bibitem\[([^\]]+)\]\{([^}]+)\}(.*?)(?=\\bibitem|$)',b[1],re.S):
            label,key,body=m.groups();labels[key]=re.sub(r'\((\d{4})\)$',r', \1',label)
            refs.append({'key':key,'label':label,'tex':body.strip()})
        replacement=r'\section*{References}'+'\n\n'+'\n\n'.join(r['tex'] for r in refs)+'\n'
        s=s[:b.start()]+replacement+s[b.end():]
    citations=re.findall(r'\\citep\{([^}]+)\}',s)
    s=re.sub(r'\\citep\{([^}]+)\}',lambda m:'('+('; '.join(labels[k] for k in m[1].split(',')))+')',s)
    refmap={'tab:pcos':'1','tab:decomp':'2','tab:bench':'3','fig:trends':'1','fig:subtypes':'2','fig:decomp':'3','fig:source':'4','fig:bench':'5'}
    refmap.update({f'{p}:s{i}':f'S{i}' for p in ['tab','fig'] for i in range(1,10)})
    crossrefs=re.findall(r'\\ref\{([^}]+)\}',s)
    s=re.sub(r'\\ref\{([^}]+)\}',lambda m:refmap[m[1]],s)
    table_info=[];figure_info=[]
    def table_replace(m):
        block=m[0];idx=len(table_info)+1
        if kind=='main':number=str(idx)
        else:number='' if idx==1 else 'S'+str(idx-1)
        caps=command_groups(block,r'\caption')
        cap=caps[0][2] if caps else ''
        notes=command_groups(block,r'\caption*')
        note=notes[0][2] if notes else ''
        for start,end,value in sorted(caps+notes,reverse=True):block=block[:start]+block[end:]
        block=re.sub(r'\\label\{[^}]+\}','',block)
        if 'longtable' in block:
            # Retain the first header; Pandoc/Word will repeat that header on page breaks.
            if r'\endfirsthead' in block:
                a=block.index(r'\endfirsthead');b=block.index(r'\endhead',a)
                block=block[:a]+block[b+len(r'\endhead'):]
            else:block=block.replace(r'\endhead','')
            block=block.replace(r'\begin{longtable}',r'\begin{tabular}').replace(r'\end{longtable}',r'\end{tabular}')
        else:
            block=re.sub(r'\\begin\{table\}(?:\[[^\]]*\])?','',block).replace(r'\end{table}','')
        block=block.strip()
        # Empty row separators left after a removed longtable caption are unnecessary.
        block=re.sub(r'(\\begin\{tabular\}\{[^\n]+\})\s*\\\\',r'\1',block)
        caption=(('Table '+number+'. ') if number else '')+cap
        table_info.append({'number':number,'caption_tex':cap,'note_tex':note})
        return ('\n\n'+r'\textbf{'+caption+'}\n\n' if cap else '\n\n')+block+'\n\n'+note+'\n\n'
    # Both table environments are found in original appearance order.
    s=re.sub(r'\\begin\{(table|longtable)\}.*?\\end\{\1\}',table_replace,s,flags=re.S)
    def fig_replace(m):
        block=m[0];idx=len(figure_info)+1;number=str(idx) if kind=='main' else 'S'+str(idx)
        cap=command_groups(block,r'\caption')[0][2]
        notes=command_groups(block,r'\caption*');alt=notes[0][2] if notes else ''
        name=re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',block)[1]
        png=(SOURCE/name).with_suffix('.png');assert png.exists()
        figure_info.append({'number':number,'image':str(png.relative_to(ROOT)),'sha256':sha(png),'caption_tex':cap,'alt_tex':alt})
        return '\n\n'+r'\newpage'+'\n'+r'\includegraphics[width=6.2in]{'+str(png)+'}\n\n'+r'\textbf{Figure '+number+'.} '+cap+'\n\n'+alt+'\n\n'
    s=re.sub(r'\\begin\{figure\}.*?\\end\{figure\}',fig_replace,s,flags=re.S)
    # Number each original align row separately. Only alignment whitespace changes.
    equations=[]
    def eq_replace(m):
        env,body=m[1],m[2]
        rows=re.split(r'\\\\\s*',body) if env=='align' else [body]
        parts=[]
        for row in rows:
            if not row.strip():continue
            row=re.sub(r'&\s*=', '=',row)
            row=row.replace('&',r'\qquad ')
            row=row.strip();equations.append({'number':len(equations)+1,'latex':row})
            parts.append('\\[\n'+row+'\n\\]')
        return '\n\n'.join(parts)
    s=re.sub(r'\\begin\{(align|equation)\}(.*?)\\end\{\1\}',eq_replace,s,flags=re.S)
    # Remove TeX-only pagination before figures/tables; deliberate Word breaks are set later.
    s=s.replace(r'\clearpage','').replace(r'\newpage','')
    result=run([PANDOC,'-f','latex','-t','json'],input=s)
    assert not result.stderr, result.stderr
    ast=json.loads(result.stdout);meta=ast['meta'];blocks=[]
    blocks.append(styled(meta['title']['c'],'Title'))
    for a in meta.get('author',{}).get('c',[]):blocks.append(styled(a['c'],'Author'))
    blocks.append(styled(meta['date']['c'],'Date'))
    if kind=='main':
        blocks.append({'t':'Header','c':[1,['',[],[]],inline('Abstract')]})
        blocks.extend(meta['abstract']['c'])
    ast['meta']={};ast['blocks']=blocks+ast['blocks']
    # Affiliation markers are ordinary superscripts, not math with an empty base.
    def fix_superscripts(v):
        if isinstance(v,dict):
            if v.get('t')=='Math' and re.fullmatch(r'\^\{[^}]+\}',v['c'][1]):
                return {'t':'Superscript','c':inline(v['c'][1][2:-1])}
            return {k:fix_superscripts(x) for k,x in v.items()}
        if isinstance(v,list):return [fix_superscripts(x) for x in v]
        return v
    ast=fix_superscripts(ast)
    maths=[n['c'][1] for n in walk(ast) if n.get('t')=='Math']
    assert not any(n.get('t')in ['Cite','RawInline','RawBlock'] for n in walk(ast))
    tables=[n for n in ast['blocks'] if n.get('t')=='Table']
    assert len(tables)==len(table_info),(kind,len(tables),len(table_info))
    for info,t in zip(table_info,tables):
        # Table c=[attr,caption,colspecs,head,bodies,foot], row c=[attr,cells].
        rows=t['c'][3][1]+[r for body in t['c'][4] for r in body[3]]+t['c'][5][1]
        info['rows']=[[norm(plain(c[4])) for c in r[1]] for r in rows]
        assert all(info['rows']),info
    images=[n for n in walk(ast) if n.get('t')=='Image']
    assert len(images)==len(figure_info)
    return ast,{'kind':kind,'references':refs,'citation_groups':citations,'cross_references':crossrefs,'tables':table_info,'figures':figure_info,'numbered_equations':equations,'all_math_latex':maths,'xx_count':original.count('XX')},s

def reference_doc():
    d=Document();sec=d.sections[0];sec.page_width=Mm(210);sec.page_height=Mm(297)
    sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Mm(25)
    for name in ['Normal','Body Text','First Paragraph','Author','Date','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption','Table Caption','Image Caption','Bibliography']:
        try:st=d.styles[name]
        except KeyError:
            from docx.enum.style import WD_STYLE_TYPE
            st=d.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
        st.font.name='Times New Roman';st.font.size=Pt(11);st.font.color.rgb=RGBColor(0,0,0)
        st.paragraph_format.line_spacing=2;st.paragraph_format.space_after=Pt(5)
        for e in st.element.xpath('.//w:pBdr'):e.getparent().remove(e)
    for n,size in [('Title',17),('Heading 1',13),('Heading 2',12),('Heading 3',11)]:
        d.styles[n].font.size=Pt(size);d.styles[n].font.bold=True
        d.styles[n].paragraph_format.keep_with_next=True
        d.styles[n].paragraph_format.space_before=Pt(12)
    for n in ['Title','Author','Date']:
        d.styles[n].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
        d.styles[n].paragraph_format.line_spacing=1.2
    d.save(PRIVATE/'reference.docx')
    return PRIVATE/'reference.docx'

def format_doc(path,info):
    d=Document(path);sec=d.sections[0]
    sec.page_width=Mm(210);sec.page_height=Mm(297)
    sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Mm(25)
    sec.header_distance=Mm(12)
    header=sec.header.paragraphs[0];header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');header._p.append(field)
    ln=OxmlElement('w:lnNumType');ln.set(qn('w:countBy'),'1');ln.set(qn('w:restart'),'continuous');ln.set(qn('w:distance'),'220');sec._sectPr.append(ln)
    settings=d.settings.element
    mathpr=settings.find(qn('m:mathPr'))
    if mathpr is None:mathpr=OxmlElement('m:mathPr');settings.append(mathpr)
    mf=mathpr.find(qn('m:mathFont'))
    if mf is None:mf=OxmlElement('m:mathFont');mathpr.insert(0,mf)
    mf.set(qn('m:val'),'STIX Two Math')
    # Use the native underbrace group object; nested limit glyphs are not reliably
    # rendered by LibreOffice. The outer limit with X/Q/S/Delta D is preserved.
    for inner in list(d.element.xpath('.//m:limLow')):
        lim=inner.find(qn('m:lim'));expr=inner.find(qn('m:e'))
        if lim is None or expr is None:continue
        if ''.join(lim.itertext())!='⏟':continue
        group=OxmlElement('m:groupChr');pr=OxmlElement('m:groupChrPr')
        for tag,val in [('chr','⏟'),('pos','bot'),('vertJc','top')]:
            e=OxmlElement('m:'+tag);e.set(qn('m:val'),val);pr.append(e)
        group.append(pr);group.append(copy.deepcopy(expr));inner.getparent().replace(inner,group)
    display=[];inrefs=False;figure_next=0
    for p in d.paragraphs:
        text=p.text.strip();pf=p.paragraph_format;pf.widow_control=True
        if text=='References':inrefs=True
        if p._p.xpath('.//m:oMathPara'):display.append(p)
        if p._p.xpath('.//w:drawing'):
            inrefs=False
            pf.page_break_before=True;pf.keep_with_next=True;pf.line_spacing=1;pf.space_before=Pt(0)
            pf.alignment=WD_ALIGN_PARAGRAPH.CENTER
            fig=info['figures'][figure_next];figure_next+=1
            for node in p._p.xpath('.//wp:docPr'):
                node.set('title','Figure '+fig['number']);node.set('descr',norm(plain_tex(fig['alt_tex'] or fig['caption_tex'])))
        elif re.match(r'^Figure S?\d+\.',text):
            pf.keep_with_next=info['kind']=='main';pf.line_spacing=1.15;pf.space_before=Pt(4)
            for r in p.runs:r.font.size=Pt(10)
        elif text.startswith('Alt text:'):
            pf.keep_with_next=False;pf.line_spacing=1.15
            for r in p.runs:r.font.size=Pt(10)
        elif re.match(r'^Table S?\d+\.',text):
            pf.keep_with_next=True;pf.line_spacing=1.15;pf.space_before=Pt(8)
            if info['kind']!='main' and not text.startswith('Table S9.'):
                pf.page_break_before=True
            for r in p.runs:r.font.size=Pt(10);r.bold=True
        elif inrefs and text and p.style.name!='Heading 1':
            pf.line_spacing=2;pf.left_indent=Mm(5);pf.first_line_indent=Mm(-5);pf.space_after=Pt(7);pf.keep_with_next=False
        if info['kind']!='main' and text in ['GATHER reporting map','Prior questions and the present estimand']:
            pf.page_break_before=True
        if p._p.getprevious() is not None and p._p.getprevious().tag==qn('w:tbl'):
            pf.line_spacing=1.15
            for r in p.runs:r.font.size=Pt(10)
    # Retain exactly the seven original equation numbers; native OMML stays editable.
    assert len(display)==len(info['numbered_equations']),(len(display),info['numbered_equations'])
    for p,eq in zip(display,info['numbered_equations']):
        mathpara=p._p.xpath('.//m:oMathPara')[0];mathnode=mathpara.find(qn('m:oMath'))
        assert mathnode is not None
        mathpara.getparent().remove(mathpara)
        pf=p.paragraph_format;pf.alignment=WD_ALIGN_PARAGRAPH.LEFT;pf.line_spacing=1.5;pf.keep_together=True
        pf.tab_stops.add_tab_stop(Mm(79),WD_TAB_ALIGNMENT.CENTER)
        pf.tab_stops.add_tab_stop(Mm(160),WD_TAB_ALIGNMENT.RIGHT)
        p.add_run('\t');p._p.append(mathnode);p.add_run('\t('+str(eq['number'])+')')
    # Plain scholarly tables; keep editable cells and repeat headings across page breaks.
    assert len(d.tables)==len(info['tables'])
    for idx,(table,tinfo) in enumerate(zip(d.tables,info['tables'])):
        # Pandoc's reference writer can emit Compact/Table style IDs absent from
        # a python-docx reference file. Give both table and cells defined styles;
        # otherwise LibreOffice detaches cell text into following paragraphs.
        table.style='Table Grid'
        table.alignment=WD_TABLE_ALIGNMENT.CENTER;table.autofit=False
        n=len(table.columns)
        if info['kind']=='main':
            widths=[[22,18,28,30,33,29],[24,24,29,29,28,26],[34,43,38,45]][idx]
        else:
            widths=([10,39,111] if idx==0 else [30,55,25,25,25] if idx==2 else [27,22,28,28,28,27] if idx==3 else [28,29,26,26,26,25] if idx==4 else [65,47,48] if idx in [5,7] else [24,43,42,51] if idx==6 else [33,27,28,36,36] if idx==8 else [28,64,68] if idx==9 else [33,20,35,35,37])
        assert len(widths)==n,(idx,n,widths)
        for col,width in zip(table.columns,widths):col.width=Mm(width)
        for rowi,row in enumerate(table.rows):
            trpr=row._tr.get_or_add_trPr();no=OxmlElement('w:cantSplit');trpr.append(no)
            if rowi==0:
                repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
            for ci,(cell,width) in enumerate(zip(row.cells,widths)):
                cell.width=Mm(width);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                pr=cell._tc.get_or_add_tcPr();marg=OxmlElement('w:tcMar')
                for side in ['top','bottom','left','right']:
                    vertical_padding='20' if info['kind']!='main' and idx==2 else '45'
                    e=OxmlElement('w:'+side);e.set(qn('w:w'),vertical_padding if side in ['top','bottom'] else '70');e.set(qn('w:type'),'dxa');marg.append(e)
                pr.append(marg)
                if rowi==0:
                    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'F0F0F0');pr.append(sh)
                for p in cell.paragraphs:
                    p.style='Normal'
                    pf=p.paragraph_format;pf.line_spacing=1.05;pf.space_before=pf.space_after=Pt(0);pf.keep_with_next=(info['kind']=='main' or idx!=2)
                    pf.alignment=WD_ALIGN_PARAGRAPH.LEFT if (ci<=1 or idx in [0,9] and info['kind']!='main') else WD_ALIGN_PARAGRAPH.CENTER
                    for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(9 if idx==2 and info['kind']!='main' else 9.5);r.bold=rowi==0
        borders=OxmlElement('w:tblBorders')
        for side in ['top','left','bottom','right','insideH','insideV']:
            e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
        table._tbl.tblPr.append(borders)
    # Remove template title rules and hyperlinks' theme colours/underlines.
    for st in d.styles:
        if st.type==1:
            st.font.name='Times New Roman'
            st.font.color.rgb=RGBColor(0,0,0)
            for font in st.element.xpath('.//w:rFonts'):
                for attr in list(font.attrib):
                    if attr.endswith('Theme'):del font.attrib[attr]
            for node in st.element.xpath('.//w:pBdr'):node.getparent().remove(node)
    d.save(path)

def plain_tex(tex):
    a=run([PANDOC,'-f','latex','-t','plain'],input=tex)
    return a.stdout.strip()

def build():
    OUT.mkdir(parents=True,exist_ok=True);PRIVATE.mkdir(parents=True,exist_ok=True)
    bp=OUT/'SOURCE_PRESERVATION.json'
    if not bp.exists():save(bp,{str(p.relative_to(ROOT)):sha(p) for p in V4.rglob('*') if p.is_file() and not p.is_relative_to(OUT)})
    ref=reference_doc()
    records={}
    for kind,name in [('main',MAIN),('supplement',SUPP)]:
        ast,info,prepared=prepare(kind)
        (PRIVATE/(kind+'_prepared.tex')).write_text(prepared)
        save(PRIVATE/(kind+'.json'),ast);save(OUT/(kind+'_content_map.json'),info)
        result=run([PANDOC,'-f','json','-t','docx','--reference-doc',ref,'-o',OUT/name],input=json.dumps(ast))
        assert not result.stderr,result.stderr
        format_doc(OUT/name,info)
        records[kind]={'file':name,'math_nodes_expected':len(info['all_math_latex']),'references':len(info['references']),'tables':len(info['tables']),'figures':len(info['figures'])}
    save(OUT/'CONVERSION_PROVENANCE.json',{'at':datetime.now().astimezone().isoformat(),'converter':json.loads((ROOT/'.shared_context_runtime/pandoc_provenance.json').read_text()),'code_sha256':sha(Path(__file__)),'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [SOURCE/'main.tex',SOURCE/'supplement.tex']},'records':records,'math':'Native editable OMML; no equation images','scientific_changes':False,'submitted':False})
    verify()

def verify():
    baseline=json.loads((OUT/'SOURCE_PRESERVATION.json').read_text())
    assert all(sha(ROOT/p)==h for p,h in baseline.items()),'An existing v4 artifact changed'
    qc={}
    for kind,name in [('main',MAIN),('supplement',SUPP)]:
        info=json.loads((OUT/(kind+'_content_map.json')).read_text())
        d=Document(OUT/name)
        with zipfile.ZipFile(OUT/name) as z:
            xml=etree.fromstring(z.read('word/document.xml'));xmlall=etree.tostring(xml).decode()
            maths=xml.xpath('//m:oMath',namespaces=NS)
            assert len(maths)==len(info['all_math_latex']),(kind,len(maths),len(info['all_math_latex']))
            assert xmlall.count('XX')==info['xx_count'],(kind,xmlall.count('XX'),info['xx_count'])
            assert len(xml.xpath('//wp:docPr',namespaces=NS))==len(info['figures'])
            # Every image is the exact source PNG, not a recreated chart.
            media=[z.read(n) for n in z.namelist() if n.startswith('word/media/')]
            assert sorted(hashlib.sha256(b).hexdigest() for b in media)==sorted(f['sha256'] for f in info['figures'])
            assert not re.search(r'\\(?:citep|begin|end|frac|sum|ref)\b',xml_text(xml))
            assert xml.xpath('//w:lnNumType[@w:restart="continuous"]',namespaces=NS)
            ast=json.loads((PRIVATE/(kind+'.json')).read_text())
            expected_nonmath=re.sub(r'\s+','',nonmath_stream(ast['blocks']))
            # Ignore only the seven added equation-label runs, not issue numbers
            # such as 52(2) in a bibliographic entry.
            actual_nonmath=''.join(t for t in xml.xpath('//w:t/text()',namespaces=NS) if not re.fullmatch(r'\([1-7]\)',t))
            actual_nonmath=re.sub(r'\s+','',actual_nonmath)
            assert expected_nonmath==actual_nonmath,(kind,'non-math text changed')
        assert len(d.tables)==len(info['tables'])
        rows_checked=0
        for t,ti in zip(d.tables,info['tables']):
            got=[[norm(xml_text(c._tc)) for c in r.cells] for r in t.rows]
            # Native mathematical header tokens contain equivalent Greek text.
            clean=lambda s:re.sub(r'\\Delta\s*','Δ',s).replace('$','')
            assert [[clean(c) for c in r] for r in got]==[[clean(c) for c in r] for r in ti['rows']],(kind,ti['number'],got[:2],ti['rows'][:2])
            rows_checked+=len(got)-1
        alltext=xml_text(xml)
        if kind=='main':
            assert all(plain_tex(r['tex']).replace('\n',' ')[:40] in alltext for r in info['references'])
            assert all(doi in alltext for doi in re.findall(r'doi:(10\.[^}\s]+)',(SOURCE/'main.tex').read_text()))
            assert all('('+str(i)+')' in alltext for i in range(1,8))
        # Inverse conversion proves the document contains machine-readable mathematics.
        inverse=json.loads(run([PANDOC,'-f','docx','-t','json',OUT/name]).stdout)
        recovered=[n['c'][1] for n in walk(inverse) if n.get('t')=='Math']
        assert len(recovered)==len(maths)
        qc[kind]={'sha256':sha(OUT/name),'native_editable_math_objects':len(maths),'numbered_equations':len(info['numbered_equations']),'math_recovered_by_docx_reader':len(recovered),'all_nonmath_text_exact_after_whitespace_normalization':True,'nonmath_characters_verified':len(actual_nonmath),'references':len(info['references']),'editable_tables':len(d.tables),'body_table_rows_exactly_verified':rows_checked,'source_pngs_byte_identical':len(media),'xx_occurrences_preserved':info['xx_count'],'continuous_line_numbers':True,'right_header_page_field':True}
        save(OUT/(kind+'_math_roundtrip.json'),{'source_latex':info['all_math_latex'],'recovered_latex':recovered,'omml_text':[''.join(m.xpath('.//m:t/text()',namespaces=NS)) for m in maths]})
    save(OUT/'CONVERSION_QC.json',{'at':datetime.now().astimezone().isoformat(),'documents':qc,'existing_v4_files_preserved':len(baseline),'visual_inspection':'pending','submitted':False})
    print(json.dumps(qc,indent=2))

def package():
    files=[p for p in OUT.iterdir() if p.is_file() and p.suffix!='.zip']+[Path(__file__).resolve()]
    save(OUT/'WORD_DELIVERY_MANIFEST.json',{'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)],'restricted_raw_data_included':False,'old_tex_pdf_modified':False})
    files.append(OUT/'WORD_DELIVERY_MANIFEST.json')
    with zipfile.ZipFile(OUT/'PCOS_HumanReproduction_v4_Word_Complete.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(set(files)):z.write(p,p.relative_to(ROOT))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['build','verify','package']);ap.add_argument('--pandoc',type=Path);a=ap.parse_args()
    if a.pandoc:PANDOC=a.pandoc
    {'build':build,'verify':verify,'package':package}[a.action]()
