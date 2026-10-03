# Compiled knowledge — 09 21 16 Gypsum Board Assemblies

Facility types: education.k12 · Confidence floor: **draft** · Review mode: per_element · Contractor-designed: sometimes
Lineage: global → 09 → [09 20 00 missing] → [09 21 00 missing] → 09 21 16
Overlays: education, education.k12
Also specified as: 09 22 16, 09 29 00

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Partitions, furring, shaft walls and gypsum board ceilings, with their framing (09 22 16 and 09 29 00 are reviewed as this assembly). The partition type is the unit of review: each type tagged on the plans is a listed fire design or tested sound assembly whose stud depth, thickness and spacing, board type and layers, fasteners, insulation and head condition have to match as built. What makes a partition fail is decided before close-in: height to structure, the deflection head, framing sized for the real height, boxes and sealing in sound-rated walls, recessed items in rated walls, and boards suited to wet and abuse exposure.

## Review checks (27)
### completeness
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] g.contractor-designed** — This scope is often performance-specified and designed or selected by the contractor. Confirm the spec's design criteria are complete enough to design to; whether the AHJ treats the design as a deferred submittal and when it must be filed relative to installation; and that the designer's assumptions about support, attachment and adjacent work are confirmed by the trades that provide them.  
  Trace: spec.part1, spec.part2 · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] d09.designation-coverage** — Every finish designation used on the finish plans, interior elevations, RCP and finish schedule (the legend codes for each floor, base, wall, ceiling and paint finish) maps to a submitted product, color and pattern, and every submitted product maps back to a designation. List codes used on drawings but missing from the schedule, schedule codes with no spec section, and submitted items nobody scheduled.  
  Trace: schedule.finish, drawings.material_legend, drawings.plans, drawings.interior_elevations, drawings.rcp · Owner: subcontractor · Scope: package · _09_
- **[high] edu.agency-approvals** — Where a state school-construction agency has jurisdiction, deferred submittals, substitutions and field changes that touch structure, fire and life safety or accessibility are approved by that agency before fabrication, not only by the architect, and the agency's inspector and testing requirements are in the inspection program.  
  Trace: spec.division_01, register.special_inspections, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.products-marked** — Cut sheets covering a product family have the proposed model, size, options, finish and accessories clearly marked; unmarked sheets are returned.  
  Trace: spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data · _global_
- **[medium] d09.acceptance-standard** — Where acceptance is a matter of appearance (lippage, gypsum finish under grazing light, paint uniformity, seam visibility, color variation between production lots), an approved mock-up or sample sets the standard before production work starts, with the viewing conditions (lighting, distance) it will be judged under, and the mock-up stays in place or is recorded until the work is accepted.  
  Trace: spec.part1, spec.part3 · Owner: gc · Scope: package · _09_
### conformance
- **[critical (reflex)] 09gb.listed-design-match** — Each fire-rated or sound-rated partition type is built exactly as its listed design or tested assembly: stud depth, thickness and spacing; board type, layers and orientation; fastener type and spacing; joint treatment; insulation; resilient channel or clips. A substituted component (another manufacturer's proprietary board, a lighter or "equivalent" stud, different insulation) is acceptable only where that design, or the component's own listing, covers it. Ratings against the life safety plans are reconciled under firestopping (07 84 00); this check is the build-up of each type.  
  Trace: schedule.partition_type, drawings.details, spec.part2 · Owner: subcontractor · Scope: element · _09 21 16_
- **[high] g.current-documents** — The submittal reflects the current contract documents, including addenda, ASIs, bulletins and responded RFIs, not the bid set. Note the drawing revision the submitter worked from.  
  Trace: drawings.revision_blocks, register.asi_bulletin_log, register.rfi_log · Owner: gc · Scope: package · _global_
- **[high] g.basis-of-design** — Proposed manufacturer and model match the basis of design or a listed acceptable manufacturer. Anything else follows the comparable-product or substitution procedure Division 01 allows, with its timing and comparison data, before it is reviewed on its merits.  
  Trace: spec.part2_manufacturers, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] g.deviations-identified** — Every deviation from the contract documents is clouded or listed by the submitter. Compare independently; do not rely on the submitter's list.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _global_
- **[high] 09gb.deflection-head** — Where the structure above deflects, the head uses deflection track or slip connections whose movement covers the structural design deflection, the board stops short of the deck by the joint the detail shows, and nothing locks the wall to the deck: board fastened into the track flange, ceiling hangers or MEP supports tied to the wall top. Non-rated heads need this as much as rated ones; rated joint systems are reviewed under 07 84 00.  
  Trace: drawings.details, drawings.structural, schedule.partition_type · Owner: subcontractor · Scope: element · _09 21 16_
- **[high] 09gb.framing-heights** — Stud depth, thickness and spacing for each type fall within the manufacturer's limiting-height table for the specified deflection criterion and lateral load, for the finish the wall carries (tile, stone and plaster need a stiffer criterion than paint), measured to the real support: to the deck when the wall runs above the ceiling. Heights beyond the tables, jambs and heads of large or heavy openings, and walls carrying heavy wall-mounted items are engineered, with bracing to structure shown.  
  Trace: schedule.partition_type, drawings.building_sections, drawings.wall_sections, spec.part2 · Owner: subcontractor · Scope: element · Gate: procurement_release · _09 21 16_
- **[high] 09gb.shaft-walls** — Shaft wall assemblies built from one side follow a listed design for the rating, the height between supports and the air pressure in the shaft (elevator hoistways see pressure from car movement), with openings for hoistway doors, call stations, access doors, ducts and dampers framed and protected as the listing allows, and they are built before ducts, risers or rails fill the shaft.  
  Trace: schedule.partition_type, drawings.life_safety, drawings.details, spec.part2 · Owner: subcontractor · Scope: package · Gate: overhead_rough_in · _09 21 16_
- **[medium] 09gb.finish-level** — The gypsum finish level is set per surface by the industry finish-level standard the spec cites, and the higher level is carried where surfaces get critical light (wall-washers and grazing fixtures on the lighting plans, long corridors, walls beside large glazing), gloss or semi-gloss paint, or thin wall coverings. A level chosen for normal light on a critically lit wall is raised before taping, not at punch.  
  Trace: spec.part3, schedule.finish, drawings.rcp, schedule.lighting_fixture · Owner: design_team · Scope: package · _09 21 16_
- **[medium] 09gb.control-joints** — Control joints in walls and gypsum ceilings are located on the drawings or shop drawings: at the spacing the spec or board manufacturer limits, at changes of framing or substrate, from the corners of door and window openings, at long ceiling runs and wings, and at every building expansion joint, which partitions and ceilings must not bridge. Rated types show the joint detail their listing allows.  
  Trace: drawings.interior_elevations, drawings.rcp, drawings.details, drawings.structural · Owner: design_team · Scope: package · _09 21 16_
- **[medium] edu.maintenance-durable-finishes** — Corridor, gym, cafeteria and restroom finishes are the abuse-resistant products scheduled (impact-resistant board or masonry to the scheduled height, wall and corner guards), and floor finishes suit the owner's maintenance program (stripped and waxed, or no-wax) so the first cleaning cycle does not void the warranty. A standard product in these spaces is a substitution even when color and pattern match.  
  Trace: schedule.finish, spec.part2 · Owner: subcontractor · Scope: element · _overlay:education_
### coordination
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
- **[high] 09gb.recessed-in-rated** — Items recessed into rated walls (fire extinguisher cabinets, recessed toilet accessories, medicine cabinets, panelboards, access doors, dryer and valve boxes) are rated products or are backed by construction that keeps the wall's rating, fit the stud depth, and have their rough openings framed as the listed design allows.  
  Trace: schedule.partition_type, drawings.life_safety, drawings.plans, schedule.toilet_accessories · Owner: gc · Scope: package · Gate: wall_close_in · _09 21 16_
### constructability
- **[high] d09.building-conditions** — The temperature, humidity, acclimation and enclosure each finish product requires before and after installation (joint compound, acoustical panels, wood, resilient flooring and adhesives, paints, wall coverings) are compared with the schedule dates for dry-in, permanent HVAC start-up and wet-work completion. Where finishes start before permanent HVAC, the temporary conditioning that holds those limits is planned and assigned.  
  Trace: spec.part1, spec.part3, schedule.master · Owner: gc · Scope: package · Gate: interior_finish_start · _09_
- **[high] 09gb.sound-rated-walls** — In sound-rated partitions the details that make the tested rating hold in the field are shown and assigned: acoustical sealant at the perimeter and every penetration on both faces; outlet boxes on opposite faces in different stud bays at the separation the acoustic design requires, or backed with putty pads; no back-to-back recessed cabinets or panels; resilient channel or clips not short-circuited by fasteners; and ducts and transfer openings through the wall lined or offset as the acoustic design requires.  
  Trace: schedule.partition_type, report.acoustical, drawings.electrical, spec.part3 · Owner: gc · Scope: element · Gate: wall_close_in · _09 21 16_
- **[high] edu.summer-window** — Where work in existing schools must fit a break in the academic calendar, each submittal's approval, owner selections, mock-ups and delivery are dated against the day the window opens, not against a floating schedule activity. Long-lead items (door frames and hardware, HVAC equipment, switchgear, casework, flooring) that miss the window push work into occupied classrooms or a year later, so their submittals are released first.  
  Trace: schedule.master, spec.division_01 · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
### absence
- **[high] 09gb.head-defined** — For each partition type the head is defined (to structure, to ceiling, or above ceiling by a stated amount), and walls that must stop sound, smoke, security or plenum air, not only fire, are typed to structure. A head detail exists for every deck condition those walls meet: flutes parallel and perpendicular, beams, joists, and ducts or trays crossing the head.  
  Trace: schedule.partition_type, drawings.details, drawings.building_sections, drawings.rcp · Owner: design_team · Scope: element · Gate: overhead_rough_in · _09 21 16_
- **[high] 09gb.exposure-boards** — Board types match exposure: a backer the tile method accepts behind tile in showers and wet areas, moisture- and mold-resistant board in high-humidity rooms and at sinks, abuse- or impact-resistant board where carts, beds or traffic hit walls (corridors, gyms, loading and service areas), and glass-mat or exterior-rated board where it will be exposed to weather before dry-in. Rooms with these exposures but a standard board type in the partition schedule are raised before framing.  
  Trace: schedule.partition_type, schedule.finish, drawings.enlarged_plans, spec.part2 · Owner: design_team · Scope: element · Gate: procurement_release · _09 21 16_
- **[high] 09gb.access-doors** — Every concealed item behind gypsum walls and above gypsum ceilings that needs service or inspection (valves, fire and smoke dampers, terminal units, cleanouts, trap primers, junction boxes, controllers) has an access door on the RCP or elevations, sized for the work, rated where the wall or ceiling is rated, and framed before board. Doors cut in after close-in are a finding, not a fix.  
  Trace: drawings.rcp, drawings.mechanical, drawings.plumbing, drawings.electrical · Owner: gc · Scope: package · Gate: above_ceiling_close_in · _09 21 16_
- **[medium] d09.unscheduled-spaces** — Spaces the finish schedule skips or marks "unfinished" (mechanical, electrical and telecom rooms, shafts, stairs, elevator machine rooms, janitor closets, storage, exterior soffits) still have a defined floor, base, wall and ceiling treatment, such as sealed or coated concrete and painted walls and structure, where the use needs one. Dust-free floors in electrical and telecom rooms and cleanable surfaces in wet rooms are the usual omissions.  
  Trace: schedule.finish, drawings.plans, spec.part3 · Owner: design_team · Scope: package · _09_

## Reconciliations — documents that must agree (3)
- **[high] 09gb.rc.type-tags** — Every partition tag on plans and enlarged plans is defined in the partition schedule and every scheduled type is used; untagged walls are listed. The submittal carries each type with the scheduled build-up.  
  Between: drawings.plans ↔ drawings.enlarged_plans ↔ schedule.partition_type · Key: Partition type tag · Fields: tag defined in the schedule, stud depth and spacing, board type and layers per face, head condition, sound rating, insulation · Owner: design_team · Gate: procurement_release · _09 21 16_
- **[high] 09gb.rc.acoustic-separations** — Each room adjacency with a sound criterion in the acoustic report or spec is separated by a partition type whose tested rating meets it, that runs to structure or stops at a ceiling the acoustic design accepted, and whose doors, transfer openings and ducts are accounted for.  
  Between: report.acoustical ↔ schedule.partition_type ↔ drawings.plans ↔ drawings.rcp · Key: Wall between two rooms with a sound criterion · Fields: required sound rating, partition type and its tested rating, head condition, ceiling attenuation where the wall stops at the ceiling, doors and openings in the wall · Owner: design_team · Gate: overhead_rough_in · _09 21 16_
- **[medium] d09.rc.room-finishes** — Room by room, the finish schedule, finish plans, RCP and interior elevations name the same room and agree on floor, base, each wall, ceiling type and ceiling height. Rooms added, split or renumbered by a revision and rooms that appear in one document only are listed.  
  Between: schedule.finish ↔ drawings.plans ↔ drawings.rcp ↔ drawings.interior_elevations · Key: Room number · Fields: room name, floor and base designation, wall designation for each wall and accent wall, ceiling type, ceiling height · Owner: design_team · Gate: procurement_release · _09_

## Compliance — regulatory hooks (5)
- **[high] 09gb.rh.rated-wall-continuity** (`rated-wall-continuity`) — For each kind of rated wall on this project (fire wall, fire barrier, shaft enclosure, fire partition, smoke barrier, smoke partition), must it run to the floor or roof deck above under the adopted code, or may it stop at a rated ceiling membrane, and what has to continue above the ceiling or through concealed spaces?  
  **Unbound** → Run /construction:code-researcher with research topic "rated-wall-continuity" (seed it with this hook's question)
- **[high] edu.rh.school-agency-review** (`school-construction-agency-review`) — Does a state agency other than the local building department review plans, approve changes or inspect construction for this school (common for public K-12 and in some states for community colleges), and what does it require for deferred submittals, change documents, testing laboratories and the inspector of record?  
  **Unbound** → Run /construction:code-researcher with research topic "school-construction-agency-review" (seed it with this hook's question)
- **[medium] d09.rh.voc-emissions** (`architectural-coatings-adhesives-voc`) — Which VOC content limits (regional air quality rules) and emissions testing (a green building code or certification the project follows) apply to the paints, coatings, flooring adhesives, sealers, ceiling panels and other finish products submitted, and do the product data show compliance for each?  
  **Unbound** → Run /construction:code-researcher with research topic "architectural-coatings-adhesives-voc" (seed it with this hook's question)
- **[medium] 09gb.rh.partition-deflection** (`interior-partition-deflection-criteria`) — What lateral load and deflection limit does the adopted code set for interior partitions, does the spec tighten it for brittle finishes (tile, stone, plaster), and are the submitted limiting heights based on those values?  
  **Unbound** → Run /construction:code-researcher with research topic "interior-partition-deflection-criteria" (seed it with this hook's question)
- **[medium] 09gb.rh.board-inspection** (`lath-gypsum-board-inspection`) — Does the AHJ require an inspection of gypsum board fastening (in rated or shear assemblies) or of lath before taping or plastering covers it, and who calls it?  
  **Unbound** → Run /construction:code-researcher with research topic "lath-gypsum-board-inspection" (seed it with this hook's question)

## Coordination routing (21)
- **[critical] if.06-backing-metal-stud** → Rough carpentry (blocking and backing) (06 10 53) · Gate: wall_close_in — Checked against the master list before second-side board
  - Send them: Stud spacing and gauge at backing locations, metal backing plates or straps where the partition type requires metal, and walls left open on one side until backing is in and checked
  - Need from them: The blocking master list by room and wall, with backing type, height, extent and fire-retardant treatment where required
  - Confirm who: Wood blocking and metal backing in metal-stud walls — typical furnish 06 10 53 or 09 22 16 / install 06 10 53 or 09 22 16
- **[critical] if.firestop-rated-walls** → Firestopping (07 84 00) · Gate: overhead_rough_in
  - Send them: Rated walls boarded full height to structure before penetrating trades pass through them
  - Need from them: Listed systems that assume clean openings in finished boards; installation and inspection area by area
  - If missed: MEP trades rough through rated walls before the walls are boarded to structure
- **[high] if.01-temporary-conditions-finishes** → Temporary facilities (enclosure, heat and humidity control) (01 50 00) · Gate: interior_finish_start — Slabs dry only in an enclosed, conditioned building, so conditioning has to start with drywall finishing, not with flooring
  - Send them: Ambient, substrate and slab-moisture limits for application and cure, and the slab moisture testing that releases flooring
  - Need from them: Enclosure and conditioning that let slabs dry and hold application and cure limits, with heat that adds no moisture where specified
  - If missed: Wood doors, casework, wood or resilient flooring delivered and installed before the building holds temperature and humidity
- **[high] if.head-of-wall-joints** → Firestopping (07 84 00) · Gate: procurement_release — The design deflection comes from the structural drawings, not from the framer
  - Send them: Deflection track type, installed joint width, and deck profile and orientation at each head of wall
  - Need from them: Listed joint system whose movement rating covers the structural design deflection, for the wall type and deck orientation
  - If missed: Head-of-wall joint system not rated for the movement of the deflection track below it
- **[high] if.08-frames-partitions** → Doors and frames (08 10 00) · Gate: procurement_release — Throat and anchors are fabricated in; welded frames must then be set before the first layer of board
  - Send them: Partition type at each opening (stud size, board layers each side, added finishes), jamb and header framing for the door's weight and hardware, and frames set and braced before the first board where welded
  - Need from them: Frame profile, throat and anchor type per opening, and whether each frame is set before board (welded) or after (knock-down)
  - Confirm who: Setting welded frames in stud partitions — typical install 08 11 13 installer or 09 22 00
  - Confirm who: Grouting frames in stud partitions where the spec requires it — typical install 09 21 00 or 08 11 13 installer
  - If missed: Frame throat sized to the nominal stud without the board layers or added finishes on each side
- **[high] if.08-access-doors-mep** → Access doors and panels (08 31 00) · Gate: above_ceiling_close_in
  - Send them: Location and required size of every concealed device that needs service, taken from approved MEP submittals; framed openings in board walls and ceilings
  - Need from them: Door sizes, ratings and frame types for each substrate
  - Confirm who: Furnishing access doors for MEP devices — typical furnish 08 31 00 or each MEP trade / install 09 21 00
  - If missed: Valves, dampers or terminal units above hard ceilings or inside chases with no access door
- **[high] if.09-ceiling-sprinklers** → Fire-suppression sprinklers (21 13 00) · Gate: overhead_rough_in — Branch lines and drops follow the coordinated RCP, not a grid assumed on the sprinkler shop drawings
  - Send them: Coordinated ceiling layout (module, datum, heights, clouds, soffits and bulkheads) and the clearance the ceiling's seismic design needs around each head
  - Need from them: Head locations set to that layout, drop type and length, flexible drops or oversized escutcheons where the seismic design requires them, and heads finished only after grid or board is fixed
  - Confirm who: Final head position and drop length to the finished ceiling — typical install 21 13 00
  - If missed: Sprinkler drops cut and installed before the ceiling layout was coordinated; Braced ceiling installed around sprinkler heads on rigid drops with no clearance
- **[high] if.09-plenum-return-walls** → HVAC ductwork, air outlets and dampers (23 31 00, 23 37 00, 23 33 00) · Gate: overhead_rough_in — Transfer openings are framed while the wall is boarded to structure, before ductwork arrives
  - Send them: Partitions running to structure across a ceiling return plenum (rated, acoustic, security), and framed openings where transfers pass through them
  - Need from them: Return-air transfer ducts or openings through those walls, with fire or smoke dampers in rated walls and lined or offset transfers in sound-rated walls
  - If missed: Full-height walls cut off the return plenum; rooms are starved or noisy, and transfers are cut into rated or sound-rated walls after the fact
- **[high] if.09-fixture-carriers** → Commercial plumbing fixtures and carriers (22 42 00) · Gate: in_wall_rough_in
  - Send them: Chase walls framed to the depth the carriers need, with studs laid out clear of carrier uprights and floor anchors
  - Need from them: Carrier models, the chase depth they need, floor anchoring, and rough-in heights for wall-hung fixtures, set before close-in
  - If missed: Chase framed too shallow for the carriers, or carriers set after board; plumbing walls rebuilt or fixtures hung on backing never designed for the load
- **[high] if.09-tile-backer** → Tiling (09 30 00) · Gate: wall_close_in
  - Send them: Backer installed to that method's type, fastening and flatness, with joints treated as the method requires
  - Need from them: Installation method per tiled wall, which sets the backer type, fastening, flatness and any membrane over it
  - Confirm who: Cementitious, fiber-cement or glass-mat backer behind wall tile — typical furnish 09 21 16 or 09 30 00 / install 09 21 16 or 09 30 00
- **[high] if.09-recessed-specialties** → Toilet accessories and fire protection cabinets (10 28 13, 10 44 13) · Gate: wall_close_in
  - Send them: Stud depth, wall thickness and finish build-up (backer and tile) at each location, which walls are rated, and rough openings framed as the wall's listed design allows
  - Need from them: Recessed and semi-recessed models with rough-opening size and depth, trim and anchors sized for the finish thickness, mounting heights, and rated cabinets or accessories where the wall is rated
- **[high] if.09-partition-plenum-barrier** → Operable, folding and demountable partitions (10 22 00) · Gate: above_ceiling_close_in — The barrier goes in after the track and before the ceiling closes along it
  - Send them: Sound barrier from the partition track or head to the structure, built to the rating the acoustic design needs, and the ceiling closure and trim along the track
  - Need from them: Track and stack layout, head and seal details, the rating the barrier above has to match, and the support the track needs from structure
  - Confirm who: Sound barrier above the partition track — typical furnish 09 21 16 / install 09 21 16
  - If missed: Barrier above the track carried by neither subcontract; sound flanks over a high-rated partition through the plenum
- **[high] if.09-hoistway-shaft-wall** → Elevators (14 20 00) · Gate: hoistway_turnover — Openings, bracket supports and fixture boxes are fixed when the hoistway goes to the elevator installer
  - Send them: Hoistway shaft wall built to a listed design for the rating and the hoistway air pressure, with entrance openings framed to the frame size and the frame anchor detail the wall's listing allows, framing and liner penetrations treated at each rail bracket support, and protected boxes for hall fixtures
  - Need from them: Entrance frame sizes and anchor details for the shaft wall type, rail bracket levels and forces, hall call and lantern box locations, and the hoistway pressure the wall must resist
  - Confirm who: Entrance frame anchorage and reinforcement at shaft wall openings — typical install 14 20 00 or 09 21 16
- **[medium] if.05-partition-heads** → Structural steel, joists and deck (05 12 00, 05 21 00, 05 31 00) · Gate: procurement_release — The deflection value comes from the engineer of record, not from the framer
  - Send them: Head details with movement for that deflection, and bracing to structure where a wall runs parallel to deck flutes, between joists or under a joist bottom chord
  - Need from them: Design deflection of the floor or roof above each partition line, including cantilevers and long spans, and the rules for fastening top track and bracing to joists and deck
  - If missed: Partition tops braced to joist bottom chords or screwed into deck flutes that cannot take the load, or heads built tight under long spans; cracked partitions and joists loaded in ways they were not designed for
- **[medium] if.acoustical-sealant-partitions** → Acoustical joint sealants (07 92 19) · Gate: wall_close_in — Sealant at the first board layer and the runners is inaccessible once the next layer goes on
  - Send them: Which partitions are sound-rated and to what tested assembly, board layer sequence, and when each layer closes
  - Need from them: Sealant product matching the tested assembly, and where it goes (runners, perimeter, each board layer, penetrations and boxes)
  - Confirm who: Acoustical sealant at perimeters, layers and penetrations of sound-rated partitions — typical furnish 07 92 19 or 09 21 16 / install 07 92 19 or 09 21 16
  - If missed: Each trade assumes the other seals the sound-rated walls; the perimeter and box penetrations are left open and field sound tests fail
- **[medium] if.09-ceiling-air-devices** → Air outlets and inlets; duct accessories (23 37 00, 23 33 00) · Gate: procurement_release — Air devices are ordered by border type, which follows the ceiling type at each location
  - Send them: Ceiling type, module and edge at each outlet (lay-in, tegular, concealed grid, gypsum), grid load limits, and which ceilings are rated membranes
  - Need from them: Outlet frame and border type and size matched to each ceiling type, independent support for heavy units, and ceiling radiation dampers at outlets in rated ceilings
  - If missed: Light fixtures or air outlets set in a rated ceiling membrane without the protection or ceiling radiation dampers its design requires
- **[medium] if.09-ceiling-lighting** → Interior, emergency and exit lighting (26 51 00, 26 52 00) · Gate: procurement_release — Fixture trims are ordered to the ceiling type; trimless fixtures need frames set before taping
  - Send them: Ceiling type, grid profile, module and plenum depth at each fixture location, and which ceilings are rated membranes
  - Need from them: Fixture trim and mounting for each ceiling type (lay-in, flanged, trimless, surface), housing depth, weight and independent support, protection or listing for rated ceilings, and the wall-washer and grazing fixtures that set the gypsum finish level
  - If missed: Light fixtures or air outlets set in a rated ceiling membrane without the protection or ceiling radiation dampers its design requires
- **[medium] if.09-ceiling-low-voltage** → Audio-video, public address, wireless access points, cameras and fire alarm devices (27 41 16, 27 51 16, 27 21 33, 28 21 00, 28 46 00) · Gate: overhead_rough_in
  - Send them: Ceiling layout and types, including clouds, soffits and open areas where devices cannot mount on tile
  - Need from them: Device locations on the RCP, mounting method (tile bridge, support from structure, back box in board), weight, and detector placement that still meets the alarm design once soffits, beams and clouds are known
  - If missed: Devices placed on panels that cannot carry them, or detectors and speakers relocated after the ceiling is built because the layout changed under them
- **[medium] if.09-boxes-in-sound-walls** → Electrical boxes and wiring devices, communications backboxes, fire alarm devices (26 05 33, 26 27 26, 27 05 33, 28 46 00) · Gate: wall_close_in
  - Send them: Which partition types are sound-rated or rated, and the box separation, pads and sealing their tested design or acoustic design requires
  - Need from them: Box locations on both faces of those walls, box type, and pads or sealing installed before the second face is boarded
  - If missed: Boxes set back to back in rated or acoustically rated walls without the listed protection or offset
- **[medium] if.09-toilet-compartments** → Toilet compartments (10 21 13) · Gate: wall_close_in — Overhead support for ceiling-hung units is gated earlier, under the toilet compartment section
  - Send them: Floor and wall finish and its thickness at compartment lines, backing for brackets and pilasters, and the ceiling layout around overhead-braced or ceiling-hung units
  - Need from them: Mounting style, pilaster and bracket layout, anchor type and embedment through tile, and the overhead support the units need
  - If missed: Anchors drilled through tile without a layout, cracking it, or ceiling-hung units with no support coordinated with the ceiling
- **[medium] if.09-ceiling-pockets** → Window shades, blinds and recessed projection screens (12 24 00, 12 21 00, 11 52 13) · Gate: above_ceiling_close_in
  - Send them: Ceiling pockets and soffits at windows and screens, framed and detailed with access to motors
  - Need from them: Pocket dimensions for the product chosen, mounting and backing, and power and control locations for motorized units
  - If missed: Shades or screens ordered for a pocket that was never framed, or motorized units with no power, support or access in the ceiling

## Failure modes to watch (24)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d09.fm.room-renumbered** — Finish schedule keyed to room numbers that a later revision changed; finishes ordered and installed to the old numbers → Wrong flooring or wall finish in finished rooms; replacement at the end of the job (caught by d09.rc.room-finishes; industry_practice)
- **d09.fm.unconditioned-install** — Finishes installed before permanent or temporary HVAC holds the manufacturers' temperature and humidity limits → Sagging ceiling panels, joint cracking, adhesive failure, cupped wood; warranty claims denied (caught by d09.building-conditions; industry_practice)
- **d09.fm.no-acceptance-standard** — Appearance disputes (lippage, wall flatness under raking light, color shift between lots) with no approved mock-up to judge against → Rework argued after installation; the owner's standard becomes whatever the punch list says (caught by d09.acceptance-standard; field_experience)
- **d09.fm.unscheduled-room** — Electrical, telecom and mechanical rooms left with bare concrete and unpainted walls because the finish schedule skipped them → Concrete dust in electrical and IT equipment; sealing and painting added around installed equipment (caught by d09.unscheduled-spaces; field_experience)
- **09gb.fm.design-drift** — Rated partition built with a substituted board, an "equivalent" stud or different insulation not covered by its listed design → Wall fails inspection or quietly loses its rating; rebuilt after finishes (caught by 09gb.listed-design-match; industry_practice)
- **09gb.fm.stud-sized-to-ceiling** — Stud size picked from the ceiling height on a wall that continues to the deck → Wall exceeds its limiting height; it flexes, cracks tile and joints, and gets reinforced after board is up (caught by 09gb.framing-heights; field_experience)
- **09gb.fm.head-locked** — Board screwed into the deflection track flange, or ceiling hangers and MEP supports fastened to the wall head → Floor deflection crushes or cracks the wall; rated head joints fail inspection (caught by 09gb.deflection-head, if.head-of-wall-joints; field_experience)
- **09gb.fm.stopped-at-ceiling** — Acoustic, security or plenum-separating wall stopped at the ceiling because only fire ratings were checked for height → Sound flanks over the wall and privacy complaints follow occupancy; walls extended through finished MEP (caught by 09gb.head-defined, 09gb.rc.acoustic-separations; field_experience)
- **09gb.fm.back-to-back-boxes** — Outlet boxes back to back in one stud bay, or perimeter left unsealed, in a sound-rated wall → Field sound isolation far below the design; walls opened in occupied rooms to fix it (caught by 09gb.sound-rated-walls, if.09-boxes-in-sound-walls; field_experience)
- **09gb.fm.standard-board-wet** — Standard paper-faced board installed in showers, janitor closets, behind tile in wet areas, or left exposed to weather before dry-in → Mold and tile failure; walls replaced after occupancy (caught by 09gb.exposure-boards, if.09-tile-backer; industry_practice)
- **09gb.fm.finish-level-under-light** — Walls under wall-washers or grazing daylight finished to the level chosen for normal light → Every joint and fastener shows; skim-coating and repainting at the end of the job (caught by 09gb.finish-level; field_experience)
- **09gb.fm.recessed-in-rated** — Non-rated recessed cabinet or accessory set into a rated corridor or shaft wall → Inspection failure; cabinets replaced or the wall rebuilt around them (caught by 09gb.recessed-in-rated, if.09-recessed-specialties; field_experience)
- **09gb.fm.no-access-hard-ceiling** — Dampers, valves or terminal units above a gypsum ceiling with no access door → Ceiling cut at damper inspection or first service; patching in finished rooms (caught by 09gb.access-doors, if.08-access-doors-mep; field_experience)
- **09gb.fm.shaft-late** — Shaft wall left until ducts, risers or rails occupy the shaft → Liner panels cannot be set from the one accessible side; listed design abandoned for field fixes (caught by 09gb.shaft-walls; industry_practice)
- **09gb.fm.hoistway-openings** — Hoistway shaft wall closed with entrance openings framed off size, no tested frame anchor detail, or no support at rail bracket levels → Hoistway walls opened after turnover; elevator installation and inspection slip (caught by 09gb.shaft-walls, if.09-hoistway-shaft-wall; industry_practice)
- **09gb.fm.expansion-joint-bridged** — Partitions or gypsum ceilings built continuous across a building expansion joint → Recurring cracks along the joint line that no repair holds (caught by 09gb.control-joints; industry_practice)
- **09gb.fm.backing-missed** — Backing for a wall-mounted item missing when the second face is boarded → Finished wall opened, patched and repainted; item installed late (caught by if.06-backing-metal-stud; industry_practice)
- **edu.fm.missed-window** — Hardware, HVAC equipment or casework approved late and delivered after the summer window closes → Work moves into occupied classrooms after hours with temporary systems, or the phase slips a full year (caught by edu.summer-window; field_experience)
- **edu.fm.agency-change-unapproved** — A substitution or field change accepted by the architect is never submitted to the state school-construction agency → The agency withholds certification or closeout of the project; work is reopened or occupancy delayed (caught by edu.agency-approvals; industry_practice)
- **edu.fm.flooring-maintenance** — Resilient flooring selected or substituted without regard to the district's strip-and-wax or no-wax maintenance → Warranty voided by the first maintenance cycle, or a finish that degrades within the first school year (caught by edu.maintenance-durable-finishes; field_experience)

## Expected submittal contents
- **Product Data**
  - Studs and track by type with depth, thickness and flange, and the limiting-height tables used, at the project's deflection criterion and lateral load
  - Each board type with its classification (fire-rated core, moisture- and mold-resistant, abuse- or impact-resistant, glass-mat, shaft liner, backer)
  - Deflection track, slip clips and head-of-wall components with the movement they allow
  - Acoustical sealant, putty pads, resilient channel or clips where used, traced to the tested assembly they belong to
- **Design Data**
  - For every partition type, the listed fire design and tested sound assembly it follows, with each submitted component identified in that design
  - Framing for heights beyond the manufacturer's tables, heavy wall-mounted loads and unbraced openings, engineered where the spec requires
- **Shop Drawings**
  - Head-of-wall details for each partition type at each deck condition (flutes parallel and perpendicular, beams, joists)
  - Bulkheads, soffits, gypsum ceilings and tall walls with spans, bracing to structure and the connection to the deck
  - Control joint layout on walls and ceilings

## Extract for reconciliation
- 09gb.xf.listed-design — Listed fire design and tested sound assembly per partition type (list, per element) → schedule.partition_type
- 09gb.xf.framing — Stud depth, thickness and spacing per partition type (string, per element) → schedule.partition_type
- 09gb.xf.board — Board type and layers on each face (string, per element) → schedule.partition_type
- 09gb.xf.limiting-height — Limiting height used, with its deflection criterion and lateral load (string, per element) → drawings.building_sections, schedule.partition_type
- 09gb.xf.head — Head condition and deflection track movement (string, per element) → drawings.details, drawings.structural

## Standards to verify against
- ASTM C645: Nonstructural Steel Framing Members
- ASTM C754: Installation of Steel Framing Members to Receive Screw-Attached Gypsum Panel Products
- ASTM C840: Application and Finishing of Gypsum Board
- ASTM C1396/C1396M: Gypsum Board
- ASTM C1629/C1629M: Abuse-Resistant Nondecorated Interior Gypsum Panel Products and Fiber-Reinforced Cement Panels
- ASTM C1658/C1658M: Glass Mat Gypsum Panels
- ASTM D3273: Resistance to Growth of Mold on the Surface of Interior Coatings in an Environmental Chamber
- GA-214: Recommended Levels of Finish for Gypsum Panel Products
- GA-600: Fire Resistance and Sound Control Design Manual
- ASTM E90 / ASTM E413 / ASTM E336: Laboratory transmission loss, sound insulation rating, and field measurement of airborne sound attenuation between rooms
- ASTM C919: Use of Sealants in Acoustical Applications

## Warnings
- Draft knowledge in use (global, 09, 09 21 16) — not yet PE-reviewed
