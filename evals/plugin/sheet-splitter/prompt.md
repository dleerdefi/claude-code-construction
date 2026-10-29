---
name: sheet-splitter
description: Splits the 4-sheet set, names sheets from the printed title blocks (A-201 bookmark is wrong on purpose), writes the index in the drawings folder, and records the drawing index's planted mismatches (A-101's title, S-101's number, S-201 the one S sheet missing, half the A sheets missing, a landscape discipline not in the folder) in a finding the summary names, logging the two that need an RFI in the issue registry and a folder finding, with no RFI, for each discipline with two or more sheets missing.
tags: [smoke, sheet-splitter]
runs: 1
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a sample construction project. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:sheet-splitter
