---
name: agentcm-mode-subcontract-writer
description: "AgentCM closed: writes the BP-08 subcontract for the synthetic awarded bid, its scope from 08 11 13 in AgentCM's specs/."
tags: [agentcm-mode, subcontract-writer]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:subcontract-writer

Write the BP-08 Hollow Metal Frames and Doors subcontract for the awarded bidder from the firm's template.
