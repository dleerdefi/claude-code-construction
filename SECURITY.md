# Security

<!-- TODO (David, AgentCM plan decision D7): the security contact. Align this file's wording with AgentCM's SECURITY.md when it lands. -->

## Reporting a vulnerability

Please don't open a public issue. Report it privately to **[security contact to be added]**. Say what you found, how to reproduce it, and which version of the plugin you ran (`version` in `.claude-plugin/plugin.json`).

## Supported versions

Only the latest release gets fixes. Marketplace installs update when a new version is released. A clone updates with `git pull`.

## What the plugin does on your machine

The plugin is a set of Claude Code skills and the Python scripts they run. It has no server and no service of its own.

- **Files it reads:** the project documents in the folder Claude Code is opened in. With AgentCM, also AgentCM's files under `.construction/`. It never reads AgentCM's database: the commit gate (`dev/check_no_queries.py`) fails on any query wrapper, `query_command` or `psql` in what the plugin ships.
- **Files it writes:** deliverables (spreadsheets, Word documents, split PDFs) in the project folder, and working data in `.construction/skills/`. Nothing else under `.construction/`. Outside the project, it writes only its Python environment, `~/.construction-skills/venv`.
- **Scripts:** skills run only the scripts in this repository and never write their own. The evals grade this.
- **Network:**
  - The first time a script runs, `pip` installs `requirements.txt` from PyPI into that environment.
  - With AgentCM, two skills use AgentCM's local API at the `api_url` in `.construction/database.yaml`, on 127.0.0.1 (`reference/agentcm-mode.md`). schedule-extractor and tag-audit-and-takeoff send to its three write endpoints. schedule-extractor also makes its one read, a schedule's rows, for the Excel round trip.
  - code-researcher uses Claude Code's web search to confirm which code edition a jurisdiction has adopted, and the code's exact wording.
  - Nothing else goes out from the plugin. What Claude Code itself sends (the documents it reads, under your own account) is governed by your Claude Code settings and Anthropic's terms.

## Keeping your documents private

Drawings, specifications, bids and submittals are often confidential. Never attach a client's documents to an issue or a pull request without permission. A crop of the area in question is enough.
