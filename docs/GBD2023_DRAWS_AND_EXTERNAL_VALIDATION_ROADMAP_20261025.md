# PCOS / Endometriosis–attributed infertility: GBD 2023 uncertainty and independent-data roadmap

**Analysis date:** 2026-10-25  
**Primary comparison:** China vs the remaining 18 sovereign G20 members, females 15–49 years, GBD 2023, infertility impairment REI 198; PCOS cause 605; endometriosis cause 607. Primary (REI 220) and secondary (REI 221) have separate inputs.

## 1. Decisions about posterior draws

**Status: jointly aligned GBD 2023 posterior draws have not been received.** The previous query to `data@healthdata.org` was acknowledged automatically; an automatic receipt is not the provider's approval or data release. The Results Tool provides marginal point estimates and uncertainty intervals; they do not encode the cross-country/age/year dependence necessary to produce full posterior intervals of the pooled China-minus-G20 comparisons or reference-country composition decomposition.

**Strict requirements before reporting full draw-propagated estimates**: posterior draw identifiers must have an explicitly documented *joint* meaning across locations, age cells, years, impairment types, PCOS/endometriosis causes and any uncertain denominators; original output release must match the 2023 burden and population files, and the provider's permitted use must allow the calculation. Request either (a) the jointly indexed draws with alignment metadata, or (b) a corresponding approved provider-generated estimate and uncertainty for the exact derived summary. Even marginal draws for each cell, if not cross-cell aligned, are insufficient.

**If denied**: keep national GBD marginal UIs as supplied; present custom pooled rates, signed differences and decompositions as **point estimates only**, with transparent fixed-country-share/leave-one-out/end-year/age-window sensitivities. Model CI, NSFG complex-survey CI or country bootstrap MUST NOT be labeled as GBD posterior UIs. An exploratory covariance or copula sensitivity may be described as dependent on assumed correlation rather than verified posterior inference, but should not be the primary paper's significance test.

## 2. New 2023 terminal-year audit: directly recomputed from the archived GBD 2023 CSV

Inputs retain exact file SHA-256 in `results/gbd2023_2023_endpoint_audit.json`. Total burden: 36,176 source rows; population 4,522; primary/secondary annual Number rows 36,176. Original Number / matched female population reproduces source Rate with maximum discrepancy 1.51×10^-11 per 100,000. Age-standardization weights for 15–49 sum to **0.494902 before within-age-range normalization**.

### China endometriosis and PCOS endpoint

- China's **endometriosis-attributed infertility** restricted 15–49 ASPR rose **43.1314 → 53.3037 per 100,000** from 2022 to 2023: change **+10.1723 per 100,000**, or **+23.5846%**.
- Primary infertility contributes **+0.7412 per 100,000 (7.3%)**; secondary infertility contributes **+9.4311 per 100,000 (92.7%)** of the *signed 2022–2023 change*. These are exact arithmetic contributions, not causal fractions, posterior percentages, or person-level transitions.
- China's **PCOS-attributed infertility** changed **602.0876 → 605.0752 per 100,000 (+0.4962%)** over the same period.
- For China the largest pre-2023 positive annual percentage change in the 1991–2022 GBD 2023 endometriosis model series was **+1.56%**, versus **+23.58%** in 2023; this is a within-model endpoint stress test and has no stand-alone epidemiological p-value.
- In the same release, endometriosis ASPR moved **+14.82% in the United States**, **+11.93% in Japan**, and **−0.41% in the Republic of Korea** from 2022 to 2023. Thus the change is neither limited to China nor universal across all countries.

### Published-source concordance and rate-definition warning

Liu Y, Hua S, Wang F, et al., *International Journal of Women's Health* (published 18 Aug 2026; DOI **10.2147/IJWH.S622604**) reported **181,587** modeled China endometriosis-infertility cases in 2023. Independently reaggregating our locally archived GBD 2023 Number file gave **181,587.09**, agreeing to the rounded published count; this is a **same-source replication**.

The publication reported ASPR **31.52 (1990)** and **26.38 (2023)** per 100,000. The corresponding un-renormalized partial-weight calculations from our source data are **31.524 and 26.380**; using the normalized 15–49 weight vector yields **63.697 and 53.304**. They differ by the exact 15–49 weight sum (0.494902). These units **must not be directly compared without harmonizing age-standardization conventions**. Numerical agreement with another publication using GBD 2023 establishes matching source and weight behavior, **not independent data validation**. The article's 168 laparoscopically confirmed infertility cases characterize selected patients and cannot validate national 2023 prevalence or its annual change.

See `results/china_endometriosis_published_rate_crosswalk.csv`, `results/gbd2023_19country_2023_yoy_stress_test.csv`, `results/china_endometriosis_2022_2023_age_subtype_components.csv` and 3 corresponding vector PDF figures.

## 3. Independent datasets ranked by what they can actually validate

| Source | What it supports | Whether available right now | Major mismatch / restriction |
|---|---|---|---|
| **NSFG 2022–2023 (CDC, US)** | Complex-survey association between reported prior PCOS/endometriosis diagnosis and broad fertility difficulty / care use. Already reproduced from 5,586 public female records with stratification and design SE. | **Already analyzed and archived** | No China trend; broad reported fertility problems ≠ GBD etiology-assigned infertility; cannot verify 2023 China jump. |
| **WHO 2023 infertility prevalence systematic review, 1990–2021** | Independent systematic literature evidence for global/regional 12-month infertility and definitions; helps contextualize heterogeneity. | Public report, **no paired country/cause/year microdata** | No PCOS/endo cause-specific 2023 data; does not replace posterior draws. |
| **South Korea NHIS / HIRA claims studies** | Independent health-service cohort with diagnosis-coded N80/N97, potentially track clinical infertility and endometriosis care. | Existing published aggregate studies; individual NHIS/HIRA records need licensed institutional access. | Healthcare utilization and insured diagnoses ≠ GBD burden; existing accessible cohorts in selected papers end before 2023; not China. |
| **China Kadoorie Biobank (CKB)** | Potential China-specific cohort clinical diagnoses and reproductive history, contingent on available variables and linkage. | **Proposal, review and data-use agreement required**; suitability for this exact end point unverified. | General female reproductive history does not automatically mean verified cause-attributed infertility; no instant download. |
| **UK Biobank** | Possible independent EHR linkage of endometriosis, PCOS and infertility plus reproductive history. | Researchers must apply; website says new applications temporarily paused, expected to resume late 2026. | United Kingdom, selection bias and clinical coding, not national China temporal validation. |
| **All of Us US EHR/survey** | Large US diagnosed-condition and fertility/health-service associations under OMOP. | Registered Workbench institutional authorization (DURA); individual rows cannot simply be downloaded to Galaxy. | US volunteer cohort; secure-environment data sharing terms; no direct GBD posterior or Chinese 2023 cause incidence. |
| **China hospital registry (with validated N80/N97 or PCOS codes, 2020–2024)** | Best route to directly stress-test timing of endometriosis-related infertility diagnoses in China if denominators, capture and a population catchment are verified. | **Not obtained**; requires agreement/ethics and adequate ascertainment. | Clinic cohort alone without population denominator is referral/case-mix data, not a national prevalence validation. |

**Interpretation:** No freely available source found in the present targeted search is an exact drop-in replacement for jointly indexed GBD draws **and** a national, cause-specific China 2023 validation series. Adding noncomparable data as if interchangeable would weaken—not strengthen—the inference.

## 4. Concrete route for a higher-tier manuscript

1. Retain the GBD international-composition result as an *explicitly descriptive, model-conditioned* analysis and disclose the missing posterior covariance.
2. Treat the 2023 endometriosis discontinuity as a **post hoc falsification / stress-test**: show primary-secondary and five-year age contribution, China/US/Japan/Korea heterogeneity, and 2021/2022 endpoint sensitivity without converting point changes to significant population trends.
3. Obtain true independent country-specific cause-attributed infertility data, ideally registry/insurance-based China series spanning 2020–2024 with a stable female population denominator and diagnostic harmonization (not yet available). If impossible, confine external evidence to NSFG independent association and WHO method contextualization.
4. Request GBD joint draws (or provider-calculated aggregate uncertainty) and appropriate indexed metadata; do not assume the 250 GBD posterior draw indices are aligned across all requested dimensions.
5. Update the exact journal target only after discussing whether the joint GBD + distinct US NSFG narrative represents one coherent research question. Check citations, research contribution, researcher author/ethics/funding declarations, journal ranking and licensed data storage before submission.

## 5. Fixed storage destinations (user instruction)

- **Downloaded raw data:** Galaxy PCOS history https://usegalaxy.eu/histories/view?id=11ac94870d0bb33ad5abd2b59708ab6e ; this run used previously archived GBD files and did NOT acquire a new person-level dataset.
- **Derived tables, figures, scripts, TeX, PDF:** GitHub https://github.com/jiabao1314/PCOS and Google Drive 2026PCOS folder https://drive.google.com/drive/folders/1Db9GIWdXt9eoCOD9oMgNCmoGkiOcQXey . Each upload must be read-back verified; if Galaxy authenticated write is unavailable, place a ready-to-upload archive in Drive with an **honest pending** flag, not a claim of Galaxy synchronization.

## 6. Primary sources (accessed 2026-10-25)

- Liu Y, Hua S, Wang F, et al. https://doi.org/10.2147/IJWH.S622604 ; PubMed: https://pubmed.ncbi.nlm.nih.gov/42621623/ . *Same GBD source as this project*.
- WHO, Infertility Prevalence Estimates 1990–2021. https://www.who.int/publications/i/item/978920068315 .
- Korea NHIS endometriosis survey. https://pmc.ncbi.nlm.nih.gov/articles/PMC8593577/ .
- Korea population infertility clinical utilization (NHIS). https://bmjopen.bmj.com/content/16/7/e117740 .
- China Kadoorie Biobank application. https://www.ckbiobank.org/data-access/data-access-procedures .
- UK Biobank access page. https://www.ukbiobank.ac.uk/use-our-data/apply-for-access/ .
- NIH All of Us data access. https://www.researchallofus.org/data-tools/data-access/ .
- IHME GBD Results Tool. https://vizhub.healthdata.org/gbd-results/ .
