# Manuscript claim and evidence audit

Executed: 2026-10-29T18:24:04+01:00.

Independent reconstruction uses the seven hashed original inputs. No source estimates were replaced.
All 28 explicitly listed central numerical claims passed their displayed rounding checks.
The four core tables (1,488 rows) were recomputed and compared against both archived Python and R outputs; 1,440 sensitivity rows were recomputed.

| Claim | Value | Manuscript location | CSV evidence | Status |
|---|---:|---|---|---|
| net_gap_change | 151.54 | Abstract; Table 2; Figure 3 | symmetric_decomposition_1990_endpoints.csv; PCOS/Total/GBD/2023 | PASS |
| china_rate_effect | 271.51 | Abstract; Table 2; Figure 3 | symmetric_decomposition_1990_endpoints.csv; PCOS/Total/GBD/2023 | PASS |
| reference_rate_effect | -208.62 | Abstract; Table 2; Figure 3 | symmetric_decomposition_1990_endpoints.csv; PCOS/Total/GBD/2023 | PASS |
| reference_country_composition_effect | 88.65 | Abstract; Table 2; Figure 3 | symmetric_decomposition_1990_endpoints.csv; PCOS/Total/GBD/2023 | PASS |
| Signed composition ratio (%) | 58.5 | Abstract; Discussion | symmetric_decomposition_1990_endpoints.csv | PASS |
| Specified sensitivity minimum (%) | 39.8 | Main Results | composition_sensitivities.csv; 1990/2023/GBD | PASS |
| Specified sensitivity maximum (%) | 67.9 | Main Results | composition_sensitivities.csv; 1990/2023/GBD | PASS |
| 1990 total china_aspr | 333.56 | Table 1; Figure 1 | all_annual_benchmark_aspr.csv | PASS |
| 1990 total ref_aspr | 606.48 | Table 1; Figure 1 | all_annual_benchmark_aspr.csv | PASS |
| 1990 total gap | -272.92 | Table 1; Figure 1 | all_annual_benchmark_aspr.csv | PASS |
| 1990 total ratio | 0.550 | Table 1; Figure 1 | all_annual_benchmark_aspr.csv | PASS |
| 2023 total china_aspr | 605.08 | Table 1; Figure 1 | all_annual_benchmark_aspr.csv | PASS |
| 2023 total ref_aspr | 726.45 | Table 1; Figure 1 | all_annual_benchmark_aspr.csv | PASS |
| 2023 total gap | -121.38 | Table 1; Figure 1 | all_annual_benchmark_aspr.csv | PASS |
| 2023 total ratio | 0.833 | Table 1; Figure 1 | all_annual_benchmark_aspr.csv | PASS |
| Secondary 2023 UN-WPP2024/dynamic | 2.26 | Abstract; Table 3; Figure 5 | all_annual_benchmark_aspr.csv | PASS |
| Secondary 2023 UN-WPP2024/fixed1990 | -48.34 | Abstract; Table 3; Figure 5 | all_annual_benchmark_aspr.csv | PASS |
| Secondary 2023 UN-WPP2024/equal | -127.89 | Abstract; Table 3; Figure 5 | all_annual_benchmark_aspr.csv | PASS |
| Secondary 2023 GBD/dynamic | 2.16 | Abstract; Table 3; Figure 5 | all_annual_benchmark_aspr.csv | PASS |
| Secondary 2023 GBD/fixed1990 | -47.99 | Abstract; Table 3; Figure 5 | all_annual_benchmark_aspr.csv | PASS |
| Primary net change | 46.40 | Main Results | symmetric_decomposition_1990_endpoints.csv | PASS |
| Secondary net change | 105.14 | Main Results | symmetric_decomposition_1990_endpoints.csv | PASS |
| Secondary fraction of total net (%) | 69.4 | Main Results | symmetric_decomposition_1990_endpoints.csv | PASS |
| UN net_gap_change | 150.69 | Results; Figure 4 | symmetric_decomposition_1990_endpoints.csv | PASS |
| UN reference_rate_effect | -207.59 | Results; Figure 4 | symmetric_decomposition_1990_endpoints.csv | PASS |
| UN reference_country_composition_effect | 86.76 | Results; Figure 4 | symmetric_decomposition_1990_endpoints.csv | PASS |
| UN signed composition ratio (%) | 57.6 | Main Results | symmetric_decomposition_1990_endpoints.csv | PASS |
| Raw restricted-age weight sum | 0.494902 | Methods; Supplement | weights.csv | PASS |

## Evidence paths and scope
Paths in the evidence columns resolve within the preserved `PCOS_Revision_2026-10-29/results/python/` package. Input manifests and code remain in that package.
The JSON report maps all 11 table fragments and 12 figures to their CSVs and generator code. Copied assets are checked byte-for-byte.
Supplementary-only outputs outside the independently recomputed core/sensitivity tables retain their existing provenance; the new supplement is editorially unchanged except for its audit description.

## Discrepancies and corrections
No discrepancy was found in the central numerical claims audited above. No effect estimate was changed.
The handoff cited the RBMO article as a 2025 study; its online publication is 2025, but its indexed issue is February 2026, volume 52(2):105239. The new bibliography uses the issue year and records both dates.
The claim that the handoff had not been saved was stale boilerplate: cloud readback had confirmed both files. The new report distinguishes execution from prior discussion.

## Scientific limits
- No joint posterior uncertainty can be identified from these inputs.
- R/Python agreement checks existing R outputs; base R was not rerun this round.
- Figures are reused rather than newly estimated; evidence mappings do not independently validate the GBD model.
- 58.5% and 69.4% are overlapping signed decompositions; they are not additive.
- 39.8%-67.9% describes specified country/age scenarios, not a confidence interval or every sensitivity setting.
- UN replacement changes reference shares only, not GBD disease rates or clinical validity.
- Author, affiliation, funding and ethics applicability XX fields remain for author completion.

## Additional completed asset verification (2026-10-29T18:29:30+01:00)

The isolated archived-generator rerun reproduced all 11 table fragments (139 numerical rows) byte-for-byte and all 12 figure PDFs with identical extracted text and 108-dpi rendered pixels. See `table_figure_qc.json`. This supersedes the earlier provisional source-mapping-only scope for supplementary assets. All 184 archived source files remain unchanged. This computational agreement does not validate the upstream GBD model.

Across the 1,440 sensitivity rows the largest absolute difference was approximately 7.00e-9, including unstable signed ratios for near-zero net changes; this was below the prespecified 1e-8 numerical tolerance. Four core-table comparisons against archived R outputs had maximum difference approximately 6.25e-13. Displayed primary claims were unchanged.
