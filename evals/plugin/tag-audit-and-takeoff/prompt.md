---
name: tag-audit-and-takeoff
description: Flat-file door tag audit of the real A101 first-floor plan; graded against the door numbers the sheet actually carries.
tags: [real, tag-audit-and-takeoff]
runs: 1
max_turns: 100
timeout_seconds: 1800
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder without AgentCM (flat file mode). Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task. At the skill's confirmation gates, state your plan or interim count and continue as if the user had approved."
---

/construction:tag-audit-and-takeoff

Audit the door tags on sheet A101 ("01 - Drawings/A101 - ARCHITECTURAL PLAN - FIRST FLOOR.pdf", one page). Rasterize the sheet, find every door tag on the plan, and produce the QTO JSON and the Excel workbook. Name the workbook `QTO_Door_Tags.xlsx` in the project root. Count door tags only (not room tags or detail callouts), and list each door number you find.
