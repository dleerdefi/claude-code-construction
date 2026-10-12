---
name: agentcm-mode-project-setup
description: "AgentCM closed: reports AgentCM's orientation from INDEX.md and changes nothing."
tags: [agentcm-mode, project-setup]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:project-setup


