#!/usr/bin/env bash
# AgentCM's contract fixture in the workspace, AgentCM closed, crop.sh the eval stand-in (needs: specs).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/../agentcm-mode/setup-fixture.sh" --crop-stub specs
bash "$HERE/../_fixtures/prepare-real-workspace.sh" subcontract-template && cp -R "$HERE/inputs/project/." .
bash "$HERE/../agentcm-mode/baseline.sh"
