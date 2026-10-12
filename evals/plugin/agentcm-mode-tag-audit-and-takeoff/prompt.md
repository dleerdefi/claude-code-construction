---
name: agentcm-mode-tag-audit-and-takeoff
description: "AgentCM running: a takeoff twice gives the same three numbers, confirmed = accepted tags only; a tag sent again is already held, a rejected one is listed once."
tags: [agentcm-mode, tag-audit-and-takeoff]
runs: 1
max_turns: 150
timeout_seconds: 2700
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:tag-audit-and-takeoff

Do a quantity takeoff of the room tags on sheets A-101 and A-102 and save its QTO JSON and workbook. Then run the same takeoff a second time from scratch, as a new session would (read AgentCM's files again and look at the sheets again), save its own QTO JSON and workbook, and report both runs' confirmed, to confirm and possible totals. Ingest new detections without asking; nobody can confirm.
