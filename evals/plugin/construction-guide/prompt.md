---
name: construction-guide
description: Answers a known-answer question from the real A500 door schedule the way the guide prescribes (rasterize, never read the PDF directly, cite the sheet).
tags: [real, construction-guide]
runs: 1
max_turns: 60
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:construction-guide

Using the drawings in this project, answer from sheet A500: for door 220, what are the door leaf width and height, the leaf type and material, the frame type and material, the door/frame fire rating, the hardware set, and the head detail reference? Cite the sheet for each value and label your confidence as the guide prescribes.
