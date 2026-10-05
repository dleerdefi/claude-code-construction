---
name: code-researcher
description: Offline code research on the real G010 code summary, A101 plan and Division 01 excerpts; graded on the project facts it reads, the research framing rule and uncertainty handling.
tags: [real, code-researcher]
runs: 1
max_turns: 100
timeout_seconds: 1800
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task. At each of the skill's human checkpoints, state the outline or findings and continue as if the user had approved. Web access is not available in this run: do not attempt web searches; mark every code requirement you cannot verify from the project documents or the toolkit's reference tables as uncertain or needs_review, never as confirmed."
---

/construction:code-researcher means of egress for the apparatus bay and first floor

Read the project context from sheet G010 (code summary) and the Division 01 sections in the project manual, then run the research for the scope above and write the report to the project root.
