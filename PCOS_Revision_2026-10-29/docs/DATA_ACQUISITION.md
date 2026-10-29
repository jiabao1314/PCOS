# Inputs and archival mapping

Original GBD 2023 exports were acquired on 25 October 2026. This revision reused them; no replacement release or simulated observations were introduced. Exact file SHA-256 and size: `docs/input_manifest.json`. Every listed file belongs in `data/input/` relative to this revision's root.

| Local filename | Official query | Existing Galaxy dataset |
|---|---|---|
| IHME-GBD_2023_DATA-1b13e337-1.csv | 1b13e3376135ab41a4bc5e0ffc60e84f | hid10, 40160950115d555eebf77aabacbbed50 |
| IHME-GBD_2023_DATA-916826fb-1.csv | 916826fb285f8d3c3e53117dd2133406 | hid11, 40160950115d555eb62eb5fd9f64809c |
| IHME-GBD_2023_DATA-416daf73-1.csv | 416daf735b9fc79bec35506514424e73 | hid18, 40160950115d555e0b6e566d0ec7f593 |
| IHME-GBD_2023_DATA-76c5523c-1.csv | 76c5523c52f32caf342843daf2326fa4 | hid19, 40160950115d555ec0b5a6acf9f8474d |
| weights.csv | Published seven-age standard reproduction | hid12, 40160950115d555ec453516913e91453 |

Galaxy names differ from official download filenames. Restore the local names above after retrieval, without editing bytes, and verify hashes. Past GBD upload byte-identical verification is preserved in the earlier project `output/galaxy_upload_receipt.json`. The 29 October browser check found these datasets in the PCOS history; it does not claim a new byte-level GBD download comparison.

GBD filters: female sex 2; years 1990–2023 inclusive; age IDs 8–14 (15–19 through 45–49); causes 605 and 607; prevalence measure 5. Total impairment is 198; primary/secondary are 220/221. Total export includes Number/Rate and YLDs as originally acquired; annual strata supply Number, and separate 1990/2023 strata supply Number/Rate. Only prevalence is selected for this manuscript. Population Number is matched by country/year/age in the same release. Complete country list is embedded in both executable core files and `docs/joint_draws_request.json`.

Official UN WPP 2024 source and rights are recorded in `data/input/UN_WPP2024_source_manifest.json`. Historical female midyear estimates for the same country/year/age cells yield `UN_WPP2024_G20_female_15_49_1990_2023.csv`, 4,522 rows. Source values in thousands are converted to persons; only within-age reference-country shares replace GBD shares. The public subset is supplied under CC BY 3.0 IGO with United Nations Population Division attribution. The source compressed SHA-256 is a04d7d1486a5eb2832cc812d599448f0a71e8ac9e1e7e6fa4066673d6a2487cd. Any new Galaxy fetch is separately logged in the current synchronization receipt and is not declared successful while queued or failed.

Official portals: https://vizhub.healthdata.org/gbd-results/ and https://population.un.org/wpp/. Source data remain subject to the originating institutions' applicable terms. The public reproduction package excludes licensed raw GBD exports and per-country/per-age source-cell extracts.
