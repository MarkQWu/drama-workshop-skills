---
schema_version: remake.market.layer_taxonomy.v0
read_when: /仿写 出海, concept.generate, market_adapt.validate, project_plan.prepare, and script_draft.preflight when target_market is overseas or differs from source_market
status: active
---

# Remake Target-Market Layer Taxonomy

Purpose: classify market-adaptation evidence and decisions for `short-drama-remake` without importing `short-drama/references/overseas/*` directly.

## Classification Principle

Remake adaptation starts from reference-story function, not from either market's surface mechanics. A source beat is portable only after the target-market layer has identified what the beat does for the viewer and which target-market mechanism can perform the same job with enough distance.

## Layers

| Layer | Name | Causal job | Artifact field |
|---|---|---|---|
| R0 | Source Truth | What the reference actually does; prevents hallucinated skeletons | `reference_function` |
| R1 | Target Market Assumption | Which market/platform/audience the remake is adapting toward | `target_market` |
| R2 | Market Non-Transferables | Source-market mechanisms that cannot carry over | `source_mechanisms_to_replace`, `must_not_carry_over` |
| R3 | Target-Market Replacement | Native status, relationship, proof, law, family, or power mechanism that performs the same job | `target_market_replacement`, `status_or_power_system` |
| R4 | Genre Promise & Paid Pressure | Viewer-facing promise and paywall pressure after adaptation | `overseas_genre_promise`, `paywall_pressure` |
| R5 | Similarity Distance | Evidence that the result is not a renamed copy | `distance_check`, `similarity_risk_note` |
| R6 | Script Flesh | Dialogue, scene texture, micro-action, sensory expression | postflight/review only unless it violates R1-R5 |

## Gate Policy

- `/仿写 出海` without a selected concept generates overseas-adapted concepts classified through R1-R5.
- `/仿写 出海 [方向编号]` creates or refreshes `market-adaptation-report.md` and must fill R0-R5.
- `/仿写 定案` and `/仿写 写集` must block when R1-R5 are missing, stale, contradictory, or not based on the selected concept.
- R6 issues must not block body generation by themselves. They belong to review/postflight unless they reveal a higher-layer failure.

## Market Source Card

Any market material promoted into remake adaptation should carry:

| Field | Meaning |
|---|---|
| `source_id` | Stable local ID for the market claim or evidence cluster |
| `target_market` | Market/platform/audience boundary |
| `layer` | R0-R6 layer affected |
| `applies_to_node` | `concept.generate`, `market_adapt.validate`, `project_plan.prepare`, or `script_draft.preflight` |
| `allowed_use` | The adaptation decision this evidence may support |
| `forbidden_use` | The decision it may not support |
| `evidence_level` | HIGH / MED / LOW / UNVERIFIED |
| `freshness` | Source date and next review date |
| `fixture_required` | Whether promotion to gate behavior requires a deterministic fixture |

LOW or UNVERIFIED material may support brainstorming, but cannot create a new blocker until it is re-sourced and covered by fixture expectations.

## Isolation Rule

Do not directly read or import `short-drama/references/overseas/*` inside remake nodes. If a rule from original overseas mode is useful, re-express it here as a target-market adaptation category with the causal layer named.
