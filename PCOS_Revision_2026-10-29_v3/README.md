# PCOS independent editorial revision v3

Date: 29 October 2026 (Europe/Paris). Prepared 2026-10-29T18:29:30+01:00.

This is a separate revision of `PCOS_Revision_2026-10-29`; all 184 files of that archived source package were preserved. The manuscript remains a descriptive GBD/UN benchmark analysis. No clinical hospital study or new posterior uncertainty analysis is included.

## Deliverables

- `output/PCOS_Editorial_v3_2026-10-29.pdf`: 19-page main manuscript, 3 tables and 5 figures.
- `output/PCOS_Supplement_v3_2026-10-29.pdf`: 18-page supplement, 8 tables and 7 figures.
- `manuscript/`: editable TeX, all numerical table fragments and the 12 referenced vector figures.
- `docs/MANUSCRIPT_CLAIM_AUDIT.md`, `claim_audit.csv` and `claim_audit.json`: 28 central claims, code/input evidence and independent reconstruction checks.
- `docs/table_figure_qc.json`: all 11 table fragments/139 rows and 12 figure rasters matched an isolated renderer rerun.
- `docs/EDITORIAL_CHANGES.diff`: complete main/supplement source changes against the retained previous revision.
- `docs/LITERATURE_VERIFICATION.json`: targeted source verification, access scope and corrected RBMO issue year.
- `docs/EXECUTION_RECORD.json` and `logs/`: actual commands, failures/fixes, versions, code hashes and compiler logs.
- `output/PCOS_Editorial_v3_Complete_2026-10-29.zip`: sources, audits, scripts, PDFs and the required public original analysis code/aggregate evidence. Licensed GBD inputs and country-age source cells are excluded.

## Reproduction and compilation

The archive preserves repository-relative paths: this folder, `scripts/`, and the public parts of the earlier `PCOS_Revision_2026-10-29` folder. In a repository checkout, use Python 3.12, the earlier revision's pinned requirements, pypdf/Pillow, Tectonic and Poppler. The retained original README explains lawful GBD acquisition and the seven input hashes; supply those originals only in its private `data/input/` location. No new research inputs were downloaded this round.

The audit/build driver is `scripts/editorial_revision_20261029.py`; asset verification is `scripts/editorial_assets_20261029.py`. The `audit`/`all` driver deliberately refuses to overwrite an existing audit or manuscript. Reproduce creation in a fresh working copy without an existing v3 output directory. To compile the supplied source in a separate copy of this version:

```sh
cd manuscript
tectonic --keep-logs --keep-intermediates --outdir ../output main.tex
tectonic --keep-logs --keep-intermediates --outdir ../output supplement.tex
```

The archived R outputs were compared against the independent new reconstruction; R itself was not rerun in this round. Original and revised numerical assets remain identical. No GBD posterior draws were obtained. The 58.5% ratio and the 39.8%-67.9% specified scenario range retain their descriptive limitations. All intentional XX author/submission declarations are preserved.

## Storage and publication

Drive: https://drive.google.com/drive/folders/1tNldHZ1Bs2ah063jy2HuMngrr4FoMGxL

GitHub: https://github.com/jiabao1314/PCOS/tree/main/PCOS_Revision_2026-10-29_v3

Publication status is established only by the later cloud-readback receipt in `00_Shared_Context/SYNC_CHECK.md`. This archive is a pre-publication content snapshot; a successful local build is not a cloud-synchronization receipt. No submission or external correspondence was performed.
