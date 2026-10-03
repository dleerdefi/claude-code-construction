# Compiled knowledge — 03 30 00 Cast-in-Place Concrete

Facility types: education.k12 · Confidence floor: **draft** · Review mode: package · Contractor-designed: never
Lineage: global → 03 → 03 30 00
Overlays: education, education.k12

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Concrete materials, mixes, placement, curing and testing for foundations, structure and slabs (03 31 00 through 03 39 00 inherit from here). The mix submittal is the cheapest place to fix problems: one mix per placement, matched to exposure, finish and whatever goes on top. Slabs carry most of the cross-trade risk, because floor finishes, equipment and underslab MEP depend on the slab's depressions, joints, curing and moisture, and every anchor bolt, embed and sleeve has to be in the forms, from approved shop drawings, before the truck arrives.

## Review checks (23)
### completeness
- **[critical] edu.storm-shelter** — Where the school has a storm shelter or safe room, every element of the shelter envelope (walls, roof deck and covering, doors with their frames and hardware, windows, louvers and penetrations) is submitted with evidence that it meets ICC 500 pressure and debris-impact testing as the tested assembly, and the shelter's ventilation, emergency lighting, toilets and power are shown. One standard door, louver or hardware substitution in the shelter boundary breaks the shelter.  
  Trace: drawings.life_safety, drawings.plans, spec.part2 · Owner: subcontractor · Scope: package · Gate: procurement_release · _overlay:education.k12_
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] d03.inspection-and-testing** — The testing agency, sampling frequency, field tests and specimen sets per placement are defined, including field-cured or extra specimens (or a calibrated maturity method) for every strength-based decision: form and shore removal, stressing, panel lifting, precast erection, early loading. The special inspections the statement of special inspections lists for this scope are booked before each placement, and results reach the contractor fast enough to change the next placement.  
  Trace: spec.part3, register.special_inspections · Owner: gc · Scope: package · Gate: foundation_pour · _03_
- **[medium] g.products-marked** — Cut sheets covering a product family have the proposed model, size, options, finish and accessories clearly marked; unmarked sheets are returned.  
  Trace: spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data · _global_
### conformance
- **[high] g.current-documents** — The submittal reflects the current contract documents, including addenda, ASIs, bulletins and responded RFIs, not the bid set. Note the drawing revision the submitter worked from.  
  Trace: drawings.revision_blocks, register.asi_bulletin_log, register.rfi_log · Owner: gc · Scope: package · _global_
- **[high] g.basis-of-design** — Proposed manufacturer and model match the basis of design or a listed acceptable manufacturer. Anything else follows the comparable-product or substitution procedure Division 01 allows, with its timing and comparison data, before it is reviewed on its merits.  
  Trace: spec.part2_manufacturers, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] g.deviations-identified** — Every deviation from the contract documents is clouded or listed by the submitter. Compare independently; do not rely on the submitter's list.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _global_
- **[high] 03cip.mix-per-placement** — Every placement type on the drawings maps to a submitted mix, and each mix meets the exposure class the structural drawings assign (maximum water-cementitious ratio, minimum strength, air, cementitious limits) at the strength age the spec allows. Where the drawings assign no exposure class but the geotechnical report finds sulfates or the element sees deicers or freezing, that is an RFI. Mixes submitted with no intended placement are returned.  
  Trace: drawings.structural, schedule.structural, spec.part2, report.geotechnical · Owner: subcontractor · Scope: package · Types: Design Data · Gate: foundation_pour · _03 30 00_
- **[high] 03cip.air-in-troweled-slab** — Interior slabs that get a hard steel-trowel finish, a dry-shake hardener or a polished finish use a mix without intentional air entrainment, even when the supplier offers one exterior mix for the whole job. Slabs that need air for freeze-thaw exposure get a finish compatible with it.  
  Trace: spec.part2, spec.part3, schedule.finish · Owner: subcontractor · Scope: package · Types: Design Data · Gate: slab_pour · _03 30 00_
- **[high] 03cip.vapor-retarder** — Slabs on ground under moisture-sensitive flooring, coatings or conditioned space have a vapor retarder of the class and thickness the spec names, placed where the design says relative to the slab (directly beneath it or under a fill layer), with laps sealed and every penetration booted. Drawings silent on the location are an RFI; fill left above the retarder needs a plan to keep it dry.  
  Trace: drawings.structural, drawings.details, spec.part2, report.geotechnical · Owner: design_team · Scope: package · Gate: slab_pour · _03 30 00_
- **[high] edu.risk-category-delegated** — Delegated designs (cladding and curtain wall, roofing attachment, joists and trusses, nonstructural and equipment anchorage) state the risk category and importance factors they used, and these match the structural general notes; schools are often assigned above the default, and designers who assume the default under-design.  
  Trace: drawings.structural, spec.part1_submittals · Owner: subcontractor · Scope: package · _overlay:education_
### coordination
- **[critical (reflex)] 03cip.cast-in-before-pour** — Before each placement, every item cast into or passing through the concrete (anchor rods, embed plates, sleeves, conduit, floor boxes, inserts, dowels, waterstops, grounding electrodes, blockouts) is located from the approved shop drawings of the trade that needs it, not the bid drawings, and surveyed by every discipline. An item with no approved shop drawing by the pour date is a hold point, not a field decision.  
  Trace: drawings.structural, drawings.foundation, drawings.plumbing, drawings.electrical, drawings.mechanical, submittals.approved · Owner: gc · Scope: package · Gate: foundation_pour · _03 30 00_
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
- **[high] d03.surface-compatibility** — Every product left on a concrete surface (form release agent, curing compound, bond breaker, hardener, densifier, sealer) is accepted in writing by the manufacturer of whatever is applied to or bonded against that surface later: waterproofing, flooring adhesive, coating, topping, sealant, applied finish. Where it is not, removal and who performs it are in a scope before the product is used.  
  Trace: spec.part2, schedule.finish · Owner: gc · Scope: package · _03_
- **[medium] 03cip.slab-joints** — The slab joint layout (contraction, construction, isolation at columns and walls) is submitted before the pour and coordinated with the flooring: tile and stone get a movement joint above every slab joint, joints under resilient and thin finishes are filled after shrinkage, and sawcutting happens within the timing window the spec sets for the saw type used.  
  Trace: drawings.structural, drawings.plans, schedule.finish, spec.part3 · Owner: gc · Scope: package · Gate: slab_pour · _03 30 00_
### constructability
- **[critical (reflex)] d03.coring-scanning** — No coring, sawcutting or drilling of placed structural concrete (slabs, beams, walls, post-tensioned slabs, precast and prestressed members) without the location and size accepted by the engineer of record and the area scanned for reinforcing, tendons, strands and embedded conduit first. Penetrations added after the pour are routed this way even when small, and the procedure is written into the MEP and tenant scopes.  
  Trace: spec.part3, spec.division_01, drawings.structural · Owner: gc · Scope: package · _03_
- **[high] 03cip.drying-before-flooring** — Where moisture-sensitive flooring or coatings go on the slab, the mix (water-cementitious ratio, lightweight or normal-weight aggregate), the deck below and the schedule (enclosure, conditioning, flooring date) let the slab reach the flooring manufacturer's moisture limit in time. Lightweight concrete and slabs on metal deck dry only from the top and are the usual miss; a mitigation allowance decided late costs the most.  
  Trace: spec.part2, schedule.finish, schedule.master, drawings.structural · Owner: gc · Scope: package · Gate: procurement_release · _03 30 00_
- **[high] 03cip.curing-by-area** — The curing method is chosen per slab area for the finish that follows: wet or sheet curing, or a compound the later manufacturer accepts, wherever adhered flooring, coatings, toppings, sealers or a polished finish follow. A single compound named for the whole slab, with no removal assigned, is returned.  
  Trace: spec.part3, schedule.finish · Owner: subcontractor · Scope: package · Gate: slab_pour · _03 30 00_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[medium] d03.weather-limits** — Hot and cold weather procedures (temperature limits for the concrete, grout or underlayment and the substrate, protection, heating or cooling, curing, and the temperature and strength record that allows forms or protection to come off) are submitted before the season they apply to, and the placement schedule shows which pours fall in it.  
  Trace: spec.part3, schedule.master · Owner: gc · Scope: package · _03_
- **[medium] 03cip.site-water** — The mix design states how much water may be added at the site, if any, and delivery tickets record batch time and any water or admixture added. Water beyond the allowance, or concrete past the discharge limit, is rejected at the chute; the decision is not left to the finisher.  
  Trace: spec.part2, spec.part3 · Owner: gc · Scope: package · _03 30 00_
### absence
- **[medium] 03cip.mass-placements** — Thick placements (mats, large pile caps, transfer girders) are identified, and where the spec or the element calls for it a thermal control plan covers temperature limits, monitoring and protection.  
  Trace: drawings.foundation, drawings.structural, spec.part3 · Owner: gc · Scope: package · Gate: foundation_pour · _03 30 00_

## Reconciliations — documents that must agree (4)
- **[critical] 03cip.rc.embeds-anchor-rods** — Anchor rods and embed plates on the foundation and slab plans agree with the column and base plate schedule and with the approved steel, miscellaneous metals and precast shop drawings, and the layout set in the field comes from those approved drawings.  
  Between: drawings.foundation ↔ drawings.structural ↔ drawings.details ↔ submittals.approved · Key: Column, base plate or embed mark · Fields: location, top of concrete and plate elevation, rod diameter, pattern and projection, plate size and orientation · Owner: gc · Gate: foundation_pour · _03 30 00_
- **[high (reflex)] 03cip.rc.depressions** — Every area with a thicker floor assembly (thick-set tile, tile over a waterproofing or crack-isolation membrane, terrazzo, recessed entrance mats, shower floors and sloped beds to floor drains, walk-in coolers) has a structural depression equal to the full assembly depth over its full extent, so the finish meets the adjacent floor flush.  
  Between: schedule.finish ↔ drawings.plans ↔ drawings.enlarged_plans ↔ drawings.structural · Key: Room or floor area whose finish assembly differs in thickness from the base floor · Fields: total assembly thickness (setting bed, membrane, mat, terrazzo, topping), depression depth, extent, slope to drains, transition at doors · Owner: design_team · Gate: slab_pour · _03 30 00_
- **[high] 03cip.rc.sleeves** — Each MEP penetration of cast-in-place concrete is on a coordinated sleeve drawing, sized for the pipe or duct plus insulation and the annular space its firestop system needs, and those through beams, grade beams, footings and post-tensioned slabs are accepted by the engineer of record.  
  Between: drawings.structural ↔ drawings.plumbing ↔ drawings.mechanical ↔ drawings.electrical ↔ drawings.fire_protection · Key: Penetration through a slab, wall, grade beam or footing · Fields: location, size including insulation and firestop annular space, elevation in walls, sleeve type (waterstop collar, cast-in firestop device), structural acceptance through beams and footings · Owner: gc · Gate: slab_pour · _03 30 00_
- **[high] 03cip.rc.housekeeping-pads** — Every housekeeping pad is sized from the approved equipment submittal (footprint, anchor pattern and the edge distance the anchorage design needs, height for condensate traps or drains), not from the scheduled basis of design, and is doweled to the slab as detailed.  
  Between: schedule.mechanical_equipment ↔ schedule.equipment ↔ drawings.mechanical ↔ drawings.electrical ↔ drawings.structural ↔ submittals.approved · Key: Equipment tag · Fields: pad length and width against the approved equipment footprint, pad height for traps, drains or clearances, anchor locations and edge distance, doweling or reinforcing · Owner: gc · Gate: slab_pour · _03 30 00_

## Compliance — regulatory hooks (9)
- **[critical] edu.rh.storm-shelter** (`storm-shelter-requirements`) — Does the adopted building code require a storm shelter for this school (tornado design wind speed, occupant load), what capacity and location does it need, which ICC 500 edition governs, and what special inspection applies to the shelter?  
  **Unbound** → Run /construction:code-researcher with research topic "storm-shelter-requirements" (seed it with this hook's question)
- **[high] d03.rh.special-inspection** (`concrete-special-inspection`) — Which special inspections and tests does the adopted building code require for this concrete work (reinforcing and embed placement, anchors cast in concrete, sampling and placement, curing temperature, post-tensioning, precast erection and connections, welding of reinforcement), which are continuous or periodic, and which are waived?  
  **Unbound** → Run /construction:code-researcher with research topic "concrete-special-inspection" (seed it with this hook's question)
- **[high] 03cip.rh.strength-acceptance** (`concrete-strength-testing-acceptance`) — What sampling frequency and strength acceptance criteria does the concrete standard adopted by the building code require, and what does it require when strength tests fall short (cores, load tests)?  
  **Unbound** → Run /construction:code-researcher with research topic "concrete-strength-testing-acceptance" (seed it with this hook's question)
- **[high] 03cip.rh.exposure-durability** (`concrete-exposure-durability-requirements`) — What exposure categories apply to each element (freezing and thawing, sulfate, water contact, corrosion from chlorides) and what maximum water-cementitious ratio, minimum strength, air content and cementitious limits does the adopted code require for them?  
  **Unbound** → Run /construction:code-researcher with research topic "concrete-exposure-durability-requirements" (seed it with this hook's question)
- **[high] edu.rh.risk-category** (`building-risk-category-assignment`) — What risk category applies to this building under the adopted code (occupant load, designation as an emergency or community shelter), and which design loads, nonstructural anchorage and special inspections change because of it?  
  **Unbound** → Run /construction:code-researcher with research topic "building-risk-category-assignment" (seed it with this hook's question)
- **[medium] d03.rh.embodied-carbon** (`concrete-embodied-carbon-limits`) — Does a state or local law, or an owner program the spec names, cap the global warming potential of concrete or precast products or require product-specific environmental product declarations, and do the submitted mixes and products carry them?  
  **Unbound** → Run /construction:code-researcher with research topic "concrete-embodied-carbon-limits" (seed it with this hook's question)
- **[medium] 03cip.rh.slab-vapor-retarder** (`slab-on-ground-vapor-retarder`) — Does the adopted building code require a vapor retarder under this slab on ground, with what minimum material and lap requirements, and which exceptions apply?  
  **Unbound** → Run /construction:code-researcher with research topic "slab-on-ground-vapor-retarder" (seed it with this hook's question)
- **[medium] 03cip.rh.radon** (`radon-resistant-construction`) — Does the jurisdiction require radon-resistant construction for this building or occupancy (gas-permeable layer, sealed retarder, sub-slab vent piping), and is it in the drawings?  
  **Unbound** → Run /construction:code-researcher with research topic "radon-resistant-construction" (seed it with this hook's question)
- **[medium] 03cip.rh.equipment-anchorage** (`seismic-nonstructural-anchorage`) — Where the adopted code requires seismic anchorage of floor-mounted equipment, what does it require of the anchorage design, its certification and its inspection, and does the pad design give the anchors the embedment and edge distance that design assumes?  
  **Unbound** → Run /construction:code-researcher with research topic "seismic-nonstructural-anchorage" (seed it with this hook's question)

## Coordination routing (29)
- **[critical] if.01-special-inspection-structure** → Quality requirements (testing agency and special inspection) (01 40 00) · Gate: foundation_pour — The first cover point on new construction; fill and deep foundations are inspected as they are placed, before it, and renovation work holds at the slab, wall or ceiling closure that covers it. Masonry grout, steel erection, fireproofing and wall close-in each hold for their own inspections
  - Send them: Notice ahead of each inspected activity, access for the inspector, and work kept uncovered until the inspection is recorded
  - Need from them: Engaged agency, inspection scope and frequency from the statement of special inspections, and the notice procedure
  - If missed: Concrete placed, steel fireproofed or walls boarded before the special inspector was called
- **[critical] if.01-structural-cutting** → Cutting and patching (01 73 00)
  - Send them: Limits on openings and coring (reinforcing, tendons, beam webs and flanges) and the reinforcement new openings need
  - Need from them: Cutting proposal with locations, sizes, scan results and the engineer's acceptance
  - If missed: A core drilled through a post-tensioned slab without scanning or the engineer's acceptance; Trades torch-cut holes through beam webs for ducts and pipes that were never on the shop drawings
- **[critical] if.02-structural-removal** → Demolition (02 41 00) · Gate: demolition_start
  - Send them: New beams, columns, lintels or reinforcement in place before the element they replace is removed, and the engineer of record's acceptance of the sequence
  - Need from them: Removal sequence and engineered temporary shoring for each load-bearing element
  - If missed: A bearing wall or beam removed before shoring or the new support is in place
- **[critical] if.03-steel-anchorage** → Structural steel, metal fabrications and post-installed anchors (05 12 00, 05 50 00, 05 05 19) · Gate: foundation_pour — The steel anchor rod layout is approved before footing and pier forms close; the as-built survey is accepted before steel_erection
  - Send them: Anchor rods and embed plates set from the approved steel and metals layouts and surveyed before the pour; grout under base and bearing plates once the frame is plumbed and released
  - Need from them: Approved anchor rod and embed layouts (location, elevation, projection, rod size and pattern, plate size) and the fabricated items, delivered before forms close; any post-installed fix proposed with an evaluation report for the engineer's acceptance
  - Confirm who: Anchor rods and embed plates — typical furnish 05 12 00 or 05 50 00 / install 03 30 00
  - Confirm who: Grout under column base plates and bearing plates — typical furnish 03 60 00 or 05 12 00 / install 03 60 00 or 05 12 00
  - If missed: Base plates left ungrouted on leveling nuts while the frame is loaded; Anchor rods cast out of position, rotated or at the wrong projection, found as the column is set; Embed plates for railings, canopies, curtain wall or equipment left off the layout the concrete trade set from
- **[high] if.03-pile-caps** → Driven, bored and special foundation piles (31 62 00, 31 63 00, 31 66 00) · Gate: foundation_pour
  - Send them: Cap and grade beam dimensions and reinforcing, adjusted by the engineer to as-built pile positions before forming
  - Need from them: As-built pile location and cut-off elevation survey, and pile acceptance (load tests, integrity tests, driving or drilling records) before caps are formed
  - If missed: A pile cap formed and reinforced before the logs and as-built survey are reviewed
- **[high] if.03-masonry-dowels** → Unit masonry and masonry reinforcing (04 20 00, 04 05 19) · Gate: foundation_pour
  - Send them: Dowels at the size, spacing and projection the masonry reinforcing requires, aligned with the cells to be grouted, and top-of-footing elevations that work with the masonry coursing
  - Need from them: Wall layout, openings, control joints, coursing start elevation and reinforced-cell locations before the footing pour
  - If missed: Dowels for masonry, pads or later pours left off the placing drawings; Foundation dowels set on the wall centerline but off the cell layout
- **[high] if.03-masonry-veneer** → Masonry anchorage and veneer (04 05 19, 04 20 00) · Gate: foundation_pour — The ledge is formed with the foundation, often before the wall insulation thickness is final
  - Send them: Brick ledge at the elevation, width and slope the veneer, air space, continuous insulation and flashing need; dovetail slots or anchor channels cast wherever veneer laps concrete walls, columns and slab edges
  - Need from them: Coursing and the ledge elevation that suits it relative to finished grade, ledge width for the insulation thickness actually specified, anchor type and spacing at concrete backup, and the flashing and weeps at the ledge
  - If missed: Ledge formed to the bid-set width after the insulation grew, or too high for the coursing and flashing above grade; veneer overhangs or is notched, and anchors are drilled into concrete that had no slots
- **[high] if.03-wood-frame-anchorage** → Wood framing and its tie-down hardware (06 11 00, 06 05 23) · Gate: slab_pour — Where the wood frame starts on footings or a slab on ground, the same hand-off is due at foundation_pour
  - Send them: Anchor bolts, hold-down anchors and tie-down rod anchors cast at the approved shear wall and tie-down locations with the embedment and edge distance the design assumes, and a podium top flat enough for the wall plates
  - Need from them: Approved shear wall, hold-down and tie-down drawings with anchor types, locations and embedment before the pour, and the sill plate and sill sealer details at the podium
  - Confirm who: Hold-down and tie-down rod anchors cast into the foundation or podium — typical furnish 06 05 23 or 06 11 00 / install 03 30 00
  - If missed: Hold-down anchors missed or misplaced in the podium or foundation pour
- **[high] if.03-metal-building-anchorage** → Metal building systems (13 34 19) · Gate: foundation_pour — The manufacturer's drawings usually follow the foundation design; hold the pour for the final plan
  - Send them: Footings, piers and anchor rods built from the manufacturer's final anchor bolt plan as checked by the foundation engineer; tie rods or hairpins for frame thrust placed with the slab and not severed by slab joints; the slab-edge notch the wall panels and base trim need
  - Need from them: Sealed final anchor bolt plan with rod sizes, projections and column reactions by load case (including frame thrust and brace reactions), and the base trim detail, before the foundation pour
  - If missed: Footings and anchor bolts built from preliminary reactions or another manufacturer's bolt plan
- **[high] if.03-cladding-embeds** → Curtain wall (08 44 00) · Gate: slab_pour — Curtain wall anchor design usually runs behind the structure; settle the embed approach before the first elevated slab
  - Send them: Slab-edge embeds or cast-in anchor channels at the curtain wall anchor locations, slab edge within the tolerance the anchors can absorb, clear of tendon anchorages
  - Need from them: Anchor layout, embed type and loads from the curtain wall engineer, before slab-edge forms are set
  - If missed: Curtain wall embeds or edge angles land on stressing anchorages at the slab edge; Embed design lags the slab pours, or embeds are cast outside the anchor tolerance
- **[high] if.03-flooring-substrate** → Flooring preparation, tile, flooring and entrance mats (09 05 61, 09 30 00, 09 60 00, 12 48 13) · Gate: slab_pour — Depressions, curing and tolerances are fixed at the pour; moisture and flatness acceptance comes again at floor_finish_install
  - Send them: Slab elevations and depressions at full assembly depth, flatness per flooring type measured on time, curing method and surface treatments by area, joint layout, and the mix and drying conditions behind the moisture schedule
  - Need from them: Floor assembly and thickness per room, each manufacturer's flatness and moisture limits and test methods, movement-joint requirements over slab joints, and written acceptance of the substrate before installation
  - Confirm who: Floor preparation beyond normal flooring prep (grinding, patching, leveling) — typical furnish 03 35 00 or 09 05 61 / install 03 35 00 or the flooring trade
  - Confirm who: Moisture mitigation where the slab exceeds the flooring limit — typical furnish 09 05 61 / install 09 05 61 or the flooring trade
  - If missed: Depression sized for tile thickness only, without membrane and mortar bed; Slab fails its moisture test weeks before turnover with no mitigation decided or priced; Curing compound or sealer left on the slab under adhered flooring
- **[high] if.03-cold-storage-floors** → Walk-in coolers and freezers, cold storage rooms (11 41 00, 13 21 26) · Gate: slab_pour
  - Send them: The floor the approved box needs, settled before forming (a depression for insulated floor panels, or an insulated slab with the vapor retarder on the warm side and underfloor heat below it), finished flush at the door
  - Need from them: Floor type and assembly depth from the approved box, the underfloor heat layout (cable in conduit or glycol piping) with power, control and monitoring, and floor drain locations
  - Confirm who: Underfloor heat under freezers on grade — typical furnish 11 41 00 or 13 21 26 / install the electrical or refrigeration trade
  - Confirm who: Insulation and vapor retarder within an insulated slab — typical furnish 11 41 00, 13 21 26 or 03 30 00 / install 03 30 00
  - If missed: Freezer built on grade without underfloor heat, or with heating cable never energized or monitored; Slab poured flat where the walk-in needed a depression, or depressed for a different floor assembly
- **[high] if.03-dock-leveler-pits** → Loading dock equipment (11 13 00) · Gate: slab_pour — Dock pits are often poured with the dock walls; hold them for the approved leveler
  - Send them: Pits formed to the approved leveler's pit drawing, curb angles and embed plates anchored as detailed, pit slope or drain, and dock-face embeds for bumpers and restraints
  - Need from them: Approved pit drawing per position (size, depth, curb angles, embeds, anchors, drainage), any pit form or curb-angle kit the manufacturer furnishes, and bumper and restraint embed locations, before the dock pour
  - Confirm who: Curb angles and pit embeds — typical furnish 11 13 00 / install 03 30 00
  - If missed: Pits formed to a generic detail or another manufacturer's dimensions before the leveler was approved
- **[high] if.03-subgrade** → Excavation and fill; termite control (31 23 00, 31 31 16) · Gate: slab_pour — Footing bearing is accepted at foundation_pour
  - Send them: Footing and slab bottom elevations, base course and retarder requirements, and a pour release that waits for subgrade acceptance
  - Need from them: Subgrade prepared and compacted to the geotechnical recommendations, base course to grade and tolerance, protected from rain and frost until the pour; soil treatment applied before the vapor retarder where required
  - Confirm who: Granular base under slabs on ground — typical furnish 31 23 00 or 03 30 00 / install 31 23 00 or 03 30 00
  - If missed: Subgrade accepted, then left exposed to rain, frost or construction traffic before the slab or base
- **[high] if.03-sleeves** → Penetrating trades (fire protection, plumbing, HVAC, electrical, communications) (21 10 00, 22 10 00, 23 20 00, 23 30 00, 26 05 33, 27 05 28, 21 05 17, 22 05 17, 23 05 17, 26 05 44, 27 05 44) · Gate: slab_pour
  - Send them: Sleeve and blockout locations surveyed before the pour, and the engineer's acceptance of penetrations through beams, footings, grade beams and post-tensioned slabs
  - Need from them: One coordinated sleeve layout across trades, sized for insulation and the firestop system's annular space, with sleeve types (waterstop collars below grade and in wet areas, cast-in firestop devices in rated floors), delivered before forms close
  - Confirm who: Sleeves and cast-in firestop devices — typical furnish each penetrating trade / install each penetrating trade or 03 30 00
  - If missed: A sleeve or floor drain arrives after the tendon layout is approved and is placed by pushing tendons aside; Plumbing sleeves missed at the slab pour, then cored through a post-tensioned slab
- **[high] if.03-hanger-inserts** → Hangers and supports for fire protection, plumbing, HVAC and electrical (21 05 29, 22 05 29, 23 05 29, 26 05 29) · Gate: slab_pour
  - Send them: The engineer's rules for hanging from the slab (cast-in inserts or post-installed anchors, zones clear of tendons and beams, loads that need review), and a pour hold until inserts are set and checked
  - Need from them: Cast-in insert layouts by trade, with loads, from coordinated routing, set on the deck or forms before the pour
  - If missed: Anchor holes drilled into a post-tensioned slab without locating the tendons
- **[high] if.03-underslab-plumbing** → Sanitary, storm and water piping below the slab (22 13 00, 22 14 00, 22 11 00) · Gate: underslab_rough_in
  - Send them: Slab elevations, depressions and slopes at drains, and sleeve details through grade beams and footings
  - Need from them: Underslab piping and drain bodies installed, tested and inspected at locations taken from current architectural layouts and approved fixtures and equipment, with drain bodies set to the finished floor and depression
  - If missed: Floor drain bodies set to the structural slab, or in an area with no slope to the drain
- **[high] if.03-housekeeping-pads** → Floor-mounted fire pump, plumbing, HVAC, electrical and owner equipment (21 30 00, 22 30 00, 23 20 00, 23 50 00, 23 60 00, 23 70 00, 26 10 00, 26 22 00, 26 24 00, 26 30 00, 11 40 00, 11 53 00, 11 70 00) · Gate: slab_pour — Dowels go in with the slab; the pad waits for the approved equipment submittal
  - Send them: Pads formed and doweled to the slab to the approved equipment dimensions, with the anchor embedment and edge distance the anchorage needs
  - Need from them: Approved footprint, weight, anchor pattern and anchorage design, pad height for traps and drains, and pad locations checked against service clearances, before the pad pour
  - Confirm who: Pad dimensions and locations — typical furnish the equipment's trade / install 03 30 00
  - Confirm who: Equipment anchors into pads — typical furnish the equipment's trade / install the equipment's trade or 03 30 00
  - If missed: Conduit stub-ups cast from the design drawings, then another manufacturer's switchboard is approved
- **[high] if.03-elevator-pit** → Elevators (14 20 00) · Gate: foundation_pour — The pit is usually formed before the elevator submittal is approved; get the layout first or hold the pit
  - Send them: Pit floor and walls built to the approved elevator's pit depth, size and reactions, with sump, rail bracket inserts or embeds, sill and entrance embeds, and the jack-hole casing a hydraulic system needs
  - Need from them: Approved layout with pit depth, buffer and rail reactions, bracket spacing and anchorage method, sump size, jack hole location and casing, before the pit is formed
  - Confirm who: Sump pit and pit drainage — typical furnish 03 30 00 (sump) and 22 30 00 or 14 20 00 (pump or drain) / install 03 30 00 and 22 30 00
  - Confirm who: Rail bracket inserts or embeds — typical furnish 14 20 00 / install 03 30 00 or 14 20 00
  - If missed: Pit cast to the bid-set elevator; too shallow or without inserts, so the pit is chipped and re-poured or the elevator is re-engineered
- **[high] if.03-pool-shell** → Swimming pools (13 11 00) · Gate: foundation_pour
  - Send them: Shell, gutter and deck concrete with waterstops at joints and every fitting, sleeve and niche cast at the approved locations, with the surface and tolerance the plaster or tile finish needs
  - Need from them: Approved shell, fitting and gutter layout (main drains, inlets, skimmers, light niches, ladder and rail anchors), the uplift and hydrostatic relief assumptions, and the bonding grid installed and inspected, before the shell pour
  - Confirm who: Pool shell and deck concrete — typical install 03 30 00 or 13 11 00
  - Confirm who: Fittings, niches and sleeves cast into the shell — typical furnish 13 11 00 / install 13 11 00 or 03 30 00
  - If missed: Shell placed before the pool layout was approved or the fittings were set; fittings cored in later, with leaks at every retrofitted penetration
- **[high] if.waterproofing-concrete** → Waterproofing (07 10 00) · Gate: foundation_pour
  - Send them: Curing and release products used, construction joint locations, waterstop installation
  - Need from them: Substrate requirements (curing method, release agents, form-tie treatment, surface profile) and waterstop compatibility
  - Confirm who: Waterstops at below-grade joints — typical furnish 03 15 00 / install 03 30 00
  - If missed: Concrete cured or released with products that block membrane adhesion
- **[medium] if.03-composite-deck** → Steel deck and structural steel framing (05 31 00, 05 12 00) · Gate: slab_pour
  - Send them: Placement method (constant thickness or finished to elevation), the added concrete expected from deck and beam deflection, and finish tolerances an unshored deck can meet
  - Need from them: Deck profile and gauge, pour stops and closures at edges and openings, shear studs installed and inspected, beam camber and the deflection assumed in design
  - Confirm who: Pour stops and edge forms at slab edges and deck openings — typical furnish 05 31 00 or 05 12 00 / install 05 31 00
  - If missed: Slab finished level on a deflecting deck adds unplanned concrete and dead load, or finished to constant thickness leaves a floor out of level for the flooring
- **[medium] if.03-stair-pan-fill** → Metal stairs (05 51 00)
  - Send them: Concrete fill in pans and landings with the reinforcing, finish and nosing embedment the details show, placed in time for the stair to serve as construction access
  - Need from them: Pans and landing forms ready for fill, nosings and anchors in place, and the stair erected and accepted before the fill
  - Confirm who: Concrete fill in metal pan stairs and landings — typical furnish 03 30 00 or 05 51 00 / install 03 30 00 or 05 51 00
  - If missed: Concrete fill in stair pans and landings carried by neither the stair nor the concrete subcontract
- **[medium] if.03-floor-recesses** → Entrances, door hardware, mobile storage and sterilizers (08 41 00, 08 42 00, 08 71 00, 10 56 00, 11 71 00) · Gate: slab_pour
  - Send them: Blockouts and recesses formed at the pour to the approved product (floor closer and pivot boxes, sliding-door floor tracks and recessed thresholds, mobile shelving rails, cart-loading sterilizer pits), with the flatness the product needs around them
  - Need from them: Approved recess sizes, locations and tolerances, and any drain, conduit or anchorage in the recess, before the pour; products that will be selected late are flagged so the recess is held open or deliberately omitted
  - If missed: Slab poured flat with no rail recess for a mobile system selected later
- **[medium] if.03-underslab-vapor-retarder** → Vapor retarders (07 26 00) · Gate: slab_pour
  - Send them: Reinforcing supports with bases, placement without damage, and repair of damage done by the concrete and reinforcing crews before the pour
  - Need from them: Retarder class, laps and sealing, boots at every penetration, and an inspection release before reinforcing goes down
  - Confirm who: Vapor retarder under slabs on ground — typical furnish 03 30 00 or 07 26 00 / install 03 30 00 or 07 26 00
  - Confirm who: Sealing and boots at underslab penetrations — typical install 07 26 00, 03 30 00 or the penetrating trade
  - If missed: Retarder installed by one trade and penetrated by several; holes and tears are never sealed because no one owns the repair
- **[medium] if.03-slab-insulation** → Thermal insulation (07 21 00) · Gate: slab_pour
  - Send them: Slab-edge and foundation details that leave room for the insulation and a thermal break at slab edges and entrances, and a pour release after the insulation is inspected
  - Need from them: Under-slab and slab-edge insulation of the type, extent and orientation the energy compliance path assumes, rated for the soil and slab load, set before the pour
  - Confirm who: Under-slab and slab-edge insulation — typical furnish 07 21 00 or 03 30 00 / install 07 21 00 or 03 30 00
  - If missed: Slab-edge or under-slab insulation left out, crushed or cut short at doors before the pour; a failed energy inspection and a cold, condensing slab edge
- **[medium] if.03-underslab-electrical** → Electrical and communications raceways, pathways and underground ducts (26 05 33, 26 05 43, 27 05 28, 27 05 43) · Gate: slab_pour
  - Send them: The engineer's limits on conduit size, spacing and placement in the slab (and exclusion from tendon zones and beams), and a pour release after rough-in inspection
  - Need from them: In-slab and underslab conduit, floor boxes and stub-ups at locations from current furniture and equipment layouts, within those limits, inspected before the pour
  - If missed: Conduit bundles in thin slabs or tendon zones, or floor boxes in the wrong place; cracking, coring and poke-throughs after the fact
- **[medium] if.03-grounding-electrode** → Grounding and bonding (26 05 26) · Gate: foundation_pour
  - Send them: Footing reinforcing and a pour hold so the concrete-encased electrode can be installed, bonded and inspected
  - Need from them: Electrode location, conductor or bar extension and stub-up locations, and the electrical inspection before the pour
  - If missed: Footings poured without the concrete-encased electrode or its stub-up; a substitute electrode system and an inspection finding
- **[medium] if.03-site-concrete** → Concrete paving, walks and curbs (32 13 13, 32 16 00) · Gate: site_paving
  - Send them: Finished floor elevation at every exterior door and the slab-edge ledge or recess that supports the exterior slab
  - Need from them: Exterior slab elevation flush with the threshold on the accessible route, slope away from the building, isolation joint and doweling at the building, and an air-entrained exterior mix
  - Confirm who: Exterior stoops and slabs at building entrances — typical install 03 30 00 or 32 13 13
  - If missed: Exterior slab settles or is placed low at the door; a step on the accessible route and water draining toward the building

## Failure modes to watch (22)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d03.fm.cored-blind** — A trade cores or drills placed concrete for a late penetration or anchor without scanning or the engineer's acceptance → Cut reinforcing, a released tendon or a severed live conduit; structural repair, shoring, or an outage (caught by d03.coring-scanning; industry_practice)
- **d03.fm.decision-without-strength** — Forms stripped, shores pulled, tendons stressed or panels lifted on the calendar, with no field-cured specimen or maturity data behind it → Cracking, excess deflection or anchorage failure; or the work stops while everyone waits for a test nobody scheduled (caught by d03.inspection-and-testing; industry_practice)
- **d03.fm.inspection-not-called** — Placement goes ahead before the special inspector has seen the reinforcing, embeds or tendons → The building official asks for cores, scanning or exposure of the work, or rejects it (caught by d03.inspection-and-testing; industry_practice)
- **d03.fm.unprotected-cold-placement** — Concrete or grout placed in cold weather without protection or temperature records, or allowed to freeze early → Strength loss and surface scaling found later; cores, repair or removal (caught by d03.weather-limits; industry_practice)
- **d03.fm.residue-blocks-bond** — Release agent, curing compound, bond breaker or sealer left on concrete that the later membrane, adhesive or coating manufacturer does not accept → Disbonded waterproofing, flooring or coating; surface removal by grinding or blasting and a fight over who pays (caught by d03.surface-compatibility; industry_practice)
- **03cip.fm.cast-in-missed** — Anchor rods, embeds or sleeves not in the forms at the pour because the trade's shop drawings were not approved or never reached the concrete crew → Post-installed anchors needing the engineer's acceptance and special inspection, coring through reinforcing, or demolition (caught by 03cip.cast-in-before-pour, 03cip.rc.embeds-anchor-rods, 03cip.rc.sleeves, if.03-steel-anchorage, if.03-sleeves; industry_practice)
- **03cip.fm.air-in-troweled-slab** — Air-entrained concrete hard-troweled or given a dry-shake hardener on an interior slab → Blistering and delamination of the surface, found at grinding, polishing or after the flooring is down (caught by 03cip.air-in-troweled-slab; industry_practice)
- **03cip.fm.slab-never-dried** — Moisture-sensitive flooring scheduled on a slab that cannot dry in time (lightweight concrete on deck, missing or misplaced retarder, late dry-in) → Adhesive failure, bubbling and odor after occupancy; a moisture mitigation system added at the end of the job (caught by 03cip.drying-before-flooring, 03cip.vapor-retarder, if.03-flooring-substrate; industry_practice)
- **03cip.fm.one-curing-method** — One curing compound used across the whole slab, including areas scheduled for adhered flooring, coatings or a polished finish → Compound ground or blasted off before flooring, or bond failures after it (caught by 03cip.curing-by-area; industry_practice)
- **03cip.fm.retarder-punctured** — Vapor retarder punctured by stakes, supports and foot traffic, penetrations left unbooted, or fill above it saturated by rain before the pour → A moisture source under the slab that no surface treatment fully cures (caught by 03cip.vapor-retarder; industry_practice)
- **03cip.fm.depression-short** — Depression cast to the tile thickness without the membrane and setting bed, or left out where a recessed mat or terrazzo goes → Finish stands proud of the adjacent floor; trip edge at doors, grinding or leveling, threshold changes (caught by 03cip.rc.depressions, if.03-flooring-substrate; industry_practice)
- **03cip.fm.pad-from-schedule** — Pads formed from the scheduled equipment before the equipment submittal was approved → Pad too small for the anchors or equipment; chipped out and re-poured (caught by 03cip.rc.housekeeping-pads, if.03-housekeeping-pads; industry_practice)
- **03cip.fm.recess-left-out** — A product that sits in the slab (floor closer, sliding-door track, mobile shelving rail, cart-loading sterilizer) is selected after the pour, or its recess never reaches the concrete crew → A finished slab sawcut and chipped near reinforcing or tendons, or a raised deck and threshold on the accessible route (caught by if.03-floor-recesses; industry_practice)
- **03cip.fm.late-sawcut** — Contraction joints sawn too late or too shallow, or laid out without the flooring in mind → Random cracks that telegraph through flooring, and tile cracking over joints with no movement joint above (caught by 03cip.slab-joints; industry_practice)
- **03cip.fm.water-at-the-truck** — Water added at the truck to ease placement or pumping → Low strength and durability, failed breaks, cores and a dispute over who pays (caught by 03cip.site-water, d03.inspection-and-testing; industry_practice)
- **03cip.fm.mass-cracking** — Thick foundation placed with no temperature control → Thermal cracking through the element, and an engineering evaluation before it can be accepted (caught by 03cip.mass-placements; industry_practice)
- **edu.fm.default-risk-category** — Delegated cladding, joist or anchorage design done to the default risk category on a school assigned a higher one → Components under-designed; recalculation and field reinforcement after installation (caught by edu.risk-category-delegated; industry_practice)
- **edu.fm.shelter-assembly-broken** — Shelter doors, frames, hardware or louvers submitted as standard products, or tested components mixed across manufacturers → The shelter boundary no longer matches a tested assembly; doors, frames or louvers replaced before occupancy (caught by edu.storm-shelter; industry_practice)

## Expected submittal contents
- **Design Data**
  - The placements each mix is for (element, exposure class, finish), not a generic list of strengths
  - Strength and test age, maximum water-cementitious ratio, air content, cementitious materials with SCM type and proportion
  - Aggregate source, size and gradation, with alkali-silica reactivity data and mitigation where the spec requires it
  - Admixtures with dosage ranges, slump or slump flow, and how much water (if any) may be added at the site
  - Strength test record or trial batches supporting the required average strength
- **Product Data**
  - Vapor retarder with its classification, thickness, seam tape and penetration boots
  - Curing method and products by area, joint fillers, bonding agents and repair materials
- **Shop Drawings**
  - Slab joint layout (contraction, construction and isolation joints) and placement sequence
- **Test Reports**
  - Field tests and strength results tied to placement location, with specimen curing method identified

## Extract for reconciliation
- 03cip.xf.mixes — Mixes by placement (strength and age, water-cementitious ratio, air, SCMs, aggregate size, slump or flow) (list, per package) → drawings.structural, spec.part2
- 03cip.xf.vapor-retarder — Vapor retarder product, classification, thickness and location (string, per package) → spec.part2, drawings.details
- 03cip.xf.curing — Curing method by slab area (list, per package) → schedule.finish, spec.part3

## Standards to verify against
- ACI 301 (ACI SPEC-301): Specifications for Concrete Construction
- ACI 305.1 (ACI SPEC-305.1) / ACI PRC-306: Specification for Hot Weather Concreting; Guide to Cold Weather Concreting — ACI lists the cold weather specification ACI 306.1 (1990) as historical; a project spec that still cites it adopts it, so check which document the spec names
- ASTM C172/C172M / ASTM C31/C31M / ASTM C39/C39M: Sampling freshly mixed concrete; making and curing test specimens in the field; compressive strength of cylindrical specimens
- ASTM C94/C94M: Standard Specification for Ready-Mixed Concrete
- ASTM E1745: Plastic Water Vapor Retarders Used in Contact with Soil or Granular Fill under Concrete Slabs
- ASTM E1643: Selection, Design, Installation, and Inspection of Water Vapor Retarders Used in Contact with Earth or Granular Fill Under Concrete Slabs
- ACI PRC-302.1: Guide to Concrete Floor and Slab Construction
- ACI PRC-302.2: Concrete Slabs that Receive Moisture-Sensitive Flooring Materials — Guide — Earlier edition titled "Guide for Concrete Slabs that Receive Moisture-Sensitive Flooring Materials"
- ACI 308.1 (ACI SPEC-308.1): External Curing of Cast-in-Place Concrete — Specification — Earlier edition titled "Specification for Curing Concrete"
- ASTM C309 / ASTM C1315: Liquid membrane-forming compounds for curing concrete; and those with special properties for curing and sealing

## Warnings
- Draft knowledge in use (global, 03, 03 30 00) — not yet PE-reviewed
