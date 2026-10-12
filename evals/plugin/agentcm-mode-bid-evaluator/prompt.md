---
name: agentcm-mode-bid-evaluator
description: "AgentCM closed: reads the bid's spec sections from AgentCM's specs/. Waits for spec sections matching the BP-09 bids."
tags: [agentcm-mode, bid-evaluator]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:bid-evaluator

Evaluate the tabulated BP-09 Flooring bids against the specifications.
