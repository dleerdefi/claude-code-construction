#!/usr/bin/env bash
# AgentCM's contract fixture in the workspace, AgentCM running (the stand-in API), AgentCM's real crop.sh (needs: pdfs).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/../agentcm-mode/setup-fixture.sh" --api pdfs

bash "$HERE/../agentcm-mode/baseline.sh"
