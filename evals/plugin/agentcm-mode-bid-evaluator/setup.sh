#!/usr/bin/env bash
# AgentCM's contract fixture in the workspace, AgentCM closed (needs: specs).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/../agentcm-mode/setup-fixture.sh" specs
cp -R "$HERE/inputs/project/." . && mkdir -p .construction/skills/bid-tabulator/bids && cp "$HERE/inputs/tabulated/"*.json .construction/skills/bid-tabulator/bids/
bash "$HERE/../agentcm-mode/baseline.sh"
