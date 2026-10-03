# Compiled knowledge — 22 40 00 Plumbing Fixtures

Facility types: education.k12 · Confidence floor: **draft** · Review mode: per_element · Contractor-designed: never
Lineage: global → 22 → 22 40 00
Overlays: education, education.k12

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Water closets, urinals, lavatories, sinks, showers, drinking fountains and their trim, carriers and supports (commercial, healthcare, security fixtures and drinking fountains inherit from here). Reviewed by fixture tag: each tag's complete package of fixture, trim and carrier against the schedule, then each location against the architectural plans, elevations, casework and accessories. The expensive misses are carriers and rough-ins that do not fit the wall before it closes, and accessible fixtures whose controls, heights and clearances fight the grab bars and casework around them.

## Review checks (21)
### completeness
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] edu.agency-approvals** — Where a state school-construction agency has jurisdiction, deferred submittals, substitutions and field changes that touch structure, fire and life safety or accessibility are approved by that agency before fabrication, not only by the architect, and the agency's inspector and testing requirements are in the inspection program.  
  Trace: spec.division_01, register.special_inspections, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.products-marked** — Cut sheets covering a product family have the proposed model, size, options, finish and accessories clearly marked; unmarked sheets are returned.  
  Trace: spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data · _global_
- **[medium] 22fx.tag-completeness** — Each fixture tag's submittal covers every component in the schedule and the rough-in it needs (wall or floor outlet, rough-in dimension, supply height), matching the scheduled fixture and the wall it mounts on.  
  Trace: schedule.plumbing_fixture, spec.part2 · Owner: subcontractor · Scope: element · Types: Product Data · _22 40 00_
### conformance
- **[high] g.current-documents** — The submittal reflects the current contract documents, including addenda, ASIs, bulletins and responded RFIs, not the bid set. Note the drawing revision the submitter worked from.  
  Trace: drawings.revision_blocks, register.asi_bulletin_log, register.rfi_log · Owner: gc · Scope: package · _global_
- **[high] g.basis-of-design** — Proposed manufacturer and model match the basis of design or a listed acceptable manufacturer. Anything else follows the comparable-product or substitution procedure Division 01 allows, with its timing and comparison data, before it is reviewed on its merits.  
  Trace: spec.part2_manufacturers, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] g.deviations-identified** — Every deviation from the contract documents is clouded or listed by the submitter. Compare independently; do not rely on the submitter's list.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _global_
- **[high] d22.potable-certification** — Every product in contact with drinking water (pipe, fittings, valves, faucets, water heaters, backflow assemblies, drinking fountains, solder and joint compounds) carries the health-effects and lead-content certification the code requires, shown on the product data, including components inside equipment packages furnished by others.  
  Trace: spec.part2, spec.part2_manufacturers · Owner: subcontractor · Scope: package · Types: Product Data · _22_
- **[high (reflex)] d22.plenum-materials** — Plastic pipe, insulation, jackets and pipe wraps exposed in return-air plenums meet the plenum flame-spread and smoke-developed limits or are listed for plenum use, or are enclosed or routed out of the plenum. A metal-to-plastic substitution is checked for this before approval.  
  Trace: drawings.mechanical, drawings.plumbing, spec.part2 · Owner: subcontractor · Scope: package · _22_
- **[high] 22fx.accessible** — Designated accessible fixtures meet the adopted accessibility standard as installed: rim and seat heights, flush controls on the open side, faucet operation, knee and toe clearance at lavatories and sinks with supply and drain piping protected or kept out of the knee space, shower controls and hand shower, and drinking fountains at both heights where required.  
  Trace: drawings.enlarged_plans, drawings.interior_elevations, schedule.plumbing_fixture · Owner: subcontractor · Scope: element · _22 40 00_
- **[high] 22fx.temperature-limits** — Public lavatories, showers and other fixtures where the code limits delivered temperature have a listed temperature-limiting device or valve of the type the code requires, reachable for adjustment.  
  Trace: schedule.plumbing_fixture, drawings.details · Owner: subcontractor · Scope: element · _22 40 00_
- **[high] edu.risk-category-delegated** — Delegated designs (cladding and curtain wall, roofing attachment, joists and trusses, nonstructural and equipment anchorage) state the risk category and importance factors they used, and these match the structural general notes; schools are often assigned above the default, and designers who assume the default under-design.  
  Trace: drawings.structural, spec.part1_submittals · Owner: subcontractor · Scope: package · _overlay:education_
- **[high] edu.childrens-dimensions** — Where elements are designed for children (toilets, lavatories, drinking fountains, grab bars, accessories, work surfaces in the lower grades), the heights follow the children's provisions the design chose, consistently by grade group, and the fixture, accessory, partition and casework submittals use those heights rather than adult defaults.  
  Trace: drawings.interior_elevations, schedule.plumbing_fixture, schedule.toilet_accessories · Owner: subcontractor · Scope: element · Gate: in_wall_rough_in · _overlay:education.k12_
- **[medium] 22fx.water-efficiency** — Flow and flush rates meet the plumbing and energy codes and any green building program the spec names, and low-flow faucets are checked against the hot water design (delivery time, activation flow of local heaters).  
  Trace: schedule.plumbing_fixture, spec.part2 · Owner: subcontractor · Scope: element · _22 40 00_
### coordination
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
- **[medium] 22fx.sensor-power** — Hardwired sensor faucets and flush valves have transformer and junction box locations in the chase or under the counter on the electrical drawings, roughed in before the walls close; battery units are confirmed with the owner.  
  Trace: drawings.electrical, drawings.plumbing, spec.part2 · Owner: gc · Scope: element · Gate: in_wall_rough_in · _22 40 00_
### constructability
- **[high] 22fx.carriers** — Wall-hung fixtures are on carriers whose type fits the chase or wall depth on the partition types (single, back-to-back, offset), rated for the load including bariatric fixtures where scheduled, and set with their rough-in heights before the wall closes.  
  Trace: schedule.partition_type, drawings.enlarged_plans, drawings.details · Owner: gc · Scope: element · Gate: wall_close_in · _22 40 00_
- **[high] edu.summer-window** — Where work in existing schools must fit a break in the academic calendar, each submittal's approval, owner selections, mock-ups and delivery are dated against the day the window opens, not against a floating schedule activity. Long-lead items (door frames and hardware, HVAC equipment, switchgear, casework, flooring) that miss the window push work into occupied classrooms or a year later, so their submittals are released first.  
  Trace: schedule.master, spec.division_01 · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
### absence
- **[medium] d22.concealed-access** — Valves, cleanouts, trap primers, water hammer arresters, mixing valves, backflow assemblies and other serviceable devices concealed in walls or above hard ceilings have access panels located on the architectural drawings, sized for the service, and placed where the finishes allow (not in tile or feature walls without the architect's approval).  
  Trace: drawings.rcp, drawings.interior_elevations, drawings.plumbing · Owner: gc · Scope: package · Gate: wall_close_in · _22_

## Reconciliations — documents that must agree (2)
- **[high] 22fx.rc.fixtures-vs-arch** — Fixture counts, types and locations on the plumbing plans and schedule match the current architectural enlarged plans room by room, in both directions, including accessible designations and mounting heights.  
  Between: schedule.plumbing_fixture ↔ drawings.plumbing ↔ drawings.enlarged_plans · Key: Fixture tag and room · Fields: count by type, location, accessible designation, mounting height · Owner: design_team · Gate: underslab_rough_in · _22 40 00_
- **[high] 22fx.rc.accessories** — In each accessible toilet room and stall, fixture centerlines, flush valve and supply locations, grab bars, dispensers and mirror fit together on the elevations without overlap, and sinks set in casework match the casework elevations.  
  Between: drawings.enlarged_plans ↔ drawings.interior_elevations ↔ schedule.toilet_accessories ↔ schedule.plumbing_fixture · Key: Accessible toilet room, stall or lavatory · Fields: water closet centerline to side wall, flush valve side and height against the grab bars, dispenser and toilet paper locations, mirror and lavatory, sink in casework · Owner: design_team · Gate: in_wall_rough_in · _22 40 00_

## Compliance — regulatory hooks (9)
- **[high] d22.rh.plumbing-code** (`plumbing-code-adoption`) — Which plumbing code and edition govern this project, with which local amendments, and do the water purveyor and the sewer authority impose their own rules on connections, metering and discharge?  
  **Unbound** → Run /construction:code-researcher with research topic "plumbing-code-adoption" (seed it with this hook's question)
- **[high] d22.rh.plenum** (`return-air-plenum-materials`) — Which plumbing materials (plastic pipe, insulation, jackets) may be exposed in return-air plenums under the adopted mechanical and building codes, and with what flame-spread and smoke-developed limits or listings?  
  **Unbound** → Run /construction:code-researcher with research topic "return-air-plenum-materials" (seed it with this hook's question)
- **[high] 22fx.rh.accessible** (`accessible-plumbing-fixtures`) — Which fixtures must be accessible and how many, and what does the adopted accessibility standard (with any state amendments) require for their heights, controls, clearances and pipe protection?  
  **Unbound** → Run /construction:code-researcher with research topic "accessible-plumbing-fixtures" (seed it with this hook's question)
- **[high] 22fx.rh.temperature** (`hot-water-temperature-limits`) — At which fixtures does the plumbing code limit delivered hot water temperature (public lavatories, showers, tubs, healthcare or childcare fixtures), and which device types and set points does it require?  
  **Unbound** → Run /construction:code-researcher with research topic "hot-water-temperature-limits" (seed it with this hook's question)
- **[high] edu.rh.school-agency-review** (`school-construction-agency-review`) — Does a state agency other than the local building department review plans, approve changes or inspect construction for this school (common for public K-12 and in some states for community colleges), and what does it require for deferred submittals, change documents, testing laboratories and the inspector of record?  
  **Unbound** → Run /construction:code-researcher with research topic "school-construction-agency-review" (seed it with this hook's question)
- **[high] edu.rh.risk-category** (`building-risk-category-assignment`) — What risk category applies to this building under the adopted code (occupant load, designation as an emergency or community shelter), and which design loads, nonstructural anchorage and special inspections change because of it?  
  **Unbound** → Run /construction:code-researcher with research topic "building-risk-category-assignment" (seed it with this hook's question)
- **[high] edu.rh.childrens-dimensions** (`childrens-accessibility-dimensions`) — Which children's reach ranges and fixture, counter and grab bar heights does the adopted accessibility standard allow or require for elements designed primarily for children, and for which age groups?  
  **Unbound** → Run /construction:code-researcher with research topic "childrens-accessibility-dimensions" (seed it with this hook's question)
- **[medium] d22.rh.potable-certification** (`potable-water-component-certification`) — What health-effects and lead-content certification do the adopted plumbing code and drinking water law require for products that convey or dispense potable water?  
  **Unbound** → Run /construction:code-researcher with research topic "potable-water-component-certification" (seed it with this hook's question)
- **[medium] 22fx.rh.efficiency** (`plumbing-fixture-water-efficiency`) — What maximum flow and flush rates apply under the plumbing code, the energy or green building code and state water efficiency rules, and what certification must each fixture carry?  
  **Unbound** → Run /construction:code-researcher with research topic "plumbing-fixture-water-efficiency" (seed it with this hook's question)

## Coordination routing (8)
- **[high] if.06-plumbing-fixture-support** → Rough carpentry and wood framing (06 10 53, 06 11 00) · Gate: wall_close_in
  - Send them: Which fixtures hang on floor-mounted carriers and which on wall backing, carrier and piping locations in the chase, and mounting heights
  - Need from them: Backing for wall-hung fixtures not on carriers, and for grab bars and accessories placed around carriers and supply piping
  - Confirm who: Support of wall-hung lavatories, sinks and drinking fountains — typical furnish 22 40 00 (carrier) or 06 10 53 (backing) / install 22 40 00 or 06 10 53
  - If missed: Grab bar backing blocked by a carrier or flush-valve piping, or a wall-hung fixture with neither carrier nor backing; relocated after the wall is closed
- **[high] if.09-fixture-carriers** → Partition framing at plumbing walls (09 21 16, 09 22 16) · Gate: in_wall_rough_in
  - Send them: Carrier models, the chase depth they need, floor anchoring, and rough-in heights for wall-hung fixtures, set before close-in
  - Need from them: Chase walls framed to the depth the carriers need, with studs laid out clear of carrier uprights and floor anchors
  - If missed: Chase framed too shallow for the carriers, or carriers set after board; plumbing walls rebuilt or fixtures hung on backing never designed for the load
- **[high] if.09-tiled-floor-drains** → Tile and fluid-applied flooring (09 30 00, 09 67 00) · Gate: slab_pour — Drain body elevation and flange type are fixed when the drain is cast in
  - Send them: Drain bodies with a clamping ring or bonding flange suited to the membrane, set at the elevation that gives the slope; adjustable strainers; linear drain sizes and outlets; shower valve rough-in depth for the wall assembly thickness
  - Need from them: Finished floor elevation at each drain, the slope method, the membrane and how it connects, and the tile module for strainer sizes
  - Confirm who: Linear and area drains in tiled floors — typical furnish 22 13 19 or 09 30 00 / install 22 13 19 / connect 22 13 19
  - Confirm who: Membrane connection to the drain flange or clamping ring — typical install 09 30 00 or the waterproofing installer
  - If missed: Membrane stops short of the drain, or the drain has no clamping ring or bonding flange to connect to
- **[high] if.10-toilet-room-fixtures** → Toilet compartments and accessories (10 21 13, 10 28 00) · Gate: in_wall_rough_in — Carriers and supplies are usually set before the compartment and accessory submittals are approved
  - Send them: Fixture centerlines, carrier and supply rough-in locations, flush valve side and height, and lavatory and faucet models
  - Need from them: Compartment module widths, accessible compartment dimensions, and grab bar and dispenser positions in each toilet room
  - If missed: Carriers and rough-in set to the plumbing drawings while the compartment module widths shifted on the shop drawings; Flush valve roughed in on the wall side where the rear grab bar runs
- **[high] if.casework-plumbing** → Casework (12 30 00, 06 41 00) · Gate: in_wall_rough_in
  - Send them: Approved fixture models and cut sheets, rough-in heights and locations for supply and waste
  - Need from them: Sink and faucet cutouts, bowl depth limits, access panels, knee-space and pipe-protection conditions
  - Confirm who: Sinks and faucets in casework tops — typical furnish 22 40 00 / install 12 30 00 or 22 40 00 / connect 22 40 00
  - If missed: Tops cut before the undermount sinks arrive, or an integral sink also bought by the plumber
- **[high] if.lab-casework-services** → Laboratory casework (12 35 53) · Gate: in_wall_rough_in
  - Send them: Piping rough-in to each fixture; connection scope
  - Need from them: Service fixture types and locations on casework and tops
  - Confirm who: Laboratory service fixtures (turrets, valves, outlets) — typical furnish 12 35 53 / install 12 35 53 / connect 22 63 00
  - If missed: Casework vendor furnishes service fixtures, plumbing assumes they are in its scope or vice versa
- **[medium] if.lab-casework-eyewash** → Laboratory casework (12 35 53) · Gate: in_wall_rough_in
  - Send them: Fixture models, supply and tempering
  - Need from them: Top cutouts and access for deck-mounted eyewash and drench hose
  - If missed: Eyewash with no cutout or blocked by casework
- **[medium] if.22-sensor-fixtures-power** → Boxes, raceways and wiring devices (26 05 33, 26 27 00) · Gate: in_wall_rough_in
  - Send them: Which fixtures and devices are hardwired, transformer and junction box locations in the chase or under counters, and the load per circuit
  - Need from them: Boxes and circuits at those locations, roughed in before the walls close, and receptacles under counters where plug-in transformers are used

## Failure modes to watch (16)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d22.fm.plastic-in-plenum** — PVC drainage or uncovered foam insulation installed in a return-air plenum → The above-ceiling inspection fails; pipe replaced with metal or wrapped after other trades have filled the ceiling (caught by d22.plenum-materials; industry_practice)
- **d22.fm.uncertified-product** — A faucet, valve or equipment component arrives without lead-content certification → Products replaced before occupancy, or the owner's water sampling fails (caught by d22.potable-certification; industry_practice)
- **d22.fm.no-access** — Valves, primers or mixing valves left behind hard ceilings or tile with no access panel → Access panels cut into finished surfaces after turnover, or devices that can never be serviced (caught by d22.concealed-access; industry_practice)
- **22fx.fm.arch-revised** — Toilet rooms revised on the architectural drawings by ASI while the plumbing drawings kept the old layout → Rough-ins in the wrong place under the slab or in the wall; fixture counts short at inspection (caught by 22fx.rc.fixtures-vs-arch; industry_practice)
- **22fx.fm.flush-valve-grab-bar** — Flush valve on the wall side, or at the height of the grab bar → The grab bar cannot be mounted where required; fixture or valve replaced (caught by 22fx.rc.accessories, 22fx.accessible, if.10-toilet-room-fixtures; industry_practice)
- **22fx.fm.exposed-piping** — Accessible lavatory installed with unprotected supplies and trap, or with piping in the knee space → Accessibility inspection finding; covers or offset drains added (caught by 22fx.accessible; industry_practice)
- **22fx.fm.sensor-no-power** — Hardwired sensor faucets bought with no transformer locations or boxes in the electrical design → Walls or counters opened to add power, or a switch to battery units after approval (caught by 22fx.sensor-power, if.22-sensor-fixtures-power; industry_practice)
- **22fx.fm.unlimited-temperature** — Public lavatories supplied with hot water and no temperature-limiting device → Scald risk; an inspection finding and devices added under finished counters (caught by 22fx.temperature-limits; industry_practice)
- **edu.fm.missed-window** — Hardware, HVAC equipment or casework approved late and delivered after the summer window closes → Work moves into occupied classrooms after hours with temporary systems, or the phase slips a full year (caught by edu.summer-window; field_experience)
- **edu.fm.agency-change-unapproved** — A substitution or field change accepted by the architect is never submitted to the state school-construction agency → The agency withholds certification or closeout of the project; work is reopened or occupancy delayed (caught by edu.agency-approvals; industry_practice)
- **edu.fm.default-risk-category** — Delegated cladding, joist or anchorage design done to the default risk category on a school assigned a higher one → Components under-designed; recalculation and field reinforcement after installation (caught by edu.risk-category-delegated; industry_practice)
- **edu.fm.adult-heights** — Fixtures, accessories and partitions in lower-grade toilet rooms installed at adult accessible heights, or the reverse → Elements unusable by the intended users or non-compliant; carriers, backing and accessories reset (caught by edu.childrens-dimensions; field_experience)

## Expected submittal contents
- **Product Data**
  - Each fixture tag with every component (fixture, seat, flush valve or tank, faucet and trim, supplies and stops, trap and tailpiece, carrier) and its mounting height
  - Accessible fixtures identified, with control type and location and under-lavatory pipe protection
  - Flow and flush rates and the certifications the spec requires
  - Power for sensor faucets and flush valves (battery, plug-in or hardwired transformer)

## Extract for reconciliation
- 22fx.xf.model — Fixture and trim models (string, per element) → schedule.plumbing_fixture
- 22fx.xf.mounting — Rim or seat height and mounting type (string, per element) → drawings.interior_elevations
- 22fx.xf.accessible — Accessible fixture (boolean, per element) → drawings.enlarged_plans
- 22fx.xf.flow — Flow or flush rate (string, per element) → schedule.plumbing_fixture
- 22fx.xf.power — Control type and power source (string, per element) → drawings.electrical

## Standards to verify against
- NSF/ANSI/CAN 61: Drinking Water System Components – Health Effects — Older specs cite it as NSF/ANSI 61; same standard
- NSF/ANSI/CAN 372: Drinking Water System Components – Lead Content — Older specs cite it as NSF/ANSI 372; same standard
- ASTM E84: Standard Test Method for Surface Burning Characteristics of Building Materials
- ASME A112.6.1M: Floor Affixed Supports for Off-the-Floor Plumbing Fixtures for Public Use
- ASSE 1070 / ASME A112.1070 / CSA B125.70: Water Temperature Limiting Devices
- ASSE 1016 / ASME A112.1016 / CSA B125.16: Automatic Compensating Valves for Individual Showers and Tub/Shower Combinations

## Warnings
- Draft knowledge in use (global, 22, 22 40 00) — not yet PE-reviewed
