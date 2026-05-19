---
schema_version: remake.market.overseas_risk_gate.v0
read_when: market_adaptation_report and script_draft.preflight when target_market is overseas
status: active_scaffold
---

# Overseas Risk Gate

Purpose: define which overseas adaptation issues block planning or script drafting.

This file is a remake-native gate scaffold. Do not use it to over-gate Flesh-layer choices, and do not import original `short-drama` overseas hard gates directly.

## Gate Shape

Block only when the issue is Foundation or Skeleton level:

- Target market is missing or contradictory.
- Source-market mechanism is carried into the overseas version without adaptation.
- Protected expression or direct surface event sequence is retained.
- The adaptation report is missing, stale, or not based on the selected concept.
- A declared target-market hard rule is violated.
- R0-R5 fields are missing from `market_adaptation_report`.
- The report names a target-market replacement but does not explain the reference function it replaces.
- The distance check only changes labels while keeping the same scene sequence, reveal order, or signature line/visual motif.

Do not block solely for weak dialogue texture, bland sensory detail, or style preferences. Those belong in review/postflight.

Use `layer-taxonomy.md` for the causal classification:

- R1-R5 may block planning or drafting when missing, stale, contradictory, or unsupported.
- R6 is script flesh and should route to review/postflight unless it reveals a higher-layer failure.
