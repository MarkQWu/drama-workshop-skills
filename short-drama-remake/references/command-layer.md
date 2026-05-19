# Command Layer

This file defines the lightweight `/仿写` user command layer for `short-drama-remake`.

The command layer is an entry router and intent normalizer only. It must not become a second workflow engine. Source scope gates, stage dependencies, `script_draft.preflight`, `script_draft.postflight`, artifact registry ownership, report ownership, and forbidden-read rules remain authoritative.

## Parsing Rule

Parse the first token after `/仿写` as the subcommand.

- No subcommand or direct reference material: use the existing guided ingest flow.
- Unknown subcommand: show `/仿写 帮助` and recommend the closest valid command.
- Episode commands accept Arabic numerals and Chinese forms when unambiguous: `写集 12`, `写第12集`, `审稿 12`, `诊断会 12`.
- A project directory argument is optional only when the active managed remake project is already clear from the conversation. If context is uncertain, ask for `PROJECT_DIR`.

Do not scan original `~/short-drama-projects/` for remake state. Managed remake projects use their own project directory with `manifest.yaml`, `00_source/`, `01_skeleton/`, `02_concepts/`, `03_plan/`, `04_outlines/`, `05_scripts/`, and `06_state/`.

## Command Map

| User command | Normalized intent | Route | Boundary |
|---|---|---|---|
| `/仿写 开始 [参考]` | `ingest_reference_source` | Ingest guidance or source ingest | With no material, ask for upload/paste/path; do not create project files. |
| `/仿写 状态 [项目目录]` | `read_project_status` | Read-only status summary | May read `manifest.yaml`, `06_state/project-state.md`, registry/report summaries; must not write files or run generation gates. |
| `/仿写 继续 [项目目录]` | `recommend_next_remake_action` | Restore/read state, then recommend next command | Do not generate scripts, concepts, outlines, or gate reports unless the user explicitly selects that next command. |
| `/仿写 帮助` | `show_remake_command_help` | Help surface | Show command list, recovery examples, and stage order. |
| `/仿写 骨架` | `extract_reference_skeleton` | Existing skeleton stage | Requires source material or ingested source files; respect source scope. |
| `/仿写 换皮` | `generate_skin_swap_concepts` | Existing concept stage | Requires skeleton; partial sources only unlock sample concepts. |
| `/仿写 出海` | `enter_overseas_remake_flow` | Target-market concept/adaptation stage | With no selected concept, generate overseas-adapted skin-swap concepts from the skeleton. With a selected concept, write/refresh `market-adaptation-report.md`, not a script body. |
| `/仿写 定案` | `deepen_selected_concept` | Existing project planning stage | Requires skeleton and selected concept; if target market is overseas or differs from source market, consume accepted `market_adaptation_report` first. |
| `/仿写 集纲` | `create_episode_outlines` | Existing outline stage | Requires project plan and source/skeleton context. |
| `/仿写 写集 N` | `draft_episode_script` | `script_draft.preflight` then draft if passed | Mandatory preflight. If blocked, `body_generated=false` and no episode script file. |
| `/仿写 审稿 N` | `audit_episode_script` | Review/postflight-adjacent audit | Advisory unless explicitly closing canonical postflight; never unlock next episode by itself. |

## Optional Advisory Meetings

These commands are optional aids for uncertain moments. They are not required gates.

| User command | Normalized intent | Use when | Forbidden effects |
|---|---|---|---|
| `/仿写 方向会` | `advisory_direction_review` | Skeleton exists and the user is unsure which skin-swap direction to choose. | Must not create accepted concept, set `gate_status`, or unlock planning. |
| `/仿写 方案会` | `advisory_plan_review` | A selected project plan exists and the user wants pressure testing. | Must not accept project bible, write execution cards, or unlock script drafting. |
| `/仿写 诊断会 N` | `advisory_episode_diagnosis` | Episode outline or candidate script N needs diagnosis. | Must not generate final body, commit canon, update current pointer, or unlock next episode. |

Preferred public labels for docs are `方向评审`, `方案评审`, and `剧本诊断`. If the user inputs `方向会`, `方案会`, or `诊断会 N`, treat them as aliases.

Advisory meetings may discuss Flesh-layer quality, but they must not convert style preferences into Foundation or Skeleton gates. When an advisory meeting recommends a craft change, label it as `建议` unless it fixes source truth, canon, compliance, remake distance, or locked story function.

## Status Command Contract

`/仿写 状态 [项目目录]` is read-only.

Read only the minimum state needed:

- `manifest.yaml`
- `06_state/project-state.md`
- `06_state/artifact-registry.yaml` when present
- latest relevant report summaries when already registered

Output:

```text
当前阶段：...
已生成文件：
- path：作用
当前限制：...
推荐下一步：`/仿写 ...`
可选增强项：`/仿写 ...`
换新对话恢复：`/仿写 状态 PROJECT_DIR`
```

Do not run `script_draft.preflight`, `source.validate`, `reference_map.validate`, `fact_gate.validate`, or `script_draft.postflight` from status.

## Continue Command Contract

`/仿写 继续 [项目目录]` recommends the next valid action. It does not silently perform that action.

Allowed behavior:

- Restore/read project state when context is uncertain.
- Identify the most likely next stage from existing artifacts and gate status.
- Provide one recommended command and 1-3 alternatives.

Forbidden behavior:

- Creating `05_scripts/**`.
- Creating or accepting execution cards.
- Setting `gate_status`.
- Writing current pointers.
- Unlocking next episode.
- Treating "continue" as "write next episode" unless the user explicitly says `写集 N` or `继续写第 N 集`.

If the previous candidate script has not passed postflight, recommend closing review/postflight before the next episode.

## Handoff Contract

After every substantial command output, include this user-visible handoff before `下一步可执行指令`:

```text
当前阶段：ingest / 骨架拆解 / 换皮方向 / 项目策划 / 集纲 / 正文 / 审稿
已完成：...
已生成文件：
- path：文件作用
当前限制：...
推荐下一步：`/仿写 ...`
可选增强项：`/仿写 ...`
换新对话恢复：`/仿写 状态 PROJECT_DIR`
```

Only list files that actually exist or artifacts that were actually produced. For planned future files, label them as `后续会生成` instead of `已生成`.

## Help Text

Use this shape for `/仿写 帮助`:

```text
[帮助] short-drama-remake：拆解复刻命令

/仿写 开始 [参考]       上传/粘贴/提供参考剧本路径，开始拆骨架
/仿写 状态 [项目目录]   只读查看当前进度、已生成文件和下一步
/仿写 继续 [项目目录]   恢复项目并推荐下一步，不自动生成正文
/仿写 骨架              拆参考剧本的可复刻骨架
/仿写 换皮              基于骨架生成换皮方向
/仿写 出海 [方向编号]     进入海外仿写：未选方向先生成海外适配换皮方向；已选方向则生成市场迁移层
/仿写 定案              深化选定方向为项目策划
/仿写 集纲              生成详细分集大纲
/仿写 写集 N            写第 N 集，必须通过 preflight
/仿写 审稿 N            审第 N 集，不能单独解锁下一集

可选增强：
/仿写 方向会            不确定方向时，评估换皮方向
/仿写 方案会            定案前，评估理解成本、爽点密度、拍摄成本和雷同风险
/仿写 诊断会 N          对第 N 集做复刻距离、节奏和台词诊断

换新对话后：
/仿写 状态 PROJECT_DIR
/仿写 继续 PROJECT_DIR
```
