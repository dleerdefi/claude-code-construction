# Compiled knowledge — 07 54 00 Membrane Roofing

Facility types: education.k12 · Confidence floor: **draft** · Review mode: package · Contractor-designed: sometimes
Lineage: global → 07 → 07 50 00 → [07 54 00 missing]
Overlays: education, education.k12

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Low-slope membrane roofing of any type (modified bitumen, EPDM, TPO, PVC, protected membrane); the type sections inherit from here. The roof is a system warranted by one manufacturer and penetrated by every MEP trade. The misses are drainage (primary and overflow), penetrations that cannot be flashed, attachment that does not match the design wind pressures, decks that are too wet to adhere to, and damage by other trades after the membrane is down.

## Review checks (27)
### completeness
- **[critical] edu.storm-shelter** — Where the school has a storm shelter or safe room, every element of the shelter envelope (walls, roof deck and covering, doors with their frames and hardware, windows, louvers and penetrations) is submitted with evidence that it meets ICC 500 pressure and debris-impact testing as the tested assembly, and the shelter's ventilation, emergency lighting, toilets and power are shown. One standard door, louver or hardware substitution in the shelter boundary breaks the shelter.  
  Trace: drawings.life_safety, drawings.plans, spec.part2 · Owner: subcontractor · Scope: package · Gate: procurement_release · _overlay:education.k12_
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] g.contractor-designed** — This scope is often performance-specified and designed or selected by the contractor. Confirm the spec's design criteria are complete enough to design to; whether the AHJ treats the design as a deferred submittal and when it must be filed relative to installation; and that the designer's assumptions about support, attachment and adjacent work are confirmed by the trades that provide them.  
  Trace: spec.part1, spec.part2 · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] d07.warranty-conditions** — Where a manufacturer's system warranty is specified, the submittal shows the installer's approval by that manufacturer, that every component in the assembly is accepted under the warranty, and any pre-approval or inspection the manufacturer requires before and after installation.  
  Trace: spec.part1, spec.part2 · Owner: subcontractor · Scope: package · _07_
- **[medium] g.products-marked** — Cut sheets covering a product family have the proposed model, size, options, finish and accessories clearly marked; unmarked sheets are returned.  
  Trace: spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data · _global_
- **[medium] rf.leak-detection-ready** — Where electronic leak detection is specified, the method suits the membrane and deck (a conductive deck, or a conductive layer under the membrane, since some methods cannot test conductive membranes), and any conductive layer is installed with the roofing.  
  Trace: spec.part3, spec.part2 · Owner: subcontractor · Scope: package · Gate: procurement_release · _07 50 00_
### conformance
- **[high] g.current-documents** — The submittal reflects the current contract documents, including addenda, ASIs, bulletins and responded RFIs, not the bid set. Note the drawing revision the submitter worked from.  
  Trace: drawings.revision_blocks, register.asi_bulletin_log, register.rfi_log · Owner: gc · Scope: package · _global_
- **[high] g.basis-of-design** — Proposed manufacturer and model match the basis of design or a listed acceptable manufacturer. Anything else follows the comparable-product or substitution procedure Division 01 allows, with its timing and comparison data, before it is reviewed on its merits.  
  Trace: spec.part2_manufacturers, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] g.deviations-identified** — Every deviation from the contract documents is clouded or listed by the submitter. Compare independently; do not rely on the submitter's list.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _global_
- **[high] d07.system-compatibility** — Products that touch in the assembly (membranes, primers, flashings, tapes, sealants, adhesives, insulation, coatings) are confirmed compatible by their manufacturers, in writing where the spec requires. Transitions between two manufacturers' products are the usual gap.  
  Trace: spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data, Certificates · _07_
- **[high] rf.drainage** — Tapered insulation and structural slope together drain every area to a drain or scupper, with crickets and saddles at curbs, walls and between drains, and no low spots at roof edges or around equipment.  
  Trace: drawings.roof_plan, drawings.structural · Owner: subcontractor · Scope: package · Types: Shop Drawings · _07 50 00_
- **[high] rf.attachment-zones** — The attachment or adhesive pattern changes by roof zone according to the design wind pressures or the approval listing the spec requires, and the listing or calculation covers the exact assembly submitted (deck, insulation, cover board, membrane, fasteners).  
  Trace: spec.part2, drawings.structural · Owner: subcontractor · Scope: package · Types: Shop Drawings, Design Data · _07 50 00_
- **[high] rf.edge-securement** — Edge metal, copings and gravel stops are tested or approved systems as the spec and code require, fastening is shown, and the installer of edge metal and counterflashing is assigned.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _07 50 00_
- **[high] edu.risk-category-delegated** — Delegated designs (cladding and curtain wall, roofing attachment, joists and trusses, nonstructural and equipment anchorage) state the risk category and importance factors they used, and these match the structural general notes; schools are often assigned above the default, and designers who assume the default under-design.  
  Trace: drawings.structural, spec.part1_submittals · Owner: subcontractor · Scope: package · _overlay:education_
### coordination
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
- **[high] d07.transition-ownership** — Where layers installed by different trades meet (below-grade waterproofing to wall air barrier, wall air barrier to roofing, air barrier to window and curtain wall frames), the trade that makes the connection and the transition material are assigned in the contract documents or subcontracts.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · Gate: procurement_release · _07_
- **[medium] rf.equipment-supports** — Rooftop equipment sits on curbs or supports flashed into the membrane, tall enough to allow future reroofing, with a protected path from the roof access point to each unit.  
  Trace: drawings.roof_plan, drawings.mechanical · Owner: gc · Scope: package · Gate: roof_membrane · _07 50 00_
### constructability
- **[high] rf.penetrations** — Every penetration, curb and equipment support on the roof has a flashing detail, and penetrations are spaced from each other, from curbs and from walls far enough apart to be flashed without pitch pans.  
  Trace: drawings.roof_plan, drawings.details, drawings.mechanical, drawings.plumbing, drawings.electrical · Owner: gc · Scope: package · Gate: roof_membrane · _07 50 00_
- **[high] rf.deck-condition** — The roofing manufacturer's deck requirements (deck type and attachment, dryness of concrete decks, venting of insulating fill) are confirmed before insulation and membrane are set.  
  Trace: spec.part3, drawings.structural · Owner: gc · Scope: package · Gate: roof_membrane · _07 50 00_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[medium] d07.application-limits** — Application limits in the product data (substrate and ambient temperature, moisture, cure time, maximum weather or UV exposure before cover) are compared with the season and sequence in the schedule. Conflicts are raised before installation, not discovered during it.  
  Trace: schedule.master, spec.part3 · Owner: gc · Scope: package · _07_
- **[medium] rf.protection-after** — Protection of finished roofing from later trades (equipment setting, photovoltaics, lightning protection, work on walls above) is planned, with who repairs damage and how the manufacturer accepts the repairs.  
  Trace: spec.part1, schedule.master · Owner: gc · Scope: package · Gate: equipment_set · _07 50 00_
- **[medium] rf.temporary-roof** — If the roof will dry in the building early (temporary roofing, phased areas, permanent membrane used during construction), the spec's position and the manufacturer's warranty conditions for it are confirmed.  
  Trace: spec.part1 · Owner: gc · Scope: package · _07 50 00_
### absence
- **[critical (reflex)] rf.overflow** — Every roof area that can pond behind parapets or walls has secondary drainage: overflow drains or scuppers.  
  Trace: drawings.roof_plan, drawings.plumbing · Owner: design_team · Scope: package · _07 50 00_
- **[high (reflex)] d07.control-layer-continuity** — On each wall section and every transition detail (foundation, slab edge, openings, roof edge and parapet, penetrations, changes of material), trace the water, air, thermal and vapor layers across the transition. Any layer that stops without a detail showing how it joins the next is a finding, even when the submittal itself is correct.  
  Trace: drawings.wall_sections, drawings.details, drawings.roof_plan · Owner: design_team · Scope: package · Gate: procurement_release · _07_
- **[medium] rf.roof-vapor-retarder** — Where the space below is humid (pools, laundries, washdown dish rooms, wet-process plants, cold storage) or the design calls for one, a roof vapor retarder is shown and tied to the wall air and vapor layers.  
  Trace: drawings.wall_sections, drawings.details · Owner: design_team · Scope: package · _07 50 00_

## Reconciliations — documents that must agree (3)
- **[critical] rf.rc.overflow-elevation** — The overflow inlet elevation on the roofing and plumbing submittals matches the ponding depth the structural rain-load design assumed; tapered insulation, raised dams and high scuppers all add rain load.  
  Between: drawings.roof_plan ↔ drawings.plumbing ↔ drawings.structural · Key: Each overflow drain or scupper · Fields: overflow inlet elevation (dam or standpipe height, scupper invert), ponding depth assumed in the rain-load design · Owner: design_team · Gate: roof_membrane · _07 50 00_
- **[high] rf.rc.drains** — Each primary and overflow drain on the roof plan appears on the plumbing drawings at the same location and size, and overflow drains are piped or discharged independently of the primary system.  
  Between: drawings.roof_plan ↔ drawings.plumbing · Key: Drain or scupper location · Fields: count, location, size, primary or overflow, discharge route · Owner: design_team · Gate: roof_membrane · _07 50 00_
- **[high] rf.rc.rooftop-equipment** — Every rooftop unit, fan, vent, conduit and pipe penetration on the MEP roof plans appears on the architectural roof plan with a curb, support or flashing detail.  
  Between: drawings.roof_plan ↔ drawings.mechanical ↔ drawings.plumbing ↔ drawings.electrical · Key: Equipment tag or penetration · Fields: location, curb or support type, penetrations · Owner: design_team · Gate: roof_membrane · _07 50 00_

## Compliance — regulatory hooks (9)
- **[critical] edu.rh.storm-shelter** (`storm-shelter-requirements`) — Does the adopted building code require a storm shelter for this school (tornado design wind speed, occupant load), what capacity and location does it need, which ICC 500 edition governs, and what special inspection applies to the shelter?  
  **Unbound** → Run /construction:code-researcher with research topic "storm-shelter-requirements" (seed it with this hook's question)
- **[high] d07.rh.energy-envelope** (`energy-code-envelope`) — Which energy code and compliance path govern the envelope, what insulation, continuous insulation, roof reflectance and fenestration criteria apply in this climate zone, and do the submitted assemblies match the compliance documentation?  
  **Unbound** → Run /construction:code-researcher with research topic "energy-code-envelope" (seed it with this hook's question)
- **[high] rf.rh.wind-uplift** (`roof-wind-uplift-design`) — What wind design criteria govern the roof assembly (adopted code and load standard edition, risk category, exposure), and does the owner's insurer require a specific approval listing or rating?  
  **Unbound** → Run /construction:code-researcher with research topic "roof-wind-uplift-design" (seed it with this hook's question)
- **[high] rf.rh.secondary-drainage** (`roof-secondary-drainage`) — What do the adopted plumbing and building codes require for secondary roof drainage (sizing, separate piping, discharge location)?  
  **Unbound** → Run /construction:code-researcher with research topic "roof-secondary-drainage" (seed it with this hook's question)
- **[high] edu.rh.risk-category** (`building-risk-category-assignment`) — What risk category applies to this building under the adopted code (occupant load, designation as an emergency or community shelter), and which design loads, nonstructural anchorage and special inspections change because of it?  
  **Unbound** → Run /construction:code-researcher with research topic "building-risk-category-assignment" (seed it with this hook's question)
- **[medium] rf.rh.edge-securement** (`roof-edge-securement`) — Does the adopted code require tested edge securement for low-slope membrane roofs, and to which test standard?  
  **Unbound** → Run /construction:code-researcher with research topic "roof-edge-securement" (seed it with this hook's question)
- **[medium] rf.rh.fire-classification** (`roof-assembly-fire-classification`) — What roof assembly fire classification does the construction type and location require, and does the submitted assembly carry it?  
  **Unbound** → Run /construction:code-researcher with research topic "roof-assembly-fire-classification" (seed it with this hook's question)
- **[medium] rf.rh.reroofing** (`reroofing-recover-limits`) — Where this is reroofing, what limits does the code place on recovering versus tearing off, and what insulation upgrade does the energy code trigger?  
  **Unbound** → Run /construction:code-researcher with research topic "reroofing-recover-limits" (seed it with this hook's question)
- **[medium] rf.rh.rooftop-guards** (`rooftop-equipment-guards`) — Does the adopted code require guards or fall protection at roof hatches and at equipment near the roof edge?  
  **Unbound** → Run /construction:code-researcher with research topic "rooftop-equipment-guards" (seed it with this hook's question)

## Coordination routing (9)
- **[high] if.05-roof-deck-roofing** → Steel roof deck (05 31 00) · Gate: procurement_release — Deck gauge and fastening are fixed when the deck is ordered; the roofing approval often arrives later
  - Send them: Deck requirements of the roofing assembly's uplift approval and of any rated roof-ceiling design (gauge, fastening by roof zone), and drain sump locations
  - Need from them: Deck gauge, profile, finish and fastening as installed, and openings framed for drains, sumps, curbs and hatches
  - If missed: Roof deck gauge or fastening does not meet the roofing assembly's uplift approval
- **[high] if.rated-roof-assembly** → Fireproofing or rated ceiling of a listed roof-ceiling design (07 81 00, 09 50 00) · Gate: procurement_release
  - Send them: Insulation, cover board, membrane and attachment as submitted
  - Need from them: The listed roof-ceiling design and the limits it places on the roofing components above
  - If missed: Roofing components substituted outside the listed design; the roof-ceiling assembly loses its rating
- **[high] if.roof-drains** → Storm drainage (22 14 00) · Gate: roof_membrane
  - Send them: Finished-roof elevation at each drain, sump details and the membrane clamping method
  - Need from them: Primary and overflow drain bodies set at that elevation before the roofer reaches them
  - If missed: Drain bodies ordered without extensions for the tapered insulation at sumps, or without deck clamps for the deck
- **[high] if.roof-equipment-curbs** → Rooftop equipment, deck-opening framing, dunnage and wood nailers (23 74 00, 23 34 00, 05 12 00, 05 50 00, 06 10 53) · Gate: roof_membrane
  - Send them: Curb and support heights and flashing details compatible with the roof assembly
  - Need from them: Equipment curb dimensions and weights, framing at deck openings, dunnage, and the setting schedule
  - Confirm who: Equipment curbs and supports — typical furnish 23 74 00 or 07 72 00 / install 06 10 53 (GC carpentry) or 23 74 00
  - Confirm who: Flashing curbs and supports into the membrane — typical install 07 50 00
  - If missed: Curbs furnished by nobody, or set after the membrane and flashed in as patches
- **[high] if.roof-edge-nailers** → Rough carpentry (06 10 53) · Gate: roof_membrane
  - Send them: Nailer size, height and fastening that the edge system and its test require
  - Need from them: Nailers installed and fastened to that design before edge metal and copings
  - If missed: Edge metal fastened to undersized or under-fastened nailers; roof edge lifts in high wind
- **[high] if.roof-skylights** → Unit and metal-framed skylights (08 62 00, 08 63 00) · Gate: roof_membrane
  - Send them: Roof assembly thickness at each skylight, base flashing height the roof manufacturer's warranty requires, and the air and vapor barrier to connect to
  - Need from them: Curb type (integral or site-built) and height above the finished roof, frame perimeter seal, counterflashing, and fall-protection screens where provided
  - Confirm who: Skylight curb — typical furnish 08 62 00, 08 63 00 or 06 10 53 / install 08 62 00, 08 63 00 or 06 10 53
  - Confirm who: Air seal from skylight frame to the roof air or vapor barrier — typical install 07 50 00 or 08 62 00
  - If missed: Curb too low for the warranted base flashing once insulation and cover board are in, or no air seal at the frame; leaks and condensation at the skylight perimeter
- **[high] if.roof-wall-air-barrier** → Air barrier (07 27 00) · Gate: roof_membrane — Base flashing and coping cover this transition before the wall cladding does
  - Send them: Roof membrane or roof vapor retarder carried to the wall and up the parapet, with the transition product
  - Need from them: Wall air barrier carried up to meet it, and deck flutes sealed where the wall line crosses the deck
  - Confirm who: Air-barrier connection at the roof-to-wall transition — typical install 07 27 00 or 07 50 00
  - If missed: Air leakage path at the roof edge that neither trade carried
- **[medium] if.roof-attachments-lp-pv** → Lightning protection and photovoltaics (26 41 00, 48 14 00) · Gate: equipment_set
  - Send them: Manufacturer-accepted attachment and penetration details, and protection requirements
  - Need from them: Attachment locations, ballast or anchorage, conduit routing and the installation schedule
  - If missed: Air terminals and conductors fastened through the finished membrane without the roofing manufacturer's details
- **[medium] if.roof-device-mounts** → Radio coverage antennas, cameras and other rooftop low-voltage devices (27 53 19, 28 20 00, 27 10 00) · Gate: roof_membrane — Donor antenna locations come from the radio coverage survey, often after the roof is on; ask for them before the membrane goes down
  - Send them: Manufacturer-accepted support and penetration details (pipe supports, curbs, pitch-pan or boot penetrations) and the roofer's schedule
  - Need from them: Device and mast locations, mount type and wind and ice loading basis, cable entry points, and grounding or bonding needs
  - Confirm who: Supports and penetrations for rooftop antennas and cameras — typical furnish 07 50 00, 27 53 19 or 28 20 00 / install 07 50 00
  - If missed: Masts and cameras clamped to parapets or fastened through the finished membrane by the low-voltage installer; leaks, and a roof warranty exclusion

## Failure modes to watch (16)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d07.fm.orphan-transition** — Two trades each install their own layer and neither makes the connection between them → Leak or air path at the transition, found after cladding or backfill has covered it (caught by d07.transition-ownership, d07.control-layer-continuity; industry_practice)
- **d07.fm.substitution-voids-warranty** — A substituted component (insulation, cover board, sealant, flashing tape) is not accepted under the specified system warranty → Manufacturer declines the system warranty at closeout; remove-and-replace or an owner claim (caught by d07.warranty-conditions; industry_practice)
- **d07.fm.exposure-exceeded** — Membrane or barrier left exposed past the manufacturer's limit while cladding or overburden is delayed → Degraded membrane and a warranty exclusion; rework under schedule pressure (caught by d07.application-limits; industry_practice)
- **d07.fm.incompatible-products** — Sealant, tape or primer from one manufacturer applied to another's membrane without confirmation → Adhesion loss or chemical attack at the joint; leaks at transitions (caught by d07.system-compatibility; industry_practice)
- **rf.fm.drains-not-set** — Drain bodies are not set when the roofer reaches the drains → Roofing stops at the drains, or drains are cut in later through finished roofing (caught by if.roof-drains, rf.rc.drains; industry_practice)
- **rf.fm.no-overflow** — Parapet roof built with no secondary drainage, or with overflow tied into the primary leader → Ponding beyond the structural design load when the primary drains clog (caught by rf.overflow, rf.rc.drains, rf.rc.overflow-elevation; industry_practice)
- **rf.fm.wet-deck** — Membrane adhered over a concrete deck that had not dried to the manufacturer's criteria → Adhesive failure, blistering and condensation inside the assembly (caught by rf.deck-condition; industry_practice)
- **rf.fm.trade-damage** — Other trades set equipment, run conduit or stage material on finished membrane → Punctures that show up as leaks months later, and a dispute over who pays (caught by rf.protection-after; industry_practice)
- **rf.fm.listing-mismatch** — Wind uplift approval submitted for a different assembly than the one installed → Roof does not meet design pressures or the insurer's requirement; possible removal (caught by rf.attachment-zones; industry_practice)
- **rf.fm.unflashable-penetrations** — Pipe and conduit penetrations clustered too close together or tight to curbs → Sealant-dependent pitch pans that leak and fall outside the warranty (caught by rf.penetrations, rf.rc.rooftop-equipment; industry_practice)
- **edu.fm.default-risk-category** — Delegated cladding, joist or anchorage design done to the default risk category on a school assigned a higher one → Components under-designed; recalculation and field reinforcement after installation (caught by edu.risk-category-delegated; industry_practice)
- **edu.fm.shelter-assembly-broken** — Shelter doors, frames, hardware or louvers submitted as standard products, or tested components mixed across manufacturers → The shelter boundary no longer matches a tested assembly; doors, frames or louvers replaced before occupancy (caught by edu.storm-shelter; industry_practice)

## Expected submittal contents
- **Product Data**
  - Every component of the assembly — vapor retarder, insulation, cover board, membrane, adhesives, fasteners, flashings, edge metal
- **Shop Drawings**
  - Tapered insulation layout with crickets and saddles to every drain and scupper
  - Attachment or adhesive pattern by roof zone (field, perimeter, corner)
  - Details for every penetration, curb, drain, edge, expansion joint and wall transition
- **Design Data**
  - Wind uplift calculation or approval listing for the exact assembly submitted

## Extract for reconciliation
- rf.xf.assembly — Roof assembly components, top to bottom (list, per package) → spec.part2
- rf.xf.drains — Drains and scuppers (location, size, primary or overflow) (list, per package) → drawings.roof_plan, drawings.plumbing
- rf.xf.warranty — Warranty type and term offered (string, per package) → spec.part1

## Standards to verify against
- ANSI/SPRI/FM 4435/ES-1: Test Standard for Edge Systems Used with Low Slope Roofing Systems
- FM 4470: FM Approvals standard for Class 1 roof assemblies (single-ply, modified bitumen, built-up, liquid-applied)

## Warnings
- No profile for 07 54 00; compiled from ancestors only
- Draft knowledge in use (global, 07, 07 50 00) — not yet PE-reviewed
