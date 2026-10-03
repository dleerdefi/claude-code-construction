# Compiled knowledge — 05 51 00 Metal Stairs

Facility types: education.k12 · Confidence floor: **draft** · Review mode: per_element · Contractor-designed: typical
Lineage: global → 05 → 05 50 00 → 05 51 00
Overlays: education, education.k12
Also specified as: 05 71 00

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Steel pan, plate and grating stairs, their landings, guards and handrails, feature stairs, and ladders where they are specified with the stairs. The architect sets the geometry; the stair engineer designs stringers, landings and connections to the loads and criteria the documents give, and every reaction lands on structure or walls someone else built. Riser uniformity is unforgiving, so floor-to-floor heights and finish thicknesses have to be known before fabrication. Stairs usually go in early as construction access, so sequence, pan fill and protection of nosings are part of the review.

## Review checks (24)
### completeness
- **[critical] edu.storm-shelter** — Where the school has a storm shelter or safe room, every element of the shelter envelope (walls, roof deck and covering, doors with their frames and hardware, windows, louvers and penetrations) is submitted with evidence that it meets ICC 500 pressure and debris-impact testing as the tested assembly, and the shelter's ventilation, emergency lighting, toilets and power are shown. One standard door, louver or hardware substitution in the shelter boundary breaks the shelter.  
  Trace: drawings.life_safety, drawings.plans, spec.part2 · Owner: subcontractor · Scope: package · Gate: procurement_release · _overlay:education.k12_
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] g.contractor-designed** — This scope is often performance-specified and designed or selected by the contractor. Confirm the spec's design criteria are complete enough to design to; whether the AHJ treats the design as a deferred submittal and when it must be filed relative to installation; and that the designer's assumptions about support, attachment and adjacent work are confirmed by the trades that provide them.  
  Trace: spec.part1, spec.part2 · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] d05.special-inspection** — The statement of special inspections covers every Division 05 element this building needs inspected (structural welding and high-strength bolting, deck fastening and shear studs, open web joists, cold-formed framing, anchors into concrete), and either names an inspector for work done in the fabricator's shop or relies on the fabricator's approved status. Both are settled before fabrication starts, not when the first load arrives.  
  Trace: register.special_inspections, spec.part1 · Owner: gc · Scope: package · Gate: procurement_release · _05_
- **[high] 05ms.design-criteria** — The documents give the stair engineer what to design to: live loads from the structural general notes, guard and handrail loads, deflection limits, vibration criteria for long-span and feature stairs, and the supports available at each floor and landing. Feature stairs also carry the architect's limits on stringer depth and visible connections.  
  Trace: drawings.structural, spec.part1, drawings.details · Owner: design_team · Scope: package · Gate: procurement_release · _05 51 00_
- **[medium] g.products-marked** — Cut sheets covering a product family have the proposed model, size, options, finish and accessories clearly marked; unmarked sheets are returned.  
  Trace: spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data · _global_
### conformance
- **[high] g.current-documents** — The submittal reflects the current contract documents, including addenda, ASIs, bulletins and responded RFIs, not the bid set. Note the drawing revision the submitter worked from.  
  Trace: drawings.revision_blocks, register.asi_bulletin_log, register.rfi_log · Owner: gc · Scope: package · _global_
- **[high] g.basis-of-design** — Proposed manufacturer and model match the basis of design or a listed acceptable manufacturer. Anything else follows the comparable-product or substitution procedure Division 01 allows, with its timing and comparison data, before it is reviewed on its merits.  
  Trace: spec.part2_manufacturers, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] g.deviations-identified** — Every deviation from the contract documents is clouded or listed by the submitter. Compare independently; do not rely on the submitter's list.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _global_
- **[high] d05.post-installed-anchors** — Every post-installed anchor (railing posts, equipment and stair supports, clips, fixes for missed rods and embeds) is the product, size and embedment the design assumed, with an evaluation report for the base material and condition: cracked concrete, seismic, masonry, adhesive in sustained tension. A different anchor is a redesign, not an equal. Drilling locations are scanned for reinforcing and post-tensioning tendons first.  
  Trace: drawings.structural, drawings.details, spec.part2 · Owner: subcontractor · Scope: package · _05_
- **[high] edu.risk-category-delegated** — Delegated designs (cladding and curtain wall, roofing attachment, joists and trusses, nonstructural and equipment anchorage) state the risk category and importance factors they used, and these match the structural general notes; schools are often assigned above the default, and designers who assume the default under-design.  
  Trace: drawings.structural, spec.part1_submittals · Owner: subcontractor · Scope: package · _overlay:education_
- **[medium] d05.duplex-coating** — Where galvanized steel is painted or powder coated, the submittal states the surface preparation for zinc, a primer or powder system compatible with galvanizing, and who applies each coat. Galvanizing damaged by welding or handling is repaired by a method the spec accepts, and the repair is compatible with the topcoat.  
  Trace: spec.part2, spec.part3 · Owner: subcontractor · Scope: package · _05_
- **[medium] d05.dissimilar-metals** — Contact between dissimilar metals (aluminum, stainless steel or copper against carbon or galvanized steel), and between aluminum and concrete, mortar or treated wood, is isolated by the method the spec requires, and fasteners are compatible with both parts they join.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _05_
- **[medium] 05mf.ladders** — Fixed ladders and ship ladders show rung spacing, clearances, rail extension at the landing, roof or hatch, the cage or ladder safety system the hook calls for, and attachment to structure; roof access ladders line up with the hatch location as built.  
  Trace: drawings.details, drawings.roof_plan, drawings.building_sections · Owner: subcontractor · Scope: package · _05 50 00_
### coordination
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
- **[high] 05mf.reactions-to-structure** — Each delegated fabrication design states the reaction at every attachment, and the engineer of record confirms that the slab edge, beam, joist, wall or framing it lands on can take it before the item is fabricated.  
  Trace: drawings.structural, spec.part1_submittals · Owner: gc · Scope: element · Gate: procurement_release · _05 50 00_
- **[medium] 05ms.treads-finish** — Tread and landing construction is resolved: concrete fill in pans and landings with its reinforcing and the trade that places it, nosing type and profile to the accessibility standard, and the thickness of any applied tread or landing finish carried into the riser layout.  
  Trace: drawings.details, schedule.finish, spec.part1 · Owner: gc · Scope: element · _05 51 00_
- **[medium] 05ms.rails-scope** — One section furnishes the stair guards and handrails (this one or 05 52 00), they are detailed with the stair, and they carry through landings and turns with the extensions the hook requires.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · Gate: procurement_release · _05 51 00_
### constructability
- **[high] 05ms.field-verify** — Floor-to-floor heights are measured on the built structure before the stair is released for fabrication, and the risers are laid out for the as-built heights so riser and tread variation stays within the adopted code's tolerance. Where the stair has to be fabricated ahead of the slabs to serve as access, it is detailed from surveyed top-of-steel or slab-edge elevations plus the slab and finish thicknesses, with the point where the difference is taken up (a landing or a field-set connection) shown on the shop drawings.  
  Trace: drawings.building_sections, schedule.master · Owner: gc · Scope: element · Gate: procurement_release · _05 51 00_
- **[high] 05ms.support** — Every stringer and landing lands on something designed for its reaction: hangers from the floor above, posts to the slab, or embeds in concrete or masonry enclosure walls placed before the pour or grout lift. Support from gypsum shaft walls or non-structural framing needs structural framing designed in, and attachments to rated exit enclosure walls keep the wall's listing.  
  Trace: drawings.structural, drawings.enlarged_plans, schedule.partition_type · Owner: design_team · Scope: element · Gate: procurement_release · _05 51 00_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[medium] d05.galvanizing-fabrication** — Items to be hot-dip galvanized are detailed for the process: vent and drain holes in every closed section and enclosed space, placed where they are acceptable on exposed work; thin, long or asymmetric pieces reviewed for distortion; assemblies sized for the galvanizer's kettle or split with bolted field splices.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · Types: Shop Drawings · Gate: procurement_release · _05_
- **[medium] 05ms.construction-use** — If stairs serve as construction access, the plan says when each stair is set relative to the structure (shafts are hard to reach once the floors above are framed), how unfilled pans get temporary treads, and how nosings and finishes are protected until turnover.  
  Trace: schedule.master, spec.part1 · Owner: gc · Scope: package · Gate: steel_erection · _05 51 00_

## Reconciliations — documents that must agree (2)
- **[high] 05mf.rc.embeds** — Every embed called for anywhere in the documents (curtain wall and canopy connections, railing and stair supports, equipment and hoist supports, door and gate frames) is on the embed layout, and the layout agrees with the approved concrete placement or masonry drawings the trade will set from, at the same location and elevation, before the pour or the grout lift reaches it.  
  Between: drawings.structural ↔ drawings.details ↔ drawings.wall_sections ↔ drawings.mechanical ↔ drawings.electrical ↔ submittals.approved · Key: Embedded item or mark · Fields: location, elevation, plate size and anchors, item it supports, furnishing trade · Owner: gc · Gate: slab_pour · _05 50 00_
- **[high] 05ms.rc.geometry** — Floor-to-floor heights, riser counts and landing elevations agree across the stair plans, sections and the structural slab elevations, and the finishes at floors and landings are included so the top and bottom risers match the rest of the flight.  
  Between: drawings.enlarged_plans ↔ drawings.building_sections ↔ drawings.structural ↔ schedule.finish · Key: Stair and flight · Fields: floor-to-floor height, riser count and height, tread depth, landing size and elevation, headroom, finish thickness at floors and landings · Owner: design_team · Gate: procurement_release · _05 51 00_

## Compliance — regulatory hooks (10)
- **[critical] edu.rh.storm-shelter** (`storm-shelter-requirements`) — Does the adopted building code require a storm shelter for this school (tornado design wind speed, occupant load), what capacity and location does it need, which ICC 500 edition governs, and what special inspection applies to the shelter?  
  **Unbound** → Run /construction:code-researcher with research topic "storm-shelter-requirements" (seed it with this hook's question)
- **[high] d05.rh.steel-special-inspection** (`steel-special-inspection`) — Which special inspections does the adopted building code require for the steel work on this building (structural welding and high-strength bolting, steel deck, open web joists, cold-formed steel framing, and the seismic force-resisting system where it applies), at what frequency, and which of them hold the work uncovered until they are done?  
  **Unbound** → Run /construction:code-researcher with research topic "steel-special-inspection" (seed it with this hook's question)
- **[high] d05.rh.fabricator-inspection** (`fabricator-special-inspection`) — Does the adopted code require in-plant special inspection of the steel fabricator, joist manufacturer or other shop producing structural members for this project, or accept an approved or certified fabricator in its place, and what certificate of compliance must be filed?  
  **Unbound** → Run /construction:code-researcher with research topic "fabricator-special-inspection" (seed it with this hook's question)
- **[high] d05.rh.post-installed-anchors** (`post-installed-anchor-inspection`) — For post-installed anchors in this metals work (railing and stair posts, equipment supports, clips, repairs of missed rods and embeds), what evaluation report, special inspection, proof loading and installer certification does the adopted code require?  
  **Unbound** → Run /construction:code-researcher with research topic "post-installed-anchor-inspection" (seed it with this hook's question)
- **[high] 05mf.rh.guards-handrails** (`guard-handrail-requirements`) — Where do the adopted building code and accessibility standard require guards and handrails on these metal stairs, ramps, landings, platforms, mezzanines and floor openings, and which heights, infill opening limits, handrail extensions, graspable profiles and guard and handrail design loads apply?  
  **Unbound** → Run /construction:code-researcher with research topic "guard-handrail-requirements" (seed it with this hook's question)
- **[high] 05ms.rh.geometry** (`stair-geometry-requirements`) — What riser and tread limits, dimensional uniformity tolerance, nosing projection and profile, headroom, and landing depth and width do the adopted building code and accessibility standard require for these stairs, including any exit stair width set by occupant load?  
  **Unbound** → Run /construction:code-researcher with research topic "stair-geometry-requirements" (seed it with this hook's question)
- **[high] edu.rh.risk-category** (`building-risk-category-assignment`) — What risk category applies to this building under the adopted code (occupant load, designation as an emergency or community shelter), and which design loads, nonstructural anchorage and special inspections change because of it?  
  **Unbound** → Run /construction:code-researcher with research topic "building-risk-category-assignment" (seed it with this hook's question)
- **[medium] d05.rh.steel-erection-safety** (`steel-erection-safety-design`) — What does the applicable federal or state steel erection safety standard require of the design and shop drawings (anchor rods at each column, connections that keep a member supported while the next is bolted, stabilization of joists and joist girders at columns, erection bridging, shear connectors installed in the field, perimeter safety cable attachment), and does the submittal provide it?  
  **Unbound** → Run /construction:code-researcher with research topic "steel-erection-safety-design" (seed it with this hook's question)
- **[medium] 05mf.rh.fixed-ladders** (`fixed-ladder-requirements`) — Where do the adopted building code and occupational safety rules allow fixed or ship ladders as access, and what do they require of them here (rung spacing and clearances, extension above the landing, cage, ladder safety system or personal fall arrest)?  
  **Unbound** → Run /construction:code-researcher with research topic "fixed-ladder-requirements" (seed it with this hook's question)
- **[medium] 05ms.rh.tread-marking** (`stair-nosing-contrast-marking`) — Must these metal stairs carry luminous egress path markings (on nosings, landings and handrails, by building height or occupancy) or contrasting stripes on treads and nosings, and where does each marking have to go?  
  **Unbound** → Run /construction:code-researcher with research topic "stair-nosing-contrast-marking" (seed it with this hook's question)

## Coordination routing (4)
- **[critical] if.03-steel-anchorage** → Cast-in-place concrete, cast-in anchors and grouting (03 30 00, 03 15 00, 03 60 00) · Gate: foundation_pour — The steel anchor rod layout is approved before footing and pier forms close; the as-built survey is accepted before steel_erection
  - Send them: Approved anchor rod and embed layouts (location, elevation, projection, rod size and pattern, plate size) and the fabricated items, delivered before forms close; any post-installed fix proposed with an evaluation report for the engineer's acceptance
  - Need from them: Anchor rods and embed plates set from the approved steel and metals layouts and surveyed before the pour; grout under base and bearing plates once the frame is plumbed and released
  - Confirm who: Anchor rods and embed plates — typical furnish 05 12 00 or 05 50 00 / install 03 30 00
  - Confirm who: Grout under column base plates and bearing plates — typical furnish 03 60 00 or 05 12 00 / install 03 60 00 or 05 12 00
  - If missed: Anchor rods, embeds or sleeves not in the forms at the pour because the trade's shop drawings were not approved or never reached the concrete crew; Base plates left ungrouted on leveling nuts while the frame is loaded; Anchor rods cast out of position, rotated or at the wrong projection, found as the column is set
- **[high] if.05-railing-backing** → Rough carpentry and metal framing (06 10 53, 09 22 16) · Gate: wall_close_in
  - Send them: Wall bracket locations, heights, loads and fasteners for every wall-mounted handrail
  - Need from them: Backing designed for the bracket loads, installed and checked before the wall is boarded
  - Confirm who: Backing for wall-mounted handrails — typical furnish 06 10 53 or 09 22 16 / install 06 10 53 or 09 22 16
  - If missed: Wall-mounted handrail brackets with no backing installed before the board went on
- **[high] if.fireproofing-hangers** → Applied fireproofing (07 81 00) · Gate: fireproofing_application
  - Send them: Hangers, clips and supports attached to steel before application in each area
  - Need from them: Application sequence by area, and the patching procedure for later attachments
  - If missed: MEP trades attach hangers after fireproofing is applied; Brace and hanger attachment points chosen after the steel was sprayed with fireproofing; Trapezes and hanger rods for heavy drainage mains attached to steel after spray fireproofing
- **[medium] if.03-stair-pan-fill** → Cast-in-place concrete (03 30 00)
  - Send them: Pans and landing forms ready for fill, nosings and anchors in place, and the stair erected and accepted before the fill
  - Need from them: Concrete fill in pans and landings with the reinforcing, finish and nosing embedment the details show, placed in time for the stair to serve as construction access
  - Confirm who: Concrete fill in metal pan stairs and landings — typical furnish 03 30 00 or 05 51 00 / install 03 30 00 or 05 51 00

## Failure modes to watch (21)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d05.fm.covered-before-inspection** — Welds, bolted connections, deck fastening or studs concealed by fireproofing, concrete or finishes before the special inspector sees them → Fireproofing stripped or slabs cored to inspect, or the AHJ withholds acceptance of the frame (caught by d05.special-inspection; industry_practice)
- **d05.fm.shop-uninspected** — Fabricator is not approved under a program the AHJ accepts and no in-plant inspection was arranged → Members arrive with no compliance record; inspection after the fact on erected steel, or rejection (caught by d05.special-inspection; industry_practice)
- **d05.fm.anchor-swap** — Installer substitutes a different post-installed anchor or adhesive, or drills without scanning → Anchors rejected at inspection, proof-tested or replaced; cut tendons or bars in the slab (caught by d05.post-installed-anchors; industry_practice)
- **d05.fm.paint-on-zinc** — Finish paint or powder coat applied over galvanizing without zinc-compatible preparation → Coating peels in sheets within a few seasons; stripping and recoating in place (caught by d05.duplex-coating; industry_practice)
- **d05.fm.unvented-sections** — Closed sections sent to the galvanizer without vent and drain holes, or holes added where they show → Pieces ruptured or rejected and refabricated; visible holes on finished railings and exposed frames (caught by d05.galvanizing-fabrication; industry_practice)
- **d05.fm.galvanic-corrosion** — Aluminum or stainless items fastened to carbon steel, or aluminum set in concrete or mortar, with no isolation → Corrosion and staining at the contact and loss of anchorage over time (caught by d05.dissimilar-metals; industry_practice)
- **05mf.fm.embed-missed** — Embed plates for railings, canopies, curtain wall or equipment left off the layout the concrete trade set from → Post-installed anchors or through-bolts designed under schedule pressure; some conditions cannot be anchored at all (caught by 05mf.rc.embeds, if.03-steel-anchorage; industry_practice)
- **05mf.fm.reaction-unchecked** — A canopy, platform, support frame or stair anchored to a slab edge, joist or framing never checked for its reactions → The supporting structure reinforced after the item is installed (caught by 05mf.reactions-to-structure; industry_practice)
- **05mf.fm.ladder-noncompliant** — Ladder fabricated without the extension, cage or ladder safety system the applicable rules require → Rejected at inspection; ladder modified or replaced in place (caught by 05mf.ladders; industry_practice)
- **05ms.fm.drawn-floor-heights** — Stair fabricated to the drawn floor-to-floor height instead of the built slabs → Top or bottom riser out of tolerance; flights refabricated or rejected at inspection (caught by 05ms.field-verify, 05ms.rc.geometry; industry_practice)
- **05ms.fm.finish-thickness** — Floor or landing finishes thicker or thinner than the riser layout assumed → Uneven first and last risers after finishes; grinding, built-up nosings or rebuilt landings (caught by 05ms.rc.geometry, 05ms.treads-finish; industry_practice)
- **05ms.fm.shaft-wall-support** — Stringers or landings fastened to gypsum shaft wall framing never designed to carry them → Posts or hangers added inside a finished enclosure, and the enclosure rating compromised by the fix (caught by 05ms.support; industry_practice)
- **05ms.fm.pan-fill-gap** — Concrete fill in stair pans and landings carried by neither the stair nor the concrete subcontract → Change order, and stairs that cannot be used as access until someone fills them (caught by 05ms.treads-finish, if.03-stair-pan-fill; industry_practice)
- **05ms.fm.lively-feature-stair** — Feature stair designed for strength only, with no vibration criterion → A lively stair the owner rejects; stiffening that changes the architecture (caught by 05ms.design-criteria; industry_practice)
- **05ms.fm.set-too-late** — Stairs scheduled after the floors above closed off crane access to the shaft → Flights hand-set in pieces, temporary access kept longer, schedule loss (caught by 05ms.construction-use; industry_practice)
- **edu.fm.default-risk-category** — Delegated cladding, joist or anchorage design done to the default risk category on a school assigned a higher one → Components under-designed; recalculation and field reinforcement after installation (caught by edu.risk-category-delegated; industry_practice)
- **edu.fm.shelter-assembly-broken** — Shelter doors, frames, hardware or louvers submitted as standard products, or tested components mixed across manufacturers → The shelter boundary no longer matches a tested assembly; doors, frames or louvers replaced before occupancy (caught by edu.storm-shelter; industry_practice)

## Expected submittal contents
- **Qualification Statements**
  - Fabricator and erector certification or the AHJ's approved-fabricator status, where the spec or the code relies on it
  - Welding procedure specifications and welder qualifications for every process and position used, including sheet steel welding of deck, studs and cold-formed framing
- **Shop Drawings**
  - Plan and section of each stair with field-verified floor-to-floor heights, riser and tread dimensions, landing elevations and headroom
  - Stringer, landing and support framing with every connection to structure or enclosure walls, and the embeds those connections need
  - Tread and landing construction (pan and fill, plate, grating), nosing type and finish
  - Guards and handrails with heights, infill, extensions and post and bracket attachment
- **Delegated Design**
  - Sealed calculations with the live, guard and handrail loads used, deflection and vibration criteria, and the reaction at each support

## Extract for reconciliation
- d05.xf.coatings — Coating system by item and exposure (bare, primed, galvanized, duplex) (list, per package) → spec.part2
- d05.xf.post-installed-anchors — Post-installed anchor product, size, embedment and evaluation report per condition (list, per package) → drawings.structural, drawings.details
- 05mf.xf.items — Fabricated items with the drawing and detail reference for each (list, per package) → drawings.details, drawings.structural
- 05mf.xf.embeds — Embed marks with location, elevation and receiving trade (list, per package) → drawings.structural, drawings.details
- 05ms.xf.geometry — Floor-to-floor height, riser count and height, tread depth per flight (list, per element) → drawings.building_sections, drawings.enlarged_plans
- 05ms.xf.reactions — Support reactions per stair (list, per element) → drawings.structural

## Standards to verify against
- AISC 207: Standard for Certification Programs
- AWS D1.3/D1.3M: Structural Welding Code — Sheet Steel
- ASTM A123/A123M: Standard Specification for Zinc (Hot-Dip Galvanized) Coatings on Iron and Steel Products
- ASTM A385/A385M: Standard Practice for Providing High-Quality Zinc Coatings (Hot-Dip)
- ASTM A780/A780M: Standard Practice for Repair of Damaged and Uncoated Areas of Hot-Dip Galvanized Coatings
- ASTM D6386 / ASTM D7803: Standard Practice for Preparation of Zinc (Hot-Dip Galvanized) Coated Iron and Steel Product and Hardware Surfaces for Painting; and for Powder Coating
- ACI CODE-355.2 / ACI CODE-355.4: Post-Installed Mechanical Anchors in Concrete — Qualification Requirements; Post-Installed Adhesive Anchors in Concrete — Qualification Requirements — Editions before the current ones are titled "Qualification of Post-Installed Mechanical (or Adhesive) Anchors in Concrete"
- NAAMM AMP 510: Metal Stairs Manual (National Association of Architectural Metal Manufacturers)
- AISC Design Guide 11: Vibrations of Steel-Framed Structural Systems Due to Human Activity

## Suppressed
- 05mf.scope-coverage (from 05 50 00) by 05 51 00 — Miscellaneous-item buyout check; stair scope gaps are covered by the stair checks
- 05mf.fm.support-steel-orphan (from 05 50 00) by 05 51 00 — Miscellaneous-item buyout failure; not a stair pattern
- 05mf.bollards (from 05 50 00) by 05 51 00 — Not part of stair work
- 05mf.fm.bollard-utility-strike (from 05 50 00) by 05 51 00 — Not part of stair work
- 05mf.rh.vehicle-impact (from 05 50 00) by 05 51 00 — Not part of stair work
- if.04-shelf-angles (from interfaces:div-04) by 05 51 00 — Masonry shelf angles are misc-metals items, not stair or railing scope
- if.04-loose-lintels (from interfaces:div-04) by 05 51 00 — Loose lintels are misc-metals items, not stair or railing scope
- if.04-wall-top-anchorage (from interfaces:div-04) by 05 51 00 — Masonry wall-top anchorage to the frame; no stair or railing component
- if.05-cladding-anchorage (from interfaces:div-05) by 05 51 00 — Cladding support steel; no stair or railing component
- if.05-overhead-door-supports (from interfaces:div-05) by 05 51 00 — Door support steel; no stair or railing component
- if.05-elevator-supports (from interfaces:div-05) by 05 51 00 — Hoistway support steel; no stair or railing component
- if.05-escalator-supports (from interfaces:div-05) by 05 51 00 — Escalator wellway and truss supports; no stair or railing component
- if.05-equipment-support-steel (from interfaces:div-05) by 05 51 00 — MEP equipment dunnage; no stair or railing component
- if.05-suspended-equipment-supports (from interfaces:div-05) by 05 51 00 — Hung equipment supports; no stair or railing component
- if.roof-equipment-curbs (from interfaces:div-07) by 05 51 00 — Roof equipment support; no stair or railing component
- if.casework-backing (from interfaces:div-12) by 05 51 00 — Casework support steel; no stair or railing component

## Warnings
- Draft knowledge in use (global, 05, 05 50 00, 05 51 00) — not yet PE-reviewed
