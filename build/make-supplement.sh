#!/usr/bin/env bash
# Package the reproducibility archive that accompanies the preprint.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=build/privacy-signaling-supplement.zip
rm -f "$OUT"

zip -q -r "$OUT" \
  data figures specs/pinned \
  extract.py code.py reliability.py finalize.py figures.py check_numbers.py \
  measure_wild.py \
  CODEBOOK.md README.md PINS.json sources.json LICENSE CITATION.cff \
  preprint-privacy-signaling.md \
  -x '*.DS_Store' '*/__pycache__/*' 'data/*.bak' 'data/statements.csv.bak' \
     'data/statements_coded.csv.bak'

python3 - "$OUT" <<'PY'
import sys, zipfile, pathlib
z = pathlib.Path(sys.argv[1])
with zipfile.ZipFile(z) as f:
    n = len(f.namelist())
print(f"wrote {z}  ({z.stat().st_size/1024/1024:.1f} MB, {n} files)")
PY
