#!/usr/bin/env bash
# AgentCM's contract fixture in the workspace, AgentCM closed, AgentCM's real crop.sh (needs: specs pdfs).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/../agentcm-mode/setup-fixture.sh" specs pdfs
cp -R "$HERE/inputs/project/." .
bash "$HERE/../agentcm-mode/baseline.sh"
