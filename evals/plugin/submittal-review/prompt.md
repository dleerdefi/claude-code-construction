---
name: submittal-review
description: Reviews a lab casework shop drawing submittal with four planted defects (wrong sink cutout, accessible station height, in-wall brackets "by others", a missing elevation) and must pass its own completeness gate.
tags: [smoke, submittal-review]
runs: 1
max_turns: 200
timeout_seconds: 3000
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill, Agent]
append_system_prompt: "This is an unattended evaluation run in a sample construction project. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task. There is no web access, so no code research can be done."
---

/construction:submittal-review "06 - Submittals/12 35 53-001 R0 Laboratory Casework Shop Drawings.pdf"

In your final message, list every finding with its id, severity, owner and governing source, then the suggested GC action, the coordination routing, and the code questions.
