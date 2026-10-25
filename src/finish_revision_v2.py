"""Finish candidate formats, compile and package without submitting a manuscript."""
from pathlib import Path
import re,json,subprocess,urllib.parse,unicodedata,hashlib,zipfile,shutil
ROOT=Path(__file__).resolve().parents[1];M=ROOT/'manuscript';O=ROOT/'output/revision_v2';O.mkdir(parents=True,exist_ok=True)
assert json.loads((ROOT/'results/external/independent_R_verification.json').read_text())['passed']
# Obtain registered author metadata from the exact cited DOI. Failed requests are logged.
doim={'pcos':'10.1210/clinem/dgad463','eshre':'10.1093/hropen/hoac009','xu':'10.1111/jebm.70100','lu':'10.3760/cma.j.cn112338-20250929-00691','wang':'10.1186/s10020-026-01548-8','feng':'10.1186/s12978-025-01966-7','chen':'10.1371/journal.pone.0351539','gather':'10.1371/journal.pmed.1002056'}
meta={};authors={};src=ROOT/'sources/revision_v2';src.mkdir(parents=True,exist_ok=True)
def esc(s):
 return s.replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
for key,doi in doim.items():
 url='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')
 cp=subprocess.run(['curl','--fail','--location','--connect-timeout','10','--max-time','25',url],capture_output=True,text=True)
 try:
  j=json.loads(cp.stdout)['message'];assert j['DOI'].lower()==doi.lower()
  names=[]
  for x in j.get('author',[])[:10]:
   if x.get('family'):
    initials=''.join(t[0].upper() for t in re.split(r'[\s-]+',x.get('given','')) if t)
    names.append(x['family']+' '+initials)
   elif x.get('name'):names.append(x['name'])
  if len(j.get('author',[]))>10:names.append('et al')
  if names:authors[key]=esc(', '.join(names))+'. '
  meta[key]={'doi':doi,'url':url,'title':j.get('title'),'authors':j.get('author',[]),'status':'verified DOI registration metadata'}
 except Exception as ex:meta[key]={'doi':doi,'url':url,'status':'not retrieved; existing reference retained','error':str(ex)[:150]}
(src/'reference_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
for file in ['main','human_reproduction']:
 p=M/f'{file}.tex';s=p.read_text()
 def update(m):
  opening,key,value=m.groups()
  if key in authors and '. ' in value:value=authors[key]+value.strip().split('. ',1)[1]
  return opening+value
 s=re.sub(r'(\\bibitem(?:\[[^\]]+\])?\{([^}]+)\})(.*?)(?=\\bibitem|\\end\{thebibliography\})',update,s,flags=re.S)
 p.write_text(s)
hr=(M/'human_reproduction.tex').read_text()
abstract=r'''\section*{Extended abstract}
\textbf{Study question:} How do reference composition, infertility subtype and outcome/denominator definitions affect the interpretation of PCOS and endometriosis infertility comparisons?

\textbf{Summary answer:} Reference-country shares explained a substantial part of the modeled China--G20 PCOS contrast change, while a separate survey showed that diagnosis-associated estimates varied with definitions and denominators.

\textbf{What is known already:} GBD studies describe infertility burden, trends and subtypes. Age standardization does not fix country composition within a pooled reference, and survey definitions are not interchangeable.

\textbf{Study design, size, duration:} Ecological secondary analysis of GBD 2023, 1990--2023, covering 19 sovereign G20 countries and seven female age groups, plus a post hoc cross-sectional NSFG 2022--2023 analysis with 4,855 respondents aged 20--49 at interview.

\textbf{Participants/materials, setting, methods:} China was compared with 18 other countries using pooling within age, restricted-age standardization, subtype accounting and symmetric endpoint decomposition, with annual-chained sensitivity. NSFG analysis used final weights, 20 strata and 80 clusters, preserving joint Taylor covariance. Independent R and Python implementations checked estimates and covariance.

\textbf{Main results and the role of chance:} The PCOS-related infertility contrast narrowed by 151.54 per 100,000; reference composition contributed 88.65 (58.5\%), compared with 87.11 (57.5\%) under annual chaining. Secondary infertility accounted for 69.4\%. These GBD quantities lack propagated uncertainty. Survey prevalence ratios for broad fertility problems versus 12-month infertility in unions were 2.65 (95\% design CI 2.30--3.04) versus 1.77 (1.22--2.57) for PCOS, and 1.78 (1.40--2.25) versus 0.84 (0.50--1.43) for endometriosis. The paired within-union PCOS definition shift in prevalence differences was 17.15 percentage points (10.24--24.06).

\textbf{Limitations, reasons for caution:} No jointly aligned GBD draws were obtained. Survey associations are unadjusted and partly sparse; the narrow endometriosis interval crosses one. Definitions and populations differ, and NSFG is not a proven held-out GBD validation sample. Several analyses were post hoc; endometriosis terminal-year instability is unresolved.

\textbf{Wider implications of the findings:} Comparisons should distinguish subtype, reference composition, definitions and denominators. Neither convergence nor definition-sensitive associations demonstrate improved care, disease causation or a protective endometriosis effect.

\textbf{Study funding/disclosures:} Actual human-author funding and disclosures remain to be verified; none are assumed.

\textbf{Trial registration number:} Not applicable; no interventional trial or external preregistration is claimed.

\textbf{Key words:} infertility; PCOS; endometriosis; reference population; survey design
'''
(M/'sections/human_reproduction_abstract.tex').write_text(abstract)
hr=re.sub(r'\\begin\{abstract\}.*?(?=\\section\{Introduction\})',lambda _:r'\input{sections/human_reproduction_abstract.tex}'+'\n',hr,count=1,flags=re.S)
hr=hr.replace(r'\fancyhead[R]{\small Human Reproduction candidate}\fancyfoot[C]{\thepage}',r'\fancyhead[R]{\thepage}\fancyfoot[C]{\small Human Reproduction candidate}')
hr=hr.replace(r'\date{25 October 2026}',r'\date{25 October 2026\\{\small Running title: Interpreting infertility comparisons}}')
hr=hr.replace(r'\subsection{Use of artificial intelligence}',r'\subsection{Ethical considerations}'+'\n'+r'Aggregate GBD estimates and deidentified public-use NSFG records were analysed without new recruitment or identifiable linkage. The research team must document the applicable institutional determination before submission; no approval or waiver is invented.'+'\n'+r'\subsection{Use of artificial intelligence}')
a=hr.index(r'\section*{Declarations}');b=hr.index(r'\section*{Additional files}',a)
parts=dict(re.findall(r'\\subsection\*\{([^}]+)\}(.*?)(?=\\subsection\*|\Z)',hr[a:b],flags=re.S))
new=''
for h in ["Authors' contributions",'Acknowledgements','Funding','Competing interests','Availability of data and materials','Ethics approval and consent to participate','Consent for publication']:
 if h in parts:
  title={"Authors' contributions":"Authors' roles",'Competing interests':'Disclosures'}.get(h,h)
  new+=r'\section*{'+title+'}'+parts[h]+'\n'
hr=hr[:a]+new+hr[b:]
alt={'trends':'Annual rates and China-minus-reference contrasts. PCOS rates rise while the negative contrast narrows. Endometriosis is endpoint-sensitive.','strata':'Primary and secondary trajectories differ and can cancel in the total contrast.','composition':'Signed rate and country-share components sum to contrast changes. Country composition contributes materially to PCOS.','nsfg':'Six survey prevalence ratios with intervals. The narrow endometriosis interval crosses one; no protective association is established.'}
for label,text in alt.items():hr=hr.replace(r'\label{fig:'+label+r'}\end{figure}',r'\label{fig:'+label+r'}\par\smallskip{\footnotesize\textit{Alt text:} '+text+r'}\end{figure}')
(M/'human_reproduction.tex').write_text(hr)
# Keep old supplementary floats from interrupting new methods.
s=(M/'supplement.tex').read_text().replace(r'\usepackage[hidelinks]{hyperref}',r'\usepackage{placeins}'+'\n'+r'\usepackage[hidelinks]{hyperref}')
s=s.replace(r'\input{sections/revision_supplement.tex}',r'\FloatBarrier'+'\n'+r'\input{sections/revision_supplement.tex}')
(M/'supplement.tex').write_text(s)
B=ROOT/'output/build_v2';B.mkdir(parents=True,exist_ok=True)
for name,dest in [('main','PCOS_Reproductive_Health_integrated_v2.pdf'),('supplement','PCOS_Additional_file_1_v2.pdf'),('human_reproduction','PCOS_Human_Reproduction_candidate_v2.pdf')]:
 for n in range(3):
  cp=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={B}',name+'.tex'],cwd=M,capture_output=True,text=True)
  (B/f'{name}_pass{n+1}.txt').write_text(cp.stdout+cp.stderr)
  if cp.returncode:raise RuntimeError('Compile failed: '+name)
 log=(B/f'{name}.log').read_text(errors='replace')
 if re.search('undefined references|Citation.*undefined|Reference.*undefined',log):raise AssertionError('Unresolved references')
 shutil.copy2(B/f'{name}.pdf',O/dest)
with zipfile.ZipFile(O/'PCOS_manuscript_TeX_sources_v2.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in M.rglob('*'):
  if p.is_file() and p.suffix in ['.tex','.pdf','.txt']:z.write(p,p.relative_to(ROOT))
with zipfile.ZipFile(O/'PCOS_Additional_file_2_code_results_v2.zip','w',zipfile.ZIP_DEFLATED) as z:
 for folder in ['src','tests','config','docs','results/tables','results/external','sources/revision_v2']:
  for p in (ROOT/folder).rglob('*'):
   if p.is_file() and '__pycache__' not in str(p):z.write(p,p.relative_to(ROOT))
manifest={'version':'integrated_v2_repository','submitted':False,'GBD_joint_draws':'not obtained; no propagated derived GBD intervals','NSFG_joint_covariance':'computed; independently reconstructed in R and Python','files':[],'visual_layout':'requires final local rendered review; compilation alone is not visual validation','remaining_human_items':['authorship and affiliations','corresponding ORCID','ethics determination','funding/conflicts','all-author approval','permanent archive DOI']}
for p in sorted(O.glob('*')):
 if p.is_file():manifest['files'].append({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(O/'artifact_manifest_v2.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
