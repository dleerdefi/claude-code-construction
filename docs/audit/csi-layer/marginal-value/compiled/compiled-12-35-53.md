# Compiled knowledge — 12 35 53 Laboratory Casework

Facility types: education.k12 · Confidence floor: **draft** · Review mode: per_element · Contractor-designed: unknown
Lineage: global → 12 → 12 30 00 → [12 35 00 missing] → 12 35 53
Overlays: education, education.k12

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Laboratory casework, chemical-resistant work surfaces, service fixtures, storage for hazardous materials, and the casework side of fume hoods. On top of casework review, the risk is the furnish / install / connect split for service fixtures and the fit between casework, hoods, exhaust and plumbing, which are usually separate submittals from separate vendors.

## Review checks (35)
### completeness
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] d12.element-coverage** — Every casework elevation, plan location and room in the CDs has a corresponding shop drawing elevation, and every shop elevation maps to a CD tag. Build the trace first (plan tag → elevation → sections and details cut on it → casework schedule → spec article) and list any element on either side with no match.  
  Trace: drawings.plans, drawings.interior_elevations, drawings.details, schedule.casework · Owner: subcontractor · Scope: package · _12_
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
- **[high] cw.detail-trace** — For each elevation, every section and detail cut on the CD elevation is located and compared to the shop drawing: construction type, profiles, support, countertop edge, backsplash, and scribe conditions.  
  Trace: drawings.interior_elevations, drawings.details · Owner: subcontractor · Scope: element · Types: Shop Drawings · _12 30 00_
- **[high] cw.counter-heights** — Counter and work-surface heights AFF match the CD elevations; designated accessible units are identified on the shops with their heights and knee and toe clearances. Check the applicable regulatory hooks independently of the drawings.  
  Trace: drawings.interior_elevations, drawings.details, schedule.casework · Owner: subcontractor · Scope: element · Types: Shop Drawings · Gate: procurement_release · _12 30 00_
- **[high] cw.knee-clearance** — Knee and toe space at accessible sinks and work surfaces is not reduced by aprons, drawers, sink bowl depth, or exposed piping; pipe protection is assigned where required.  
  Trace: drawings.interior_elevations, drawings.details, drawings.plumbing · Owner: subcontractor · Scope: element · Types: Shop Drawings · _12 30 00_
- **[high] edu.risk-category-delegated** — Delegated designs (cladding and curtain wall, roofing attachment, joists and trusses, nonstructural and equipment anchorage) state the risk category and importance factors they used, and these match the structural general notes; schools are often assigned above the default, and designers who assume the default under-design.  
  Trace: drawings.structural, spec.part1_submittals · Owner: subcontractor · Scope: package · _overlay:education_
- **[high] edu.childrens-dimensions** — Where elements are designed for children (toilets, lavatories, drinking fountains, grab bars, accessories, work surfaces in the lower grades), the heights follow the children's provisions the design chose, consistently by grade group, and the fixture, accessory, partition and casework submittals use those heights rather than adult defaults.  
  Trace: drawings.interior_elevations, schedule.plumbing_fixture, schedule.toilet_accessories · Owner: subcontractor · Scope: element · Gate: in_wall_rough_in · _overlay:education.k12_
- **[medium] cw.grade-construction** — Casework material and construction (metal, wood, phenolic, polypropylene, plastic laminate) match Part 2, and the conformance claims and test data are to the SEFA 8 document for that material, as the spec requires.  
  Trace: spec.part2 · Owner: subcontractor · Scope: element · Types: Shop Drawings, Product Data, Test Reports · _12 30 00_
- **[medium] cw.hardware** — Each hardware type (hinges, pulls, slides, locks, shelf supports, grommets, catches) matches the spec or schedule by function, grade and finish, with quantity per unit; keying matches the owner's requirement.  
  Trace: spec.part2, schedule.casework_hardware · Owner: subcontractor · Scope: element · Types: Product Data, Shop Drawings · _12 30 00_
- **[medium] cw.countertops** — Countertop material, thickness, edge profile, backsplash and sidesplash heights, and seam locations match the CDs; no seam falls at a sink or cooktop cutout.  
  Trace: drawings.interior_elevations, drawings.details, spec.part2 · Owner: subcontractor · Scope: element · Types: Shop Drawings, Samples · _12 30 00_
- **[medium] cw.panel-cores** — Panel cores suit their location: moisture-resistant cores at sinks, dishwashers and other wet areas, fire-rated cores where a flame spread class is required, and no-added-formaldehyde or certified products where the spec requires them.  
  Trace: spec.part2, drawings.interior_elevations, schedule.plumbing_fixture · Owner: subcontractor · Scope: element · _12 30 00_
- **[medium] lc.work-surfaces** — Work surface material, thickness and chemical resistance match the spec and the lab program; marine edges, drip grooves and cup sinks are where the CDs show them.  
  Trace: spec.part2, drawings.interior_elevations, drawings.details · Owner: subcontractor · Scope: element · Types: Product Data, Samples, Shop Drawings · _12 35 53_
### coordination
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
- **[high] d12.furnished-by** — Owner-furnished and contractor-furnished designations (OFCI, OFOI, CFCI) for each item match the contract documents, and each owner-furnished item that needs backing, rough-in or an opening has a date by which the owner's selection must be frozen.  
  Trace: spec.part1, drawings.plans · Owner: gc · Scope: package · Gate: in_wall_rough_in · _12_
- **[high] cw.cutouts-by-others** — Cutouts for sinks, faucets, appliances and devices furnished by others are sized to the current approved model of that item, not the scheduled basis of design if it has since changed.  
  Trace: schedule.plumbing_fixture, schedule.equipment, drawings.plumbing, drawings.electrical · Owner: gc · Scope: element · Types: Shop Drawings · Gate: procurement_release · _12 30 00_
- **[high] cw.electrical-in-casework** — Receptacles, data, and under-cabinet or in-cabinet lighting are located on the shops with cutouts and wiring access, and match the electrical drawings and backsplash heights.  
  Trace: drawings.electrical, drawings.interior_elevations · Owner: gc · Scope: element · Types: Shop Drawings · Gate: in_wall_rough_in · _12 30 00_
- **[high] lc.service-fixtures** — Every service fixture (lab gases, vacuum, air, water, purified water, electrical pedestals) matches the CDs by location and type, and who furnishes, installs and connects each one is explicit.  
  Trace: drawings.lab_gas, drawings.plumbing, drawings.electrical, spec.part1 · Owner: gc · Scope: element · Types: Shop Drawings, Product Data · Gate: in_wall_rough_in · _12 35 53_
- **[high] lc.fume-hood-interface** — Hood base cabinets, work surface under the hood, and cutouts match the current fume hood submittal (width, depth, services, sash clearance), not the original hood basis of design.  
  Trace: schedule.equipment, drawings.interior_elevations · Owner: gc · Scope: element · Types: Shop Drawings · Gate: procurement_release · _12 35 53_
- **[high] lc.ventilated-storage** — Flammable and corrosive storage cabinets are vented or unvented as the CDs and owner standards require; where vented, the connection size and location are on the mechanical drawings.  
  Trace: drawings.mechanical, spec.part2 · Owner: gc · Scope: element · Types: Shop Drawings, Product Data · Gate: above_ceiling_close_in · _12 35 53_
- **[high] edu.instructional-lab-shutoffs** — Science classrooms and instructional labs show the emergency shutoff of fuel gas (and of power where required) operable from the teacher station, with the valve, controls, resets and any fire alarm or hood interlock on the plumbing, electrical and lab equipment submittals. Research-lab requirements come from the laboratory overlay.  
  Trace: drawings.plumbing, drawings.lab_gas, drawings.electrical · Owner: gc · Scope: element · _overlay:education_
- **[medium] lc.emergency-fixtures** — Deck-mounted eyewashes and drench hoses have top cutouts and clear access as shown on the plumbing drawings.  
  Trace: drawings.plumbing, drawings.interior_elevations · Owner: gc · Scope: element · Types: Shop Drawings · _12 35 53_
### constructability
- **[critical] cw.in-wall-support** — Wall-hung casework, countertop brackets and support frames show support type, location, height and load, with every in-wall component flagged for installation before close-in and routed to the framer.  
  Trace: drawings.details, drawings.interior_elevations, spec.part3 · Owner: gc · Scope: element · Types: Shop Drawings · Gate: wall_close_in · _12 30 00_
- **[high] cw.site-conditions** — Casework is delivered only after the room is enclosed and dry, the HVAC is holding the humidity range the AWI standard sets for the project's region, and walls are finished and primed behind it; units acclimate in the room before they are scribed and installed.  
  Trace: spec.part1, spec.part3, schedule.master · Owner: gc · Scope: package · _12 30 00_
- **[high] edu.summer-window** — Where work in existing schools must fit a break in the academic calendar, each submittal's approval, owner selections, mock-ups and delivery are dated against the day the window opens, not against a floating schedule activity. Long-lead items (door frames and hardware, HVAC equipment, switchgear, casework, flooring) that miss the window push work into occupied classrooms or a year later, so their submittals are released first.  
  Trace: schedule.master, spec.division_01 · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[medium] cw.appliance-openings** — Openings for undercounter appliances fit the scheduled appliance plus the manufacturer's ventilation and service clearances.  
  Trace: schedule.equipment · Owner: subcontractor · Scope: element · Types: Shop Drawings · _12 30 00_
- **[medium] cw.fillers-scribes** — Fillers and scribes are shown at walls, corners and ends, and dimensions needing field verification are flagged before release.  
  Trace: drawings.plans, drawings.interior_elevations · Owner: subcontractor · Scope: element · Types: Shop Drawings · _12 30 00_
- **[medium] lc.top-support** — Heavy work surfaces and tables have support frames, legs or wall rails shown per the manufacturer; adjustable-height tables show their electrical needs.  
  Trace: drawings.details, drawings.electrical · Owner: subcontractor · Scope: element · Types: Shop Drawings · _12 35 53_
### absence
- **[low] cw.base-toe-kick** — Toe kick height and finish, and who provides base at casework (casework fabricator or resilient base installer), are defined somewhere in the contract documents.  
  Trace: drawings.details, spec.part2 · Owner: design_team · Scope: element · _12 30 00_

## Reconciliations — documents that must agree (3)
- **[high] cw.rc.sinks** — Every sink on the casework elevations has a fixture tag on the plumbing plans and schedule, and the scheduled sink's mounting, bowl depth and faucet holes suit the top and, at accessible units, the knee space.  
  Between: drawings.interior_elevations ↔ schedule.plumbing_fixture ↔ drawings.plumbing · Key: Each sink location in casework · Fields: fixture tag, sink type and mounting, bowl depth, faucet holes, accessible designation · Owner: design_team · Gate: procurement_release · _12 30 00_
- **[high] lc.rc.service-fixtures** — Every service outlet on the lab gas and plumbing drawings appears on the casework elevations at the same location and mounting, and every fixture on the elevations has piping to it.  
  Between: drawings.lab_gas ↔ drawings.plumbing ↔ drawings.interior_elevations · Key: Each service fixture location · Fields: service type, fixture type, mounting (deck, panel, reagent rack, pedestal), outlet count · Owner: design_team · Gate: in_wall_rough_in · _12 35 53_
- **[medium] cw.rc.devices** — Receptacles, switches, data outlets and under-cabinet lights on the electrical drawings land where the elevations leave wall exposed: above the backsplash, below upper cabinets, and not behind tall units or appliances.  
  Between: drawings.interior_elevations ↔ drawings.electrical · Key: Each casework elevation · Fields: device type, location, height relative to backsplash and upper cabinets, under-cabinet lighting · Owner: design_team · Gate: in_wall_rough_in · _12 30 00_

## Compliance — regulatory hooks (9)
- **[high] cw.rh.accessibility-work-surfaces** (`accessibility-work-surfaces`) — Do designated accessible work surfaces, sinks and service counters meet the adopted accessibility standard for height, knee and toe clearance, and reach, and how many of each type must be accessible?  
  **Unbound** → Run /construction:code-researcher with research topic "accessibility-work-surfaces" (seed it with this hook's question)
- **[high] cw.rh.seismic-anchorage** (`seismic-nonstructural-anchorage`) — Does the seismic design category or occupancy require engineered anchorage for tall or heavy casework, and does the submittal include it?  
  **Unbound** → Run /construction:code-researcher with research topic "seismic-nonstructural-anchorage" (seed it with this hook's question)
- **[high] lc.rh.hazardous-storage** (`laboratory-hazardous-materials-storage`) — What do the adopted fire code and laboratory fire protection standard require for flammable and corrosive storage cabinets (construction, labeling, quantity limits, venting)?  
  **Unbound** → Run /construction:code-researcher with research topic "laboratory-hazardous-materials-storage" (seed it with this hook's question)
- **[high] lc.rh.emergency-eyewash** (`emergency-eyewash-shower`) — Do emergency eyewash and shower locations, travel distance, water supply and tempering meet the standard the owner or jurisdiction applies?  
  **Unbound** → Run /construction:code-researcher with research topic "emergency-eyewash-shower" (seed it with this hook's question)
- **[high] edu.rh.school-agency-review** (`school-construction-agency-review`) — Does a state agency other than the local building department review plans, approve changes or inspect construction for this school (common for public K-12 and in some states for community colleges), and what does it require for deferred submittals, change documents, testing laboratories and the inspector of record?  
  **Unbound** → Run /construction:code-researcher with research topic "school-construction-agency-review" (seed it with this hook's question)
- **[high] edu.rh.risk-category** (`building-risk-category-assignment`) — What risk category applies to this building under the adopted code (occupant load, designation as an emergency or community shelter), and which design loads, nonstructural anchorage and special inspections change because of it?  
  **Unbound** → Run /construction:code-researcher with research topic "building-risk-category-assignment" (seed it with this hook's question)
- **[high] edu.rh.instructional-lab-shutoffs** (`instructional-lab-emergency-shutoffs`) — Do the adopted fire and fuel gas codes, NFPA 45 where it is adopted, or state education rules require emergency shutoff of fuel gas or power in instructional science labs, and where must the controls be located?  
  **Unbound** → Run /construction:code-researcher with research topic "instructional-lab-emergency-shutoffs" (seed it with this hook's question)
- **[high] edu.rh.childrens-dimensions** (`childrens-accessibility-dimensions`) — Which children's reach ranges and fixture, counter and grab bar heights does the adopted accessibility standard allow or require for elements designed primarily for children, and for which age groups?  
  **Unbound** → Run /construction:code-researcher with research topic "childrens-accessibility-dimensions" (seed it with this hook's question)
- **[low] d12.rh.composite-wood-formaldehyde** (`composite-wood-formaldehyde`) — Are composite wood products (particleboard, MDF, hardwood plywood) in furnishings certified to the applicable formaldehyde emission standard, and does the spec require more (e.g. no added formaldehyde)?  
  **Unbound** → Run /construction:code-researcher with research topic "composite-wood-formaldehyde" (seed it with this hook's question)

## Coordination routing (11)
- **[critical] if.casework-backing** → Framing / rough carpentry / misc. metals (06 10 53, 09 22 16, 05 50 00) · Gate: wall_close_in — Before second-side gypsum board
  - Send them: In-wall supports and backing per elevation — type, location, height, load, bracket model
  - Need from them: Backing type for each wall assembly; confirmation it is installed and inspected before close-in
  - Confirm who: Concealed in-wall brackets for wall-hung counters — typical furnish 12 30 00 / install 06 10 53 or 09 22 16
- **[high] if.01-temporary-conditions-woodwork** → Temporary facilities (enclosure, heat and humidity control) (01 50 00) · Gate: interior_finish_start
  - Send them: The temperature and humidity range the woodwork standard and the manufacturers require for delivery, storage, acclimation and installation, and the delivery date
  - Need from them: Building enclosed, wet work dry, and temperature and humidity held within the woodwork and door limits continuously from before delivery
  - If missed: Wood doors, casework, wood or resilient flooring delivered and installed before the building holds temperature and humidity; Woodwork delivered into a building without running HVAC, or with wet plaster or concrete
- **[high] if.casework-plumbing** → Plumbing (22 40 00) · Gate: in_wall_rough_in
  - Send them: Sink and faucet cutouts, bowl depth limits, access panels, knee-space and pipe-protection conditions
  - Need from them: Approved fixture models and cut sheets, rough-in heights and locations for supply and waste
  - Confirm who: Sinks and faucets in casework tops — typical furnish 22 40 00 / install 12 30 00 or 22 40 00 / connect 22 40 00
  - If missed: Tops cut before the undermount sinks arrive, or an integral sink also bought by the plumber
- **[high] if.casework-electrical** → Electrical (26 27 26, 26 51 00) · Gate: in_wall_rough_in
  - Send them: Device and light cutouts, backsplash heights, wiring chases and access
  - Need from them: Device locations and heights, under-cabinet fixture models and drivers
  - If missed: Boxes set at plan heights before casework shop drawings; a box is split by the backsplash or hidden behind an upper cabinet
- **[high] if.lab-casework-fume-hoods** → Fume hoods (11 53 13) · Gate: procurement_release — Review hood and casework shops together
  - Send them: Base cabinets and work surface under each hood, cutouts for hood services
  - Need from them: Hood dimensions, service locations, sash clearance, weight
- **[high] if.lab-casework-services** → Laboratory gases and plumbing (22 63 00, 22 40 00) · Gate: in_wall_rough_in
  - Send them: Service fixture types and locations on casework and tops
  - Need from them: Piping rough-in to each fixture; connection scope
  - Confirm who: Laboratory service fixtures (turrets, valves, outlets) — typical furnish 12 35 53 / install 12 35 53 / connect 22 63 00
- **[high] if.lab-casework-exhaust** → HVAC ductwork (23 31 00) · Gate: above_ceiling_close_in
  - Send them: Ventilated storage cabinet locations and vent connection sizes
  - Need from them: Exhaust connection or confirmation that cabinets stay unvented
- **[medium] if.09-finishes-equipment-casework** → Flooring, tile and painting (09 60 00, 09 30 00, 09 90 00) · Gate: floor_finish_install
  - Send them: Fixed or movable status, footprints, setting sequence relative to flooring, floor anchoring, and the sealing to wall and floor that cleanability or health rules require
  - Need from them: Whether floor and wall finishes run under and behind each fixed item or stop at it, and the base and sealing at that edge
  - Confirm who: Finish under and behind fixed equipment and casework — typical install 09 60 00, 09 30 00 or 09 90 00 before the item is set, or excluded by the finish schedule
  - If missed: Equipment set on bare slab with no finish under it, or flooring run under items that must be sealed to the slab; edges rejected as uncleanable
- **[medium] if.10-counter-dispensers** → Toilet accessories (10 28 00) · Gate: procurement_release — Before stone, quartz or solid-surface tops are fabricated
  - Send them: Shop-cut holes at those positions, and access below the top inside the vanity
  - Need from them: Counter-mounted dispenser models, hole sizes and positions, and the reservoir and refill clearance they need below the top
  - Confirm who: Holes for counter-mounted soap dispensers — typical install 12 36 00
  - If missed: Tops fabricated without dispenser holes; field drilling chips or cracks the top, or dispensers move to the wall
- **[medium] if.lab-casework-eyewash** → Emergency plumbing fixtures (22 45 00) · Gate: in_wall_rough_in
  - Send them: Top cutouts and access for deck-mounted eyewash and drench hose
  - Need from them: Fixture models, supply and tempering
  - If missed: Eyewash with no cutout or blocked by casework
- **[low] if.casework-base** → Resilient flooring (09 65 13) · Gate: equipment_set
  - Send them: Toe kick height and finish
  - Need from them: Base type at casework
  - Confirm who: Base at casework toe kicks — typical furnish 09 65 13 / install 09 65 13
  - If missed: Nobody carries base at casework; punch list item with no owner

## Failure modes to watch (19)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d12.fm.owner-selection-late** — An owner-furnished item is selected after its backing, rough-in or opening was built to a guess → Walls opened, casework recut, or the item surface-mounted on exposed raceway (caught by d12.furnished-by; field_experience)
- **cw.fm.in-wall-brackets-missed** — In-wall brackets and backing for wall-hung counters were never identified or never reached the framer before drywall → Finished walls opened, patched and repainted; casework install slips behind finishes (caught by cw.in-wall-support, if.casework-backing; field_experience)
- **cw.fm.elevations-only** — Shops checked against elevations only; sections and details cut on the elevations never pulled → Construction, support or edge conditions differ from design; discovered at install (caught by cw.detail-trace, d12.element-coverage; field_experience)
- **cw.fm.heights-drawings-only** — Counter heights verified against the drawings but not against the governing accessibility or licensing rule → Fabricated or installed casework fails inspection; rework after install (caught by cw.counter-heights; field_experience)
- **cw.fm.sink-model-changed** — Plumbing fixture substitution approved after casework tops were cut for the original sink → Recut or replace tops; schedule hit at the end of the job (caught by cw.cutouts-by-others; industry_practice)
- **cw.fm.hardware-short** — Hardware quantities per unit undercounted across hundreds of units → Short shipment discovered at install; punch list drags (caught by cw.hardware; field_experience)
- **cw.fm.warped-doors** — Casework installed while the HVAC is off or the room is still wet → Doors warp, veneer and laminate delaminate and joints open; doors and panels replaced (caught by cw.site-conditions, if.01-temporary-conditions-woodwork; industry_practice)
- **cw.fm.swollen-sink-base** — Standard particleboard cores used at sinks and dishwashers → Swollen tops and bases after the first leak or wet cleaning (caught by cw.panel-cores; industry_practice)
- **lc.fm.service-fixture-split** — Casework vendor furnishes service fixtures, plumbing assumes they are in its scope or vice versa → Duplicate fixtures or none; connections missed at turnover (caught by lc.service-fixtures, if.lab-casework-services; industry_practice)
- **lc.fm.vented-cabinet-no-duct** — Vented storage cabinets submitted with no exhaust connection in the mechanical design → Late duct and fan work, or cabinets plugged contrary to owner standards (caught by lc.ventilated-storage, if.lab-casework-exhaust; industry_practice)
- **lc.fm.hood-size-changed** — Fume hood width changed in the hood submittal; casework base and top still built to the old width → Rework of base cabinets and tops at hood locations (caught by lc.fume-hood-interface, if.lab-casework-fume-hoods; industry_practice)
- **edu.fm.missed-window** — Hardware, HVAC equipment or casework approved late and delivered after the summer window closes → Work moves into occupied classrooms after hours with temporary systems, or the phase slips a full year (caught by edu.summer-window; field_experience)
- **edu.fm.agency-change-unapproved** — A substitution or field change accepted by the architect is never submitted to the state school-construction agency → The agency withholds certification or closeout of the project; work is reopened or occupancy delayed (caught by edu.agency-approvals; industry_practice)
- **edu.fm.default-risk-category** — Delegated cladding, joist or anchorage design done to the default risk category on a school assigned a higher one → Components under-designed; recalculation and field reinforcement after installation (caught by edu.risk-category-delegated; industry_practice)
- **edu.fm.adult-heights** — Fixtures, accessories and partitions in lower-grade toilet rooms installed at adult accessible heights, or the reverse → Elements unusable by the intended users or non-compliant; carriers, backing and accessories reset (caught by edu.childrens-dimensions; field_experience)

## Expected submittal contents
- **Shop Drawings**
  - Plan layout keyed to every CD elevation tag and room
  - Elevations with overall dimensions, counter and work-surface heights AFF, knee spaces, toe kick
  - Sections showing box construction, materials, grade and attachment
  - Countertop material, thickness, edges, backsplash and sidesplash, seam locations, cutouts
  - In-wall supports and backing with type, height and load, per elevation
  - Hardware keyed to the hardware schedule, with quantity per unit
  - Fillers, scribes and field-verify dimensions
  - Items by others (sinks, faucets, appliances, devices) with the model each cutout is sized for
- **Product Data**
  - Every hardware item, marked to the scheduled function and finish
  - Laminate, solid surface or other surfacing and edge materials
  - Adhesives and sealants where the spec limits VOC content
- **Samples**
  - Each finish, laminate, edge band and countertop material, in the selected color
- **Qualification Statements**
  - Fabricator and installer qualifications or certification program the spec names

## Extract for reconciliation
- cw.xf.counter-height — Counter / work-surface height AFF (number, in, per element) → drawings.interior_elevations
- cw.xf.accessible-unit — Designated accessible unit (boolean, per element) → drawings.interior_elevations, drawings.plans
- cw.xf.in-wall-supports — In-wall supports (type, height, load) (list, per element) → drawings.details
- cw.xf.cutout-models — Fixture or appliance model each cutout is sized for (list, per element) → schedule.plumbing_fixture, schedule.equipment
- cw.xf.devices — Electrical devices and lights in casework (list, per element) → drawings.electrical
- cw.xf.hardware-counts — Hardware type and quantity per unit (list, per element) → schedule.casework_hardware
- lc.xf.service-fixtures — Service fixtures (type, location, furnished by) (list, per element) → drawings.lab_gas, drawings.plumbing
- lc.xf.storage-cabinets — Hazardous storage cabinets (type, vented or not) (list, per element) → drawings.mechanical

## Standards to verify against
- AWI standards: AWS Edition 2, or ANSI/AWI 0641 (Architectural Wood Casework), 1232 (Manufactured Wood Casework), 1236 (Countertops) — The ANSI/AWI series replaced parts of AWS Edition 2; review against whichever the spec cites
- ANSI/BHMA A156.9: Cabinet Hardware — Confirm the edition the spec cites
- NEMA LD 3: High-Pressure Decorative Laminates — Older specs cite this; if the cited edition is no longer published, ask which criteria govern
- SEFA 8 series: Lab Grade Casework Standards — 8-M metal, 8-W wood, 8-PH phenolic, 8-P polypropylene, 8-PL plastic laminate — Confirm the edition the spec cites
- SEFA 3: Work Surfaces Standard
- SEFA 7: Lab Grade Fixtures Standard

## Escalations
- cw.rh.seismic-anchorage: medium → high by overlay:education — Schools are often assigned a higher risk category, and tall classroom storage and shelving can topple onto students

## Suppressed
- d12.anchorage (from 12) by 12 30 00 — cw.in-wall-support checks support and backing per elevation; engineered anchorage is cw.rh.seismic-anchorage
- d12.power-data (from 12) by 12 30 00 — cw.electrical-in-casework and cw.rc.devices check devices per elevation
- d12.fm.outlets-vs-layout (from 12) by 12 30 00 — Follows d12.power-data; if.casework-electrical carries the casework version

## Warnings
- Draft knowledge in use (global, 12, 12 30 00, 12 35 53) — not yet PE-reviewed
