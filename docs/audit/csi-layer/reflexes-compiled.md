# Reflex checks — always on (37)

Notice these while looking at anything, even when they are unrelated to the question. Each lives in the file shown; resolve that section for the full context.

## Division 01
- **[critical (reflex)] 01qr.inspection-before-cover** — Work requiring special inspection or testing is not concealed (concrete placed, cells grouted, steel fireproofed, walls boarded, trenches backfilled) until the inspection is done and recorded. Ask for the inspector's report for the area, not the trade's word that the inspector was there.  
  Trace: register.special_inspections, spec.division_01 · Owner: gc · _01 40 00_
- **[high (reflex)] 01tf.conditioning-before-finishes** — The building is enclosed, wet work is dry, and temperature and humidity are held within the limits the woodwork, flooring and finish sections and their manufacturers require, continuously from before delivery through installation and acclimation. Where permanent HVAC will not run in time, temporary heat that adds no moisture (indirect-fired or electric, where the spec requires it), dehumidification and recorded monitoring are in the plan.  
  Trace: spec.division_01, spec.part1, schedule.master · Owner: gc · Gate: interior_finish_start · _01 50 00_

## Division 02
- **[critical (reflex)] 02dm.services-live** — Every utility in the demolition area is marked as removed, capped and abandoned, or kept live. Services that pass through to areas staying in use are traced, protected and labeled before demolition, and each disconnect is verified dead by the trade that made it.  
  Trace: drawings.demolition, drawings.plumbing, drawings.mechanical, drawings.electrical, drawings.fire_protection · Owner: gc · Gate: demolition_start · _02 41 00_
- **[critical (reflex)] 02dm.structural-sequence** — Load-bearing walls, columns, beams, slabs and bracing come out in an engineered sequence: temporary shoring designed and installed, new supporting members in place first where the design requires, and the engineer of record's acceptance of the sequence. Elements that look non-structural (infill walls, partitions under old transfer conditions, roof bracing) are confirmed before removal.  
  Trace: drawings.structural, drawings.demolition · Owner: gc · Gate: demolition_start · _02 41 00_
- **[critical (reflex)] d02.hazmat-survey-scope** — A hazardous materials survey covers the full extent of disturbance (every area of demolition, cutting, coring and MEP removal, including roofing, flooring layers and concealed spaces), lists the materials it assumed rather than sampled and the areas it could not reach, and post-dates the last change to the demolition scope. Gaps are sampled before the work, not discovered during it.  
  Trace: report.hazmat_survey, drawings.demolition · Owner: owner · Gate: demolition_start · _02_

## Division 03
- **[critical (reflex)] 03cip.cast-in-before-pour** — Before each placement, every item cast into or passing through the concrete (anchor rods, embed plates, sleeves, conduit, floor boxes, inserts, dowels, waterstops, grounding electrodes, blockouts) is located from the approved shop drawings of the trade that needs it, not the bid drawings, and surveyed by every discipline. An item with no approved shop drawing by the pour date is a hold point, not a field decision.  
  Trace: drawings.structural, drawings.foundation, drawings.plumbing, drawings.electrical, drawings.mechanical, submittals.approved · Owner: gc · Gate: foundation_pour · _03 30 00_
- **[critical (reflex)] d03.coring-scanning** — No coring, sawcutting or drilling of placed structural concrete (slabs, beams, walls, post-tensioned slabs, precast and prestressed members) without the location and size accepted by the engineer of record and the area scanned for reinforcing, tendons, strands and embedded conduit first. Penetrations added after the pour are routed this way even when small, and the procedure is written into the MEP and tenant scopes.  
  Trace: spec.part3, spec.division_01, drawings.structural · Owner: gc · _03_
- **[high (reflex)] 03cip.rc.depressions** — Every area with a thicker floor assembly (thick-set tile, tile over a waterproofing or crack-isolation membrane, terrazzo, recessed entrance mats, shower floors and sloped beds to floor drains, walk-in coolers) has a structural depression equal to the full assembly depth over its full extent, so the finish meets the adjacent floor flush.  
  Between: schedule.finish ↔ drawings.plans ↔ drawings.enlarged_plans ↔ drawings.structural · Key: Room or floor area whose finish assembly differs in thickness from the base floor · Fields: total assembly thickness (setting bed, membrane, mat, terrazzo, topping), depression depth, extent, slope to drains, transition at doors · Owner: design_team · Gate: slab_pour · _03 30 00_

## Division 04
- **[critical (reflex)] d04.flashing-every-interruption** — At every horizontal interruption of a masonry wall (base of wall, shelf and relief angles, lintels and heads, sills, copings and wall caps, roof-to-wall intersections, and over louvers and other penetrations) the details show through-wall flashing carried past the face with a drip, end dams wherever the flashing stops, sealed laps, its termination on the backup lapped under the air and water barrier above, and weeps at that level. An interruption with no such detail is a finding.  
  Trace: drawings.wall_sections, drawings.details, drawings.exterior_elevations · Owner: design_team · Gate: procurement_release · _04_
- **[high (reflex)] 04um.movement-joints** — Expansion joints in clay masonry and control joints in concrete masonry are located on the elevations, not left to a spacing note: at corners, offsets, openings, changes in wall height or backup, and wherever clay and concrete units meet in the same wythe. The details keep the joint free of mortar, stop the joint reinforcement, give the filler and sealant, and use anchors that let the veneer move independently of its backup.  
  Trace: drawings.exterior_elevations, drawings.plans, drawings.details · Owner: design_team · Gate: procurement_release · _04 20 00_

## Division 05
- **[critical (reflex)] 05jst.rc.concentrated-loads** — Every unit, fan, tank, coil, main, cable tray, solar array and hung partition the other disciplines put on or under joists appears in the joist loading at its operating weight and location, including equipment approved or relocated after the structural design.  
  Between: schedule.mechanical_equipment ↔ drawings.mechanical ↔ drawings.plumbing ↔ drawings.fire_protection ↔ drawings.electrical ↔ drawings.structural ↔ submittals.approved · Key: Each item carried by joists (equipment tag, main, array, partition track) · Fields: operating weight, location, support method (curb, rails, dunnage, hung), joist or girder it lands on, load shown on the structural drawings · Owner: design_team · Gate: procurement_release · _05 21 00_
- **[high (reflex)] 05dk.rc.openings** — Every floor and roof opening on the architectural and MEP drawings (shafts, duct and pipe chases, roof drains and sumps, curbs, hatches, stair and equipment openings) is on the structural drawings with framing, or the typical reinforcement detail its size allows.  
  Between: drawings.plans ↔ drawings.roof_plan ↔ drawings.mechanical ↔ drawings.plumbing ↔ drawings.structural · Key: Opening or penetration through floor or roof deck · Fields: location, size, framing or reinforcement detail, who cuts it and when · Owner: design_team · Gate: procurement_release · _05 31 00_

## Division 06
- **[critical (reflex)] 06rc.blocking-master-list** — A blocking and backing master list is assembled by room and wall from every source, because no single drawing shows it: toilet accessories and grab bars, casework and countertop supports, wall-hung plumbing fixtures, handrails and guards, door stops and wall-mounted hardware, shelving, markerboards, displays, projectors and speakers, wall-hung equipment, and owner-furnished items. Each entry has a backing type, height and extent, and is checked in place before second-side board.  
  Trace: drawings.interior_elevations, drawings.enlarged_plans, drawings.details, schedule.toilet_accessories, schedule.casework, schedule.equipment, drawings.technology · Owner: gc · Gate: wall_close_in · _06 10 00_
- **[high (reflex)] 06tr.rc.equipment-loads** — Every mechanical unit, fan and heater set on or hung from trusses appears in the truss designs at its location and operating weight, using the approved equipment, not the basis of design if it has since changed.  
  Between: schedule.mechanical_equipment ↔ submittals.approved ↔ drawings.mechanical ↔ drawings.structural · Key: Each unit or load supported by trusses · Fields: operating weight, location, support method (curb, platform, hung), load in the truss design at that location · Owner: gc · Gate: procurement_release · _06 17 53_

## Division 07
- **[critical (reflex)] tp.wall-fire-test-assembly** — Where the exterior wall needs to pass a fire propagation test, the submitted barrier, continuous insulation, sheathing and cladding appear together in the tested assembly or engineering analysis the design relies on. Any substituted layer needs new evidence before approval.  
  Trace: drawings.wall_sections, spec.part2 · Owner: gc · Gate: procurement_release · _07 20 00_
- **[critical (reflex)] rf.overflow** — Every roof area that can pond behind parapets or walls has secondary drainage: overflow drains or scuppers.  
  Trace: drawings.roof_plan, drawings.plumbing · Owner: design_team · _07 50 00_
- **[high (reflex)] d07.control-layer-continuity** — On each wall section and every transition detail (foundation, slab edge, openings, roof edge and parapet, penetrations, changes of material), trace the water, air, thermal and vapor layers across the transition. Any layer that stops without a detail showing how it joins the next is a finding, even when the submittal itself is correct.  
  Trace: drawings.wall_sections, drawings.details, drawings.roof_plan · Owner: design_team · Gate: procurement_release · _07_

## Division 08
- **[critical (reflex)] 08hw.rated-function** — Every rated opening's set has a closer (or listed automatic closing), positive latching on every leaf (automatic or self-latching bolts on the inactive leaf of rated pairs, never manual bolts unless the listing and code allow them) and a coordinator where the astragal needs one, fire exit hardware rather than panic hardware where an exit device is used, no mechanical dogging or kick-down holders, the gasketing the label requires, and labeled protective plates where plates run higher than the fire door standard allows unlabeled. Hold-opens on rated doors release by the fire alarm or detection.  
  Trace: schedule.door_hardware, schedule.door, drawings.life_safety · Owner: subcontractor · _08 71 00_
- **[critical (reflex)] d08.rc.rated-openings** — Every opening in a rated or smoke-resistant wall on the life safety plans has an opening protective in the door schedule with the rating that wall needs, and every rated door sits in a wall the life safety plans rate. Ratings copied from an earlier life safety plan, and walls upgraded after the schedule was written, show up here.  
  Between: drawings.life_safety ↔ schedule.door ↔ schedule.partition_type · Key: Opening in a rated wall, shaft, corridor or smoke barrier · Fields: wall rating, required opening rating, door and frame label, smoke and draft control, glazing rating · Owner: design_team · Gate: procurement_release · _08_

## Division 09
- **[critical (reflex)] 09gb.listed-design-match** — Each fire-rated or sound-rated partition type is built exactly as its listed design or tested assembly: stud depth, thickness and spacing; board type, layers and orientation; fastener type and spacing; joint treatment; insulation; resilient channel or clips. A substituted component (another manufacturer's proprietary board, a lighter or "equivalent" stud, different insulation) is acceptable only where that design, or the component's own listing, covers it. Ratings against the life safety plans are reconciled under firestopping (07 84 00); this check is the build-up of each type.  
  Trace: schedule.partition_type, drawings.details, spec.part2 · Owner: subcontractor · _09 21 16_
- **[critical (reflex)] 09ti.wet-area-waterproofing** — Showers, tub surrounds and wet rooms, and tiled floors that are hosed down or drained above occupied or finished space (commercial kitchens, locker and toilet rooms with floor drains, pool decks on elevated slabs), have a waterproof membrane under the tile, turned up walls and curbs, carried into the drain's clamping ring or bonding flange, and flood tested before tile. Where none is shown at those locations the design team confirms the intent, and the section that furnishes and installs it (this one or Division 07) is named.  
  Trace: drawings.enlarged_plans, drawings.details, schedule.finish, spec.part2 · Owner: design_team · Gate: floor_finish_install · _09 30 00_

## Division 13
- **[critical (reflex)] 13cs.floor-frost** — Freezer floors on grade have insulation in a slab recess with heat trace or a ventilated subfloor against frost heave, with the heat trace powered and monitored; the recess depth matches the floor build-up so the room floor is flush with the corridor. Cooler floors follow the design's insulated or uninsulated choice.  
  Trace: drawings.structural, drawings.details, drawings.electrical · Owner: design_team · Gate: slab_pour · _13 21 26_
- **[critical (reflex)] 13mb.reactions-foundation** — The manufacturer's final reactions (by column and load case, with horizontal thrust at frames and brace reactions) are checked by the foundation EOR before footings, tie rods or hairpins and anchor bolts are released. Foundations designed on preliminary or another manufacturer's reactions are rechecked when the final design arrives.  
  Trace: drawings.foundation, drawings.structural · Owner: design_team · Gate: foundation_pour · _13 34 19_

## Division 14
- **[critical (reflex)] 14el.rc.hoistway** — Hoistway size, pit depth and overhead agree among the architectural plans and sections, the structural drawings and the spec's capacity, speed and door type. The structural pit and top-of-hoistway framing are what will be built, so check them first.  
  Between: drawings.enlarged_plans ↔ drawings.building_sections ↔ drawings.structural ↔ spec.part2 · Key: Elevator car designation · Fields: clear hoistway width and depth, pit depth, overhead, machine room or control space, capacity and car size, door type and width, front or rear openings, stops · Owner: design_team · Gate: foundation_pour · _14 20 00_

## Division 21
- **[critical (reflex)] 21sp.hazard-commodity** — Each area's hazard or storage protection matches its real use: storage height, commodity class (including plastics and packaging), rack or solid-piled arrangement and aisle widths come from the owner's or tenant's stated use, not from the room name. Storage beyond what the design criteria cover needs storage-specific criteria (possibly in-rack sprinklers) and is a design-team question if the drawings are silent.  
  Trace: drawings.fire_protection, drawings.plans, spec.part2 · Owner: design_team · Gate: procurement_release · _21 13 00_

## Division 22
- **[high (reflex)] d22.plenum-materials** — Plastic pipe, insulation, jackets and pipe wraps exposed in return-air plenums meet the plenum flame-spread and smoke-developed limits or are listed for plenum use, or are enclosed or routed out of the plenum. A metal-to-plastic substitution is checked for this before approval.  
  Trace: drawings.mechanical, drawings.plumbing, spec.part2 · Owner: subcontractor · _22_

## Division 23
- **[critical (reflex)] 23da.rc.dampers-vs-life-safety** — Every duct or air transfer opening that crosses a fire-rated wall, floor, shaft, corridor or smoke barrier on the life safety plans has the damper the code requires, and every damper on the mechanical drawings sits in an assembly that needs it. Recheck after life safety plan revisions, which often move rated walls after the ductwork is drawn.  
  Between: drawings.life_safety ↔ drawings.mechanical ↔ schedule.partition_type · Key: Each duct or transfer opening through a rated wall, floor, shaft, corridor or smoke barrier · Fields: assembly fire rating, smoke rating, damper type required, damper shown, access door · Owner: design_team · Gate: overhead_rough_in · _23 33 00_
- **[high (reflex)] d23.rc.mech-elec** — Each tag's electrical data in the approved submittal matches its circuit on the panel schedule and the single-line. Recheck after every substitution, alternate and option change (electric heat, drive, factory disconnect, service receptacle, second power connection): the submitted unit's MCA and MOCP govern the conductors and the overcurrent device, not the design-stage schedule.  
  Between: schedule.mechanical_equipment ↔ schedule.electrical_panel ↔ drawings.single_line · Key: Equipment tag · Fields: voltage, phase, MCA, MOCP or breaker size, number of power connections, disconnect and who furnishes it, starter or drive and who furnishes it, emergency or standby source · Owner: design_team · Gate: procurement_release · _23_

## Division 26
- **[critical (reflex)] 26ds.sccr-vs-fault** — Each assembly's short-circuit current rating and each device's interrupting rating meets the available fault current at its line terminals from the study or the utility's data; series ratings are used only as listed combinations and only where the code permits them. The comparison is redone whenever the utility transformer, the service size or a building transformer's impedance changes.  
  Trace: drawings.single_line, report.utility_requirements · Owner: subcontractor · Gate: procurement_release · _26 20 00_

## Division 27
- **[critical (reflex)] 27rc.need-determined** — Whether emergency responder radio coverage is required is settled early: the AHJ's requirement, a predictive study or a survey of the enclosed building, and a budget and design path if amplification is needed. Silence in the documents is not a no.  
  Trace: spec.part1, drawings.technology, drawings.life_safety · Owner: design_team · Gate: procurement_release · _27 53 19_
- **[high (reflex)] d27.skeleton** — The base building documents show every telecom room with its size, door, backboard, power, dedicated cooling, bonding busbar and lighting, the backbone pathways between rooms and floors, and the entrance conduits from the property line, even when the cabling itself is design-build or owner-furnished.  
  Trace: drawings.technology, drawings.enlarged_plans, drawings.mechanical, drawings.electrical · Owner: design_team · Gate: overhead_rough_in · _27_

## Division 28
- **[critical (reflex)] 28ac.egress-release** — For each locked egress door, the locking method and its release (free egress through the door hardware, release on fire alarm and power loss, delayed or controlled egress, sensor release) is one the egress code permits for that door and occupancy, and stair doors meet the re-entry rules.  
  Trace: schedule.door_hardware, drawings.life_safety · Owner: design_team · _28 10 00_

## Division 31
- **[high (reflex)] d31.adjacent-monitoring** — Where excavation, dewatering, pile or sheet driving, or vibratory compaction happens near existing buildings, streets, utilities or vibration-sensitive occupancies, a pre-construction condition survey with photographs is taken and vibration and settlement limits with response actions are set before the work starts.  
  Trace: spec.part3, report.geotechnical, report.existing_conditions · Owner: gc · Gate: excavation · _31_

## Division 32
- **[high (reflex)] pv.accessible-route** — An accessible route is shown from accessible parking, passenger loading zones, public sidewalks and transit stops to each accessible entrance, without steps, with curb ramps where it crosses curbs, and with spot elevations at ramps, landings and doors that prove the slopes.  
  Trace: drawings.site, drawings.civil, drawings.plans · Owner: design_team · _32 10 00_

## Division 33
- **[high (reflex)] d33.rc.building-line** — Every service the civil drawings bring to the building matches the building drawings in location, size, material and invert or depth, and both sets put the end of the site scope at the same point; the two sides are usually drawn by different engineers.  
  Between: drawings.civil ↔ drawings.plumbing ↔ drawings.fire_protection ↔ drawings.electrical ↔ drawings.technology · Key: Each service at the building line (domestic water, fire service, sanitary, storm, gas, electric, communications) · Fields: entry location on the building, size, material, invert or depth, point where site scope ends and building scope begins · Owner: design_team · Gate: foundation_pour · _33_

## Interfaces
- **[critical] if.firestop-rated-walls** — Firestopping (07 84 00) ↔ Gypsum board assemblies and framing (09 21 16, 09 22 16, 09 29 00) · Gate: overhead_rough_in
  - From Firestopping: Listed systems that assume clean openings in finished boards; installation and inspection area by area
  - From Gypsum board assemblies and framing: Rated walls boarded full height to structure before penetrating trades pass through them
- **[critical] if.08-electrified-openings** — Electrified door hardware and automatic entrances (08 71 00, 08 42 29) ↔ Electrical raceway and wiring, access control and intrusion detection (26 05 19, 26 05 33, 28 10 00, 28 30 00) · Gate: wall_close_in — Openings and their devices are frozen at hardware approval; cable to the frame goes in before board
  - From Electrified door hardware and automatic entrances: Each electrified opening's devices, voltage, load, fail-safe or fail-secure, power supply location and the frame and header boxes its wiring needs, issued before in-wall rough-in
  - From Electrical raceway and wiring, access control and intrusion detection: Circuits to power supplies and operators; conduit and boxes from each frame and header to an accessible ceiling, in place before the wall is closed; readers, request-to-exit and position switches where security furnishes them; the cable, terminations and programming
  - Confirm who: Lock power supplies — typical furnish 08 71 00 or 28 10 00 / install 08 71 00 or 28 10 00 / connect 26 05 00
  - Confirm who: Conduit and back boxes from frame to ceiling — typical furnish 26 05 00 or 28 10 00 / install 26 05 00 or 28 10 00
  - Confirm who: Door position switches and request-to-exit devices — typical furnish 08 71 00 or 28 10 00 / install 08 71 00 or 28 10 00
  - Confirm who: Cable from electrified hardware to the access control panel, termination and testing of each opening — typical install 28 10 00 or 26 05 00 / connect 28 10 00
