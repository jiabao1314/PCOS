# NSFG 2022–2023 independent age-standardization sensitivity (2026-10-25)

## Verified original public-use data

- CDC female-respondent ZIP SHA-256: \`ef9f0ec715ce7909b50f1ea67958166b2cd1ad3482c4b083174898ec8c7ceaaa\`.
- Decompressed CSV SHA-256: \`eb10fa3bd11e671b1a3533781a01550261bde9c6b8ad9b17a87dd7250bc131a8\`.
- Records: 5,586 female respondents; strict interview age 20–49 domain: **4,855**. CDC tabulates 4,856 including one interview-age-50 respondent who was 49 at screening.
- Survey design: **20 strata, 80 PSUs, 60 design degrees of freedom**; survey weight WGT2022_2023.
- The four current-fertility-problem CDC point estimates reproduced at public reporting precision; four original design standard errors also reproduced to within 1e-10 against previously independently computed R/Python results.

## New exploratory reanalysis

Compared women reporting a prior professional PCOS/endometriosis diagnosis with women reporting no such diagnosis. The outcome is broad current fertility problems (FECUND=3–5 or INFERT=2), **not** modeled GBD cause-attributed infertility.

| Condition | Definition | Prevalence difference, pp (95% design CI) | Ratio (95% design CI) |
|---|---|---|---|
| PCOS | Crude | 28.09 (22.11–34.07) | 2.65 (2.30–3.04) |
| PCOS | Direct age standardization | 28.57 (22.50–34.65) | 2.67 (2.32–3.07) |
| PCOS | Direct age standardization; exclude reported endometriosis | 28.34 (21.95–34.73) | 2.71 (2.32–3.15) |
| Endometriosis | Crude | 14.41 (6.80–22.02) | 1.78 (1.40–2.25) |
| Endometriosis | Direct age standardization | 18.68 (10.38–26.98) | 2.00 (1.59–2.52) |
| Endometriosis | Direct age standardization; exclude reported PCOS | 15.89 (7.41–24.36) | 1.96 (1.49–2.57) |

Direct age standardization uses the survey-weighted population age distribution among all US women aged 20–49 (20–29: 0.33562, 30–39: 0.34666, 40–49: 0.31773), shared across both diagnosis groups. Taylor linearization includes uncertainty from age-specific ratio estimates **and from the estimated common age weights**; 95% pointwise intervals use t_60. No preregistration or multiplicity correction. No causal or country-comparative inference is claimed.

## Reproducibility package

- Complete TeX sources, new Supplemental Table S7, Supplemental Figure S6, compiled Human Reproduction and Reproductive Health candidates, 10-page updated supplemental PDF, figures, original-file SHA audit, analytic Python source, detailed CSV/JSON results:
  [output/PCOS_NSFG_age_standardized_manuscript_update_20261025.zip](../output/PCOS_NSFG_age_standardized_manuscript_update_20261025.zip)
- Cloud copy (same artifact): [Google Drive 2026PCOS](https://drive.google.com/file/d/1ENWQfslxngN5zbG340wEqQJjkrMvSlOC/view).
- Public respondent-level CSV is **not committed to this repo**; the official CDC source is https://www.cdc.gov/nchs/nsfg/nsfg-2022-2023-puf.htm .
- The existing GBD 2023 jointly indexed draws request is still unresolved; the NSFG survey-design confidence intervals do not substitute for GBD posterior uncertainty.

## Literature and interpretation

Nugent CN, Lochner KA. NCHS Health E-Stat 121, July 2026: https://www.cdc.gov/nchs/data/hestat/hestat121.htm .

The CDC bivariate proportions are previously published. This secondary age-standardized/co-diagnosis sensitivity is an original calculation using public records, but novelty beyond all published or unpublished work cannot be guaranteed. It is an independent US association/measurement analysis, **not direct external validation** of the GBD China–other-G20 comparisons.
