#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PCOS_PYTHON_BIN="${PCOS_PYTHON:-python3}"
mkdir -p logs output
"$PCOS_PYTHON_BIN" code/PCOS_NewArticle_complete.py > logs/python_core.log 2>&1
Rscript code/PCOS_NewArticle_complete.R > logs/R_core.log 2>&1
"$PCOS_PYTHON_BIN" code/revision_analysis.py > logs/revision_analysis.log 2>&1
(cd manuscript && tectonic --keep-logs --keep-intermediates --outdir ../output main.tex > ../logs/main_compile.log 2>&1)
(cd manuscript && tectonic --keep-logs --keep-intermediates --outdir ../output supplement.tex > ../logs/supplement_compile.log 2>&1)
cp output/main.pdf output/PCOS_ReproductiveHealth_Revised_2026-10-29.pdf
cp output/supplement.pdf output/PCOS_Supplement_Revised_2026-10-29.pdf
"$PCOS_PYTHON_BIN" code/verify_revision.py
