#!/usr/bin/env bash
# AgentCM's contract fixture in the workspace, AgentCM closed, crop.sh the eval stand-in (needs: specs unread-manual pdfs).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/../agentcm-mode/setup-fixture.sh" --crop-stub specs unread-manual pdfs

bash "$HERE/../agentcm-mode/baseline.sh"
