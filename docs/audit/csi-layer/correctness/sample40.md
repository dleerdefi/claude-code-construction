## 1. [edges] `if.08-dock-equipment` — reference/csi/interfaces/div-08.yaml
```yaml
id: if.08-dock-equipment
a:
- 08 33 00
- 08 36 00
a_trade: Coiling and sectional doors
b:
- 11 13 00
b_trade: Loading dock equipment
a_provides: Door guides and tracks, jamb and header conditions, door height against the shelter or seal
  head, bottom seal and where the closed door lands on the leveler or pit edge, and operator controls
  at each dock position
b_provides: Leveler, restraint, bumper and seal or shelter mounting on the door jambs and header, clear
  of the guides, and the interlocks the spec requires among restraint, leveler and door operator (door
  cannot open until the trailer is restrained; leveler cannot deploy with the door closed)
responsibility:
- item: Interlock wiring between dock equipment and door operators
  typical:
    furnish: 11 13 00 or 08 33 00
    install: 26 05 00
    connect: 26 05 00
  confirm_in:
  - spec.part1
  - drawings.electrical
gate:
  milestone: procurement_release
severity: medium
failure: Seals or shelters clash with door guides, or interlocks left unwired at turnover
```

## 2. [failure_modes] `21fp.fm.test-water-nowhere` — reference/csi/profiles/21/21-30-00.yaml
```yaml
id: 21fp.fm.test-water-nowhere
what_happens: Test header discharge aimed at landscaping, a sidewalk or a drain far too small for it
consequence: Acceptance test delayed, or the site and the building flooded during it
caught_by:
- 21fp.test-flow
- if.21-drain-discharge
source: industry_practice
```

## 3. [edges] `if.03-steel-anchorage` — reference/csi/interfaces/div-03.yaml
```yaml
id: if.03-steel-anchorage
a:
- 03 30 00
- 03 15 00
- 03 60 00
a_trade: Cast-in-place concrete, cast-in anchors and grouting
b:
- 05 12 00
- 05 50 00
- 05 05 19
b_trade: Structural steel, metal fabrications and post-installed anchors
a_provides: Anchor rods and embed plates set from the approved steel and metals layouts and surveyed before
  the pour; grout under base and bearing plates once the frame is plumbed and released
b_provides: Approved anchor rod and embed layouts (location, elevation, projection, rod size and pattern,
  plate size) and the fabricated items, delivered before forms close; any post-installed fix proposed
  with an evaluation report for the engineer's acceptance
responsibility:
- item: Anchor rods and embed plates
  typical:
    furnish: 05 12 00 or 05 50 00
    install: 03 30 00
  confirm_in:
  - spec.part1
  - drawings.structural
- item: Grout under column base plates and bearing plates
  typical:
    furnish: 03 60 00 or 05 12 00
    install: 03 60 00 or 05 12 00
  confirm_in:
  - spec.part1
  - spec.part3
gate:
  milestone: foundation_pour
  note: The steel anchor rod layout is approved before footing and pier forms close; the as-built survey
    is accepted before steel_erection
severity: critical
```

## 4. [review_checks] `d07.warranty-conditions` — reference/csi/profiles/07/_division.yaml
```yaml
id: d07.warranty-conditions
kind: completeness
check: 'Where a manufacturer''s system warranty is specified, the submittal shows the installer''s approval
  by that manufacturer, that every component in the assembly is accepted under the warranty, and any pre-approval
  or inspection the manufacturer requires before and after installation.

  '
trace_to:
- spec.part1
- spec.part2
severity: high
owner: subcontractor
```

## 5. [failure_modes] `01sch.fm.permanent-power-late` — reference/csi/profiles/01/01-32-00.yaml
```yaml
id: 01sch.fm.permanent-power-late
what_happens: The utility company's permanent service date is never in the schedule
consequence: Start-up, testing and conditioning wait on temporary power; finishes and commissioning slide
  behind it
caught_by:
- 01sch.owner-activities
source: industry_practice
```

## 6. [failure_modes] `up.fm.permeable-clogged` — reference/csi/profiles/32/32-14-00.yaml
```yaml
id: up.fm.permeable-clogged
what_happens: Permeable pavers installed before the site is stabilized; sediment fills the joints and
  reservoir
consequence: Fails infiltration; vacuum restoration or reconstruction, and stormwater certification withheld
caught_by:
- up.permeable-protection
- if.32-permeable-paving-stormwater
source: industry_practice
```

## 7. [review_checks] `11fh.hood-types` — reference/csi/profiles/11/11-53-13.yaml
```yaml
id: 11fh.hood-types
kind: conformance
submittal_types:
- Shop Drawings
- Product Data
check: 'Each hood''s type (bypass, variable-volume, high-performance, perchloric acid with washdown, radioisotope,
  distillation or floor-mounted), size, sash configuration, liner and interior services match the hood
  schedule and lab program. Perchloric acid hoods need washdown water, a drain and a dedicated exhaust
  duct and fan with no other connections.

  '
trace_to:
- schedule.equipment
- spec.part2
- drawings.plumbing
severity: high
owner: subcontractor
gate: procurement_release
```

## 8. [review_checks] `06wf.joist-routing` — reference/csi/profiles/06/06-11-00.yaml
```yaml
id: 06wf.joist-routing
kind: coordination
check: 'Joist and rafter direction, depth and hole zones leave paths for the duct mains, waste lines and
  sprinkler mains the MEP drawings route through them; where they do not, the routing or the framing changes
  before the framing layout is released.

  '
trace_to:
- drawings.structural
- drawings.mechanical
- drawings.plumbing
- drawings.fire_protection
severity: medium
owner: gc
gate: procurement_release
```

## 9. [standards] `cw.std.bhma-a156-9` — reference/csi/profiles/12/12-30-00.yaml
```yaml
id: cw.std.bhma-a156-9
name: ANSI/BHMA A156.9
title: Cabinet Hardware
verify: Hardware grade and function claims on product data
note: Confirm the edition the spec cites
```

## 10. [review_checks] `ind.storage-basis` — reference/csi/overlays/industrial.warehouse.yaml
```yaml
id: ind.storage-basis
kind: conformance
scope: package
check: 'The sprinkler design states the storage it protects (commodity class including plastics, storage
  height, rack or solid-pile arrangement, aisle widths, clearance to sprinklers) and that basis matches
  the owner''s or tenant''s storage program. A speculative building records the basis it was designed
  for, so the first tenant can be checked against it before move-in.

  '
trace_to:
- drawings.fire_protection
- spec.part2
- drawings.storage_racks
severity: critical
owner: design_team
gate: procurement_release
```

## 11. [review_checks] `22pp.gravity-fit` — reference/csi/profiles/22/22-10-00.yaml
```yaml
id: 22pp.gravity-fit
kind: constructability
check: 'Long gravity runs are checked from the farthest fixture to the building exit at the design slope
  against beams, ducts, ceiling heights and the building-line invert, before the above-ceiling coordination
  is settled.

  '
trace_to:
- drawings.plumbing
- drawings.structural
- drawings.building_sections
severity: high
owner: design_team
gate: overhead_rough_in
```

## 12. [review_checks] `08lv.rating-basis` — reference/csi/profiles/08/08-91-00.yaml
```yaml
id: 08lv.rating-basis
kind: conformance
check: 'Water penetration and pressure drop are certified ratings at the free-area velocity this louver
  will actually see, not catalog figures at nominal face area; intakes in exposed locations or where the
  spec asks for it carry a wind-driven rain rating, and screens are counted in the free area and pressure
  drop.

  '
trace_to:
- spec.part2
- schedule.mechanical_equipment
severity: high
owner: subcontractor
```

## 13. [review_checks] `12wt.motorized-controls` — reference/csi/profiles/12/12-20-00.yaml
```yaml
id: 12wt.motorized-controls
kind: coordination
scope: package
check: 'Motorized shades have motor voltage, power supply and panel locations, circuits, control wiring,
  keypads, sensors and the integration with lighting controls, building automation or AV defined, with
  who furnishes, wires, programs and commissions each piece.

  '
trace_to:
- drawings.electrical
- spec.part1
- spec.part2
severity: high
owner: gc
gate: in_wall_rough_in
```

## 14. [standards] `06tr.std.bcsi` — reference/csi/profiles/06/06-17-53.yaml
```yaml
id: 06tr.std.bcsi
name: BCSI
title: Guide to Good Practice for Handling, Installing, Restraining and Bracing of Metal Plate Connected
  Wood Trusses
verify: Temporary and permanent bracing practice the installer follows
```

## 15. [edges] `if.21-drain-discharge` — reference/csi/interfaces/div-21.yaml
```yaml
id: if.21-drain-discharge
a:
- 21 10 00
- 21 30 00
a_trade: Sprinkler, standpipe and fire pump systems
b:
- 22 13 00
- 22 14 00
b_trade: Sanitary and storm drainage
a_provides: Each test and drain discharge (main drain, inspector's test, auxiliary drains, backflow forward-flow
  test, pump test, relief and casing discharge) with its location and full flow
b_provides: Receptors and drains sized for those flows, or an exterior discharge point agreed with the
  site design
responsibility:
- item: Receptors for fire protection test and relief discharges
  typical:
    furnish: 22 13 00
    install: 22 13 00
  confirm_in:
  - drawings.plumbing
  - drawings.fire_protection
gate:
  milestone: underslab_rough_in
severity: medium
```

## 16. [edges] `if.06-av-backing` — reference/csi/interfaces/div-06.yaml
```yaml
id: if.06-av-backing
a:
- 06 10 53
- 06 11 00
a_trade: Rough carpentry and wood framing
b:
- 27 41 00
- 11 52 00
b_trade: Audio-video systems and equipment (displays, projectors, speakers, screens)
a_provides: Backing in walls and ceilings at each display, projector, speaker and screen mount
b_provides: Mount model, location, height, weight and backing extent for each device, including owner-furnished
  displays
gate:
  milestone: wall_close_in
severity: high
failure: Displays and projectors located after close-in on owner-selected mounts; walls opened, or devices
  hung on anchors the mount maker does not allow
```

## 17. [review_checks] `23ct.sequences-absent` — reference/csi/profiles/23/23-09-00.yaml
```yaml
id: 23ct.sequences-absent
kind: absence
check: 'The design gives a sequence for every controlled system, including exhaust fans, unit heaters,
  decentralized units, packaged equipment interfaces and fire and smoke modes. "By the controls contractor"
  or "per manufacturer" for a system that needs coordination is an RFI candidate before the controls design
  starts.

  '
trace_to:
- drawings.controls
- spec.part3
severity: high
owner: design_team
gate: procurement_release
```

## 18. [regulatory_hooks] `d10.rh.membrane-penetrations` — reference/csi/profiles/10/_division.yaml
```yaml
id: d10.rh.membrane-penetrations
topic: membrane-penetration-allowances
question: 'Which recessed specialties in rated walls does the adopted code treat as membrane penetrations,
  and which need a listed rated unit or rated construction behind them?

  '
applies_when: Recessed or semi-recessed specialties in rated walls
source_families:
- building_code
severity: high
```

## 19. [review_checks] `08hw.egress-hardware` — reference/csi/profiles/08/08-71-00.yaml
```yaml
id: 08hw.egress-hardware
kind: conformance
check: 'Every door in the means of egress opens from the egress side without a key, tool or special knowledge;
  panic or fire exit hardware is provided where the occupancy and occupant load require it; and any special
  locking (delayed egress, sensor release, controlled egress, elevator lobby or stair door locking with
  re-entry) is one the code allows for this occupancy, with its signage and release conditions.

  '
trace_to:
- drawings.life_safety
- schedule.door_hardware
severity: critical
owner: design_team
```

## 20. [failure_modes] `28fa.fm.monitoring-not-live` — reference/csi/profiles/28/28-46-00.yaml
```yaml
id: 28fa.fm.monitoring-not-live
what_happens: Monitoring lines or cellular communicator not live when the AHJ arrives for the acceptance
  test
consequence: Test rescheduled; occupancy delayed
caught_by:
- 28fa.monitoring-path
- if.27-fire-alarm-communicator
source: industry_practice
```

## 21. [review_checks] `park.enclosed-ventilation` — reference/csi/overlays/parking_structure.yaml
```yaml
id: park.enclosed-ventilation
kind: completeness
scope: package
sections:
- 23 09*
- 23 3*
- 28 4*
check: 'In enclosed garages the exhaust fans, gas detection (carbon monoxide, and nitrogen dioxide where
  diesel vehicles use the garage), sensor layout and calibration, the control sequence that stages fans
  on gas level with any minimum ventilation mode, and makeup air are submitted together and agree with
  each other.

  '
trace_to:
- drawings.mechanical
- spec.part2
severity: high
owner: subcontractor
```

## 22. [failure_modes] `22sd.fm.hidden-overflow` — reference/csi/profiles/22/22-14-00.yaml
```yaml
id: 22sd.fm.hidden-overflow
what_happens: Overflow leaders discharge behind landscaping or into an underground line nobody watches
consequence: Clogged primary drains go unnoticed until the roof ponds or leaks
caught_by:
- 22sd.overflow-discharge
source: industry_practice
```

## 23. [regulatory_hooks] `33hc.rh.fuel-gas` — reference/csi/profiles/33/33-50-00.yaml
```yaml
id: 33hc.rh.fuel-gas
topic: fuel-gas-service-installation
question: 'What do the adopted fuel gas code and the gas utility require for service lines, meter location
  and clearances, buried piping material and protection, and pressure testing?

  '
applies_when: Natural gas or propane service
source_families:
- fuel_gas_code
- utility_service_rules
severity: high
```

## 24. [review_checks] `26lt.substitution-photometrics` — reference/csi/profiles/26/26-50-00.yaml
```yaml
id: 26lt.substitution-photometrics
kind: conformance
check: 'A substituted or value-engineered type is accepted only with photometric files for the proposed
  product and recalculated light levels, uniformity and lighting power; equal lumen output is not equivalence.

  '
trace_to:
- schedule.lighting_fixture
- report.energy_compliance
- register.substitutions
severity: high
owner: subcontractor
```

## 25. [regulatory_hooks] `park.rh.open-or-enclosed` — reference/csi/overlays/parking_structure.yaml
```yaml
id: park.rh.open-or-enclosed
topic: open-parking-garage-classification
sections:
- 03 45*
- 04 2*
- 05 7*
- 07 4*
- 08 9*
- 10 82*
- 21 1*
- 23 3*
- 32 35*
question: 'Does the garage meet the adopted code''s definition of an open parking garage (openness area
  and its distribution around the perimeter, interior wall limits), or is it enclosed, and what ventilation,
  sprinkler and construction requirements follow from the classification?

  '
applies_when: Every parking structure
source_families:
- building_code
- mechanical_code
- fire_code
severity: critical
```

## 26. [review_checks] `gi.design-criteria` — reference/csi/profiles/31/31-66-00.yaml
```yaml
id: gi.design-criteria
kind: completeness
check: 'The contract states the performance criteria the delegated design must meet (bearing pressure,
  settlement and differential settlement limits, slab support, uplift and lateral demand, liquefaction
  mitigation where required), and they are the same values the structural design assumed.

  '
trace_to:
- report.geotechnical
- drawings.structural
- spec.part1
severity: critical
owner: design_team
gate: procurement_release
```

## 27. [regulatory_hooks] `22in.rh.flame-smoke` — reference/csi/profiles/22/22-07-00.yaml
```yaml
id: 22in.rh.flame-smoke
topic: insulation-flame-smoke-ratings
question: 'What flame-spread and smoke-developed limits apply to plumbing pipe insulation, jackets and
  adhesives under the adopted mechanical code, inside and outside plenums?

  '
applies_when: Every plumbing insulation submittal
source_families:
- mechanical_code
severity: medium
```

## 28. [standards] `11hc.std.nfpa-99` — reference/csi/profiles/11/11-70-00.yaml
```yaml
id: 11hc.std.nfpa-99
name: NFPA 99
title: Health Care Facilities Code
verify: Essential electrical system and medical gas requirements that govern equipment connections
note: Confirm the edition adopted by the jurisdiction and the federal reimbursement authority
```

## 29. [edges] `if.23-gas-service` — reference/csi/interfaces/div-23.yaml
```yaml
id: if.23-gas-service
a:
- 23 11 23
- 23 50 00
- 23 74 00
a_trade: Facility natural-gas piping and gas-fired equipment
b:
- 33 52 16
b_trade: Gas service piping and the utility meter set
a_provides: Connected load and the inlet pressure each appliance needs at full fire, the building piping
  design pressure, and the meter and regulator location the building layout wants
b_provides: The utility's committed delivery pressure, meter and service regulator location and clearances,
  service line route and size, and the point where the utility's scope ends
responsibility:
- item: Service line, meter and service regulator
  typical:
    furnish: gas utility or 33 52 16
    install: gas utility or 33 52 16
  confirm_in:
  - drawings.civil
  - report.utility_requirements
- item: Piping from the meter outlet to the appliances, with line regulators where the building runs at
    elevated pressure
  typical:
    furnish: 23 11 23
    install: 23 11 23
  confirm_in:
  - spec.part1
  - drawings.mechanical
gate:
  milestone: procurement_release
  note: Get the utility's delivery pressure in writing before gas-fired equipment and regulators are released
severity: high
```

## 30. [failure_modes] `23pu.fm.cavitation` — reference/csi/profiles/23/23-21-23.yaml
```yaml
id: 23pu.fm.cavitation
what_happens: Condenser water pump selected without checking NPSH against the basin elevation and suction
  piping
consequence: Cavitation noise, impeller erosion and lost flow at peak load
caught_by:
- 23pu.npsh
source: industry_practice
```

## 31. [review_checks] `04cm.reinforcing-details` — reference/csi/profiles/04/04-05-00.yaml
```yaml
id: 04cm.reinforcing-details
kind: completeness
submittal_types:
- Shop Drawings
check: 'Reinforcing shop drawings show every wall''s vertical bars in the cells the layout grouts, the
  laps and positioners, bars at openings, corners, wall ends and intersections, and bond beam bars continuous
  or stopped at control joints as the structural details require.

  '
trace_to:
- drawings.structural
- drawings.exterior_elevations
severity: high
owner: subcontractor
gate: procurement_release
```

## 32. [regulatory_hooks] `13sv.rh.isolated-seismic` — reference/csi/profiles/13/13-48-00.yaml
```yaml
id: 13sv.rh.isolated-seismic
topic: seismic-nonstructural-anchorage
question: 'What seismic restraint must isolated floors, ceilings and wall assemblies have at this site,
  and must its design be sealed and submitted?

  '
applies_when: Isolated construction in seismic design categories where nonstructural components need restraint
source_families:
- building_code_seismic
severity: medium
```

## 33. [failure_modes] `d31.fm.dirty-import` — reference/csi/profiles/31/_division.yaml
```yaml
id: d31.fm.dirty-import
what_happens: Fill imported from an undocumented source turns out contaminated or outside the gradation
  limits
consequence: Excavation and disposal of placed fill, and environmental liability for the site
caught_by:
- d31.material-tracking
source: industry_practice
```

## 34. [review_checks] `11wi.refrigeration-route` — reference/csi/profiles/11/11-41-00.yaml
```yaml
id: 11wi.refrigeration-route
kind: coordination
check: 'Each condensing unit has a confirmed location (roof, yard or remote rack) with its curb or pad,
  power and disconnect, and a refrigerant line route within the manufacturer''s length and lift limits;
  roof and wall penetrations for the lines are located; heat rejected by self-contained units into the
  kitchen is in the mechanical load.

  '
trace_to:
- drawings.roof_plan
- drawings.mechanical
- drawings.foodservice
severity: high
owner: gc
gate: overhead_rough_in
```

## 35. [failure_modes] `01sch.fm.manufactured-recovery` — reference/csi/profiles/01/01-32-00.yaml
```yaml
id: 01sch.fm.manufactured-recovery
what_happens: An update recovers a slipped completion date by deleting logic or cutting remaining durations
consequence: The accepted schedule hides a real delay that later becomes a claim with no credible baseline
caught_by:
- 01sch.update-changes
- 01sch.constraints-and-float
source: industry_practice
```

## 36. [failure_modes] `04um.fm.joints-bridged` — reference/csi/profiles/04/04-20-00.yaml
```yaml
id: 04um.fm.joints-bridged
what_happens: Movement joints filled with mortar or crossed by continuous joint reinforcement
consequence: Cracks beside the joint; brick growth pushes past corners and cracks the returns
caught_by:
- 04um.movement-joints
source: industry_practice
```

## 37. [regulatory_hooks] `06aw.rh.interior-finish` — reference/csi/profiles/06/06-40-00.yaml
```yaml
id: 06aw.rh.interior-finish
topic: interior-wall-finish-classification
question: 'What flame spread and smoke-developed classification does the adopted code require for wall
  and ceiling finishes in each occupancy and location (exits, corridors, rooms), and which panel products
  in the woodwork achieve it?

  '
applies_when: Wood paneling, wainscot or ceilings used as interior finish
source_families:
- building_code
severity: high
```

## 38. [review_checks] `08df.frame-wall-match` — reference/csi/profiles/08/08-10-00.yaml
```yaml
id: 08df.frame-wall-match
kind: conformance
submittal_types:
- Shop Drawings
check: 'Each frame''s profile, throat and anchors match the wall at that opening: stud size, board layers
  on each side, finishes that add thickness (tile, wainscot, abuse-resistant board), shaft wall, masonry,
  concrete or existing construction, and a change of wall type across the opening. Wraparound, butt and
  slip-on profiles match the details.

  '
trace_to:
- schedule.partition_type
- drawings.plans
- drawings.details
severity: high
owner: subcontractor
gate: procurement_release
```

## 39. [failure_modes] `22ef.fm.source-runs-out` — reference/csi/profiles/22/22-45-00.yaml
```yaml
id: 22ef.fm.source-runs-out
what_happens: The heater serving the emergency fixtures cannot hold tepid water for the full flush
consequence: An injured person gets cold water partway through; a heater added or replaced
caught_by:
- 22ef.tempered-capacity
source: industry_practice
```

## 40. [regulatory_hooks] `fs.rh.membrane-penetrations` — reference/csi/profiles/07/07-84-00.yaml
```yaml
id: fs.rh.membrane-penetrations
topic: membrane-penetration-allowances
question: 'Which membrane penetrations of rated walls (device boxes by material, size, area and spacing)
  does the adopted code allow without a listed system, and which need listed boxes or protective pads?

  '
applies_when: Electrical and low-voltage boxes in rated walls
source_families:
- building_code
severity: medium
```

