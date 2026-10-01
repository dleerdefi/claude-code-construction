---
name: submittal-log-generator
description: Starts from an unsplit manual, so the skill must run spec-splitter itself, then build the submittal log.
tags: [smoke, submittal-log-generator]
runs: 1
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a sample construction project. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:submittal-log-generator
