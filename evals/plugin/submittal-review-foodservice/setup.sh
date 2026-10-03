#!/usr/bin/env bash
# Copy the prepared foodservice project in and link the eval Python environment.
# The fixture keeps its .construction/ folder as dot-construction/ (the repository
# ignores .construction/), so restore the real name after copying.
set -euo pipefail
bash "$(dirname "${BASH_SOURCE[0]}")/../_fixtures/prepare-workspace.sh" foodservice-project
mv dot-construction .construction
