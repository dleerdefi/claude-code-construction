---
type: regex
target: tool_inputs
pattern: '\.construction[\\/]+(?:INDEX\.md|sheets[\\/]+|schedules[\\/]+|tags\.tsv|xrefs\.tsv|specs[\\/]+|index[\\/]+sheet_index\.yaml)|\bcd\s+[^&;|]*?\.construction[\\/]*\\?[\"'']?\s*(?:&&|;|\\n).*?(?:[\s\"''=]|\./)(?:INDEX\.md|sheets[\\/]+|schedules[\\/]+|tags\.tsv|xrefs\.tsv|specs[\\/]+|index[\\/]+sheet_index\.yaml)'
weight: 1
---
The run read AgentCM's files (INDEX.md, the sheet files, schedules, tags, xrefs, specs, the sheet index).
