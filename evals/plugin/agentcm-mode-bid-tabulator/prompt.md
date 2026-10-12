---
name: agentcm-mode-bid-tabulator
description: "AgentCM closed: takes the project name from project.yaml and keeps its working data under .construction/skills/."
tags: [agentcm-mode, bid-tabulator]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder that AgentCM manages. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:bid-tabulator

Tabulate the five BP-09 Flooring bids in 03 - Subcontractor Bids/BP-09 Flooring/ into a bid comparison workbook named Bid_Tabulation_BP-09.xlsx in the project root.
