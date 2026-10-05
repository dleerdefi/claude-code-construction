---
type: tool_used
tool: Bash
input_match: 'Specification Sections[\s\S]*(?:\.pdf|pdf_text\.py)|pdf_text\.py[\s\S]*Specification Sections'
weight: 2
---
At least one Bash call reads a specification section PDF, by path or through pdf_text.py after changing into the sections folder (Step 1a is never skipped; the scope baseline comes from the sections, not the scope sheet alone). A directory listing in a tool result does not count; a bare `ls` of the folder does not either.
