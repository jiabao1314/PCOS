#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
Rscript code/PCOS_NewArticle_complete.R
read -p "完成。按回车关闭。"
