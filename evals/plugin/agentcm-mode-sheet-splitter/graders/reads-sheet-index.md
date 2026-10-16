---
type: regex
target: tool_inputs
pattern: '\.construction[\\/]+(?:index[\\/]+sheet_index\.yaml)|\bcd\s+[^&;|]*?\.construction[\\/]*\\?[\"'']?\s*(?:&&|;|\\n).*?(?:[\s\"''=]|\./)(?:index[\\/]+sheet_index\.yaml)'
weight: 1
---
It read AgentCM's sheet index to confirm the split.
