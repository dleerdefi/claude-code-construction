# Quality Checks — RFI Draft Validation

## Pre-Presentation Gates

Before presenting any RFI draft to the user, verify every item.
If any gate fails, fix before presenting — do not present a draft
with known deficiencies.

### Reference Specificity
- [ ] Every drawing reference includes sheet number AND grid location
      or room number (never "the floor plan" or "the detail")
- [ ] Detail references use full format: "Detail 3/A-7.02"
- [ ] Spec references include section AND paragraph: "08 71 00, 2.01.A"
- [ ] Room references include number AND name: "Room 203 (Classroom)"

### Description Clarity
- [ ] A person unfamiliar with the project could understand the issue
      from the description alone
- [ ] The description states what the documents show (facts), not
      what the PE thinks is wrong (opinion)
- [ ] The conflict/ambiguity is explicitly identified — not implied
- [ ] No jargon without explanation (avoid abbreviations the A/E
      might not use)

### Suggested Resolution
- [ ] A resolution is provided (never submit without one)
- [ ] Resolution is framed as suggestion, not directive
- [ ] Resolution includes reasoning (why this solution makes sense)
- [ ] Resolution is technically feasible (not just "fix it")

### Schedule Impact
- [ ] Specific construction activity affected is named
- [ ] Date of that activity is stated (or "TBD — verify with PM")
- [ ] Response-needed-by date is stated
- [ ] Impact is proportional (don't overstate for minor issues)

### Routing
- [ ] Addressee is the correct design professional for the scope
- [ ] If cross-discipline: addressed to Architect (prime), with
      the relevant engineer CC'd
- [ ] From line matches the GC's project team

### Duplication
- [ ] No existing RFI addresses the same condition (checked log)
- [ ] If related RFI exists, it's referenced in the new draft
- [ ] Issue is not resolved by addenda, ASI, or general notes

### Document Precedence
- [ ] If the issue involves conflicting documents, the precedence
      hierarchy is correctly applied and cited
- [ ] Large-scale vs small-scale drawing precedence noted if relevant
- [ ] Figured dimension vs scaled dimension precedence noted if
      relevant

## Common Failure Patterns

These patterns indicate an RFI that will be returned or ignored:

**"Please clarify."** — Without stating what specifically needs
clarification. The A/E won't know what you're asking.

**"Per our discussion..."** — Verbal agreements must be formalized,
but the RFI must still state the technical issue independently.

**"The drawings are wrong."** — Presumptive. State what the drawings
show and why it creates a problem. Let the A/E determine if it's
an error.

**Missing drawing references.** — The A/E will need to look up the
exact location. Make their job easy — give them every reference.

**Scope creep.** — One issue per RFI. If you found three problems
in the same area, write three RFIs. Combined RFIs get partial
responses and create tracking nightmares.

## Post-Draft User Options

After presenting the quality-checked draft, offer:
1. **Export as .docx** — Produces a formatted Word document
2. **Refine** — User provides edits, Claude iterates
3. **Reject** — Issue isn't actually an issue; discard
4. **Defer** — Log back to issue registry for later action
5. **Batch** — User wants to draft multiple RFIs from the queue
