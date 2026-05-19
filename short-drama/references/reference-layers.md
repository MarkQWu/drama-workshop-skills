# Reference Layers

> Phase 4 first-pass classification. This file does not move or rename any
> reference. It only gives maintainers one place to see each document's primary
> layer before metadata and hard-gate refactors.

## Layer Definitions

| Layer | Purpose | Hard-gate bias |
|---|---|---|
| `foundation` | Runtime safety, state, release/update, compliance, research truth, output contract | Can contain blocking rules when evidence is objective |
| `structure` | Story architecture, genre positioning, hooks, paywall, rhythm, character function | Usually soft-to-hard depending on command and evidence |
| `craft` | Line-level and scene-level writing craft, polish, realism, quality rubric | Mostly soft rubric unless it triggers OOC, unfilmable output, format failure, or factual contradiction |
| `modes` | Medium, market, or command-mode specific overlays | Can override baseline rules only inside its declared mode |
| `templates` | Reusable output formats, forms, prompt skeletons, and project artifacts | Contractual for formatting, non-authoritative for method |

Chinese control names:

- `foundation` = 地基层
- `structure` = 骨架层
- `craft` = 血肉层
- `modes` = 模式覆盖层
- `templates` = 输出契约层

## Classification

### Foundation

| Reference | Primary role |
|---|---|
| `compliance-checklist.md` | Content safety and platform red lines |
| `format-control.md` | Command-level output and script format contract |
| `project-management.md` | Project state schema, active project routing, write safety |
| `research-fallback.md` | Research fallback behavior when search/tools are unavailable |
| `research-guide.md` | Research workflow and factual grounding |
| `three-layer-control.md` | Original-story control boundary: foundation 100%, structure 75%, craft 35%; decides whether a problem blocks, repairs structure, or stays advisory |
| `update-mechanism.md` | `/更新` behavior and repository-level update policy |
| `used-lines-protocol.md` | Reuse prevention and line-level continuity hygiene |

### Structure

| Reference | Primary role |
|---|---|
| `anchor-library.md` | Genre anchor examples and emotional reference pool |
| `anchor-trigger.md` | Anchor activation logic for planning and episodes |
| `commercial-ledger-cn.md` | Domestic commercial ledger for viewer-buy reason, paid hook pressure, payoff delivery, and villain escalation |
| `creative-intent-ledger.md` | `control=creative_guidance`; original premise, core relationship, satisfaction engine, ending preference, and non-negotiables |
| `genre-guide.md` | Genre taxonomy, audience fit, and configuration choices |
| `hook-design.md` | Episode-ending hook types and placement strategy |
| `opening-rules.md` | Opening structure and first-episode entry patterns |
| `paywall-design.md` | Paid-episode pressure and cliffhanger architecture |
| `plot-types.md` | Plot type selection and structural archetypes |
| `rhythm-curve.md` | Episode and full-series pacing shape |
| `satisfaction-matrix.md` | Audience payoff mapping |
| `short-dynasties.md` | Dynasty/setting shorthand for structure and premise work |
| `villain-design.md` | Antagonist function, pressure, and escalation design |

### Craft

| Reference | Primary role |
|---|---|
| `dramatic-truth.md` | Dialogue truth, anti-trailer-speak, and polish audit |
| `dialogue-craft-cn.md` | Chinese dialogue voice fingerprint, subtext, deletion-first fixes |
| `quality-rubric.md` | `control=soft_rubric + commercial_vitality_rubric + anti_greenlight`; hard-gate overlay only for OOC, compliance, unfilmable output, medium mismatch, or factual contradiction |
| `quality-rules.md` | Quality constraints and recurring failure patterns |
| `realism-checklist.md` | Plausibility, causality, and grounded behavior checks |
| `roundtable-figures.md` | Character voice and roundtable reference figures |
| `script-element-extraction.md` | Dialogue, scene, insert, shot, and parenthetical extraction pipeline |
| `vertical-drama-craft.md` | Vertical-drama line, scene, and information-density craft |

### Modes

| Reference | Primary role |
|---|---|
| `ai-live-rules.md` | `medium=ai_live` production constraints |
| `comic-rules.md` | `medium=comic` production constraints |
| `imitation-protocol.md` | `/仿写` compatibility and reference adaptation flow |
| `storyboard-guide.md` | Storyboard and video prompt generation guide |
| `storyboard-rules.md` | Storyboard command constraints and checks |
| `overseas/anti-patterns.md` | Overseas mode failure patterns |
| `overseas/anti-domestic-transfer.md` | Domestic-market carryover and failed transfer patterns |
| `overseas/anti-structure-import.md` | Feature-film and domestic-structure vocabulary pollution |
| `overseas/compliance-risk.md` | Overseas legal, IP, cultural, and similarity risk separated from domestic compliance |
| `overseas/dialogue-craft.md` | Overseas dialogue craft and platform conventions |
| `overseas/dialogue-exemplar-risk.md` | Long-form / prestige exemplar use boundaries and contamination risks |
| `overseas/dialogue-platform.md` | Overseas vertical-platform native dialogue rules |
| `overseas/hard-rules.md` | Overseas mode non-negotiable constraints |
| `overseas/layer-index.md` | Overseas reference taxonomy and causal placement rules |
| `overseas/platform-knowledge.md` | Overseas platform and market reference |
| `overseas/vertical-filmability.md` | 9:16 phone-screen filmability and readability anti-patterns |

### Templates

| Reference | Primary role |
|---|---|
| `brainstorm.md` | Isomorphic story ideation skeleton |
| `output-templates-core.md` / `output-templates-aux.md` | User-facing command output templates and `/帮助` source |
| `setting-bible-template.md` | Setting bible artifact template |

## Non-Markdown Utility In References

| Path | Current status | Phase 4 note |
|---|---|---|
| `condense-source.py` | Utility script stored under `references/` | Needs a later ownership decision: move to `scripts/`, declare as allowed reference utility, or retire |

## Hard-Gate Metadata Coverage

These references now carry explicit metadata fields:
`layer`, `control`, `authority_id`, `canonical_path`, and `read_when`.

| Reference | Control | Read when |
|---|---|---|
| `format-control.md` | `hard_gate` | Every command before output generation |
| `project-management.md` | `hard_gate` | `/开始`, `/新建`, `/分集`, `/自检`, and any command that reads or writes project state |
| `compliance-checklist.md` | `hard_gate` | `/自检`, `/导出`, and publishability/platform risk checks |
| `research-guide.md` | `hard_gate` | `/考据` and thick-topic script generation that relies on domain facts |
| `research-fallback.md` | `hard_gate` | `/考据 auto` when WebSearch, WebFetch, PDF, or source access fails |
| `three-layer-control.md` | `control_model` | `/策划`, `/角色开发`, `/考据`, `/分集目录`, `/分集`, `/自检`, `/圆桌诊断`, `/角色一致性`, `/导出`, `/分镜`, and any blocking decision |
| `update-mechanism.md` | `hard_gate` | Every skill activation update check and explicit `/更新` command |
| `ai-live-rules.md` | `hard_gate` | `medium=ai_live` or missing medium |
| `comic-rules.md` | `hard_gate` | `medium=comic` |
| `overseas/hard-rules.md` | `hard_gate` | `mode=overseas` before `/开始`, `/分集`, and `/自检` |
| `overseas/compliance-risk.md` | `hard_gate` | `mode=overseas` before `/开始`, `/分集`, `/自检`, `/合规`, and `/导出` |
| `overseas/layer-index.md` | `reference_architecture` | `mode=overseas` before selecting overseas references or classifying new material |
| `overseas/anti-domestic-transfer.md` | `review_gate` | `mode=overseas` before `/开始`, `/分集`, `/自检`, and domestic-carryover diagnosis |
| `overseas/anti-structure-import.md` | `hard_gate` | `mode=overseas` before reviewing outlines, beat sheets, structural documents, and reference imports |
| `overseas/vertical-filmability.md` | `mixed_gate` | `mode=overseas` before `/分集`, `/自检`, scene polish, and production feasibility review |

## Control Boundary

### Hard Gates

Hard gates block continuation, export, delivery, or publishability advice when evidence is objective. They must include evidence, next owner, and the smallest repair action.

| Control | References | Blocks when |
|---|---|---|
| Format and output contract | `format-control.md` | Output violates command format, dialogue rules, export structure, or medium contract |
| Project state and write safety | `project-management.md` | Command would read/write the wrong project, overwrite state, or corrupt project progress |
| Compliance and platform risk | `compliance-checklist.md` | Content crosses legal, platform, or publishability red lines |
| Research and factual traceability | `research-guide.md`, `research-fallback.md` | Thick or medium-weight topics rely on fabricated, untraceable, or contradicted facts |
| Three-layer control boundary | `three-layer-control.md` | A command misclassifies a foundation, structure, or craft problem and would either under-block collapse risk or over-block creative texture |
| Medium and market hard rules | `ai-live-rules.md`, `comic-rules.md`, `overseas/hard-rules.md` | Script is unfilmable, medium-mismatched, or violates declared market constraints |
| Release/update behavior | `update-mechanism.md` | `/更新` or startup update checks point to the wrong repo or split authority |

### Original Three-Layer Control Strength

The original-story skill uses control strength, not score weight:

| Layer | Control strength | Execution rule |
|---|---:|---|
| Foundation / 地基层 | 100% | Objective collapse risks block continuation, export, delivery, or publishability advice. |
| Structure / 骨架层 | 75% | Lock the story job, pressure, payoff, rhythm, and hook; do not lock surface implementation. |
| Craft / 血肉层 | 35% | Score, diagnose, and revise line/scene texture; do not block solely for style unless it crosses foundation or structure. |

### Soft Rubrics

Soft rubrics diagnose quality and prioritize revision. They do not block by themselves unless they cross a hard-gate boundary.

| Control | References | Use for |
|---|---|---|
| Commercial vitality score | `quality-rubric.md` | Rhythm, satisfaction, dialogue, mainline continuity, AI Slop, research score |
| Craft polish | `dramatic-truth.md`, `quality-rules.md`, `realism-checklist.md`, `vertical-drama-craft.md` | Dialogue truth, grounded behavior, line density, scene polish |
| Structural strength | `hook-design.md`, `opening-rules.md`, `paywall-design.md`, `rhythm-curve.md`, `satisfaction-matrix.md`, `villain-design.md` | Hook strength, paid pressure, escalation, payoff mapping |

### Creative Guidance

Creative guidance preserves intent and improves taste. It should steer choices, not masquerade as objective failure.

| Control | References | Use for |
|---|---|---|
| Original intent | `creative-intent-ledger.md` | Preserve original premise, core relationship, satisfaction engine, ending preference, and non-negotiables |
| Genre and anchor imagination | `genre-guide.md`, `anchor-library.md`, `anchor-trigger.md`, `plot-types.md`, `short-dynasties.md` | Select genre fit, emotional anchors, story archetypes, and world shorthand |
| Character and voice references | `roundtable-figures.md` | Improve voice and perspective without creating hard constraints |

### Template Contracts

Template contracts are strict about output shape and loose about creative method.

| Control | References | Use for |
|---|---|---|
| User-facing command templates | `output-templates-core.md` / `output-templates-aux.md` | Keep `/帮助`, command output, and generated project documents consistent |
| Project artifact templates | `brainstorm.md`, `setting-bible-template.md` | Preserve expected sections while allowing content variation |
| Extraction contracts | `script-element-extraction.md`, `storyboard-guide.md`, `storyboard-rules.md` | Keep downstream script parsing and storyboard handoff stable |

## Next Metadata Pass

The next Phase 4 pass should add per-document metadata to hard-gate candidates:

```yaml
layer: foundation|structure|craft|modes|templates
control: hard_gate|control_model|soft_rubric|creative_guidance|template_contract
authority_id: short-drama.<stable-id>
canonical_path: references/<path>
read_when: <command or condition>
```
