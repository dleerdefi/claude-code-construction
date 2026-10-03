# Classification protocol (marginal value of the knowledge layer)

You are a skeptical auditor. You have two files for one CSI section:
- BASELINE: what an expert-PE persona listed closed-book, with no access to the knowledge layer.
- COMPILED: the knowledge layer's compiled context for the same section (resolver output).

Classify EVERY item in COMPILED under these headings: review checks, reconciliations, regulatory hooks, coordination routing (interfaces), failure modes, expected submittal contents (each must_show bullet), standards. (Skip "Extract for reconciliation" and "Suppressed"; count them but do not classify.)

Classes:
- (a) baseline already produced it: the baseline has an item that would lead a reviewer to the same check, pairing, question, trade routing, failure mode or standard. More specific wording of a baseline idea is still (a).
- (b) baseline missed it, AND it is correct, AND it would change a review: a reviewer following only the baseline would plausibly miss a real defect, a required coordination, an unasked compliance question, or would wrongly answer from memory. Be strict: it has to be something an expert would actually do and a capable model would not do unprompted.
- (c) wrong or misleading: factually wrong, wrong trade, wrong document, misleading routing, retired MasterFormat number, mis-titled standard, states a code value, or would send the reviewer down a wrong path.
- (d) noise: true but would not change a review: generic ("coordinate with other trades"), restates procedure or Division 01 boilerplate, duplicates another compiled item, or is so obvious any PE/model does it unprompted.

Judge (b) against the full BASELINE across all its headings, not only the matching heading. If you are torn between (a) and (b), choose (a). If torn between (b) and (d), choose (d).

Output file format (markdown):
1. A table: `item id | heading | class | one-line reason` — one row per compiled item.
2. Counts per heading and overall: a / b / c / d and ratio b/(a+b+c+d).
3. "Best (b) items": quote up to 8 verbatim with why they would change a review.
4. "Every (c) item": quote each verbatim and say what is wrong.
5. "Reverse gaps": up to 10 baseline items that are important and that COMPILED lacks entirely (things the layer missed).
6. Two-sentence verdict for this section: does (a)+(d) dominate?
