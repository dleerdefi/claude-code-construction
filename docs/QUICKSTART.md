# Quickstart: Your First 5 Minutes

## What This Is

Construction skills for Claude Code that let you navigate drawings, extract schedules, parse specs, tabulate bids, and generate subcontracts — all from your terminal or IDE. See the [README](../README.md#skills) for the full list of skills.

**These skills work standalone** with any construction PDFs. They rasterize PDF pages with the plugin's own scripts and read the resulting images; they never read a PDF directly. No additional platform is required. AgentCM, a separate project-data tool, is optional; the skills work without it and use its pre-indexed data when it is present.

## Install

A person can follow these steps, or Claude Code can follow them for the person: for example from AgentCM's install guide, whose optional step links here. Claude: use plain words, one step at a time. Ask before installing anything, and install nothing these steps don't name. The steps are safe to repeat; the checks find what's already done.

You need Claude Code, Git, Python 3.10 or newer, and your project's documents (drawings, specs, bids and so on). An AgentCM install already has Claude Code and Git.

### Step 1: Check, changing nothing

1. **Git:** `git --version`. On Windows, Git for Windows also gives Claude Code the Bash tool that the skills' commands run in.
2. **Python 3.10 or newer:**
   - Windows: `py -3 --version`, or `python --version`. A `python` that opens the Microsoft Store doesn't count.
   - macOS and Linux: `python3 --version`. Apple's built-in `python3` is 3.9, which is too old.
3. **The plugin, if it's already installed:** `claude plugin list` shows `construction@construction-skills`.

Show the person what was found, say what you'll install, and ask once: "Shall I go ahead?"

### Step 2: Install what is missing

- **Windows:** Python with `winget install --id Python.Python.3.12 -e`; Git, if missing, with `winget install --id Git.Git -e`. An installer that asks for administrator rights: the person presses **Yes**.
- **macOS:** `brew install python@3.12 git`. Without Homebrew, the person installs it from https://brew.sh first, since it asks for their Mac password.
- **Debian and Ubuntu:** `sudo apt install python3 python3-venv git`. The person runs it in their own terminal, since it asks for their password.

A program installed just now isn't on Claude Code's PATH yet: reopen Claude Code in the same folder before Step 3.

### Step 3: Install the plugin

The person types these two lines in Claude Code:

```
/plugin marketplace add dleerdefi/claude-code-construction
/plugin install construction@construction-skills
```

Claude can run the same from a terminal instead:

```
claude plugin marketplace add dleerdefi/claude-code-construction
claude plugin install construction@construction-skills
```

Then run `/reload-plugins`, or reopen Claude Code.

This repository is its own marketplace. Updates arrive with each release; turn on auto-update under `/plugin` → Marketplaces.

Where it writes:
- the plugin itself, under `~/.claude/plugins/`;
- the first time a skill runs one of its scripts, a Python environment at `~/.construction-skills/venv` (this takes about a minute).

It writes nothing in a project folder until a skill runs there.

### Step 4: Check

1. `claude plugin list` shows `construction@construction-skills`, enabled. In Claude Code, typing `/construction:` lists the skills.
2. Open Claude Code in a project folder and run `/construction:project-setup`. With AgentCM, open the project folder AgentCM manages: the skill says it found AgentCM, with AgentCM's contract version.

[Validating your install](VALIDATING.md) has the full checks. To work on the skills themselves, or to use the newest unreleased ones, clone the repository instead ([Setup in the README](../README.md#setup), Option B).

## Try It: Index Your Project

Open Claude Code in a folder with construction documents and type:

```
/construction:project-setup
```

Claude will:
1. Scan the directory for all PDFs, drawings, specs, and project files
2. Classify each file by type (Drawing, Specification, RFI, Submittal, etc.)
3. Detect operational mode (AgentCM vs. Flat File) and establish context
4. Report a summary of what was found

## Try It: Extract a Schedule

If you have a drawing sheet with a door, finish, or equipment schedule:

```
/construction:schedule-extractor A-3.2
```

Claude will:
1. Open the PDF and locate the schedule table
2. Extract every row using pdfplumber (with vision fallback if table detection fails)
3. Save the data to an Excel (.xlsx) workbook
4. Report the extraction quality (row count, column count)

## Try It: Read a Drawing

Point Claude at any drawing sheet and ask about it — drawing reading is built into the core skills:

> "Read sheet A-1.1 and tell me what rooms are shown"

Claude will rasterize the sheet to a PNG and use vision to describe what's on it — room layouts, door tags, section cuts, detail callouts, and more.

## Try It: Split Your Specs

If you have a bound project manual (one large PDF with all spec sections):

```
/construction:spec-splitter
```

Claude will:
1. Parse the Table of Contents
2. Find section boundaries in the PDF
3. Split into individual PDFs in a `Specification Sections/` folder (inside your specs folder): `03 30 00 - CAST-IN-PLACE CONCRETE.pdf`, etc.
4. Create a spec index YAML
5. Extract each section's text to `.construction/skills/spec_text/`, with a quality rating per section

## Try It: Generate a Submittal Log

Run this on a project with specs. If spec text has not been extracted yet, the skill runs spec-splitter itself first.

```
/construction:submittal-log-generator
```

Claude will:
1. Read the extracted text of each spec section
2. Find submittal requirements in Part 1 (the SUBMITTALS articles, quality assurance, closeout and similar articles) and in Parts 2 and 3 where a product or execution article calls for one
3. Score each item's confidence and flag uncertain ones
4. Generate `Submittal_Log.xlsx` with three sheets: "Submittal Log", "Summary" and "Extraction QA"

## What Gets Created

Skills save deliverables in your project folder, where you can open them, and keep their working data in a hidden `.construction/skills/` folder:

```
your-project/
  drawings/                         # Your PDFs
    sheets/                         # Split sheet PDFs + sheet_index.yaml (sheet-splitter)
  specs/Specification Sections/     # Split spec PDFs + spec_index.yaml (spec-splitter; goes in your specs folder)
  Submittal_Log.xlsx                # Excel/Word deliverables (or in a matching folder, e.g. Submittals/)
  .construction/                    # Hidden on Mac/Linux; you don't need to open it
    skills/                         # Skills' working data: spec text, issue registry, progress
```

In projects that use AgentCM (marked by `.construction/project.yaml`), `.construction/` also holds AgentCM's project data, which skills read but never write; a skill's findings stay in `.construction/skills/` in every project.

## Running Evals

Want to verify the skills work? See [Running Evals](RUNNING_EVALS.md) for how to test against sample construction documents.

## Troubleshooting

See [Troubleshooting](TROUBLESHOOTING.md) for common issues and fixes.

For the full list of skills, see the [README skill table](../README.md#skills). Drawing reading and construction conventions live in the `construction-guide` skill, which Claude loads when you work with construction documents.
