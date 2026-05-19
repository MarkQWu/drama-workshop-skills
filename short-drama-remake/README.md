# short-drama-remake

`short-drama-remake` is the dedicated remake / reference-analysis skill. Use it for `仿写`, reference skeleton extraction, skin-swap concepting, managed remake projects, episode execution cards, and shooting-ready remake scripts.

## Entry

- Main entry: call this skill directly for `/仿写` or remake requests.
- Command help: `/仿写 帮助`
- Do not route remake work through `short-drama`.
- In managed projects, script drafting is guarded by `script_draft.preflight`; downstream script generation must not rely on memory or ad hoc file search.

## Quick Start

1. Send `/仿写 开始` with a script file path, attached file, pasted script, or screen-recorded prompt workflow description.
2. The skill first judges source scope and extracts a reusable story-function skeleton. It does not rewrite immediately.
3. Continue through the guided chain: skeleton table -> 10 skin-swap concepts -> selected concept plan -> episode outlines -> shooting-ready script.

After every substantial output, the skill should show what was completed, what files or artifacts now matter, why the next stage follows, and 2-4 copy-paste next commands.

The workflow uses a three-layer control model:

- Foundation: source scope, canon, compliance, character core, project state, and similarity boundaries are hard gates.
- Skeleton: episode function, viewer emotion, payoff/setup, and hook function are locked, while concrete implementation stays open.
- Flesh: dialogue wording, micro-action, sensory detail, sentence rhythm, and memorable texture stay maximally free unless they break Foundation or Skeleton rules.

## Command Layer

The `/仿写` command layer is a lightweight entry map, not a second workflow engine.

| Command | Use |
|---|---|
| `/仿写 开始 [参考]` | Start ingest from a reference script, file path, pasted text, or prompt workflow. |
| `/仿写 状态 [项目目录]` | Read-only progress summary for a managed remake project. |
| `/仿写 继续 [项目目录]` | Restore context and recommend the next valid command without generating downstream artifacts. |
| `/仿写 帮助` | Show remake command help and recovery examples. |
| `/仿写 骨架` | Extract the reusable reference skeleton. |
| `/仿写 换皮` | Generate skin-swap concepts from the skeleton. |
| `/仿写 出海 [方向编号]` | Enter overseas remake flow: first generate overseas-adapted skin-swap concepts, then build the target-market adaptation layer for the selected concept. |
| `/仿写 定案` | Deepen a selected concept into the project plan. |
| `/仿写 集纲` | Generate detailed episode outlines. |
| `/仿写 写集 N` | Draft episode N through `script_draft.preflight`; blocked preflight creates no script body. |
| `/仿写 审稿 N` | Review episode N; next-episode unlock still requires canonical postflight. |

Optional advisory entries:

| Command | Use |
|---|---|
| `/仿写 方向会` | Evaluate remake directions when the user is unsure. |
| `/仿写 方案会` | Pressure-test a selected plan for cost, clarity, hooks, and similarity risk. |
| `/仿写 诊断会 N` | Diagnose episode N without unlocking gates or continuation. |

New chat recovery:

```text
/仿写 状态 PROJECT_DIR
/仿写 继续 PROJECT_DIR
```

`/仿写 状态` is read-only. `/仿写 继续` recommends the next action; it is not a hidden "write next episode" command.

## Managed Project Gate

Before writing an episode script, the project must have readable current artifacts:

- accepted execution card for the target episode
- market adaptation report when the target market is overseas or differs from the source market
- `fact_gate_report`
- `source_integrity_report`
- `reference_mapping_report`
- `reference-expression-guide.md`
- `factor-scorecard.yaml`
- `remake-risk-audit.md`
- `project-state.md`
- accepted canon

`script_draft.preflight` consumes those artifacts and reports. It must not rerun full `resume.restore`, `fact_gate.validate`, `source.validate`, or `reference_map.validate` inside the script-drafting node.

Preflight blocks only Foundation/Skeleton failures. Flesh-layer concerns can warn or request revision in postflight, but they must not silently become hard gates before body generation.

## Blocking Summary

When preflight blocks script generation, return one user-visible blocking summary:

- blocking reason
- affected scope
- whether it blocks this episode or the whole project
- recommended next step
- available user actions

Blocked preflight must set `body_generated=false` and must not create an episode script.

## Postflight Reliability

After a candidate episode script is drafted, `script_draft.postflight` must close the episode before the next episode can unlock.

`quality_gate_status=passed` is not enough by itself. The next episode remains locked until postflight confirms user acceptance, canon commit, project-state update, clean read trace, passed risk/sync checks, and top-level `postflight_report.report_status=passed`.

The bundled `script-postflight-auditor` contract is a thin role boundary around the existing route table and report schema. It is not a platform runtime and does not replace `SKILL.md` as workflow authority.

## Validation

Run the minimal gate checks from the skill root:

```bash
python3 scripts/remake_gate_checker.py --self-test
```

Run all bundled fixtures:

```bash
find references/fixtures -name fixture.yaml -print0 | xargs -0 -n1 python3 scripts/remake_gate_checker.py --fixture
```

Compile the checker:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/short-drama-remake-pycache python3 -m py_compile scripts/remake_gate_checker.py
```

Fixture files are JSON-compatible YAML. The checker intentionally validates deterministic contracts only; creative quality remains an LLM review boundary.
