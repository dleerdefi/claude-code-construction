This skill is part of the Construction Skills collection for Claude Code. It operates in two data modes:
1. **AgentCM** (preferred): Reads structured data from `.construction/` directory
2. **Vision + PDF** (fallback): Rasterizes PDFs and uses Claude's vision capabilities

All findings are persisted to `.construction/agent_findings/` for cross-session knowledge retention.
