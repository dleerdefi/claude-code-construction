---
name: project-setup
description: Inventories the sample project and appends construction context to CLAUDE.md without touching AgentCM data.
tags: [smoke, project-setup]
runs: 1
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a sample construction project. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:project-setup
