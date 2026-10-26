#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
.venv/bin/python code/PCOS_NewArticle_complete.py
read -p "完成。按回车关闭。"
