#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PCOS_PYTHON="${PCOS_PYTHON:-.venv/bin/python}"
"$PCOS_PYTHON" src/prepare_inputs.py
"$PCOS_PYTHON" src/analyze.py
"$PCOS_PYTHON" src/trend_sensitivity.py
"$PCOS_PYTHON" src/endpoint_sensitivity.py
"$PCOS_PYTHON" src/forecast_validation.py
"$PCOS_PYTHON" src/make_figures.py
"$PCOS_PYTHON" src/analyze_strata.py
"$PCOS_PYTHON" src/manuscript_tables.py
"$PCOS_PYTHON" src/reference_composition.py
cp results/figures/*.pdf manuscript/figures/
"$PCOS_PYTHON" src/journal_figures.py
if [[ -f data/raw/nsfg_2022_2023/NSFG_2022_2023_FemRespPUFData.csv ]]; then
  "$PCOS_PYTHON" src/external_validation.py
  Rscript src/validate_external_survey.R
  "$PCOS_PYTHON" src/external_figures_tables.py
fi
"$PCOS_PYTHON" -m unittest discover -s tests -v
tectonic --outdir output/pdf manuscript/main.tex
cp output/pdf/main.pdf output/pdf/GBD2023_Reproductive_Health_main.pdf
tectonic --outdir output/pdf manuscript/supplement.tex
cp output/pdf/supplement.pdf output/pdf/GBD2023_Reproductive_Health_Additional_file_1.pdf
