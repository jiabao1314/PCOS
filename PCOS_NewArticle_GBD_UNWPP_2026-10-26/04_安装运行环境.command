#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3 code/setup_environment.py
read -p "完成。按回车关闭。"
