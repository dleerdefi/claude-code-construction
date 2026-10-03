# Compiled knowledge — 28 46 00 Fire Detection and Alarm

Facility types: education.k12 · Confidence floor: **draft** · Review mode: package · Contractor-designed: typical
Lineage: global → 28 → [28 40 00 missing] → 28 46 00
Overlays: education, education.k12

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Fire alarm and detection, usually performance-specified: the engineer shows intent and the contractor's designer produces the permit drawings, calculations and sequence of operations (28 46 11 through 28 46 24 inherit from here). It is the most connected system in the building (sprinkler supervision, elevator recall and shunt trip, air handler shutdown and smoke control, dampers, door hold-opens and locked-door release, kitchen hood suppression, generators and fire pumps) and most acceptance failures are integration failures. Devices go in after finishes, but their wiring, the interface modules and the other trades' contacts must be in place before ceilings close.

## Review checks (23)
### completeness
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] g.contractor-designed** — This scope is often performance-specified and designed or selected by the contractor. Confirm the spec's design criteria are complete enough to design to; whether the AHJ treats the design as a deferred submittal and when it must be filed relative to installation; and that the designer's assumptions about support, attachment and adjacent work are confirmed by the trades that provide them.  
  Trace: spec.part1, spec.part2 · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] 28fa.monitoring-path** — The communicator, its communication paths and the supervising station contract are arranged so monitoring is live for the acceptance test.  
  Trace: spec.part1, drawings.fire_alarm · Owner: owner · Scope: package · Gate: substantial_completion · _28 46 00_
- **[high] 28fa.acceptance** — Pre-test of every device and interface, the acceptance test with the AHJ witness, the record of completion and record drawings are scheduled after the systems it controls (elevators, smoke control, dampers, suppression, access control) are ready to be tested together.  
  Trace: spec.part3, report.commissioning · Owner: gc · Scope: package · Gate: substantial_completion · _28 46 00_
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
- **[high] 28fa.battery-calcs** — Secondary power calculations use the submitted devices' standby and alarm currents for the durations the code requires, with the capacity margin the spec states, for the control unit and every power extender.  
  Trace: spec.part2, drawings.fire_alarm · Owner: subcontractor · Scope: package · _28 46 00_
- **[high] 28fa.voltage-drop** — Notification circuit voltage drop is calculated to the last appliance at the lowest supply voltage the equipment listing allows (battery at end of discharge), over the installed circuit lengths.  
  Trace: drawings.fire_alarm · Owner: subcontractor · Scope: package · _28 46 00_
- **[high] 28fa.notification-coverage** — Audible and visible notification reaches every occupiable space, including restrooms, sleeping rooms with the appliances required there, and spaces whose noise or shape needs added appliances; strobes seen together are synchronized as the code requires, and speaker taps and candela settings are on the drawings.  
  Trace: drawings.fire_alarm, drawings.plans · Owner: subcontractor · Scope: package · _28 46 00_
- **[high] 28fa.survivability** — Circuits that must survive attack by fire (voice evacuation risers in partial-evacuation or relocation buildings, and others the code names) use the pathway survivability level required: rated cable, a rated shaft or enclosure, or a route the code accepts.  
  Trace: drawings.fire_alarm, drawings.life_safety · Owner: subcontractor · Scope: package · _28 46 00_
- **[medium] 28fa.annunciator** — Control unit and annunciator locations are the ones the fire department accepts (responding entrance, fire command center), and annunciator zoning matches what responders need to find an alarm.  
  Trace: drawings.fire_alarm, drawings.life_safety · Owner: design_team · Scope: package · _28 46 00_
### coordination
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
- **[high] d28.owner-platform** — Where the owner already runs a platform the new system must join (a security head-end and credential system, or a campus fire alarm network and its proprietary supervising station), the platform, licensing and cybersecurity rules are written into the contract documents before product data is reviewed against the basis of design.  
  Trace: spec.part1, spec.part2_manufacturers · Owner: owner · Scope: package · Gate: procurement_release · _28_
### constructability
- **[high] edu.summer-window** — Where work in existing schools must fit a break in the academic calendar, each submittal's approval, owner selections, mock-ups and delivery are dated against the day the window opens, not against a floating schedule activity. Long-lead items (door frames and hardware, HVAC equipment, switchgear, casework, flooring) that miss the window push work into occupied classrooms or a year later, so their submittals are released first.  
  Trace: schedule.master, spec.division_01 · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[medium] 28fa.detector-protection** — Smoke detectors are installed after construction cleaning, or, where phased occupancy or the AHJ needs them in service earlier, are protected during dusty work and cleaned or replaced before the acceptance test, with the cost and responsibility for that assigned.  
  Trace: spec.part3, schedule.master · Owner: gc · Scope: package · _28 46 00_
### absence
- **[high] 28fa.duct-detectors** — Duct smoke detectors on the fire alarm drawings match every air handler, damper and duct location the mechanical drawings and schedules call for, and concealed detectors have remote test and indicator stations.  
  Trace: drawings.mechanical, schedule.mechanical_equipment, drawings.fire_alarm · Owner: gc · Scope: package · _28 46 00_
- **[high] 28fa.existing-system** — In alterations and additions, new devices are listed as compatible with the existing control unit and fit its remaining capacity, or the replacement scope is defined in the contract documents.  
  Trace: drawings.fire_alarm, drawings.demolition, report.existing_conditions · Owner: design_team · Scope: package · _28 46 00_
- **[medium] d28.head-end-spaces** — Head-end equipment (fire alarm control units, access control and video servers and storage, intrusion panels) has a room or rack with power, network, cooling and service clearance, and remote panels sit where they can be serviced without entering secure or occupied spaces.  
  Trace: drawings.enlarged_plans, drawings.security, drawings.fire_alarm · Owner: design_team · Scope: package · _28_

## Reconciliations — documents that must agree (2)
- **[critical] 28fa.rc.sequence-matrix** — Every output in the fire alarm sequence matrix has its counterpart on the other trade's documents (air handlers and smoke control modes in the mechanical sequences, dampers on the damper schedule, held-open and access-controlled doors in the hardware sets, elevator recall floors, sprinkler and suppression contacts), and every point those documents expect the fire alarm to monitor or control is in the matrix.  
  Between: drawings.fire_alarm ↔ drawings.mechanical ↔ schedule.door_hardware ↔ drawings.fire_protection ↔ drawings.electrical · Key: Each input and each controlled output · Fields: initiating device or system, air handler shutdown or smoke control mode, damper action, door hold-open release and locked-door unlock, elevator recall floors and shunt trip, sprinkler and suppression supervision, generator and fire pump supervision · Owner: gc · Gate: above_ceiling_close_in · _28 46 00_
- **[medium] 28fa.rc.devices-vs-rcp** — Device locations on the fire alarm drawings work with the reflected ceiling plans: detectors kept clear of supply diffusers and beam pockets by the spacing rules, appliances not hidden by soffits or bulkheads, and high, sloped or beamed ceilings treated as the standard requires.  
  Between: drawings.fire_alarm ↔ drawings.rcp ↔ drawings.mechanical · Key: Room · Fields: detector locations against diffusers and returns, beam and soffit conditions, ceiling height and slope, appliance mounting · Owner: subcontractor · Gate: above_ceiling_close_in · _28 46 00_

## Compliance — regulatory hooks (8)
- **[critical] 28fa.rh.system-required** (`fire-alarm-system-requirements`) — What fire alarm system does the adopted code require for this occupancy (manual initiation, automatic detection, occupant notification, emergency voice/alarm communication), and where may detection be omitted because the building is sprinklered?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-alarm-system-requirements" (seed it with this hook's question)
- **[high] 28fa.rh.notification** (`fire-alarm-notification-coverage`) — What audible, visible and voice notification do the adopted code and accessibility standard require here (sleeping rooms, restrooms, public and common use areas, voice intelligibility), and which spaces may be exempt?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-alarm-notification-coverage" (seed it with this hook's question)
- **[high] 28fa.rh.secondary-power** (`fire-alarm-secondary-power`) — What standby and alarm durations on secondary power does the adopted code require for the fire alarm and emergency communication system, and is a capacity margin required?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-alarm-secondary-power" (seed it with this hook's question)
- **[high] 28fa.rh.survivability** (`fire-alarm-pathway-survivability`) — Which fire alarm and emergency communication pathways need survivability here (high-rise, partial evacuation or relocation, areas of refuge), and at what level?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-alarm-pathway-survivability" (seed it with this hook's question)
- **[high] 28fa.rh.acceptance** (`fire-alarm-acceptance-testing`) — What acceptance testing, AHJ witnessing, documentation (record of completion, record drawings) and supervising station connection does the jurisdiction require before occupancy?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-alarm-acceptance-testing" (seed it with this hook's question)
- **[high] edu.rh.school-agency-review** (`school-construction-agency-review`) — Does a state agency other than the local building department review plans, approve changes or inspect construction for this school (common for public K-12 and in some states for community colleges), and what does it require for deferred submittals, change documents, testing laboratories and the inspector of record?  
  **Unbound** → Run /construction:code-researcher with research topic "school-construction-agency-review" (seed it with this hook's question)
- **[medium] 28fa.rh.duct-detectors** (`duct-smoke-detector-requirements`) — Must the duct smoke detectors the mechanical code requires connect to the building fire alarm system, and do they initiate a supervisory or an alarm signal with what remote indication?  
  **Unbound** → Run /construction:code-researcher with research topic "duct-smoke-detector-requirements" (seed it with this hook's question)
- **[medium] 28fa.rh.carbon-monoxide** (`carbon-monoxide-detection`) — Does the adopted code require carbon monoxide detection in this occupancy (fuel-burning appliances, enclosed parking, classrooms or sleeping rooms), and must it report to the fire alarm system?  
  **Unbound** → Run /construction:code-researcher with research topic "carbon-monoxide-detection" (seed it with this hook's question)

## Coordination routing (22)
- **[critical] if.01-integrated-life-safety-testing** → Commissioning (integrated testing) (01 91 00) · Gate: substantial_completion
  - Send them: Each system tested and accepted on its own first; interface relays and devices installed, programmed to the matrix and labeled
  - Need from them: One integrated test plan, the input-output sequence matrix, and a test date with the AHJ
  - If missed: Fire alarm, elevator, damper and smoke-control interfaces are first tested together at the AHJ's final inspection
- **[critical] if.08-fire-alarm-doors** → Door hardware, coiling fire doors and automatic entrances (08 71 00, 08 33 00, 08 42 29) · Gate: wall_close_in — Acceptance testing of every release follows at substantial completion
  - Send them: Release relays, holder circuits and detectors at each of those doors, programmed to the sequence, and acceptance testing with the door trades present
  - Need from them: The doors that release, unlock, close or stop on alarm (hold-opens, fail-safe locks, delayed egress, stair re-entry, rolling fire doors and shutters, operators), with the input or contact each needs
  - Confirm who: Magnetic door holders — typical furnish 08 71 00 or 28 46 00 / install 08 71 00 or 28 46 00 / connect 28 46 00
  - Confirm who: Detectors and release devices for rolling fire doors — typical furnish 08 33 00 or 28 46 00 / connect 28 46 00
  - If missed: Rated coiling door's release never tied to the fire alarm, or its operator holds the door open on alarm; Fail-safe locks, hold-opens or delayed egress devices not tied to the fire alarm
- **[critical] if.14-elevator-fire-alarm** → Elevators (14 20 00) · Gate: above_ceiling_close_in
  - Send them: Smoke detectors at each elevator lobby, the machine room or control space and the hoistway where required, with outputs mapped to designated and alternate recall and the hat
  - Need from them: Recall inputs the controller accepts (designated and alternate landing, firefighter's hat), status outputs, and Phase II switch locations
  - Inspect before: Recall functions tested with the fire alarm system before the elevator acceptance inspection
  - Confirm who: Recall and status wiring between the fire alarm system and each controller — typical install 28 46 00 / connect 28 46 00 and Division 14
  - If missed: Fire alarm recall outputs do not match the controller's designated and alternate landing logic
- **[critical] if.14-elevator-sprinkler-shunt-trip** → Elevators (14 20 00) · Gate: overhead_rough_in
  - Send them: Sprinklers where required, a heat detector beside each sprinkler that the elevator code ties to shunt trip, a shunt-trip disconnect that opens before water flows, and monitoring of its control power
  - Need from them: Hoistway, pit and machine room or control space locations, and the mainline disconnect location and rating
  - Confirm who: Shunt-trip mainline disconnect — typical furnish 26 28 16 / install Division 26
  - Confirm who: Heat detectors and shunt-trip control relay — typical furnish 28 46 00 / install 28 46 00
  - If missed: Sprinklers installed in the hoistway or machine room without shunt trip and heat detectors; Sprinklers installed in an elevator machine room or hoistway without the heat detector and shunt trip that must accompany them
- **[critical] if.23-fire-alarm-hvac** → HVAC controls and smoke dampers (23 09 00, 23 33 00) · Gate: procurement_release — The fire alarm shop drawings need the HVAC response matrix
  - Send them: Relays and monitor modules, their wiring, fire alarm programming and the acceptance test with HVAC operating
  - Need from them: The HVAC response matrix (which units stop, which dampers move, smoke control modes, restart), relay and module locations at starters, drives and damper actuators, and damper position switches
  - Confirm who: Shutdown relays at fans and drives (working in drive bypass) — typical furnish 28 46 00 / connect 28 46 00 or 23 09 00
  - Confirm who: Smoke damper control and position monitoring — typical install 28 46 00 or 23 09 00
  - Confirm who: Firefighter's smoke control panel — typical furnish 28 46 00 or 23 09 00
  - If missed: Fire alarm shutdown wired to the automation controller instead of the starter or drive, or lost when the drive is in bypass; Smoke damper actuators with no power circuit, or no fire alarm module to close them
- **[critical] if.28-fire-alarm-access-release** → Access control (28 10 00) · Gate: above_ceiling_close_in
  - Send them: Relay outputs that release fail-safe locks and unlock stair doors on alarm, by the zones the code requires
  - Need from them: Fail-safe locks and power supplies with fire alarm release inputs at each location, and the list of doors that must release
  - Confirm who: Relay modules and wiring from the fire alarm to lock power supplies — typical furnish 28 46 00 / install 28 46 00 or 28 10 00
  - If missed: Fail-secure lock on an egress door with no mechanical free egress, or a magnetic lock with no fire alarm and power-loss release
- **[high] if.01-cutting-patching-mep** → Cutting and patching (01 73 00) · Gate: wall_close_in — Openings planned before close-in avoid cutting finished work
  - Send them: Openings needed in existing or finished construction, located and sized before cutting, and kept within what the patch and firestop system allow
  - Need from them: Who cuts, who patches the substrate, who finishes the patch, and the standard the patch must meet
  - Confirm who: Patching and refinishing openings the MEP trades cut in finished walls and ceilings — typical install 01 73 00 (general contractor) or the cutting trade
  - If missed: An MEP trade cuts finished gypsum board and ceilings for late work and leaves the opening
- **[high] if.02-fire-protection-impairment** → Demolition (02 41 00) · Gate: demolition_start
  - Send them: Impairment notices, drain-down and refill, detector protection and daily restoration, and temporary coverage for areas staying in use
  - Need from them: Areas and dates where demolition affects sprinkler and alarm coverage or creates dust at detectors
  - If missed: Smoke detectors left uncovered during demolition, or covered and never restored
- **[high] if.firestop-mep-penetrations** → Firestopping (07 84 00) · Gate: procurement_release — Settle the installer and the system matrix before rough-in starts
  - Send them: Penetrant types, materials, sizes and insulation through each rated assembly; openings sized within system limits
  - Need from them: Listed system per penetrant and assembly, with annular space and opening limits
  - Confirm who: Firestopping of MEP penetrations through rated assemblies — typical furnish 07 84 00 / install 07 84 00 or each penetrating trade
  - If missed: Each MEP trade firestops its own penetrations with its own products; Boxes set back to back in rated or acoustically rated walls without the listed protection or offset
- **[high] if.11-hood-fire-alarm** → Food cooking equipment, kitchen hoods and hood suppression (often specified in 11 40 00, hoods sometimes in 23 38 13) (11 44 00, 23 38 13) · Gate: above_ceiling_close_in
  - Send them: Monitoring of the suppression system and control relays for the shutdowns the design requires
  - Need from them: Suppression system alarm and supervisory contacts, and the fans, make-up air and appliances that must respond on discharge
  - Inspect before: Hood suppression acceptance test witnessed by the fire authority
  - Confirm who: Wiring from the suppression control head to the fire alarm system — typical install 28 46 00 / connect 28 46 00
  - If missed: Hood suppression system not connected to the building fire alarm, or make-up air not shut down on discharge
- **[high] if.11-stage-fire-curtain** → Stage equipment (fire curtain and smoke vents, where provided) (11 61 00) · Gate: procurement_release
  - Send them: Detection and release signals, deluge or water curtain piping where used, and monitoring
  - Need from them: Fire curtain or water curtain release devices and stage smoke vent operators, with their release and reset requirements
  - If missed: Fire curtain or stage vents installed with no release signal from detection; fails the fire authority's acceptance test
- **[high] if.21-supervision** → Fire suppression (21) · Gate: above_ceiling_close_in — Modules and wiring at devices above ceilings go in before the ceiling closes
  - Send them: A monitored point and module for each, programmed as alarm, supervisory or trouble, and power to the devices that need it
  - Need from them: The list and location of every supervised device and signal (tamper, waterflow, low air, pump running, power and phase failure, releasing panel outputs)
  - Confirm who: Tamper, flow and pressure switches — typical furnish 21 10 00 / install 21 10 00 / connect 28 46 00
  - If missed: Tamper and flow switches installed by the sprinkler contractor never reached the fire alarm design, or were added in the field without modules
- **[high] if.21-release-control** → Preaction, deluge and clean-agent systems (21 13 00, 21 22 00) · Gate: procurement_release — The panel and the valve actuators must be listed together
  - Send them: Detection layout and zoning for release, the releasing panel or its interface, and the alarm and shutdown outputs
  - Need from them: Release valve or actuator models, the releasing panels they are listed with, and the release logic (single or double interlock, cross-zoned detection, time delay and abort)
  - Confirm who: Releasing control panel and its detection — typical furnish 21 13 00, 21 22 00 or 28 46 00 / install 21 13 00, 21 22 00 or 28 46 00
  - If missed: The releasing panel and the agent valve actuators are not listed together
- **[high] if.23-duct-smoke-detectors** → Air-handling units, ductwork and smoke dampers (23 70 00, 23 80 00, 23 31 00, 23 33 00) · Gate: above_ceiling_close_in — Housings go in with the duct; the detector list has to be agreed when the fire alarm shop drawings are prepared
  - Send them: Detectors, housings and sampling tubes, remote test and indicator stations, wiring and programming of the shutdown
  - Need from them: Units and dampers that need duct detection, duct locations with the straight run and orientation the detector listing requires, and access doors at each detector
  - Confirm who: Duct detector housings and sampling tubes — typical furnish 28 46 00 / install 23 31 00 or 28 46 00
  - Confirm who: Remote test and indicator stations — typical furnish 28 46 00 / install 28 46 00
  - If missed: Duct detectors left off the fire alarm drawings for a unit above the code threshold, or furnished but never installed in the duct
- **[high] if.26-fire-alarm-power** → Electrical branch circuits and panelboards (26 05 19, 26 05 33, 26 24 16) · Gate: above_ceiling_close_in — Extender locations come from the fire alarm shop drawings, which often arrive after electrical rough-in starts
  - Send them: Number, locations and loads of control units and power extender panels from the fire alarm shop drawings, and the electrical status points it must monitor
  - Need from them: Dedicated branch circuits to the control unit, power extender panels and other fire alarm equipment, with locking means and circuit identification, on the source the design requires; monitoring contacts on generators, transfer switches and fire pump controllers where required
  - Confirm who: Branch circuits to power extender panels added by the fire alarm shop drawings — typical install Division 26 or 28 46 00
  - If missed: Power extender panels located by the fire alarm designer with no circuits; circuits pulled through finished ceilings before the acceptance test
- **[high] if.27-fire-alarm-communicator** → Communications services and cabling (27 05 28, 27 05 43, 27 10 00) · Gate: substantial_completion — The path must be live for the AHJ acceptance test, which comes before substantial completion
  - Send them: Communicator type, number of communication paths required and its location
  - Need from them: Telephone lines, network connection or antenna pathway from the service entrance to the communicator
  - Confirm who: Supervising station monitoring service and communication lines — typical furnish owner or 28 46 00
- **[high] if.27-paging-fire-alarm** → Paging, music and sound masking (27 51 00) · Gate: above_ceiling_close_in
  - Send them: Relay outputs and programming that operate that input on alarm
  - Need from them: A listed input that mutes or shuts down paging, music and sound masking
  - If missed: Background music or sound masking keeps playing during a voice alarm
- **[high] if.27-errcs-fire-alarm-monitoring** → In-building radio coverage (27 53 19) · Gate: above_ceiling_close_in
  - Send them: Monitor modules, programming and annunciation for those signals
  - Need from them: Supervisory outputs for amplifier, antenna, power and battery trouble at a point the fire alarm can reach
  - If missed: Signal boosters installed with no fire alarm monitoring points
- **[medium] if.06-equipment-backboards** → Rough carpentry (06 10 53) · Gate: equipment_set
  - Send them: Backboard layout per room (wall, size, height), treatment and finish requirements, and when equipment mounting starts
  - Need from them: Plywood backboards of the treatment and finish the drawings require, at the sizes and locations given
  - Confirm who: Plywood backboards in telecommunications and electrical rooms — typical furnish 06 10 53 or 27 11 00 / install 06 10 53 or 27 11 00
  - If missed: Backboards furnished by nobody, or untreated, or painted over the treatment stamp; equipment mounting waits or the inspector rejects the board
- **[medium] if.09-ceiling-low-voltage** → Suspended and gypsum board ceilings (09 50 00, 09 21 16) · Gate: overhead_rough_in
  - Send them: Device locations on the RCP, mounting method (tile bridge, support from structure, back box in board), weight, and detector placement that still meets the alarm design once soffits, beams and clouds are known
  - Need from them: Ceiling layout and types, including clouds, soffits and open areas where devices cannot mount on tile
  - If missed: Devices placed on panels that cannot carry them, or detectors and speakers relocated after the ceiling is built because the layout changed under them
- **[medium] if.09-boxes-in-sound-walls** → Gypsum board partitions (09 21 16) · Gate: wall_close_in
  - Send them: Box locations on both faces of those walls, box type, and pads or sealing installed before the second face is boarded
  - Need from them: Which partition types are sound-rated or rated, and the box separation, pads and sealing their tested design or acoustic design requires
  - If missed: Outlet boxes back to back in one stud bay, or perimeter left unsealed, in a sound-rated wall; Boxes set back to back in rated or acoustically rated walls without the listed protection or offset
- **[medium] if.10-wall-protection-devices** → Wall protection (10 26 00) · Gate: in_wall_rough_in
  - Send them: Device mounting heights and locations along those walls
  - Need from them: Rail, guard and handrail heights and extents along each corridor wall
  - If missed: Switches, thermostats, card readers and fire alarm devices roughed in at crash-rail or handrail height along corridors

## Failure modes to watch (17)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d28.fm.platform-mismatch** — Submittal approved on the spec's basis of design while the owner runs a different security or fire alarm network platform campus-wide → Replacement, or a second head-end the owner won't support (caught by d28.owner-platform; industry_practice)
- **d28.fm.no-server-room** — Video and access control servers have no conditioned room or rack space → Equipment in a closet without cooling; failures and relocation after turnover (caught by d28.head-end-spaces; industry_practice)
- **28fa.fm.matrix-orphan** — The matrix lists outputs to air handlers, dampers or doors the other trades never wired for, or the mechanical sequence expects a fire alarm signal the matrix lacks → Acceptance test fails on integrations; retest with the AHJ and occupancy delayed (caught by 28fa.rc.sequence-matrix, if.23-fire-alarm-hvac, if.08-fire-alarm-doors; industry_practice)
- **28fa.fm.recall-floors** — Elevator lobby, machine room and hoistway detectors not programmed for the primary and alternate recall floors, or the shunt trip not monitored → Elevator inspection and fire alarm acceptance both fail (caught by 28fa.rc.sequence-matrix, if.14-elevator-fire-alarm; industry_practice)
- **28fa.fm.diffuser-detector** — Smoke detectors placed beside supply diffusers or in beam pockets → Detectors relocated at pre-test; ceilings patched (caught by 28fa.rc.devices-vs-rcp; industry_practice)
- **28fa.fm.battery-undersized** — Battery calculations from the design-stage device count; strobes and speakers added during plan review → Batteries or power extenders added late; panels relocated (caught by 28fa.battery-calcs; industry_practice)
- **28fa.fm.end-of-line-voltage** — Voltage drop calculated at nominal voltage instead of the battery's end-of-discharge voltage → Appliances at circuit ends fail the battery test; circuits split (caught by 28fa.voltage-drop; industry_practice)
- **28fa.fm.duct-detector-gap** — Duct detectors furnished with the air handlers, but nobody carries mounting, wiring or the remote test station → Unwired detectors at the acceptance test (caught by 28fa.duct-detectors, if.23-duct-smoke-detectors; industry_practice)
- **28fa.fm.monitoring-not-live** — Monitoring lines or cellular communicator not live when the AHJ arrives for the acceptance test → Test rescheduled; occupancy delayed (caught by 28fa.monitoring-path, if.27-fire-alarm-communicator; industry_practice)
- **28fa.fm.dusty-detectors** — Smoke detectors installed and energized during drywall sanding and floor finishing to support early or phased occupancy → Trouble signals and false alarms; detectors cleaned or replaced across the floor before acceptance (caught by 28fa.detector-protection; industry_practice)
- **28fa.fm.existing-incompatible** — New devices added to an existing control unit that isn't listed for them or has no capacity left → Control unit replacement discovered during installation (caught by 28fa.existing-system; industry_practice)
- **edu.fm.missed-window** — Hardware, HVAC equipment or casework approved late and delivered after the summer window closes → Work moves into occupied classrooms after hours with temporary systems, or the phase slips a full year (caught by edu.summer-window; field_experience)
- **edu.fm.agency-change-unapproved** — A substitution or field change accepted by the architect is never submitted to the state school-construction agency → The agency withholds certification or closeout of the project; work is reopened or occupancy delayed (caught by edu.agency-approvals; industry_practice)

## Expected submittal contents
- **Shop Drawings**
  - Device layout on plans that show ceiling features (beams, soffits, diffusers, luminaires) and ceiling heights
  - Riser with every circuit, power extender and interface module
  - Sequence of operations matrix, every input against every output
  - Notification appliance settings (candela, speaker taps) and pathway class and survivability
  - Control unit, annunciator and communicator locations
- **Design Data**
  - Secondary power calculations for the control unit and every power extender
  - Voltage drop for every notification circuit, at the lowest voltage the listing allows
  - Speaker circuit loading, and intelligibility analysis where required
- **Product Data**
  - Every device and module, listed and compatible with the submitted control unit
- **Qualification Statements**
  - Designer and installer qualifications the spec or AHJ requires, and the seal where one is required
- **Test Reports**
  - Pre-test results, the acceptance test record and the record of completion

## Extract for reconciliation
- 28fa.xf.secondary-power — Battery capacity and calculated margin, per control unit and power extender (list, per package) → spec.part2
- 28fa.xf.matrix — Sequence matrix inputs and outputs (list, per package) → drawings.mechanical, schedule.door_hardware, drawings.fire_protection

## Standards to verify against
- NFPA 72: National Fire Alarm and Signaling Code
- UL 864: Control Units and Accessories for Fire Alarm Systems
- UL 2196: Fire Test for Circuit Integrity of Fire-Resistive Power, Instrumentation, Control and Data Cables

## Warnings
- Draft knowledge in use (global, 28, 28 46 00) — not yet PE-reviewed
