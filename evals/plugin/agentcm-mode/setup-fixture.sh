#!/usr/bin/env bash
# Copy AgentCM's contract fixture into the eval workspace, with AgentCM closed unless --api.
# Usage: setup-fixture.sh [--api] [--crop-stub] [needs...]
#   --crop-stub: the eval stand-in for crop.sh and crop.ps1 (one fixed image), for a case that never looks at a
#   drawing; otherwise AgentCM's real crop scripts render the seed PDFs (AGENTCM_POPPLER_BIN)
#   needs: specs unread-manual groups pending pdfs api api-url schedule-id flooring-specs submittal
# A need the fixture does not meet exits 3: the harness reports the case as skipped.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$HERE/../../../bin/construction-python"
SRC="$HERE/construction"
start_api=0; crop_stub=0
while [ "${1:-}" = "--api" ] || [ "${1:-}" = "--crop-stub" ]; do
  if [ "$1" = "--api" ]; then start_api=1; else crop_stub=1; fi
  shift
done
if [ "$start_api" = 1 ]; then set -- api "$@"; fi
missing=()
for need in "$@"; do
  case "$need" in
    specs) ls "$SRC"/specs/*.txt >/dev/null 2>&1 && grep -q '^## Specification sections' "$SRC/INDEX.md" || missing+=("spec sections") ;;
    unread-manual) grep -q '^## Spec manuals not read' "$SRC/INDEX.md" || missing+=("a manual AgentCM could not read") ;;
    groups) ls "$SRC"/sheets/*.groups.tsv >/dev/null 2>&1 || missing+=("accepted groups") ;;
    pending) grep -q "$(printf '\tpending\t')" "$SRC"/sheets/*.tsv 2>/dev/null || missing+=("a pending group") ;;
    pdfs) ls "$HERE"/project/drawings/*.pdf >/dev/null 2>&1 || missing+=("the sheets' PDFs") ;;
    api) [ -f "$HERE/api-responses.json" ] && grep -q '127.0.0.1:47817' "$SRC/database.yaml" || missing+=("AgentCM's recorded answers at 127.0.0.1:47817") ;;
    api-url) grep -q '127.0.0.1:47817' "$SRC/database.yaml" || missing+=("an api_url at 127.0.0.1:47817") ;;
    schedule-id) grep -q 'schedule_id=[0-9a-f]\{8\}-' "$SRC"/schedules/*.tsv 2>/dev/null || missing+=("an ingested schedule (schedule_id=)") ;;
    flooring-specs) grep -q '^| 09 6' "$SRC/INDEX.md" || missing+=("flooring sections matching the BP-09 bids") ;;
    submittal) [ -d "$HERE/project/06 - Submittals" ] || missing+=("a submittal against one of its sections") ;;
    *) echo "setup-fixture.sh: unknown need '$need'" >&2; exit 2 ;;
  esac
done
if [ "${#missing[@]}" -gt 0 ]; then
  printf 'waiting for the contract fixture: it has no %s\n' "$(IFS=';'; echo "${missing[*]}")" >&2
  exit 3
fi
mkdir -p .construction
cp -R "$SRC/." .construction/
if [ -d "$HERE/project" ]; then cp -R "$HERE/project/." .; fi
if [ "$crop_stub" = 1 ]; then cp "$HERE/stub/crop.sh" "$HERE/stub/crop.ps1" .construction/; fi
# AgentCM closed: its database does not answer (skills never query it anyway).
printf '#!/bin/sh\necho "AgentCM is not running: its database does not answer" >&2\nexit 1\n' > .construction/query.sh
printf 'Write-Error "AgentCM is not running: its database does not answer"\nexit 1\n' > .construction/query.ps1
if [ "$start_api" = 1 ]; then
  "$PY" "$HERE/stub_api.py" start --responses "$HERE/api-responses.json" --workspace .
else
  "$PY" "$HERE/stub_api.py" stop >/dev/null || true
fi
