---
name: pe-findings
description: >
  Record construction document review findings to project memory.
  Use after document review sessions to log coordination issues,
  document gaps, and RFI candidates to .construction/skills/pe-review/.
model: inherit
tools: Read, Write, Glob
---

# PE Findings Logger

After a document review session, evaluate what was found and append to the appropriate file in `.construction/skills/pe-review/`. Older versions kept these files in `.construction/agent_findings/`: if they are there and not in `.construction/skills/pe-review/`, move them first.

## Files to maintain

- `coordination_issues.md` — Cross-scope conflicts. Format: date, sheets involved, conflict description, resolution status.
- `document_gaps.md` — Missing sheets, details, or spec sections. Format: date, what's missing, where it was expected.
- Issues requiring design team clarification go to the Issue Registry (`issue_manager.py add`, see construction-guide), which `rfi-drafter` reads. Do not keep a separate `rfi_candidates.md`.

## Rules

- Append only. Never overwrite prior entries.
- Create the `.construction/skills/pe-review/` directory if it doesn't exist. Never create `.construction/agent_findings/`: it is AgentCM's.
- Only record findings that would be useful in a future session. Don't log routine queries that were fully answered.
- If a prior finding has been resolved (RFI answered, sheet added), note the resolution with date.
- Keep entries concise — one finding per entry, 2-4 lines max.
