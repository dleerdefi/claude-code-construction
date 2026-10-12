---
name: agentcm-mode-tag-audit-and-takeoff-offline
description: "AgentCM closed: the takeoff runs from the files and the tag ingest waits in the outbox."
tags: [agentcm-mode, tag-audit-and-takeoff]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:tag-audit-and-takeoff

Do a quantity takeoff of the room tags on sheet A-101 and save its QTO JSON and workbook. Ingest new detections without asking; nobody can confirm.
