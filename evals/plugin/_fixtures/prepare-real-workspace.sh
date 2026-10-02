#!/usr/bin/env bash
# Scaffold for the real-document eval cases (run by each case's setup.sh).
#
# Usage: prepare-real-workspace.sh <profile> [<profile>...]
#
# Copies fixtures derived from the Sanibel Fire and Rescue Station 172 documents
# into the empty eval workspace. The fixtures are generated once from the PDFs
# users download (docs/RUNNING_EVALS.md) by sanibel/make_fixtures.py. When the
# downloads are missing this exits 3, which the harness reports as a skipped
# case rather than a failure.
#
# Profiles (combine as needed):
#   mech         01 - Drawings/<the 8-sheet mechanical set>
#   a500         01 - Drawings/A500 - DOOR SCHEDULE, DOOR AND FRAME TYPES.pdf
#   a101         01 - Drawings/A101 - ARCHITECTURAL PLAN - FIRST FLOOR.pdf
#   g010         01 - Drawings/G010 - CODE SUMMARY & CALCULATIONS.pdf
#   specs        02 - Specifications/Project Manual - Division 09 Flooring.pdf (9 sections)
#   specs-small  02 - Specifications/Project Manual - Three Sections.pdf
#   flooring     02 - Specifications/Specification Sections/<the 6 flooring sections, pre-split>
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN="$(cd "$HERE/../../.." && pwd)"
SOURCE="$PLUGIN/evals/test_docs/SANIBEL FIRE AND RESCUE STATION 172"
GEN="$HERE/sanibel/generated"

if ! ls "$SOURCE/01 - Drawings"/*.pdf >/dev/null 2>&1 || ! ls "$SOURCE/02 - Specifications"/*VOL-1.pdf >/dev/null 2>&1; then
  echo "Sanibel documents not found under '$SOURCE'. Download them first: docs/RUNNING_EVALS.md" >&2
  exit 3
fi
if [ ! -f "$GEN/manifest.json" ]; then
  echo "Generating Sanibel fixtures (one-time)..." >&2
  "$PLUGIN/bin/construction-python" "$HERE/sanibel/make_fixtures.py" >&2
fi

mkdir -p "01 - Drawings" "02 - Specifications"
for profile in "$@"; do
  case "$profile" in
    mech)        cp "$GEN/drawings/"*Mechanical*.pdf "01 - Drawings/" ;;
    a500)        cp "$GEN/drawings/A500 - "*.pdf "01 - Drawings/" ;;
    a101)        cp "$GEN/drawings/A101 - "*.pdf "01 - Drawings/" ;;
    g010)        cp "$GEN/drawings/G010 - "*.pdf "01 - Drawings/" ;;
    specs)       cp "$GEN/specs/Project Manual - Division 09 Flooring.pdf" "02 - Specifications/" ;;
    specs-small) cp "$GEN/specs/Project Manual - Three Sections.pdf" "02 - Specifications/" ;;
    flooring)    mkdir -p "02 - Specifications/Specification Sections"
                 cp "$GEN/specs/sections/"*.pdf "02 - Specifications/Specification Sections/" ;;
    *) echo "unknown profile: $profile" >&2; exit 1 ;;
  esac
done
rmdir "01 - Drawings" "02 - Specifications" 2>/dev/null || true

cat > CLAUDE.md <<'EOF'
# Sanibel Fire and Rescue Station 172

Eval workspace holding a subset of the project's 100% Construction Documents
(Schenkel Shultz Architecture, issued January 5, 2024). Drawings are in
`01 - Drawings/` and specifications in `02 - Specifications/`.
EOF
