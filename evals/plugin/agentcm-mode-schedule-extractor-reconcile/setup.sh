#!/usr/bin/env bash
# AgentCM's contract fixture in the workspace, AgentCM running (the stand-in API), crop.sh the eval stand-in (needs: schedule-id).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$HERE/../agentcm-mode/setup-fixture.sh" --api --crop-stub schedule-id
"$HERE/../../../bin/construction-python" "$HERE/../agentcm-mode/make_edited_schedule.py" .
bash "$HERE/../agentcm-mode/baseline.sh"
