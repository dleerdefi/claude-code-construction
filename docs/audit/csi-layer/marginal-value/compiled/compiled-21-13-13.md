# Compiled knowledge — 21 13 13 Fire-Suppression Sprinkler Systems

Facility types: education.k12 · Confidence floor: **draft** · Review mode: package · Contractor-designed: typical
Lineage: global → 21 → 21 10 00 → 21 13 00 → [21 13 13 missing]
Overlays: education, education.k12

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Wet, dry, preaction and deluge sprinkler systems (21 13 13 and the other system types inherit from here). A design is only as good as the hazard it was classified for: storage height, commodity and arrangement set the protection, not the room name. Beyond that the misses are coverage (concealed spaces, canopies, below wide ducts), areas that freeze, sprinkler types in finished and special spaces, and a head layout that has to fit a ceiling already crowded with lights, diffusers and detectors.

## Review checks (29)
### completeness
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] g.contractor-designed** — This scope is often performance-specified and designed or selected by the contractor. Confirm the spec's design criteria are complete enough to design to; whether the AHJ treats the design as a deferred submittal and when it must be filed relative to installation; and that the designer's assumptions about support, attachment and adjacent work are confirmed by the trades that provide them.  
  Trace: spec.part1, spec.part2 · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] d21.approvals-before-install** — The working plans and calculations carry every approval the project needs before fabrication: the engineer of record's review, the building or fire official's permit, and, where the owner's property insurer reviews fire protection, the insurer's acceptance with its comments incorporated. Insurer criteria can exceed the adopted standard (density, sprinkler type, storage protection), so a design approved only by the jurisdiction is not final.  
  Trace: spec.part1, spec.part1_submittals · Owner: gc · Scope: package · Gate: procurement_release · _21_
- **[high] d21.test-before-concealment** — Hydrostatic tests, and air tests of dry and preaction piping, are done and witnessed area by area before ceilings, shafts and soffits conceal the piping, with a signed material and test certificate for each area.  
  Trace: spec.part3, register.special_inspections · Owner: gc · Scope: package · Gate: above_ceiling_close_in · _21_
- **[high] edu.agency-approvals** — Where a state school-construction agency has jurisdiction, deferred submittals, substitutions and field changes that touch structure, fire and life safety or accessibility are approved by that agency before fabrication, not only by the architect, and the agency's inspector and testing requirements are in the inspection program.  
  Trace: spec.division_01, register.special_inspections, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.products-marked** — Cut sheets covering a product family have the proposed model, size, options, finish and accessories clearly marked; unmarked sheets are returned.  
  Trace: spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data · _global_
- **[medium] 21wb.test-discharges** — Every discharge the system needs for testing (main drain, inspector's test, auxiliary drains, backflow forward-flow test, standpipe drain riser) has a destination shown that can take full flow without flooding the building or the site: an exterior outlet with splash protection, or a drain the plumbing design sized for it.  
  Trace: drawings.fire_protection, drawings.plumbing, drawings.site · Owner: gc · Scope: package · Gate: underslab_rough_in · _21 10 00_
### conformance
- **[critical] 21wb.water-supply-test** — The calculations use a water supply test that meets the AHJ's and the purveyor's rules on age, location and witness, taken on the main that will actually feed the building, and the supply is reduced for the backflow assembly, meter, underground piping and any seasonal or system pressure drop the purveyor reports. The margin between supply and demand is at least what the spec requires.  
  Trace: spec.part1, drawings.civil, report.utility_requirements · Owner: subcontractor · Scope: package · Types: Design Data · Gate: procurement_release · _21 10 00_
- **[critical (reflex)] 21sp.hazard-commodity** — Each area's hazard or storage protection matches its real use: storage height, commodity class (including plastics and packaging), rack or solid-piled arrangement and aisle widths come from the owner's or tenant's stated use, not from the room name. Storage beyond what the design criteria cover needs storage-specific criteria (possibly in-rack sprinklers) and is a design-team question if the drawings are silent.  
  Trace: drawings.fire_protection, drawings.plans, spec.part2 · Owner: design_team · Scope: package · Gate: procurement_release · _21 13 00_
- **[high] g.current-documents** — The submittal reflects the current contract documents, including addenda, ASIs, bulletins and responded RFIs, not the bid set. Note the drawing revision the submitter worked from.  
  Trace: drawings.revision_blocks, register.asi_bulletin_log, register.rfi_log · Owner: gc · Scope: package · _global_
- **[high] g.basis-of-design** — Proposed manufacturer and model match the basis of design or a listed acceptable manufacturer. Anything else follows the comparable-product or substitution procedure Division 01 allows, with its timing and comparison data, before it is reviewed on its merits.  
  Trace: spec.part2_manufacturers, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] g.deviations-identified** — Every deviation from the contract documents is clouded or listed by the submitter. Compare independently; do not rely on the submitter's list.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _global_
- **[high] 21wb.design-basis** — The design method and criteria on the working plans match what the fire protection drawings and spec assign to each area, and every area that can govern is calculated, not just the obvious one: high and sloped ceilings, attics, exterior canopies, storage areas and the standpipe demand where it combines with sprinklers.  
  Trace: drawings.fire_protection, spec.part2 · Owner: subcontractor · Scope: package · Types: Shop Drawings, Design Data · _21 10 00_
- **[high] 21wb.backflow-assembly** — The fire service backflow assembly is the type the purveyor requires (double check or reduced pressure, with or without a detector meter), its friction loss is in the calculations, it can be forward-flow tested at system demand, and a reduced-pressure assembly's relief discharge has a drain or exterior outlet that can take it.  
  Trace: drawings.fire_protection, drawings.plumbing, drawings.civil · Owner: gc · Scope: package · Gate: procurement_release · _21 10 00_
- **[high] 21wb.component-pressure** — Where static pressure, fire pump churn or fire department pumping through the connection can exceed standard component ratings, the submittal shows high-pressure rated pipe, fittings, valves and sprinklers or pressure-reducing valves, and the riser diagram shows the pressure zones the design requires.  
  Trace: drawings.riser_diagrams, spec.part2 · Owner: subcontractor · Scope: package · _21 10 00_
- **[high] 21sp.head-selection** — Sprinkler type and temperature suit each area: quick response where the standard requires it; concealed or recessed heads where finished ceilings call for them, with factory-finished cover plates listed with that sprinkler model and its temperature rating; higher temperature ratings near heat sources (skylights, unit heaters, attics, cooking areas); corrosion-resistant heads in pools and chemical areas; and storage sprinklers used within their clearance and obstruction rules.  
  Trace: drawings.fire_protection, drawings.rcp, spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data, Shop Drawings, Samples · _21 13 00_
- **[high] 21sp.dry-preaction** — For dry pipe and preaction systems, system volume and water delivery time meet the standard by calculation or test; piping pitches to accessible low-point drains; the valve and its water supply sit in a space kept above freezing; the air or nitrogen supply and its power are shown; corrosion control matches the spec. For preaction systems, the release type (single or double interlock) matches the owner's intent and the fire alarm design.  
  Trace: drawings.fire_protection, spec.part2, drawings.fire_alarm · Owner: subcontractor · Scope: package · _21 13 00_
- **[high] 21sp.cpvc** — Where CPVC pipe is used, it stays within its listing (hazard, exposure, ceiling and plenum limits), and every product that will touch it (firestop, thread sealant, cable jackets, spray foam, cutting oil, paint) is on the pipe manufacturer's compatibility list.  
  Trace: spec.part2, spec.part3 · Owner: subcontractor · Scope: package · _21 13 00_
- **[high] edu.risk-category-delegated** — Delegated designs (cladding and curtain wall, roofing attachment, joists and trusses, nonstructural and equipment anchorage) state the risk category and importance factors they used, and these match the structural general notes; schools are often assigned above the default, and designers who assume the default under-design.  
  Trace: drawings.structural, spec.part1_submittals · Owner: subcontractor · Scope: package · _overlay:education_
### coordination
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
### constructability
- **[high] d21.existing-system-work** — Where new work extends or modifies an existing system, the existing piping, water supply and hazard are re-evaluated (new heads on an old system are calculated with the old pipe and a current supply), and each shutdown follows the owner's impairment procedure with notice to the fire department, the monitoring company and the insurer.  
  Trace: spec.part1, drawings.fire_protection, drawings.demolition · Owner: gc · Scope: package · _21_
- **[high] 21sp.obstructions** — The head layout accounts for obstructions to the spray pattern: ducts, cable tray and piping too wide to leave without heads beneath, beams and joists, light fixtures, soffits, overhead doors and equipment, and open-grid ceilings. Any duct or tray added or widened after the layout means added heads.  
  Trace: drawings.mechanical, drawings.electrical, drawings.rcp, drawings.fire_protection · Owner: gc · Scope: package · Gate: overhead_rough_in · _21 13 00_
- **[high] edu.summer-window** — Where work in existing schools must fit a break in the academic calendar, each submittal's approval, owner selections, mock-ups and delivery are dated against the day the window opens, not against a floating schedule activity. Long-lead items (door frames and hardware, HVAC equipment, switchgear, casework, flooring) that miss the window push work into occupied classrooms or a year later, so their submittals are released first.  
  Trace: schedule.master, spec.division_01 · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[medium] 21sp.finish-protection** — Sprinklers installed before painting, spray-applied finishes or fireproofing in the area are covered with the manufacturer's protective caps or bags, which come off before acceptance, and any sprinkler or cover plate that is painted, oversprayed or damaged is replaced, not cleaned or touched up.  
  Trace: spec.part3, schedule.master · Owner: gc · Scope: package · _21 13 00_
### absence
- **[high] 21sp.concealed-spaces** — Every concealed space, canopy and exterior projection is either protected or falls within an exemption the adopted standard grants for its construction (combustible or noncombustible, depth, insulation fill), and the construction above each ceiling type is identified.  
  Trace: drawings.building_sections, drawings.wall_sections, drawings.fire_protection · Owner: design_team · Scope: package · _21 13 00_
- **[high] 21sp.freezing** — Every area that can freeze (canopies, vestibules, loading docks, attics, unheated stairs, parking structures, freezers and coolers) has a protection method the adopted standard allows: a dry or preaction system, dry sprinklers long enough for the wall or ceiling they pass through, a listed antifreeze solution where still permitted, or heat; and the boundary of the wet system is shown.  
  Trace: drawings.fire_protection, drawings.mechanical, drawings.plans · Owner: design_team · Scope: package · _21 13 00_
- **[high] 21sp.cooking-hoods** — Commercial cooking hoods and their exhaust ducts are protected by a listed hood system or by sprinklers as the design intends, the party furnishing that protection is named, and the sprinkler design does not assume protection nobody provides.  
  Trace: drawings.foodservice, drawings.fire_protection, spec.part1 · Owner: gc · Scope: package · _21 13 00_

## Reconciliations — documents that must agree (5)
- **[high] d21.rc.supervised-devices** — Every control valve tamper switch, waterflow switch, low-air or low-pressure switch, fire pump signal and releasing panel output on the fire protection drawings has a matching monitored point on the fire alarm drawings, and the fire alarm drawings carry no device the fire protection design has since dropped.  
  Between: drawings.fire_protection ↔ drawings.fire_alarm · Key: Supervised device or signal (valve, flow switch, pressure switch, pump or release signal) · Fields: device type, location or zone, signal type (alarm, supervisory, trouble), monitoring module · Owner: design_team · Gate: above_ceiling_close_in · _21_
- **[high] 21wb.rc.fire-service** — The fire service size, entry point, backflow and meter location and control valve arrangement agree on the civil, plumbing and fire protection drawings and in the hydraulic calculations.  
  Between: drawings.civil ↔ drawings.fire_protection ↔ drawings.plumbing · Key: Fire service from the public main to the base of the riser · Fields: main size and material, point of connection, backflow and meter location, control valves (post indicator or wall valve), combined or separate from domestic · Owner: design_team · Gate: underslab_rough_in · _21 10 00_
- **[high] 21sp.rc.design-areas** — Hazard classifications and system types on the sprinkler drawings line up with the room uses on the current architectural and life safety plans; a use changed by ASI or tenant fit-out (office to storage, storage to server room) carries its new classification.  
  Between: drawings.fire_protection ↔ drawings.plans ↔ drawings.life_safety · Key: Room or area · Fields: use, hazard or commodity classification, ceiling height, system type · Owner: design_team · _21 13 00_
- **[medium] 21wb.rc.fdc** — The fire department connection is at the same location and of the same type on the site, elevation and fire protection drawings, and that location is the one the fire department accepted.  
  Between: drawings.civil ↔ drawings.exterior_elevations ↔ drawings.fire_protection · Key: Fire department connection · Fields: location on the building or site, coupling type, mounting height, distance to the hydrant, signage · Owner: design_team · _21 10 00_
- **[medium] 21sp.rc.rcp** — Heads on the sprinkler drawings fit the reflected ceiling plans: located in tiles as the architect requires, clear of lights, diffusers, speakers and detectors, and dropped to every soffit and ceiling height change the drawings show.  
  Between: drawings.rcp ↔ drawings.fire_protection · Key: Ceiling area or room · Fields: ceiling type and height, head location in the grid or tile, lights, diffusers, speakers and detectors, soffits and height changes · Owner: gc · Gate: overhead_rough_in · _21 13 00_

## Compliance — regulatory hooks (13)
- **[high] d21.rh.plan-approval** (`fire-suppression-plan-approval`) — Which authorities must approve fire suppression working plans and calculations before installation (building official, fire marshal, state fire marshal, water purveyor, and the owner's insurer where it reviews fire protection), what qualification must the designer hold (certification level, contractor license, engineer's seal), and must the approved set be kept on site?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-suppression-plan-approval" (seed it with this hook's question)
- **[high] d21.rh.supervision** (`fire-suppression-supervision`) — Which valves, waterflow devices and pump and system conditions must be electrically supervised and transmitted to a supervising station under the adopted fire code, and where are locks or seals allowed instead?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-suppression-supervision" (seed it with this hook's question)
- **[high] d21.rh.acceptance-testing** (`fire-suppression-acceptance-testing`) — Which acceptance tests must the AHJ witness (underground flush and hydrostatic test, aboveground hydrostatic test, trip tests, fire pump field test, alarm tests), which certificates must be filed, and must they be complete before the certificate of occupancy?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-suppression-acceptance-testing" (seed it with this hook's question)
- **[high] 21wb.rh.water-supply-test** (`fire-protection-water-supply-test`) — How recent must the water supply test behind the hydraulic calculations be, who must perform or witness it (purveyor, fire department), and what safety margin or supply reduction does the AHJ or purveyor require?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-protection-water-supply-test" (seed it with this hook's question)
- **[high] 21wb.rh.backflow** (`service-backflow-prevention`) — Which backflow assembly does the purveyor's cross-connection program require on the fire service (type, detector meter, location at the property line or inside the building), and who must test it at installation?  
  **Unbound** → Run /construction:code-researcher with research topic "service-backflow-prevention" (seed it with this hook's question)
- **[high] 21sp.rh.sprinkler-standard** (`sprinkler-standard-and-coverage`) — Which sprinkler standard does the building code require for this occupancy and height (NFPA 13, 13R or 13D), and which spaces (concealed spaces, balconies, attics, closets, elevator spaces) may be left unsprinklered under that standard and edition?  
  **Unbound** → Run /construction:code-researcher with research topic "sprinkler-standard-and-coverage" (seed it with this hook's question)
- **[high] 21sp.rh.high-piled** (`high-piled-combustible-storage`) — Does the planned storage (height, commodity, arrangement) make this high-piled combustible storage under the fire code, and what permit, sprinkler design, smoke removal, access doors and fire department access does that bring?  
  **Unbound** → Run /construction:code-researcher with research topic "high-piled-combustible-storage" (seed it with this hook's question)
- **[high] 21sp.rh.elevator** (`elevator-sprinklers-shunt-trip`) — Does the adopted code require or allow omitting sprinklers in elevator machine rooms, control spaces, hoistways and pits, and where they are installed, what sprinkler temperature rating and shunt-trip arrangement go with them?  
  **Unbound** → Run /construction:code-researcher with research topic "elevator-sprinklers-shunt-trip" (seed it with this hook's question)
- **[high] edu.rh.school-agency-review** (`school-construction-agency-review`) — Does a state agency other than the local building department review plans, approve changes or inspect construction for this school (common for public K-12 and in some states for community colleges), and what does it require for deferred submittals, change documents, testing laboratories and the inspector of record?  
  **Unbound** → Run /construction:code-researcher with research topic "school-construction-agency-review" (seed it with this hook's question)
- **[high] edu.rh.risk-category** (`building-risk-category-assignment`) — What risk category applies to this building under the adopted code (occupant load, designation as an emergency or community shelter), and which design loads, nonstructural anchorage and special inspections change because of it?  
  **Unbound** → Run /construction:code-researcher with research topic "building-risk-category-assignment" (seed it with this hook's question)
- **[medium] d21.rh.impairment** (`fire-protection-impairment-procedures`) — When an existing sprinkler or standpipe system is shut down for tie-ins, what notice, fire watch and restoration steps do the fire code and the fire department require?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-protection-impairment-procedures" (seed it with this hook's question)
- **[medium] 21wb.rh.fdc** (`fire-department-connection-requirements`) — What does the fire department require for the fire department connection: location relative to the hydrant and the address side, coupling type, height, signage, and whether a remote or freestanding connection is acceptable?  
  **Unbound** → Run /construction:code-researcher with research topic "fire-department-connection-requirements" (seed it with this hook's question)
- **[medium] 21sp.rh.freeze** (`sprinkler-freeze-protection`) — Which freeze protection methods does the adopted sprinkler standard allow (listed antifreeze solutions, dry sprinklers, dry or preaction systems, listed heat tracing), and do the AHJ or the insurer restrict antifreeze further?  
  **Unbound** → Run /construction:code-researcher with research topic "sprinkler-freeze-protection" (seed it with this hook's question)

## Coordination routing (31)
- **[critical] if.01-integrated-life-safety-testing** → Commissioning (integrated testing) (01 91 00) · Gate: substantial_completion
  - Send them: Each system tested and accepted on its own first; interface relays and devices installed, programmed to the matrix and labeled
  - Need from them: One integrated test plan, the input-output sequence matrix, and a test date with the AHJ
  - If missed: Fire alarm, elevator, damper and smoke-control interfaces are first tested together at the AHJ's final inspection
- **[critical] if.13-shielding-penetrations** → Radiation and RF shielding (13 49 00) · Gate: wall_close_in
  - Send them: Box and penetration locations in shielded walls ahead of framing, and services routed to the waveguides and filters rather than through the shield
  - Need from them: Shielding requirement per barrier, lead backing, sleeve and baffle details at boxes, ducts and pipes, and waveguide and filter locations at MRI enclosures
  - Confirm who: Lead backing at boxes and penetrations in shielded walls — typical furnish 13 49 00 / install 13 49 00 or the penetrating trade
  - Confirm who: Waveguides and filters at MRI RF enclosures — typical furnish 13 49 00 / install 13 49 00 / connect the trade bringing each service
  - If missed: Electrical boxes, recessed cabinets or duct openings cut through lead-lined walls without backing; A trade penetrates the MRI RF shield directly instead of through a waveguide or filter
- **[critical] if.14-elevator-sprinkler-shunt-trip** → Elevators (14 20 00) · Gate: overhead_rough_in
  - Send them: Sprinklers where required, a heat detector beside each sprinkler that the elevator code ties to shunt trip, a shunt-trip disconnect that opens before water flows, and monitoring of its control power
  - Need from them: Hoistway, pit and machine room or control space locations, and the mainline disconnect location and rating
  - Confirm who: Shunt-trip mainline disconnect — typical furnish 26 28 16 / install Division 26
  - Confirm who: Heat detectors and shunt-trip control relay — typical furnish 28 46 00 / install 28 46 00
  - If missed: Sprinklers installed in the hoistway or machine room without shunt trip and heat detectors
- **[high] if.01-cutting-patching-mep** → Cutting and patching (01 73 00) · Gate: wall_close_in — Openings planned before close-in avoid cutting finished work
  - Send them: Openings needed in existing or finished construction, located and sized before cutting, and kept within what the patch and firestop system allow
  - Need from them: Who cuts, who patches the substrate, who finishes the patch, and the standard the patch must meet
  - Confirm who: Patching and refinishing openings the MEP trades cut in finished walls and ceilings — typical install 01 73 00 (general contractor) or the cutting trade
  - If missed: An MEP trade cuts finished gypsum board and ceilings for late work and leaves the opening
- **[high] if.03-sleeves** → Cast-in-place and post-tensioned concrete (03 30 00, 03 23 00) · Gate: slab_pour
  - Send them: One coordinated sleeve layout across trades, sized for insulation and the firestop system's annular space, with sleeve types (waterstop collars below grade and in wet areas, cast-in firestop devices in rated floors), delivered before forms close
  - Need from them: Sleeve and blockout locations surveyed before the pour, and the engineer's acceptance of penetrations through beams, footings, grade beams and post-tensioned slabs
  - Confirm who: Sleeves and cast-in firestop devices — typical furnish each penetrating trade / install each penetrating trade or 03 30 00
  - If missed: A sleeve or floor drain arrives after the tendon layout is approved and is placed by pushing tendons aside; Anchor rods, embeds or sleeves not in the forms at the pour because the trade's shop drawings were not approved or never reached the concrete crew; Plumbing sleeves missed at the slab pour, then cored through a post-tensioned slab
- **[high] if.03-precast-mep-cast-in** → Precast and tilt-up concrete (03 40 00) · Gate: procurement_release — Openings and cast-in items are fixed when each piece is cast; anything added later is cored or surface-mounted, and coring a prestressed piece needs the precaster's engineer
  - Send them: A coordinated layout of floor and roof drains, toilet and shower drains, risers, duct and louver openings, and boxes and conduit cast into panels, with sizes, before the piece or panel drawings are released for casting
  - Need from them: The zones where openings and cores are allowed in each prestressed piece (between strands, through hollow cores, away from bearing), and the casting date by which every opening, sleeve, box and conduit stub must be on the piece or panel drawings
  - If missed: An embed or opening for another trade left off a piece cast before that trade's submittal was approved; An opening cored through a plank or tee in the field, cutting strands; Joist seats, canopy embeds or electrical boxes left out of a panel
- **[high] if.05-sprinkler-main-loads** → Joists and structural steel (05 21 00, 05 12 00) · Gate: procurement_release — The sprinkler layout is often drawn after the joists are ordered
  - Send them: Routing, size and water-filled weight of mains and feed lines, with hanger locations, early enough to reach the joist design
  - Need from them: Where large mains may hang and the loads the joist design carries for them
  - If missed: Rooftop units, hung air handlers, unit heaters, fire-protection mains or solar racks never given to the joist manufacturer as loads
- **[high] if.06-truss-mep-loads** → Shop-fabricated wood trusses (06 17 53) · Gate: procurement_release — Release truss designs after the equipment submittals they carry are approved
  - Send them: Equipment operating weights and locations, platforms and hangers, duct and sprinkler mains routed through or hung from the trusses, and attic access needs
  - Need from them: Truss layout, depth and web openings, and the concentrated and hanging loads each design carries
  - If missed: Trusses designed for uniform loads only; a rooftop unit, solar array or sprinkler main added later
- **[high] if.firestop-mep-penetrations** → Firestopping (07 84 00) · Gate: procurement_release — Settle the installer and the system matrix before rough-in starts
  - Send them: Penetrant types, materials, sizes and insulation through each rated assembly; openings sized within system limits
  - Need from them: Listed system per penetrant and assembly, with annular space and opening limits
  - Confirm who: Firestopping of MEP penetrations through rated assemblies — typical furnish 07 84 00 / install 07 84 00 or each penetrating trade
  - If missed: Each MEP trade firestops its own penetrations with its own products; Boxes set back to back in rated or acoustically rated walls without the listed protection or offset
- **[high] if.waterproofing-utility-entries** → Below-grade waterproofing (07 10 00) · Gate: foundation_pour
  - Send them: Entry locations, sleeve sizes and seal products, set before the pour
  - Need from them: Membrane-compatible sleeve and seal details for every below-grade entry
  - If missed: Unsealed or incompatible seals at service entries; leaks at each one
- **[high] if.08-sprinklered-glazing** → Glazing and glazed framing (08 80 00, 08 40 00) · Gate: procurement_release
  - Send them: Sprinklers listed for protecting glazing, at the spacing and distance from the glass their listing requires, on the sides required
  - Need from them: Where the design protects ordinary glazing with sprinklers instead of fire-rated glazing, glass type and size, and framing and window treatments kept out of the zone between sprinklers and glass
  - If missed: Blinds, deep mullions or a different glass type installed where sprinklers protect the glazing; the protection no longer matches its listing
- **[high] if.08-overhead-door-clearances** → Coiling and sectional doors (08 33 00, 08 36 00) · Gate: overhead_rough_in
  - Send them: Routing kept out of that envelope, and sprinkler coverage below open doors and tracks where the sprinkler standard treats them as obstructions
  - Need from them: Hood, guide, track, spring and operator envelope in section at each door, with the door both open and closed
  - If missed: Ductwork, sprinkler mains or lights installed in the zone the coil hood and operator need; High-lift or horizontal track drawn only in elevation; unit heaters, lights or sprinkler lines installed in its path
- **[high] if.08-access-doors-mep** → Access doors and panels (08 31 00) · Gate: above_ceiling_close_in
  - Send them: Location and required size of every concealed device that needs service, taken from approved MEP submittals; framed openings in board walls and ceilings
  - Need from them: Door sizes, ratings and frame types for each substrate
  - Confirm who: Furnishing access doors for MEP devices — typical furnish 08 31 00 or each MEP trade / install 09 21 00
  - If missed: Valves, dampers or terminal units above hard ceilings or inside chases with no access door; Dampers, valves or terminal units above a gypsum ceiling with no access door
- **[high] if.09-ceiling-sprinklers** → Suspended and gypsum board ceilings (09 50 00, 09 21 16) · Gate: overhead_rough_in — Branch lines and drops follow the coordinated RCP, not a grid assumed on the sprinkler shop drawings
  - Send them: Head locations set to that layout, drop type and length, flexible drops or oversized escutcheons where the seismic design requires them, and heads finished only after grid or board is fixed
  - Need from them: Coordinated ceiling layout (module, datum, heights, clouds, soffits and bulkheads) and the clearance the ceiling's seismic design needs around each head
  - Confirm who: Final head position and drop length to the finished ceiling — typical install 21 13 00
  - If missed: Sprinkler drops cut and installed before the ceiling layout was coordinated; Braced ceiling installed around sprinkler heads on rigid drops with no clearance
- **[high] if.09-ceiling-service-access** → Suspended and specialty ceilings (09 50 00) · Gate: above_ceiling_close_in — Check access on the coordinated RCP before the grid is filled, not at the damper inspection
  - Send them: Service points placed over removable panels and clear of fixtures, ducts, mains and bulkheads, with the clearance each needs for its actuator, filter or coil to come out
  - Need from them: Ceiling type and layout at each service point, which panels are removable, and where fixed bulkheads, clouds or monolithic areas need access doors instead
  - If missed: Terminal unit, damper or valve located over a light fixture, duct or fixed bulkhead
- **[high] if.10-cubicle-track-sprinklers** → Cubicle curtain track (10 21 23) · Gate: above_ceiling_close_in
  - Send them: Sprinkler positions for each curtained area with the clearances the curtains need
  - Need from them: Track layout and curtain extents in each room
  - If missed: Track laid out without the sprinkler and lighting plans; heads and fixtures end up in the curtain path
- **[high] if.10-storage-sprinklers** → Shelving and storage racks (10 56 00) · Gate: procurement_release — Storage heights fix the sprinkler design
  - Send them: Sprinkler design for the storage arrangement, deflector clearance to the top of storage, and in-rack sprinklers where required
  - Need from them: Unit and rack heights, top-of-storage elevation, solid or open shelves, carriage layout and flue spaces
  - If missed: Shelving or racks taller than the sprinkler design assumed, or solid shelves where open ones were assumed
- **[high] if.11-walk-in-sprinklers** → Walk-in coolers and freezers (11 41 00) · Gate: above_ceiling_close_in
  - Send them: Heads inside each box where required (dry type in freezers) and above the box, located before panels are cut
  - Need from them: Box dimensions, ceiling panel construction, which boxes are freezers, and penetration details
  - Confirm who: Sealing sprinkler penetrations through walk-in panels — typical install 11 41 00 or 21 13 00
  - If missed: Sprinklers omitted inside the box, or standard wet heads used inside a freezer
- **[high] if.11-stage-fly-space** → Stage rigging (11 61 00) · Gate: overhead_rough_in
  - Send them: Routing that stays outside those envelopes, and sprinkler coverage that battens do not obstruct
  - Need from them: Batten travel envelopes, loft wells, curtain tracks and hoist locations
  - If missed: Sprinkler mains, ducts or conduit routed through batten travel or loft wells
- **[high] if.11-stage-fire-curtain** → Stage equipment (fire curtain and smoke vents, where provided) (11 61 00) · Gate: procurement_release
  - Send them: Detection and release signals, deluge or water curtain piping where used, and monitoring
  - Need from them: Fire curtain or water curtain release devices and stage smoke vent operators, with their release and reset requirements
  - If missed: Fire curtain or stage vents installed with no release signal from detection; fails the fire authority's acceptance test
- **[high] if.13-metal-building-hung-loads** → Metal building systems (13 34 19) · Gate: procurement_release — Hung loads have to reach the manufacturer before its design is sealed
  - Send them: Weights and hanging locations of mains, ducts, unit heaters, lights and rooftop units, before the metal building design is final
  - Need from them: Collateral and auxiliary loads designed for, allowable hanging points and attachment methods on purlins and frames, and framed openings and supports for rooftop units
  - If missed: Sprinkler mains, unit heaters or rooftop units added or relocated beyond the collateral load, or hung from purlins without the manufacturer's acceptance
- **[high] if.13-controlled-room-sprinklers** → Controlled environment rooms (13 21 00) · Gate: above_ceiling_close_in
  - Send them: Sprinkler protection inside the room (dry, preaction or antifreeze where it freezes), penetration locations, and sealed escutcheons in clean rooms
  - Need from them: Room ceiling layout and height, interior temperature, and the panel sealing method for sprinkler penetrations
  - If missed: The room's ceiling blocks the building sprinklers and no protection is designed inside the room
- **[high] if.13-isolation-crossings** → Sound and vibration isolation (13 48 00) · Gate: above_ceiling_close_in
  - Send them: Flexible connections, resilient hangers and sleeves at every crossing of isolated floors, walls and ceilings
  - Need from them: Isolation lines and the flexible or resilient connection each crossing needs
  - If missed: A rigid conduit, pipe, sprinkler drop or screw bridges the isolation
- **[high] if.14-escalator-openings** → Escalators and moving walks (14 30 00) · Gate: overhead_rough_in
  - Send them: Closely spaced sprinklers and the draft curtain arrangement where the code uses that protection method
  - Need from them: Floor opening outline, truss enclosure and the ceiling conditions around the wellway
  - Confirm who: Draft curtain around the floor opening — typical furnish Division 14 or the architectural trades / install Division 14 or the architectural trades
  - If missed: Escalator opening left without enclosure or the sprinkler and draft curtain arrangement
- **[high] if.21-fire-service-underground** → Site water utilities (fire service main) (33 10 00) · Gate: trench_backfill — The underground is flushed at full flow and tested before it is connected to the riser
  - Send them: Flow and pressure needed at the base of the riser, the riser and backflow location, and the point where the aboveground contractor takes over
  - Need from them: Fire main size, material and route, thrust restraint, hydrant and post indicator valve locations, the flush and hydrostatic test certificate for the underground, and the hydrant flow test (date, location, witness) the calculations are based on
  - Inspect before: Thrust restraint inspected and hydrostatic test witnessed as the AHJ requires
  - Confirm who: Fire service from the site point of connection to the riser flange inside the building — typical furnish 33 14 00 or 21 10 00 / install 33 14 00 or 21 10 00
  - If missed: Sprinklers designed on an old or remote flow test, and the actual supply is lower; Fire service connected to the riser without the flush
- **[high] if.21-water-entry** → Domestic water distribution (22 11 00) · Gate: underslab_rough_in — The entry location and the room drain are fixed with the underslab work
  - Send them: Fire service size, backflow assembly type and location, and the room it needs at the entry
  - Need from them: Whether the service is combined or separate, the split point, domestic meter and backflow locations, and the room drain for relief discharges
  - Confirm who: Backflow assembly on the fire service — typical furnish 21 10 00 or 22 11 00 / install 21 10 00 or 22 11 00
  - If missed: The two trades draw the split, meter and backflow assemblies differently; the entry room is too small or has no drain for relief discharge
- **[high] if.21-duct-obstructions** → HVAC ductwork (23 31 00) · Gate: overhead_rough_in — Settle ducts and sprinklers in one coordination layout before either is hung
  - Send them: Main, branch line and head routing and elevations, and heads needed below ducts wide enough to obstruct the spray
  - Need from them: Duct sizes and elevations in the coordinated ceiling layout, and any later change in duct width or height
- **[high] if.21-supervision** → Fire detection and alarm (28 46 00) · Gate: above_ceiling_close_in — Modules and wiring at devices above ceilings go in before the ceiling closes
  - Send them: The list and location of every supervised device and signal (tamper, waterflow, low air, pump running, power and phase failure, releasing panel outputs)
  - Need from them: A monitored point and module for each, programmed as alarm, supervisory or trouble, and power to the devices that need it
  - Confirm who: Tamper, flow and pressure switches — typical furnish 21 10 00 / install 21 10 00 / connect 28 46 00
- **[high] if.21-release-control** → Fire detection and alarm (28 46 00) · Gate: procurement_release — The panel and the valve actuators must be listed together
  - Send them: Release valve or actuator models, the releasing panels they are listed with, and the release logic (single or double interlock, cross-zoned detection, time delay and abort)
  - Need from them: Detection layout and zoning for release, the releasing panel or its interface, and the alarm and shutdown outputs
  - Confirm who: Releasing control panel and its detection — typical furnish 21 13 00, 21 22 00 or 28 46 00 / install 21 13 00, 21 22 00 or 28 46 00
  - If missed: The releasing panel and the agent valve actuators are not listed together
- **[medium] if.12-shade-pockets-sprinklers** → Window treatments (12 20 00) · Gate: above_ceiling_close_in
  - Send them: Sprinkler positions relative to the pockets, and sprinklers inside pockets where the pocket would obstruct discharge
  - Need from them: Pocket, fascia and drapery track locations, widths and depths along each window wall
  - If missed: A deep shade pocket next to the window wall obstructs sprinkler discharge
- **[medium] if.21-drain-discharge** → Sanitary and storm drainage (22 13 00, 22 14 00) · Gate: underslab_rough_in
  - Send them: Each test and drain discharge (main drain, inspector's test, auxiliary drains, backflow forward-flow test, pump test, relief and casing discharge) with its location and full flow
  - Need from them: Receptors and drains sized for those flows, or an exterior discharge point agreed with the site design
  - Confirm who: Receptors for fire protection test and relief discharges — typical furnish 22 13 00 / install 22 13 00
  - If missed: Test header discharge aimed at landscaping, a sidewalk or a drain far too small for it

## Failure modes to watch (30)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d21.fm.insurer-late** — The owner's insurer reviews the sprinkler design after the jurisdiction approved it and requires a different density, sprinkler or storage protection → Redesign after fabrication; piping and heads changed in installed areas (caught by d21.approvals-before-install; industry_practice)
- **d21.fm.covered-untested** — Ceilings or soffits close over sprinkler piping before the hydrostatic test is witnessed → Ceilings opened for the inspector; leaks found after finishes are in (caught by d21.test-before-concealment; industry_practice)
- **d21.fm.unsupervised-devices** — Tamper and flow switches installed by the sprinkler contractor never reached the fire alarm design, or were added in the field without modules → Final acceptance fails; occupancy waits on fire alarm additions and reprogramming (caught by d21.rc.supervised-devices, if.21-supervision; industry_practice)
- **d21.fm.old-system-overloaded** — Renovation heads tied into an existing system without a calculation against the current supply and the existing pipe → The system fails plan review late, or underperforms unnoticed; mains replaced (caught by d21.existing-system-work; industry_practice)
- **21wb.fm.stale-test** — Calculations based on an old flow test, or one taken on a different main than the one serving the building → The margin disappears when the purveyor's current data arrive; a fire pump or larger pipe is added after installation (caught by 21wb.water-supply-test; industry_practice)
- **21wb.fm.backflow-loss-omitted** — The purveyor requires a backflow assembly late in design, or its loss is left out of the calculations → Demand exceeds supply at acceptance; mains resized or a pump added (caught by 21wb.water-supply-test, 21wb.backflow-assembly; industry_practice)
- **21wb.fm.remote-area-skipped** — Only the obvious remote area calculated; a high-ceiling, attic or canopy area with higher demand left out → Plan review rejection, or a system that cannot meet demand where it matters most (caught by 21wb.design-basis; industry_practice)
- **21wb.fm.fdc-rejected** — Fire department connection located or specified without the fire department's review → Relocated or adapted after the facade or site work is finished (caught by 21wb.rc.fdc; industry_practice)
- **21wb.fm.overpressure** — Components rated below the pressure that pump churn or fire department pumping can produce → Failed hydrostatic test or replaced components; pressure-reducing valves added late (caught by 21wb.component-pressure; industry_practice)
- **21wb.fm.test-water** — Inspector's test, main drain or forward-flow test discharge shown nowhere, or into a floor drain far too small for it → Acceptance tests cannot be run, or flood finished rooms when they are (caught by 21wb.test-discharges, if.21-drain-discharge; industry_practice)
- **21wb.fm.underground-debris** — The fire service underground is connected to the riser before it is flushed → Debris lodges in valves and sprinklers; heads replaced and the system flushed again (caught by if.21-fire-service-underground; industry_practice)
- **21sp.fm.storage-misclassified** — A stockroom or warehouse designed as ordinary hazard; the tenant stores high-piled plastics or racks above the design height → Protection is inadequate; in-rack sprinklers, larger mains or a fire pump added after occupancy, or storage limits imposed on the owner (caught by 21sp.hazard-commodity, 21sp.rc.design-areas; industry_practice)
- **21sp.fm.duct-shadow** — Wide ducts or cable tray installed below the sprinkler branch lines after the layout was set → Heads added below obstructions after ceilings are framed, or a failed above-ceiling inspection (caught by 21sp.obstructions, if.21-duct-obstructions; industry_practice)
- **21sp.fm.concealed-unprotected** — A combustible concealed space or exterior canopy left without sprinklers on the assumption it was exempt → AHJ final inspection finding; heads added through finished soffits (caught by 21sp.concealed-spaces; industry_practice)
- **21sp.fm.frozen-branch** — Wet pipe extended into a canopy, vestibule or loading dock that drops below freezing → Burst pipe and water damage in the first cold snap (caught by 21sp.freezing; industry_practice)
- **21sp.fm.cover-plates** — Sprinklers or concealed cover plates painted or oversprayed during finishes, or cover plates mixed between sprinkler models and temperature ratings they are not listed with → Heads and plates replaced at final inspection (caught by 21sp.finish-protection, 21sp.head-selection; industry_practice)
- **21sp.fm.cpvc-attack** — Incompatible firestop, sealant, cable or foam in contact with CPVC sprinkler pipe → Stress cracking and leaks months after occupancy, above finished ceilings (caught by 21sp.cpvc; industry_practice)
- **21sp.fm.delivery-time** — A dry system enlarged in the field without re-checking water delivery time → The trip test fails at acceptance; the system is split or an accelerator added (caught by 21sp.dry-preaction; industry_practice)
- **21sp.fm.trapped-water** — Dry or preaction piping with trapped sections and no low-point drains → Internal corrosion and pinhole leaks, or trapped water that freezes (caught by 21sp.dry-preaction; industry_practice)
- **21sp.fm.valve-room-unheated** — A dry pipe or preaction valve set in the unheated garage, dock or canopy area its piping protects → The valve trim and its water supply freeze; the system is impaired until the valve is enclosed and heated (caught by 21sp.dry-preaction; industry_practice)
- **21sp.fm.elevator-heads** — Sprinklers installed in an elevator machine room or hoistway without the heat detector and shunt trip that must accompany them → Elevator acceptance fails, or water reaches energized elevator equipment (caught by if.14-elevator-sprinkler-shunt-trip; industry_practice)
- **21sp.fm.hood-unassigned** — Cooking hood suppression assumed by the sprinkler contractor and the hood supplier each to be the other's → The kitchen cannot open; the system is bought and installed at the end (caught by 21sp.cooking-hoods; industry_practice)
- **21sp.fm.heads-vs-ceiling** — Drops cut before the ceiling layout is final → Arm-overs added at every conflict with lights and diffusers; tiles recut (caught by 21sp.rc.rcp; industry_practice)
- **edu.fm.missed-window** — Hardware, HVAC equipment or casework approved late and delivered after the summer window closes → Work moves into occupied classrooms after hours with temporary systems, or the phase slips a full year (caught by edu.summer-window; field_experience)
- **edu.fm.agency-change-unapproved** — A substitution or field change accepted by the architect is never submitted to the state school-construction agency → The agency withholds certification or closeout of the project; work is reopened or occupancy delayed (caught by edu.agency-approvals; industry_practice)
- **edu.fm.default-risk-category** — Delegated cladding, joist or anchorage design done to the default risk category on a school assigned a higher one → Components under-designed; recalculation and field reinforcement after installation (caught by edu.risk-category-delegated; industry_practice)

## Expected submittal contents
- **Shop Drawings**
  - Design criteria for each area on the drawings (hazard or commodity, density and area or other method, hose allowance, system type)
  - The water supply test used (date, time, location, static and residual pressure, flow, and who witnessed it)
  - Fire service entry, backflow assembly, control valves, fire department connection, drains and test connections, with where each discharges
- **Design Data**
  - Hydraulic calculations for every remote area the design criteria create, with a supply curve showing demand, margin and every loss between the test point and the base of the riser
- **Product Data**
  - Each valve, backflow assembly, flow switch, pipe and fitting with its listing and pressure rating marked
- **Qualification Statements**
  - The designer's certification, license or seal the spec and jurisdiction require
- **Certificates**
  - Material and test certificates for underground and aboveground piping, signed by the witness
- **Shop Drawings**
  - Head layout per area with sprinkler type, temperature rating, response, K-factor and finish by symbol, drawn over the reflected ceiling plan with ceiling heights
  - Obstructions considered (ducts, beams, lights, cable tray, overhead doors) and the heads added below them
  - Protection of concealed spaces, canopies, overhangs, stairs and elevator spaces, or the exemption relied on for each
  - Inspector's test and drains, and for dry or preaction systems the air or nitrogen supply and every low-point drain
- **Product Data**
  - Each sprinkler by model and identification number, with listing, K-factor, response, temperature, finish and escutcheon or cover plate
  - For CPVC piping, the manufacturer's list of materials compatible with the pipe
  - Dry pipe, preaction or deluge valve, accelerator, and air or nitrogen supply
- **Samples**
  - Concealed or decorative sprinklers and cover plates in the selected finish

## Extract for reconciliation
- 21wb.xf.supply-test — Water supply test (date, location, static, residual, flow) (list, per package) → report.utility_requirements, drawings.civil
- 21wb.xf.demand — Demand and margin at the base of the riser for each remote area (list, per package) → drawings.fire_protection
- 21wb.xf.backflow — Fire service backflow assembly type and size (string, per package) → drawings.civil, drawings.plumbing
- 21sp.xf.design-areas — Hazard or storage classification, density and area per design area (list, per package) → drawings.fire_protection, drawings.plans
- 21sp.xf.sprinkler-types — Sprinkler model, response, temperature, K-factor and finish per symbol (list, per package) → spec.part2, drawings.rcp
- 21sp.xf.system-types — System type per area (wet, dry, preaction, deluge, antifreeze) (list, per package) → drawings.fire_protection

## Standards to verify against
- NFPA 24: Standard for the Installation of Private Fire Service Mains and Their Appurtenances
- NFPA 291: Recommended Practice for Water Flow Testing and Marking of Hydrants
- NFPA 25: Standard for the Inspection, Testing, and Maintenance of Water-Based Fire Protection Systems
- ASSE 1013 / ASSE 1015 / ASSE 1047 / ASSE 1048: Reduced pressure principle and double check backflow prevention assemblies, and their detector versions
- NFPA 13: Standard for the Installation of Sprinkler Systems — Confirm the edition the jurisdiction adopted; the owner's insurer may impose its own criteria

## Warnings
- No profile for 21 13 13; compiled from ancestors only
- Draft knowledge in use (global, 21, 21 10 00, 21 13 00) — not yet PE-reviewed
