# Standard Operating Procedure: Claude Code Skills for Construction Management
**Role:** Claude Code operating as a Project Engineer  
**Source of Truth:** Construction Document Set (Plans, Specifications, Schedules, Submittals, RFIs)  
**Version:** 2.0 — Aligned with official Anthropic Agent Skills spec (agentskills.io) and Claude Code documentation

---

## Table of Contents
1. [Foundational Philosophy: The Project Engineer Mental Model](#1-foundational-philosophy-the-project-engineer-mental-model)
2. [The Construction Document Hierarchy](#2-the-construction-document-hierarchy)
3. [Engineering the `SKILL.md` Entry Point](#3-engineering-the-skillmd-entry-point)
4. [Tier 3 Resource Management: The Two-Layer Asset Model](#4-tier-3-resource-management-the-two-layer-asset-model)
5. [Core Skill Library: Standard CM Workflows](#5-core-skill-library-standard-cm-workflows)
6. [The Refactoring Lifecycle for CM Skills](#6-the-refactoring-lifecycle-for-cm-skills)
7. [Performance Validation via Construction-Specific Evals](#7-performance-validation-via-construction-specific-evals)
8. [Continuous Optimization and Agentic Orchestration](#8-continuous-optimization-and-agentic-orchestration)
9. [Architect's Final Checklist](#9-architects-final-checklist)

---

## 1. Foundational Philosophy: The Project Engineer Mental Model

### The Core Mandate

Claude Code, when operating in a construction management context, assumes the role of a **Project Engineer (PE)**. This is not a general-purpose assistant role. The PE role carries specific obligations:

- The **Construction Document Set** is the non-negotiable source of truth. No assumption overrides a drawing, specification, or addendum.
- **Conflicts between documents** must be surfaced, not silently resolved. When plan sheets contradict specifications, the agent flags the conflict and escalates — it does not choose.
- **Domain language is precise.** "Change Order," "RFI," "Submittal," "ASI," and "Bulletin" are not synonyms. Each triggers a specific workflow with its own document lineage.

### The Progressive Disclosure Model for Construction

Construction projects generate tens of thousands of documents across a multi-year lifecycle. Loading everything into context simultaneously would be the equivalent of handing a Project Engineer every project document on their first day and asking them to memorize it. Instead, skills must mirror how an experienced PE actually navigates a project: **query first, read only what is needed, act on the minimum viable document set.**

The Three Tiers of Information Loading for Construction Management:

| Tier | Components | Loading Trigger | Context Impact |
|---|---|---|---|
| **Tier 1: Discovery** | YAML Front Matter (`name` + `description`) | Always loaded when the skill exists in `.claude/skills/`. ~100 tokens per skill. | High (Constant). Consumes the system-wide Context Budget. Descriptions **truncated at 250 characters** in the listing. |
| **Tier 2: Execution** | `SKILL.md` Body (Workflow SOP, Routing Logic, Domain Knowledge) | Loaded only upon explicit skill activation | Moderate. Contains PE-level decision logic and document navigation patterns. Recommended ≤500 lines / ≤5,000 tokens. |
| **Tier 3: Deep Knowledge** | `/references`, `/scripts`, `/assets` and the **Global Project Document Store** | Just-in-Time (JIT) via explicit reference in Tier 2 | Low (Ephemeral). Navigated with minimum viable precision. Cleared after step completion. |

### The Context Budget and 250-Character Description Truncation

All skill descriptions within `.claude/skills/` share a cumulative budget of **1% of the context window (~8,000 characters fallback)**. This is configurable via `SLASH_COMMAND_TOOL_CHAR_BUDGET` but the default is tight. In a construction project with dozens of active skills (RFI, Submittal, Schedule, Punchlist, Closeout, etc.), budget overruns will degrade reasoning before a single document is parsed.

**Critical:** Each skill's `description` is **truncated at 250 characters** in the skill listing that Claude sees at startup. This means the first 250 characters of every description must contain the key use case and trigger keywords. Anything beyond 250 characters is only visible after the skill is activated.

**Rule:** Every character spent in a YAML description must earn its place. Front-load the primary trigger and purpose in the first 250 characters. If a concept requires more than two sentences to trigger correctly, it belongs in the `SKILL.md` body, not the description.

---

## 2. The Construction Document Hierarchy

Before engineering any skill, the architect must understand two foundational concepts: the **project initialization process** that establishes the document store for Claude Code, and the **two operational modes** that govern how skills navigate that store.

---

### 2.0 — Project Initialization: `/init` + `/project-setup`

Skills do not bootstrap themselves. Before any skill can navigate a project's documents, Claude Code must first understand the project's structure. This happens in two steps.

#### Step 1: `/init` (Built-In Command)

`/init` is a **protected built-in** Claude Code command. It cannot be overridden or customized by skills. When a user runs `/init`, Claude Code analyzes the codebase and generates a starter `CLAUDE.md` at the project root with build commands, project structure, and conventions it discovers.

For construction projects, `/init` will produce a generic `CLAUDE.md` that captures the folder structure but lacks construction-specific context (document classification, discipline conventions, register locations).

#### Step 2: `/project-setup` (Construction Skill — Planned)

After `/init` creates the base `CLAUDE.md`, a construction-specific `/project-setup` skill enriches it with domain context:

1. **Traverse the directory tree** — Walk the full folder structure and classify construction document types: drawing sets (by discipline prefix: A-, S-, M-, E-, P-, C-, L-), the specification book (Division folders or a single Project Manual PDF), schedule files, and active registers (RFI log, Submittal log, Change Order log).
2. **Detect operational mode** — Check for `.construction/` directory existence. If present, the project is AgentCM-backed. If absent, it operates in Flat File Mode.
3. **Amend `CLAUDE.md`** — Append construction-specific context to the existing `CLAUDE.md`:
   - Project name, number, GC, Owner, Architect (if discoverable)
   - The canonical path to each document category
   - The drawing discipline prefix conventions in use on this project
   - Any non-standard folder structures or naming conventions

> **Note:** `/project-setup` is a planned skill. Currently, each skill discovers document paths independently through directory search (look for `Specifications/`, `drawings/`, `plans/`, etc.). This works but creates redundant discovery across skills. `/project-setup` would centralize this into a one-time operation.

**The `CLAUDE.md` is the universal context anchor.** Every skill reads it at activation to know where documents live and which navigation strategy to use. Skills must never hardcode paths — they must always resolve paths through `CLAUDE.md`.

**Example `CLAUDE.md` skeleton (flat file mode):**
```markdown
# Project: Holabird Elementary School Renovation

## Project Info
- Project Number: 2024-0047
- GC: Barton Malow Company
- Owner: Baltimore City Public Schools
- Architect: Ziger/Snead Architects

## Document Store Paths
- Drawing set: ./drawings/ (disciplines: A, S, M, E, P, FP, C, L)
- Spec book: ./specifications/project_manual.pdf
- Schedule: ./schedule/master_schedule.xlsx
- RFI log: ./logs/rfi_log.xlsx
- Submittal log: ./logs/submittal_log.xlsx
```

**Example `CLAUDE.md` skeleton (AgentCM mode):**
```markdown
# Project: Holabird Elementary School Renovation

## AgentCM
The `.construction/` directory contains the project graph and extracted data.
- Graph: .construction/graph/navigation_graph.json
- Graph summary: .construction/graph/graph_summary.yaml
- Spec text: .construction/spec_text/
- Sheet index: .construction/index/sheet_index.yaml
- Spec index: .construction/index/spec_index.yaml
```

---

### 2.1 — Two Operational Modes

CM skills must be **mode-aware**. The document navigation strategy differs depending on whether AgentCM's data layer is present. The detection mechanism is simple: **check for the `.construction/` directory at the project root.** If it exists, the project is in AgentCM mode. If not, Flat File mode.

#### Mode A: Flat File Mode (Default)

The project folder is a standard directory of files. No pre-processed data layer exists. Claude Code navigates using directory search, YAML index files, and direct PDF/text reads.

**How skills navigate in Flat File Mode:**
- Use paths declared in `CLAUDE.md` (if populated by `/project-setup`) or discover paths via directory search
- Use YAML index files (`spec_index.yaml`, `sheet_index.yaml`) as pre-built indexes when available
- When an index is absent, use targeted file-name pattern matching — never open-ended directory scans
- Read only the specific file and, where possible, only the relevant page range or section

**Example — finding a concrete mix design in Flat File Mode:**
```
Step 1: Check if .construction/spec_text/03_30_00.txt exists (no — flat file mode)
Step 2: Look for split spec PDFs in Specification Sections/ folder
Step 3: If found, read "03 30 00 - CAST-IN-PLACE CONCRETE.pdf"
Step 4: If not split, search the bound project_manual.pdf for "SECTION 03 30 00"
Step 5: Return the relevant content — do not load the full spec book
```

#### Mode B: AgentCM Mode

The project has been processed through AgentCM. A `.construction/` directory exists at the project root containing structured data: a navigation graph (JSON), YAML indexes, extracted text files, and graph summaries.

**How skills navigate in AgentCM Mode:**
- Read `.construction/CLAUDE.md` for navigation context
- Read `.construction/graph/graph_summary.yaml` for quick project orientation
- Read specific JSON/YAML files from `.construction/` for structured lookups (spec text, sheet indexes, findings)
- The `.construction/` data layer is the index; the underlying PDFs remain the source of truth for content

**Example — finding a concrete mix design in AgentCM Mode:**
```
Step 1: Check .construction/ directory exists (yes — AgentCM mode)
Step 2: Read .construction/spec_text/03_30_00.txt (pre-extracted text)
Step 3: Return the relevant content from the .txt file
```

**The rule in both modes is identical:**
> Skills navigate to the minimum viable document fragment. They do not load categories of documents — they load specific files, sections, pages, or text extracts.

---

### 2.2 — Layer 1: The Global Project Document Store

This is the **universal source of truth** for the entire project. It is not owned by any single skill. Its structure is declared in `CLAUDE.md` and is the same in both operational modes — only the navigation mechanism differs.

**Contents include:**
- Drawing set: Architectural, Structural, MEP, Civil, Landscape PDFs
- Specification book: Project Manual covering CSI MasterFormat Divisions 00–49
- Active schedule: Master CPM schedule, three-week lookahead, milestone log
- Document registers: RFI log, Submittal log, Punchlist, Change Order log, ASI/Bulletin log
- *(AgentCM Mode only)* `.construction/` data layer: Navigation graph (JSON), extracted spec text, sheet/spec indexes, and graph summaries connecting spec sections, drawing sheets, and project entities

---

### 2.3 — Layer 2: Navigational References and Index Files

Reference files and index files do **not** hold plans, specs, or schedules. They hold **navigation logic, routing rules, and structured indexes** that tell the agent how to find what it needs within the Global Project Document Store.

Think of the Global Document Store as the library and reference/index files as the skill's private card catalog, tuned for its specific workflow.

Reference files can live in two places (both are valid per the official Agent Skills spec):
1. **Shared resources** at the skills root: `reference/` (PE domain knowledge), `scripts/` (Python tools shared across skills)
2. **Per-skill resources** inside each skill directory: `references/`, `scripts/`, `assets/` (output schemas, decision trees specific to one skill)

**Index and Reference Files Currently in Use:**

| File | Location | Purpose | Generated By |
|---|---|---|---|
| `sheet_index.yaml` | `sheets/` or `.construction/index/` | Drawing sheet numbers, titles, discipline prefixes, file paths | `/sheet-splitter` + `/sheet-index-builder` |
| `spec_index.yaml` | `Specification Sections/` | Spec section numbers, titles, page counts, file paths | `/spec-splitter` |
| `manifest.json` | `.construction/spec_text/` | Spec text extraction quality (GOOD/DEGRADED/POOR) per section | `/spec-splitter` |
| `submittal_log_schema.json` | `submittal-log-generator/references/` | JSON schema for submittal log output data contract | Manual |
| `pe-review/references/*.md` | `pe-review/` skill dir | PE behavioral rules, red flags, coordination matrix, scope gaps | Manual |
| `navigation_graph.json` | `.construction/graph/` | Project entity relationships (AgentCM only) | AgentCM |
| `graph_summary.yaml` | `.construction/graph/` | Quick orientation summary of graph contents (AgentCM only) | AgentCM |

**Planned reference files** (not yet implemented):
- `submittal_routing_rules.md` — Maps CSI divisions to responsible subcontractors
- `division_scope_matrix.md` — Maps CSI MasterFormat divisions to trade packages
- `conflict_escalation_protocol.md` — Decision tree: clarification vs. RFI vs. ASI

---

## 3. Engineering the `SKILL.md` Entry Point

### The Golden Rule

The `SKILL.md` file is a **high-efficiency Standard Operating Procedure**, not a data repository. It tells Claude Code *what to do* and *where to look* — it does not contain the plans, specs, or domain encyclopedias itself.

A construction PE does not walk onto a jobsite carrying every drawing in hand. They carry a plan of attack and know exactly which drawing to pull from the rack when needed.

### The 500-Line Soft Limit

Per Anthropic's official recommendation, `SKILL.md` should stay **under 500 lines (~5,000 tokens)**. Beyond this, split content into reference files that load JIT. This is a soft recommendation, not a hard enforcement.

For construction skills, keep the SOP workflow steps concise. Domain knowledge that the PE needs throughout the workflow (submittal type taxonomies, confidence scoring rules, boilerplate detection criteria) may extend the file beyond a minimal SOP — this is acceptable when the knowledge is actively used during processing, not pure reference material. Move lookup tables, CSI Division keyword lists, and other reference-only content to Tier 3 files.

### Mandatory YAML Front-Matter Framework

Every `SKILL.md` must begin with a structured YAML block. This is the **only** content loaded during Tier 1 Discovery (~100 tokens per skill).

#### Official Supported Fields

**Required fields (Agent Skills open standard — agentskills.io):**

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Max 64 chars. Lowercase letters, numbers, hyphens only. **Must match the parent directory name.** |
| `description` | Yes | Max 1,024 chars. Truncated to **250 chars** in the skill listing. Front-load triggers and purpose. |

**Optional fields (Claude Code extensions):**

| Field | Use Case for CM Skills |
|-------|------------------------|
| `argument-hint` | Autocomplete hint, e.g., `"<project_manual.pdf> [--output-dir <path>]"` |
| `disable-model-invocation` | Set `true` for skills with side effects (PDF splitting, file writing) to prevent auto-triggering |
| `paths` | Glob patterns to limit auto-activation, e.g., `"*.pdf"` |
| `context` | Set to `fork` for heavy processing skills that benefit from isolated subagent execution |
| `model` | Override model when skill is active (e.g., use Opus for complex analysis) |
| `effort` | Override effort level: `low`, `medium`, `high`, `max` |

**Fields that do NOT exist and must not be used:** `triggers`, `negative_constraints`, `outcome`, `document_authority`, `reads_from`, `writes_to`, `tags`, `category`, `priority`. Claude Code does not parse these — they would be silently ignored.

#### How the `description` Field Does the Work

Since Claude matches skills to user intent based solely on `name` + `description`, the description must encode what other systems might split across triggers, constraints, and outcome fields. Write it in third person, front-load the primary use case, and include specific trigger keywords.

---

## 4. Tier 3 Resource Management: The Two-Layer Asset Model

### When to Navigate vs. When to Load Wholesale

This is the most critical architectural decision in CM skill design. The wrong choice collapses the context window. The correct action varies by operational mode but the principle is identical in both: **load the minimum viable document fragment.**

| Situation | Flat File Mode — Correct Action | AgentCM Mode — Correct Action | Never Do This |
|---|---|---|---|
| Need the concrete mix design from Section 03 30 00 | Search for split spec PDF or bound `project_manual.pdf` for "03 30 00", extract matching pages only | Read `.construction/spec_text/03_30_00.txt` directly | Load all of Division 03 |
| Need structural sheets intersecting grid line G | Filter `sheet_index.yaml` for S-series entries | Read `.construction/index/sheet_index.yaml` for S-series entries | Scan all structural PDFs sequentially |
| Need the subcontractor responsible for fire suppression submittals | Lookup Division 21 in scope matrix reference file | Read graph summary for Division 21 relationships | Read the entire submittal log |
| Need the current RFI count and latest open item | Read header rows of `rfi_log.xlsx` declared in `CLAUDE.md` | Read RFI findings from `.construction/graph/` | Load the entire project document store |

### JIT Loading Protocol

Tier 2 (`SKILL.md`) must explicitly command the loading of Tier 3 references at the step where they are needed — not at skill initialization.

**Correct pattern:**
```
Step 3: Identify affected specification sections.
  → Check for .construction/ directory to determine mode
  → [Flat File] Search spec_index.yaml or bound spec PDF for the matching division
  → [AgentCM]  Read .construction/spec_text/{section_number}.txt
  → Proceed to Step 4 with only the relevant section content in context.
```

**Anti-pattern:**
```
Step 1: Load all references.
  → Load every spec text file
  → Load the full sheet index
  → Load all graph summaries
  [all remain in context for the entire workflow]
```

### Pathing Standard

**Use `${CLAUDE_SKILL_DIR}` for skill-relative paths.** This variable resolves to the skill's directory and ensures portability. For scripts shared across skills:

```
${CLAUDE_SKILL_DIR}/scripts/bid_comparison_to_xlsx.py          ✓  (per-skill script)
${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py        ✓  (shared script via relative path)
${CLAUDE_SKILL_DIR}/references/output_schema.json              ✓  (skill-local reference)
/absolute/path/to/anything                                      ✗  (never hardcode absolute paths)
```

> **Always resolve project document paths through `CLAUDE.md` or directory discovery, never hardcode them.** A skill that hardcodes `./drawings/` will break on any project where the drawing folder has a different name.

---

## 5. Skill Requirements, Composition, and Relationship to the Document Codebase

In a software project, Claude Code treats the codebase as its working environment — reading files, understanding structure, and making targeted edits. In a construction management deployment, **the Construction Document Set is the codebase.** Plans, specifications, schedules, and registers are not reference material to consult occasionally — they are the live, authoritative data layer that every skill reads, navigates, and writes back to.

This section defines what a valid CM skill looks like, how its files are composed, and how it relates to that document codebase.

---

### 5.1 — What Qualifies as a CM Skill

A skill is warranted when a construction workflow meets **all three of the following criteria:**

1. **It is document-driven.** The task requires reading from or writing to the Construction Document Set — a plan sheet, specification section, schedule, register, or contract document. A task that requires only Claude's general knowledge (explaining what a submittal is, drafting a generic email) does not need a skill.

2. **It is repeatable across projects.** The workflow structure is consistent regardless of project-specific content. The inputs change (different spec sections, different sheet numbers, different sub names) but the logic does not.

3. **It produces a named, structured artifact.** The output is a specific deliverable: a populated log entry, a formatted document draft, a structured data file, a flagged conflict report. Open-ended "help me think about this" workflows are not skills.

If a workflow fails any of these criteria, it belongs in a prompt or a `CLAUDE.md` project instruction — not a skill.

---

### 5.2 — Skill File Composition

Every skill is a directory, not a single file. The directory name **must match** the `name` field in YAML front matter (this is a hard requirement of the Agent Skills spec).

**Our construction skills directory structure:**

```
~/.claude/skills/construction/          # Plugin root
├── .claude/skills/                     # All skill directories live here
│   ├── spec-splitter/
│   │   └── SKILL.md                   # Required. Uppercase. The SOP entry point.
│   ├── sheet-splitter/
│   │   └── SKILL.md
│   ├── submittal-log-generator/
│   │   └── SKILL.md
│   ├── bid-tabulator/
│   │   └── SKILL.md
│   └── ...
├── reference/                          # Shared domain knowledge (CSI, conventions, codes)
│   ├── csi_masterformat.yaml
│   ├── drawing_conventions.md
│   ├── common_abbreviations.yaml
│   ├── scale_factors.yaml
│   ├── ada_requirements.yaml
│   └── ibc_egress_tables.yaml
├── scripts/                            # Shared Python tools
│   ├── pdf/                            # PDF rasterize, crop, annotate, extract
│   └── graph/                          # Graph write utilities (AgentCM)
├── bin/                                # Python venv wrapper
│   └── construction-python
└── CLAUDE.md                           # Dev/contributor guide for the skills themselves
```

Per-skill `references/`, `scripts/`, and `assets/` subdirectories are also valid per the official spec and appropriate for skill-specific resources (output schemas, decision trees). Currently our skills use the shared resources at the plugin root.

---

#### The `SKILL.md` File

This is the only file Claude Code reads at skill activation. It must do three things and nothing else:

**1. Declare itself via YAML front matter (Tier 1):**

```yaml
---
name: spec-splitter
description: "Split a bound project manual PDF into individual specification section PDFs and extract searchable text from each section. Two functions: (1) split combined PDF into per-section PDFs, (2) extract per-section text to .txt files. Use when specs are in a single bound PDF, when text extraction is needed, or as a prerequisite for submittal-log-generator. Triggers on 'split specs', 'break up the project manual', 'separate spec sections', 'extract spec text'."
argument-hint: "<project_manual.pdf> [--output-dir <path>]"
---
```

Only `name` and `description` are required. See Section 3 for the full list of supported optional fields (`argument-hint`, `disable-model-invocation`, `paths`, `context`, `model`, `effort`).

**2. Check operational mode (Tier 2):**

The first executable step of every skill should determine the operational mode:

```
Step 1: Check for .construction/ directory.
  → If present: AgentCM mode. Read .construction/CLAUDE.md for navigation context.
  → If absent: Flat File mode. Discover paths via directory search or CLAUDE.md.
```

**3. Route to references JIT (Tier 2 → Tier 3):**

Steps load exactly one reference at a time, use it, and release it before the next step. The skill body never holds more than one reference in active context simultaneously unless the step explicitly requires cross-referencing two documents.

---

#### Shared vs. Per-Skill Resources

| Resource Type | Location | Example |
|---|---|---|
| **Shared scripts** | `scripts/pdf/`, `scripts/graph/` | `rasterize_page.py`, `crop_region.py`, `write_finding.py` |
| **Shared domain knowledge** | `reference/` | `csi_masterformat.yaml`, `drawing_conventions.md`, `common_abbreviations.yaml` |
| **Per-skill scripts** | `{skill-name}/scripts/` | Canonical executable scripts for each skill |
| **Per-skill references** | `{skill-name}/references/` | Data contracts, schemas, or domain knowledge specific to one skill |

Scripts are referenced via `${CLAUDE_SKILL_DIR}` for portability:
```bash
${CLAUDE_SKILL_DIR}/scripts/bid_comparison_to_xlsx.py          # per-skill script
${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py        # shared script
```

---

#### The `learnings.md` File (Aspirational)

> **Status: Not yet implemented.** The concept of a per-skill self-improvement file is valuable but is not currently part of the shipped skill architecture. This section describes the planned design for future implementation.

When implemented, `learnings.md` would start empty and be populated by a session wrap-up process. It would contain only validated observations: patterns that measurably improved output, edge cases discovered in real project data, and superseded instructions that should be pruned. Every entry must state: what was observed, in which scenario, and what rule change it implies.

---

### 5.3 — The Construction Document Set as Codebase

The analogy to software development is precise and should be kept in mind when designing any skill:

| Software Project | Construction CM Project |
|---|---|
| Source files (`.py`, `.ts`, `.go`) | Drawing PDFs, specification sections, schedule files |
| `package.json` / dependency manifest | `CLAUDE.md` — declares what exists and where |
| Database / data store | Document registers (RFI log, Submittal log, CO log) |
| API schema | CSI MasterFormat division structure |
| Version control history | Revision blocks, ASIs, Bulletins, addenda |
| Test suite | Evals assertions (see Section 7) |
| `README.md` | Division 01 — General Requirements |

Just as Claude Code does not read every source file before answering a code question, a CM skill does not read every drawing before answering a document question. It reads `CLAUDE.md`, identifies the relevant file and location, and reads only that.

**The discipline of minimum viable document access is the primary performance lever for CM skills.** A skill that consistently over-reads the document set will degrade across long sessions as context fills. A skill that navigates precisely will remain sharp through complex, multi-step workflows.

---

### 5.4 — Skill Categories in a CM Deployment

While this SOP does not prescribe a fixed skill catalog (each project team will develop skills suited to their specific workflows and document conventions), CM skills tend to fall into four functional categories. Understanding these categories helps in scoping new skills correctly and avoiding overlap.

**Builder Skills** — Process raw project documents into structured navigational assets. They run once (or on each document update) and produce outputs consumed by other skills. They write to the project document store rather than reading from registers.
> *Examples from the current skill library: `spec-splitter`, `sheet-splitter`*

**Extraction Skills** — Read from specific document types and produce structured data outputs. They are document-type specialists: they know the schema of a particular construction document and can reliably pull structured information from it.
> *Examples: `schedule-extractor`, `bid-tabulator`*

**Generation Skills** — Take structured inputs (from registers, user prompts, or extraction skill outputs) and produce formatted construction documents conforming to project or industry conventions.
> *Examples: `subcontract-writer`, `submittal-log-generator`*

**Research Skills** — Navigate external sources (building codes, standards, product data) and return findings in a form that can be directly applied to the project's open questions.
> *Examples: `code-researcher`*

When scoping a new skill, identify its category first. Builder skills must be run before Extraction or Generation skills that depend on their outputs. This dependency order should be declared in `CLAUDE.md` and respected by the Wrap-Up orchestration layer.

---

## 6. The Refactoring Lifecycle for CM Skills

Legacy or over-built skills degrade reasoning performance. The following 4-step lifecycle governs all CM skill refactoring.

### Step 1 — Analyze

Identify the ratio of **workflow logic** (what the PE does) versus **embedded knowledge** (what belongs in the document store or references). A skill with more than 30% of its line count dedicated to CSI division definitions, spec section summaries, or drawing legends is over-built.

**Red flags in CM skills:**
- Spec section content copied inline into `SKILL.md`
- Drawing sheet lists hardcoded into the skill body instead of read from `sheet_index.yaml`
- Trade scope definitions written as prose in the skill body (move to `reference/` files)
- Project document paths hardcoded in the skill (must always be resolved through `CLAUDE.md` or directory discovery)
- AgentCM-specific logic without checking for `.construction/` directory existence first
- A skill that doesn't check operational mode at all — it should branch based on `.construction/` directory presence

### Step 2 — Abstract

Migrate all embedded knowledge to the appropriate layer:

| Content Type | Destination |
|---|---|
| CSI spec section text | Read from `.construction/spec_text/` (AgentCM) or split PDFs (flat file) — never inline |
| Drawing sheet indices | `sheet_index.yaml` — generated by `/sheet-splitter` + `/sheet-index-builder` |
| Trade scope descriptions | `reference/` files at the skills root |
| Output templates (RFI form, CO form) | Per-skill `references/` as a named template file |
| Decision trees (conflict classification) | Per-skill `references/` or shared `reference/` directory |
| Project document paths | `CLAUDE.md` at project root or directory discovery — never hardcoded |

### Step 3 — Optimize

Rewrite `SKILL.md` to be a clean SOP that **routes to** these resources rather than **containing** them. Validate the 500-line soft limit before marking complete.

### Step 4 — Validate

Run the skill against a representative set of real project scenarios (see Section 7). Confirm that no workflow logic was lost in the abstraction — only static knowledge was offloaded.

---

## 7. Performance Validation via Construction-Specific Evals

No skill ships to a production project without passing an Evals Framework. CM projects carry contractual and financial consequences for errors. An 80% pass rate is the minimum threshold.

### Assertion-Based Testing

Each skill must be tested against **3–5 specific, verifiable assertions**. These assertions must mirror real PE quality control checkpoints.

### A/B Testing Reference Files

Test each `/references` file for measurable value:

- Run the skill **with** a specific reference file loaded → measure assertion pass rate
- Run the skill **without** that reference file → measure assertion pass rate
- If the delta is less than 10%, the reference file is a token cost without benefit — remove or consolidate

### Structured Eval Report

Every evaluation run produces a report with:

| Metric | Threshold |
|---|---|
| Assertion Pass Rate | ≥80% required; <80% returns to Optimize phase |
| Conflicting Document Flags | 100% of seeded conflicts must be surfaced — no silent resolution |
| Hallucinated Sheet/Section References | Must be 0% — any fabricated drawing or spec reference is a critical failure |
| Token Usage per Run | Benchmark for cost-efficiency; flag if >2× baseline |
| Time to Completion | Establish per-skill baseline; flag regressions |

> **Critical Failure Condition:** Any skill that produces a fabricated drawing sheet number, specification section, or subcontractor reference — without querying the actual document store — must be quarantined and refactored before any further use on a live project.

---

## 8. Continuous Optimization and Agentic Orchestration

### Self-Improving Skills (Aspirational)

> **Status: Not yet implemented.** The following describes a planned architecture for future development. Current skills do not include `learnings.md` files or automated wrap-up processes.

The vision: each skill directory would contain a `learnings.md` file populated by a session wrap-up process that captures validated observations — patterns that improved output, edge cases from real project data, and instructions that should be updated.

### Skill Orchestration Patterns

Construction management workflows rarely exist in isolation. Skills should be designed to **invoke one another** across a document lifecycle. For example:
- `submittal-log-generator` invokes `/spec-splitter` if spec text hasn't been extracted yet
- `sheet-index-builder` depends on `/sheet-splitter` having already split the drawing set
- Future skills may chain: `/project-setup` → `/spec-splitter` → `/submittal-log-generator`

Skills invoke other skills using the `/skill-name` syntax — they do NOT call shared scripts directly when a skill exists for that function.

### The Non-Destructive Merge Principle

When skills update the Global Project Document Store (adding an RFI, logging a submittal, updating an index), they must **append and merge** — never overwrite. Every write operation must:
- Use additive merge logic for index files (e.g., `spec_index.yaml`, `sheet_index.yaml` merge by key)
- Use `safe_output_path()` or equivalent versioning for output files (auto-version `_v2`, `_v3`)
- Include timestamps in graph entries (AgentCM mode)
- In AgentCM mode: write findings as append-only timestamped entries via `write_finding.py`
- In Flat File mode: version output files and merge index YAMLs additively

---

## 9. Architect's Final Checklist

Before any CM skill is deployed on a live project, verify every item:

**YAML Front Matter (Tier 1)**
- [ ] **`name` matches directory:** The `name` field exactly matches the skill's parent directory name (hard requirement)
- [ ] **Description front-loaded:** The first 250 characters of `description` contain the primary use case and trigger keywords (descriptions are truncated at 250 chars in the listing)
- [ ] **Description within budget:** All skill descriptions collectively fit within the ~8,000-character system budget
- [ ] **No fabricated fields:** Only officially supported YAML fields are used (`name`, `description`, `argument-hint`, `disable-model-invocation`, `paths`, `context`, `model`, `effort`, etc.)
- [ ] **Side effects flagged:** Skills that write files or modify project data use `disable-model-invocation: true` to prevent auto-triggering

**Architecture (Tier 2)**
- [ ] **500-Line soft limit:** Is `SKILL.md` under 500 lines? If over, is all content actively used during processing (not pure reference)?
- [ ] **Three-Tier Disclosure:** Is all deep knowledge abstracted to `/references`, shared `reference/` files, or routed to the Global Document Store?
- [ ] **Portable pathing:** Are skill-relative paths using `${CLAUDE_SKILL_DIR}`? Are project paths resolved through `CLAUDE.md` or directory discovery?
- [ ] **JIT Loading:** Are reference files loaded only at the step that requires them?

**Construction Document Integrity**
- [ ] **Mode-Aware Navigation:** Does the skill check for `.construction/` directory to determine mode — using file search in Flat File and `.construction/` data layer in AgentCM?
- [ ] **No Inline Spec Content:** Are specification section texts read from split PDFs or `.construction/spec_text/` — never copied into `SKILL.md`?
- [ ] **No Hardcoded Sheet Lists:** Are drawing indices in `sheet_index.yaml`, not embedded in skill logic?
- [ ] **Conflict Surfacing:** Does the skill explicitly flag document conflicts rather than silently resolving them?
- [ ] **No Hallucination Pathways:** Does every sheet number and spec section reference trace back to a query against the actual document store?

**Validation**
- [ ] **Eval-Ready:** Has the skill achieved ≥80% assertion pass rate across 3–5 CM-specific assertions?
- [ ] **Zero Fabricated References:** Has the skill passed a hallucination test with 0% fabricated drawing or spec references?
- [ ] **A/B Tested References:** Has each reference file been validated as contributing measurable assertion improvement?

**Lifecycle**
- [ ] **Orchestration Mapped:** Is this skill's position in the project workflow chain documented (e.g., spec-splitter must run before submittal-log-generator)?
- [ ] **Non-Destructive Writes:** Do all index updates use additive merge logic? Do output files use versioning (`safe_output_path()`)?
- [ ] **Graph Entries:** Does the skill write findings to `.construction/graph/` when in AgentCM mode?

---

*This SOP governs all Claude Code skill development for construction management deployments. It aligns with the official Agent Skills specification (agentskills.io) and Anthropic's Claude Code skill best practices (platform.claude.com). The construction document set is sovereign — when in doubt, query it.*
