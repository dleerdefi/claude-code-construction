---
type: regex
target: tool_inputs
pattern: '\.construction[\\/]+(?:specs[\\/]+)|\bcd\s+[^&;|]*?\.construction[\\/]*\\?[\"'']?\s*(?:&&|;|\\n).*?(?:[\s\"''=]|\./)(?:specs[\\/]+)'
weight: 2
---
The skill read the spec text from AgentCM's specs/, not its own extraction.
