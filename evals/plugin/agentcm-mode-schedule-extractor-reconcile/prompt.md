---
name: agentcm-mode-schedule-extractor-reconcile
description: "AgentCM running: the Excel round trip reads the stored rows from the rows endpoint and reconciles the PE's edit."
tags: [agentcm-mode, schedule-extractor]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:schedule-extractor

The PE edited the schedule they exported from AgentCM; the workbook is in the project root, named "... Schedule (PE edits).xlsx". Apply their changes back to AgentCM.
