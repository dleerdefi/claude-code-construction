---
name: spec-splitter-real
description: Splits a real 9-section project manual (Division 01 and 09 excerpts) into section PDFs and extracted text; graded against the section list.
tags: [real, spec-splitter]
runs: 1
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:spec-splitter
