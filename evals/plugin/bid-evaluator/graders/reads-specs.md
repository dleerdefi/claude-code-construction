---
type: regex
target: trace
pattern: '"type": "tool_use".*Specification Sections.{1,120}?\.pdf'
weight: 2
---
At least one tool call opens a specification section PDF (Step 1a is never skipped; the scope baseline comes from the sections, not the scope sheet alone). The match is on a tool_use line so a directory listing in a tool result does not count.
