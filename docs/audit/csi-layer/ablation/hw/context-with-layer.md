# Compiled knowledge — 08 71 00 Door Hardware

Facility types: education.k12 · Confidence floor: **draft** · Review mode: per_element · Contractor-designed: never
Lineage: global → 08 → [08 70 00 missing] → 08 71 00
Overlays: education, education.k12

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Hardware sets for every opening, including electrified locking, exit devices, closers and holders, operators, seals and thresholds (08 71 13 power door operators inherit from here). At each door the hardware is where egress, fire rating, accessibility, security and the owner's operations meet: free egress without special knowledge, rated doors that close and latch, closers that open easily, locks on the owner's keying and access control standards. The submittal is reviewed opening by opening, and its electrified openings drive work by the frame fabricator, electrician, security contractor and fire alarm contractor that must be in the walls months before the hardware ships.

## Review checks (24)
### completeness
- **[critical] edu.storm-shelter** — Where the school has a storm shelter or safe room, every element of the shelter envelope (walls, roof deck and covering, doors with their frames and hardware, windows, louvers and penetrations) is submitted with evidence that it meets ICC 500 pressure and debris-impact testing as the tested assembly, and the shelter's ventilation, emergency lighting, toilets and power are shown. One standard door, louver or hardware substitution in the shelter boundary breaks the shelter.  
  Trace: drawings.life_safety, drawings.plans, spec.part2 · Owner: subcontractor · Scope: package · Gate: procurement_release · _overlay:education.k12_
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] d08.opening-trace** — Build the trace for every tagged opening before reviewing content: plan or elevation tag, schedule row, and the submittal item that answers it (door and frame by mark, window, storefront or curtain wall type, skylight, louver, glass type). List tags with no submittal entry and submittal entries with no tag; quantities come from the trace, never from the submitter's own count.  
  Trace: drawings.plans, drawings.exterior_elevations, schedule.door, schedule.window · Owner: subcontractor · Scope: package · _08_
- **[high] 08hw.keying** — A keying conference with the owner sets the keyway, hierarchy, construction keying and permanent or interchangeable cores, and any existing key system or patented keyway the owner controls, before cylinders are ordered; the keying schedule is approved by the owner as its own submittal.  
  Trace: spec.part1, spec.part2 · Owner: gc · Scope: package · Gate: procurement_release · _08 71 00_
- **[high] edu.agency-approvals** — Where a state school-construction agency has jurisdiction, deferred submittals, substitutions and field changes that touch structure, fire and life safety or accessibility are approved by that agency before fabrication, not only by the architect, and the agency's inspector and testing requirements are in the inspection program.  
  Trace: spec.division_01, register.special_inspections, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.products-marked** — Cut sheets covering a product family have the proposed model, size, options, finish and accessories clearly marked; unmarked sheets are returned.  
  Trace: spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data · _global_
### conformance
- **[critical (reflex)] 08hw.rated-function** — Every rated opening's set has a closer (or listed automatic closing), positive latching on every leaf (automatic or self-latching bolts on the inactive leaf of rated pairs, never manual bolts unless the listing and code allow them) and a coordinator where the astragal needs one, fire exit hardware rather than panic hardware where an exit device is used, no mechanical dogging or kick-down holders, the gasketing the label requires, and labeled protective plates where plates run higher than the fire door standard allows unlabeled. Hold-opens on rated doors release by the fire alarm or detection.  
  Trace: schedule.door_hardware, schedule.door, drawings.life_safety · Owner: subcontractor · Scope: element · _08 71 00_
- **[critical] 08hw.egress-hardware** — Every door in the means of egress opens from the egress side without a key, tool or special knowledge; panic or fire exit hardware is provided where the occupancy and occupant load require it; and any special locking (delayed egress, sensor release, controlled egress, elevator lobby or stair door locking with re-entry) is one the code allows for this occupancy, with its signage and release conditions.  
  Trace: drawings.life_safety, schedule.door_hardware · Owner: design_team · Scope: element · _08 71 00_
- **[high] g.current-documents** — The submittal reflects the current contract documents, including addenda, ASIs, bulletins and responded RFIs, not the bid set. Note the drawing revision the submitter worked from.  
  Trace: drawings.revision_blocks, register.asi_bulletin_log, register.rfi_log · Owner: gc · Scope: package · _global_
- **[high] g.basis-of-design** — Proposed manufacturer and model match the basis of design or a listed acceptable manufacturer. Anything else follows the comparable-product or substitution procedure Division 01 allows, with its timing and comparison data, before it is reviewed on its merits.  
  Trace: spec.part2_manufacturers, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] g.deviations-identified** — Every deviation from the contract documents is clouded or listed by the submitter. Compare independently; do not rely on the submitter's list.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _global_
- **[high] d08.labeled-assemblies** — Every rated opening (door, shutter, access door, fire window, rated storefront or glazed wall) is submitted as a listed assembly: frame, leaf, glazing, vision kit, louver, gasketing and hardware each fall within the listing that carries the label, and components from different manufacturers (a frame from one, a lite kit or louver from another) are confirmed as covered by it. Oversize openings and configurations outside the tested ones (transoms, sidelites, borrowed lites, pairs) say how they will be labeled or certified.  
  Trace: spec.part2, schedule.door, drawings.life_safety · Owner: subcontractor · Scope: package · _08_
- **[high] 08hw.accessible-operation** — Operable hardware on accessible doors works without tight grasping or twisting and sits within the reach range; closers can be set to the opening force and closing speed the hook requires; thresholds stay within the height and bevel limits; and where the force cannot be met (exterior doors, pressurized stairs, heavy doors) a power operator is in the set.  
  Trace: schedule.door_hardware, spec.part2 · Owner: subcontractor · Scope: element · _08 71 00_
- **[high] 08hw.owner-standards** — Locks, cylinders, electrified devices and credentials match the owner's hardware and access control standards where they exist (keyway, lock platform, reader technology and protocol); an alternate that changes the keyway or the access control platform is not an equal.  
  Trace: spec.part2_manufacturers, spec.part1 · Owner: gc · Scope: package · Gate: procurement_release · _08 71 00_
- **[high] 08hw.operators** — Door operators are low-energy or full-energy as the traffic requires, actuators sit outside the door swing and within reach, the electric lock releases before the operator drives, and operators on rated doors are listed for them and let the door close and latch on alarm.  
  Trace: schedule.door_hardware, drawings.plans, drawings.electrical · Owner: subcontractor · Scope: element · _08 71 00_
- **[high] edu.lockdown-hardware** — Classroom and other occupied-room doors lock from inside the room without opening the door, keep free egress, and can be unlocked from the corridor by key or credential, using the lock function the owner's security standard names. Add-on barricade devices that are not part of the listed door assembly are flagged: they can defeat egress, the fire door label and accessible operation.  
  Trace: schedule.door_hardware, spec.part2 · Owner: subcontractor · Scope: element · _overlay:education_
### coordination
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
- **[high] d08.sequence-of-operation** — Each electrified or motorized opening (electric locks and strikes, exit devices, operators, hold-opens, coiling and sectional door operators, automatic entrances, motorized vents) has a written sequence covering normal and after-hours operation, credential and request-to-exit behavior, fire alarm response and power loss, and the hardware, security, fire alarm and electrical submittals all describe the same sequence at that opening.  
  Trace: schedule.door_hardware, drawings.security, drawings.fire_alarm, drawings.electrical · Owner: gc · Scope: package · _08_
- **[high] edu.secure-vestibule** — The secure entry vestibule works as one system: exterior doors released by schedule or from the office, inner doors held until staff release them with sight of the visitor, a transaction window or pass-through, fire alarm release and egress from the vestibule. Door hardware, access control, storefront and glazing submittals are reviewed together, and any attack- or ballistic-resistant rating covers glass, frame and anchorage as tested, not the glass alone.  
  Trace: schedule.door_hardware, drawings.security, spec.part2 · Owner: gc · Scope: package · _overlay:education_
### constructability
- **[high] d08.field-modification** — Work on labeled doors, frames, shutters and rated glazing after fabrication (added hardware or access control, enlarged preps, re-trimming past the listed clearance, field-added lites or louvers, replacement glass, welding knock-down frames) is limited to what the listing and the fire door standard allow; anything else goes back to the manufacturer for field labeling or replacement. Hardware or security scope added after door and frame release is where this starts, so flag it at the change, not at the fire door inspection.  
  Trace: spec.part3, register.asi_bulletin_log, register.rfi_log · Owner: gc · Scope: package · _08_
- **[high] edu.summer-window** — Where work in existing schools must fit a break in the academic calendar, each submittal's approval, owner selections, mock-ups and delivery are dated against the day the window opens, not against a floating schedule activity. Long-lead items (door frames and hardware, HVAC equipment, switchgear, casework, flooring) that miss the window push work into occupied classrooms or a year later, so their submittals are released first.  
  Trace: schedule.master, spec.division_01 · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[medium] 08hw.power-supplies** — Power supplies are sized for the devices on them, including lock inrush and operators, sit in accessible conditioned rooms within the wire length the devices allow, have fire alarm release inputs where locks must release on alarm, and have battery backup where the security design calls for it.  
  Trace: drawings.electrical, drawings.security, spec.part2 · Owner: subcontractor · Scope: package · _08 71 00_

## Reconciliations — documents that must agree (4)
- **[critical (reflex)] d08.rc.rated-openings** — Every opening in a rated or smoke-resistant wall on the life safety plans has an opening protective in the door schedule with the rating that wall needs, and every rated door sits in a wall the life safety plans rate. Ratings copied from an earlier life safety plan, and walls upgraded after the schedule was written, show up here.  
  Between: drawings.life_safety ↔ schedule.door ↔ schedule.partition_type · Key: Opening in a rated wall, shaft, corridor or smoke barrier · Fields: wall rating, required opening rating, door and frame label, smoke and draft control, glazing rating · Owner: design_team · Gate: procurement_release · _08_
- **[high] 08hw.rc.sets-vs-schedule** — Every door mark on the plans and in the door schedule is in exactly one hardware set, every mark listed under a set exists on the plans, and each set suits the rating, material and hand of the doors assigned to it. Count the openings per set on both sides.  
  Between: schedule.door_hardware ↔ schedule.door ↔ drawings.plans · Key: Door mark · Fields: hardware set, openings per set, rating, hand, door and frame material, electrified · Owner: subcontractor · Gate: procurement_release · _08 71 00_
- **[high] 08hw.rc.electrified-openings** — The electrified openings in the hardware sets, on the security device plans and with power and conduit on the electrical drawings are the same list, with the same devices at each door. The hardware submittal usually arrives first and is the earliest chance to catch an opening the other drawings missed.  
  Between: schedule.door_hardware ↔ drawings.security ↔ drawings.electrical · Key: Door mark · Fields: electrified lock or strike, exit device type, reader, request-to-exit, position switch, operator, power supply, fail-safe or fail-secure · Owner: design_team · Gate: in_wall_rough_in · _08 71 00_
- **[high] 08hw.rc.fire-alarm-doors** — Every door the hardware sets expect to release, unlock or stop on alarm has a fire alarm connection (relay, holder circuit or detector) on the fire alarm drawings, and every door connection on the fire alarm drawings has the matching device in a hardware set.  
  Between: schedule.door_hardware ↔ drawings.fire_alarm ↔ drawings.life_safety · Key: Door mark · Fields: magnetic or closer holder, fail-safe lock, delayed egress, stair re-entry, operator shutdown, rolling fire door release · Owner: design_team · Gate: wall_close_in · _08 71 00_

## Compliance — regulatory hooks (10)
- **[critical] d08.rh.opening-protectives** (`opening-protective-ratings`) — What fire-protection rating, smoke and draft control, temperature-rise limit and glazing limits does the adopted code require for opening protectives (doors, shutters, access doors, fire windows and glazing) in each rated wall, shaft, corridor and smoke barrier type on the life safety plans, and which of them may be held open, released by what?  
  **Unbound** → Run /construction:code-researcher with research topic "opening-protective-ratings" (seed it with this hook's question)
- **[critical] 08hw.rh.panic-hardware** (`egress-door-panic-hardware`) — Which doors require panic or fire exit hardware under the adopted code (occupancy, occupant load, electrical and refrigeration machinery rooms), and where may it be omitted?  
  **Unbound** → Run /construction:code-researcher with research topic "egress-door-panic-hardware" (seed it with this hook's question)
- **[critical] 08hw.rh.locking-arrangements** (`electrically-locked-egress-doors`) — Which egress door locking arrangements does the adopted code permit for this occupancy (key-operated main entrance locks with signage, bolts on pairs, delayed egress, sensor release, controlled egress, elevator lobby doors, stairway doors with re-entry), and with what signage, release and fire alarm conditions?  
  **Unbound** → Run /construction:code-researcher with research topic "electrically-locked-egress-doors" (seed it with this hook's question)
- **[critical] edu.rh.storm-shelter** (`storm-shelter-requirements`) — Does the adopted building code require a storm shelter for this school (tornado design wind speed, occupant load), what capacity and location does it need, which ICC 500 edition governs, and what special inspection applies to the shelter?  
  **Unbound** → Run /construction:code-researcher with research topic "storm-shelter-requirements" (seed it with this hook's question)
- **[high] d08.rh.windborne-debris** (`windborne-debris-product-approval`) — Is the site in a wind-borne debris region that requires impact-resistant openings or opening protection, and does the jurisdiction require a state or local product approval for exterior doors, windows, storefronts, curtain walls, skylights or louvers?  
  **Unbound** → Run /construction:code-researcher with research topic "windborne-debris-product-approval" (seed it with this hook's question)
- **[high] d08.rh.energy-openings** (`energy-code-envelope`) — Under the adopted energy code and the compliance path the design uses, what U-factor, SHGC and visible transmittance apply to fenestration, what U-factor and air leakage apply to opaque and non-swinging doors, are entrance vestibules or air curtains required, and must the submitted values be certified whole-product ratings?  
  **Unbound** → Run /construction:code-researcher with research topic "energy-code-envelope" (seed it with this hook's question)
- **[high] 08hw.rh.accessible-operation** (`accessible-door-operation`) — What operable-parts, mounting height, opening force, closing speed and threshold requirements does the adopted accessibility standard set for doors on accessible routes, and does the adopted building code require power-operated doors at public entrances for this occupancy?  
  **Unbound** → Run /construction:code-researcher with research topic "accessible-door-operation" (seed it with this hook's question)
- **[high] 08hw.rh.fire-door-inspection** (`fire-door-assembly-inspection`) — Does the adopted fire code require an acceptance inspection of swinging fire door assemblies before occupancy and periodic inspection after, who may perform it, and to which standard and edition?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-door-assembly-inspection" (seed it with this hook's question)
- **[high] edu.rh.school-agency-review** (`school-construction-agency-review`) — Does a state agency other than the local building department review plans, approve changes or inspect construction for this school (common for public K-12 and in some states for community colleges), and what does it require for deferred submittals, change documents, testing laboratories and the inspector of record?  
  **Unbound** → Run /construction:code-researcher with research topic "school-construction-agency-review" (seed it with this hook's question)
- **[high] edu.rh.classroom-locking** (`classroom-door-locking`) — What do the adopted building and fire codes, and any state school-safety law, allow for locking classroom doors from inside, including supplemental barricade devices, and what egress, fire door and accessible-operation limits apply?  
  **Unbound** → Run /construction:code-researcher with research topic "classroom-door-locking" (seed it with this hook's question)

## Coordination routing (7)
- **[critical] if.08-electrified-openings** → Electrical raceway and wiring, access control and intrusion detection (26 05 19, 26 05 33, 28 10 00, 28 30 00) · Gate: wall_close_in — Openings and their devices are frozen at hardware approval; cable to the frame goes in before board
  - Send them: Each electrified opening's devices, voltage, load, fail-safe or fail-secure, power supply location and the frame and header boxes its wiring needs, issued before in-wall rough-in
  - Need from them: Circuits to power supplies and operators; conduit and boxes from each frame and header to an accessible ceiling, in place before the wall is closed; readers, request-to-exit and position switches where security furnishes them; the cable, terminations and programming
  - Confirm who: Lock power supplies — typical furnish 08 71 00 or 28 10 00 / install 08 71 00 or 28 10 00 / connect 26 05 00
  - Confirm who: Conduit and back boxes from frame to ceiling — typical furnish 26 05 00 or 28 10 00 / install 26 05 00 or 28 10 00
  - Confirm who: Door position switches and request-to-exit devices — typical furnish 08 71 00 or 28 10 00 / install 08 71 00 or 28 10 00
  - Confirm who: Cable from electrified hardware to the access control panel, termination and testing of each opening — typical install 28 10 00 or 26 05 00 / connect 28 10 00
  - If missed: Access control locks the door while the operator drives it, or the fire alarm opens a vestibule door the smoke strategy needs closed; Security contractor mobilizes after drywall with no conduit or cable to the frames
- **[critical] if.08-fire-alarm-doors** → Fire detection and alarm (28 46 00) · Gate: wall_close_in — Acceptance testing of every release follows at substantial completion
  - Send them: The doors that release, unlock, close or stop on alarm (hold-opens, fail-safe locks, delayed egress, stair re-entry, rolling fire doors and shutters, operators), with the input or contact each needs
  - Need from them: Release relays, holder circuits and detectors at each of those doors, programmed to the sequence, and acceptance testing with the door trades present
  - Confirm who: Magnetic door holders — typical furnish 08 71 00 or 28 46 00 / install 08 71 00 or 28 46 00 / connect 28 46 00
  - Confirm who: Detectors and release devices for rolling fire doors — typical furnish 08 33 00 or 28 46 00 / connect 28 46 00
  - If missed: Rated coiling door's release never tied to the fire alarm, or its operator holds the door open on alarm; The matrix lists outputs to air handlers, dampers or doors the other trades never wired for, or the mechanical sequence expects a fire alarm signal the matrix lacks
- **[high] if.08-doors-hardware** → Doors and frames (08 10 00) · Gate: procurement_release — Doors and frames are machined to the hardware; release them only against the approved sets
  - Send them: Approved hardware schedule and templates, including electrified items, power transfer method, concealed closers and holders, before doors and frames are released
  - Need from them: Door and frame material, core, rating and construction per mark, and the prep and reinforcement drawings returned for the hardware supplier's check
  - Confirm who: Hardware templates to the door and frame fabricators — typical furnish 08 71 00
  - Confirm who: Installing electrified hardware and the wire between frame and device — typical install 08 71 00 installer or the door installer / connect 28 10 00 or 26 05 00
  - If missed: Doors and frames released for fabrication before the hardware schedule was approved, or from an earlier revision of it
- **[high] if.08-door-airflow** → Air outlets and transfer grilles, testing and balancing, smoke-control fans (23 37 00, 23 05 93, 23 34 00) · Gate: procurement_release — Doors are premachined to an undercut and seals are bought by set
  - Send them: Undercut, door louvers, gasketing, door bottoms and closer sizes per opening
  - Need from them: Doors the air design relies on for transfer or return air, room pressure relationships, and stair and smoke-zone pressure differences that set door opening and closing forces
  - If missed: The air design returns air through door undercuts, but the doors are gasketed smoke or acoustic doors with seals and bottoms
- **[medium] if.03-floor-recesses** → Slabs and floor finishing (03 30 00, 03 35 00) · Gate: slab_pour
  - Send them: Approved recess sizes, locations and tolerances, and any drain, conduit or anchorage in the recess, before the pour; products that will be selected late are flagged so the recess is held open or deliberately omitted
  - Need from them: Blockouts and recesses formed at the pour to the approved product (floor closer and pivot boxes, sliding-door floor tracks and recessed thresholds, mobile shelving rails, cart-loading sterilizer pits), with the flatness the product needs around them
  - If missed: A product that sits in the slab (floor closer, sliding-door track, mobile shelving rail, cart-loading sterilizer) is selected after the pour, or its recess never reaches the concrete crew; Slab poured flat with no rail recess for a mobile system selected later
- **[medium] if.08-thresholds-flooring** → Flooring and tile (09 60 00, 09 30 00) · Gate: procurement_release — Thresholds are bought by set and doors premachined to an undercut, so floor thickness at each door must be known first
  - Send them: Threshold type, height, bevel and setting method at each door, and the undercut each door is machined to
  - Need from them: Finish and setting-bed thickness on each side of each door, where a change of level or material falls (under the door, at the threshold, at the frame face), and the transition or reducer at each one
  - Confirm who: Transition strips and reducers at doors — typical furnish 09 60 00, 09 30 00 or 08 71 00 / install 09 60 00 or 09 30 00
  - If missed: Floor finish changed (carpet to tile, added underlayment or walk-off mat) after doors were premachined to an undercut
- **[low] if.08-door-signage** → Signage (10 14 00) · Gate: in_wall_rough_in — Card reader and actuator boxes fix the latch-side wall before signs are made
  - Send them: Final hand and swing at each door, sidelites, borrowed lites and vision lites beside or in the door, latch-side wall devices the hardware sets bring (card readers, actuators, hold-open magnets), and which doors are rated
  - Need from them: Sign location and mounting at each door, confirmed against that door's final swing and latch-side devices before rough-in; signs kept off rated door leaves except as the fire door standard allows them to be attached
  - Confirm who: Field confirmation of sign locations at pairs, sidelites and doors with latch-side devices — typical install 10 14 00
  - If missed: Light switches or card readers roughed in on the latch-side wall where the room sign belongs; At double doors, sidelights and storefronts the sign is put on the door or the glass because no wall is available

## Failure modes to watch (22)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d08.fm.label-voided** — Access control or extra hardware added after rated doors and frames were fabricated, and the doors and frames were cut in the field to take it → Labels voided; doors replaced or field-relabeled before the fire door inspection (caught by d08.field-modification; field_experience)
- **d08.fm.rating-drift** — Door schedule ratings follow an earlier life safety plan; corridor, shaft or smoke barrier walls were added or upgraded later → Unrated doors and frames fabricated for rated openings, found at the fire door or final inspection (caught by d08.rc.rated-openings; field_experience)
- **d08.fm.mixed-listing** — Vision kit, louver or frame from another manufacturer installed in a rated door assembly the door's listing does not cover → Opening fails the fire door inspection; components replaced with listed ones (caught by d08.labeled-assemblies; industry_practice)
- **d08.fm.trades-disagree** — Hardware, access control and fire alarm each submitted their own idea of how an opening behaves on alarm, after hours and on power loss → Doors that lock when they must release (or the reverse) found at acceptance testing; devices swapped and rewired (caught by d08.sequence-of-operation; field_experience)
- **08hw.fm.rough-in-missed** — Access-controlled and electrified openings identified after walls were closed, with no conduit or box to the frame → Walls opened at each door, or surface raceway on finished frames; frames field-modified for preps (caught by 08hw.rc.electrified-openings, if.08-electrified-openings; field_experience)
- **08hw.fm.split-unassigned** — Nobody assigned to pull cable from the frame to the lock, terminate at the power supply, or test each electrified opening → Doors on temporary locking at turnover; change orders between electrical, security and the hardware supplier (caught by if.08-electrified-openings; field_experience)
- **08hw.fm.panic-on-fire-door** — Panic hardware with dogging, manual flush bolts or kick-down holders on rated doors → Openings fail the fire door inspection; devices replaced across the floor (caught by 08hw.rated-function; field_experience)
- **08hw.fm.locking-not-allowed** — Delayed egress, sensor-release or magnetic locks installed on egress doors where the occupancy or the arrangement does not permit them → Fails final inspection; locks replaced and access control redesigned at the end of the job (caught by 08hw.egress-hardware; industry_practice)
- **08hw.fm.keying-late** — Cylinders ordered before the keying conference, or keyed to a scheme the owner never approved → Cores recombinated or reordered; owner cannot secure the building at turnover (caught by 08hw.keying; field_experience)
- **08hw.fm.wrong-platform** — Locks, cores or readers approved on a platform outside the owner's standard → Owner refuses the hardware at turnover; replacement at the contractor's cost (caught by 08hw.owner-standards; field_experience)
- **08hw.fm.alarm-release-missing** — Fail-safe locks, hold-opens or delayed egress devices not tied to the fire alarm → Fails acceptance testing; relays and wiring added after ceilings close (caught by 08hw.rc.fire-alarm-doors, if.08-fire-alarm-doors; field_experience)
- **08hw.fm.stair-door-force** — Stair and vestibule door closers selected without the pressure difference the smoke-control system creates → Doors too heavy to open or that will not latch; closers and pressure settings reworked during acceptance testing (caught by if.08-door-airflow; field_experience)
- **08hw.fm.operator-fights-lock** — Operator and electric lock not interlocked, so the operator drives against a locked door → Burned-out operators and damaged strikes; the interlock added in the field (caught by 08hw.operators, d08.sequence-of-operation; field_experience)
- **edu.fm.missed-window** — Hardware, HVAC equipment or casework approved late and delivered after the summer window closes → Work moves into occupied classrooms after hours with temporary systems, or the phase slips a full year (caught by edu.summer-window; field_experience)
- **edu.fm.agency-change-unapproved** — A substitution or field change accepted by the architect is never submitted to the state school-construction agency → The agency withholds certification or closeout of the project; work is reopened or occupancy delayed (caught by edu.agency-approvals; industry_practice)
- **edu.fm.barricade-device** — Add-on classroom barricade devices bought by the owner or added to the hardware sets late → Fire door labels and egress compromised; devices removed at inspection or after an incident review (caught by edu.lockdown-hardware; industry_practice)
- **edu.fm.rated-glass-standard-frame** — Attack- or ballistic-resistant glazing submitted in a standard storefront frame with standard anchorage → The opening does not deliver the rating the owner paid for; frames and anchorage replaced (caught by edu.secure-vestibule; field_experience)
- **edu.fm.shelter-assembly-broken** — Shelter doors, frames, hardware or louvers submitted as standard products, or tested components mixed across manufacturers → The shelter boundary no longer matches a tested assembly; doors, frames or louvers replaced before occupancy (caught by edu.storm-shelter; industry_practice)

## Expected submittal contents
- **Schedule**
  - Hardware sets in the format the spec cites, each listing every door mark it applies to with hand, door and frame material, rating, and each item's function, finish and quantity
  - Electrified items flagged per opening, with voltage, fail-safe or fail-secure, and the devices furnished by others (reader, request-to-exit, position switch)
- **Shop Drawings**
  - Point-to-point wiring diagram and riser for each electrified opening type, with power supply location and fire alarm inputs
  - Elevation of each electrified opening type locating devices, power transfer and junction boxes
- **Schedule**
  - Keying schedule from the keying conference with keyway, hierarchy, construction keying and core type, signed off by the owner
- **Product Data**
  - Each product with its grade, function and finish marked, and the fire exit hardware, panic hardware and electrified listings claimed

## Extract for reconciliation
- 08hw.xf.set — Hardware set and the door marks assigned to it (list, per element) → schedule.door, drawings.plans
- 08hw.xf.electrified — Electrified devices, voltage and fail-safe or fail-secure per opening (list, per element) → drawings.security, drawings.electrical
- 08hw.xf.alarm-release — Devices that release or unlock on alarm (list, per element) → drawings.fire_alarm

## Standards to verify against
- NFPA 80: Standard for Fire Doors and Other Opening Protectives — Confirm the edition the adopted code references
- NFPA 105: Standard for Smoke Door Assemblies and Other Opening Protectives
- ANSI/BHMA A156.2 / ANSI/BHMA A156.13: Bored and Preassembled Locks and Latches; Mortise Locks and Latches
- ANSI/BHMA A156.3: Exit Devices
- UL 305: Panic Hardware
- ANSI/BHMA A156.4: Door Controls - Closers
- ANSI/BHMA A156.23 / A156.24 / A156.25 / A156.31: Electromagnetic Locks; Delayed Egress Locking Systems; Electrified Locking Devices; Electric Strikes and Frame Mounted Actuators
- ANSI/BHMA A156.15: Release Devices - Closer Holder, Electromagnetic and Electromechanical
- ANSI/BHMA A156.19: Power Assist and Low Energy Power Operated Doors
- ANSI/BHMA A156.28: Recommended Practices for Mechanical Keying Systems
- ANSI/BHMA A156.18: Materials and Finishes

## Suppressed
- d08.rh.safety-glazing (from 08) by 08 71 00 — Hardware carries no glass; glazing in and beside doors is reviewed under 08 10 00 and 08 80 00
- d08.rh.exterior-opening-protection (from 08) by 08 71 00 — Hardware does not change whether an exterior opening must be protected; reviewed with the doors and framing

## Warnings
- Draft knowledge in use (global, 08, 08 71 00) — not yet PE-reviewed
