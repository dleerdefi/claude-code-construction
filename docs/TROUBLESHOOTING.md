# Troubleshooting

## Setup Issues

### "Python not found"
Install Python 3.10+ from [python.org](https://www.python.org/downloads/). On Windows, check "Add Python to PATH" during installation.

### "pip permission error" or "Access denied"
Use the `--user` flag:
```bash
python -m pip install --user -r requirements.txt
```
Or run the setup script which creates an isolated venv automatically.

### "Skill not found" / Skills don't appear in autocomplete
Run setup to register skills with Claude Code:
```bash
cd ~/.claude/skills/construction  # or wherever you cloned
./setup --global
```

Then verify: start Claude Code and type `/` — you should see construction skills listed.

### Setup hangs on Windows
The venv creation or pip install may take a minute on Windows. If it hangs longer than 5 minutes, try:
```bash
python -m venv ~/.construction-skills/venv
~/.construction-skills/venv/Scripts/pip install -r requirements.txt
```

## Skill Issues

### "PDF too large for vision"
This is expected for construction drawings (26-60MB). Skills automatically rasterize large PDFs to PNG using PyMuPDF — no action needed. The rasterized PNG is typically 2-8MB and works with vision.

### "No .construction/ directory"
Run `/project-onboarding` first. It creates the `.construction/` directory with indexes and context.

### Schedule extraction returns few or no rows
The skill tries pdfplumber first, then falls back to text extraction, then vision. If all fail:
- Check the PDF has a text layer (not a scanned image)
- Try on a different sheet — some schedule layouts are harder to parse than others
- The rasterized PNG will be saved in the output for manual review

### "pdfplumber not installed" or import errors
The setup script installs deps into a venv at `~/.construction-skills/venv/`. Skills use `bin/construction-python` which auto-detects this venv. If it's not working:
```bash
~/.construction-skills/venv/bin/pip install pdfplumber openpyxl PyYAML Pillow PyMuPDF
```

### Submittal log has too many items
The v3 extractor parses only under SUBMITTALS headings in Part 1 of each spec section. If you're still seeing noise:
- Run `/spec-splitter` first to split the project manual — the extractor works better on individual section PDFs
- Division 01 items are separated to a "General Requirements" tab in the Excel output

### Code compliance checker gives incorrect jurisdiction
The skill reads the project location from the title block. If it misidentifies the location:
- Run `/project-onboarding` first so the project context file has the correct city/state
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

The exact folder names don't matter — `/project-onboarding` will find and classify files anywhere in your project directory.

### "Do I need AgentCM?"
No. All skills work standalone with Claude Code's built-in vision and PDF tools. AgentCM is an optional structured data layer that makes skills faster and more accurate by pre-indexing drawings and specs.

## Getting Help

- File issues at the [GitHub repository](https://github.com/dleerdefi/claude-code-construction/issues)
- Check `evals/` for test cases and expected outputs
- See [Running Evals](RUNNING_EVALS.md) to verify skills work on your documents
