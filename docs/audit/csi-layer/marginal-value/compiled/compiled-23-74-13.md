# Compiled knowledge — 23 74 13 Central HVAC Equipment

Facility types: education.k12 · Confidence floor: **draft** · Review mode: per_element · Contractor-designed: never
Lineage: global → 23 → 23 70 00 → [23 74 00 missing] → [23 74 13 missing]
Overlays: education, education.k12

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Indoor air handlers, packaged rooftop and outdoor units, dedicated outdoor air and make-up air units, and air-to-air energy recovery (23 72 00 through 23 76 00 inherit from here), reviewed by tag. Each unit is checked for fan and coil performance with its real internal pressure drops, outdoor air and economizer control with a relief path, energy recovery that does not carry contaminated exhaust back, a condensate trap the pad or curb can fit, and the duct smoke detectors the code requires. Most misses are what the unit needs from others: power, curb, condensate route, control points, detectors.

## Review checks (25)
### completeness
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] edu.agency-approvals** — Where a state school-construction agency has jurisdiction, deferred submittals, substitutions and field changes that touch structure, fire and life safety or accessibility are approved by that agency before fabrication, not only by the architect, and the agency's inspector and testing requirements are in the inspection program.  
  Trace: spec.division_01, register.special_inspections, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.products-marked** — Cut sheets covering a product family have the proposed model, size, options, finish and accessories clearly marked; unmarked sheets are returned.  
  Trace: spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data · _global_
### conformance
- **[high] g.current-documents** — The submittal reflects the current contract documents, including addenda, ASIs, bulletins and responded RFIs, not the bid set. Note the drawing revision the submitter worked from.  
  Trace: drawings.revision_blocks, register.asi_bulletin_log, register.rfi_log · Owner: gc · Scope: package · _global_
- **[high] g.basis-of-design** — Proposed manufacturer and model match the basis of design or a listed acceptable manufacturer. Anything else follows the comparable-product or substitution procedure Division 01 allows, with its timing and comparison data, before it is reviewed on its merits.  
  Trace: spec.part2_manufacturers, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] g.deviations-identified** — Every deviation from the contract documents is clouded or listed by the submitter. Compare independently; do not rely on the submitter's list.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _global_
- **[high] d23.design-conditions** — Capacity and performance are rated at the scheduled design conditions (entering air and water temperatures, outdoor design temperature, altitude, glycol type and concentration, fouling factor, external static pressure), not at the manufacturer's standard rating conditions, and corrected values are shown for every scheduled performance line.  
  Trace: schedule.mechanical_equipment, spec.part2 · Owner: subcontractor · Scope: element · _23_
- **[high] 23ah.fan-static** — The fan is selected for the scheduled external static plus every internal pressure drop the unit actually contains, with filters taken at the loading the spec names, and coil face velocities stay below the moisture carryover limit the spec sets.  
  Trace: schedule.mechanical_equipment, spec.part2 · Owner: subcontractor · Scope: element · _23 70 00_
- **[high] 23ah.economizer-relief** — Units with economizers bring in their full economizer airflow and have a relief path (relief fan, return fan or barometric relief) that keeps the building pressure the design intends; outdoor air is measured where the sequence controls to an airflow; the high-limit control matches the energy code for the climate zone.  
  Trace: schedule.mechanical_equipment, drawings.controls, spec.part3 · Owner: subcontractor · Scope: element · _23 70 00_
- **[high] 23ah.energy-recovery** — Energy recovery meets the scheduled effectiveness at design conditions, its exhaust air transfer suits the class of air being exhausted (contaminated exhaust kept off wheels that can carry it over), fan placement and purge keep leakage toward the exhaust side, and frost control and economizer bypass are included.  
  Trace: schedule.mechanical_equipment, spec.part2 · Owner: subcontractor · Scope: element · _23 70 00_
- **[high] edu.risk-category-delegated** — Delegated designs (cladding and curtain wall, roofing attachment, joists and trusses, nonstructural and equipment anchorage) state the risk category and importance factors they used, and these match the structural general notes; schools are often assigned above the default, and designers who assume the default under-design.  
  Trace: drawings.structural, spec.part1_submittals · Owner: subcontractor · Scope: package · _overlay:education_
- **[high] edu.classroom-acoustics** — Where classroom acoustic criteria apply, HVAC equipment serving or located in learning spaces (unit ventilators, fan coils, terminal units, indoor units, rooftop units over classrooms) submits sound data in the form the criteria are judged by, and acoustical ceilings and wall panels keep the absorption the design relied on. Substitutions are compared on sound performance, not capacity and price alone.  
  Trace: report.acoustical, schedule.mechanical_equipment, spec.part2 · Owner: subcontractor · Scope: element · _overlay:education_
- **[medium] d23.sound-data** — Where the spec or an acoustical report sets sound criteria, the submittal gives octave-band sound power at the scheduled operating point for each path the criteria cover (discharge, inlet, casing radiated, outdoor), not a single A-weighted value, and names any attenuator, enclosure or barrier the result depends on.  
  Trace: report.acoustical, spec.part2, schedule.mechanical_equipment · Owner: subcontractor · Scope: element · _23_
- **[medium] 23ah.filtration** — Filter ratings and banks match the spec at each position (pre-filter, final filter, outdoor air), frames are gasketed so air cannot bypass the media, and filters are reachable from the access side.  
  Trace: spec.part2, schedule.mechanical_equipment · Owner: subcontractor · Scope: element · _23 70 00_
### coordination
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
- **[high] d23.substitution-cascade** — When the unit is not the basis of design, or adds or drops options, list what it changes outside this submittal: electrical data, operating weight and support points, footprint, curb and connection locations, service clearances, sound, refrigerant, controls interface and the values claimed in the energy compliance forms. Each change goes to the trade or designer it affects before approval, with who pays named.  
  Trace: register.substitutions, schedule.mechanical_equipment, report.energy_compliance · Owner: gc · Scope: element · Gate: procurement_release · _23_
- **[high] d23.vfd-motors** — For each variable-speed motor: who furnishes the drive, where it is mounted (on the unit, on a wall, in an electrical room), whether its heat is counted in that room's cooling or ventilation, whether the cable run to the motor needs output filtering, and whether the motor is inverter-rated with the shaft-grounding or bearing protection the spec requires. A drive with a bypass keeps safeties and fire alarm shutdown working in bypass.  
  Trace: schedule.mechanical_equipment, drawings.electrical, spec.part2 · Owner: gc · Scope: element · Gate: procurement_release · _23_
- **[high] 23ah.rooftop-curb** — Rooftop units have a curb or rail of the type and height the spec and roofing require (insulated, isolation, rated for the wind and seismic restraint design), duct openings that match the roof framing, and, on replacements, an adapter for any difference from the existing curb.  
  Trace: drawings.roof_plan, drawings.structural, drawings.details · Owner: subcontractor · Scope: element · Gate: roof_membrane · _23 70 00_
### constructability
- **[high] d23.service-access** — The manufacturer's service clearances (coil and filter pull, tube pull, fan and motor removal, control panel working space, access door swing) fit the room or roof as drawn once the piping, ductwork and electrical gear around the unit are in, and there is a route to deliver and later replace the unit (shipping splits, doors, shafts, crane or roof access).  
  Trace: drawings.enlarged_plans, drawings.mechanical, drawings.plans · Owner: subcontractor · Scope: element · Gate: procurement_release · _23_
- **[high] edu.summer-window** — Where work in existing schools must fit a break in the academic calendar, each submittal's approval, owner selections, mock-ups and delivery are dated against the day the window opens, not against a floating schedule activity. Long-lead items (door frames and hardware, HVAC equipment, switchgear, casework, flooring) that miss the window push work into occupied classrooms or a year later, so their submittals are released first.  
  Trace: schedule.master, spec.division_01 · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[medium] 23ah.condensate-trap** — The condensate trap height the drain pan's pressure needs fits under the unit's pad, curb or base rail height, with heat trace on outdoor traps in freezing climates.  
  Trace: drawings.details, schedule.mechanical_equipment · Owner: subcontractor · Scope: element · Gate: procurement_release · _23 70 00_
- **[medium] 23ah.field-assembly** — Units shipped in sections or knocked down to fit the rigging route are reassembled and sealed under the manufacturer's supervision, and any casing leakage test the spec requires is done after reassembly, not taken from the factory test.  
  Trace: spec.part3, drawings.enlarged_plans · Owner: subcontractor · Scope: element · Gate: final_connection · _23 70 00_
### absence
- **[high] d23.concealed-access** — Every concealed item that needs service, inspection or testing (fire and smoke dampers, terminal units, valves, coils, filters, drain pans, duct detectors, control devices) has an access door or a lay-in ceiling with a clear path to it. Access doors in hard ceilings and walls appear on the reflected ceiling plans, sized for the task.  
  Trace: drawings.rcp, drawings.mechanical · Owner: design_team · Scope: package · Gate: above_ceiling_close_in · _23_

## Reconciliations — documents that must agree (7)
- **[high (reflex)] d23.rc.mech-elec** — Each tag's electrical data in the approved submittal matches its circuit on the panel schedule and the single-line. Recheck after every substitution, alternate and option change (electric heat, drive, factory disconnect, service receptacle, second power connection): the submitted unit's MCA and MOCP govern the conductors and the overcurrent device, not the design-stage schedule.  
  Between: schedule.mechanical_equipment ↔ schedule.electrical_panel ↔ drawings.single_line · Key: Equipment tag · Fields: voltage, phase, MCA, MOCP or breaker size, number of power connections, disconnect and who furnishes it, starter or drive and who furnishes it, emergency or standby source · Owner: design_team · Gate: procurement_release · _23_
- **[high] d23.rc.equipment-presence** — Every scheduled tag appears on the mechanical plans and has a power connection on the electrical plans, and every mechanical item on the electrical plans exists on the mechanical schedule. Small items (exhaust fans, unit heaters, condensate pumps, electric duct heaters) are the usual gaps.  
  Between: schedule.mechanical_equipment ↔ drawings.mechanical ↔ drawings.electrical · Key: Equipment tag · Fields: tag shown, location, quantity · Owner: design_team · Gate: procurement_release · _23_
- **[high] d23.rc.structural-loads** — The submitted unit's operating weight and support arrangement are within what the structural drawings carry at its location. A heavier unit, a moved unit or a new point load on a roof or elevated slab goes to the structural engineer before release.  
  Between: schedule.mechanical_equipment ↔ drawings.structural ↔ drawings.roof_plan · Key: Equipment tag and location · Fields: operating weight, support points or curb footprint, location on the framing, dunnage or support steel · Owner: design_team · Gate: procurement_release · _23_
- **[high] d23.rc.intake-separation** — The unit's outdoor air intake keeps the required separation from every exhaust or relief outlet, plumbing vent, flue, cooling tower and vehicle area on any discipline's roof plan or elevations, and its own exhaust, relief or flue keeps it from every intake, including outlets added by substitutions and later bulletins.  
  Between: drawings.mechanical ↔ drawings.roof_plan ↔ drawings.plumbing ↔ drawings.exterior_elevations · Key: Each outdoor air intake, and each exhaust, relief or flue outlet, of the unit · Fields: distance to exhaust and relief outlets, plumbing vents, flues and generator exhaust, cooling towers, loading docks and drives, relative height · Owner: design_team · Gate: roof_membrane · _23_
- **[high] d23.rc.energy-compliance** — The submitted unit carries the efficiency, economizer, energy recovery and fan power that the energy compliance documents claimed for its tag. A substitution that drops one fails the energy inspection even when it meets the spec.  
  Between: schedule.mechanical_equipment ↔ report.energy_compliance · Key: Equipment tag · Fields: efficiency metric and value, economizer, energy recovery, fan power or motor efficiency, control features the compliance path credits · Owner: design_team · Gate: procurement_release · _23_
- **[high] 23ah.rc.duct-detectors** — Every unit whose airflow or configuration triggers duct smoke detection under the adopted code shows its detectors on the fire alarm drawings at the locations the mechanical drawings provide, with the shutdown it causes; units serving areas fully covered by area detection are checked against the exception the design relies on.  
  Between: schedule.mechanical_equipment ↔ drawings.fire_alarm ↔ drawings.mechanical · Key: Air-handling unit tag · Fields: design supply airflow, supply or return detector required, detector shown on fire alarm drawings, duct location, shutdown action · Owner: design_team · Gate: procurement_release · _23 70 00_
- **[medium] 23ah.rc.condensate** — Each unit's condensate reaches a receptor shown on the plumbing drawings, or a roof discharge point the plumbing code allows, and indoor units over finished spaces or electrical rooms have a secondary pan or an overflow switch that stops the unit.  
  Between: schedule.mechanical_equipment ↔ drawings.mechanical ↔ drawings.plumbing ↔ drawings.roof_plan · Key: Each unit with a cooling coil, humidifier or condensing heat exchanger · Fields: drain connection, route, receptor or roof discharge point, secondary pan or overflow switch, heat trace · Owner: design_team · Gate: overhead_rough_in · _23 70 00_

## Compliance — regulatory hooks (14)
- **[high] d23.rh.equipment-efficiency** (`hvac-equipment-efficiency`) — Which energy code edition and compliance path govern, what minimum full-load and part-load efficiency applies to this equipment type and capacity, and is the submitted rating stated in the same metric and under the same rating standard that the code edition uses?  
  **Unbound** → Run /construction:code-researcher with research topic "hvac-equipment-efficiency" (seed it with this hook's question)
- **[high] d23.rh.intake-separation** (`outdoor-air-intake-separation`) — What separation and height does the adopted mechanical code require between outdoor air intakes and exhaust outlets, plumbing vents, flues, cooling towers, streets, parking and loading areas, and does it vary by the class of exhaust?  
  **Unbound** → Run /construction:code-researcher with research topic "outdoor-air-intake-separation" (seed it with this hook's question)
- **[high] d23.rh.seismic-certification** (`seismic-equipment-certification`) — For this project's seismic design category, which mechanical equipment needs anchorage designed for seismic forces, and which components are designated seismic systems that need the manufacturer's certification that they remain operable after the design earthquake?  
  **Unbound** → Run /construction:code-researcher with research topic "seismic-equipment-certification" (seed it with this hook's question)
- **[high] 23ah.rh.duct-detectors** (`duct-smoke-detector-requirements`) — Which air-distribution systems require duct smoke detectors under the adopted mechanical code (supply or return, by system airflow, return systems serving more than one story), what exceptions apply where area smoke detection covers the space, and what must the detectors shut down?  
  **Unbound** → Run /construction:code-researcher with research topic "duct-smoke-detector-requirements" (seed it with this hook's question)
- **[high] 23ah.rh.economizer** (`hvac-economizer-requirements`) — Does the adopted energy code require an air or water economizer for this unit's cooling capacity and climate zone, which high-limit controls are allowed, and are fault detection and diagnostics required?  
  **Unbound** → Run /construction:code-researcher with research topic "hvac-economizer-requirements" (seed it with this hook's question)
- **[high] 23ah.rh.energy-recovery** (`energy-recovery-requirements`) — Does the adopted energy code require exhaust air energy recovery for this unit's outdoor air fraction, airflow, operating hours and climate zone, and what effectiveness must it reach?  
  **Unbound** → Run /construction:code-researcher with research topic "energy-recovery-requirements" (seed it with this hook's question)
- **[high] 23ah.rh.refrigerant** (`refrigerant-safety-requirements`) — For packaged units with A2L or other flammable refrigerants, what do the adopted mechanical code and the unit's listing require (factory refrigerant detection and mitigation, minimum airflow on a leak, sealing of duct and openings, minimum conditioned area served)?  
  **Unbound** → Run /construction:code-researcher with research topic "refrigerant-safety-requirements" (seed it with this hook's question)
- **[high] 23ah.rh.refrigerant-gwp** (`refrigerant-gwp-restrictions`) — Which refrigerants may the packaged and split DX units on this project use under federal and state high-GWP restrictions, given each unit's manufacture and installation dates?  
  **Unbound** → Run /construction:code-researcher with research topic "refrigerant-gwp-restrictions" (seed it with this hook's question)
- **[high] edu.rh.school-agency-review** (`school-construction-agency-review`) — Does a state agency other than the local building department review plans, approve changes or inspect construction for this school (common for public K-12 and in some states for community colleges), and what does it require for deferred submittals, change documents, testing laboratories and the inspector of record?  
  **Unbound** → Run /construction:code-researcher with research topic "school-construction-agency-review" (seed it with this hook's question)
- **[high] edu.rh.risk-category** (`building-risk-category-assignment`) — What risk category applies to this building under the adopted code (occupant load, designation as an emergency or community shelter), and which design loads, nonstructural anchorage and special inspections change because of it?  
  **Unbound** → Run /construction:code-researcher with research topic "building-risk-category-assignment" (seed it with this hook's question)
- **[medium] d23.rh.equipment-access** (`mechanical-equipment-access-clearance`) — What access, passageway, service clearance, platforms, lighting and service receptacle does the adopted mechanical code require for this equipment in its location (roof, attic, above a ceiling, mechanical room), and does the layout provide it?  
  **Unbound** → Run /construction:code-researcher with research topic "mechanical-equipment-access-clearance" (seed it with this hook's question)
- **[medium] d23.rh.drive-working-space** (`electrical-working-space`) — What electrical working space does the adopted electrical code require in front of this equipment's drives, control panels and disconnects, and is that space kept clear of the piping, ductwork and equipment around them?  
  **Unbound** → Run /construction:code-researcher with research topic "electrical-working-space" (seed it with this hook's question)
- **[medium] 23ah.rh.filtration** (`hvac-filtration-requirements`) — What minimum filtration does the adopted mechanical code or ventilation standard require upstream of coils and on outdoor air, and does the local outdoor air quality trigger more?  
  **Unbound** → Run /construction:code-researcher with research topic "hvac-filtration-requirements" (seed it with this hook's question)
- **[medium] edu.rh.classroom-acoustics** (`classroom-acoustics-criteria`) — Does the state, the owner's standards or a green-building program the project pursues require classroom acoustic performance (ASA/ANSI S12.60 Part 1 or an equivalent), which edition, and must background noise and reverberation be verified in the field?  
  **Unbound** → Run /construction:code-researcher with research topic "classroom-acoustics-criteria" (seed it with this hook's question)

## Coordination routing (14)
- **[high] if.03-housekeeping-pads** → Cast-in-place concrete (03 30 00) · Gate: slab_pour — Dowels go in with the slab; the pad waits for the approved equipment submittal
  - Send them: Approved footprint, weight, anchor pattern and anchorage design, pad height for traps and drains, and pad locations checked against service clearances, before the pad pour
  - Need from them: Pads formed and doweled to the slab to the approved equipment dimensions, with the anchor embedment and edge distance the anchorage needs
  - Confirm who: Pad dimensions and locations — typical furnish the equipment's trade / install 03 30 00
  - Confirm who: Equipment anchors into pads — typical furnish the equipment's trade / install the equipment's trade or 03 30 00
  - If missed: Pads formed from the scheduled equipment before the equipment submittal was approved; Conduit stub-ups cast from the design drawings, then another manufacturer's switchboard is approved
- **[high] if.05-equipment-support-steel** → Structural framing and metal fabrications (05 12 00, 05 21 00, 05 50 00) · Gate: procurement_release
  - Send them: Approved equipment weights, footprints, support points, isolation rails or bases, and which frames and supports each trade furnishes
  - Need from them: Support framing and dunnage as scheduled, and the engineer of record's acceptance of each equipment load and support point
  - Confirm who: Support steel and dunnage for floor-, roof- and platform-mounted equipment — typical furnish 05 50 00 or the equipment trade / install 05 50 00 or the equipment trade
  - If missed: Heavier or relocated equipment approved after the joists were designed and fabricated; Support steel shown on MEP drawings as "by others" or "by GC" and carried by no contract
- **[high] if.06-truss-mep-loads** → Shop-fabricated wood trusses (06 17 53) · Gate: procurement_release — Release truss designs after the equipment submittals they carry are approved
  - Send them: Equipment operating weights and locations, platforms and hangers, duct and sprinkler mains routed through or hung from the trusses, and attic access needs
  - Need from them: Truss layout, depth and web openings, and the concentrated and hanging loads each design carries
  - If missed: Trusses designed for uniform loads only; a rooftop unit, solar array or sprinkler main added later
- **[high] if.roof-equipment-curbs** → Roofing and roof accessories (07 50 00, 07 72 00) · Gate: roof_membrane
  - Send them: Equipment curb dimensions and weights, framing at deck openings, dunnage, and the setting schedule
  - Need from them: Curb and support heights and flashing details compatible with the roof assembly
  - Confirm who: Equipment curbs and supports — typical furnish 23 74 00 or 07 72 00 / install 06 10 53 (GC carpentry) or 23 74 00
  - Confirm who: Flashing curbs and supports into the membrane — typical install 07 50 00
  - If missed: Curbs furnished by nobody, or set after the membrane and flashed in as patches
- **[high] if.08-louvers-ductwork** → Louvers (08 91 00) · Gate: procurement_release
  - Send them: Airflow and function (intake, exhaust or relief) per louver mark, connection size and location, a plenum sloped and drained to the exterior or to a drain, and the motorized or backdraft dampers behind the louver
  - Need from them: Louver size and free area, certified water penetration and pressure drop at the free-area velocity the scheduled airflow produces, sill or drain pan, blank-off panel layout, and the frame the duct or plenum attaches to
  - Confirm who: Insulated blank-off panels on unused louver area — typical furnish 08 91 00 or 23 33 00 / install 08 91 00 or 23 31 00
  - Confirm who: Plenum or duct connection to the louver and its drain — typical furnish 23 31 00 / install 23 31 00
  - If missed: Unused louver area left open behind the face because neither the louver nor the duct trade provided blank-offs
- **[high] if.11-foodservice-gas-exhaust** → Food cooking, dishwashing and hood equipment (often specified in 11 40 00) (11 44 00, 11 48 00) · Gate: procurement_release
  - Send them: Gas piping and shutoff valve to each appliance; grease and exhaust duct to the hood collars; fans and make-up air sized to the approved hoods, with interlocks
  - Need from them: Gas input, connection size and pressure per appliance; hood airflow, static pressure and collar locations; hood control panel functions
  - Confirm who: Kitchen hoods — typical furnish 11 40 00 or 23 38 13 / install 11 40 00 or 23 38 13
  - Confirm who: Final gas connection to each appliance (flexible connector, restraint, quick-disconnect) — typical furnish 11 40 00 / install 23 11 23
  - Confirm who: Hood control panel and its interlock wiring to fans and make-up air — typical furnish 11 40 00 / install Division 26 / connect 23 09 00 or Division 26
  - If missed: Hoods bought twice or not at all because both the equipment and mechanical sections specify them
- **[high] if.13-metal-building-hung-loads** → Metal building systems (13 34 19) · Gate: procurement_release — Hung loads have to reach the manufacturer before its design is sealed
  - Send them: Weights and hanging locations of mains, ducts, unit heaters, lights and rooftop units, before the metal building design is final
  - Need from them: Collateral and auxiliary loads designed for, allowable hanging points and attachment methods on purlins and frames, and framed openings and supports for rooftop units
  - If missed: Sprinkler mains, unit heaters or rooftop units added or relocated beyond the collateral load, or hung from purlins without the manufacturer's acceptance
- **[high] if.23-equipment-power** → Equipment wiring connections, panelboards, motor control centers, disconnects, motor controllers and drives (26 05 83, 26 24 16, 26 24 19, 26 28 16, 26 29 13, 26 29 23) · Gate: procurement_release — Repeat the exchange after every substitution, alternate or option change, before the electrical gear is released
  - Send them: Electrical data per tag from the approved submittal (voltage, phase, MCA, MOCP, number of connections), which disconnects, starters and drives come factory-mounted, and every change after a substitution or option change
  - Need from them: Circuit, overcurrent device, conductors, disconnect and starter or drive per tag sized to the approved data, emergency or standby power where scheduled, and the service receptacle and lighting at rooftop and attic equipment
  - Confirm who: Variable-frequency drives — typical furnish 23 (with the equipment) or 26 29 23 / install 26 or 23 for unit-mounted drives / connect 26
  - Confirm who: Disconnect switches at equipment — typical furnish 26 28 16 or 23 (factory-mounted) / install 26
  - Confirm who: Motor starters for equipment without factory controls — typical furnish 26 29 13, 26 24 19 or 23 / install 26
  - If missed: Equipment arrives with electrical data the circuits were not built for; breakers, wire and disconnects changed at startup
- **[high] if.23-duct-smoke-detectors** → Fire detection and alarm (28 46 00) · Gate: above_ceiling_close_in — Housings go in with the duct; the detector list has to be agreed when the fire alarm shop drawings are prepared
  - Send them: Units and dampers that need duct detection, duct locations with the straight run and orientation the detector listing requires, and access doors at each detector
  - Need from them: Detectors, housings and sampling tubes, remote test and indicator stations, wiring and programming of the shutdown
  - Confirm who: Duct detector housings and sampling tubes — typical furnish 28 46 00 / install 23 31 00 or 28 46 00
  - Confirm who: Remote test and indicator stations — typical furnish 28 46 00 / install 28 46 00
  - If missed: Duct detectors furnished with the air handlers, but nobody carries mounting, wiring or the remote test station
- **[high] if.23-gas-service** → Gas service piping and the utility meter set (33 52 16) · Gate: procurement_release — Get the utility's delivery pressure in writing before gas-fired equipment and regulators are released
  - Send them: Connected load and the inlet pressure each appliance needs at full fire, the building piping design pressure, and the meter and regulator location the building layout wants
  - Need from them: The utility's committed delivery pressure, meter and service regulator location and clearances, service line route and size, and the point where the utility's scope ends
  - Confirm who: Service line, meter and service regulator — typical furnish gas utility or 33 52 16 / install gas utility or 33 52 16
  - Confirm who: Piping from the meter outlet to the appliances, with line regulators where the building runs at elevated pressure — typical furnish 23 11 23 / install 23 11 23
  - If missed: Appliance's minimum inlet pressure not available at full fire; The utility delivers a lower pressure than the building gas piping was sized for; Meter set location does not meet the clearances to openings or air intakes
- **[medium] if.01-permanent-hvac-construction-use** → Temporary facilities (use of permanent systems) (01 50 00) · Gate: final_connection — Agree warranty start and filtration before the equipment is started for construction use
  - Send them: Manufacturer start-up before use, filter media, and the warranty terms that apply to construction use and how they are extended
  - Need from them: Which equipment will run during construction, from when, with temporary filtration, protection and cleaning before turnover
  - If missed: Permanent air handlers run during drywall sanding and floor preparation with no return filtration; Equipment warranties start at start-up or shipment while the equipment runs for construction
- **[medium] if.22-vent-intake-separation** → Plumbing vents and laboratory or medical vacuum exhausts (22 13 00, 22 60 00) · Gate: roof_membrane — Roof penetrations are fixed before the membrane; moving a vent afterward means new flashing
  - Send them: Outdoor air intake locations and heights, and any unit moved or added on the roof after the plumbing roof layout was set
  - Need from them: Vent terminal and vacuum exhaust locations and heights on the roof and walls
  - If missed: A plumbing vent stack terminated beside a rooftop unit's outside air hood, under an operable window or on an occupied roof; Vacuum or anesthetic gas exhaust terminated near the medical air intake or an air handler intake
- **[medium] if.22-hvac-drains** → Sanitary drainage (22 13 00) · Gate: underslab_rough_in
  - Send them: Condensate, blowdown, relief valve and drain discharges with their location, flow and temperature, and the drain piping to the receptor
  - Need from them: Receptors (floor sinks, funnel and hub drains) sized and placed for each equipment discharge, and neutralization where condensate is acidic
  - Confirm who: Drain piping from HVAC equipment to the receptor — typical install Division 23
  - Confirm who: Receptors at HVAC equipment — typical furnish 22 13 00 / install 22 13 00
  - If missed: Equipment set with condensate or relief piped to nothing, or a floor sink under an equipment frame where it cannot be seen or cleaned
- **[medium] if.23-packaged-controls** → HVAC controls (23 09 00) · Gate: procurement_release — The interface card is ordered with the equipment
  - Send them: Factory controller, network interface and the points it exposes
  - Need from them: Points mapped into the automation system, the split of the sequence between factory controller and automation system, and who programs each part
  - Confirm who: Protocol interface card or gateway — typical furnish the equipment section or 23 09 00
  - If missed: Packaged equipment arrives without the interface the automation system needs; gateways added late, sequences split ad hoc

## Failure modes to watch (26)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d23.fm.substitution-electrical** — A substituted or re-optioned unit is approved with a different voltage, MCA or MOCP, and the electrical work is built to the original schedule → Breakers, conductors or disconnects replaced at startup; delay and a dispute over who pays (caught by d23.rc.mech-elec, d23.substitution-cascade; industry_practice)
- **d23.fm.missing-circuit** — An exhaust fan, unit heater, condensate pump or duct heater on the mechanical plans has no circuit on the electrical drawings → Circuits added by change order after rough-in and ceilings (caught by d23.rc.equipment-presence; industry_practice)
- **d23.fm.standard-conditions** — Equipment selected at standard rating conditions instead of the scheduled design conditions (altitude, glycol, outdoor design temperature, fouling) → Capacity shortfall found at balancing or in the first peak season (caught by d23.design-conditions; industry_practice)
- **d23.fm.heavier-unit** — A substituted unit is heavier or has a different footprint than the one the structure, curb or pad was designed for → Structural reinforcement, curb adapters or new pads after the fact (caught by d23.rc.structural-loads, d23.substitution-cascade; industry_practice)
- **d23.fm.blocked-service** — The unit fits its space, but piping, conduit or walls installed around it block coil pull, filter access or panel working space → Rework of surrounding systems, or equipment that cannot be maintained or replaced without demolition (caught by d23.service-access; industry_practice)
- **d23.fm.no-access-door** — A terminal unit, damper or valve sits above a hard ceiling with no access door, or the door is too small to reach it → Access doors cut into finished ceilings; dampers that fail their acceptance or periodic test (caught by d23.concealed-access; industry_practice)
- **d23.fm.drive-heat** — Drives mounted in a small mechanical or electrical room without counting their heat → Drives trip on over-temperature in summer; room cooling added late (caught by d23.vfd-motors; industry_practice)
- **d23.fm.energy-compliance-lost** — A substitution meets the spec but drops the efficiency, economizer or energy recovery the energy compliance path relied on → Failed energy inspection; revised compliance documents or replaced equipment (caught by d23.rc.energy-compliance, d23.substitution-cascade; industry_practice)
- **d23.fm.re-entrainment** — An exhaust fan, plumbing vent or flue ends up beside an intake, often added late by another discipline or a substitution → Odors and fumes drawn into the building; intake or vent relocated through finished roofing (caught by d23.rc.intake-separation; industry_practice)
- **23ah.fm.detectors-missing** — Duct detectors left off the fire alarm drawings for a unit above the code threshold, or furnished but never installed in the duct → Fire alarm acceptance test failed; detectors, housings and access added above finished ceilings (caught by 23ah.rc.duct-detectors, if.23-duct-smoke-detectors; industry_practice)
- **23ah.fm.static-underestimated** — Fan selected on external static alone, or with clean-filter pressure drop → Airflow falls short as filters load; motor and drive changes after balancing (caught by 23ah.fan-static; industry_practice)
- **23ah.fm.no-relief** — Economizer added or enlarged without a relief path → Building over-pressurized in economizer mode; doors that will not close and whistling openings (caught by 23ah.economizer-relief; industry_practice)
- **23ah.fm.cross-contamination** — Energy recovery wheel handling contaminated or odorous exhaust, or fans arranged so leakage runs toward the supply side → Odors or contaminants returned to occupied spaces; recovery device bypassed or replaced (caught by 23ah.energy-recovery; industry_practice)
- **23ah.fm.trap-too-tall** — The trap the drain pan needs is taller than the pad or curb allows → Drain pans overflow into the unit or the roof; units raised or condensate pumps added (caught by 23ah.condensate-trap; industry_practice)
- **23ah.fm.filter-bypass** — Filters installed in ungasketed racks or the wrong size for the frame → Dirty coils and ducts, lost capacity, and an indoor air quality complaint (caught by 23ah.filtration; industry_practice)
- **23ah.fm.leaky-reassembly** — A unit knocked down for rigging is reassembled by the installer without the manufacturer → Casing leaks, wet insulation at the coil section and voided factory warranty (caught by 23ah.field-assembly; industry_practice)
- **23ah.fm.curb-mismatch** — Substituted or replacement unit's footprint and duct openings differ from the curb and roof framing → Curb adapters, reframed openings and roof patches under schedule pressure (caught by 23ah.rooftop-curb; industry_practice)
- **23ah.fm.condensate-no-receptor** — Air handler condensate dumped on the roof or run to a receptor the plumbing drawings never show → Ponding and algae at roof drains, or receptors added after floors are finished (caught by 23ah.rc.condensate; industry_practice)
- **edu.fm.missed-window** — Hardware, HVAC equipment or casework approved late and delivered after the summer window closes → Work moves into occupied classrooms after hours with temporary systems, or the phase slips a full year (caught by edu.summer-window; field_experience)
- **edu.fm.agency-change-unapproved** — A substitution or field change accepted by the architect is never submitted to the state school-construction agency → The agency withholds certification or closeout of the project; work is reopened or occupancy delayed (caught by edu.agency-approvals; industry_practice)
- **edu.fm.default-risk-category** — Delegated cladding, joist or anchorage design done to the default risk category on a school assigned a higher one → Components under-designed; recalculation and field reinforcement after installation (caught by edu.risk-category-delegated; industry_practice)
- **edu.fm.noisy-classroom-units** — In-room HVAC units or ceilings substituted on capacity and price, with sound data never compared → Classrooms exceed background-noise or reverberation criteria; silencers, unit relocation or ceiling replacement after occupancy (caught by edu.classroom-acoustics; field_experience)

## Expected submittal contents
- **Product Data**
  - Per tag, fan selection with external static and each internal pressure drop listed (filters at the spec's loading, coils, energy recovery, dampers, attenuators)
  - Coil performance at the scheduled entering conditions, with face velocity, rows and fin spacing
  - Outdoor air, economizer and relief arrangement, airflow measurement, and filter ratings by bank
  - Energy recovery effectiveness at the design conditions, exhaust air transfer, frost control and bypass
  - Casing construction, section dimensions and weights for rigging, and curb or base details
  - Condensate trap height for the drain pan's pressure, and factory refrigerant detection where the refrigerant requires it

## Extract for reconciliation
- d23.xf.electrical — Voltage, phase, MCA and MOCP for each power connection (string, per element) → schedule.electrical_panel, drawings.single_line
- d23.xf.operating-weight — Operating weight (number, lb, per element) → drawings.structural
- d23.xf.capacity — Rated capacity and the conditions it is rated at (string, per element) → schedule.mechanical_equipment
- d23.xf.efficiency — Efficiency metric and value (string, per element) → report.energy_compliance
- 23ah.xf.refrigerant — Refrigerant and charge per circuit, and factory leak detection where fitted (string, per element) → schedule.mechanical_equipment

## Standards to verify against
- AHRI Directory of Certified Product Performance: Certified performance ratings for HVAC equipment
- AHRI 340/360 / AHRI 1340: Performance Rating of Commercial and Industrial Unitary Air-conditioning and Heat Pump Equipment — AHRI 1340 introduces new full- and part-load metrics for federal ratings; confirm which standard and metric the adopted energy code edition uses
- AHRI 1350: Mechanical Performance Rating of Central Station Air-handling Unit Casings
- AHRI 1060: Performance Rating of Air-to-Air Exchangers for Energy Recovery Ventilation Equipment
- ANSI/ASHRAE 52.2: Method of Testing General Ventilation Air-Cleaning Devices for Removal Efficiency by Particle Size
- ANSI/ASHRAE 62.1: Ventilation and Acceptable Indoor Air Quality

## Warnings
- No profile for 23 74 13; compiled from ancestors only
- Draft knowledge in use (global, 23, 23 70 00) — not yet PE-reviewed
