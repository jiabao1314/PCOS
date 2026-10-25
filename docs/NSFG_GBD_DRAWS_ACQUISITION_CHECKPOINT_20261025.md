# PCOS data acquisition checkpoint — 2026-10-25

## Confirmed
- The original GBD 2023 raw-data package is preserved in Google Drive 2026PCOS and Galaxy PCOS history. Do not redownload or republish the licensed source tables without checking IHME terms.
- Matched cross-cell posterior draws remain unavailable. The IHME inquiry has received only an automatic acknowledgment. An explicit provider statement describing draw ID joint alignment, population uncertainty and permitted use is required before propagating uncertainty.
- CDC 2022–2023 NSFG female respondent public-use CSV download is officially listed at https://www.cdc.gov/nchs/nsfg/nsfg-2022-2023-puf.htm . Official FTP file is https://ftp.cdc.gov/pub/Health_Statistics/NCHS/NSFG/NSFG-2022-2023-FemRespPUFData.zip ; the posted archive is ~2.54MB. An attempted direct retrieval on 2026-10-25 failed in the runtime due to network/DNS restrictions, not a CDC authorization requirement.
- The existing repository includes src/nsfg_replication.py (requires original 5,586 respondent records, verified recodes and design variables), src/joint_draws_pipeline.py (rejects unverified joins), and tests. 15 local unit checks passed when run against synthetic fixtures; this is NOT real-data validation.

## Concrete NSFG reproducibility steps
1. Obtain the female respondent public-use CSV ZIP from the official CDC file page. Record URL, retrieval timestamp, exact file name, byte length and SHA-256.
2. Review official female codebook, file index, recode definitions, NSFG design/weight documentation. Confirm ENDO/PCOS and INFERT/FECUND/HLPPRG/HLPMC codes, including refused/don't-know/not-applicable; never recode missing as disease absent.
3. Preserve the full 5,586 records and the full stratified/cluster survey design before restricting analyses to the 4,856 respondents aged 20–49.
4. Verify the 2026 CDC survey report's released estimates with Taylor linearization and the appropriate design-based intervals. Only then conduct clearly labeled exploratory adjusted comparisons, if scientifically relevant. Never treat the survey as validation of GBD-attributable infertility or China–G20 gaps.
5. Keep individual respondent data outside public GitHub. Record the CDC public source and derived privacy-safe aggregate outputs, with no participant identifiers.

## Useful code invocation once actual input and verified review JSON exist
```bash
python src/nsfg_replication.py --data data/restricted/NSFG-2022-2023-FemRespPUFData.csv --review config/nsfg_codebook_review.json
python src/joint_draws_pipeline.py
python -m unittest discover -s tests -v
```

## Blockers that must not be relabeled as complete
- Genuine provider-aligned GBD draws and matching uncertainty for denominator: NOT ACQUIRED.
- NSFG individual dataset: OFFICIAL DOWNLOAD FOUND, not retrieved into current execution runtime.
- Galaxy upload: no authenticated Galaxy action is available in this chat; the prior raw data and outcomes in the existing PCOS history remain preserved.
- New PDF manuscript: separate revision artifacts already generated in prior analysis; this checkpoint does not imply reanalysis or new figures.

The user's objective is submission to a CAS Category 1 journal, but the originality of every result or acceptance cannot be guaranteed. Cross-study overlap and 2025 CAS category/source should be checked before choosing a journal.
