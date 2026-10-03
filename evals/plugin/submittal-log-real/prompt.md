---
name: submittal-log-real
description: Builds a submittal log from a real 4-section manual (01 33 00, 09 30 00, 09 65 13, 09 65 40), running spec-splitter itself first; graded against the Part 1 submittal articles.
tags: [real, submittal-log-generator]
runs: 1
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:submittal-log-generator
