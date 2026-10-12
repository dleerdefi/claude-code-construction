---
name: agentcm-mode-subcontract-writer
description: "AgentCM closed: reads the scope's spec sections from AgentCM's specs/. Waits for spec sections matching the BP-09 bids."
tags: [agentcm-mode, subcontract-writer]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:subcontract-writer

Write the BP-09 Flooring subcontract for the awarded bidder from the firm's template.
