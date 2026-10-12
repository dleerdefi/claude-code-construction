#!/usr/bin/env bash
# The last step of an agentcm-mode case's setup: record the fixture as setup left it.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/../../../bin/construction-python" "$HERE/baseline.py" .
