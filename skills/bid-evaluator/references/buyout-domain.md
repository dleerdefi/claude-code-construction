# Buyout Domain Knowledge

Loaded during Step 2 (Bid Analysis). Use for bid language interpretation, scope split conventions, red flag detection, and non-price evaluation.

## Bid Language

| Term | Meaning | Risk |
|------|---------|------|
| NIC / Not in Contract | Explicitly excluded from this sub's scope | Who carries it? |
| NFC / Not From Contract | Same as NIC — different wording | Who carries it? |
| By Others | Another trade is responsible | Verify assignment in specs |
| "As required" | Vague inclusion — sub interprets minimally | Quantify during negotiation |
| "Per plans and specs" | Claims full compliance — verify bid date matches current set | Check addenda acknowledgment |
| Allowance | Placeholder amount — actual cost TBD | Track overruns; confirm units |
| Alternate | Optional scope — add or deduct from base | Preserve sign; don't mix into base |
| Unit price | Rate per unit — quantity TBD or variable | Confirm units match spec (SF, LF, EA, CY) |
| T&M / Time & Material | No lump sum — cost-plus | Cap or convert to GMP if possible |
| Lump sum | Fixed price for defined scope | Confirm scope matches |
| "Budget pricing" | Not a firm bid — estimate only | Cannot award on budget price |

## Trade-Specific Evaluation Notes

### Concrete (Div 03)
- Pump inclusion vs. exclusion (significant cost)
- Winter protection / hot water / heated enclosures
- Vapor retarder under SOG — who provides?
- FF/FL tolerances: higher = more cost
- Rebar placement vs. detailing (fabricator vs. placer)

### Steel (Div 05)
- Fabrication vs. erection — same sub or split?
- Connection design: EOR-designed or delegated to fabricator?
- Misc metals: often excluded from structural steel bid
- Shop primer vs. field paint vs. fireproofing prep

### Finishes (Div 09)
- Drywall: acoustic sealant, fire tape, STC walls — often excluded
- Flooring: subfloor prep, moisture testing, transition strips
- Tile: waterproofing membrane, cement board, schluter profiles
- ACT ceilings: seismic bracing, light fixture support clips

### MEP (Div 21-28)
- Controls wiring: mech controls sub vs. electrician
- Startup / commissioning: often excluded from install bid
- Test & balance: separate sub or included?
- Permits: who pulls? Some jurisdictions require licensed sub
- Temporary utilities during construction

### Sitework (Div 31-33)
- Rock excavation: excluded unless specifically priced
- Dewatering: often excluded
- Import/export of fill: hauling costs volatile
- Winter conditions: frozen ground, snow removal

## Common Scope Splits (GC vs. Sub)

| Item | Typically GC | Typically Sub |
|------|-------------|---------------|
| Cutting & patching | GC or affected trade | N/A |
| Backing & blocking | GC (rough carpentry) | Sometimes drywall sub |
| Temporary protection | GC | Sub for their own work |
| Hoisting / crane time | GC | Heavy trades (steel, MEP) |
| Dumpsters / debris removal | GC (general cleanup) | Sub (own debris) |
| Layout / surveying | GC | Sub for their own work |
| Permits | GC (building permit) | Sub (trade-specific) |
| Bonds | GC | Sub if required by GC |

## Red Flag Patterns

### Bust Detection (proceed with caution — never call it a "bust")
- Base bid >20-30% below field average
- Multiple scope exclusions on spec-required items
- Incomplete submission (missing alternates, unit prices, schedule)
- No addenda acknowledgment
- Bid validity expired or very short (< 30 days)
- **Action:** Flag for verification, request clarification, compare line items

### Qualification-Heavy Bids
- >5 qualifications = sub is hedging
- "Subject to field verification" on quantity items = potential change order exposure
- "Owner to provide access" type conditions = schedule risk

### Other Red Flags
- No bond on bonded project
- Insurance limits below project requirements
- License expired or wrong jurisdiction
- Bid references wrong project name or drawing date
- Math errors in bid (line items don't sum to total)
- "Verbal" pricing or handwritten changes without initials

## Non-Price Factors

Assess per bidder where information is available:

| Factor | What to Check |
|--------|--------------|
| Bonding capacity | Can they bond this project + their backlog? |
| Insurance limits | Meet project requirements (GL, auto, umbrella, workers comp)? |
| Licensing | Current in project jurisdiction? Correct classification? |
| Experience | Similar projects in size, type, complexity? |
| Capacity | Current workload — can they staff this project? |
| DBE/MBE | Meets project participation goals? |
| References | Recent, relevant, checkable? |
| Safety record | EMR < 1.0? OSHA citations? |
| Past performance | Prior work with this GC? Quality, schedule, change orders? |
| Financial stability | Years in business, D&B rating if available? |

## Price Normalization

When adjusting bids for comparison:
```
Adjusted Base = Submitted Base
              + Value of excluded spec-required items
              - Value of included GC-provided items
              + Accepted alternates
              ± Allowance adjustments
```

**Valuation order for excluded items:**
1. Another bidder's line item price for same work (best)
2. Budget estimate or quantity × unit rate
3. Professional judgment (flag as estimated)
4. Qualitative risk note if truly unknown

**Document every adjustment.** No silent price changes.
