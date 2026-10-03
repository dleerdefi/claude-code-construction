---
name: pe-review
description: Reviews door 220 against the real A500 schedule and a synthetic Addendum 01 that revises it; the known answer is a CONFLICTING finding with the addendum governing.
tags: [real, pe-review]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:pe-review

Review door 220. Does the door schedule on sheet A500 (01 - Drawings) agree with Addendum 01 (04 - Addenda)? Report every finding in the skill's format with severity, type, priority and status, cite both sources, and say which document governs.
