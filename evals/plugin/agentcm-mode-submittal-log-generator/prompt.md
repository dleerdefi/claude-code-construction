---
name: agentcm-mode-submittal-log-generator
description: "AgentCM closed: reads AgentCM's specs/ text, and runs spec-splitter only for a manual AgentCM could not read."
tags: [agentcm-mode, submittal-log-generator]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:submittal-log-generator

Generate the submittal register for this project.
