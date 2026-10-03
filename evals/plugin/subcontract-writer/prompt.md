---
name: subcontract-writer
description: Writes a subcontract for the awarded synthetic flooring bid from a firm template with a planted indemnity defect and stale example data; graded on bid fidelity, template fixes and placeholders.
tags: [synthetic, subcontract-writer]
runs: 1
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task. When the skill would ask you to confirm extracted structure, scope or a data model, treat it as confirmed and continue."
---

/construction:subcontract-writer

Write the subcontract for the awarded flooring bid. Template: "16 - Templates/Subcontract Template - Example Builders.docx". Awarded bid: "03 - Subcontractor Bids/BP-09 Flooring/01 - Gulfshore Resilient Floors LLC.pdf" (base bid; no alternates accepted). Specification sections: "02 - Specifications/Specification Sections". Contractor: Example Builders, Inc.; subcontract number EB-24009; project Sanibel Fire and Rescue Station 172; retainage 10 percent; liquidated damages flow down at $1,500 per calendar day. The flooring sections have no extended warranty article, so apply the general one-year warranty. Treat every checkpoint as confirmed, fix anything in the template that is legally deficient and flag it, and produce the document as "Subcontract_Gulfshore_EB-24009.docx" in the project root with "scope_data.json" and "template_data.json" beside it.
