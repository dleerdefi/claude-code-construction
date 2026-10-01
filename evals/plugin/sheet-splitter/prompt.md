---
name: sheet-splitter
description: Splits the 4-sheet set, names sheets from the printed title blocks (A-201 bookmark is wrong on purpose) and writes the index in the drawings folder.
tags: [smoke, sheet-splitter]
runs: 1
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a sample construction project. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:sheet-splitter
