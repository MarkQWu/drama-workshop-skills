---
schema_version: remake.three_layer_control.v1
read_when: every remake stage that classifies constraints, builds skeletons, drafts scripts, or reviews candidate episodes
---

# Three-Layer Control Model

Use this model to decide which remake constraints are hard gates and which are creative guidance.

Core rule: **control strength must match collapse risk**. If a violation can collapse the project, block it. If a violation only weakens rhythm or clarity, constrain the node. If a choice belongs to texture, protect freedom and review only the lowest-risk boundaries.

## Layer 1: Foundation, 100% Controlled

Foundation rules protect legality, source truth, continuity, and project state. They have zero creative freedom because failure can collapse the whole remake project.

### Lock

- Source scope: `complete`, `partial`, `incomplete`, or `unknown`; partial sources never unlock full-series claims.
- Source market and target market: domestic, overseas, or unknown. Cross-market remakes require an accepted market adaptation report before planning or scripting.
- Copyright and similarity boundaries: no copied expression, names, dialogue, scene specifics, protected surface event sequences, or direct reference mechanics.
- Canon and state: accepted artifacts, current pointers, transaction records, project state, and user-confirmed canon.
- Character core: identity, motivation, relationship logic, core power position, ability/resource boundary, and accepted voice constraints.
- World and production facts: world rules, professional facts, project-specific constraints, accepted setting bible, and fact gate treatment.
- Platform and format hard limits: compliance, required screenplay format, language mode, forbidden read paths, and source/report freshness.
- Full-series memory: committed events, promises, unresolved hooks, payoff nodes, relationship changes, and explicit recovery obligations.

### Block When

- A downstream stage claims more source coverage than the ingested source allows.
- A script node reads forbidden raw source, legacy review, research notes, drafts, candidates, or unrelated `short-drama` references.
- A candidate depends on stale or missing SIR/RMR/FGR/preflight/postflight reports.
- A draft changes accepted character core, world rules, canon, or committed relationship state without a user decision.
- A remake keeps protected surface expression instead of only preserving story function.

### Required Artifacts

- `manifest.yaml`
- `00_source/source-index.json`
- `01_skeleton/reference-skeleton.md`
- `01_skeleton/reference-expression-guide.md`
- `01_skeleton/factor-scorecard.yaml`
- `02_concepts/market-adaptation-report.md` when target market is overseas or differs from source market
- `03_plan/project-bible.md` or equivalent accepted project plan
- `04_outlines/episodes/epXXX.execution-card.md`
- `06_state/project-state.md`
- `06_state/artifact-registry.yaml`
- required accepted reports: SIR, RMR, FGR, preflight, postflight, similarity risk

## Layer 2: Skeleton, 60% Controlled

Skeleton rules protect the dramatic job of the remake. They lock function, sequence, and reader expectation, but leave implementation open.

Principle: **lock the node, free the method**.

### Lock

- Episode function: what this episode must do in the viewing chain.
- Pressure source: who/what creates pressure and why the protagonist cannot ignore it.
- Viewer emotion: what the audience should feel at the main beat.
- Hook function: what exact question or unfinished action pulls the next episode.
- Reveal and misdirection timing: when the reference creates false safety, delayed recognition, proof, reversal, or payoff.
- Payoff/foreshadowing obligations: which promise is planted or collected.
- Remake distance: which reference surface elements must be replaced before scripting.
- Target-market function mapping: which story functions transfer, and which market-specific mechanisms must change.

### Free

- Venue, scene mechanics, props, evidence devices, profession, family-secret mechanism, ceremony type, proof object, and visual business.
- Concrete conflict choreography, joke/tension delivery, emotional buildup method, scene order between locked beats, and dialogue choices.
- Genre-native replacements, as long as they perform the same story function and increase surface distance.

### Skeleton Table Contract

Every reusable skeleton table must separate locked function from free implementation:

| Field | Meaning |
|---|---|
| `locked_episode_function` | The dramatic job that must be preserved. |
| `locked_viewer_emotion` | The intended audience emotion at the key beat. |
| `locked_hook_function` | The continuation question/action that must survive. |
| `locked_payoff_or_setup` | What is planted, escalated, or paid off. |
| `must_replace_surface` | Reference specifics that cannot be reused. |
| `free_implementation_zone` | Scene, prop, action, dialogue, and rhythm choices left open. |
| `distance_test` | One sentence proving this is not a renamed copy. |

### Execution Card Contract

Each execution card must include:

- `locked_story_job`
- `locked_entry_pressure`
- `locked_turning_point`
- `locked_exit_hook`
- `free_scene_options`
- `free_dialogue_options`
- `surface_replacement_notes`

If an execution card specifies exact dialogue, exact prop, exact venue, and exact scene mechanics all at once, downgrade those items to options unless they are foundation facts. Over-specified skeleton cards are a regression.

## Layer 3: Flesh, 20% Controlled

Flesh rules protect memorability, character texture, and surprise. This layer should not be preflight-blocked unless it violates foundation or skeleton rules.

### Keep Free

- The concrete wording of dialogue.
- Micro-actions, emotional pauses, reaction details, sensory choices, sentence rhythm, and scene texture.
- How a beat becomes funny, painful, romantic, humiliating, suspenseful, or cathartic.
- The exact way a character avoids saying the obvious.
- The memorable image, line, or silence that makes the episode feel authored.

### Review Lightly

- Does the scene violate accepted character core?
- Does the expression copy the reference too closely?
- Is the language obviously generic AI filler?
- Does the episode still land its locked story job?
- What is the one concrete moment a viewer can remember?

### Do Not

- Do not turn dialogue style, sentence length, sensory expression, or micro-action choice into preflight hard gates.
- Do not require a fixed number of metaphors, pauses, adjectives, emotional labels, or camera beats.
- Do not block a draft for having a different texture from the reference when the locked story function still lands.
- Do not let a checklist claim creative quality unless it can name a concrete memorable moment.

## Stage Mapping

| Stage | Foundation | Skeleton | Flesh |
|---|---|---|---|
| Ingest | source scope, evidence, file map | available episode/function coverage | none |
| Skeleton | source-true claims, no copied expression | locked function table | expression guide only as avoidance notes |
| Concepts | no full claim from partial source, no protected copy | concept preserves function and hook pattern | genre-native invention is free |
| Project plan | accepted world, character core, production facts | long arc and payoff obligations | tone and texture are directional only |
| Episode outline | accepted execution card inputs | entry pressure, turn, exit hook | scene options stay open |
| Script draft | preflight blocks only foundation/skeleton failures | write to the locked story job | dialogue/action/sensory realization is free |
| Review/postflight | no canon commit without user acceptance | confirm the episode landed its function | name the memorable moment; suggest edits, do not over-gate |

## Report Policy

- Preflight may block on Foundation and Skeleton failures only.
- Preflight may warn on Flesh concerns, but must not block solely for style, taste, sentence rhythm, or lack of polish.
- Postflight may mark `needs_revision` when Flesh is weak, but the reason must cite a concrete scene, line, or missing memorable moment.
- `quality_gate_status=passed` means process quality passed. It does not by itself mean the episode has creative force.
