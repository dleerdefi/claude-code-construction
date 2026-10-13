---
type: regex
target: tool_inputs
pattern: '\.construction[\\/]+(?:project\.yaml)|\bcd\s+[^&;|]*?\.construction[\\/]*\\?[\"'']?\s*(?:&&|;|\\n).*?(?:[\s\"''=]|\./)(?:project\.yaml)'
weight: 1
---
The run read .construction/project.yaml: it decided the mode from AgentCM's marker.
