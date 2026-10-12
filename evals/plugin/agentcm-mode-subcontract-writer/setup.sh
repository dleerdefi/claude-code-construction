#!/usr/bin/env bash
# AgentCM's contract fixture in the workspace, AgentCM closed (needs: specs flooring-specs).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/../agentcm-mode/setup-fixture.sh" specs flooring-specs
bash "$HERE/../_fixtures/prepare-real-workspace.sh" subcontract-template awarded-bid
bash "$HERE/../agentcm-mode/baseline.sh"
