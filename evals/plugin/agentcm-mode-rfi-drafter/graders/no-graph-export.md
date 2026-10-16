---
type: regex
target: tool_inputs
pattern: 'graph/export|\.construction[\\/]+(?:rasters|extractions)|\bcd\s+[^&;|]*?\.construction[\\/]*\\?[\"'']?\s*(?:&&|;|\\n).*?(?:[\s\"''=]|\./)(?:rasters|extractions)'
match: not_contains
weight: 1
---
Nothing outside the contract: no graph/export, rasters/ or extractions/.
