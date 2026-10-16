---
name: control-idle
description: The harness's idle control. The session runs one harmless shell command and answers; no skill runs and nothing is written. Whatever the run leaves outside its project folder is Claude Code's own, or noise. It confirms by name the entries the outside-write check allows in the run's temp folder (leftovers.py CLAUDE_CODE_OWN), and must come back clean.
tags: [control]
runs: 1
max_turns: 4
timeout_seconds: 300
allowed_tools: [Bash]
append_system_prompt: "This is the eval harness's idle control run. Do exactly what the prompt says and nothing else: no skills, no files written."
---

Run `ls` once with the Bash tool, then reply with the single word DONE. Do not write or change any file.
