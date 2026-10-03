---
name: bid-tabulator
description: Tabulates five synthetic flooring bids (one scanned, one letter-style) with planted problems; graded against the per-bid ground truth.
tags: [synthetic, bid-tabulator]
runs: 1
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task. When the skill would ask you to confirm extracted structure, scope or a data model, treat it as confirmed and continue."
---

/construction:bid-tabulator

Tabulate the five subcontractor bids in "03 - Subcontractor Bids/BP-09 Flooring" for scope "BP-09 Flooring". The file "00 - Bid Package Scope Sheet.pdf" is the GC's scope sheet, not a bid. Extract every field the bids contain (totals, line items with units and unit prices, alternates with their sign, allowances, inclusions, exclusions, qualifications, validity, bond, addenda acknowledged) as submitted, without normalizing or correcting them; where the line items do not add up to a bidder's stated total, keep both and flag it. One bid is a scan with no text layer: rasterize it and read it with vision, and flag any value you cannot read as unclear rather than guessing. Name the workbook "Bid_Tabulation_BP-09.xlsx" in the project root.
