---
type: regex
target: trace
pattern: "graph/export|\\.construction[\\\\/]+rasters|\\.construction[\\\\/]+extractions"
match: not_contains
weight: 1
---
Nothing outside the contract: no graph/export, rasters/ or extractions/.
