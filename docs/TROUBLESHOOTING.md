# Troubleshooting

## Setup Issues

### "Python not found" / "Python 3.10+ not found"
Install Python 3.10+ from [python.org](https://www.python.org/downloads/). On Windows, check "Add Python to PATH" during installation (the `py` launcher also works). On macOS, Apple's built-in `python3` is 3.9, which is too old: install Python from python.org or with `brew install python`, then re-run `./setup`.

### Windows: "bash\r: No such file or directory" or "set: pipefail: invalid option name"
The scripts were checked out with Windows line endings. Current versions prevent this; if you see it, your clone predates the fix: delete it and clone again (or run `git rm -r --cached . && git reset --hard` inside it).

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
That's fine: skills work without AgentCM, an optional separate tool whose projects are marked by `.construction/project.yaml`. Skills create `.construction/skills/` for their own working data on first use; your deliverables are always saved in the project folder. Run `/construction:project-setup` to inventory your project files.

### Schedule extraction returns few or no rows
The skill uses two methods: pdfplumber table extraction first, then vision (it rasterizes the sheet and reads the schedule from the image) when pdfplumber finds no table or the result looks garbled. If both give poor results:
- Check the PDF has a text layer (not a scanned image); without one, pdfplumber finds nothing and the result depends on vision alone
- Try on a different sheet — some schedule layouts are harder to parse than others
- Ask for a specific sheet and schedule (for example "the door schedule on A-3.2") so the skill targets the right table
- Check the row and column counts the skill reports against the schedule on the sheet

### "pdfplumber not installed" or import errors
Skills run Python through `bin/construction-python`, which creates the venv at `~/.construction-skills/venv/` on first use and re-installs `requirements.txt` whenever it changes. To force a re-install, delete `~/.construction-skills/venv/.requirements-installed` and run `./setup` (or any skill) again. To do it by hand (on Windows use `Scripts/python` instead of `bin/python`):
```bash
~/.construction-skills/venv/bin/python -m pip install -r requirements.txt
```
Offline or locked-down machine? Set `CONSTRUCTION_SKILLS_NO_BOOTSTRAP=1` to stop the automatic install and use the Python already on your PATH.

### Submittal log has too many items, or items look wrong
The skill reads every spec section's extracted text and pulls submittal requirements from Part 1 (SUBMITTALS articles and others such as quality assurance and closeout), and from Parts 2 and 3 where a product or execution article requires one. It runs spec-splitter itself if spec text is missing, so you don't need to run it first. To judge the results:
- Check the **Confidence** column, and read the **Flag Reason** column on flagged items: these are the ones to check against the spec
- Open the **Extraction QA** sheet: it lists each spec section's extraction method, quality rating, items extracted and flagged items
- Sections rated DEGRADED or POOR in `.construction/skills/spec_text/manifest.json` have poor text extraction, and their items get a minimum confidence of MEDIUM. Check those sections against the source PDF

### Code research assumes the wrong jurisdiction
The skill is `/construction:code-researcher`. It writes its project context, including the city, state and authority having jurisdiction (AHJ), to `.construction/skills/code-researcher/project_context.yaml`. `/construction:project-setup` does not write a project context file; it appends project context to your `CLAUDE.md`. If the jurisdiction is wrong:
- Give the city, state and AHJ in your prompt
- Or correct the values in `project_context.yaml` and run the skill again

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
No. All skills work standalone: they rasterize PDF pages with the plugin's own scripts and read them as images, and never read PDFs directly. AgentCM is an optional structured data layer that makes skills faster and more accurate by pre-indexing drawings and specs.

## Getting Help

- File issues at the [GitHub repository](https://github.com/dleerdefi/claude-code-construction/issues)
- See [evals/plugin/README.md](../evals/plugin/README.md) for the eval cases, and `evals/plugin/_fixtures/sanibel/ground_truth/` for expected outputs on the Sanibel test set
- See [Running Evals](RUNNING_EVALS.md) to verify skills work on your documents
