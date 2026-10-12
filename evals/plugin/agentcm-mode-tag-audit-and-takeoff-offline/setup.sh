#!/usr/bin/env bash
# AgentCM's contract fixture in the workspace, AgentCM closed (needs: groups pending pdfs api-url).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/../agentcm-mode/setup-fixture.sh" groups pending pdfs api-url

bash "$HERE/../agentcm-mode/baseline.sh"
