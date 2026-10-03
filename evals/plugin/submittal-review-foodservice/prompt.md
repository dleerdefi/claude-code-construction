---
name: submittal-review-foodservice
description: Reviews a 366-page foodservice equipment product data package with four planted defects (a scheduled item missing, a condensing unit voltage buried on page 15, a short hood buried on page 206, an unscheduled extra item) and must pass its own completeness gate.
tags: [submittal-review, large-pdf]
runs: 1
max_turns: 250
timeout_seconds: 3600
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill, Agent]
append_system_prompt: "This is an unattended evaluation run in a sample construction project. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task. There is no web access, so no code research can be done."
---

/construction:submittal-review "06 - Submittals/11 40 00-001 R0 Foodservice Equipment Product Data.pdf"

In your final message, list every finding with its id, severity, owner and governing source, then the suggested GC action, the coordination routing, and the code questions.
