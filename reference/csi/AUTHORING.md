# Authoring a Division

How to add or extend knowledge in this layer. `SCHEMA.md` defines the format; this file is the process and the conventions. The Division 07 files (`profiles/07/`, `interfaces/div-07.yaml`) are the worked example: read them before writing anything.

## 1. The value test

Every line must pass: **would an expert PE do this, and would a capable model not do it reliably unprompted?** Claude already knows MasterFormat, what each trade does, and what a shop drawing is. What it lacks is:
- how a scope actually goes wrong in the field (failure modes)
- which documents must agree and on which fields (reconciliations)
- which trade owes which information to whom, and by when (interfaces with gates)
- which compliance questions a drawing will never mention (regulatory hooks)
- what a complete submittal for this scope shows (submittals `must_show`)
- the checks that catch all of the above, pointed at where the answer lives (`trace_to`)

Generic statements ("verify compliance with the specifications", "coordinate with other trades") fail the test. Cut them.

## 2. Raw material (mined, never trusted)

- `reference/pe_expertise/scope-NN-*.md` and `pe_behavior.md` (the archived A/B baseline; read-only)
- `skills/pe-review/references/` (`red-flags.md`, `absence-checklists.md`, `scope-gaps.md`, `coordination-matrix.md`)
- `docs/PE_EXPERTISE_REVIEW.md` §3 F4: archive claims that were wrong or overstated. Do not carry them over.

Spec-number listings, drawing-type lists, "check the register" and lead times are dropped (review §4).

## 3. What to write for a division

| File | Content |
|---|---|
| `profiles/NN/_division.yaml` | What is true of every section in the division: a short `scope_summary`, a handful of checks and failure modes, hooks that apply division-wide |
| `profiles/NN/NN-XX-00.yaml` | One profile per scope that is commonly submitted and carries distinct knowledge. Prefer level-2 (`08 71 00`) so specific sections inherit (`08 71 13`). Add level-3 only when the subtype differs materially. Typically 4–10 profiles per division |
| `interfaces/div-NN.yaml` | Edges this division owns (§5) |

For each section profile:
- `scope_summary`: what a PE watches in this scope, in three to five sentences. Not a definition.
- `review_mode` and `element_types`: `per_element` when submittals are organized by tagged elements the drawings also tag (doors by mark, equipment by item number, fixtures and light fixtures by type tag, casework by elevation, windows by type). `package` when it is one system's product data. `submittal-review` fans out per element and expects one answer per element × element-scope check.
- `contractor_designed`: `typical` for performance-specified systems the contractor designs or selects (sprinklers, fire alarm, cold-formed framing, PEMB, precast, curtain wall, stairs and railings, shoring, joists, trusses); `sometimes`; or `never`.
- `submittals`: per submittal type, what a complete submittal must show. This is expert content: what the spec boilerplate forgets.
- `review_checks`: 5–12 per section. Set `scope` only when the default is wrong (SCHEMA §4.1). Set `gate` on anything time-critical. Mark `reflex: true` only for the red flags a PE notices anywhere: at most two or three per division.
- `reconciliations`: the document pairs that must agree, with the key and fields. These are what make MEP review real.
- `failure_modes`: real field patterns, each linked by `caught_by` to a check, reconciliation or interface edge id.
- `standards`: designation, title, what to verify. Verified (§7).
- `regulatory_hooks`: compliance questions (§6).
- `extract_fields`: the values a reviewer reads from the submittal to reconcile.

## 4. Ids

Ids are global across the layer; `validate` rejects a repeat.

| Item | Convention | Example |
|---|---|---|
| Division baseline items | `dNN.` | `d08.frame-anchors` |
| Section items | two-digit division + mnemonic, then list | `08hw.electrified-power`, `08hw.fm.no-power-transfer`, `08hw.rh.egress-hardware`, `08hw.std.bhma-a156-13`, `08hw.xf.hardware-set`, `08hw.rc.sets-vs-schedule` |
| Interface edges | `if.NN-` + slug, NN = owning division | `if.08-electrified-hardware` |
| Overlay items | facility mnemonic | `food.`, `lab.`, `edu.`, `mf.` |

Division 07 and 12 use older short prefixes (`rf.`, `cw.`); leave them.

## 5. Interface ownership

An edge between two divisions lives in the **lower-numbered** division's file (`div-03.yaml` holds 03↔22). Exceptions: the edges already in `div-07.yaml` and `div-12.yaml` stay where they are. Never duplicate an existing edge: list all edges first (`grep -h "  - id: if." reference/csi/interfaces/*.yaml`). If your division needs an edge with a lower division that doesn't exist, request it in your report rather than writing it in another division's file.

Edge rules: `a` is your side. `responsibility.typical` is a prompt to confirm, never an answer. Leave `failure` off when a failure mode names the edge in `caught_by`.

## 6. Regulatory hooks and numbers

- **No bare numbers** in authored text: no dimensions, ratings, durations, percentages, ratios, R-values or lead times. `validate` lints them. A threshold becomes a hook question; a project value comes from the project documents.
- **Reuse topics.** Run `csi_knowledge.py topics` first. If the same code research answers your question, reuse the slug. New slugs are lowercase-hyphenated and name the question (`fire-damper-access-requirements`), not a code section.
- Hooks are questions about the adopted code and jurisdiction, phrased so `code-researcher` can answer them, with `source_families` that seed its search. Never state a code section number as a fact in a check.
- No single-jurisdiction rules. If a requirement exists only in some states, the hook asks whether it applies here.
- No brand names, except standards bodies and listing agencies.

## 7. Verification

- Every MasterFormat number and title you use (profile ids, `equivalents`, interface endpoints) is verified against a current listing, for example `https://www.designguide.com/csi-masterformat-index/NN-00-00`. Current MasterFormat, not 1995 or 2004.
- Every standard designation and title is verified against the publisher (ASTM, UL, NFPA, ANSI, BHMA, SEFA, AWI, TCNA, SMACNA, ASHRAE...).
- If you cannot verify a number, leave it out.

## 8. Shared files

Do not edit `SCHEMA.md`, `milestones.yaml`, `profiles/_global.yaml`, the resolver, or another division's files. Need a milestone, a `trace_to` term, or a source family that doesn't exist? Request it in your report.

## 9. Validate

```bash
"bin/construction-python" scripts/csi/csi_knowledge.py validate --strict --focus "profiles/NN/" --focus "div-NN" --focus "resolve NN "
"bin/construction-python" scripts/csi/csi_knowledge.py resolve --section "NN XX 00" --format md
```

Fix every error, warning and lint line in your files. Read the compiled output of at least two sections as a reviewer would: if a line would not change a review, cut it.

## 10. Status

Everything you write is `status: draft`, `reviewed_by: []`. It moves to `pe_reviewed` only when a named PE has reviewed the file.
