---
name: agentcm-mode-spec-splitter
description: "AgentCM closed: splits and extracts only the manual INDEX.md lists as not read; never re-splits one AgentCM read."
tags: [agentcm-mode, spec-splitter]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:spec-splitter


