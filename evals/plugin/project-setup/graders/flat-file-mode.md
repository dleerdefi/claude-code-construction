---
type: regex
target: { source: file, path: CLAUDE.md }
pattern: "Operational mode: Flat File"
weight: 2
---
Another skill's finding is already in `.construction/skills/bid-tabulator/findings/` when the run starts (setup.sh). The skill still detects flat-file mode, since only `.construction/project.yaml` means AgentCM, and appends its flat-file block.
