# Plan A — UN WPP 2024 independent population-weighting analysis: data and sync manifest

Date: 2026-10-25. Study: GBD 2023 PCOS/endometriosis-attributed infertility, China versus 18 other sovereign G20 countries, 1990–2023, females 15–49.

## Reproducibility summary
- Original independently downloaded UN WPP2024 dataset (female population by five-year age group, mid-year July 1) acquired via [GitHub Actions](https://github.com/jiabao1314/PCOS/actions/runs/40212070057) from the [UN population division](https://population.un.org/wpp/).
- Original WPP gzip SHA256: `a04d7d1486a5eb2832cc812d599448f0a71e8ac9e1e7e6fa4066673d6a2487cd`.
- G20 19-country age-sex-population subset: 4,522 cells for 19 countries × 34 years × seven five-year ages; subset CSV SHA256: `07a8edbeaa9d1d2114664e19c7c4d8709c7cc5cf3d5b4dfbb8e46e7acc429de9`.
- Study does **not** infer disease rates from UN denominators. GBD-derived age-specific disease rates and age standardization are held constant, and **only country shares within the reference comparator at each age/year** are switched from GBD population to UN WPP2024 population.
- Country-year-age/cause/subtype 27,132 cells passed primary+secondary=total and two-source alignment checks; symmetric decomposition identities checked.
- PCOS total change in China−18-country difference: +151.54/100k under GBD population, +150.69/100k under UN population. Contribution of changing reference country population shares: +88.65/100k (58.5%) versus +86.76/100k (57.6%).
- PCOS secondary 2023 China−reference difference under UN-current shares: +2.26/100k; with 1990 fixed shares: -48.34/100k. Comparator policy sensitivity is substantive; the small positive sign is not robust.
- **No GBD 2023 jointly indexed draws** have been received; decomposed contributions, pooled comparison differences and reference sensitivity are model-conditioned point estimates, not posterior 95% intervals.
- **Not independent validation** of disease rates or the 2023 endometriosis endpoint anomaly. Existing US NSFG survey is related but outcome nonidentical.

## Verified destinations

### GitHub (derived analysis + TeX + PDF)
- [Main publication and code package](../output/PlanA_UNWPP2024_20261025/PCOS_PlanA_UN_WPP2024_analysis_TeX_PDF_20261025.zip)
- [Human Reproduction candidate](../output/PlanA_UNWPP2024_20261025/PCOS_PlanA_Human_Reproduction_candidate_20261025.pdf)
- [Reproductive Health candidate](../output/PlanA_UNWPP2024_20261025/PCOS_PlanA_Reproductive_Health_candidate_20261025.pdf)
- [Updated supplement](../output/PlanA_UNWPP2024_20261025/PCOS_PlanA_Supplement_20261025.pdf)
- [Executable independent-population reanalysis](../src/un_population_benchmark_analysis.py)
- [Derived point-estimate table](../results/un_wpp2024_20261025/symmetric_decomposition_1990_endpoints.csv)
- [QC manifest](../results/un_wpp2024_20261025/qc_summary.json)

### Google Drive (2026PCOS)
- [Study subfolder](https://drive.google.com/drive/folders/133vTCSpkXBAxiRRQN-bnYTHO08hgFuVJ) under [2026PCOS](https://drive.google.com/drive/folders/1Db9GIWdXt9eoCOD9oMgNCmoGkiOcQXey)
- [Full analysis and publication ZIP](https://drive.google.com/file/d/1juuGWXtaQJ5LC-szjHuKxfdKOsgUNUrT/view)
- [Full original UN WPP2024 source and 19-country subset, Galaxy-ready ZIP](https://drive.google.com/file/d/1j8of0rg0V8ZELCZYjcfCRbdIoGAshurV/view)
- [Human Reproduction PDF](https://drive.google.com/file/d/1pzrhq-FU13wuX_8Zigsx9zm5maYOa3Dz/view), [Reproductive Health PDF](https://drive.google.com/file/d/15Vgsm4gZmNsuOjkIZhDEb7iOH5Eq8NlZ/view), [Supplement PDF](https://drive.google.com/file/d/1xSuUMPwYxiNPKV1zhdjF797QmyIitNUd/view).

### Galaxy PCOS (ORIGINAL FILE UPLOAD PENDING)
- Exact user-designated destination: https://usegalaxy.eu/histories/view?id=11ac94870d0bb33ad5abd2b59708ab6e
- **Status: NOT uploaded by ChatGPT in this session**. The only available connected browser action in Chat mode is read-only. Do not claim that Drive/GitHub uploads automatically synced to Galaxy.
- Galaxy-ready ZIP: [Download/source from Drive](https://drive.google.com/file/d/1j8of0rg0V8ZELCZYjcfCRbdIoGAshurV/view); raw official gzip filename `WPP2024_PopulationByAge5GroupSex_Medium.csv.gz` and filtered `UN_WPP2024_G20_female_15_49_1990_2023.csv` should be imported as separate dataset entries in the existing **PCOS** history, accompanied by the SHA256 manifest.
- GitHub stores permitted **code and derived aggregates only**; original UN source is archived in Drive pending upload to designated Galaxy.

## Scientific and submission boundaries
The revised `Human Reproduction` and `Reproductive Health` PDFs are complete research drafts, not submitted final versions. Author affiliations, author approvals, ethics determination, funding and conflicts of interest must be supplied by the research team. This analysis does not guarantee a CAS Zone 1 acceptance.