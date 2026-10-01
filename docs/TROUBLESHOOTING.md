# Troubleshooting

## Setup Issues

### "Python not found" / "Python 3.10+ not found"
Install Python 3.10+ from [python.org](https://www.python.org/downloads/). On Windows, check "Add Python to PATH" during installation (the `py` launcher also works). On macOS, Apple's built-in `python3` is 3.9, which is too old: install Python from python.org or with `brew install python`, then re-run `./setup`.

### Windows: "bash\r: No such file or directory" or "set: pipefail: invalid option name"
The scripts were checked out with Windows line endings. Current versions prevent this; if you see it, your clone predates the fix: delete it and clone again (or run `git rm -r --cached . && git reset --hard` inside it).

### "pip permission error" or "Access denied"
Use the `--user` flag:
```bash
python -m pip install --user -r requirements.txt
```
Or run the setup script which creates an isolated venv automatically.

### "Skill not found" / Skills don't appear in autocomplete
The skills ship as the `construction` plugin, so their commands are namespaced: type `/construction:` to list them.

If none appear:
- The clone must sit directly at `~/.claude/skills/construction` (all projects) or `<project>/.claude/skills/construction` (one project), with `.claude-plugin/plugin.json` at its top. Cloned somewhere else? Run `./setup --global`, or `setup --project` from your project folder.
- Start a new session or run `/reload-plugins`. Per-project installs load once you trust the project folder.
- Check `/plugin` (Installed tab), or run `claude plugin list` in a terminal: you should see `construction@skills-dir` (clone) or `construction@construction-skills` (marketplace).
- Organizations that restrict plugin marketplaces can block plugins in skills directories; install from the marketplace instead, or ask your admin.

### Old skills show up twice, or a command runs an old version
Earlier versions linked (or, on Windows, copied) each skill into `~/.claude/skills/<skill>`. Pull the update and run `./setup` once: it removes those links and moves old copies to `~/.construction-skills/old-skill-copies/`.

### Setup hangs on Windows
The venv creation or pip install may take a minute on Windows. If it hangs longer than 5 minutes, try:
```bash
py -3 -m venv ~/.construction-skills/venv
~/.construction-skills/venv/Scripts/python -m pip install -r requirements.txt
cp requirements.txt ~/.construction-skills/venv/.requirements-installed
```

## Skill Issues

### "PDF too large for vision"
This is expected for construction drawings (26-60MB). Skills automatically rasterize large PDFs to PNG using PyMuPDF — no action needed. The rasterized PNG is typically 2-8MB and works with vision.

### "No .construction/ directory"
That's fine: skills work without [AgentCM](https://github.com/dleerdefi/AgentCM), which creates `.construction/` (marked by `.construction/project.yaml`). Skills create `.construction/skills/` for their own working data on first use; your deliverables are always saved in the project folder. Run `/construction:project-setup` to inventory your project files.

### Schedule extraction returns few or no rows
The skill tries pdfplumber first, then falls back to text extraction, then vision. If all fail:
- Check the PDF has a text layer (not a scanned image)
- Try on a different sheet — some schedule layouts are harder to parse than others
- The rasterized PNG will be saved in the output for manual review

### "pdfplumber not installed" or import errors
Skills run Python through `bin/construction-python`, which creates the venv at `~/.construction-skills/venv/` on first use and re-installs `requirements.txt` whenever it changes. To force a re-install, delete `~/.construction-skills/venv/.requirements-installed` and run `./setup` (or any skill) again. To do it by hand (on Windows use `Scripts/python` instead of `bin/python`):
```bash
~/.construction-skills/venv/bin/python -m pip install -r requirements.txt
```
Offline or locked-down machine? Set `CONSTRUCTION_SKILLS_NO_BOOTSTRAP=1` to stop the automatic install and use the Python already on your PATH.

### Submittal log has too many items
The v3 extractor parses only under SUBMITTALS headings in Part 1 of each spec section. If you're still seeing noise:
- Run `/construction:spec-splitter` first to split the project manual — the extractor works better on individual section PDFs
- Division 01 items are separated to a "General Requirements" tab in the Excel output

### Code compliance checker gives incorrect jurisdiction
The skill reads the project location from the title block. If it misidentifies the location:
- Run `/construction:project-setup` first so the project context file has the correct city/state
- The skill will use `.construction/project_context.yaml` if it exists

## File Organization

### "Where do I put my PDFs?"
Skills look for drawings and specs in your project directory. A typical structure:
```
my-project/
  drawings/           # or "01 - Drawings/"
    A-1.1.pdf
    A-3.2.pdf
  specs/              # or "02 - Specifications/"
    project_manual.pdf
```

The exact folder names don't matter — `/construction:project-setup` will find and classify files anywhere in your project directory.

### "Do I need AgentCM?"
No. All skills work standalone with Claude Code's built-in vision and PDF tools. AgentCM is an optional structured data layer that makes skills faster and more accurate by pre-indexing drawings and specs.

## Getting Help

- File issues at the [GitHub repository](https://github.com/dleerdefi/claude-code-construction/issues)
- Check `evals/` for test cases and expected outputs
- See [Running Evals](RUNNING_EVALS.md) to verify skills work on your documents
