#!/bin/bash
set -euo pipefail

project_dir="$(dirname "$(dirname "$(realpath "$0")")")"

python -m venv "$project_dir/.venv"
"$project_dir/.venv/bin/python" -m pip install -e "${project_dir}[dev]"
exec "$project_dir/.venv/bin/python" -m pytest "$project_dir/tests/" -v
