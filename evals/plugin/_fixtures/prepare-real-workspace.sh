#!/usr/bin/env bash
# Scaffold for the real-document and synthetic-document eval cases (run by each case's setup.sh).
#
# Usage: prepare-real-workspace.sh <profile> [<profile>...]
#
# Copies fixtures into the empty eval workspace. Profiles marked (real) come from
# the Sanibel Fire and Rescue Station 172 documents users download
# (docs/RUNNING_EVALS.md), derived once by sanibel/make_fixtures.py; when the
# downloads are missing and a real profile is requested this exits 3, which the
# harness reports as a skipped case. The other profiles are synthetic fixtures
# committed in this folder and need no download.
#
# Profiles (combine as needed):
#   mech         (real) 01 - Drawings/<the 8-sheet mechanical set>
#   a500         (real) 01 - Drawings/A500 - DOOR SCHEDULE, DOOR AND FRAME TYPES.pdf
#   a101         (real) 01 - Drawings/A101 - ARCHITECTURAL PLAN - FIRST FLOOR.pdf
#   g010         (real) 01 - Drawings/G010 - CODE SUMMARY & CALCULATIONS.pdf
#   specs        (real) 02 - Specifications/Project Manual - Division 09 Flooring.pdf (9 sections)
#   specs-small  (real) 02 - Specifications/Project Manual - Four Sections.pdf (01 33 00, 09 30 00, 09 65 13, 09 65 40)
#   flooring     (real) 02 - Specifications/Specification Sections/<the 6 flooring sections, pre-split>
#   addendum     04 - Addenda/Addendum 01 (eval fixture).pdf
#   rfi-template 16 - Templates/RFI Template - Example Builders.docx and its mapping under .construction/skills/rfi-drafter/
#   subcontract-template  16 - Templates/Subcontract Template - Example Builders.docx
#   bids         03 - Subcontractor Bids/BP-09 Flooring/<the 5 synthetic bids and the scope sheet>
#   awarded-bid  03 - Subcontractor Bids/BP-09 Flooring/<the awarded bid (Gulfshore) and the scope sheet>
#   bids-tabulated  .construction/skills/bid-tabulator/bids/<per-bid JSON as bid-tabulator writes it>
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN="$(cd "$HERE/../../.." && pwd)"
SOURCE="$PLUGIN/evals/test_docs/SANIBEL FIRE AND RESCUE STATION 172"
GEN="$HERE/sanibel/generated"
SYN="$HERE/synthetic"

needs_real=0
for profile in "$@"; do
  case "$profile" in mech|a500|a101|g010|specs|specs-small|flooring) needs_real=1 ;; esac
done
if [ "$needs_real" = 1 ]; then
  if ! ls "$SOURCE/01 - Drawings"/*.pdf >/dev/null 2>&1 || ! ls "$SOURCE/02 - Specifications"/*VOL-1.pdf >/dev/null 2>&1; then
    echo "Sanibel documents not found under '$SOURCE'. Download them first: docs/RUNNING_EVALS.md" >&2
    exit 3
  fi
  if [ ! -f "$GEN/manifest.json" ]; then
    echo "Generating Sanibel fixtures (one-time)..." >&2
    "$PLUGIN/bin/construction-python" "$HERE/sanibel/make_fixtures.py" >&2
  fi
fi

for profile in "$@"; do
  case "$profile" in
    mech)        mkdir -p "01 - Drawings"; cp "$GEN/drawings/"*Mechanical*.pdf "01 - Drawings/" ;;
    a500)        mkdir -p "01 - Drawings"; cp "$GEN/drawings/A500 - "*.pdf "01 - Drawings/" ;;
    a101)        mkdir -p "01 - Drawings"; cp "$GEN/drawings/A101 - "*.pdf "01 - Drawings/" ;;
    g010)        mkdir -p "01 - Drawings"; cp "$GEN/drawings/G010 - "*.pdf "01 - Drawings/" ;;
    specs)       mkdir -p "02 - Specifications"; cp "$GEN/specs/Project Manual - Division 09 Flooring.pdf" "02 - Specifications/" ;;
    specs-small) mkdir -p "02 - Specifications"; cp "$GEN/specs/Project Manual - Four Sections.pdf" "02 - Specifications/" ;;
    flooring)    mkdir -p "02 - Specifications/Specification Sections"
                 cp "$GEN/specs/sections/"*.pdf "02 - Specifications/Specification Sections/" ;;
    addendum)    mkdir -p "04 - Addenda"; cp "$HERE/addendum/"*.pdf "04 - Addenda/" ;;
    rfi-template) mkdir -p "16 - Templates" ".construction/skills/rfi-drafter"
                 cp "$SYN/templates/RFI Template - Example Builders.docx" "16 - Templates/"
                 cp "$SYN/templates/rfi_template_map.json" ".construction/skills/rfi-drafter/" ;;
    subcontract-template) mkdir -p "16 - Templates"; cp "$SYN/templates/Subcontract Template - Example Builders.docx" "16 - Templates/" ;;
    bids)        mkdir -p "03 - Subcontractor Bids/BP-09 Flooring"; cp "$SYN/bids/"*.pdf "03 - Subcontractor Bids/BP-09 Flooring/" ;;
    awarded-bid) mkdir -p "03 - Subcontractor Bids/BP-09 Flooring"
                 cp "$SYN/bids/00 - Bid Package Scope Sheet.pdf" "$SYN/bids/01 - Gulfshore Resilient Floors LLC.pdf" "03 - Subcontractor Bids/BP-09 Flooring/" ;;
    bids-tabulated) mkdir -p ".construction/skills/bid-tabulator/bids"
                 cp "$SYN/bids_ground_truth/bids/"*.json ".construction/skills/bid-tabulator/bids/" ;;
    *) echo "unknown profile: $profile" >&2; exit 1 ;;
  esac
done

cat > CLAUDE.md <<'EOF'
# Sanibel Fire and Rescue Station 172

Eval workspace holding a subset of the project's 100% Construction Documents
(Schenkel Shultz Architecture, issued January 5, 2024). Drawings are in
`01 - Drawings/` and specifications in `02 - Specifications/`. The general
contractor is Example Builders, Inc.
EOF
