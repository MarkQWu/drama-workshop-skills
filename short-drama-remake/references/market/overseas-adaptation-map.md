---
schema_version: remake.market.overseas_adaptation_map.v0
read_when: /仿写 出海 and market_adapt.validate
status: active_scaffold
---

# Overseas Adaptation Map

Purpose: map reference-drama story functions into overseas-market equivalents.

This file defines the minimum remake-native mapping contract for overseas adaptation. It is intentionally category-level; do not import original `short-drama` overseas reference files.

## Mapping Contract

Overseas concept directions must be adapted before project planning. Do not generate domestic-facing skin-swap concepts and translate them later.

Every overseas-adapted concept should include:

| Field | Meaning |
|---|---|
| `target_market` | The intended overseas market, platform, or audience assumption. |
| `layer_classification` | The `layer-taxonomy.md` layer affected by the concept decision. |
| `overseas_genre_promise` | The overseas-native genre/audience promise. |
| `relationship_grammar` | The relationship, agency, consent, and power grammar used by the concept. |
| `status_or_power_system` | The target-market-native power/status mechanism. |
| `source_mechanisms_to_replace` | Domestic/source-market mechanics that must not carry over. |
| `paywall_pressure` | How the concept creates paid-episode pressure for the target market. |
| `similarity_risk_note` | Why this direction is not just the reference with translated labels. |

Every overseas adaptation report should separate:

| Field | Meaning |
|---|---|
| `layer_classification` | Which remake market layer the mapping decision affects. |
| `reference_function` | What the original beat does for the viewer. |
| `source_market_mechanism` | The domestic or source-market surface mechanism. |
| `target_market_replacement` | The overseas-native mechanism that performs the same function. |
| `must_not_carry_over` | Surface items that would create market mismatch or similarity risk. |
| `distance_check` | Why this is not a renamed copy. |

## Required Mapping Areas

Every market adaptation report must cover these mappings when applicable:

1. **Status and power systems**: source hierarchy, wealth, office, school, clan, family, or legal power -> target-market-native status/power mechanism.
2. **Public proof scenes**: source slap, humiliation, reveal, crowd witness, test result, contract, or family proof -> target-market proof mechanism that is legible without domestic context.
3. **Family secrets and identity mechanics**: source bloodline, household, adoption, pregnancy, inheritance, or mistaken identity -> target-market equivalent with IP distance.
4. **Paywall pressure**: source paid cliffhanger function -> target-market reason to continue, such as relationship choice, identity reveal, danger escalation, debt, oath, or betrayal.
5. **Romance, danger, and agency grammar**: source coercion / pursuit / grovel / protection function -> target-market relationship grammar with agency and consent boundary named.
6. **Vertical filmability**: source crowd/wide/action spectacle -> phone-screen readable visual anchor, single-subject action, or consequence/reaction beat.
