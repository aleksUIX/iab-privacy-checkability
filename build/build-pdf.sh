#!/usr/bin/env bash
# Build the preprint PDF for ResearchGate.
#
#   pandoc (markdown -> HTML) | weasyprint (HTML -> PDF)
#
# Usage: build/build-pdf.sh
set -euo pipefail

cd "$(dirname "$0")/.."
SRC=preprint-privacy-signaling.md
OUT=build/privacy-signaling-preprint.pdf
HTML=build/.paper.html

command -v pandoc >/dev/null    || { echo "pandoc not found"; exit 1; }
command -v weasyprint >/dev/null || { echo "weasyprint not found"; exit 1; }

for f in figures/fig1-hops.png figures/fig2-classes.png figures/fig3-gpp-sections.png; do
  [ -f "$f" ] || { echo "missing figure: $f (run python3 figures.py)"; exit 1; }
done

echo "pandoc -> html"
pandoc "$SRC" \
  --from=markdown+pipe_tables+backtick_code_blocks+fenced_code_attributes \
  --to=html5 \
  --standalone \
  --metadata title="How Machine-Checkable Is IAB Privacy Signaling" \
  --metadata lang=en \
  --section-divs=false \
  -o "$HTML"

python3 - "$HTML" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1])
h = p.read_text()
h = re.sub(r'<header[^>]*id="title-block-header".*?</header>', '', h, flags=re.S)
h = re.sub(r'<style>.*?</style>', '', h, flags=re.S)
p.write_text(h)
PY

echo "weasyprint -> pdf"
weasyprint -s build/print.css -u . "$HTML" "$OUT"

rm -f "$HTML"
python3 - "$OUT" <<'PY'
import sys, pathlib, subprocess
f = pathlib.Path(sys.argv[1])
size = f.stat().st_size / 1024
pages = "?"
try:
    out = subprocess.run(["pdfinfo", str(f)], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"):
            pages = line.split()[-1]
except FileNotFoundError:
    pass
print(f"\nwrote {f}  ({size:.0f} KB, {pages} pages)")
PY
