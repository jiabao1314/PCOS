#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
exec .venv/bin/jupyter lab --notebook-dir="$PWD"
