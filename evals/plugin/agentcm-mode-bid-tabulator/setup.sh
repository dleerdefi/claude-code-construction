#!/usr/bin/env bash
# AgentCM's contract fixture in the workspace, AgentCM closed.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/../agentcm-mode/setup-fixture.sh" 
bash "$HERE/../_fixtures/prepare-real-workspace.sh" bids
bash "$HERE/../agentcm-mode/baseline.sh"
