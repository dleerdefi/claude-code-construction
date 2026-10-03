---
name: sheet-splitter-real
description: Splits the real 8-sheet mechanical set and names each sheet from its printed title block; graded against the sheet list read from the title blocks.
tags: [real, sheet-splitter]
runs: 1
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:sheet-splitter

Split the drawing set in "01 - Drawings" (the mechanical set) into one PDF per sheet, named from the printed title blocks.
