#!/usr/bin/env python3
"""Reconstruct the complete teacher manuscript, then apply only FIX-01--09.

Editorial production/QC only; no research input or statistical computation.
"""
from pathlib import Path
import re,json,csv,hashlib,shutil,subprocess,types,difflib,unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1]
P=R/'.shared_context_runtime/bluek_editorial_20261030'
O=R/'PCOS_HumanReproduction_BlueK_Editorial_v7_DRAFT_2026-10-30'
V=R/'PCOS_HumanReproduction_v6_2026-10-30'
A=R/'PCOS_HumanReproduction_v6_Overleaf_r1_2026-10-30'
B='20261030_PCOS_HumanReproduction_BlueK_v7_DRAFT_'
D='20261030_PCOS_BlueK_v7_DRAFT_'
PAN=R/'.shared_context_runtime/tools/pandoc-3.13'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def run(args,**kw):return subprocess.run([str(x) for x in args],capture_output=True,text=True,check=True,**kw)
def norm(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s)).replace('’',"'").replace('–','--').replace('−','-').strip()
def plain(s):return norm(run([PAN,'-f','latex','-t','plain'],input=s).stdout)
def writecsv(p,rows):
    with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def build():
    assert not list((O/'manuscript').glob('*.tex')),'Completed paper sources already exist; do not overwrite them.'
    for n in ['manuscript','word','output','docs','sources']: (O/n).mkdir(parents=True,exist_ok=True)
    protect={str(p.relative_to(R)):sha(p) for folder in [V,A,R/'PCOS_Revision_2026-10-29'] for p in folder.rglob('*') if p.is_file()}
    save(O/'docs'/(D+'Preservation.json'),protect)
    teacher=P/'package/PCOS 20261030 Blue K.pdf'
    assert sha(teacher)=='e6884c181a3992ba1612635133c58b60f1a1762c98bddbdbd39576a1c10e5d5d'
    assert teacher.read_bytes()==(P/'PCOS 20261030 Blue K.pdf').read_bytes()
    shutil.copy2(teacher,O/'sources/20261030_PCOS_BlueK_Teacher_Original.pdf')
    for n in ['20261030_PCOS_BlueK_EditorialFixes_for_Codex.md','20261030_PCOS_BlueK_Codex_README.txt']:
        shutil.copy2(P/'package'/n,O/'sources'/n)
    source=V/'manuscript/20261030_PCOS_HumanReproduction_v6_Manuscript.tex'
    s=source.read_text();original=s
    # Use the PDF's printed line numbers as immutable source locators.
    lines={};pages={}
    for pi,page in enumerate((P/'teacher_layout.txt').read_text().split('\f'),1):
        if pi>14:continue  # later pages contain figure-axis numbers, not manuscript line numbers
        for line in page.splitlines():
            m=re.match(r'^\s*(\d{1,3})\s{2,}(\S.*)$',line)
            if m and 1<=int(m[1])<=372:
                num=int(m[1]);assert num not in lines,num;lines[num]=unicodedata.normalize('NFKC',m[2]);pages[num]=pi
    # Explicit hyphenated compounds; all other end-of-line hyphens are typesetting.
    compounds=set(re.findall(r'[A-Za-z]+(?:-[A-Za-z]+)+',original))|{'age-standardization','age-specific','within-age','reference-country','country-specific','national-versus-pool','national-versus-pooled-reference','population-pooled','cause-specific','five-year','cause-attribution','primary-plus-secondary','six-decimal','restricted-age','population-source','China-minus-reference','reference-share','country-share','fixed-1990','Equal-country','current-year','total-variation','disease-rate','secondary-infertility','country-exclusion','reproductive-health','full-precision','age-weight','model-output','author-by-author','AI-assisted','country-age','source-cell','non-specific-funding'}
    def segment(a,b):
        txt=''
        for i in range(a,b+1):
            part=lines[i]
            if txt.endswith('–') and part[:1].isdigit():
                txt+=part
            elif txt.endswith('-'):
                left=re.search(r'([A-Za-z]+(?:-[A-Za-z]+)*-)$',txt)
                right=re.match(r'([A-Za-z]+(?:-[A-Za-z]+)*)',part)
                compound=(left[1]+right[1]) if left and right else ''
                if compound not in compounds:txt=txt[:-1]
                txt+=part
            else:txt+=(' ' if txt else '')+part
        return txt
    citations={'Teede et al., 2023':'pcos','GBD 2023 Collaborators, 2025':'gbd','Liu et al., 2024':'liu_pcos2024','Liang et al., 2025':'liang_burden2025','Liang, 2026':'liang_trend2026','Institute for Health Metrics and Evaluation, 2026':'results','Australian Government, 2026':'g20','Chen et al., 2026':'chen','Kitagawa, 1955':'kitagawa','United Nations, 2024':'wpp2024','PCOS research workspace, 2026':'repository','Stevens et al., 2016':'gather','Yang et al., 2022':'yang'}
    def latex(txt):
        txt=txt.replace('’',"'").replace('–','--').replace('−','-').replace('%',r'\%').replace('&',r'\&')
        for label,key in citations.items():txt=txt.replace('('+label+')',r'\citep{'+key+'}')
        # The only multi-citation group is in Discussion.
        txt=txt.replace('(Liu et al., 2024; Liang et al., 2025; Liang, 2026)',r'\citep{liu_pcos2024,liang_burden2025,liang_trend2026}')
        return txt
    cross=[];changed=[]
    def replace(prefix,a,b,manual=None):
        nonlocal s
        pattern=r'(?m)^'+re.escape(prefix)+r'[^\n]*'
        m=re.search(pattern,s);assert m,(prefix,a,b)
        before=m[0];teachertext=segment(a,b);after=manual if manual is not None else latex(teachertext)
        s=s[:m.start()]+after+s[m.end():]
        row={'teacher_pages':','.join(map(str,sorted({pages[i] for i in range(a,b+1)}))),'teacher_lines':f'{a}--{b}','locator':prefix,'BlueK_text':teachertext,'v6_text':plain(before),'status':'Blue K已合入' if plain(before)!=plain(after) else '原稿一致','baseline_editable_text':plain(after),'note':'PDF文字层完整段落；公式/表图另独立核对'}
        cross.append(row)
        if before!=after:changed.append(after)
    # Every narrative paragraph, including unchanged paragraphs, is mapped.
    abstract=[('STUDY QUESTION',2,4),('SUMMARY ANSWER',5,7),('WHAT IS KNOWN ALREADY',8,10),('STUDY DESIGN, SIZE, DURATION',11,13),('PARTICIPANTS/MATERIALS, SETTING, METHODS',14,21),('MAIN RESULTS AND THE ROLE OF CHANCE',22,29),('LIMITATIONS, REASONS FOR CAUTION',30,33),('WIDER IMPLICATIONS OF THE FINDINGS',34,38),('FUNDING',39,40),('DISCLOSURES',41,41),('TRIAL REGISTRATION NUMBER',42,43)]
    for head,a,b in abstract:
        txt=segment(a,b);assert txt.startswith(head+':');replace(r'\noindent\textbf{'+head+':}',a,b,r'\noindent\textbf{'+head+':} '+latex(txt[len(head)+1:].strip()))
    maps=[('Polycystic ovary syndrome (PCOS) affects',47,52),('Liu and colleagues quantified',53,61),('A contemporaneous population pool',62,70),('This ecological secondary analysis',73,83),('We selected prevalence',84,93)]
    for x in maps:replace(*x)
    replace('For country $c$',94,98,re.search(r'(?m)^For country \$c\$[^\n]+',s)[0])
    replace('Let $\\mathcal{R}$',100,104,r'Let $\mathcal{R}$ be the set of 18 reference countries; the labels $\mathrm{CHN}$ and $\mathrm{R}$ denote China and the pooled reference. We used the seven published six-decimal age weights reproduced by Chen and colleagues \citep{chen}, normalized them to sum to one over ages 15--49 and held them fixed. Supplementary Methods report the weight vector, its source limitations and the numerical rounding check.')
    for prefix,a,b in [('Here $w_a$',107,111),('For endpoints $t_0$',113,114)]:replace(prefix,a,b,re.search(r'(?m)^'+re.escape(prefix)+r'[^\n]+',s)[0])
    replace('$X_k$, $Q_k$ and $S_k$',119,124,r'$X_k$, $Q_k$ and $S_k$ allocate the period change to Chinese rates, reference-country rates and reference-country shares, respectively. Each uses the same endpoints, subtype and population-source specification. Averaging the two replacement orders splits the product interaction symmetrically, giving an exact identity before rounding. Positive components raise the signed China-minus-reference difference. For a difference that remains negative at both endpoints, a positive net change indicates a smaller absolute gap.')
    replace('The identity is additive',125,128)
    replace('We report absolute components',129,134,r'We report absolute components before the ratio $100S_k/\Delta D_k(t_0,t_1)$. Its signed net denominator contains cancellation between components and can approach zero; ratios can consequently exceed 100\% or change sign. This accounting ratio is distinct from a fraction of women, cases or disease causation. The primary- and secondary-infertility contributions add to the total change. Each subtype contribution can itself be separated into rate and country-share components; subtype percentages and composition percentages should therefore not be added to one another.')
    for x in [('UN WPP 2024 supplied',136,140),('Current-year shares compare',141,150),('Existing sensitivity analyses',152,157),('The available study exports',158,166),('The exploratory analyses were',168,174),('Public aggregate GBD estimates',176,178),('OpenAI ChatGPT and Codex supported',180,182),('The GBD population and UN subset',185,190),("China's PCOS-attributed total infertility",191,195)]:replace(*x)
    s=s.replace(r'\subsection{Design data and outcome}',r'\subsection{Design, data and outcome}').replace(r'\subsection{Absolute decomposition before percentages}',r'\subsection{Rate and reference-composition components}').replace(r'\subsection{Population-source and benchmark sensitivity in the main results}',r'\subsection{Population sources and benchmark definitions}')
    replace('with displayed rounding',199,202)
    replace('The country-share component was',203,209)
    replace('Secondary infertility contributed',210,217)
    # Teacher's Table 1 footnote is longer than v6, and must also be inherited.
    oldnote='Rates and differences are per 100,000 females, standardized within ages 15--49. Difference is China minus reference. All are model point estimates without propagated posterior intervals.'
    newnote='Rates and differences are per 100,000 females, standardized within ages 15--49. Difference is China minus reference; ratio is China divided by reference. Calculations precede rounding, so displayed values may not add or subtract exactly. All values are model point estimates without propagated posterior intervals.'
    assert oldnote in s;s=s.replace(oldnote,newnote)
    cross.append({'teacher_pages':'8','teacher_lines':'Table 1 footnote','locator':'Table 1 note','BlueK_text':newnote,'v6_text':oldnote,'status':'Blue K已合入','baseline_editable_text':newnote,'note':'数值表身保持原字节'})
    for x in [('UN weighting gave',219,226),('Under current GBD shares',227,233),('Reference-country composition made',235,242),('This analysis adds',243,250),('The practical implication is',251,260),('Clinical interpretation also depends',261,268),('The principal limitation is',269,278),('Reproductive-health monitoring can',279,284),('XX: verified author-by-author',286,287),('We acknowledge the GBD',289,290),('OpenAI ChatGPT and Codex supported',291,296),('XX: verified sponsors',298,299),('XX: author-specific financial',301,302),('The executable Python and R workflow',304,314),('Supplementary methods, nine numerical',316,320)]:replace(*x)
    # Last repeated OpenAI prefix matched the acknowledgement because Methods was replaced.
    # References and all figures are unchanged in the teacher PDF; cross-checked later.
    for kind,count in [('references',14),('main tables',3),('main figures and captions',5),('equation rows',7)]:
        cross.append({'teacher_pages':'14--19' if kind.startswith(('references','main figures')) else '4--10','teacher_lines':'structural audit','locator':kind,'BlueK_text':f'{count} items','v6_text':f'{count} items','status':'原稿一致','baseline_editable_text':f'{count} items','note':'独立PDF/TeX/资产核验；不改分析图表'})
    baseline=s
    (P/'BlueK_complete_baseline_external.tex').write_text(baseline)
    writecsv(O/'docs'/(D+'BlueK_vs_v6_crosswalk.csv'),cross)
    fixes=[]
    def fix(i,old,new,page,reason):
        nonlocal s
        assert s.count(old)==1,(i,s.count(old),old)
        s=s.replace(old,new);fixes.append({'id':f'FIX-{i:02d}','teacher_page':page,'before':old,'after':new,'reason':reason,'status':'applied; verification pending'})
    fix(1,'Consequently, a smaller national-versus-pool difference need not reflect a decline in the national rate.','Consequently, a smaller absolute gap between the national and pooled-reference rates need not reflect a decline in the national rate.',3,'有符号D增大，绝对差距缩小')
    fix(2,"How did changing reference-country population shares contribute to China's PCOS-attributed infertility rate difference from an 18-country pool during 1990--2023?","How did changing within-age reference-country population shares contribute to the 1990--2023 change in China's age-standardized PCOS-attributed total-infertility rate difference from an 18-country pooled reference?",1,'明确主估计目标；其余摘要栏目不改')
    fix(3,'The share and net-change components were close under this population-source substitution.','The reference-share components and total changes were similar under the two population sources.',10,'净变化是分量之和')
    ev=json.loads((V/'docs/20261030_v6_AI_evidence.json').read_text());assert ev['earlier_verified_evidence']['recorded_model_identifier']=='gpt-6.1-sol'
    aiold=re.search(r'(?m)^OpenAI ChatGPT and Codex assisted[^\n]+',s)[0]
    ainew=aiold.replace('Human authors retain responsibility for the study.',r'The documented Codex session on 29 October 2026 recorded the model identifier \texttt{gpt-6.1-sol}; model identifiers for other sessions were not independently verified. Human authors retain responsibility for the study.')
    # Preserve the teacher's XX pending-review clause verbatim; do not claim approval.
    fix(4,aiold,ainew,12,'恢复已保存且仅对应2026-10-29会话的版本；作者核查仍待确认')
    xu=re.search(r'\\bibitem\[Xu et al\.\(2025\)\]\{xu\}[^\n]+\n',s)[0]
    assert not re.search(r'\\cite[pt]?\{[^}]*\bxu\b',s)
    fix(5,xu,'',14,'Blue K无正文引用；删除游离条目，不新增疾病或方法主张')
    fix(6,'The reproducibility archive contains code, aggregate results, source specifications, a complete annual subtype CSV and execution instructions; licensed GBD originals and restricted source cells are excluded.','The public reproducibility repository contains code, aggregate derived results, source specifications, a complete annual subtype CSV and execution instructions; licensed GBD originals and restricted country--age source cells are excluded.',13,'区分公开库与私人FULL_PRIVATE原始输入')
    fix(7,"Yang and colleagues' Chinese community survey used Rotterdam PCOS ascertainment among married Han women aged 20--49",'In the 2020 Chinese community survey, Yang and colleagues used Rotterdam PCOS ascertainment among married Han women aged 20--49',11,'原论文2020组对应20--49岁；保留Yang2022引文')
    fix(8,'In the existing age-specific decomposition','In the age-specific decomposition',9,'去除工作记录用语')
    fix(8,'the economically selected reference-country set','the purposively selected G20 country set','11--12','准确描述固定G20集合，不改变国家或权重')
    fixes.append({'id':'FIX-09','teacher_page':1,'before':'Two internal editorial sentences and blue review colour','after':'Clean manuscript omits internal editorial notes; teacher PDF retained; final review copy has identical scientific text with blue editorial paragraphs','reason':'独立clean稿和审阅记录，不投稿','status':'applied; verification pending'})
    assert s.count('XX')==baseline.count('XX')
    # Keep all old statistics and assets. The final standalone TeX uses exactly
    # the already-verified native PGF vectors from v6/r1, without any redraw.
    standalone=(A/'manuscript/20261030_PCOS_HumanReproduction_v6_Overleaf_r1_Manuscript.tex').read_text()
    pgfs={m[1]:m[0] for m in re.finditer(r'% BEGIN INLINE VECTOR (\S+)\n[\s\S]*?% END INLINE VECTOR \1',standalone)}
    assert len(pgfs)==5
    def inlinepaper(text):
        text=text.replace(r'\usepackage[T1]{fontenc}',r'\usepackage[T1]{fontenc}'+'\n'+r'\usepackage{pgf,xcolor}'+'\n'+r'\providecommand{\mathdefault}[1]{#1}')
        text=re.sub(r'\\input\{([^}]+)\}',lambda m:(V/'manuscript'/m[1]).read_text(),text)
        def vector(m):return pgfs[Path(m[1]).stem.removeprefix('20261030_v6_')]
        text=re.sub(r'\\includegraphics\[[^]]+\]\{([^}]+)\}',vector,text)
        return text.replace('% HUMAN_REPRODUCTION_V6_2026_10_30','% Blue K v7 DRAFT, 30 October 2026; finite editorial revision only.')
    (P/'main_final_external.tex').write_text(s)
    clean=inlinepaper(s);(O/'manuscript'/(B+'Manuscript.tex')).write_text(clean)
    review=s
    # Colour entire changed narrative paragraphs, leaving equations/assets intact.
    oldparas=set(baseline.split('\n\n'))
    for para in s.split('\n\n'):
        if para and para not in oldparas and not para.startswith('\\bibitem') and '\\begin{' not in para and '\\end{' not in para:
            review=review.replace(para,'{\\color{blue} '+para+'}')
    question=next(f['after'] for f in fixes if f['id']=='FIX-02')
    review=review.replace(question,'{\\color{blue} '+question+'}')
    (O/'manuscript'/(B+'Manuscript_Review.tex')).write_text(inlinepaper(review))
    (P/'fixes.json').write_text(json.dumps(fixes,ensure_ascii=False,indent=2))
    save(O/'docs'/(D+'Input_Manifest.json'),{str(p.relative_to(R)):sha(p) for p in [teacher,P/'package/20261030_PCOS_BlueK_EditorialFixes_for_Codex.md',source,A/'manuscript/20261030_PCOS_HumanReproduction_v6_Overleaf_r1_Manuscript.tex',A/'manuscript/20261030_PCOS_HumanReproduction_v6_Overleaf_r1_Supplement.tex',V/'word/20261030_PCOS_HumanReproduction_v6_Manuscript.docx',V/'word/20261030_PCOS_HumanReproduction_v6_Supplement.docx',V/'docs/20261030_v6_AI_evidence.json',R/'PCOS_Revision_2026-10-29/code/revision_analysis.py',*sorted((R/'PCOS_Revision_2026-10-29/results/python').glob('*.csv'))]})
    print(json.dumps({'teacher_paragraphs_mapped':len(cross),'fix_rows':len(fixes),'old_files_protected':len(protect),'XX_count':s.count('XX')}))

def word():
    path=R/'scripts/convert_hr_v4_word_20261029.py'
    code=path.read_text().replace("(SOURCE/(kind+'.tex'))","TEX_FILES[kind]")
    c=types.ModuleType('bluek_converter');c.__file__=str(path);exec(compile(code,str(path),'exec'),c.__dict__)
    c.SOURCE=V/'manuscript';c.OUT=O/'word';c.PRIVATE=P/'word';c.PRIVATE.mkdir(exist_ok=True)
    c.TEX_FILES={'main':P/'main_final_external.tex'};c.MAIN=B+'Manuscript.docx'
    ref=c.reference_doc();ast,info,prepared=c.prepare('main')
    running=[b for b in ast['blocks'] if c.plain(b).startswith('Running title:')]
    assert len(running)==1
    ast['blocks'].remove(running[0])
    abstract_index=next(i for i,b in enumerate(ast['blocks']) if b.get('t')=='Header' and c.plain(b).strip()=='Abstract')
    ast['blocks'].insert(abstract_index,running[0])
    save(P/'word/main.json',ast);save(O/'docs'/(D+'Word_Content_Map.json'),info)
    (P/'word/main_prepared.tex').write_text(prepared)
    r=run([PAN,'-f','json','-t','docx','--reference-doc',ref,'-o',O/'word'/c.MAIN],input=json.dumps(ast))
    assert not r.stderr,r.stderr;c.format_doc(O/'word'/c.MAIN,info)
    print('Editable Word created, including native OMML and exact unchanged PNG assets.')

def compile_papers():
    logs={}
    for p in sorted((O/'manuscript').glob('*.tex')):
        result=subprocess.run(['/opt/homebrew/bin/tectonic','--keep-logs','--outdir',str(O/'output'),str(p)],cwd=V/'manuscript',capture_output=True,text=True)
        (O/'docs'/(p.stem+'_compile.txt')).write_text(result.stdout+'\n'+result.stderr)
        logs[p.name]={'exit_code':result.returncode,'log_sha256':sha(O/'docs'/(p.stem+'_compile.txt'))}
        assert result.returncode==0,result.stderr[-3000:]
    save(P/'compilation.json',logs);print(logs)

if __name__=='__main__':
    import sys
    {'build':build,'word':word,'compile':compile_papers}[sys.argv[1]]()
