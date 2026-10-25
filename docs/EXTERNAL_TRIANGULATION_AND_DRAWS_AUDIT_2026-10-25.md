# PCOS GBD 2023 — independent triangulation and joint-draw audit (25 October 2026)

## Scope and evidentiary status
This document **does not claim independent validation of GBD cause-attributed infertility prevalence**. It supplies an independently collected US survey comparison about reproductive-health problems among women with a diagnosis of PCOS or endometriosis. Definitions, denominators, geography and estimands differ from the GBD analysis. The existing core manuscript and figures are unchanged pending a statistically defensible comparison.

## Verified independent publication (CDC/NCHS)
Nugent CN, Lochner KA. *Endometriosis, Polycystic Ovary Syndrome, and Uterine Fibroids in Women Ages 20–49: United States, 2022–2023.* NCHS Health E-Stat 121, July 2026. DOI 10.15620/cdc/252459. Primary source: https://www.cdc.gov/nchs/data/hestat/hestat121.htm (also https://www.cdc.gov/nchs/data/hestat/hestat121.pdf).

The nationally representative 2022–2023 NSFG report included 4,856 female respondents aged 20–49 years. Survey results account for the complex sample design. Its exposure is **ever receiving a diagnosis**, not GBD cause attribution. Its outcomes are **current fertility problems** (infertility OR impaired fecundity) and **ever use of fertility services**, not GBD infertility impairment prevalence. These are descriptive bivariate associations, not causal effects or individual longitudinal transitions.

| Exposure (ever diagnosed) | Outcome | Diagnosed (%) | Not diagnosed (%) | Absolute percentage-point difference | Ratio of published point estimates |
|---|---|---:|---:|---:|---:|
| Endometriosis | Current fertility problems | 33.0 | 18.6 | +14.4 | 1.77 |
| PCOS | Current fertility problems | 45.2 | 17.1 | +28.1 | 2.64 |
| Endometriosis | Ever use of fertility services | 30.7 | 12.7 | +18.0 | 2.42 |
| PCOS | Ever use of fertility services | 34.5 | 11.7 | +22.8 | 2.95 |

Ratios and percentage-point differences above are deterministic arithmetic on rounded CDC percentages. No uncertainty bounds are calculated from rounded percentages. Before reusing published estimates with independent standard errors, obtain the exact tables and any accompanying design information. The CDC report also gives marginal ever-diagnosis proportions: endometriosis 6.2% and PCOS 8.7% among women aged 20–49. These **must not** be placed alongside GBD cause-attributed infertility ASPRs as estimates of the same event.

## Valid use in the paper
- **Background/Discussion triangulation**: PCOS and endometriosis diagnoses coincide with greater reported current fertility problems and fertility-service use in a US survey, supporting clinical relevance but not the magnitude/direction of China-minus-G20 GBD rate contrasts.
- Clearly label as an independent *contextual* population survey, not a direct external validation of GBD attribution, 1990–2023 temporal changes or the 2023 endometriosis discontinuity.
- The CDC age range is 20–49 and respondents are US household women, whereas the GBD cohort is 15–49 and 19 sovereign G20 countries. The CDC association is conditional on diagnostic history. GBD output uses age-specific population as denominator and modeled cause attribution.
- To assess comparability rather than simply cite the result, consider a **separate** US 20–49 GBD descriptive display with explicit outcome differences. Never present numeric agreement of prevalences as validation.

## Optional individual-level external study (not yet performed)
The NSFG 2022–2023 public-use data and design documentation are available from https://www.cdc.gov/nchs/nsfg/index.htm. A weighted survey analysis should use the actual public-use variable dictionary, design weights/strata/clusters and coding for eligibility, diagnosis, fertility outcomes, age and union history. Verify suppression rules, effective sample sizes, missing data and design-based variance estimates. Do not assume current fertility problems and GBD's primary/secondary infertility are definitionally interchangeable. This item is **planned, not executed**.

## Jointly indexed GBD draws request and gate
GBD 2023 public point estimates and marginal lower/upper intervals do **not** provide the cross-cell dependence required to propagate uncertainty for pooled age-standardized rates, China-minus-reference differences, subtype contributions, symmetric country-share decomposition or end-year contrasts. Required identifiers:
- GBD release 2023; years 1990–2023;
- locations: China plus 18 other G20 sovereign countries (same fixed 19 as config/study.json);
- female sex_id=2; five-year age groups from 15–19 to 45–49;
- impairment REI 198 total, 220 primary, 221 secondary;
- causes 605 PCOS and 607 endometriosis;
- prevalence measure 5, YLD measure 3 if available, metric 1 Number;
- indexed draws that are **jointly aligned** across locations, ages, years, types, causes (including dependence between numerator and denominator where relevant), with usage/redistribution terms and the underlying matched population and standard weights.

An inquiry specifying these dimensions was emailed to data@healthdata.org on 25 October 2026. **Receipt or access has not been confirmed.** If draws cannot be supplied, existing derived results must remain point estimates; sensitivity ranges, conditional trend CIs and manually sampled marginal UIs are not substitutes for valid GBD posterior uncertainty.

## Publication and sync gate
The existing Reproductive Health manuscript, main/supplementary PDFs, tables and TeX remain the **current compiled research draft** as of this audit. This note is an evidence update only; not a validated revised manuscript, and does not change original numerical conclusions. Update main.tex/Additional file 1 and recompile only after careful author review and journal formatting checks. All author identity, institutional review, funding, competing-interest declarations, permanent archive accession, and submission confirmations remain open.

Primary sources:
- CDC Health E-Stat 121: https://www.cdc.gov/nchs/data/hestat/hestat121.htm
- NSFG data portal: https://www.cdc.gov/nchs/nsfg/index.htm
- IHME GBD Results Tool: https://vizhub.healthdata.org/gbd-results/
