---
name: agentcm-mode-schedule-extractor
description: "AgentCM running: ingests with A-601's id from sheet_index.yaml and the contract's payload."
tags: [agentcm-mode, schedule-extractor]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:schedule-extractor

Extract the door schedule on A-601 into Excel and ingest it into AgentCM.
