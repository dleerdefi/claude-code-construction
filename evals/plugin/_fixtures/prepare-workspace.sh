#!/usr/bin/env bash
# Shared scaffold for the plugin eval cases (run by each case's setup.sh).
#
# 1. Copies a synthetic project into the empty eval workspace: sample-project by
#    default, or the fixture folder named by the first argument (e.g. submittal-project).
# 2. Under `claude plugin eval`, gives the run the toolkit's Python environment.
#    Each eval run gets a fresh, sandboxed HOME with no network, so
#    bin/construction-python could not build its venv there. Build it once in
#    .eval-home at the plugin root (this script runs outside the sandbox) and
#    link it into the run's HOME. The harness (evals/harness) runs with the
#    user's own HOME and venv and sets CONSTRUCTION_EVAL_HARNESS=1 to skip this.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN="$(cd "$HERE/../../.." && pwd)"
CACHE_HOME="$PLUGIN/.eval-home"  # outside the eval dir: cases may not contain symlinks

FIXTURE="${1:-sample-project}"
cp -R "$HERE/$FIXTURE/." .

[ "${CONSTRUCTION_EVAL_HARNESS:-0}" = "1" ] && exit 0

# A no-op when the cached venv is already in sync with requirements.txt
HOME="$CACHE_HOME" "$PLUGIN/bin/construction-python" -c 'pass' >&2
if [ ! -f "$CACHE_HOME/.construction-skills/venv/.requirements-installed" ]; then
  echo "Could not build the eval Python environment in $CACHE_HOME (see above)." >&2
  exit 1
fi
mkdir -p "$HOME/.construction-skills"
ln -s "$CACHE_HOME/.construction-skills/venv" "$HOME/.construction-skills/venv"
