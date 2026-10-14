---
name: agentcm-mode-construction-guide
description: "AgentCM closed: answers from AgentCM's files, and looks at D103's row through AgentCM's real crop.sh, where the drawing shows what the files do not."
tags: [agentcm-mode, construction-guide]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:construction-guide

From this project's documents: what size is door D103 on the A-601 door schedule, and what refers to sheet A-102? Look at the drawing to confirm the door's size, and report anything the drawing shows at that row that the text does not. Cite where each answer comes from.
