---
layer: modes
control: hard_gate
authority_id: short-drama.overseas-hard-rules
canonical_path: references/overseas/hard-rules.md
read_when: mode is overseas before /开始, /分集, and /自检
---

# Hard Rules — Overseas Hard Gate Matrix

> Only **HARD BLOCK** items create `violation=must rewrite`.
> **REVIEW** items create a human-review flag and cannot be the sole basis for must-rewrite.
> **STRONG GUIDANCE** items are craft constraints; treat misses as revision notes unless they also trigger a HARD BLOCK.
> Source: B6 failure cases + B5 mafia craft expert + C2 recommendations, reclassified into gate severity.
> Read before /开始, /分集, /自检.
>
> **v1.20.0 适用范围说明**：domestic mode 的「Ep1 设计卡 / 首集冷开场硬合同 / 有效爽点判定 / 事件钩首集硬约束 / 首集传播句」**不强制套用到 overseas mode**——overseas 首集规则按本文件 + `anti-patterns.md`（mafia romance / dubcon timing / paywall × beat 对齐等海外 craft 体系）。如需把 v1.20.0 个别规则迁过来，需独立做 overseas 校准（mafia romance hard rules vs domestic 战神归来 hard rules 不可互换）。

## Severity Definitions

- **HARD BLOCK**: Cannot ship in overseas mode. Rewrite content before continuing, unless explicitly labeled as an export/process stop.
- **REVIEW**: Must be surfaced to a human editor or project owner. Rewrite only if the review confirms target-market, legal, or relationship-grammar failure.
- **STRONG GUIDANCE**: Craft preference or diagnostic heuristic. Use to improve the draft, not as an automatic fail state.

---

## HARD BLOCK Gates

### HB1: Target Market Cannot Be Missing

An overseas project must name a target market, platform, or audience assumption before genre rules are applied.

Block when:
- The brief only says "overseas" with no market/platform/audience assumption.
- A scene depends on an unstated audience norm while also using coercion, intimacy, violence, legal stakes, or protected-identity material.
- The target market changes mid-project without rechecking consent, violence, IP, and cultural assumptions.

### HB2: No Traceable IP or Real-Person Likeness

Script, character design, naming, and persona must not be traceable to existing English mafia IP, recognizable fictional families, real actors, public figures, or platform-protected likenesses.

Block when:
- Character names, family names, taglines, visual designs, or signature plot devices can reasonably be traced to existing IP or a real person.
- The draft uses near-neighbor substitutions that preserve recognizability.
- Brand, family, or location elements are presented as real-world protected marks without clearance.

### HB3: No Domestic Mechanism Transplanted as Target-Market Logic

Chinese/domestic mechanisms cannot carry the core conflict unless they are remapped into the declared target market's power grammar.

Block when:
- The male lead's power depends on audience understanding 入赘, bloodline purity, domestic class humiliation, household registration, local school/workplace hierarchy, or similar China-specific status systems.
- A domestic legal, family, medical, workplace, school, or status mechanism is used as if the target audience already shares that context.
- The beat is a direct translation of a known Chinese short-drama device and the overseas version adds no target-market equivalent.

Allowed remaps:
- inheritance rights
- territory control
- honor debt
- family oath
- cartel/mafia chain of command
- trust, estate, or contract stakes legible in the named market

### HB4: Consent Breach and Chemical-Consent Substitution

Intimacy must be legible as relationship grammar for the declared target market. Coercion may exist in dark romance only when the story preserves choice, cost, and payoff; substances cannot replace consent escalation.

Block when:
- Aphrodisiacs, cold-medicine mix-ups, intoxication, magic potions, hypnosis, or any external substance causes intimacy or substitutes for consent.
- The female lead has no authored choice before major intimacy escalation.
- A coercive setup is played as romance without later consent clarification, cost, or reversal.
- The scene violates the declared target-market relationship grammar in `compliance-risk.md`.

### HB5: Violence Calibration Breach

The male lead cannot author violence downward against protected or innocent targets.

Block when:
- He kills, tortures, sexually assaults, threatens, or deliberately harms civilians, children, innocent bystanders, or the female lead as a romantic beat.
- Violence against women is used as proof of his desirability or dominance rather than an explicitly condemned villain action.
- The script asks the audience to eroticize helpless victimization without agency, reversal, or protection.

Allowed dark-romance violence remains outward and narratively accountable:
- against traffickers, rapists, or attackers
- against rival mafia who cross a declared line
- as protection, rescue, retaliation, or underworld consequence aimed away from innocent targets

## REVIEW Gates

### R1: Domestic-Drama Smell

Flag any passage that feels reverse-traceable to a Chinese drama plot device. Do not auto-rewrite solely because it resembles a domestic source; review whether the beat has been remapped to the declared target market.

Known review triggers:
1. Fatal toxin + wrong blood report as misunderstanding engine
2. Aphrodisiac + cold medicine mix-up
3. 追妻火葬场 grovel without target-market grovel grammar
4. 下克上 without target-market power mapping
5. Good girl -> mafia queen without a moral turning point episode

Escalate to HB3 only when the domestic mechanism is doing the actual causal work.

### R2: Male-Frequency Humiliation-to-Power Arc

Flag "endure humiliation -> suddenly become powerful" arcs for review. This pattern has weak overseas fit when it makes the male lead read as passive or when it imports domestic male-frequency gratification.

Escalate to HB3 only when the arc depends on Chinese status systems or direct domestic genre transfer.

### R3: Consent Timing

Flag relationship escalation that delays explicit choice too long for the declared target market. The useful default is:
- ep 1-2: forced proximity, possessive behavior, or power imbalance may appear if framed as pressure rather than consent
- around ep 3 or first major intimacy beat: the female lead should make an active choice and understand the cost

This timing is a diagnostic, not an automatic gate. Escalate to HB4 only when there is a consent breach, chemical substitution, or unpayoffed coercion.

### R4: Female Lead Agency

Flag episodes where the female lead only reacts, is carried by plot, or never voices a preference. The numeric diagnostics below are useful but not hard gates:
- Aim for multiple plot-changing decisions per episode.
- A spoken-line floor can help catch action-only female leads.
- Strong examples often let the female lead choose darkness rather than merely suffer it.

Escalate to HB4 or HB5 only when lack of agency creates consent or victimization failure.

### R5: Mafia-Language Accuracy

Flag incorrect or ornamental use of Don / consigliere / made man / sitdown / capo / underboss. Rewrite the term or the power relation when misuse confuses the scene's stakes.

### R6: Generic CEO Reverse Test

Ask: "If the male lead became a regular CEO, would this beat still work?" If yes, review whether the mafia setting is load-bearing. This is a craft diagnostic unless the beat also triggers HB3.

### R7: English Audience Reverse Test

After generating each episode, produce a reverse-test note: "If this beat appeared in a comparable overseas vertical drama, would viewers skip or rewind?" Treat the answer as review input, not as a standalone violation.

---

## STRONG GUIDANCE

### SG1: EP1 Should Detonate, Not Ease In

Open mid-conflict: kidnapping, rejection, confrontation, public humiliation, identity reveal, or another active pressure point. Avoid long static atmosphere openings. See `references/platform-knowledge.md` section 2 for retention context.

Do not enforce a fixed 5-beat EP1 bundle. Specific beat prescriptions are deferred until EP1-3 pilots are hand-written bottom-up and a new beat dictionary is derived from what worked.

### SG2: Paywall Episodes Should Carry the Strongest Unresolved Pressure

First paywall often falls around ep 10/11 for 60-ep series but can float by title. Secondary paywalls around ep 20 and ep 30 are planning aids, not canon. Put the strongest unresolved cliffhanger of that phase at the paywall rather than following a mechanical "every 10 episodes" rule.

Gwen Hayes beat mapping (Adhesion / Deepening / Midpoint) is a writing-coach scaffold, not an industry-native law.

### SG3: Risky Intimacy/Fetish Beats Belong Late and After Safety Context

C2 Appendix 2.1 (Wound-as-Fetish), 2.2 (Hickey Branding), 2.3 (Lovers-Pose-as-Prison) should appear only after the story has established outward violence toward enemies, female-lead agency, and target-market consent grammar. Treat early use as review risk; escalate to HB4 or HB5 only when the beat breaches consent or violence calibration.

### SG4: Provenance Examples Are Diagnostics, Not Positive Instructions

The old v0.3 source-pattern note is retained only as diagnostic provenance: novel-length dark romance can sustain some redemption arcs through long runway and trigger-warning context, while vertical short drama usually cannot. Do not copy source-specific IP, names, scenes, or likenesses.

---

## EXPORT / PROCESS STOPS

### EP1: Legal Flag Checklist Missing Before Export

Before `/导出` or external handoff, the episode set must include a legal/IP review list. Missing this list blocks export, but it does not imply the script body must be rewritten.

Block export when the project has not listed:
- character names
- family names
- brand elements
- locations
- visual likeness references
- source inspirations or comparable titles used during drafting
