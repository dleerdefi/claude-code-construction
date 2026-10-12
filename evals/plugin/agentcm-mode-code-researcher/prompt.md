---
name: agentcm-mode-code-researcher
description: "AgentCM closed: reads AgentCM's specs/ and sheet files and looks through crop.sh."
tags: [agentcm-mode, code-researcher]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:code-researcher

What do the specifications require of the hollow metal doors and frames, and which codes and standards do they cite?
