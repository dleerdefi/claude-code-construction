# Gate audit — `reference/csi` milestones and gates

Source: `reference/csi/milestones.yaml` (29 milestones), SCHEMA.md §4.1/§4.4/§6/§6.1, all 293 YAML files under `reference/csi/`. Script: `scratchpad/gates_enum.py`, sample: `scratchpad/sample.py` (random.seed(7), round-robin across divisions/interface files/overlays so no division dominates).

## 1. Counts

| | checks | reconciliations | edges | total |
|---|---|---|---|---|
| gated | 636 | 129 | 270 | **1,035** |
| ungated | 624 | 12 | 4 | **640** |
| share ungated | **49.5%** | 8.5% | 1.5% | 38.2% |

- Ungated checks by severity: high 320, medium 254, **critical 34**, low 12, none 4. Ungated by kind: conformance 352, constructability 81, completeness 80, coordination 57, absence 50. Half the check layer has no "last cheap moment" at all; a critical check with no gate never appears in any `milestone --id` view.
- Unknown gate ids: 0 (validator holds). **Milestones never used: none** — but the tail is thin: `sheathing_cover` 1, `overburden_placement` 1, `precast_erection` 2, `fireproofing_application` 3, `backfill` 4, `masonry_grout` 4.
- `procurement_release`: **389 / 1,035 = 37.6%** of all gates (checks 39.3%, reconciliations 47.3%, edges 28.9%). Top 5 milestones (procurement_release, slab_pour 86, above_ceiling_close_in 77, overhead_rough_in 69, in_wall_rough_in 68) carry 689 / 1,035 = 67%.
- `procurement_release` share by division profile: 04 **85%**, 05 **71%**, 08 **62%**, 06 **61%**, 01 54%, 26 50%; interfaces div-23 **73%**, div-05 71%, div-08 65%. Overlays education/historic/public_works/occupied_renovation: 100%.

Per-milestone (total / checks / recon / edges):

```
procurement_release      389  250  61  78     opening_install            11   7  0   4
slab_pour                 86   54  12  20     equipment_set               8   4  0   4
above_ceiling_close_in    77   42   5  30     steel_erection              7   7  0   0
overhead_rough_in         69   42  14  13     energization                7   5  1   1
in_wall_rough_in          68   35  12  21     final_connection            7   5  0   2
foundation_pour           47   26   6  15     hoistway_turnover           6   4  0   2
wall_close_in             47   27   2  18     interior_finish_start       5   3  0   2
substantial_completion    41   33   1   7     backfill                    4   2  0   2
underslab_rough_in        25    9   6  10     masonry_grout               4   2  0   2
demolition_start          22   14   1   7     fireproofing_application    3   2  0   1
roof_membrane             21   10   4   7     precast_erection            2   2  0   0
site_paving               20   12   1   7     sheathing_cover             1   1  0   0
excavation                15   12   2   1     overburden_placement        1   1  0   0
trench_backfill           15    8   1   6
envelope_close_in         14    8   0   6
floor_finish_install      13    9   0   4
```

Is `procurement_release` a catch-all? Yes. Its own definition ("product, options, dimensions and quantities become fixed") is honest, but the items parked there are four different moments: subcontract buyout / scope split (`if.23-controls-wiring` says "settle in both subcontracts before buyout"), submittal approval (`01smt.grouped-packages`), release to fabrication (`08cw.mock-up-before-production`), and plain "early" (`27rc.need-determined`: whether ERRCS is required at all; `fs.installer-named`; `d05.special-inspection`: statement of special inspections). Everything that is not a concealment point lands here. Its compiled view is 1,206 lines / 35,728 words — nobody will read that before releasing anything.

## 2. Seeded sample of 30 gated items (random.seed(7))

Verdicts: **ok** = last cheap moment; **early** = forces resolution before the information exists; **late** = work already locked; **wrong** = unrelated/mis-typed. `(inc)` = inconsistent with a sibling item elsewhere.

| # | id | file | gate | verdict | right milestone | why |
|---|---|---|---|---|---|---|
| 1 | if.01-extra-stock-finishes | interfaces/div-01.yaml | procurement_release | ok | — | Extra stock must come from the same production run; order release is the moment. |
| 2 | if.05-cfmf-air-barrier | interfaces/div-05.yaml | envelope_close_in | ok | — | Slip-joint transition and clip seals are concealed by cladding; the detail itself should be in the AB submittal, but cladding is the cover. |
| 3 | if.06-openings-in-framing | interfaces/div-06.yaml | opening_install | **late** | sheathing_cover (really a missing "rough framing" milestone) | Rough openings are framed, sheathed and wrapped long before a window arrives; discovering a nominal-size RO at install means reframing and re-flashing. |
| 4 | if.blindside-shoring | interfaces/div-07.yaml | foundation_pour | ok | — | Pre-applied membrane over lagging is locked when the wall is poured; tieback/raker details should already be on the shoring submittal, but the pour is the cover. |
| 5 | if.08-framing-glazing | interfaces/div-08.yaml | procurement_release | ok | — | Glass makeup vs pocket depth/bite must be settled before frames are cut. |
| 6 | if.10-visual-display-av | interfaces/div-10.yaml | in_wall_rough_in | ok | — | Boxes/conduit behind the board wall; consistent with the other backing/rough-in edges. |
| 7 | if.12-mat-recess-drains | interfaces/div-12.yaml | slab_pour | ok | — | Drain body in the recess is cast with the slab. |
| 8 | if.21-water-entry | interfaces/div-21.yaml | underslab_rough_in | ok | — | Split point/backflow/room drain are fixed with the underslab stubs; the room size is a design question that should be settled earlier, but the concealment point is right. |
| 9 | if.22-sensor-fixtures-power | interfaces/div-22.yaml | in_wall_rough_in | ok | — | Transformer boxes and circuits under counters/in chases. |
| 10 | if.23-controls-wiring | interfaces/div-23.yaml | procurement_release | **wrong (no home)** | missing `buyout` milestone | The note itself says "before buyout; a pricing question before a field question". Order release of controls is months after subcontract award. |
| 11 | if.28-fire-alarm-access-release | interfaces/div-28.yaml | above_ceiling_close_in | ok (inc) | wall_close_in | Release wiring to lock power supplies usually runs through door frames/walls; sibling `if.08-fire-alarm-doors` (same relays, same doors) is gated wall_close_in. One of the two is wrong. |
| 12 | if.31-subgrade-paving | interfaces/div-31.yaml | site_paving | ok | — | Proof-roll/acceptance immediately before base is the actual hold point. |
| 13 | if.32-irrigation-water-service | interfaces/div-32.yaml | procurement_release | ok | — | Pressure/flow before irrigation equipment is released; the tap size is locked later at trench_backfill, acceptable. |
| 14 | if.food-grease-duct-enclosure | interfaces/ov-foodservice.yaml | above_ceiling_close_in | **late** (inc) | overhead_rough_in | Its own note: "shafts are closed as they are built; access-door framing goes in with the shaft wall". `09gb.shaft-walls` is gated overhead_rough_in. By ceiling closure the shaft is boarded and the leakage test window is gone. |
| 15 | if.lab-gas-detection | interfaces/ov-laboratory.yaml | in_wall_rough_in | ok | — | Detector boxes and shutoff interlock wiring need in-wall boxes. |
| 16 | if.park-barrier-anchorage | interfaces/ov-parking_structure.yaml | procurement_release | ok | — | Anchors must be on the PT/precast shop drawings; "whose" procurement is ambiguous but the moment is right. |
| 17 | hc.ceiling-mounted-equipment | overlays/healthcare.hospital.yaml | overhead_rough_in | ok | — | Boom/light structure and the clear zones must be set while structure is still reachable. |
| 18 | 01smt.grouped-packages | profiles/01/01-33-00.yaml | procurement_release | ok | — | Review-together rule; approval is the only moment it can bite. |
| 19 | 08lv.drainage | profiles/08/08-91-00.yaml | opening_install | ok (mixed) | — | Sill flashing/AB return is concealed at install; the integral drain pan is a fabrication item and would belong at procurement_release. Acceptable. |
| 20 | 09cl.service-access | profiles/09/09-50-00.yaml | above_ceiling_close_in | ok | — | Classic. |
| 21 | 11fs.hood-suppression | profiles/11/11-40-00.yaml | procurement_release | ok | — | Coverage of the final line-up is a design/submittal check; the test is at SC and is separately gated. |
| 22 | 12wt.motorized-controls | profiles/12/12-20-00.yaml | in_wall_rough_in | ok (mixed) | — | Rough-in is right for power/control boxes; the "who furnishes, wires, programs" clause is a buyout question with no milestone. |
| 23 | 13sv.isolator-selection | profiles/13/13-48-00.yaml | procurement_release | ok | — | Isolator selection is fixed at order. |
| 24 | 21fp.selection | profiles/21/21-30-00.yaml | procurement_release | ok | — | Pump curve vs supply; fixed at order. |
| 25 | 23vs.restraint-design | profiles/23/23-05-48.yaml | procurement_release | **early / split** (inc) | slab_pour for the reactions-and-pads clause | The check says reactions reach "the concrete trade before pads are formed"; `if.03-housekeeping-pads` is gated slab_pour. The restraint hardware itself is procurement_release; the check bundles two moments under the earlier one. |
| 26 | 26ts.time-delays | profiles/26/26-36-00.yaml | substantial_completion | ok | — | Set and recorded at the generator acceptance test. |
| 27 | 27rc.need-determined | profiles/27/27-53-19.yaml | procurement_release | **wrong** | above_ceiling_close_in (pathways), or a missing preconstruction/permit milestone for the decision | Nothing is "ordered" here; the cheap moment for the decision is permit/preconstruction, and the cheap moment for the DAS pathways is before ceilings close. procurement_release is being used to mean "early". |
| 28 | 28fa.monitoring-path | profiles/28/28-46-00.yaml | substantial_completion | ok | — | Monitoring live for the acceptance test. |
| 29 | pv.slope-tolerance | profiles/32/32-10-00.yaml | site_paving | ok | — | "Raise it before forming; check before the pour" — the pour is the last cheap moment. |
| 30 | sw.pipe-substitution | profiles/33/33-40-00.yaml | procurement_release | ok | — | Substitution is fixed at order. |

Tally: **22 ok, 2 ok-with-caveat, 2 late, 1 early/split, 2 wrong/no-home, 1 inconsistent-ok** (24/30 defensible, 6/30 I would change). Of the 11 sampled `procurement_release` gates, 3 (#10, #25, #27) are not about an order or fabrication release at all.

### Cross-division inconsistencies (same kind of item, different gate)

- **Firestopping**: `if.firestop-mep-penetrations` procurement_release; `if.firestop-rated-walls` overhead_rough_in; `fs.annular-space` above_ceiling_close_in. The near-identical insulation-vs-listing check is `23in.firestop-match` = procurement_release but `22in.firestop-match` = above_ceiling_close_in. Both cannot be "last cheap".
- **Fixture carriers**: `if.09-fixture-carriers` in_wall_rough_in; `22fx.carriers` and `if.06-plumbing-fixture-support` wall_close_in.
- **Housekeeping pads / reactions to structure**: `if.03-housekeeping-pads`, `03cip.rc.housekeeping-pads`, `26ds.stub-ups` slab_pour; `23vs.restraint-design`, `d11.structural-support`, `if.26-utility-service` procurement_release.
- **Mock-ups**: `08cw.mock-up-before-production` and `d04.mockup` procurement_release; `if.01-envelope-mockup` opening_install, although its own note says "release production fabrication after the mock-up's field test" — that is procurement_release by definition; at opening_install the production units are already on the truck. **Late.**
- **Elevator steel**: `if.05-elevator-supports` hoistway_turnover, note says "steel is usually detailed before the elevator is selected" — the divider/hoist beams are fixed at steel fabrication (procurement_release / steel_erection); the hoistway survey only discovers the miss. **Late.**
- **Shaft enclosure**: `09gb.shaft-walls` overhead_rough_in vs `if.food-grease-duct-enclosure` above_ceiling_close_in.
- **Access panels**: 8 at above_ceiling_close_in vs `d23.service-access`, `23tu.handing-access` at procurement_release.
- **Sleeves/embeds**: split roughly evenly among procurement_release (10), slab_pour (9), foundation_pour (8) — partly legitimate (precast cast-in vs CIP), but `03pc.cast-in-for-others` (procurement_release) and `if.03-cladding-embeds` (slab_pour) describe the same hand-off.
- **Permits/AHJ**: `d21.approvals-before-install`, `d14.permit-filing`, `26gn.permits`, `21wb.water-supply-test` all at procurement_release because there is no permit milestone.

## 3. The milestone list itself

**Missing milestones a PE needs**

1. `buyout` / subcontract award — every "confirm who" responsibility split and the "settle in both subcontracts" notes (#10, #22, `if.26-utility-service`) have no home; they are mis-filed under procurement_release.
2. `permit_approval` / AHJ plan approval and deferred submittals (fire sprinkler, fire alarm, elevator, ERRCS, curtain wall) — 8 items currently parked at procurement_release (`d21.approvals-before-install`, `d14.permit-filing`, `27rc.need-determined`, `01smt.rc.deferred-list`).
3. Split `procurement_release` into **`submittal_approval`** (design-level conformance, 250 checks) and **`fabrication_release`** (dimensions/embeds fixed) at minimum; a `long_lead_order` date would carry `g.lead-time`, `01sch.procurement-logic`, `edu.summer-window`.
4. `rough_framing` (partition layout / rough openings framed) — `in_wall_rough_in` presupposes the walls exist; items like #3 and `if.09-fixture-carriers` (chase depth) are framing-layout items, not rough-in items.
5. `ceiling_grid` — grid layout fixes sprinkler, light and diffuser positions before tile; the schema folds it into above_ceiling_close_in, which is the tile, not the grid.
6. `shaft_enclosure` — SCHEMA §6.1 says shafts are "concealed at above_ceiling_close_in"; on site they are boarded with the framing, months earlier. The definition papers over a real timing difference (#14).
7. `curtain_wall_mockup` (performance mock-up test) — exists only as `inspect_before` on opening_install, which is the wrong moment; it gates fabrication release.
8. `dry_in` / building enclosed and `temporary_to_permanent_hvac` — `interior_finish_start` approximates this but is phrased as a trade start, not an enclosure state.
9. `owner_move_in` / `final_completion` / occupancy — FF&E, owner-furnished equipment, training, extra stock receipt, warranty start are all crammed into substantial_completion (41 items).
10. `underground_utilities`: exists as `trench_backfill`; fine. `tab_complete` / `startup` could split `final_connection` (7 items) from `substantial_completion`.

**Ordering** (file says approximate, within one area; still): `hoistway_turnover` sits before `overhead_rough_in` — normally after structure tops out and alongside rough-in; `equipment_set` and `final_connection` sit after `floor_finish_install` — mechanical/electrical rooms set equipment before any finish floor; `site_paving` is listed second-to-last although site utilities (`trench_backfill`) sit near the top — fine as a separate area, but `inspect_before` ordering in the compiled list will mislead a sequence reader. `sheathing_cover` between `precast_erection` and `slab_pour` is only true for podium-style wood frame.

**`inspect_before` accuracy as hold points**

- Good: foundation_pour, slab_pour (except "PT tendon layout on hand" is a records item, not a hold), trench_backfill, masonry_grout, steel_erection, precast_erection, sheathing_cover, roof_membrane, energization, floor_finish_install, substantial_completion, demolition_start, excavation.
- **Empty and wrong**: `backfill` — waterproofing manufacturer's/consultant's inspection before backfill is a standard warranty hold point; `overburden_placement` — flood test / electronic leak detection before overburden is the classic hold point; `overhead_rough_in` — defensibly empty.
- **Violate the file's own rule** ("formal hold points only"): `wall_close_in` "Blocking and backing checked against the master list"; `underslab_rough_in` "locations checked against layouts"; `equipment_set` "rough-in locations checked against submittals"; `procurement_release` "submittal approved" (tautological). These are coordination items and should compile from gates.
- **Mis-timed**: `opening_install` "Mock-up and field testing approved" — must precede fabrication release, not installation.
- `envelope_close_in` "flashings inspected" names no inspector (AB manufacturer / envelope consultant); `roof_membrane` lacks the roofing manufacturer's substrate/deck acceptance.
- `excavation` and `final_connection` have `covers: []` — a milestone that covers nothing and locks nothing is, by §6.1's own definition, not a milestone; excavation covers "existing utilities and adjacent structure condition", final_connection locks "utility characteristics".

## 4. `milestone --id wall_close_in --format md`

178 lines, 4,760 words, 33.4 KB ≈ 6.5–8.2k tokens. Sections: covers (3) · inspect first (2) · coordination to close (18 edges) · checks due (23) · documents that must agree (2) · what goes wrong (33 failure modes).

Usable, not a dump: sorted by severity, one line per item with trace/owner/gate, `Confirm who` splits attached. Weaknesses: the 33 failure modes are ~40% of the words and restate the same miss eight ways (`05rl.fm.bracket-no-backing`, `06rc.fm.backing-missed`, `06aw.fm.no-backing`, `09gb.fm.backing-missed`, `10wp.fm.rails-pull-off`, `d10.fm.backing-after-close-in`, `cw.fm.in-wall-brackets-missed`, `12hc.fm.rail-backing-partial`); no de-duplication of the seven backing edges into one "backing master list" line; `--project` would prune but was not tested here. For comparison: `procurement_release` compiles to 1,206 lines / 35.7k words (a dump), `slab_pour` 293 / 8.4k, `above_ceiling_close_in` 273 / 7.0k, `sheathing_cover` 14 / 154.

## 5. Judgment: rigor or theater?

**Mostly rigor at the concealment milestones, theater at `procurement_release`.** The numbers:

- Where the gate is a physical cover (wall_close_in, above_ceiling_close_in, slab_pour, foundation_pour, roof_membrane, site_paving, trench_backfill), the sample was 17/18 correct and the compiled views (7–8k words) are genuine pre-cover review packages.
- `procurement_release` carries 389 items (37.6%) and is used to mean five different things (buyout, submittal approval, fabrication release, permit, "early"). In the sample 3 of 11 procurement_release gates were not procurement at all. Its compiled view (35.7k words) cannot be used, so for 38% of gated items the mechanism exists only as a label.
- 640 items (49.5% of checks, including 34 critical) have no gate and are invisible to every milestone view.
- Found inconsistencies in 9 item families where the same hand-off is gated at different milestones in different divisions, including one pair of near-identical checks (`22in`/`23in.firestop-match`) and two gates the authors' own notes contradict (`if.01-envelope-mockup`, `if.05-elevator-supports`).
- Two milestones have empty `inspect_before` where the industry has a standard hold point (backfill, overburden), and four `inspect_before` lists break the file's own "formal hold points only" rule.

Fixes in priority order: (1) split `procurement_release` into buyout / submittal_approval / fabrication_release and add `permit_approval`; (2) gate or explicitly mark `gate: none` on the 34 critical and 320 high ungated checks; (3) reconcile the nine inconsistent families; (4) fill backfill/overburden hold points and move the mock-up test to the fabrication gate; (5) de-duplicate failure modes in the compiled view.
