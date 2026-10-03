# Compiled knowledge — 11 40 00 Foodservice Equipment

Facility types: education.k12, foodservice · Confidence floor: **draft** · Review mode: per_element · Contractor-designed: sometimes
Lineage: global → 11 → 11 40 00
Overlays: education, education.k12, foodservice
Legacy scope file: reference/pe_expertise/scope-11-equipment.md

> Knowledge, not requirements: each check names where to look (trace_to). The project documents govern; surface conflicts, never resolve them silently.

## Scope
Commercial kitchen and serving equipment, custom stainless fabrication, hoods and their suppression, and walk-ins (11 41 00 inherits from here). Submittals run to hundreds of item numbers, each with its own power, water, waste, gas and exhaust data, and the building trades rough in from the consultant's rough-in plans long before the equipment contractor's approved data exists. The expensive misses are rough-ins built to symbols, floor sinks in the wrong place, hoods and suppression that no longer match the appliance line, and make-up air that was never revised.

## Review checks (30)
### completeness
- **[high] g.delegated-design** — Delegated design carries the required professional seal and is routed for Engineer of Record review.  
  Trace: spec.part1_submittals · Owner: subcontractor · Scope: package · Types: Delegated Design, Design Data · _global_
- **[high] g.contractor-designed** — This scope is often performance-specified and designed or selected by the contractor. Confirm the spec's design criteria are complete enough to design to; whether the AHJ treats the design as a deferred submittal and when it must be filed relative to installation; and that the designer's assumptions about support, attachment and adjacent work are confirmed by the trades that provide them.  
  Trace: spec.part1, spec.part2 · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] 11fs.walk-ins-included** — Walk-in coolers and freezers carried in this section are also reviewed against the storage equipment profile (11 41 00): floor type and slab depression, freezer underfloor heat, condensate, door heaters, refrigeration route and sprinklers inside the box, all of which are settled before the slab pour, not at the walk-in delivery.  
  Trace: schedule.foodservice_equipment, drawings.foodservice · Owner: gc · Scope: package · Gate: slab_pour · _11 40 00_
- **[high] 11fs.rough-in-drawings** — The equipment contractor's rough-in plans cover every item that needs a connection, are based on the approved models rather than the bid-stage consultant plans, and are issued to the plumbing and electrical trades before underslab rough-in. If they arrive after the slab is poured, list the floor connections already set and check each one against them.  
  Trace: drawings.foodservice, drawings.plumbing, drawings.electrical · Owner: gc · Scope: package · Types: Shop Drawings · Gate: underslab_rough_in · _11 40 00_
- **[high] edu.agency-approvals** — Where a state school-construction agency has jurisdiction, deferred submittals, substitutions and field changes that touch structure, fire and life safety or accessibility are approved by that agency before fabrication, not only by the architect, and the agency's inspector and testing requirements are in the inspection program.  
  Trace: spec.division_01, register.special_inspections, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[high] food.plan-review** — The health department's plan approval is in hand and its conditions are carried into the submittals. Any equipment, sink or finish change made after approval (substitution, relocation, owner reselection) is checked against the approved plans and resubmitted where the health department requires it, before the item is ordered.  
  Trace: drawings.foodservice, register.substitutions, spec.division_01 · Owner: gc · Scope: package · Gate: procurement_release · _overlay:foodservice_
- **[medium] g.products-marked** — Cut sheets covering a product family have the proposed model, size, options, finish and accessories clearly marked; unmarked sheets are returned.  
  Trace: spec.part2 · Owner: subcontractor · Scope: package · Types: Product Data · _global_
### conformance
- **[critical] 11fs.hood-suppression** — Suppression for each grease hood covers every appliance in the final line-up plus the plenum and duct; on discharge it shuts off fuel and power to all appliances under the hood with manual reset, its manual release sits on the egress path, and it signals the fire alarm system. Appliances on casters have restraints and quick-disconnect gas connectors so they go back to their protected positions.  
  Trace: drawings.foodservice, drawings.fire_protection, drawings.fire_alarm · Owner: subcontractor · Scope: element · Gate: procurement_release · _11 40 00_
- **[high] g.current-documents** — The submittal reflects the current contract documents, including addenda, ASIs, bulletins and responded RFIs, not the bid set. Note the drawing revision the submitter worked from.  
  Trace: drawings.revision_blocks, register.asi_bulletin_log, register.rfi_log · Owner: gc · Scope: package · _global_
- **[high] g.basis-of-design** — Proposed manufacturer and model match the basis of design or a listed acceptable manufacturer. Anything else follows the comparable-product or substitution procedure Division 01 allows, with its timing and comparison data, before it is reviewed on its merits.  
  Trace: spec.part2_manufacturers, register.substitutions · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[high] g.deviations-identified** — Every deviation from the contract documents is clouded or listed by the submitter. Compare independently; do not rely on the submitter's list.  
  Trace: spec.part2, drawings.details · Owner: subcontractor · Scope: package · _global_
- **[high] d11.item-utilities** — For each item, the submitted model's utility data (voltage, phase, load, cord-and-plug configuration or hardwired connection, water sizes and temperatures, direct or indirect waste, gas input and pressure, steam, exhaust or venting) matches the equipment schedule and the MEP drawings at that item's location. Read the manufacturer's nameplate data on the cut sheet, not a schedule copied into the submittal.  
  Trace: schedule.foodservice_equipment, drawings.foodservice, drawings.electrical, drawings.plumbing, drawings.mechanical · Owner: subcontractor · Scope: element · Gate: in_wall_rough_in · _11_
- **[high] 11fs.indirect-waste** — Every item that must waste indirectly has a receptor with the required air gap or air break: a floor sink or receptor located where the item's outlet actually lands, reachable for cleaning, not under a walk-in or fixed equipment base, and with a grate suited to the discharge.  
  Trace: drawings.plumbing, drawings.foodservice · Owner: design_team · Scope: element · Gate: slab_pour · _11 40 00_
- **[high] 11fs.hood-airflow** — Each hood section's listing, overhang past the appliances below, exhaust and supply airflow, static pressure, and duct collar size and location match the mechanical schedule and drawings, and the appliance line under it is the one the airflow was selected for. Moving a heavier-duty appliance under a hood section changes its airflow.  
  Trace: schedule.foodservice_equipment, schedule.mechanical_equipment, drawings.mechanical · Owner: subcontractor · Scope: element · Types: Shop Drawings, Product Data · Gate: procurement_release · _11 40 00_
- **[high] 11fs.gas-connections** — Gas items show input rating, connection size and required inlet pressure; movable items use listed flexible connectors with restraint cables; and the valve the suppression system closes is upstream of every appliance under that hood, with reset accessible.  
  Trace: drawings.plumbing, drawings.mechanical, drawings.foodservice · Owner: subcontractor · Scope: element · _11 40 00_
- **[medium] d11.service-clearance** — Manufacturer service and code clearances around each item (coil and filter access, door swings, access to controls and disconnects, clearance to combustibles for fuel-fired and cooking equipment) fit the space shown on the plans with adjacent equipment in place.  
  Trace: drawings.enlarged_plans, drawings.plans · Owner: design_team · Scope: package · _11_
- **[medium] 11fs.custom-fabrication** — Custom fabrications show integral sinks and drainboards, faucet and drain locations, cutouts sized to the approved drop-in and undercounter models, utility chases, edges and wall attachment, in the material gauge and construction the spec requires. A drop-in substituted after approval needs its cutout re-checked before fabrication.  
  Trace: drawings.foodservice, spec.part2 · Owner: subcontractor · Scope: element · Types: Shop Drawings · Gate: procurement_release · _11 40 00_
### coordination
- **[high] g.by-others-mapped** — Every "by others", "NIC", "furnished by owner" or "by GC" note is mapped to a specific responsible party in the contract documents or a subcontract. An unmapped "by others" is a scope gap.  
  Trace: spec.part1, drawings.details · Owner: gc · Scope: package · _global_
- **[high] d11.furnished-by** — Each item is designated owner- or contractor-furnished, and for every owner-furnished item the contract names who receives, unloads, stores, sets, assembles, connects and starts it up, and the date the owner's vendor must deliver final rough-in data. An OFCI note on the schedule with no responsibility matrix behind it is a scope gap.  
  Trace: spec.division_01, spec.part1, schedule.equipment · Owner: gc · Scope: package · Gate: procurement_release · _11_
- **[high] d11.substitution-cascade** — A change of make, model, size or fuel from the basis of design is checked against every trade it touches (power, water and waste, gas, exhaust and make-up air, fire suppression, structure, casework cutouts) before approval, and the revised data is issued to those trades in writing rather than left inside the equipment submittal.  
  Trace: register.substitutions, schedule.equipment · Owner: gc · Scope: package · Gate: procurement_release · _11_
- **[high] d11.structural-support** — Weight, operating and dynamic loads, and anchorage of heavy, suspended, wall-hung or vibrating items are on the submittal and match what the structural design assumed: floor loads on elevated slabs, housekeeping pads, support framing for ceiling-hung items, in-wall backing, and vibration isolation. Loads on delegated-design joists have to reach the joist supplier before joists are designed.  
  Trace: drawings.structural, drawings.details, schedule.equipment · Owner: design_team · Scope: package · Gate: procurement_release · _11_
- **[high] 11fs.grease-waste** — Grease-laden fixtures and equipment (pot and prep sinks, floor drains and troughs at the cooking line, kettles, tilt skillets, dish areas) route to the grease interceptor or grease removal devices, and the interceptor was sized from the final fixture and equipment list rather than a preliminary one.  
  Trace: drawings.plumbing, drawings.civil, schedule.foodservice_equipment · Owner: design_team · Scope: package · Gate: underslab_rough_in · _11 40 00_
- **[high] food.hand-sinks** — Hand sinks sit in or next to each food preparation, dispensing and warewashing area as the health department requires, are not blocked by equipment, carts or a door swing, and are separate from prep and utility sinks. Whether each hand sink is a plumbing fixture or part of a custom fabrication is settled, and tempered water, splash guards beside prep surfaces, and soap and towel dispensers are each assigned to a trade or to the owner.  
  Trace: drawings.foodservice, drawings.plumbing, schedule.plumbing_fixture · Owner: gc · Scope: element · _overlay:foodservice_
### constructability
- **[high] d11.approved-model-rough-in** — Rough-ins are built from the approved unit's installation drawings (or the owner vendor's final data), not from basis-of-design cut sheets or the symbols on the MEP plans. Items whose approval or owner purchase decision lags the rough-in schedule are listed with the date their data is needed.  
  Trace: register.submittal_log, schedule.master, drawings.equipment · Owner: gc · Scope: package · Gate: underslab_rough_in · _11_
- **[high] edu.summer-window** — Where work in existing schools must fit a break in the academic calendar, each submittal's approval, owner selections, mock-ups and delivery are dated against the day the window opens, not against a floating schedule activity. Long-lead items (door frames and hardware, HVAC equipment, switchgear, casework, flooring) that miss the window push work into occupied classrooms or a year later, so their submittals are released first.  
  Trace: schedule.master, spec.division_01 · Owner: gc · Scope: package · Gate: procurement_release · _overlay:education_
- **[medium] g.field-verify** — Dimensions marked "verify in field" are listed with who verifies them and the milestone they depend on, before fabrication release.  
  Trace: schedule.master · Owner: gc · Scope: package · Types: Shop Drawings · Gate: procurement_release · _global_
- **[medium] g.lead-time** — Stated lead time supports the schedule activity that needs the product, counting review and resubmittal cycles.  
  Trace: schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _global_
- **[medium] d11.delivery-path** — Each large item has a route from the delivery point to its room (door and corridor widths, elevator or hoist capacity, floor capacity along the path) or an opening left until it is set. Items that only fit before walls, roof or envelope close are ordered to arrive then.  
  Trace: drawings.plans, schedule.master · Owner: gc · Scope: package · Gate: procurement_release · _11_
### absence
- **[high] food.required-sinks** — The other sinks the health department requires are on the drawings and assigned to the plumbing or foodservice scope: a warewashing sink with the compartments and drainboards it requires, large enough for the biggest utensil; a separate food preparation sink where produce washing or thawing calls for one; and a service sink or curbed cleaning facility for mop water.  
  Trace: drawings.foodservice, drawings.plumbing, schedule.plumbing_fixture · Owner: design_team · Scope: element · _overlay:foodservice_
- **[medium] 11fs.type-ii-exhaust** — Dish machines, steamers, combination ovens and other heat- or vapor-producing items that the code or manufacturer requires to be exhausted have a Type II hood or a direct duct connection on the mechanical drawings, sized from the approved unit's vent data.  
  Trace: drawings.mechanical, schedule.foodservice_equipment · Owner: design_team · Scope: element · _11 40 00_

## Reconciliations — documents that must agree (5)
- **[high] d11.rc.electrical** — Every item with an electrical connection appears on the electrical plans at its location with a circuit of matching voltage, phase and capacity, the matching receptacle configuration or a hardwired connection, and its disconnect; items the owner needs on standby power are on that branch.  
  Between: schedule.foodservice_equipment ↔ schedule.electrical_panel ↔ drawings.electrical · Key: Equipment item number · Fields: voltage, phase, load (amps or kW), receptacle configuration or hardwired, disconnect, circuit, standby branch, shut off by hood suppression · Owner: design_team · Gate: in_wall_rough_in · _11_
- **[high] d11.rc.plumbing-mechanical** — Every item with a water, waste, gas, steam or exhaust connection has that connection on the plumbing and mechanical drawings at the item's location, with matching sizes and an indirect-waste receptor wherever the item discharges indirectly.  
  Between: schedule.foodservice_equipment ↔ drawings.plumbing ↔ drawings.mechanical · Key: Equipment item number · Fields: cold, hot or filtered water and size, water temperature, waste size, direct or indirect waste, grease or non-grease waste, receptor location, gas input and pressure, steam and condensate, backflow protection · Owner: design_team · Gate: underslab_rough_in · _11_
- **[high] 11fs.rc.rough-in-locations** — Each connection on the foodservice rough-in plans appears on the plumbing and electrical plans at the same location and height. MEP plans that show only a generic symbol at the item, rather than the dimensioned point, are flagged so the trades rough in from the foodservice plans.  
  Between: drawings.foodservice ↔ drawings.plumbing ↔ drawings.electrical · Key: Connection point by item number · Fields: location, height above floor, wall or floor, floor sink or trench position, receptacle or junction box · Owner: design_team · Gate: underslab_rough_in · _11 40 00_
- **[high] 11fs.rc.hood-exhaust** — Each hood's exhaust and make-up airflow matches the exhaust fan and make-up air unit that serve it, the fan's static pressure covers the hood and its duct, and total make-up air keeps the kitchen at the pressure the design intends relative to the dining and corridor areas.  
  Between: schedule.foodservice_equipment ↔ schedule.mechanical_equipment ↔ drawings.mechanical · Key: Hood tag and the fans serving it · Fields: exhaust airflow, make-up or supply airflow, static pressure, exhaust fan served by, make-up air unit served by, duct collar size and count, fan interlock · Owner: design_team · Gate: procurement_release · _11 40 00_
- **[medium] 11fs.rc.gas-load** — The total input of the final gas line-up stays within what the gas piping, regulators and utility service were sized for; higher-input substitutions are traced back to the meter.  
  Between: schedule.foodservice_equipment ↔ drawings.plumbing ↔ drawings.mechanical · Key: Gas appliance, and the gas service that feeds the kitchen · Fields: input rating per appliance, connection size, inlet pressure, total connected load, service pressure and meter · Owner: design_team · Gate: procurement_release · _11 40 00_

## Compliance — regulatory hooks (12)
- **[critical] 11fs.rh.hood-suppression** (`commercial-kitchen-hood-suppression`) — What does the adopted fire code require of the cooking-line suppression system (listing standard, fuel and power shutoff, manual release location, fire alarm connection, portable extinguisher type), and which acceptance test does the fire marshal witness?  
  **Unbound** → Run /construction:code-researcher with research topic "commercial-kitchen-hood-suppression" (seed it with this hook's question)
- **[high] 11fs.rh.hood-type** (`commercial-kitchen-hood-requirements`) — Which appliances in the final line-up require a Type I hood, a Type II hood or no hood under the adopted mechanical code, and how does the AHJ treat listed recirculating or ventless appliances?  
  **Unbound** → Run /construction:code-researcher with research topic "commercial-kitchen-hood-requirements" (seed it with this hook's question)
- **[high] 11fs.rh.grease-interceptor** (`grease-interceptor-sizing`) — How do the adopted plumbing code and the local sewer authority size and locate grease interceptors and grease removal devices, which fixtures must or must not discharge to them (dish machines, food waste disposers), and is a pretreatment permit required?  
  **Unbound** → Run /construction:code-researcher with research topic "grease-interceptor-sizing" (seed it with this hook's question)
- **[high] 11fs.rh.indirect-waste** (`foodservice-indirect-waste`) — Which foodservice items must discharge through an indirect waste with an air gap or air break under the adopted plumbing and food codes?  
  **Unbound** → Run /construction:code-researcher with research topic "foodservice-indirect-waste" (seed it with this hook's question)
- **[high] 11fs.rh.equipment-certification** (`food-equipment-certification`) — Does the adopted food code or health authority require food equipment to be certified to the applicable NSF/ANSI standard or an equivalent, and must the equipment plan be approved before fabrication or installation?  
  **Unbound** → Run /construction:code-researcher with research topic "food-equipment-certification" (seed it with this hook's question)
- **[high] edu.rh.school-agency-review** (`school-construction-agency-review`) — Does a state agency other than the local building department review plans, approve changes or inspect construction for this school (common for public K-12 and in some states for community colleges), and what does it require for deferred submittals, change documents, testing laboratories and the inspector of record?  
  **Unbound** → Run /construction:code-researcher with research topic "school-construction-agency-review" (seed it with this hook's question)
- **[high] food.rh.plan-review** (`foodservice-plan-review`) — Does the health department require plan review and approval of the kitchen before construction, resubmittal of later changes, and a pre-opening inspection and permit to operate separate from the certificate of occupancy; which Food Code edition has the state adopted?  
  **Unbound** → Run /construction:code-researcher with research topic "foodservice-plan-review" (seed it with this hook's question)
- **[high] food.rh.hand-sinks** (`foodservice-handwashing-sinks`) — How many hand sinks are required and where (preparation, dispensing, warewashing, bars, toilet rooms), at what minimum water temperature, and with what splash guards, dispensers and signage?  
  **Unbound** → Run /construction:code-researcher with research topic "foodservice-handwashing-sinks" (seed it with this hook's question)
- **[high] food.rh.required-sinks** (`foodservice-required-sinks`) — Besides hand sinks, which sinks does the adopted Food Code and health department require (warewashing compartments and drainboards, food preparation sinks, service sinks or curbed cleaning facilities), and how are they sized?  
  **Unbound** → Run /construction:code-researcher with research topic "foodservice-required-sinks" (seed it with this hook's question)
- **[medium] d11.rh.seismic-anchorage** (`seismic-nonstructural-anchorage`) — Does the seismic design category require engineered anchorage or bracing for floor-, wall- and ceiling-mounted equipment, who designs it, and is special inspection of the anchorage required?  
  **Unbound** → Run /construction:code-researcher with research topic "seismic-nonstructural-anchorage" (seed it with this hook's question)
- **[medium] 11fs.rh.makeup-air** (`kitchen-exhaust-makeup-air`) — What make-up air, interlock and pressure relationship does the adopted mechanical code require for kitchen exhaust, and above what exhaust rate does the energy code require demand control, transfer air or heat recovery?  
  **Unbound** → Run /construction:code-researcher with research topic "kitchen-exhaust-makeup-air" (seed it with this hook's question)
- **[medium] 11fs.rh.accessible-service** (`accessibility-work-surfaces`) — Do self-service lines, tray slides, condiment and beverage dispensers and service counters meet the adopted accessibility standard for height, reach range and clear floor space?  
  **Unbound** → Run /construction:code-researcher with research topic "accessibility-work-surfaces" (seed it with this hook's question)

## Coordination routing (10)
- **[critical] if.11-hood-suppression** → Wet-chemical fire-extinguishing systems (21 23 00) · Gate: procurement_release — Design the system from the approved appliance line-up, and redo it if the line-up changes
  - Send them: Final appliance line-up under each hood (type, position, fuel), hood plenum and duct collar locations
  - Need from them: Listed system design with nozzle coverage of every appliance, plenum and duct; fuel and power shutoff interlocks; manual release location
  - Confirm who: Hood fire suppression system — typical furnish 11 40 00, 23 38 13 or 21 23 00 / install 11 40 00, 23 38 13 or 21 23 00
  - Confirm who: Gas shutoff valve closed by the suppression system — typical furnish 11 40 00 or 21 23 00 / install 23 11 23
  - Confirm who: Shutoff of electric appliances under the hood on discharge (shunt trip or contactor) — typical furnish 26 28 16 / install Division 26 / connect 21 23 00
  - If missed: Grease hood installed without a listed suppression system, or with one designed for an earlier appliance line-up
- **[high] if.03-cold-storage-floors** → Slabs on ground and depressed slabs (03 30 00) · Gate: slab_pour
  - Send them: Floor type and assembly depth from the approved box, the underfloor heat layout (cable in conduit or glycol piping) with power, control and monitoring, and floor drain locations
  - Need from them: The floor the approved box needs, settled before forming (a depression for insulated floor panels, or an insulated slab with the vapor retarder on the warm side and underfloor heat below it), finished flush at the door
  - Confirm who: Underfloor heat under freezers on grade — typical furnish 11 41 00 or 13 21 26 / install the electrical or refrigeration trade
  - Confirm who: Insulation and vapor retarder within an insulated slab — typical furnish 11 41 00, 13 21 26 or 03 30 00 / install 03 30 00
  - If missed: Freezer built on grade without underfloor heat, or with heating cable never energized or monitored; Slab poured flat where the walk-in needed a depression, or depressed for a different floor assembly
- **[high] if.03-housekeeping-pads** → Cast-in-place concrete (03 30 00) · Gate: slab_pour — Dowels go in with the slab; the pad waits for the approved equipment submittal
  - Send them: Approved footprint, weight, anchor pattern and anchorage design, pad height for traps and drains, and pad locations checked against service clearances, before the pad pour
  - Need from them: Pads formed and doweled to the slab to the approved equipment dimensions, with the anchor embedment and edge distance the anchorage needs
  - Confirm who: Pad dimensions and locations — typical furnish the equipment's trade / install 03 30 00
  - Confirm who: Equipment anchors into pads — typical furnish the equipment's trade / install the equipment's trade or 03 30 00
  - If missed: Pads formed from the scheduled equipment before the equipment submittal was approved; Conduit stub-ups cast from the design drawings, then another manufacturer's switchboard is approved
- **[high] if.11-equipment-power** → Electrical equipment connections, panelboard circuits, receptacles and disconnects (26 05 83, 26 24 00, 26 27 26, 26 28 16) · Gate: in_wall_rough_in
  - Send them: Nameplate electrical data per item, plug configuration or hardwired connection point, integral disconnects, and the control wiring diagram between remote components of an item
  - Need from them: Circuits, receptacles and disconnects matching each approved item, final connections, and the standby branch for items the owner designates
  - Confirm who: Final electrical connection to hardwired equipment — typical connect 26 05 83
  - Confirm who: Disconnect switches at equipment — typical furnish 26 28 16 or integral to the equipment / install Division 26
  - Confirm who: Control wiring between remote components of one item (condensing unit to evaporator, hood panel to fans, controller to motorized equipment) — typical furnish Division 11 / install Division 11 or Division 26
  - If missed: Control wiring between components of one item claimed by neither the equipment vendor nor the electrician; equipment cannot start at turnover
- **[high] if.11-hood-fire-alarm** → Fire detection and alarm (28 46 00) · Gate: above_ceiling_close_in
  - Send them: Suppression system alarm and supervisory contacts, and the fans, make-up air and appliances that must respond on discharge
  - Need from them: Monitoring of the suppression system and control relays for the shutdowns the design requires
  - Inspect before: Hood suppression acceptance test witnessed by the fire authority
  - Confirm who: Wiring from the suppression control head to the fire alarm system — typical install 28 46 00 / connect 28 46 00
- **[high] if.11-foodservice-plumbing** → Plumbing (water, sanitary and grease waste, water heaters) (22 11 00, 22 13 00, 22 33 00) · Gate: underslab_rough_in
  - Send them: Rough-in plans by item number with connection sizes, heights and indirect-waste outlets; faucets and fittings on fabricated sinks
  - Need from them: Rough-in to the dimensioned points, floor sinks and trench drains at the approved locations, grease interceptor, and final connections
  - Confirm who: Indirect waste piping from equipment outlets to floor sinks — typical install 11 40 00 or 22 13 00
  - Confirm who: Faucets, pre-rinse units and drain fittings on fabricated sinks — typical furnish 11 40 00 / install 11 40 00 / connect 22 11 00
  - Confirm who: Booster heater for high-temperature dish machines — typical furnish 11 40 00 or 22 33 00 / install 11 40 00 or 22 33 00 / connect 22 11 00 and Division 26
  - Confirm who: Backflow preventers and filters for beverage, ice and chemical dispensers — typical furnish 11 40 00 or 22 11 00 / install 22 11 00
- **[high] if.11-foodservice-gas-exhaust** → Gas piping, kitchen hoods, grease and exhaust duct, exhaust fans and make-up air units (23 11 23, 23 38 13, 23 31 00, 23 34 00, 23 74 00) · Gate: procurement_release
  - Send them: Gas input, connection size and pressure per appliance; hood airflow, static pressure and collar locations; hood control panel functions
  - Need from them: Gas piping and shutoff valve to each appliance; grease and exhaust duct to the hood collars; fans and make-up air sized to the approved hoods, with interlocks
  - Confirm who: Kitchen hoods — typical furnish 11 40 00 or 23 38 13 / install 11 40 00 or 23 38 13
  - Confirm who: Final gas connection to each appliance (flexible connector, restraint, quick-disconnect) — typical furnish 11 40 00 / install 23 11 23
  - Confirm who: Hood control panel and its interlock wiring to fans and make-up air — typical furnish 11 40 00 / install Division 26 / connect 23 09 00 or Division 26
  - If missed: Hoods bought twice or not at all because both the equipment and mechanical sections specify them
- **[high] if.11-walk-in-sprinklers** → Fire-suppression sprinkler systems (21 13 00) · Gate: above_ceiling_close_in
  - Send them: Box dimensions, ceiling panel construction, which boxes are freezers, and penetration details
  - Need from them: Heads inside each box where required (dry type in freezers) and above the box, located before panels are cut
  - Confirm who: Sealing sprinkler penetrations through walk-in panels — typical install 11 41 00 or 21 13 00
  - If missed: Sprinklers omitted inside the box, or standard wet heads used inside a freezer
- **[high] if.11-walk-in-refrigeration** → Refrigerant piping and condensing units (23 23 00, 23 62 00) · Gate: procurement_release — Settle who designs and furnishes the refrigeration before either is bought; line routes and penetrations before overhead rough-in
  - Send them: Refrigeration selection and loads, evaporator and controller locations, line sizes and route limits, panel penetrations for the lines, electrical data and control diagram
  - Need from them: Condensing unit location and support, refrigerant piping, charging and start-up, and roof or wall penetrations, where the refrigeration is not in the box or room vendor's scope
  - Confirm who: Refrigeration system design and equipment (condensing units, evaporators, controls) — typical furnish 11 41 00, 13 21 26 or 23 62 00 / install 11 41 00, 13 21 26 or 23 62 00
  - Confirm who: Refrigerant piping between condensing unit and evaporator, charge and start-up — typical install 11 41 00, 13 21 26 or 23 23 00
  - If missed: Condensing unit location and refrigerant line route left to be worked out in the field; Piping and control wiring between condensing unit and evaporators falls between the room vendor, the refrigeration contractor and the electrician
- **[medium] if.09-finishes-equipment-casework** → Flooring, tile and painting (09 60 00, 09 30 00, 09 90 00) · Gate: floor_finish_install
  - Send them: Fixed or movable status, footprints, setting sequence relative to flooring, floor anchoring, and the sealing to wall and floor that cleanability or health rules require
  - Need from them: Whether floor and wall finishes run under and behind each fixed item or stop at it, and the base and sealing at that edge
  - Confirm who: Finish under and behind fixed equipment and casework — typical install 09 60 00, 09 30 00 or 09 90 00 before the item is set, or excluded by the finish schedule
  - If missed: Equipment set on bare slab with no finish under it, or flooring run under items that must be sealed to the slab; edges rejected as uncleanable

## Failure modes to watch (23)
- **g.fm.superseded-revision** — Shop drawings prepared from the bid set; later ASIs and RFI responses never incorporated → Fabrication to a superseded design; rework or field modification (caught by g.current-documents; industry_practice)
- **g.fm.unmarked-cut-sheet** — Product data for a whole product family approved with nothing marked → Wrong model, voltage or finish ordered; approval stamp can't settle the dispute (caught by g.products-marked; industry_practice)
- **g.fm.silent-deviation** — Sub changes a material or dimension without clouding it → Approval stamp argued as acceptance of the change (caught by g.deviations-identified; industry_practice)
- **g.fm.by-others-gap** — Submittal notes an item "by others" that no other contract includes → Scope gap discovered at install; change order (caught by g.by-others-mapped; industry_practice)
- **d11.fm.substitution-cascade** — An item is substituted or changes fuel or size after MEP rough-in, and only the equipment submittal is revised → Wrong circuits, receptacles, gas sizing, waste and exhaust connections found at setting; rework across several trades (caught by d11.substitution-cascade, d11.rc.electrical, d11.rc.plumbing-mechanical; industry_practice)
- **d11.fm.owner-data-late** — Owner-furnished items are bought late and the vendor's rough-in data arrives after slabs and walls close → Cored slabs, opened walls and change orders charged against the owner's own late decision (caught by d11.furnished-by, d11.approved-model-rough-in; industry_practice)
- **d11.fm.nameplate-mismatch** — Receptacle configuration, voltage or phase on the electrical drawings differs from the delivered unit's plug or nameplate → Equipment cannot be connected at turnover; receptacles, breakers and sometimes feeders changed in the field (caught by d11.rc.electrical; industry_practice)
- **d11.fm.no-path-in** — Large equipment arrives after the envelope and interior openings are finished and does not fit through them → Finished openings demolished, crane picks, or disassembly and reassembly at extra cost (caught by d11.delivery-path; industry_practice)
- **d11.fm.unsupported-load** — Heavy or suspended equipment placed on a slab or hung from framing never designed for its load → Reinforcement after the fact, relocated equipment or a structural redesign during construction (caught by d11.structural-support; industry_practice)
- **11fs.fm.roughed-to-symbols** — Plumbing and electrical rough-ins set from MEP plan symbols instead of the dimensioned foodservice rough-in plans → Stubs land behind equipment, inside fabricated bases or at the wrong height; slab coring and wall patching before turnover (caught by 11fs.rough-in-drawings, 11fs.rc.rough-in-locations; industry_practice)
- **11fs.fm.floor-sink-misplaced** — Floor sinks cast in before equipment approval, ending up under legs, behind fixed equipment or beyond the reach of the item's drain → Unusable or uncleanable receptors, health inspection findings, cored and patched floors (caught by 11fs.indirect-waste, 11fs.rc.rough-in-locations; field_experience)
- **11fs.fm.suppression-line-up** — Appliances added, swapped or rearranged under the hood after the suppression system was laid out → Appliances left unprotected; the system fails its acceptance test or fire inspection (caught by 11fs.hood-suppression; industry_practice)
- **11fs.fm.exhaust-fan-short** — Hood sections lengthened or appliance duty raised in the hood submittal, while the exhaust fan is ordered to the bid-stage airflow and static pressure → Hoods fail to capture at start-up; smoke and heat roll into the kitchen and the fan is replaced or resheaved (caught by 11fs.rc.hood-exhaust, 11fs.hood-airflow; industry_practice)
- **11fs.fm.dish-vapor** — Dish machine or steam equipment venting left unconnected because no Type II hood or duct was drawn → Condensation damage to ceilings, lights and finishes; ductwork added after ceilings close (caught by 11fs.type-ii-exhaust; field_experience)
- **11fs.fm.indirect-piping-orphan** — Indirect waste piping from equipment outlets to floor sinks claimed by neither the equipment contractor nor the plumber → Unconnected drains at the health inspection; last-minute change order (caught by if.11-foodservice-plumbing; field_experience)
- **11fs.fm.suppression-not-monitored** — Hood suppression system not connected to the building fire alarm, or make-up air not shut down on discharge → Failed acceptance test and delayed occupancy (caught by if.11-hood-fire-alarm; industry_practice)
- **11fs.fm.interceptor-preliminary** — Grease interceptor sized and set from a preliminary fixture list or the civil drawings before the equipment was final → Interceptor rejected by the plumbing or sewer authority, or replaced after site work (caught by 11fs.grease-waste; industry_practice)
- **11fs.fm.cutout-mismatch** — Drop-in or undercounter unit substituted after the fabrication drawings were approved → Fabricated counters field-cut or rebuilt (caught by 11fs.custom-fabrication, d11.substitution-cascade; industry_practice)
- **edu.fm.missed-window** — Hardware, HVAC equipment or casework approved late and delivered after the summer window closes → Work moves into occupied classrooms after hours with temporary systems, or the phase slips a full year (caught by edu.summer-window; field_experience)
- **edu.fm.agency-change-unapproved** — A substitution or field change accepted by the architect is never submitted to the state school-construction agency → The agency withholds certification or closeout of the project; work is reopened or occupancy delayed (caught by edu.agency-approvals; industry_practice)
- **food.fm.change-after-approval** — Equipment substituted, a sink dropped or a finish changed after health department plan approval, without resubmitting → Pre-opening inspection fails; opening slips while items are replaced or plans re-reviewed (caught by food.plan-review; field_experience)
- **food.fm.hand-sink-items-unassigned** — Soap and towel dispensers, splash guards or tempering at hand sinks fall between the foodservice contractor, the plumber and the owner → Missing at the pre-opening inspection; last-minute purchases and a re-inspection (caught by food.hand-sinks; field_experience)
- **food.fm.no-service-sink** — No service sink or mop basin in the kitchen, or a warewashing sink too small for the largest pots, because each scope assumed the other drew it → Plan review or pre-opening comment; a sink squeezed into a finished kitchen with new waste and supply lines (caught by food.required-sinks; field_experience)

## Expected submittal contents
- **Shop Drawings**
  - Rough-in plans built from the approved equipment, dimensioning every water, waste, gas, steam and electrical connection by item number (height above floor, offset from wall or column, wall or floor)
  - Custom fabrication plans, elevations and sections with drop-in cutouts keyed to the approved model, sinks, faucet locations, utility chases and wall or floor attachment
  - Hood plan and sections per hood section, with the appliance line beneath, overhang, exhaust and supply airflow, static pressure, duct collar size and location
  - Suppression nozzle layout over the actual appliance line, with the gas valve, shutoff interlocks and manual release location
- **Product Data**
  - Equipment list by item number with quantity, model, options and owner- or contractor-furnished designation
  - Cut sheet per item with nameplate utility data and the food equipment certification
  - Hood listing and suppression system listing

## Extract for reconciliation
- d11.xf.utilities — Utility data per item (voltage, phase, load, connection type, water, waste, gas, steam, exhaust) (list, per element) → schedule.equipment, schedule.electrical_panel, drawings.plumbing, drawings.mechanical
- d11.xf.weight — Operating weight per item (number, lb, per element) → drawings.structural
- d11.xf.furnished-by — Furnished and installed by (OFOI, OFCI, CFCI) (enum, per element) → schedule.equipment, spec.part1
- 11fs.xf.item-list — Item number, quantity, model and furnished-by for every item (list, per package) → schedule.foodservice_equipment, drawings.foodservice
- 11fs.xf.gas-input — Gas input rating (number, Btu/h, per element) → drawings.plumbing, drawings.mechanical
- 11fs.xf.hood-data — Hood section exhaust and supply airflow, static pressure and collar size (list, per element) → schedule.mechanical_equipment
- 11fs.xf.certification — Food equipment certification claimed (string, per element) → spec.part2

## Standards to verify against
- NSF/ANSI 2, 3, 4 and 7: Food Equipment; Commercial Warewashing Equipment; Commercial Cooking, Rethermalization, and Powered Hot Food Holding and Transport Equipment; Commercial Refrigerators and Freezers — Confirm certification in the certifier's listing, not from a logo on a brochure page
- UL 710: Exhaust Hoods for Commercial Cooking Equipment
- UL 300: Fire Testing of Fire Extinguishing Systems for Protection of Commercial Cooking Equipment
- NFPA 96: Standard for Ventilation Control and Fire Protection of Commercial Cooking Operations — Confirm the edition the adopted fire and mechanical codes reference
- NFPA 17A: Standard for Wet Chemical Extinguishing Systems

## Warnings
- Draft knowledge in use (global, 11, 11 40 00) — not yet PE-reviewed
