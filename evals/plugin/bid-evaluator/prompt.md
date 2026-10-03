---
name: bid-evaluator
description: Evaluates five tabulated synthetic flooring bids against the real spec sections; graded on whether each planted problem (silent omission, math error, buried exclusion, budget pricing, unclear scan value, short validity) is caught.
tags: [synthetic, bid-evaluator]
runs: 1
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task. When the skill would ask you to confirm extracted structure, scope or a data model, treat it as confirmed and continue."
---

/construction:bid-evaluator

Evaluate the tabulated bids for package BP-09 Flooring. The tabulation JSON files are in ".construction/skills/bid-tabulator/bids/" (one per bidder); the bid PDFs and the GC's scope sheet are in "03 - Subcontractor Bids/BP-09 Flooring"; the specification sections are in "02 - Specifications/Specification Sections". Answers to the scope questions you would normally ask: the package is the six sections listed on the scope sheet; the GC provides temporary floor protection, final cleaning and dumpsters; five bids were received, each on the bidder's own form; no drawing review is needed for this evaluation. Build the evaluation JSON as "bid_evaluation.json" in the project root and export the workbook as "Bid_Evaluation_BP-09.xlsx" in the project root. Stop after the evaluation; do not start a subcontract.
