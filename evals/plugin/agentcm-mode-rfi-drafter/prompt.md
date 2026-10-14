---
name: agentcm-mode-rfi-drafter
description: "AgentCM closed: researches through AgentCM's files and AgentCM's real crop.sh, where D101's hardware points to a keynote the files do not hold, and writes the RFI outside .construction/."
tags: [agentcm-mode, rfi-drafter]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:rfi-drafter

Draft an RFI asking the architect to confirm the hardware for door D101: the A-601 door schedule gives its size but the hardware column needs confirming. Research it in the project documents first and look at the schedule on the drawing.
