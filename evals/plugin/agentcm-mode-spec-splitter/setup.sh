#!/usr/bin/env bash
# AgentCM's contract fixture in the workspace, AgentCM closed (needs: specs unread-manual pdfs).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/../agentcm-mode/setup-fixture.sh" specs unread-manual pdfs

bash "$HERE/../agentcm-mode/baseline.sh"
