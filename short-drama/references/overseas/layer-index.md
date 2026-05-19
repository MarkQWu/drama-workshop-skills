---
layer: modes
control: reference_architecture
authority_id: short-drama.overseas-layer-index
canonical_path: references/overseas/layer-index.md
read_when: mode is overseas before selecting overseas references or classifying new material
---

# Overseas Reference Layer Index

Purpose: classify overseas-mode references by market-causal role so future material can be screened, placed, and used without mixing platform facts, genre promise, relationship grammar, structure, format, craft polish, compliance, and anti-pollution rules.

## Classification Principle

Classify a reference by the problem it causally controls:

- If the rule decides whether a project can survive the target market, legal/IP risk, or declared platform mode, it belongs to a hard-gate layer.
- If the rule decides what story promise, pressure engine, episode function, or paywall logic the audience is buying, it belongs to a skeleton layer.
- If the rule improves line texture, voice, sensory detail, rhythm, or style after the project is viable, it belongs to a flesh layer.
- If the item is evidence, market data, or a source claim, it must carry confidence and freshness before any downstream rule may depend on it.

Do not classify by file name, source prestige, or whether the rule sounds important. Classify by what breaks when it is wrong.

## Layers

| Layer | Name | Causal job | Control | Typical files |
|---|---|---|---|---|
| L0 | Source Confidence & Freshness | Determines whether a market claim may be trusted or must be re-checked | evidence gate | `platform-knowledge.md` |
| L1 | Target Market & Platform | Determines who watches, where they watch, and how the episode is paid for | hard gate for declared mode; soft when claim confidence is MED/LOW | `platform-knowledge.md` |
| L2 | Genre Promise & Audience Buy | Defines what the viewer thinks they are buying: billionaire, mafia, werewolf, revenge, secret baby, dark romance | skeleton constraint | `genre-guide.md`, `platform-knowledge.md`, `roundtable-figures.md` |
| L3 | Relationship, Power & Moral Grammar | Explains why a beat works or fails in the target market: consent, agency, grovel, honor, inheritance, territory, oath, violence calibration | hard gate when violation breaks target-market viability | `hard-rules.md`, `anti-domestic-transfer.md`, `compliance-risk.md` |
| L4 | Story Structure & Paid Pressure | Episode job, opening pressure, reveal/reversal/cliffhanger function, relationship choice, paywall pressure | skeleton constraint; hard gate only when missing blocks continuation | `hard-rules.md`, `anti-structure-import.md`, `platform-knowledge.md` |
| L5 | Medium & Filmability | 9:16 phone-screen physics, visual anchor, single-subject action, caption legibility, wordless stretch | mixed gate: hard only for unfilmable or unreadable output; otherwise craft guidance | `vertical-filmability.md`, `platform-knowledge.md`, `output-templates.md` |
| L6 | Dialogue, Voice & Language Craft | Caption-readable line, trope-forward wording, VO boundary, character voice, subtext/opacity, short-line polish | soft rubric unless it violates L1/L3/L5 | `dialogue-platform.md`, `dialogue-craft.md`, `dialogue-exemplar-risk.md`, `roundtable-figures.md` |
| L7 | Compliance, IP & Similarity Risk | Determines whether the project can be delivered without IP, likeness, brand, legal, cultural, or protected-expression exposure | hard gate | `compliance-risk.md`, `hard-rules.md` |
| L8 | Anti-Pollution & Transfer Bans | Blocks domestic carryover, failed genre transfers, forbidden terminology, and known bad patterns | review gate by default; hard gate only when pollution becomes L1/L3/L7 failure | `anti-patterns.md`, `anti-domestic-transfer.md`, `anti-structure-import.md`, `hard-rules.md` |
| L9 | Templates & Execution Contracts | Defines output shape, command artifacts, export schema, and state fields | format contract only; never method authority | `format-control.md`, `output-templates.md` |

## Placement Rules For New Material

1. **Platform fact first**: any claim about runtime, paywall, monetization, ranking, platform format, or market share goes to L0/L1 and must carry source, date, and confidence.
2. **Target market before genre**: any "overseas" claim must name a market, platform, or audience assumption before it becomes a genre rule.
3. **Genre promise before plot**: classify the viewer's paid promise before selecting episode structure.
4. **Relationship grammar before surface events**: consent, agency, power, moral choice, and violence calibration decide whether the same beat can transfer.
5. **Function before surface**: any adaptation note must name the viewer function before the new surface mechanism.
6. **Structure before texture**: episode function, paywall pressure, and relationship turn go to L4; exact line style and sensory expression go to L6.
7. **Format is not craft**: screenplay markers, scene headings, dialogue quotation, captions, and export shape go to L9 even when they affect readability.
8. **Maintenance stays local**: agent error retrospectives, symlink notes, release-process lessons, and private planning do not belong in runtime references unless they directly change user-visible skill behavior.

## Source Card Standard

Any new overseas reference claim that may influence a hard gate or skeleton decision should be captured with:

| Field | Meaning |
|---|---|
| `source_id` | Stable local ID for the claim or source cluster |
| `target_market` | Market/platform/audience boundary |
| `layer` | L0-L9 layer from this index |
| `control` | `evidence`, `hard_gate`, `skeleton_constraint`, `soft_rubric`, or `template_contract` |
| `allowed_use` | What decisions may rely on this claim |
| `forbidden_use` | What decisions must not rely on this claim |
| `evidence_level` | HIGH / MED / LOW / UNVERIFIED |
| `freshness` | Source date and next review date |
| `fixture_required` | Whether a deterministic fixture must exist before promotion to hard gate |

No claim may become a new hard gate if `evidence_level` is LOW/UNVERIFIED or `fixture_required` is true but no fixture exists.

## Conflict Resolution

When two references disagree:

1. Higher causal layer wins over lower causal layer: L1/L3/L5/L7/L8 can override L6.
2. More recent audited platform fact wins over older unverified claim inside the same layer.
3. Hard-gate rule wins only inside its declared layer; it may not police flesh-level choices.
4. Imported frameworks such as Gwen Hayes, Save the Cat, McKee, or Mamet are scaffolds. They never override platform mechanics or target-market cultural grammar.
5. `short-drama-remake` must not directly read this file at runtime. Remake uses its own target-market taxonomy and adaptation report contract.
