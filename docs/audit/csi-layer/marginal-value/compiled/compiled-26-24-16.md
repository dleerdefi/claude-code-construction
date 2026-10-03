# Compiled knowledge — 26 24 16 Switchboards and Panelboards

Facility types: education.k12 · Confidence floor: **draft** · Review mode: per_element · Contractor-designed: never
Lineage: global → 26 → 26 20 00 → 26 24 00 → [26 24 16 missing]
Overlays: education, education.k12

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Switchboards, panelboards and motor-control centers (26 24 13 through 26 24 19 inherit from here), reviewed one tagged assembly at a time against its panel schedule and the single-line. Fault ratings, the study, utility requirements and room fit are inherited from 26 20 00; here the review is the content of each board (mains, devices, spares, options, lugs) and what the board demands of the wall it is set in.

## Review checks (29)
### completeness
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] edu.agency-approvals** — Where a state school-construction agency has jurisdiction, deferred submittals, substitutions and field changes that touch structure, fire and life safety or accessibility are approved by that agency before fabrication, not only by the architect, and the agency's inspector and testing requirements are in the inspection program.  
  Trace: spec.division_01, register.special_inspections, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.products-marked** — Cut sheets covering a product family have the proposed model, size, options, finish and accessories clearly marked; unmarked sheets are returned.  
  Trace: spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data · _global_
- **[medium] 26ds.gfp-testing** — Ground-fault protection of equipment, where provided, is set to the study's values and performance-tested in place before energization, with the test record kept at the equipment.  
  Trace: spec.part3 · Owner: subcontractor · Scope: element · Gate: energization · _26 20 00_
### conformance
- **[critical (reflex)] 26ds.sccr-vs-fault** — Each assembly's short-circuit current rating and each device's interrupting rating meets the available fault current at its line terminals from the study or the utility's data; series ratings are used only as listed combinations and only where the code permits them. The comparison is redone whenever the utility transformer, the service size or a building transformer's impedance changes.  
  Trace: drawings.single_line, report.utility_requirements · Owner: subcontractor · Scope: element · Gate: procurement_release · _26 20 00_
- **[high] g.current-documents** — The submittal reflects the current contract documents, including addenda, ASIs, bulletins and responded RFIs, not the bid set. Note the drawing revision the submitter worked from.  
  Trace: drawings.revision_blocks, register.asi_bulletin_log, register.rfi_log · Owner: gc · Scope: package · _global_
- **[high] g.basis-of-design** — Proposed manufacturer and model match the basis of design or a listed acceptable manufacturer. Anything else follows the comparable-product or substitution procedure Division 01 allows, with its timing and comparison data, before it is reviewed on its merits.  
  Trace: spec.part2_manufacturers, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] g.deviations-identified** — Every deviation from the contract documents is clouded or listed by the submitter. Compare independently; do not rely on the submitter's list.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _global_
- **[high] d26.emergency-separation** — Emergency system wiring, panels and transfer equipment are kept independent of all other wiring, and essential electrical system branches from each other where the facility has them; legally required and optional standby loads are separated wherever the code, the spec or the load classification requires it (the model code lets some share raceways and panels). Emergency raceways and boxes carry the identification the spec calls for.  
  Trace: drawings.single_line, schedule.electrical_panel, spec.part3 · Owner: subcontractor · Scope: package · _26_
- **[high] 26ds.grounding-neutral** — The neutral is bonded to ground only at the service and at each separately derived system; downstream panelboards have isolated neutrals; transformer secondaries have their system bonding jumper and grounding electrode conductor shown.  
  Trace: drawings.single_line, drawings.details · Owner: subcontractor · Scope: element · _26 20 00_
- **[high] 26pb.schedule-match** — The board's voltage, bus rating, main type and rating, feed-through or sub-feed lugs, and every device (poles, trip and type: GFCI, AFCI, shunt trip, lock-on for circuits that must not be switched off) match its panel schedule as revised by ASIs.  
  Trace: schedule.electrical_panel, register.asi_bulletin_log · Owner: subcontractor · Scope: element · Gate: procurement_release · _26 24 00_
- **[high] edu.risk-category-delegated** — Delegated designs (cladding and curtain wall, roofing attachment, joists and trusses, nonstructural and equipment anchorage) state the risk category and importance factors they used, and these match the structural general notes; schools are often assigned above the default, and designers who assume the default under-design.  
  Trace: drawings.structural, spec.part1_submittals · Owner: subcontractor · Scope: package · _overlay:education_
- **[medium] d26.ratings-for-location** — Enclosures, luminaires and devices carry ratings for where they go: wet, damp or washdown locations, corrosive areas, classified (hazardous) locations, air-handling spaces, and outdoor exposure.  
  Trace: spec.part2, drawings.electrical, drawings.plans · Owner: subcontractor · Scope: package · _26_
- **[medium] 26ds.transformers** — Transformers match the single-line voltages, winding configuration and impedance (which drives downstream fault current), carry the harmonic rating specified for nonlinear loads, suit the sound sensitivity of adjacent rooms, and their losses are within what the room's ventilation was sized for.  
  Trace: drawings.single_line, drawings.mechanical, spec.part2 · Owner: subcontractor · Scope: package · _26 20 00_
- **[medium] 26pb.spares** — Spare devices, spaces and bus capacity are what the spec and schedule require, counted after circuits added by ASIs and change orders, not against the bid-set schedule.  
  Trace: schedule.electrical_panel, spec.part2 · Owner: subcontractor · Scope: element · _26 24 00_
### coordination
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
- **[high] 26ds.utility-requirements** — The serving utility's written requirements are in hand and the service equipment follows them: metering and current-transformer compartments, meter types and locations, transformer pad and clearances, service conductors, and who furnishes and installs each piece.  
  Trace: report.utility_requirements, drawings.site, drawings.single_line · Owner: gc · Scope: package · Gate: procurement_release · _26 20 00_
- **[high] 26ds.dedicated-space** — Piping, ductwork and sprinkler lines foreign to the electrical installation stay out of the dedicated space above switchboards and panelboards on the coordination drawings, including drains and sprinkler branches serving the electrical room itself.  
  Trace: drawings.mechanical, drawings.plumbing, drawings.fire_protection, drawings.enlarged_plans · Owner: gc · Scope: element · Gate: overhead_rough_in · _26 20 00_
- **[high] edu.central-plant** — Connections to a campus or district central plant or distribution network (steam and condensate, heating and chilled water, campus power and telecom) follow the owner's utility standards for valves, metering, materials and points, are reviewed by the owner's utility group, and are scheduled through its outage process, which can limit tie-ins to academic breaks.  
  Trace: drawings.site, drawings.mechanical, spec.division_01 · Owner: gc · Scope: element · _overlay:education_
- **[medium] 26ds.disconnect-furnish** — For each motor and equipment connection, who furnishes the disconnect, starter or variable-frequency drive (factory-mounted by the equipment manufacturer or field-installed by electrical) is stated once. Items furnished twice, or by nobody, are scope gaps.  
  Trace: schedule.mechanical_equipment, spec.part1, drawings.electrical · Owner: gc · Scope: package · Gate: procurement_release · _26 20 00_
### constructability
- **[critical] 26ds.study-before-release** — The short-circuit and coordination study, run on the submitted equipment, is accepted before distribution equipment is released, and the breaker types, frames and trip units it needs for selectivity are in the released equipment.  
  Trace: spec.part1_submittals, drawings.single_line · Owner: gc · Scope: package · Gate: procurement_release · _26 20 00_
- **[high] 26ds.fits-room-and-path** — The submitted footprint, with working space in front and dedicated space above, fits the electrical room as drawn; shipping sections and transformers fit the delivery path (doors, corridors, elevators, areaways), and that path is held open until they are set.  
  Trace: drawings.enlarged_plans, drawings.electrical, drawings.plans · Owner: gc · Scope: element · Gate: procurement_release · _26 20 00_
- **[high] 26ds.stub-ups** — Conduit stub-ups and housekeeping pads under floor-standing equipment are laid out from the approved submittal's footprint and conduit entry areas, not from the design drawings.  
  Trace: drawings.enlarged_plans, drawings.details · Owner: gc · Scope: element · Gate: slab_pour · _26 20 00_
- **[high] edu.summer-window** — Where work in existing schools must fit a break in the academic calendar, each submittal's approval, owner selections, mock-ups and delivery are dated against the day the window opens, not against a floating schedule activity. Long-lead items (door frames and hardware, HVAC equipment, switchgear, casework, flooring) that miss the window push work into occupied classrooms or a year later, so their submittals are released first.  
  Trace: schedule.master, spec.division_01 · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[medium] 26pb.lugs-and-gutters** — Lug sizes and quantities fit the feeder conductors as designed or as substituted (aluminum, parallel sets), and gutter space allows the bending those conductors need.  
  Trace: drawings.single_line, spec.part2 · Owner: subcontractor · Scope: element · _26 24 00_
- **[medium] 26pb.wall-mounting** — Recessed panelboards fit the wall depth shown, are not recessed into rated walls without a listed protection method or a rated box-out detail, and are not set back to back in acoustic walls; surface panels in finished spaces are accepted by the architect.  
  Trace: schedule.partition_type, drawings.enlarged_plans, drawings.electrical · Owner: gc · Scope: element · Gate: in_wall_rough_in · _26 24 00_
### absence
- **[high] 26ds.equipment-connections** — Every item needing power on the mechanical, plumbing, fire protection, conveying, foodservice and owner equipment schedules has a circuit, disconnecting means and connection point on the electrical drawings, and every electrical connection still serves equipment that exists in the current design (ASIs and owner changes included).  
  Trace: schedule.mechanical_equipment, schedule.plumbing_fixture, schedule.equipment, drawings.electrical, schedule.electrical_panel, register.asi_bulletin_log · Owner: design_team · Scope: package · Gate: procurement_release · _26 20 00_

## Reconciliations — documents that must agree (3)
- **[high] 26ds.rc.equipment-nameplate** — Before panelboards and switchboards are released, every circuit that serves another division's equipment (mechanical, plumbing, foodservice, conveying, owner equipment) is checked against that equipment's approved submittal rather than its design-stage schedule line, and circuits whose equipment is not yet approved are listed as release risks.  
  Between: schedule.mechanical_equipment ↔ schedule.plumbing_fixture ↔ schedule.equipment ↔ schedule.electrical_panel · Key: Equipment tag · Fields: voltage, phase, MCA or FLA, MOCP or fuse size, conductor size, disconnect type and furnished-by, normal or standby source · Owner: gc · Gate: procurement_release · _26 20 00_
- **[high] 26ds.rc.single-line** — Every switchboard, panelboard and transformer on the single-line matches its panel schedule and the submitted nameplate data, including what feeds it and from which source.  
  Between: drawings.single_line ↔ schedule.electrical_panel · Key: Switchboard, panel or transformer name · Fields: voltage and configuration, bus rating, main device type and rating, feeder device and conductor size, fed from, short-circuit rating, normal or standby source · Owner: design_team · Gate: procurement_release · _26 20 00_
- **[medium] 26pb.rc.circuits** — Every circuit on the power and lighting plans appears on its panel schedule under the same panel and number, and no scheduled circuit is missing from the plans.  
  Between: schedule.electrical_panel ↔ drawings.electrical · Key: Panel and circuit number · Fields: load served, poles and trip, room, normal or standby · Owner: design_team · _26 24 00_

## Compliance — regulatory hooks (13)
- **[critical] d26.rh.load-classification** (`emergency-standby-load-classification`) — Which loads must be on an emergency, legally required standby or optional standby system (or on essential electrical system branches where the facility type has them), under which codes and standards, and what transfer time, wiring separation and testing does each class require?  
  **Unbound** → Run /construction:code-researcher with research topic "emergency-standby-load-classification" (seed it with this hook's question)
- **[high] d26.rh.electrical-code-amendments** (`electrical-code-edition-local-amendments`) — Which edition of the electrical code is adopted here, with what local amendments, and does the jurisdiction restrict wiring methods or conductor materials (cable assemblies, aluminum conductors, nonmetallic raceway) beyond the model code?  
  **Unbound** → Run /construction:code-researcher with research topic "electrical-code-edition-local-amendments" (seed it with this hook's question)
- **[high] 26ds.rh.working-space** (`electrical-working-space`) — What working space depth, width and headroom, dedicated equipment space, and entrance and egress from the working space (including door hardware) does the adopted electrical code require for this equipment, and does the room layout provide it?  
  **Unbound** → Run /construction:code-researcher with research topic "electrical-working-space" (seed it with this hook's question)
- **[high] 26ds.rh.selective-coordination** (`selective-coordination-requirements`) — Which systems must be selectively coordinated under the adopted code (emergency, legally required standby, elevator feeders, fire pumps, critical operations power), over what range of fault current, and who must select and document the devices?  
  **Unbound** → Run /construction:code-researcher with research topic "selective-coordination-requirements" (seed it with this hook's question)
- **[high] 26ds.rh.utility** (`utility-service-metering-requirements`) — What does the serving utility require for service equipment, metering, current transformers, transformer pad, clearances and access, and service-entrance conductors, and has it accepted the service equipment drawings?  
  **Unbound** → Run /construction:code-researcher with research topic "utility-service-metering-requirements" (seed it with this hook's question)
- **[high] edu.rh.school-agency-review** (`school-construction-agency-review`) — Does a state agency other than the local building department review plans, approve changes or inspect construction for this school (common for public K-12 and in some states for community colleges), and what does it require for deferred submittals, change documents, testing laboratories and the inspector of record?  
  **Unbound** → Run /construction:code-researcher with research topic "school-construction-agency-review" (seed it with this hook's question)
- **[high] edu.rh.risk-category** (`building-risk-category-assignment`) — What risk category applies to this building under the adopted code (occupant load, designation as an emergency or community shelter), and which design loads, nonstructural anchorage and special inspections change because of it?  
  **Unbound** → Run /construction:code-researcher with research topic "building-risk-category-assignment" (seed it with this hook's question)
- **[medium] d26.rh.seismic** (`seismic-nonstructural-anchorage`) — Which electrical equipment, raceway, cable tray and luminaires need seismic anchorage or bracing in this project's seismic design category, which exemptions apply, and does the submittal include the anchorage design?  
  **Unbound** → Run /construction:code-researcher with research topic "seismic-nonstructural-anchorage" (seed it with this hook's question)
- **[medium] d26.rh.seismic-certification** (`seismic-equipment-certification`) — Are generators, transfer switches, distribution equipment, fire alarm and emergency lighting equipment designated seismic systems here, and must the manufacturer certify that they remain operable after the design earthquake?  
  **Unbound** → Run /construction:code-researcher with research topic "seismic-equipment-certification" (seed it with this hook's question)
- **[medium] d26.rh.classified-locations** (`hazardous-location-classification`) — Are any areas classified as hazardous locations (fuel storage and dispensing, spray finishing, battery rooms, repair garages, process areas), and which equipment and wiring methods does the classification require?  
  **Unbound** → Run /construction:code-researcher with research topic "hazardous-location-classification" (seed it with this hook's question)
- **[medium] 26ds.rh.ground-fault** (`ground-fault-protection-of-equipment`) — Where does the adopted electrical code require ground-fault protection of equipment (by service or feeder disconnect rating and voltage, and additional levels in health care), and where does it prohibit it?  
  **Unbound** → Run /construction:code-researcher with research topic "ground-fault-protection-of-equipment" (seed it with this hook's question)
- **[medium] 26ds.rh.equipment-marking** (`available-fault-current-and-arc-flash-marking`) — What must be field-marked on service and distribution equipment under the adopted code (available fault current with the date it was calculated, arc-flash warnings or incident energy labels), and when must the marking be updated?  
  **Unbound** → Run /construction:code-researcher with research topic "available-fault-current-and-arc-flash-marking" (seed it with this hook's question)
- **[medium] 26ds.rh.arc-energy-reduction** (`arc-energy-reduction-requirements`) — Does the adopted electrical code require an arc energy reduction method on circuit breakers or fuses above a rating threshold, which methods qualify (maintenance switching, zone-selective interlocking, differential relaying, energy-reducing active arc-flash mitigation), and must the method be performance-tested at installation?  
  **Unbound** → Run /construction:code-researcher with research topic "arc-energy-reduction-requirements" (seed it with this hook's question)

## Coordination routing (14)
- **[critical] if.26-utility-service** → Electrical utility distribution and utility transformers (33 71 00, 33 73 00) · Gate: procurement_release — Get the utility's requirements and fault data in writing before service equipment is released
  - Send them: Service size and voltage, load letter, and service equipment and metering drawings for the utility's acceptance
  - Need from them: The utility's written service requirements (transformer location, pad and clearances, metering and current transformers, available fault current and X/R), primary and secondary duct scope, and the energization process
  - Confirm who: Utility transformer pad, primary duct and secondary service conductors — typical furnish serving utility, 33 71 00 or 26 05 43 / install serving utility, 33 71 00 or 26 05 43
  - Confirm who: Metering and current-transformer enclosures — typical furnish serving utility or 26 20 00 / install 26 20 00
  - If missed: Pad, primary duct, metering and fault data assumed instead of obtained in writing; the utility refuses to set its transformer or energize, or equipment ratings and the study rest on the wrong fault current
- **[high] if.03-housekeeping-pads** → Cast-in-place concrete (03 30 00) · Gate: slab_pour — Dowels go in with the slab; the pad waits for the approved equipment submittal
  - Send them: Approved footprint, weight, anchor pattern and anchorage design, pad height for traps and drains, and pad locations checked against service clearances, before the pad pour
  - Need from them: Pads formed and doweled to the slab to the approved equipment dimensions, with the anchor embedment and edge distance the anchorage needs
  - Confirm who: Pad dimensions and locations — typical furnish the equipment's trade / install 03 30 00
  - Confirm who: Equipment anchors into pads — typical furnish the equipment's trade / install the equipment's trade or 03 30 00
  - If missed: Pads formed from the scheduled equipment before the equipment submittal was approved
- **[high] if.11-equipment-power** → Equipment (all Division 11) (11) · Gate: in_wall_rough_in
  - Send them: Circuits, receptacles and disconnects matching each approved item, final connections, and the standby branch for items the owner designates
  - Need from them: Nameplate electrical data per item, plug configuration or hardwired connection point, integral disconnects, and the control wiring diagram between remote components of an item
  - Confirm who: Final electrical connection to hardwired equipment — typical connect 26 05 83
  - Confirm who: Disconnect switches at equipment — typical furnish 26 28 16 or integral to the equipment / install Division 26
  - Confirm who: Control wiring between remote components of one item (condensing unit to evaporator, hood panel to fans, controller to motorized equipment) — typical furnish Division 11 / install Division 11 or Division 26
  - If missed: Control wiring between components of one item claimed by neither the equipment vendor nor the electrician; equipment cannot start at turnover
- **[high] if.11-medical-equipment-power-data** → Healthcare equipment (11 70 00) · Gate: underslab_rough_in
  - Send them: Circuits on the required branches, pathways and floor trenches to the vendor's locations, data outlets and nurse call integration
  - Need from them: Power per item with branch and receptacle type, vendor disconnects and emergency-off, data and nurse call needs, cable pathways and trenches
  - Confirm who: Interconnecting cables between imaging components — typical furnish 11 70 00 / install 11 70 00 or Division 26
  - Confirm who: Pathways, trenches and floor ducts for vendor cabling — typical furnish 26 05 33 or 26 05 39 / install 26 05 33 or 26 05 39
  - If missed: Imaging cable trenches and pathways missing at slab pour; slabs saw-cut for the vendor's cabling
- **[high] if.13-cold-storage-power** → Cold storage rooms (13 21 26) · Gate: in_wall_rough_in
  - Send them: Circuits, disconnects and heat trace power and alarm, roughed in before the room is set
  - Need from them: Loads, voltages and locations for condensing units, evaporators, door and relief-port heaters, underfloor heat trace and its monitoring, and lights
  - Confirm who: Control wiring between condensing unit, evaporators and room controller — typical install 13 21 26 or 26 05 83
  - If missed: Freezer built on grade without heat trace or a ventilated subfloor, or the heat trace never energized or monitored
- **[high] if.14-conveying-power** → Conveying equipment (all Division 14) (14 10 00, 14 20 00, 14 30 00, 14 40 00, 14 92 00) · Gate: energization — Installers need permanent power to adjust and test; temporary power rarely satisfies the controller
  - Send them: Feeders and mainline disconnects sized to that data, separate car lighting circuits, pit and machine room lighting and receptacles, and standby transfer with a pre-transfer signal
  - Need from them: Electrical data per unit (voltage, phase, full-load and starting current, heat release), required disconnect locations, and standby operation signals
  - Confirm who: Mainline and car lighting disconnects — typical furnish 26 28 16 / install Division 26
  - Confirm who: Pre-transfer and standby power signal wiring to the controller — typical install Division 26 / connect Division 14
  - If missed: Units wait on permanent power or standby signals for adjustment and acceptance; turnover slips
- **[high] if.22-equipment-power** → Plumbing equipment, pumps and heat tracing (22 05 33, 22 11 00, 22 13 00, 22 14 00, 22 30 00) · Gate: procurement_release
  - Send them: Circuits, disconnects and controllers sized to that data, standby power where the design puts pumps or heaters on it, and alarm wiring to the monitoring point
  - Need from them: Electrical data for the approved models (voltage, phase, load, elements operating at once), pump control panels and alarms, and heat tracing circuits with their ground-fault protection
  - Confirm who: Disconnects and motor controllers for plumbing equipment — typical furnish Division 26 or with the equipment / install Division 26 / connect Division 26
  - Confirm who: Pump control panels and alarm devices — typical furnish 22 13 00 or 22 14 00 / install 22 13 00 or 22 14 00 / connect Division 26
  - If missed: Heat tracing installed without circuits or ground-fault protection in the electrical design; Electric heater submitted at a different voltage or kW, or with all elements firing at once, against the panel schedule
- **[high] if.22-gas-source-power** → Medical and laboratory gas sources and alarms (22 60 00, 22 09 63) · Gate: in_wall_rough_in
  - Send them: Circuits from the branch of the essential electrical system, or the standby system, that the design assigns, through the matching transfer switch
  - Need from them: Source equipment and alarm panel loads and locations, and which must stay on through an outage
  - If missed: Alarm panels or source equipment circuited from normal power
- **[high] if.23-equipment-power** → HVAC equipment (23 05 13, 23 21 23, 23 34 00, 23 36 00, 23 50 00, 23 60 00, 23 70 00, 23 80 00) · Gate: procurement_release — Repeat the exchange after every substitution, alternate or option change, before the electrical gear is released
  - Send them: Circuit, overcurrent device, conductors, disconnect and starter or drive per tag sized to the approved data, emergency or standby power where scheduled, and the service receptacle and lighting at rooftop and attic equipment
  - Need from them: Electrical data per tag from the approved submittal (voltage, phase, MCA, MOCP, number of connections), which disconnects, starters and drives come factory-mounted, and every change after a substitution or option change
  - Confirm who: Variable-frequency drives — typical furnish 23 (with the equipment) or 26 29 23 / install 26 or 23 for unit-mounted drives / connect 26
  - Confirm who: Disconnect switches at equipment — typical furnish 26 28 16 or 23 (factory-mounted) / install 26
  - Confirm who: Motor starters for equipment without factory controls — typical furnish 26 29 13, 26 24 19 or 23 / install 26
  - If missed: Equipment arrives with electrical data the circuits were not built for; breakers, wire and disconnects changed at startup
- **[high] if.26-telecom-room-power** → Structured cabling and equipment room fittings (27 10 00, 27 11 00) · Gate: in_wall_rough_in — Receptacle types follow the owner's equipment choice, which often comes late
  - Send them: Dedicated circuits and receptacle configurations at each rack, the panel serving telecom rooms and its source, and UPS where electrical furnishes it
  - Need from them: Rack layouts, equipment loads and plug types, UPS sizing and who furnishes it
  - Confirm who: UPS for telecom racks — typical furnish 26 33 53, 27 11 26 or owner / install 26 33 53 or 27 11 26
  - If missed: Racks arrive with plug types and loads the room circuits don't match; circuits rerun after the room is finished
- **[high] if.26-errcs-power** → In-building radio and antenna systems (27 53 19) · Gate: above_ceiling_close_in — Radio coverage is often added after the survey; request locations as soon as the need is known
  - Send them: Dedicated circuit on the source the radio coverage code requires, with the circuit protection and identification that code calls for
  - Need from them: Amplifier and headend locations and loads, battery cabinets, and the source the code requires
  - If missed: No circuit on the source the code requires was designed for the amplifiers
- **[high] if.26-fire-alarm-power** → Fire detection and alarm (28 46 00) · Gate: above_ceiling_close_in — Extender locations come from the fire alarm shop drawings, which often arrive after electrical rough-in starts
  - Send them: Dedicated branch circuits to the control unit, power extender panels and other fire alarm equipment, with locking means and circuit identification, on the source the design requires; monitoring contacts on generators, transfer switches and fire pump controllers where required
  - Need from them: Number, locations and loads of control units and power extender panels from the fire alarm shop drawings, and the electrical status points it must monitor
  - Confirm who: Branch circuits to power extender panels added by the fire alarm shop drawings — typical install Division 26 or 28 46 00
  - If missed: Power extender panels located by the fire alarm designer with no circuits; circuits pulled through finished ceilings before the acceptance test
- **[high] if.26-study-equipment** → Power system study (26 05 73) · Gate: procurement_release — Review the study with the distribution equipment submittals, before release
  - Send them: Submitted equipment data the study models (device types, frames, trip units and ratings, series combinations, transformer impedances, generator reactances, transfer switch withstand basis) and feeder sizes and lengths
  - Need from them: Calculated fault at each bus against each device and assembly rating, the device types, frames and trip units selectivity needs, recommended settings, and arc-flash results with any energy-reduction feature they depend on
  - Confirm who: Preparing the study and applying its settings in the field — typical furnish 26 05 73, often by the equipment manufacturer or an independent engineer / install 26 05 73 or the testing agency
  - If missed: Selective coordination for emergency or elevator circuits cannot be met with the breakers already submitted
- **[medium] if.26-security-power** → Access control, video surveillance and intrusion detection (28 10 00, 28 20 00, 28 30 00) · Gate: above_ceiling_close_in
  - Send them: Circuits to access control panels, lock power supplies, intrusion panels and security equipment racks, on the source the owner's standards require
  - Need from them: Panel and power supply locations and loads, and which must be on standby power
  - If missed: Lock power supplies and panels located late with no circuits, or on normal power where the owner expected standby

## Failure modes to watch (23)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d26.fm.mixed-classes** — Optional standby loads put on an emergency panel, or emergency circuits run in raceway with normal circuits → Rejected at inspection; panels re-circuited and raceway rerun late in the job (caught by d26.emergency-separation; industry_practice)
- **d26.fm.wrong-enclosure** — Indoor-rated enclosure or damp-rated luminaire installed in a wet, washdown or outdoor location → Corrosion and failures after turnover; replacement under warranty dispute (caught by d26.ratings-for-location; industry_practice)
- **26ds.fm.substitution-not-carried** — Mechanical or owner equipment is substituted or re-selected after the electrical design, and the new MCA, MOCP or voltage never reaches the panel schedules → Wrong breakers, conductors or disconnects found at start-up; equipment cannot be energized until rework (caught by 26ds.rc.equipment-nameplate; industry_practice)
- **26ds.fm.orphan-equipment** — Equipment added by an ASI or owner change with no circuit, or a circuit left serving equipment that was deleted → Circuits added after panels are full and walls are closed; change orders and panel rework (caught by 26ds.equipment-connections; industry_practice)
- **26ds.fm.double-furnished** — Equipment arrives with a factory disconnect or drive and electrical installs a second one, or each side assumed the other furnished the drive → Duplicate cost, or no drive at start-up (caught by 26ds.disconnect-furnish; industry_practice)
- **26ds.fm.fault-rises** — The utility installs a larger or lower-impedance transformer, or a building transformer is substituted, after equipment ratings were set → Equipment rated below the available fault current; replacements, added current-limiting devices, or a failed inspection (caught by 26ds.sccr-vs-fault; industry_practice)
- **26ds.fm.released-before-study** — Switchboards and panelboards released on assumed fault levels; the study arrives after fabrication → Re-fabrication or field-replaced breakers, or selective coordination quietly abandoned (caught by 26ds.study-before-release; industry_practice)
- **26ds.fm.utility-rejects** — Service equipment built without the utility's metering and service requirements → Utility refuses to energize; metering section rebuilt and permanent power delayed (caught by 26ds.utility-requirements; industry_practice)
- **26ds.fm.no-path-in** — Switchboard sections or a transformer cannot pass through the doors, corridors or elevator once walls are built → Walls, louvers or slabs opened, or equipment split in the field at the risk of its listing (caught by 26ds.fits-room-and-path; industry_practice)
- **26ds.fm.pipe-over-gear** — Sprinkler, domestic water or drain piping routed through the dedicated space above switchboards and panelboards → Rejected at inspection; piping rerouted after the room is built out (caught by 26ds.dedicated-space; industry_practice)
- **26ds.fm.stubs-misaligned** — Conduit stub-ups cast from the design drawings, then another manufacturer's switchboard is approved → Stubs land outside the conduit entry area; slab chipped or equipment modified (caught by 26ds.stub-ups, if.03-housekeeping-pads; industry_practice)
- **26ds.fm.downstream-bond** — Neutral bonded to ground in a downstream panel, or at a generator that feeds a transfer switch with a solid neutral → Objectionable current on grounding paths, ground-fault protection misoperation, failed inspection (caught by 26ds.grounding-neutral; industry_practice)
- **26pb.fm.spaces-used-up** — Panelboards released before ASIs added circuits; spares and spaces consumed before the building is occupied → Added panels or sub-feeds late, with no wall space left for them (caught by 26pb.spares; industry_practice)
- **26pb.fm.lugs-too-small** — Aluminum or paralleled feeders substituted without checking lug size and gutter space → Lugs replaced or enclosures enlarged in the field; energization delayed (caught by 26pb.lugs-and-gutters; industry_practice)
- **26pb.fm.recessed-in-rated-wall** — Recessed panelboard installed in a rated wall with no listed protection → Wall fails inspection; panel relocated or a rated box-out built around it (caught by 26pb.wall-mounting; industry_practice)
- **26pb.fm.wrong-device-type** — Board shipped with standard breakers where the schedule called for GFCI, AFCI, shunt-trip or lock-on devices → Field replacement and re-inspection (caught by 26pb.schedule-match; industry_practice)
- **edu.fm.missed-window** — Hardware, HVAC equipment or casework approved late and delivered after the summer window closes → Work moves into occupied classrooms after hours with temporary systems, or the phase slips a full year (caught by edu.summer-window; field_experience)
- **edu.fm.agency-change-unapproved** — A substitution or field change accepted by the architect is never submitted to the state school-construction agency → The agency withholds certification or closeout of the project; work is reopened or occupancy delayed (caught by edu.agency-approvals; industry_practice)
- **edu.fm.default-risk-category** — Delegated cladding, joist or anchorage design done to the default risk category on a school assigned a higher one → Components under-designed; recalculation and field reinforcement after installation (caught by edu.risk-category-delegated; industry_practice)

## Expected submittal contents
- **Shop Drawings**
  - One-line matching the contract single-line, with bus, main and feeder ratings
  - Short-circuit current rating of each assembly and interrupting rating of each device, with any series-rated combinations and their listing
  - Plan footprint, elevations, shipping splits and weights, and conduit entry areas
  - Utility metering and current-transformer compartments built to the serving utility's standards
  - Neutral and grounding arrangement at the service and at each separately derived system
  - Surge protective device location, type and short-circuit rating
- **Product Data**
  - Transformers with winding configuration, impedance, harmonic rating where specified, temperature rise and sound level
  - Overcurrent devices with trip unit type and adjustable functions
- **Design Data**
  - Seismic certification or anchorage calculation where required
- **Certificates**
  - The serving utility's acceptance of the service equipment and metering drawings
- **Shop Drawings**
  - Each board by its tag, with voltage, bus rating, main device or main lugs, and short-circuit rating
  - Every device with poles, trip, frame and type (GFCI, AFCI, shunt trip, lock-on, ground-fault)
  - Spares and spaces, feed-through or sub-feed lugs, and lug sizes and quantities
  - Mounting (surface or flush), enclosure type, and trim

## Extract for reconciliation
- 26ds.xf.available-fault — Available fault current used for ratings, and its source (string, per package) → report.utility_requirements, drawings.single_line
- 26ds.xf.footprint — Footprint, largest shipping section and weight per assembly (list, per item) → drawings.enlarged_plans
- 26pb.xf.main — Main device type and rating, or main lugs (string, per element) → schedule.electrical_panel, drawings.single_line
- 26pb.xf.sccr — Assembly short-circuit current rating (number, kA, per element) → drawings.single_line
- 26pb.xf.devices — Devices with poles, trip and type (list, per element) → schedule.electrical_panel

## Standards to verify against
- NFPA 70: National Electrical Code
- ANSI/NETA ATS: Standard for Acceptance Testing Specifications for Electrical Power Equipment and Systems — Confirm the edition the spec cites
- UL 891: Switchboards
- UL 67: Panelboards

## Warnings
- No profile for 26 24 16; compiled from ancestors only
- Draft knowledge in use (global, 26, 26 20 00, 26 24 00) — not yet PE-reviewed
