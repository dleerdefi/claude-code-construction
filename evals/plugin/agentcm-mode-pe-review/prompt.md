---
name: agentcm-mode-pe-review
description: "AgentCM closed: reviews from AgentCM's files and looks at the drawings through AgentCM's real crop.sh, where A-101 shows a callout bubble the files do not."
tags: [agentcm-mode, pe-review]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:pe-review

Review sheets A-101 and A-102 of this project for coordination problems and anything missing. Look at the drawings where the text points.
