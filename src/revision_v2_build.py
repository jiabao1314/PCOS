"""Reproduce external survey estimates and integrate them into the archived draft.

All computations use real CDC public-use data. No GBD posterior draws are invented.
Run from the repository root after obtaining the source files specified below.
"""
from pathlib import Path
import json, re, subprocess, hashlib, sys, shutil
import numpy as np
import pandas as pd
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator, NullFormatter

ROOT=Path(__file__).resolve().parents[1]
M=ROOT/'manuscript'; OUT=ROOT/'results/external'; OUT.mkdir(parents=True,exist_ok=True)
S=M/'sections';S.mkdir(exist_ok=True)
R=OUT/'Rcheck'
e=pd.read_csv(R/'independent_R_estimates.csv').set_index('estimate_id')
v=pd.read_csv(R/'independent_R_joint_covariance.csv',index_col=0).loc[e.index,e.index]
assert len(e)==36 and set(e.df)=={60}
assert np.allclose(np.diag(v),e.se**2,atol=1e-12)
crit=t.ppf(.975,60)
contrasts=[]; vecs={}
for scope in ['strict_20_49','sampled_20plus']:
 for dis in ['ENDO','PCOS']:
  for out in ['current_problems_all','current_problems_union','infertility12_union','ever_services_all']:
   a=f'{scope}_{dis}_{out}_diagnosed';b=f'{scope}_{dis}_{out}_not_diagnosed'
   g=np.zeros(len(e));g[e.index.get_loc(a)]=1;g[e.index.get_loc(b)]=-1
   gl=g.copy();gl[e.index.get_loc(a)]=1/e.loc[a,'p'];gl[e.index.get_loc(b)]=-1/e.loc[b,'p']
   diff=float(g@e.p);sd=float(np.sqrt(g@v@g));rr=float(e.loc[a,'p']/e.loc[b,'p']);sr=float(np.sqrt(gl@v@gl))
   contrasts.append(dict(scope=scope,disease=dis,outcome=out,diagnosed=e.loc[a,'p'],not_diagnosed=e.loc[b,'p'],difference=diff,lower_difference=diff-crit*sd,upper_difference=diff+crit*sd,prevalence_ratio=rr,lower_ratio=np.exp(np.log(rr)-crit*sr),upper_ratio=np.exp(np.log(rr)+crit*sr)))
   vecs[scope,dis,out]=g
c=pd.DataFrame(contrasts);c.to_csv(OUT/'nsfg_contrasts.csv',index=False)
e.to_csv(OUT/'nsfg_estimates.csv');v.to_csv(OUT/'nsfg_joint_covariance.csv')
paired=[]
for dis in ['ENDO','PCOS']:
 a=vecs['strict_20_49',dis,'current_problems_all'];b=vecs['strict_20_49',dis,'current_problems_union'];z=vecs['strict_20_49',dis,'infertility12_union']
 for name,g in [('population_restriction',a-b),('definition_within_union',b-z),('total_shift',a-z)]:
  p=float(g@e.p);se=float(np.sqrt(g@v@g));paired.append(dict(disease=dis,contrast=name,value=p,se=se,lower=p-crit*se,upper=p+crit*se,design_df=60))
pd.DataFrame(paired).to_csv(OUT/'nsfg_denominator_definition_accounting.csv',index=False)
for dis,expected in [('PCOS',2.6453439),('ENDO',1.7750439)]:
 row=c[(c.scope=='strict_20_49')&(c.disease==dis)&(c.outcome=='current_problems_all')].iloc[0]
 assert abs(row.prevalence_ratio-expected)<1e-5

fig,ax=plt.subplots(figsize=(8.6,5.4),layout='constrained');rows=[];labels=[]
for dis,label in [('PCOS','PCOS'),('ENDO','Endometriosis')]:
 for outcome,text in [('current_problems_all','Broad / all women'),('current_problems_union','Broad / in union'),('infertility12_union','12-month / in union')]:
  rows.append(c[(c.scope=='strict_20_49')&(c.disease==dis)&(c.outcome==outcome)].iloc[0]);labels.append(label+' — '+text)
a=pd.DataFrame(rows);y=np.arange(6)
ax.errorbar(a.prevalence_ratio,y,xerr=np.vstack([a.prevalence_ratio-a.lower_ratio,a.upper_ratio-a.prevalence_ratio]),fmt='o',capsize=3)
ax.axvline(1,linestyle='--',linewidth=1);ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xscale('log');ax.set_xlim(.4,4)
ax.xaxis.set_minor_locator(NullLocator());ax.xaxis.set_minor_formatter(NullFormatter());ax.set_xticks([.5,1,2,3,4],[.5,1,2,3,4]);ax.set_xlabel('Prevalence ratio: ever diagnosed vs not diagnosed (95% design CI)')
ax.set_title('US NSFG 2022–2023: definition and denominator sensitivity');ax.spines[['top','right']].set_visible(False)
for ext in ['pdf','png','tiff']:
 kw={'dpi':400,'bbox_inches':'tight'}
 if ext=='tiff':kw['pil_kwargs']={'compression':'tiff_lzw'}
 fig.savefig(M/f'figures/Figure4_NSFG.{ext}',**kw)
plt.close(fig)
lines=[]
for row,label in zip(rows,['Broad, all','Broad, union','12-month, union']*2):
 name='Endometriosis' if row.disease=='ENDO' else 'PCOS'
 lines.append(f'{name} & {label} & {row.diagnosed*100:.2f} & {row.not_diagnosed*100:.2f} & {row.prevalence_ratio:.2f} ({row.lower_ratio:.2f}, {row.upper_ratio:.2f}) \\\\')
(M/'tables/nsfg_main.tex').write_text('\n'.join(lines)+'\n'+r'\bottomrule'+'\n')

baseline=ROOT/'output/audit_previous';baseline.mkdir(parents=True,exist_ok=True)
for filename in ['main','supplement']:
 target=baseline/f'{filename}_before_v2.tex'
 if not target.exists():
  content=subprocess.check_output(['git','show',f'f2df9f3e2ca6d2c0056c442dc9a5d32b4d9e55ab:manuscript/{filename}.tex'],cwd=ROOT,text=True)
  target.write_text(content)
main=(baseline/'main_before_v2.tex').read_text();supp=(baseline/'supplement_before_v2.tex').read_text()
main=main.replace("Infertility subtype and reference population composition shape China's contrasts with other G20 countries: an ecological analysis of GBD 2023",'Reference composition and outcome definitions in PCOS- and endometriosis-related infertility comparisons: GBD 2023 and US survey analyses')
main=main.replace('No individual records were accessed.','The GBD component used no individual records; a separate post hoc analysis used deidentified NSFG public-use respondent records, as described below.')
methods=r'''\subsection{Independent survey: definitions and denominators}
We added a post hoc cross-sectional analysis of the 2022--2023 US National Survey of Family Growth (NSFG) public-use female respondent file \cite{nsfgdata}. This is a separate analysis, not a validation of Chinese GBD levels, China--G20 contrasts or GBD cause attribution. CDC's published estimates provided computational replication targets rather than new findings \cite{nugent2026}.

The original file contained 5,586 respondents. Our primary domain comprised 4,855 women aged 20--49 at interview. A sensitivity included one respondent aged 50 who had been 49 at screening according to the recode specification, yielding 4,856. Unknown diagnosis responses were excluded for each condition, not coded as no. Exposures were ever-reported professional diagnoses, not assigned causes of infertility.

Three estimands were distinguished: broad current fertility problems among all eligible women; that broad outcome among current opposite-sex married/cohabiting women; and 12-month infertility within the same union domain. Broad problems were FECUND categories 3--5 or INFERT=2. Surgical sterility (FECUND=1 or 2) was not classified as impaired fecundity. The union domain used RMARITAL categories 1--2, and the narrower outcome INFERT=2 with valid INFERT categories 1--3. The recodes can reflect either partner's fertility and do not isolate a disease-specific cause \cite{nugent2024,nsfgrecodes}.

Final weights WGT2022\_2023, strata VEST and clusters VECL were used. All 80 clusters in 20 strata were retained, including zero domain contributions, giving 60 design degrees of freedom. Taylor-linearized covariance across 36 proportions preserved dependence between overlapping definitions. Pointwise 95\% intervals used $t_{60}$, the log scale for ratios and the untransformed scale for differences. Paired changes in prevalence differences were evaluated in the same union domain. Analyses were exploratory, unadjusted and not multiple-comparison corrected. Narrow-outcome sparse-event counts were reported. R \texttt{survey} reconstructed proportions and the full covariance from original records using \texttt{svyratio} and a joint delta transformation of \texttt{svytotal}. The separate local Python calculation agreed to numerical precision; audit files record the comparison. This verifies computation under the design, not GBD validity.
'''
results=r'''\subsection{Independent survey: definition and denominator sensitivity}
The two diagnosis proportions, four broad-outcome percentages and two published diagnosis standard errors were reproduced at CDC's published precision. These were already published, not novel epidemiological discoveries. Complete-case fertility-service estimates did not all reproduce the report's rounding; the discrepancy was retained rather than forced to agree.

For PCOS, broad fertility problems occurred in 45.16\% of diagnosed versus 17.07\% of non-diagnosed women: prevalence ratio 2.65 (95\% design CI 2.30--3.04). Restricting the broad outcome to current unions gave 2.17 (1.77--2.66); using 12-month infertility within unions gave 1.77 (1.22--2.57). Endometriosis ratios were 1.78 (1.40--2.25), 1.29 (0.95--1.76) and 0.84 (0.50--1.43), respectively (Table~\ref{tab:nsfg}; Figure~\ref{fig:nsfg}). The narrow endometriosis interval included one and does not establish protection.

Within the same union domain, the paired broad-minus-12-month difference in diagnosed--non-diagnosed prevalence differences was 17.15 percentage points for PCOS (95\% CI 10.24--24.06), and 7.34 for endometriosis ($-1.44$ to 16.11). The 12-month diagnosed groups had only 29 PCOS and 15 endometriosis events. The interview-age sensitivity did not change the rounded core replication targets or qualitative interpretation.

\begin{table}[htbp]\centering\small\setstretch{1.2}
\caption{Independent NSFG survey estimates under different outcome and denominator definitions.}\label{tab:nsfg}
\setlength{\tabcolsep}{4pt}
\begin{tabular}{llrrl}\toprule
Diagnosis & Outcome, domain & Diagnosed (\%) & Other (\%) & Ratio (95\% CI)\\\midrule
\input{tables/nsfg_main.tex}\end{tabular}
\caption*{Ages 20--49 at interview. Other means no reported diagnosis, not verified absence of disease. Broad denotes impaired fecundity or 12-month infertility. Union denotes current opposite-sex marriage/cohabitation. Intervals are pointwise survey design-based, not GBD uncertainty intervals. Unadjusted exploratory comparisons.}
\end{table}
'''
discussion=r'''The independent US survey supports a measurement argument, not validation of Chinese GBD estimates. Association magnitudes changed when the denominator was restricted and the outcome narrowed. Joint survey covariance avoids incorrectly treating estimates from the same respondents as independent. PCOS retained a positive narrow-outcome association; endometriosis did not show a precise protective or harmful narrow-outcome association. Age, diagnostic access, previous treatment, surgical sterilization, parity and selection into ongoing unions remain uncontrolled explanations. These are descriptive estimand changes, not causal effects.

The two data sources cannot be directly pooled or calibrated: NSFG reports diagnostic history and fertility problems in US households; GBD models cause-specific infertility in all-female population denominators. We have not established whether NSFG evidence contributed to upstream GBD modeling. Independent therefore means separately acquired records and independently coded calculations, not a proven held-out GBD validation sample. The survey does not corroborate the Chinese endometriosis terminal-year jump or numerical GBD composition shares.
'''
(S/'nsfg_methods.tex').write_text(methods);(S/'nsfg_results.tex').write_text(results);(S/'nsfg_discussion.tex').write_text(discussion)
main=main.replace(r'\subsection{Use of artificial intelligence}',r'\input{sections/nsfg_methods.tex}'+'\n'+r'\subsection{Use of artificial intelligence}')
main=main.replace(r'\section{Discussion}',r'\input{sections/nsfg_results.tex}'+'\n'+r'\section{Discussion}')
main=main.replace('The most serious limitation is unavailable joint uncertainty draws.',r'\input{sections/nsfg_discussion.tex}'+'\n\nThe principal GBD limitation remains unavailable joint uncertainty draws.')
main=main.replace('and the absence of external epidemiological validation.','and the absence of definitionally matched external validation of GBD. The US survey is a separate measurement-sensitivity analysis.')
main=main.replace('This study analyzed aggregated GBD estimates without access to identifiable individual records or recruitment of participants.','This study analyzed aggregate GBD estimates and deidentified public-use NSFG records, without access to identifiable records or recruitment of participants.')
main=main.replace('The manuscript contains no individual person\'s data, images or identifiable details.','The manuscript presents aggregate results only, without identifiable participant information.')
main=main.replace('No synthetic research observations or raw licensed downloads are included.','No synthetic research observations or raw licensed downloads are included; the additional survey outputs are aggregate estimates and design covariance.')
main=main.replace('The share component accounted for 58.5\\% of the +151.54 signed net change;', 'An additional post hoc annual-chained decomposition gave a share component of +87.11 (57.5\\%), compared with the endpoint value +88.65 (58.5\\%). This is a deterministic time-path sensitivity, not uncertainty estimation. The endpoint share component accounted for 58.5\\% of the +151.54 signed net change;')
main=main.replace('These results concern how an international comparison is constructed and what its summary conceals.','These results concern how an international comparison is constructed and what its summary conceals. The independent survey additionally demonstrates why outcome and denominator definitions must be aligned before validation is claimed.')
main=main.replace('OLS, ordinary least squares;', 'NSFG, National Survey of Family Growth; OLS, ordinary least squares;')
abstract=r'''\begin{abstract}
\noindent\textbf{Background:} International infertility comparisons depend on subtype, reference-population composition, outcome definitions and denominators. We assessed these choices for infertility associated with PCOS and endometriosis.

\noindent\textbf{Methods:} GBD 2023 estimates for females aged 15--49 in China and 18 other sovereign G20 countries, 1990--2023, were compared using age-standardized differences and symmetric reference-composition decomposition. An additional post hoc annual-chained sensitivity and separate US NSFG 2022--2023 survey analysis assessed definition and denominator sensitivity. Survey contrasts retained joint Taylor covariance and were independently checked in R. GBD joint draws were unavailable.

\noindent\textbf{Results:} China's modeled PCOS-related infertility contrast narrowed by 151.54 per 100,000. Reference composition contributed +88.65 (58.5\%), compared with +87.11 (57.5\%) under annual chaining. Secondary infertility accounted for 69.4\% of the signed contrast change; endometriosis near parity was endpoint-sensitive. Among 4,855 NSFG respondents aged 20--49, PCOS prevalence ratios were 2.65 (95\% design CI 2.30--3.04) for broad fertility problems and 1.77 (1.22--2.57) for 12-month infertility in current unions. Endometriosis ratios were 1.78 (1.40--2.25) and 0.84 (0.50--1.43). The paired within-union definition shift in the PCOS prevalence difference was 17.15 percentage points (10.24--24.06). Independent R and Python estimates and covariance agreed numerically.

\noindent\textbf{Conclusions:} Reference composition and estimand choices altered interpretation. Survey results provide definition-sensitive triangulation, not validation of Chinese GBD estimates. GBD contrasts lack propagated uncertainty; survey associations are exploratory and do not establish causation or protection.
\end{abstract}'''
main=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:abstract,main,count=1,flags=re.S)
main=main.replace('The estimates come from statistical models, and we could not calculate the full uncertainty of our comparisons.','GBD estimates come from statistical models, and their comparisons still lack full uncertainty. A separate US survey showed that associations also changed with outcome definitions and who was included. We calculated survey uncertainty, but it cannot substitute for GBD uncertainty or prove that the Chinese estimates are correct.')
newrefs=r'''
\bibitem{nsfgdata} National Center for Health Statistics. 2022--2023 National Survey of Family Growth public-use female respondent data and documentation. \url{https://www.cdc.gov/nchs/nsfg/nsfg-2022-2023-puf.htm}. Accessed 25 October 2026.
\bibitem{nugent2026} Nugent CN, Lochner KA. Endometriosis, polycystic ovary syndrome, and uterine fibroids in women ages 20--49: United States, 2022--2023. \emph{NCHS Health E-Stat}. 2026;(121):1--5. doi:10.15620/cdc/252459.
\bibitem{nugent2024} Nugent CN, Chandra A. Infertility and impaired fecundity in women and men in the United States, 2015--2019. \emph{Natl Health Stat Rep}. 2024;(202):1--19. doi:10.15620/cdc/147886.
\bibitem{nsfgrecodes} National Center for Health Statistics. 2022--2023 NSFG female respondent recode specifications. \url{https://www.cdc.gov/nchs/data/nsfg/recodespecs/2022-2023-NSFG-FemResp-RecodeSpecs.pdf}. Accessed 25 October 2026.
'''
main=main.replace(r'\end{thebibliography}',newrefs+r'\end{thebibliography}')
fig=r'''\begin{figure}[htbp]\centering\includegraphics[width=\textwidth]{figures/Figure4_NSFG.pdf}
\caption{\textbf{US survey definition and denominator sensitivity.} Prevalence ratios compare reported diagnosis with no reported diagnosis. Broad denotes impaired fecundity or 12-month infertility. Union denotes current opposite-sex marriage/cohabitation. Pointwise 95\% design intervals use joint covariance and $t_{60}$, not GBD posterior draws. Unadjusted exploratory associations; narrow diagnosed events: PCOS 29, endometriosis 15. The narrow endometriosis interval crosses one and does not imply protection.}\label{fig:nsfg}\end{figure}
'''
main=main.replace(r'\end{document}',fig+'\n'+r'\end{document}')
# Vancouver bibliography order, including inserted method/results sections.
body,rest=main.split(r'\begin{thebibliography}{99}',1);bib,end=rest.split(r'\end{thebibliography}',1)
entries=dict(re.findall(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\Z)',bib,flags=re.S))
expanded=body.replace(r'\input{sections/nsfg_methods.tex}',methods).replace(r'\input{sections/nsfg_results.tex}',results).replace(r'\input{sections/nsfg_discussion.tex}',discussion)
order=[]
for keys in re.findall(r'\\cite\{([^}]+)\}',expanded):
 for key in keys.split(','):
  if key not in order:order.append(key)
order += [x for x in entries if x not in order]
main=body+r'\begin{thebibliography}{99}'+'\n'+'\n'.join(r'\bibitem{'+k+'}'+entries[k] for k in order)+r'\end{thebibliography}'+end
(M/'main.tex').write_text('% INTEGRATED_REVISION_V2\n'+main)
extra=r'''\section{Independent NSFG outcome and denominator audit}
The original female respondent file contained 5,586 records; the strict interview-age 20--49 domain contained 4,855. Including one interview-age-50 respondent eligible at screening gave 4,856. Valid diagnosis groups were analysed separately, excluding unknown responses. Broad fertility problems were FECUND in 3--5 or INFERT=2; surgical sterility was excluded from impaired fecundity. Current union was RMARITAL in 1--2. The narrow outcome was INFERT=2, retaining valid INFERT categories 1--3 in the denominator. Narrow diagnosed numerator/domain counts were 15/173 for endometriosis and 29/252 for PCOS.

For ratio estimate $p_j=\sum_iw_in_{ij}/\sum_iw_id_{ij}$ the linearized respondent vector is $u_{ij}=w_i(n_{ij}-p_jd_{ij})/\sum_iw_id_{ij}$. Sum vectors by PSU within stratum and compute
\[\widehat V=\sum_h\frac{m_h}{m_h-1}\sum_b(\boldsymbol U_{hb}-\overline{\boldsymbol U}_h)(\boldsymbol U_{hb}-\overline{\boldsymbol U}_h)^T.\]
All 80 PSUs in 20 strata were retained. The 36-by-36 matrix preserves dependence across outcome definitions. R survey and Python reconstructions agreed within approximately $10^{-15}$ for estimates/standard errors and $10^{-18}$ for covariance. These are computational checks, not GBD validation. Pointwise $t_{60}$ intervals do not establish familywise significance or causal effects.

PCOS prevalence-difference shifts were 5.43 percentage points (95\% CI 0.33--10.53) for restricting the broad-outcome population to unions, and 17.15 (10.24--24.06) for changing broad to 12-month outcome within unions. The total shift was 22.58 (16.07--29.08), using joint covariance. Endometriosis shifts were 8.28 (3.01--13.56), 7.34 ($-1.44$ to 16.11) and 15.62 (7.32--23.92). All are exploratory and unadjusted.

Ever fertility services were HLPPRG=1 or HLPMC=1, with definite negatives requiring both responses=5. Complete-case estimates were 30.84/12.72\% for endometriosis diagnosed/not diagnosed and 34.49/11.80\% for PCOS. They did not all equal the CDC rounded percentages 30.7/12.7 and 34.5/11.7. The report does not provide the full missing-response implementation; the discrepancy is not hidden or forced to agree. Six core published percentages and two diagnosis standard errors did agree to published precision.

\section{Annual-chained decomposition sensitivity}
The endpoint product decomposition can be applied to each adjacent year and summed. The PCOS reference-share contribution becomes +87.11 per 100,000 (57.5\%), compared with endpoint +88.65 (58.5\%). Both sum with their rate components to +151.54. The Chinese-rate component remains +271.51; the chained reference-rate component is $-207.08$. The decomposition describes time-path allocation, not a new method or GBD uncertainty.

\section{GBD joint uncertainty remains unavailable}
The IHME request received an automatic acknowledgement, not data or approval. Original marginal intervals do not identify cross-cell dependence. NSFG covariance cannot replace jointly indexed GBD draws. GBD derived results remain point estimates. The survey is not a proven held-out source relative to GBD and does not validate the Chinese endometriosis terminal-year change.
'''
(S/'revision_supplement.tex').write_text(extra)
supp=supp.replace(r'\end{document}',r'\input{sections/revision_supplement.tex}'+'\n'+r'\end{document}')
(M/'supplement.tex').write_text('% INTEGRATED_REVISION_V2\n'+supp)
# First-tier candidate format uses a structured extended abstract and author-year citations.
hr=main.replace('Reproductive Health draft','Human Reproduction candidate')
hr=hr.replace(r'\usepackage[hidelinks]{hyperref}',r'\usepackage[authoryear,round]{natbib}'+'\n'+r'\usepackage[hidelinks]{hyperref}')
hr=hr.replace(r'\section{Background}',r'\section{Introduction}').replace(r'\section{Methods}',r'\section{Materials and methods}')
labels={'pcos':'Teede et al.(2023)','eshre':'Becker et al.(2022)','gbd':'GBD 2023 Collaborators(2025)','xu':'Xu et al.(2025)','lu':'Lu et al.(2026)','wang':'Wang et al.(2026)','feng':'Feng et al.(2025)','results':'IHME(2026)','repository':'PCOS research workspace(2026)','chen':'Chen et al.(2026)','gather':'Stevens et al.(2016)','nsfgdata':'NCHS(n.d.-a)','nsfgrecodes':'NCHS(n.d.-b)','nugent2026':'Nugent and Lochner(2026)','nugent2024':'Nugent and Chandra(2024)'}
a,rest=hr.split(r'\begin{thebibliography}{99}',1);_,end=rest.split(r'\end{thebibliography}',1)
hr=a+r'\begin{thebibliography}{99}'+'\n'+'\n'.join(r'\bibitem['+labels[k]+']{'+k+'}'+entries[k] for k in sorted(entries,key=lambda x:labels[x].lower()))+r'\end{thebibliography}'+end
# The fully formatted, locally visually checked candidate is separately archived in Drive.
(M/'human_reproduction.tex').write_text('% INTEGRATED_REVISION_V2\n'+hr)
qc={'phase':'repository build','source_zip_sha256':'ef9f0ec715ce7909b50f1ea67958166b2cd1ad3482c4b083174898ec8c7ceaaa','survey_estimates':36,'survey_design_df':60,'GBD_draws_obtained':False,'submitted':False,'note':'Repository build reproduces revised core results. The full locally formatted candidate and complete audited archive are in 2026PCOS.'}
(ROOT/'docs/revision_v2_repository_build.json').write_text(json.dumps(qc,indent=2))
print(json.dumps(qc,indent=2))
