---
name: agentcm-mode-bid-evaluator
description: "AgentCM closed: evaluates three synthetic BP-08 bids against 08 11 13, read from AgentCM's specs/."
tags: [agentcm-mode, bid-evaluator]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:bid-evaluator

Evaluate the tabulated BP-08 Hollow Metal Frames and Doors bids against the specifications.
