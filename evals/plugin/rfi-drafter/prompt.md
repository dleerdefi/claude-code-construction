---
name: rfi-drafter
description: Drafts an RFI on a seeded door-220 discrepancy (real A500 schedule vs synthetic Addendum 01) in the firm's template, exports it and records the issue in the registry.
tags: [real, rfi-drafter]
runs: 1
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
append_system_prompt: "This is an unattended evaluation run in a construction project folder. Nobody can answer questions: make reasonable choices, do not wait for confirmation, and finish the task. When the skill would ask for approval of a draft, treat it as approved and export."
---

/construction:rfi-drafter

Draft RFI-001 about door 220. Addendum 01 ("04 - Addenda") revises door 220 on sheet A500 ("01 - Drawings") from a 3'-0" leaf width and hardware set 10 to a 3'-6" width and hardware set 11, but leaves the frame type, frame material and the head, jamb and sill detail references unchanged. Ask the architect to confirm whether frame type 1 (HM) and details A11/A510, F11/A510 and L1/A510 still apply to the wider leaf, and to confirm hardware set 11. Verify the facts against the documents first.

Use the firm's RFI template "16 - Templates/RFI Template - Example Builders.docx"; its field mapping is already stored at ".construction/skills/rfi-drafter/rfi_template_map.json". From: Example Builders, Inc. (Project Engineer). To: Schenkel Shultz Architecture. Date: today. Response needed within 10 working days; the affected work is door frame procurement.

Write the RFI data to "rfi_001.json" and the exported document to "RFI-001.docx", both in the project root. Also add this discrepancy to the issue registry and mark it escalated to RFI-001.
