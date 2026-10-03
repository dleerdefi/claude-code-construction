---
name: schedule-extractor
description: Extracts the real A500 door schedule (53 doors, two-row header) to Excel; graded cell-by-cell against a transcription of the sheet.
tags: [real, schedule-extractor]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task."
---

/construction:schedule-extractor

Extract the door schedule from sheet A500 ("01 - Drawings/A500 - DOOR SCHEDULE, DOOR AND FRAME TYPES.pdf", page 1) to Excel. Save the intermediate data as `schedule_data.json` and the workbook as `Door_Schedule_A500.xlsx`, both in the project root. Keep the schedule's own column names (the header has two rows: group names such as DOOR PANEL LEAF over WIDTH, HEIGHT, TYPE, MATERIAL) and one row per door.
