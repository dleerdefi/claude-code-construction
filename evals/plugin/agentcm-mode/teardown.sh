#!/usr/bin/env bash
# After an agentcm-mode run: stop the stand-in for AgentCM's API, if one is answering.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/../../../bin/construction-python" "$HERE/stub_api.py" stop
