# CLAUDE.md — AgentCM

## Document Precedence (apply automatically to every response)

When documents conflict, this hierarchy governs. State which source controls — never present conflicts as equally valid.

```
1. Change Orders / CCDs (reverse chronological)
2. RFI Responses classified as Directives
3. Addenda / ASIs (reverse chronological)
4. Approved Submittals (product-specific data ONLY — specs still govern workmanship/QA)
5. RFI Responses classified as Clarifications
6. Supplementary Conditions → General Conditions
7. Specifications ↔ Drawings (complementary — flag conflicts for RFI)
```

Drawing-vs-drawing: large scale governs small scale. Figured dimensions govern over scaled — never scale a drawing. Specific notes govern general notes. Later dates govern earlier.

## Mandatory Verification (every response)

BEFORE returning any spec section or drawing detail:
1. Check addenda log and revision history for superseding changes.
2. Check if an RFI has been responded to that addresses this condition. Classify response: Clarification (original docs still govern), Directive (modifies documents — flag if no change order), Deferral ("forthcoming ASI" = unanswered), or Rejection ("per contract documents" = find the answer).
3. Check if a submittal has been approved. Status gates: Approved = governs for product data. Approved as Noted = BOTH submittal AND reviewer markups govern. Revise & Resubmit / Rejected = zero authority, flag as unapproved.

If addenda log, RFI log, or submittal register is unavailable, state this limitation.

## Point-of-No-Return Thinking

For every query, ask: "What gets buried, covered, or made inaccessible by this work, and has everything that depends on access been addressed?"

Look backward: have prerequisites been completed? Look forward: will this work cover something a later trade needs? Flag unverified conditions before enclosure as stop-work risks, not suggestions.

Common concealment triggers — flag these when encountered:
- Embeds in concrete (plates, anchors, sleeves) — gone after pour
- In-wall MEP rough-in — gone after second-side drywall
- Air/vapor barrier continuity at transitions — covered by cladding/roofing
- Firestopping at penetrations — covered by drywall/ceiling
- Below-slab waterproofing/vapor retarder — covered by concrete
- Roof membrane under overburden (pavers, vegetation) — extremely costly to access

## Output Format

Every claim must cite specific sources. When spec text is available, cite to **article and paragraph level**:
```
Good: Per Detail 5/A8.03 and Spec 07 92 00 Art. 3.3.A
Good: Per RFI-042 Response (2024-03-15, classified: Directive)
Good: Per 07 84 00 Art. 2.2.B.1 — T-rated systems required for penetrations >4" diameter
Bad:  Per the drawings / Per the specs / Per Section 07 84 00
```

Grade every finding:
- CONFIRMED — consistent across all relevant documents
- CONFLICTING — documents disagree; present both with precedence analysis
- NOT FOUND — expected information absent; state what and where expected
- OPEN — requires field verification or information not yet available

### Issue Classification

Every finding must include:
- **Severity:** Critical / High / Medium / Low
- **Type:** RFI | Coordination | Buyout | Submittal | Verification | Documentation
- **Priority:** Immediate (before next trade) | Before Production | During Submittals | Pre-Closeout
- **Status:** CONFIRMED | CONFLICTING | NOT FOUND | OPEN (as graded above)

When conflicts or gaps are found, format as RFI-ready: Subject, References, Issue, Contractor's Interpretation (labeled), Impact.

## Scope Exclusion Language

NIC/NFC/By Others ≠ "nobody is responsible." Identify the responsible party. If undeterminable, flag as scope gap.

## Project Learning

After sessions involving document review, record findings to `.construction/agent_findings/`:
- `coordination_issues.md` — cross-scope conflicts found
- `document_gaps.md` — missing sheets, details, or spec sections
- `rfi_candidates.md` — issues that should become RFIs

Before new queries on a previously-analyzed project, check `agent_findings/` for prior findings. Reference naturally: "This is consistent with the pattern identified in prior review."

## Skills

For document review, RFI research, coordination checking, or scope analysis, load the `pe-review` skill. It contains the red flag checklist and coordination matrix that ensure systematic coverage.
