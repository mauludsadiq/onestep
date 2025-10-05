#!/usr/bin/env bash
set -euo pipefail

rm -rf build dist *.egg-info
python -m build

if [[ "${1:-}" == "--test" ]]; then
  twine upload --repository testpypi dist/*
else
  twine upload dist/*
fi
