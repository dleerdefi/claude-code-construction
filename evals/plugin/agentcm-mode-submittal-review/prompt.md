---
name: agentcm-mode-submittal-review
description: "AgentCM closed: reviews a synthetic 08 11 13 submittal against AgentCM's specs/ and the A-601 door schedule."
tags: [agentcm-mode, submittal-review]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:submittal-review

Review the submittal package in 06 - Submittals/.
