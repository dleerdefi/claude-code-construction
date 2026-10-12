---
name: agentcm-mode-submittal-review
description: "AgentCM closed: reads the governing sections from AgentCM's specs/ and the trace from tags.tsv and xrefs.tsv. Waits for a submittal against one of the fixture's sections."
tags: [agentcm-mode, submittal-review]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:submittal-review

Review the submittal package in 06 - Submittals/.
