# GC Review (draft) — Submittal 047 / 23 74 13-001 R0 — Packaged Rooftop Units

Project: Chesapeake Ridge Middle School — Classroom & Multipurpose Addition (education.k12, Group E with A-3)
Subcontractor: Bayline Mechanical Contractors; supplier Mid-Atlantic HVAC Sales. Types: Product Data, Shop Drawings. Received 2026-09-21.

**Unattended run.** Facility type education.k12 taken from the task; nobody could confirm it or authorize code research, so every regulatory question below is left open. The compiled knowledge for 23 74 13 is **draft** (global Division 01 rules only; no 23 74 13 profile, no Division 23 baseline, no education overlay). The context carries no section checks, hooks or interfaces; the per-unit checks, reconciliations, interfaces and compliance questions below were derived from the contract documents (23 74 13 Parts 1–3, M-601, E-601, S-001, S-201, A-511, P-501, FA-001, 23 09 00, 23 05 48, 01 25 00) and PE practice. Review mode: the context says package; the section schedules six tagged units, so each RTU was reviewed as an element and the package checks run once.

Elements traced from the CDs: RTU-1, RTU-2, RTU-3, RTU-4, RTU-5, RTU-6 (23 74 13 1.2.A; M-601). Submitted: RTU-1 through RTU-5. Missing: RTU-6. Extra items: Lennox product-line literature (pp. 53–60, 70) supporting an unnamed manufacturer (see F-03); blank start-up forms (pp. 92–94, informational, acceptable).

## 1. Findings

| id | element | severity | owner | grade | what the submittal shows (page) | what governs (document, location) | action (who does what) |
|---|---|---|---|---|---|---|---|
| F-01 | package (1.3.C) | critical | subcontractor | NOT FOUND | No wind/seismic restraint calculations or unit-to-curb / curb-to-structure attachment details. Cover letter p. 2: "provided after release of the order"; curb detail p. 69 and Carrier IOM p. 44: "attachment hardware by installing contractor, per local code"; scope clarification p. 95 item 3: available after release "at an additional fee" | 23 74 13 1.3.C (sealed calcs submitted with product data; submittal incomplete without them); 23 05 48 1.3.C; S-001 (supplier designs attachment for V_ult 115 mph Exp. B, SDC B, Ip 1.0; Maryland PE seal); 23 74 13 3.2.A (units set per the sealed restraint submittal) | Subcontractor: submit Maryland-PE-sealed calculations and attachment details for every unit and curb (including RTU-5 curb-to-dunnage) with the resubmittal; no additional fee, it is in the Contract Sum. GC: do not release any unit for production without them. |
| F-02 | RTU-6 | critical | subcontractor | NOT FOUND | Transmittal p. 1 "RTU-1 through RTU-5 (5 units)"; equipment summary p. 4 and curb schedule p. 68 omit RTU-6 | 23 74 13 1.2.A (RTU-1 through RTU-6); M-601 RTU-6 (Carrier 48LC 7.5 ton, 3,000 CFM, 600 OA CFM, 90/68 MBH, 150/121 MBH, 1.00 ESP, 460/3, MCA 28, MOCP 35, 1,100 lb, 14 in. curb above membrane); S-201 (1,500 lb allowable, Grid A-B/8-9); A-511 (20 in. overall curb); E-601 ckt 43,45,47; P-501 (150 MBH, 3/4 in.) | Subcontractor: add RTU-6 selection, dimensional drawing, curb, wiring, controls, options, warranty and restraint calcs; resubmit. Required element missing → package incomplete. |
| F-03 | RTU-5 | high | subcontractor | CONFLICTING | Lennox Energence LGH360H4E (p. 4, p. 25); p. 4 note "48LC chassis available through 25 tons; 30-ton selection provided from the Lennox Energence line"; transmittal p. 1 deviations "None" | 23 74 13 2.1.A (BOD Carrier 48LC), 2.1.B (acceptable: Trane, Daikin Applied, JCI/York), 2.1.C → 01 25 00; 01 25 00 1.3.B (unnamed manufacturer = substitution; Form 01 25 00-A separately and before the product submittal, with point-by-point comparison and effect on structural/electrical/plumbing/controls/roofing) and 1.3.C (returned "Rejected – Resubmit" without technical review) | Subcontractor: select RTU-5 from a named manufacturer, or submit Substitution Request 01 25 00-A before the resubmittal (Architect has 14 days). GC: return the RTU-5 item per 01 25 00 1.3.C; the technical notes on RTU-5 below (F-11, F-12, F-17) are given so the resubmittal can address them whatever product is chosen. |
| F-04 | RTU-5 | medium | design_team | OPEN | p. 4 note states the BOD line (48LC) is not made at 30 tons | M-601 RTU-5 basis of design "Carrier 48LC, 30 ton"; 23 74 13 2.1.A | Design team (Tidewater): confirm the intended basis-of-design product for RTU-5 and whether the named acceptable manufacturers' 30-ton products are intended; GC logs as issue for `rfi-drafter` (rfi_candidate). |
| F-05 | RTU-4 | critical | subcontractor | CONFLICTING | Operating weight 2,780 lb incl. 20-in. curb, coated coils and stainless pan (p. 24, p. 66); corner weights 760/720/660/640 | S-201 note 6 table: RTU-4 at Grid A-B/2-3 allowable 2,500 lb; units exceeding bear on SE-designed dunnage per 5/S-501, weights submitted before steel fabrication; M-601 RTU-4 1,850 lb and note 4 (confirm against S-201); 23 74 13 3.2.B (not set until supplemental steel in place) | Subcontractor: verify the stated weight (a 12.5-ton unit at 2,780 lb against the 15-ton RTU-1 at 2,165 lb is implausible even with coated coils and a stainless pan) and drop unscheduled options if they drive it. GC: if the weight stands, submit it to Keystone (SE) for dunnage per 5/S-501 before steel fabrication; hold RTU-4 set until supplemental steel is in. Raised to critical: roof framing and steel fabrication timing. |
| F-06 | RTU-4 | high | subcontractor | CONFLICTING | Filters 2-in. MERV 8 pleated, standard rack; "4-in. rack option FLT4 not selected" (p. 23; p. 85 "No (2-in. MERV 8 std.)") | 23 74 13 2.3.A (4-in. MERV 13 per ASHRAE 52.2, factory rack, gasketed tracks, hinged door, all units); M-601 RTU-4 "4 in. MERV 13" | Subcontractor: select the 4-in. MERV 13 factory rack for RTU-4 and reconfirm the fan selection with loaded filters (2.2.C); resubmit. Factory option — must be fixed before release. |
| F-07 | RTU-2 | high | subcontractor | CONFLICTING | Minimum OA damper position set for 1,500 CFM (p. 13) | M-601 RTU-2 OA CFM (min) 1,800; 23 74 13 1.5.C (scheduled OA are design minimums from ASHRAE 62.1; do not reduce), 2.4.A | Subcontractor: correct RTU-2 minimum OA setting to 1,800 CFM; TAB (23 05 93) verifies at start-up per 1.7.B. Classroom ventilation in a school — fix before release. |
| F-08 | RTU-1 | high | subcontractor | CONFLICTING | High-heat furnace option, input/output 350/283 MBH, 43°F rise (p. 7; p. 85 "High-heat furnace: RTU-1 Yes, RTU-2 No") | M-601 RTU-1 heating 250/202 MBH and note 6 (gas input is the basis for the P-501 riser; changes require Engineer approval); P-501 note 3 table (RTU-1 250 MBH, 3/4 in. branch; total 1,750 MBH; riser 1-1/2 in.; meter 1,800 CFH; any increase requires Engineer re-verification); 23 74 13 2.5.A (input as scheduled) | Subcontractor: select the scheduled 250 MBH furnace (as submitted for RTU-2, which serves an identical wing) or list it as a deviation with reason per 1.3.D. GC: if the design team accepts 350 MBH, P-501 branch, riser and the 1,800 CFH meter must be re-verified by the Engineer (connected load would rise to 1,850 MBH) and the utility meter application updated. |
| F-09 | RTU-3 | high | subcontractor | CONFLICTING | Power exhaust, 3 HP modulating, 6,500 CFM at 0.3 in. w.g. in place of barometric relief (p. 15, p. 18; p. 85 "Barometric relief: No (power exhaust)"); hood adds 18 in. on the return end (p. 62) | M-601 RTU-3 economizer "Diff. enthalpy, baro relief"; 23 74 13 2.2.A and 2.4.A (barometric relief) | Subcontractor: provide barometric relief as scheduled, or identify power exhaust as a deviation with the reason (1.3.D) for the Engineer's decision. Unidentified deviation; it drives F-10 and the unit footprint. |
| F-10 | RTU-3 | high | subcontractor | CONFLICTING | MCA 88.0 A / MOCP 100 A, "values include 10 HP supply motor and 3 HP power exhaust motor" (p. 19; wiring p. 72) | M-601 RTU-3 MCA 62 / MOCP 70, note 7 (do not exceed); 23 74 13 2.6.B (shall not exceed; options that raise MCA are a deviation); E-601 MDP-1 ckt 25,27,29: 70 A/3P, 3 #4 + 1 #8 G in 1-1/4 in., general note 4 | Subcontractor: reselect RTU-3 within the scheduled MCA/MOCP (remove power exhaust; confirm whether the 10 HP high-static motor is needed at 1.75 in. ESP) or list the deviation with reason. GC: hold the RTU-3 feeder rough-in; if the deviation is accepted, Tidewater must revise E-601 ckt 25-29 (breaker, feeder, conduit) and electrical subcontractor re-prices. |
| F-11 | RTU-5 | high | subcontractor | CONFLICTING | Curb schedule p. 68: RTU-5 Lennox C1CURB76A-1, 20 in. overall; note "14 in. above finished roof plus 6 in. insulation" applied to all units | A-511 detail 3 table: RTU-5 insulation + cover board 9 in. (near tapered ridge) → overall curb 23 in.; 23 74 13 2.8.B; M-601 note 3; A-511 "shimming to make up height is not permitted"; A-511 note: verify insulation thickness with the roofing submittal before ordering curbs | Subcontractor: order the RTU-5 curb at 23 in. overall (or the height A-511 gives for whatever unit is finally selected) and correct the p. 68 note. GC: before curb release, verify the A-511 thicknesses at all six units against the approved roofing (07 54 23) submittal and A-131 tapered layout. |
| F-12 | RTU-5 | medium | subcontractor | CONFLICTING | Supply fan: belt-drive forward-curved blower, 15 HP with VFD (p. 28) | 23 74 13 2.2.C (direct-drive with VFD or ECM motor) | Subcontractor: provide a direct-drive supply fan or list the belt drive as a deviation with reason. Carry into the reselection under F-03. |
| F-13 | RTU-1, -2, -3, -4, -5 | medium | subcontractor | NOT FOUND | Dirty filter switch (DFS) "Not included" on all units (p. 85); BACnet lists p. 79 "switch is accessory DFS", p. 80 "requires field-installed filter switch kit (not included)" | 23 74 13 2.7.C (dirty-filter differential-pressure switch, factory-mounted across the filter bank, reported to BAS); 23 09 00 Table 23 09 00-A (filter DP status DI) | Subcontractor: add the factory-mounted DFS on every unit (and RTU-6) and show the point as provided; must be in the factory order, so before release. |
| F-14 | RTU-1, -2, -3, -4 | medium | subcontractor | CONFLICTING | Carrier compressors 1 year standard; 5-year compressor parts option W05 "not included in this selection; available at additional cost" (p. 90) | 23 74 13 1.6.B (compressors 5 years parts from Substantial Completion, included in the Contract Sum) | Subcontractor: include option W05 (or equivalent) on all Carrier units at no change to the Contract Sum; resubmit warranty pages. |
| F-15 | all units | medium | subcontractor | CONFLICTING | Warranty 1 year parts "from start-up or 18 months from shipment, whichever is first", labor not included (Carrier p. 90; Lennox p. 91 1 year parts, labor not included) | 23 74 13 1.6.A (1 year parts and labor from Substantial Completion); 1.6.B/C (from Substantial Completion) | Subcontractor: provide a warranty statement meeting 1.6.A–C (labor included; terms run from Substantial Completion, not start-up or shipment). |
| F-16 | package (1.3.D) | high | subcontractor | CONFLICTING | Transmittal p. 1 "Deviations from Contract Documents: None"; GC stamp "Reviewed for conformance" 2026-09-19; p. 95 item 1 "selected to the M-601 schedule" | 23 74 13 1.3.D (list every deviation from the section and M-601 on the transmittal with reason); 01 25 00 1.3.D (deviations not identified are not accepted even if stamped). Deviations found: F-03, F-05, F-06, F-07, F-08, F-09, F-10, F-11, F-12, F-13, F-14, F-15, F-25, and F-01 | Subcontractor: list every deviation with its reason on the resubmittal transmittal. GC: the contractor stamp was applied without catching these; re-review the resubmittal before stamping. |
| F-17 | RTU-5 | medium | gc | OPEN | Lennox LGH360 198 x 92 x 68 in. (p. 64), curb footprint 194 x 88 in. (p. 68), corner weights 1,120/1,080/1,010/970 lb (p. 29), service clearances 48 in. all sides | S-201 RTU-5 on dunnage per 5/S-501 (shown on plan), note 7 (any change in location, footprint or weight to the SE before fabrication); 5/S-501 and roof plan not in the excerpts | GC: send the RTU-5 curb footprint, corner weights and clearances (pp. 29, 64, 68) to Keystone to confirm the 5/S-501 dunnage layout and curb-to-dunnage bearing before steel fabrication; repeat for whatever product replaces it under F-03. |
| F-18 | package | gc | OPEN | p. 87 "Duct smoke detectors (supply and return): by others"; p. 95 item 5 | M-601 note 5 and FA-001 note 12: detectors, sampling tubes, remote test stations furnished by 28 46 00; **installed in the unit or duct by the mechanical contractor (Division 23)**; wired by 28 46 00; mechanical provides access doors and sampling-tube clearance; 23 74 13 3.2.A | GC: notify Bayline that detector installation, access doors and sampling-tube clearance are in its scope; route controller terminal pages 75–76 to the fire alarm contractor (28 46 00) for shutdown wiring. Subcontractor: correct the scope clarification on resubmittal. |
| F-19 | package | gc | NOT FOUND | p. 95 item 4 "units ship on separate trucks; crane and rigging by others" | No contract document assigns rigging; 23 74 13 3.2.A (set units on curbs) — unmapped "by others" | GC: assign crane and rigging (Bayline subcontract or GC general conditions) in writing before resubmittal; otherwise scope gap at equipment set. |
| F-20 | package | medium | gc | OPEN | 14-week lead time from release of approved submittal; release requested by 2026-10-10 (p. 1, p. 2, p. 95 item 4) | Project schedule not in the excerpts; F-01, F-02 and F-03 require a resubmittal, so 2026-10-10 cannot be met | GC: re-baseline rooftop unit delivery (resubmittal plus 14 weeks), the 01 25 00 14-day substitution cycle for RTU-5, the steel/dunnage sequence (F-05, F-17) and the curb-before-roofing sequence; RTU-6 has not been selected at all. |
| F-21 | all units | medium | gc | OPEN | Efficiency summary p. 89: "meet or exceed ... ASHRAE 90.1-2013 Table 6.8.1-1"; LGH360 "meets the minimum IEER with the MSAV option" (EER 10.6 / IEER 12.4, p. 26, p. 88) | G-002: energy code per Maryland Building Performance Standards and Severn County amendments in effect at the permit application, ASHRAE 90.1 mechanical path, edition per permit set; 23 74 13 1.5.B; M-601 note 2 | GC: pull the adopted energy code edition from the permit set / permit conditions (or run `/construction:code-researcher`). Subcontractor: restate the efficiency comparison for each unit against that edition, not 90.1-2013; RTU-5 is marginal and may need reselection if the adopted minimums are higher. Not a code finding until the edition is retrieved. |
| F-22 | all units | low | subcontractor | NOT FOUND | AHRI 340/360 certificates provided (p. 88); no UL 1995 / UL 60335-2-40 listing or ANSI Z21.47 / CSA 2.3 furnace certification shown | 23 74 13 1.5.A | Subcontractor: provide listing/certification statements for each model with the resubmittal. |
| F-23 | RTU-1, -2, -3, -4 (RTU-5 via F-12) | low | subcontractor | OPEN | Fan selections state scheduled CFM at scheduled ESP (e.g., p. 8: 6,000 CFM at 1.50 in. ESP, 2.35 in. total "incl. unit internal losses"); no statement of the loaded-filter allowance | 23 74 13 2.2.C (selected at scheduled ESP with filters loaded to 0.5 in. w.g.) | Subcontractor: state on each selection that the 0.5 in. w.g. loaded-filter allowance is included (or reselect). |
| F-24 | package | low | gc | OPEN | p. 95 item 1 "selected to the M-601 schedule as of the issued-for-construction set" | IFC set 2026-03-27 with Addendum 2 (2026-04-14) incorporated; RFI/ASI/bulletin logs not in the excerpts | GC: confirm with Bayline that Addendum 2 and any responded RFIs/ASIs affecting Division 23 were incorporated; note the drawing revision on the resubmittal transmittal. |
| F-25 | RTU-4 | low | subcontractor | OPEN | Unscheduled options: stainless-steel condensate pan, coated condenser and evaporator coils "(lab exhaust proximity)", "dual-enthalpy economizer" (p. 20, p. 85) | M-601 RTU-4 (not scheduled); 23 74 13 1.3.D | Subcontractor: list as additions on the transmittal with reason and confirm no cost change; see F-05 for their effect on weight. |
| F-26 | RTU-1, -2, -3, -4 (curbs) | medium | gc | OPEN | Curb footprints p. 68 (118x56, 118x56, 140x70, 104x56); RTU-3 unit 144 in. plus 18 in. power exhaust hood (p. 62); service clearances 36–48 in. (pp. 61–63) | S-201 note 6/7: curbs bear on support angles per 4/S-501 between joists; any change in footprint to the SE before fabrication; 4/S-501 and the mechanical roof plan are not in the excerpts | GC: send p. 68 footprints and pp. 61–63 dimensions to Keystone and the steel fabricator to confirm the 4/S-501 support-angle layout, and check clearances on the roof plan before steel fabrication. Unverifiable from the documents in hand. |
| F-27 | package (1.7.A) | low | subcontractor | OPEN | p. 94: "factory-authorized start-up by Bayline's service division", one trip per unit | 23 74 13 1.7.A (start-up by a factory-authorized service representative, manufacturer's checklist, 72 h notice to Engineer and CxA) | Subcontractor: provide the manufacturer's written authorization of Bayline's service division for both product lines, and confirm the start-up scope of 1.7.B (charge, combustion analysis, economizer/min OA with TAB, smoke shutdown, BACnet). |

Counts: critical 3 (F-01, F-02, F-05); high 8 (F-03, F-06, F-07, F-08, F-09, F-10, F-11, F-16); medium 11 (F-04, F-12, F-13, F-14, F-15, F-17, F-18, F-19, F-20, F-21, F-26); low 5 (F-22, F-23, F-24, F-25, F-27). Total 27.

## 2. Suggested GC disposition

**Return to subcontractor — incomplete; revise and resubmit.** Plus RFI candidate (F-04, basis of design for RTU-5). Plus compliance questions open (energy code edition; A2L refrigerant) — research before release for fabrication.

Drivers: **F-02** (RTU-6, a scheduled unit, is not in the package) and **F-01** (the sealed wind/seismic restraint submittal that 1.3.C says the product submittal is incomplete without, offered only after release and at extra cost). Immediately behind them: F-03 (RTU-5 is an unnamed manufacturer with no 01 25 00 substitution request — returned without technical review per 01 25 00 1.3.C) and F-05 (RTU-4 at 2,780 lb exceeds the 2,500 lb roof framing allowance). Do not forward to the design team in this form; the transmittal's "Deviations: None" is wrong on at least thirteen counts (F-16).

## 3. Coordination routing

| interface / trade | section(s) | relevant? | what to send them (pages/items) | what is needed back | confirm who furnishes/installs/connects | gate milestone | need-by (relative to construction sequence) |
|---|---|---|---|---|---|---|---|
| Structural engineer (Keystone, via A/E) | S-001, S-201, S-501 | yes | pp. 9, 14, 19, 24, 29, 66 (weights, corner weights), p. 68 (curb footprints), pp. 61–64 (dimensions); F-01, F-05, F-17, F-26 | Dunnage design per 5/S-501 for RTU-4 if its weight stands; confirmation of 4/S-501 support-angle layout at all curbs and 5/S-501 dunnage at RTU-5; review of the sealed restraint calcs when submitted | Restraint design by equipment supplier (S-001, 23 05 48 1.3.C); dunnage design by SE (S-201 note 6); attachment hardware per sealed calcs, installed by Bayline | steel_fabrication (roof framing / dunnage) | Before roof steel and support-angle fabrication release; S-201 note 6 "submit equipment weights before steel fabrication" |
| Steel fabricator / erector | 05 12 00 (support angles 4/S-501, dunnage 5/S-501) | yes | p. 68 curb schedule footprints; SE's response above | Shop drawings showing angle/dunnage layout matching the curb footprints | Angles and dunnage by steel; curbs by unit manufacturer (2.8.A) | steel_fabrication | With the SE confirmation, before steel shop drawings are released |
| Electrical subcontractor / Tidewater (E-601) | 26 xx xx, E-601 | yes | p. 19 (RTU-3 MCA 88/MOCP 100), pp. 9, 14, 24, 29 (others), pp. 71–74 power wiring; F-10 | Either confirmation that RTU-3 is reselected to MCA 62/MOCP 70, or revised E-601 ckt 25,27,29 (breaker, feeder, conduit) from the Engineer with electrical pricing | Feeder and conduit by electrical (p. 87); factory disconnect and GFCI outlet by unit (2.6.A; E-601 note 7, no separate 120 V circuit) | electrical_rough_in (feeders to roof) | Before conduit rough-in to the RTU locations; E-601 note 4 "verify against approved equipment submittals before rough-in" |
| Plumbing / gas (Division 22) and Tidewater (P-501) | 22 xx xx, P-501 | yes | p. 7 (RTU-1 350 MBH), pp. 12, 17, 22, 27 (inputs, connection sizes, inlet pressure), pp. 61–64 (gas connection locations); F-08 | Engineer re-verification of branch, riser and 1,800 CFH meter if RTU-1 stays at 350 MBH; Div 22 confirmation that line regulators, drip legs and shutoffs at each unit are in its scope (p. 87 says "by others") | Regulators by Division 22 (2.5.B, P-501 note 3); unit inlet 5–13 in. w.c. accepts the 7 in. w.c. supply (Carrier p. 41; Lennox range not stated) | gas_rough_in / utility meter application | Before roof gas piping fabrication and before the meter set is ordered from the utility |
| Roofing (07 54 23) | 07 54 23, A-511, A-131 | yes | p. 68 curb schedule, p. 69 curb cross-section, p. 67; F-11 | Approved roofing submittal insulation/cover-board thickness at each unit (A-511 table: 6 in. at RTU-1–4, -6; 9 in. at RTU-5); confirmation of cant, flashing to top of nailer and counterflashing scope | Curb with nailer by unit manufacturer (2.8.A); cant, membrane flashing, counterflashing by roofer (A-511) | curb_order (before roofing starts at unit locations) | Curbs must be ordered to final overall height before release — A-511 "verify with the roofing submittal before ordering curbs" |
| Fire alarm (28 46 00) | 28 46 00, FA-001 note 12 | yes | pp. 75–76 (smoke detector shutdown terminals), p. 87, p. 95 item 5; F-18 | Detector models, sampling-tube lengths and remote test station locations so Bayline can provide access doors and clearance; shutdown wiring plan to unit terminals | Detectors furnished and wired by 28 46 00; installed by Division 23 (Bayline); unit provides shutdown terminals (2.7.B) | duct_and_unit_installation | Before duct/unit installation at each RTU; detector submittal 28 46 00 should be in hand first |
| Controls (23 09 00) | 23 09 00 | yes | pp. 77–84 (controllers, BACnet points, MS/TP wiring, CO2/space sensor compatibility), p. 85 (DFS not included); F-13 | Confirmation the controls contractor's trunk, space sensors and CO2 sensor (RTU-5) match the SystemVu/Prodigy inputs (0–10 V); points list acceptance against Table 23 09 00-A once the DFS is added | Controller, BACnet interface, unit-mounted OA sensors by unit manufacturer; trunk, space/CO2 sensors, graphics by controls contractor (23 09 00 2.14.A/B; p. 84) | controls_submittal / MS_TP_trunk_rough_in | Before the 23 09 00 submittal is finalized and before trunk rough-in |
| Sheet metal / ductwork (Division 23) | 23 31 13 (duct) | yes | p. 65 (duct openings and curb-to-duct transitions), p. 62 (RTU-3 hood) | Duct shop drawings matching the curb openings for each size | Duct transitions by sheet metal; curb cross-members shipped loose by unit (p. 86) | duct_fabrication | Before duct fabrication at RTU connections |
| TAB (23 05 93) | 23 05 93 | yes | pp. 8, 13, 18, 23, 28 (min OA settings; note F-07 at RTU-2) | Minimum OA damper position verification at scheduled CFM at start-up (1.7.B) | TAB by 23 05 93 (p. 95 item 6 "by others" — mapped) | start_up | At unit start-up; no action before resubmittal |
| Commissioning authority / Engineer (start-up) | 23 74 13 1.7, 01 91 13 if any | yes | pp. 92–94; F-27 | Acceptance of start-up provider and checklist; 72 h notice protocol | Start-up by factory-authorized rep (1.7.A) | start_up | Before start-up scheduling |
| Crane / rigging | — | yes | p. 95 item 4; F-19 | Written assignment of crane, rigging and setting | Unassigned in the CDs — GC decides (Bayline subcontract or GC) | equipment_set | Before resubmittal is returned, so the price and sequence are known before delivery |
| Design team (Tidewater / Harbor & Lane) | 23 74 13, M-601, 01 25 00 | yes | F-04 (RTU-5 BOD), and the deviations in F-08, F-09, F-10 if Bayline elects to keep them | Answer on BOD for 30-ton unit; decisions on any retained deviations; substitution review within 14 days if Form 01 25 00-A is filed | — | design_review / procurement_release | With the issue log now (F-04 is an RFI candidate); do not wait for the resubmittal |
| Owner (Severn County Public Schools) | 23 74 13 1.7.C, 1.6 | no | — | — | No owner-furnished items; temporary heat approval (1.7.C) and warranty are not at issue in this review | — | — |

## 4. Compliance questions

| question | authority | status | elements affected |
|---|---|---|---|
| Which ASHRAE 90.1 edition (with Maryland Building Performance Standards and Severn County amendments) governs at the permit application date, and what are its minimum EER/IEER and thermal-efficiency values for each unit's capacity class? The submittal compares against 90.1-2013 (p. 89); RTU-5 is stated to meet the minimum only with the MSAV option. | Maryland Building Performance Standards (COMAR 09.12.51 per G-002) / Severn County building official; edition per permit set and permit conditions | open: needs research (`/construction:code-researcher`, topic: energy code minimum efficiencies for packaged rooftop units); see F-21 | RTU-1 through RTU-6 |
| Does the adopted energy code require economizer fault detection and diagnostics on these units (23 74 13 2.4.B "as required by the adopted energy code")? FDD is submitted on all units regardless (pp. 83, 85). | Same as above | open: needs research — no shortfall either way, since FDD is provided; record for the file | RTU-1 through RTU-6 |
| Does the adopted mechanical/fuel-gas code edition (IMC/IFGC as adopted by Severn County, G-002) accept the A2L refrigerant R-454B in packaged rooftop units serving a Group E / A-3 building, with any county amendments? All submitted units are R-454B (pp. 6, 11, 16, 21, 26). | Severn County mechanical AHJ (IMC as adopted) | open: needs research (topic: A2L refrigerant acceptance in packaged rooftop equipment) | RTU-1 through RTU-6 |
| Duct smoke detectors in supply and return of each unit over 2,000 CFM | Fire marshal / IMC as adopted — but the requirement is already a contract requirement (FA-001 note 12, M-601 note 5) | consistent: CDs require detectors at all six units; unit controllers provide shutdown terminals (pp. 75–76). Scope split finding F-18 is contractual, not code | RTU-1 through RTU-6 |
| Wind and seismic attachment of rooftop equipment (V_ult 115 mph Exp. B, Risk Category III, SDC B, Ip 1.0) with Maryland PE seal | Maryland State Board for Professional Engineers (seal); Severn County building official (structural review) | finding: F-01 — requirement is in S-001 / 23 74 13 1.3.C / 23 05 48 1.3.C; the submittal omits it. No code value cited beyond S-001 | all units and curbs |
| Minimum outdoor air (scheduled OA CFM are design minimums derived from ASHRAE 62.1 per 1.5.C) | Mechanical code / ASHRAE 62.1 as adopted — not researched; the contract values govern | finding: F-07 (RTU-2 set to 1,500 CFM against 1,800 scheduled) — a contract-document finding; no code value cited | RTU-2 |
| UL 1995 / UL 60335-2-40 listing and ANSI Z21.47 / CSA 2.3 furnace certification | Specification 1.5.A (and the electrical/mechanical inspectors who will look for the listing mark) | finding: F-22 — evidence not in the submittal | all units |
| Gas supply pressure to the units (2 psig roof distribution regulated to 7 in. w.c. at each unit) | IFGC as adopted — not researched; P-501 and 2.5.B give the design | consistent: Carrier inlet range 5–13 in. w.c. (p. 41) accepts 7 in. w.c.; Lennox range not stated (unverifiable) | RTU-1 through RTU-5 |

No code section or value is cited above beyond what G-002, S-001 and the specification state.

## 5. Coverage ledger

Element checks (derived from the CDs; the compiled context has none for this section): 1 bod-model (2.1, M-601) · 2 cooling-capacity (2.2.B, ±3 %) · 3 heating-input-output (2.5.A, M-601, P-501) · 4 supply-fan (2.2.C) · 5 compressor-staging (2.2.D) · 6 filters (2.3.A) · 7 economizer-min-oa (2.4, 1.5.C) · 8 electrical-mca-mocp (2.6.B, E-601) · 9 operating-weight (S-201, 3.2.B) · 10 curb-height (2.8.B, A-511) · 11 bacnet-points (2.7.A, 23 09 00 Table A) · 12 dirty-filter-switch (2.7.C) · 13 smoke-shutdown-terminals (2.7.B) · 14 scheduled-options (M-601 note 1, 2.2.E, 2.6.A) · 15 warranty (1.6) · 16 dimensions-clearances-footprint (1.3.B, S-201 note 7) · 17 certifications (1.5.A) · 18 efficiency-energy-code (1.5.B) · 19 gas-connection (2.5.B, P-501) · 20 sound-data (1.3.A).

| element | check | status | finding | note / evidence |
|---|---|---|---|---|
| RTU-1 | 1 bod-model | pass | | Carrier 48LCDA17, 15 ton (p. 5) = M-601 BOD |
| RTU-1 | 2 cooling-capacity | pass | | 182.4/137.1 MBH ≥ 180/135 (p. 6) |
| RTU-1 | 3 heating-input-output | finding | F-08 | 350/283 vs 250/202 (p. 7; M-601, P-501) |
| RTU-1 | 4 supply-fan | finding | F-23 | 6,000 @ 1.50, direct-drive VFD matches (p. 8); loaded-filter allowance not stated |
| RTU-1 | 5 compressor-staging | pass | | 2 scroll, 2 stages (p. 6) |
| RTU-1 | 6 filters | pass | | 4-in. MERV 13 (p. 8, p. 85) |
| RTU-1 | 7 economizer-min-oa | pass | | Diff. enthalpy, baro relief, 1,800 CFM, FDD (p. 8) |
| RTU-1 | 8 electrical-mca-mocp | pass | | 46/60 vs 48/60 (p. 9; E-601 ckt 13-17 60 A) |
| RTU-1 | 9 operating-weight | pass | | 2,165 lb ≤ 2,500 allowable (p. 9; S-201); 15 lb over scheduled 2,150, within allowance |
| RTU-1 | 10 curb-height | pass | | 20 in. overall (p. 68) = A-511 |
| RTU-1 | 11 bacnet-points | pass | | SystemVu native MS/TP; Table A points provided except filter DI (p. 79) — see 12 |
| RTU-1 | 12 dirty-filter-switch | finding | F-13 | Not included (p. 85) |
| RTU-1 | 13 smoke-shutdown-terminals | pass | | Supply/return terminals (p. 75) |
| RTU-1 | 14 scheduled-options | pass | | Hinged doors, hail guards, disconnect, phase monitor, GFCI (p. 85) |
| RTU-1 | 15 warranty | finding | F-14, F-15 | Compressor 1 yr; labor excluded; start at start-up (p. 90) |
| RTU-1 | 16 dimensions-clearances-footprint | finding | F-26 | 122x60x55 (p. 61); support-angle layout and roof plan not in excerpts |
| RTU-1 | 17 certifications | finding | F-22 | AHRI yes (p. 88); UL/ANSI not shown |
| RTU-1 | 18 efficiency-energy-code | finding | F-21 | EER 11.2 / IEER 13.8 vs 90.1-2013 only (p. 89); edition open |
| RTU-1 | 19 gas-connection | pass | | 3/4 in. NPT, 5–13 in. w.c. (p. 7) vs P-501 3/4 in., 7 in. w.c.; branch changes if F-08 stands |
| RTU-1 | 20 sound-data | pass | | 84 dBA sound power (p. 9) |
| RTU-2 | 1 bod-model | pass | | 48LCDA17 (p. 10) |
| RTU-2 | 2 cooling-capacity | pass | | 182.4/137.1 (p. 11) |
| RTU-2 | 3 heating-input-output | pass | | 250/202 (p. 12) = M-601, P-501 |
| RTU-2 | 4 supply-fan | finding | F-23 | 6,000 @ 1.50 direct-drive VFD (p. 13); allowance not stated |
| RTU-2 | 5 compressor-staging | pass | | 2 stages (p. 11) |
| RTU-2 | 6 filters | pass | | 4-in. MERV 13 (p. 13) |
| RTU-2 | 7 economizer-min-oa | finding | F-07 | Min OA 1,500 vs 1,800 (p. 13) |
| RTU-2 | 8 electrical-mca-mocp | pass | | 46/60 vs 48/60 (p. 14; E-601 ckt 19-23) |
| RTU-2 | 9 operating-weight | pass | | 2,165 ≤ 2,500 (p. 14; S-201) |
| RTU-2 | 10 curb-height | pass | | 20 in. (p. 68) |
| RTU-2 | 11 bacnet-points | pass | | p. 79 |
| RTU-2 | 12 dirty-filter-switch | finding | F-13 | p. 85 |
| RTU-2 | 13 smoke-shutdown-terminals | pass | | p. 75 |
| RTU-2 | 14 scheduled-options | pass | | p. 85 |
| RTU-2 | 15 warranty | finding | F-14, F-15 | p. 90 |
| RTU-2 | 16 dimensions-clearances-footprint | finding | F-26 | p. 61, p. 68 |
| RTU-2 | 17 certifications | finding | F-22 | p. 88 |
| RTU-2 | 18 efficiency-energy-code | finding | F-21 | p. 89 |
| RTU-2 | 19 gas-connection | pass | | 3/4 in., 250 MBH (p. 12) = P-501 |
| RTU-2 | 20 sound-data | pass | | 84 dBA (p. 14) |
| RTU-3 | 1 bod-model | pass | | 48LCDA24, 20 ton (p. 15) = M-601 BOD |
| RTU-3 | 2 cooling-capacity | pass | | 236.5/178.9 vs 240/180: 1.5 % and 0.6 % below, within the 3 % of 2.2.B (p. 16) |
| RTU-3 | 3 heating-input-output | pass | | 350/283 (p. 17) = M-601, P-501 |
| RTU-3 | 4 supply-fan | finding | F-23 | 8,000 @ 1.75 direct-drive VFD, 10 HP high-static (p. 18); allowance not stated; motor choice feeds F-10 |
| RTU-3 | 5 compressor-staging | pass | | 3 stages (p. 16) |
| RTU-3 | 6 filters | pass | | 4-in. MERV 13 (p. 18) |
| RTU-3 | 7 economizer-min-oa | finding | F-09 | Power exhaust instead of baro relief (p. 18, p. 85); min OA 2,400 matches |
| RTU-3 | 8 electrical-mca-mocp | finding | F-10 | 88/100 vs 62/70 (p. 19; E-601 ckt 25-29 70 A) |
| RTU-3 | 9 operating-weight | pass | | 2,740 ≤ 3,000 (p. 19; S-201); 140 lb over scheduled 2,600, within allowance |
| RTU-3 | 10 curb-height | pass | | 20 in. (p. 68) |
| RTU-3 | 11 bacnet-points | pass | | p. 79 |
| RTU-3 | 12 dirty-filter-switch | finding | F-13 | p. 85 |
| RTU-3 | 13 smoke-shutdown-terminals | pass | | p. 75 |
| RTU-3 | 14 scheduled-options | pass | | Note 1 items present (p. 85); relief type under check 7 |
| RTU-3 | 15 warranty | finding | F-14, F-15 | p. 90 |
| RTU-3 | 16 dimensions-clearances-footprint | finding | F-26 | 144 in. + 18 in. hood (p. 62); layout not in excerpts |
| RTU-3 | 17 certifications | finding | F-22 | p. 88 |
| RTU-3 | 18 efficiency-energy-code | finding | F-21 | EER 10.9 / IEER 13.2 (p. 89) |
| RTU-3 | 19 gas-connection | pass | | 3/4 in. unit connection (p. 17) vs 1 in. P-501 branch — reduction at the Div 22 regulator; note for Div 22 |
| RTU-3 | 20 sound-data | pass | | 86 dBA (p. 19) |
| RTU-4 | 1 bod-model | pass | | 48LCDA14, 12.5 ton (p. 20) |
| RTU-4 | 2 cooling-capacity | pass | | 151.2/111.4 ≥ 150/110 (p. 21) |
| RTU-4 | 3 heating-input-output | pass | | 250/202 (p. 22) |
| RTU-4 | 4 supply-fan | finding | F-23 | 5,000 @ 1.50 direct-drive VFD (p. 23); allowance not stated; reselect with MERV 13 rack (F-06) |
| RTU-4 | 5 compressor-staging | pass | | 2 stages (p. 21) |
| RTU-4 | 6 filters | finding | F-06 | 2-in. MERV 8 (p. 23, p. 85) |
| RTU-4 | 7 economizer-min-oa | pass | | Diff. enthalpy, baro relief, 2,000 CFM (p. 23) |
| RTU-4 | 8 electrical-mca-mocp | pass | | 38.5/50 vs 40/50 (p. 24; E-601 ckt 31-35) |
| RTU-4 | 9 operating-weight | finding | F-05 | 2,780 > 2,500 allowable (p. 24; S-201) |
| RTU-4 | 10 curb-height | pass | | 20 in. (p. 68) |
| RTU-4 | 11 bacnet-points | pass | | p. 79 |
| RTU-4 | 12 dirty-filter-switch | finding | F-13 | p. 85 |
| RTU-4 | 13 smoke-shutdown-terminals | pass | | p. 75 |
| RTU-4 | 14 scheduled-options | finding | F-25 | Note 1 items present; unscheduled coated coils, stainless pan (p. 20, p. 85) |
| RTU-4 | 15 warranty | finding | F-14, F-15 | p. 90 |
| RTU-4 | 16 dimensions-clearances-footprint | finding | F-26 | 108x60x51 (p. 63) |
| RTU-4 | 17 certifications | finding | F-22 | p. 88 |
| RTU-4 | 18 efficiency-energy-code | finding | F-21 | EER 11.0 / IEER 13.5 (p. 89) |
| RTU-4 | 19 gas-connection | pass | | 3/4 in., 250 MBH (p. 22) = P-501 |
| RTU-4 | 20 sound-data | pass | | 82 dBA (p. 24) |
| RTU-5 | 1 bod-model | finding | F-03, F-04 | Lennox LGH360H4E — unnamed manufacturer (p. 4, p. 25) |
| RTU-5 | 2 cooling-capacity | pass | | 363.8/268.0 ≥ 360/265 (p. 26) |
| RTU-5 | 3 heating-input-output | pass | | 500/405 (p. 27) = M-601, P-501 |
| RTU-5 | 4 supply-fan | finding | F-12 | Belt-drive FC blower with VFD (p. 28); CFM/ESP match |
| RTU-5 | 5 compressor-staging | pass | | 4 scroll, 4 stages = multi-stage per 2.2.D (p. 26) |
| RTU-5 | 6 filters | pass | | 4-in. MERV 13 (p. 28) |
| RTU-5 | 7 economizer-min-oa | pass | | Diff. enthalpy, baro relief, 4,800 CFM, DCV input, FDD (p. 28); CO2 sensor by 23 09 00 as specified |
| RTU-5 | 8 electrical-mca-mocp | pass | | 93.4/110 vs 95/110 (p. 29; E-601 ckt 37-41) |
| RTU-5 | 9 operating-weight | pass | | 4,180 ≤ 4,500 on dunnage (p. 29; S-201); > 4,000 lb so dunnage applies, already shown |
| RTU-5 | 10 curb-height | finding | F-11 | 20 in. vs A-511 23 in. (p. 68) |
| RTU-5 | 11 bacnet-points | pass | | Prodigy 2.0 with BACnet module; Table A points provided except filter DI (p. 78, p. 80) — see 12 |
| RTU-5 | 12 dirty-filter-switch | finding | F-13 | Field kit not included (p. 80, p. 85) |
| RTU-5 | 13 smoke-shutdown-terminals | pass | | S1/S2 terminals (p. 76) |
| RTU-5 | 14 scheduled-options | pass | | Note 1 items present (p. 25, p. 85) |
| RTU-5 | 15 warranty | finding | F-15 | Compressors 5 yr standard (pass); labor excluded, start at start-up (p. 91) |
| RTU-5 | 16 dimensions-clearances-footprint | finding | F-17 | 198x92x68, 48 in. clearances, 194x88 curb vs 5/S-501 dunnage (pp. 29, 64, 68) |
| RTU-5 | 17 certifications | finding | F-22 | AHRI yes (p. 88); UL/ANSI not shown |
| RTU-5 | 18 efficiency-energy-code | finding | F-21 | EER 10.6 / IEER 12.4, "meets minimum with MSAV" vs 90.1-2013 (p. 89) — marginal |
| RTU-5 | 19 gas-connection | unverifiable | | 1 in. NPT (p. 27) = P-501 1 in.; furnace inlet pressure range not stated for the LGH — request |
| RTU-5 | 20 sound-data | pass | | 89 dBA (p. 29) |
| RTU-6 | completeness (all 20 checks) | finding | F-02 | Not submitted; no element checks possible |
| package | g.delegated-design | finding | F-01 | Sealed restraint calcs absent (p. 2, p. 69, p. 95) |
| package | g.products-marked | pass | | Per-unit selection printouts (pp. 5–29) and option matrix (p. 85) identify model, options and accessories; generic IOMs are support only |
| package | g.current-documents | finding | F-24 | "IFC set" (p. 95); Addendum 2 incorporation and RFI/ASI log not confirmable from the excerpts |
| package | g.basis-of-design | finding | F-03, F-04 | RTU-5 Lennox; no 01 25 00 substitution request |
| package | g.deviations-identified | finding | F-16 | Transmittal "None" (p. 1) against 13+ deviations |
| package | g.by-others-mapped | finding | F-18, F-19 | Detectors (install is Div 23, not "others"); rigging unassigned; gas regulators → Div 22 (mapped, confirm subcontract); condensate traps → Bayline (mapped); line-voltage wiring → Div 26 (mapped); TAB → 23 05 93 (mapped); CO2/space sensors → 23 09 00 (mapped) |
| package | g.field-verify | finding | F-11 | A-511 "verify insulation thickness with roofing submittal before ordering curbs" — roofing submittal status unknown; GC verifies before curb release |
| package | g.lead-time | finding | F-20 | 14 weeks from release; 2026-10-10 release not achievable; schedule not in excerpts |
| package | rc.m601-e601-electrical | finding | F-10 | RTU-3 only; RTU-1, -2, -4, -5 within schedule and E-601 |
| package | rc.m601-p501-gas | finding | F-08 | RTU-1 350 vs 250 MBH; others match; total would be 1,850 vs 1,800 CFH meter |
| package | rc.s201-weights | finding | F-05 | RTU-4 over; RTU-1, -2, -3, -5 within; RTU-6 not submitted |
| package | rc.a511-curb-heights | finding | F-11 | RTU-5 20 vs 23 in.; RTU-1–4 20 in. correct |
| package | rc.2309-points-list | finding | F-13 | pp. 79–80 vs Table 23 09 00-A: all points provided except filter DP (DFS omitted) |
| package | rc.fa001-m601-detectors | finding | F-18 | p. 87 "by others" vs FA-001 note 12 / M-601 note 5 install by Div 23 |
| package | rc.warranty-1.6 | finding | F-14, F-15 | pp. 90–91 vs 1.6.A–C |
| package | rc.restraint-s001-2305-48 | finding | F-01 | Nothing to reconcile; calcs absent |
| package | pr.1.3.A product data | finding | F-02, F-22 | Submitted for RTU-1–5 (pp. 4–29, 85–89); RTU-6 missing; listings not shown |
| package | pr.1.3.B shop drawings | finding | F-11, F-26 | Dimensions, weights, corner weights, curbs, clearances, duct/gas/electrical connections, wiring, controls submitted (pp. 61–84); curb relationship to A-511 is a generic cross-section (p. 69) and the RTU-5 height is wrong |
| package | pr.1.3.C restraint submittals | finding | F-01 | Not submitted |
| package | pr.1.3.D deviations list | finding | F-16 | "None" |
| package | pr.1.7.A start-up provider | finding | F-27 | Factory authorization of Bayline's service division not shown (p. 94) |

Row count: 100 element rows (5 submitted units × 20 checks) + 1 RTU-6 completeness row + 21 package rows (8 global checks, 8 reconciliations, 4 Part 1 package requirements, 1 start-up provider) = **122 rows**. Status totals: pass 61, finding 60, unverifiable 1, na 0.

## 6. Unverifiable items and confidence floor

Unverifiable from the documents in hand (the resubmittal or the GC must supply):
- Mechanical roof plan (unit locations, service clearances around the 48 in. Lennox envelope and the RTU-3 power-exhaust hood) and Details 4/S-501 and 5/S-501 (support-angle and dunnage layout vs the p. 68 curb footprints) — F-17, F-26.
- Approved roofing (07 54 23) submittal and A-131 tapered layout — needed to confirm the A-511 insulation thicknesses before curb order (F-11).
- RFI, ASI and bulletin logs — whether anything after Addendum 2 affects Division 23 (F-24).
- Project master schedule — true need-by dates for release, steel fabrication and roofing (F-20); routing need-bys are given relative to the sequence.
- Lennox LGH furnace inlet-pressure range (RTU-5 check 19); UL/ANSI listing evidence for all models (F-22); the 0.5 in. w.g. loaded-filter allowance in each fan selection (F-23).
- Whether the Division 22 subcontract carries the line regulators at each unit and whether any subcontract carries crane and rigging (F-19).
- The adopted energy code edition and the adopted mechanical/fuel-gas code edition with county amendments (compliance questions 1–3); nothing was researched or answered from memory.

Knowledge confidence floor: **draft**. The compiled context for 23 74 13 is global Division 01 practice only (no section profile, no Division 23 baseline, no education overlay, zero hooks, zero interfaces, zero reflexes); the section-specific checks, reconciliations, interfaces and compliance questions in this review are derived from the project documents and PE practice and have not been PE-reviewed in the knowledge layer. Disposition is a suggestion; the PE decides and sends.
