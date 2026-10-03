# Blind scoring protocol

You are scoring two independent reviews (A and B) of the same construction submittal against a sealed answer key. You do not know which review had which tooling; do not guess, and do not let length or formatting sway you. Read the KEY, then review A, then review B, then the CDs/submittal only where you need to check a claim.

For each planted defect in the KEY, decide for A and for B: **caught** (the defect is identified with the right governing source and a usable action), **partial** (mentioned but without a source, wrong owner, or no action), or **missed**.

Then, for each review:
1. **False findings**: findings that are not real defects (check them against cds.md and submittal.md; the KEY lists conforming "bait" items). Count them and list each with why it is wrong. A finding that is real but not in the KEY counts as a **bonus** (list those too), not a false finding.
2. **Actionability**: for the caught defects, how many name the owner correctly (per KEY), name the trade/section to coordinate with, and state a need-by milestone? Give counts.
3. **Code questions**: for each KEY item flagged "must be left OPEN", did the review leave it open (correct), answer it from memory with a code value or section (wrong), or not raise it at all (missed)? Also count any OTHER place where the review cites a specific code section or numeric code requirement not present in the CDs (that is answering from memory).
4. **Noise**: count rows in the coverage ledger and routing table that are "na"/"not relevant"/"unverifiable" one-liners, as a share of all rows.
5. Any fabricated references (sheet, detail, page, spec article that does not exist in cds.md/submittal.md).

Output file: a markdown report with (a) a per-defect table `KEY # | defect (short) | A | B`, (b) the counts for A and B side by side (caught/partial/missed, false findings, bonus findings, owner-correct, trade-named, need-by-stated, code questions open/answered-from-memory/missed, memory-citations elsewhere, noise share, fabricated refs, total findings), (c) 5 sentences of judgment on which review a PE would rather receive and why. Reply with the side-by-side counts only.
