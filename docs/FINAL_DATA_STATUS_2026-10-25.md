# Final data and synchronization status — 25 October 2026

## NSFG individual-level reproduction: completed
- CDC official 2022–2023 female respondent PUF ZIP was downloaded by GitHub Actions directly from ftp.cdc.gov and hash-locked: SHA-256 ef9f0ec715ce7909b50f1ea67958166b2cd1ad3482c4b083174898ec8c7ceaaa.
- The official file contains 5,586 female respondents; the published age-domain sensitivity contains 4,856.
- Survey design uses WGT2022_2023, VEST and VECL: 20 strata, 80 PSUs, 60 design degrees of freedom.
- Independent R survey and Python implementations reconstructed 36 proportions and their 36x36 joint design covariance; they agreed to numerical precision.
- Main published CDC diagnosis/fertility-problem benchmarks reproduce to published rounding. Fertility-service complete-case values are reported transparently where the report's missing-response implementation cannot be exactly reconstructed.
- These US survey results are external triangulation of disease/infertility associations and denominator sensitivity, not outcome-matched validation of GBD cause-attributed infertility or China–G20 trends.

## GBD 2023 jointly indexed posterior draws: provider-access blocked
- GBD 2023 generates final uncertainty from 250 posterior draws.
- Public Results Tool releases final point estimates and marginal uncertainty intervals, not the jointly indexed cross-cell draw files needed for this study's pooled reference, standardized differences and decompositions.
- IHME acknowledged the direct data request on 25 October 2026 but has not delivered or approved the requested draws.
- Public GHDx/Results Tool, code repositories and IHME documentation were rechecked; no legal public infertility-specific aligned draw file was found.
- Therefore no pseudo-draws were generated from marginal intervals. Derived GBD contrasts remain point estimates; the existing conservative marginal-bound audit is not a substitute for posterior propagation.

## Cloud synchronization
- GitHub main contains the integrated v2 manuscript, NSFG R/Python verification outputs, joint survey covariance, figures, TeX sources and compiled PDFs. Current integrated build commit: e4b4418901e86a1f3bfa5a0e09a9bb2c10254e11.
- Google Drive / 2026PCOS contains the official NSFG audit-input bundle and verified integrated v2 Human Reproduction candidate PDF, Reproductive Health backup PDF, Additional files, TeX source ZIP and complete integrated revision ZIP.
- Galaxy history PCOS (11ac94870d0bb33ad5abd2b59708ab6e) remains readable from this Chat session, but the available Browser connector exposes read-only tab access and no authenticated write/API action. A Galaxy-ready official NSFG input bundle has therefore been prepared and stored in Drive; this status must not be described as a completed Galaxy upload.

## Submission boundary
The work is not submitted. Human authors must still verify authorship, affiliations, corresponding author/ORCID, ethics determination, funding, competing interests, author approval and permanent archive identifiers. A targeted novelty audit cannot guarantee that no unindexed, preprint or in-review work overlaps the comparator-composition question.
