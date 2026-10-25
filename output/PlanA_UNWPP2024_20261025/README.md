# PCOS Plan A: independent UN WPP 2024 reference-population audit

**Analysis executed 25 October 2026.** Reusable GBD 2023 model inputs, 19 sovereign G20 country members, females 15--49, 7 five-year ages, 1990--2023. Main scientific endpoint: China-minus-other-18-country standardised burden rate difference for infertility *attributed by GBD* to PCOS (cause 605) or endometriosis (607), split into primary, secondary and total infertility (REI 220, 221, 198). All reported GBD effects are **descriptive model-conditioned point estimates**, not provider-verified joint posterior uncertainty intervals.

## Data sources, rights and checks

- **UN:** Official United Nations DESA Population Division [World Population Prospects 2024](https://population.un.org/wpp/) historical female mid-year (1 July) `PopulationByAge5GroupSex_Medium.csv.gz`; 1,759,905 source rows and 4,522 matching G20 country/year/age rows; values in **thousands**, multiplied by 1,000. Raw source hash: `a04d7d1486a5eb2832cc812d599448f0a71e8ac9e1e7e6fa4066673d6a2487cd`; subset hash: `07a8edbeaa9d1d2114664e19c7c4d8709c7cc5cf3d5b4dfbb8e46e7acc429de9`. Rights: CC BY 3.0 IGO. The separate full original archive is retained as provenance and for Galaxy upload when write capability is available; it is **not** a disease-rate validation dataset.
- **GBD:** GBD 2023 official Results Tool 19-country female population (4,522 rows), total cause-specific prevalence (36,176 measure/metric rows overall) and primary/secondary annual count exports. Original query IDs and SHA-256 are in `results/qc_summary.json` and the PCOS repo's acquisition document. Licensed downloads should remain where permitted and **are not included in this public analysis package**; reobtain with original queries to reproduce.
- **Research question:** Does changing the reference-country population-source alter country-composition contribution to the modeled China-minus-G20 contrast? **GBD rates and standard age weights never changed** between GBD-weighted and UN-weighted scenarios. UN population replaces only each reference country's proportion of its age-specific comparator population.

## Results

| Indicator (per 100,000 women, 15–49) | GBD reference shares | UN WPP 2024 reference shares |
|---|---:|---:|
| PCOS total China–reference difference, 1990 | -272.92 | -273.31 |
| PCOS total China–reference difference, 2023 | -121.38 | -122.62 |
| PCOS total 1990–2023 signed change | +151.54 | +150.69 |
| Country-composition component of change | +88.65 | +86.76 |
| Composition component / net signed change | 58.5% | 57.6% |
| PCOS primary China–reference, 2023 | -123.54 | -124.88 |
| PCOS secondary China–reference, 2023 | +2.16 | +2.26 |
| Endometriosis total China–reference, 2023 | -0.20 | -0.03 |

The UN-weighted PCOS secondary contrast changes from **+2.26** with contemporary reference population shares, to **-48.34** with fixed-1990 UN shares and **-127.89** with equal-country weights. These are different policy benchmark definitions, not estimates with statistical confidence bands. The UN population audit preserves the main composition contribution while underscoring that near-zero subtype comparisons are benchmark-sensitive.

Country mix changed materially: India's age-weighted reference share rose from **35.71%** to **46.45%** in UN WPP. Mean country-share total variation between UN and GBD reference within-age vectors was **1.13 percentage points** over all 1990–2023 age cells and **1.32 percentage points** in 2023. This is a *population-weight estimate comparison*, not independent replication of GBD disease rates.

## Quality checks

- All 4,522 WPP target cells and all 4,522 GBD female-population cells exist with exact 19×34×7 coverage and unique keys.
- All 27,132 (19×34×7×2 causes×3 subtypes) GBD cause/infertility subtype cells are represented without duplicate keys.
- For each country/year/age/cause, primary + secondary modeled cases equals total within `1e-6` source units.
- GBD population-weighted 2023 PCOS total difference is reproduced as **-121.376216 per 100,000** from independent source CSVs.
- 1990→2021, 2022, 2023 symmetric decompositions are exactly additive for both population sources, two causes and three subtypes, with errors below `1e-8` per 100,000.
- Source hashes and transformation outputs are in `results/qc_summary.json` and `source/UN_WPP2024_source_manifest.json`.

## Contents and reproducibility

- `source/UN_WPP2024_G20_female_15_49_1990_2023.csv`: selected official UN rows (population unit: persons) for downstream research.
- `source/UN_WPP2024_source_manifest.json`: source metadata and SHA-256.
- `analyze_un_benchmarks.py`: reference population mixing, exact symmetric decomposition, policy benchmarks, country exclusions and QC; input GBD files must be placed under `raw_gbd/` using source names in the script.
- `make_wpp_figures.py`: render publication-grade vector figures.
- `results/*.csv` and `results/qc_summary.json`: transparent outputs and source hashes.
- `manuscript/`: editable TeX sources for two journal-style variants plus supplement.
- `pdf/`: compiled manuscript PDFs; compiled with local TeX Live and visually reviewed.

## Interpretation and limitations

The G20 is an economically defined, non-representative comparison set. Changes in country share are not biological causes or improvements in care, and neither effect should be called preventable cases. WPP population is not an external check on Chinese disease incidence/prevalence; underlying demographic inputs may overlap GBD. The GBD-2023 endometriosis final-year jump remains unexplained and has no independent clinical corroboration here. No jointly indexed posterior draws were obtained: no inferential GBD intervals or p-values for custom pooled differences/decompositions may be claimed. Standard weights were reproduced from rounded published values. Analyses were post hoc exploratory and author/ethics/funding/consent declarations in the draft remain to be completed by the research team.

## Fixed requested cloud workflow

- **Galaxy**: [PCOS history](https://usegalaxy.eu/histories/view?id=11ac94870d0bb33ad5abd2b59708ab6e) for permitted raw downloaded inputs. Chat mode browser is read-only; any Galaxy upload not actually confirmed must be marked **pending**, not complete.
- **GitHub**: [PCOS repository](https://github.com/jiabao1314/PCOS) for code, analysis results, TeX and PDFs.
- **Drive**: [2026PCOS](https://drive.google.com/drive/folders/1Db9GIWdXt9eoCOD9oMgNCmoGkiOcQXey) for paper/TeX/PDF ZIP and interim raw data pending Galaxy upload.
