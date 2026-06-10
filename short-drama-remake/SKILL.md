---
name: short-drama-remake
description: Analyze reference short-drama scripts or screen-recorded prompt workflows, ingest long/partial scripts into project files, extract the commercial story skeleton, and help with Red Fruit/Douyin-style skin-swap remakes, episode outlines, hook/s爽点 analysis, and shooting-ready scripts. Optionally create staged copy-paste prompts only when the user explicitly asks for 提示词, prompt chain, or a full workflow.
---

# Short Drama Remake

> License: SKILL.md, agents metadata, scripts, and bundled code are MIT; references are gobuildit methodology documentation with all rights reserved except use as part of this skill distribution.
> Version: 0.5.2

## Core Rule

Treat "1:1 remake" as **story-function replication**, not copying protected expression. Preserve the reference script's emotional rhythm, episode function, misdirection, reveal timing,爽点, and hooks; replace names, dialogue, scene specifics, professions, world rules, props, and surface events.

Match the user's current working language by default. If the user writes in Chinese, respond in Chinese; if the user writes in English, respond in English. Keep screenplay headings, dialogue, prompts, and audits in that same working language unless the user explicitly asks for another language. English skill instructions are internal control text; do not let them leak into screenplay language, character dialogue, headings, or user-facing prompts.

If the source text, screenshot, or video frame is unclear, mark the uncertain part as `[待确认]` instead of inventing it.

Use [references/three-layer-control.md](references/three-layer-control.md) as the control boundary for all remake stages: Foundation rules are hard gates, Skeleton rules lock story function while freeing implementation, and Flesh rules protect creative texture. Do not use foundation-level strictness to police dialogue wording, micro-actions, sensory detail, or sentence rhythm unless they violate canon, compliance, source truth, or remake distance.

## User Guidance Surface

When the user invokes `/仿写` without enough material, respond as a guided product flow, not as an internal protocol:

```text
当前模式：参考剧本拆解复刻（short-drama-remake）
请上传、拖入、粘贴参考剧本，或提供剧本文件路径。支持 .docx / .pdf / .txt / .md；也可以描述录屏里的提示词工作流。
我会先判断材料范围，再拆骨架；不会直接照搬原剧表达，也不会进入原创短剧 /开始 项目。
```

After each substantial stage, include a short user-visible handoff before `下一步可执行指令`:

- `当前阶段`: ingest / 骨架拆解 / 换皮方向 / 项目策划 / 集纲 / 正文 / 审稿
- `已完成`: what was analyzed or created
- `生成内容`: key files or named artifacts, with plain-language purpose
- `当前限制`: missing source, partial scope, open risk, or gate status when relevant
- `为什么下一步这样走`: one sentence explaining the stage dependency

For managed projects, after ingesting a file, show a file map using the template in [references/ingest-and-file-management.md](references/ingest-and-file-management.md#post-ingest-user-file-map). The file map is navigation only; do not treat `source-index.json` or `episode-map.md` `[待确认]` fields as facts.

## Command Layer

`/仿写` is the lightweight user command layer for this skill. When the latest user message starts with `/仿写` and contains a subcommand, or asks for remake help/status/continuation, read [references/command-layer.md](references/command-layer.md) before routing.

The command layer only normalizes user intent. It must not replace the stage contract, source gates, `script_draft.preflight`, `script_draft.postflight`, artifact registry ownership, report ownership, or forbidden-read rules.

Core subcommands:

- `/仿写 开始 [参考]`: enter ingest guidance or source ingest.
- `/仿写 状态 [项目目录]`: read-only project status and next-step summary.
- `/仿写 继续 [项目目录]`: restore/read status and recommend the next valid action; do not generate downstream artifacts.
- `/仿写 帮助`: show remake command help, file structure, and recovery examples.
- `/仿写 骨架`: run the reference skeleton stage.
- `/仿写 换皮`: run the skin-swap concept stage.
- `/仿写 出海`: enter overseas-target remake mode. Without a selected concept, generate overseas-adapted skin-swap concepts; with a selected concept number/text, create or refresh the target-market adaptation report.
- `/仿写 发现 [关键词/剧名/题材]`: 无剧本入口——调用网文大数据 MCP 查询热播榜单，从剧情摘要、AI 冲突分析和分集热度数据提炼可复刻骨架，可衔接 `/仿写 换皮`。需配置 `wangwen-bigdata` MCP Key（输入 `/配置数据` 完成设置）。
- `/配置数据`: 通过对话完成网文大数据 MCP Key 配置，无需命令行或手动编辑文件。
- `/仿写 定案`: deepen the selected concept into a project plan.
- `/仿写 集纲`: create detailed episode outlines.
- `/仿写 写集 N`: route to the existing managed script drafting path; `script_draft.preflight` remains mandatory.
- `/仿写 审稿 N`: audit or postflight-adjacent review; it must not unlock the next episode unless canonical postflight passes.

Optional advisory entries:

- `/仿写 方向会`
- `/仿写 方案会`
- `/仿写 诊断会 N`

These advisory meetings are not required workflow steps. They may produce analysis or prescriptions, but they must not set `gate_status`, write current pointers, generate an episode script, commit canon, or unlock continuation.

## MCP 数据增强（可选）

### /配置数据

**功能：** 通过对话完成网文大数据 MCP Key 配置，无需命令行或手动编辑文件。

**使用场景：** 使用 `/仿写 发现` 或 `/仿写 换皮` 热度验证时需要配置。

1. 询问：「请粘贴你的网文大数据 API Key（Key 以 `wwmcp_` 开头）」
2. 若用户还没有 Key，提示：「还没有 Key？免费注册：**wangwendashuju.com** → 登录后进入 **wangwendashuju.com/mcp** → 创建 Key → 复制（Key 以 `wwmcp_` 开头）」
3. 校验格式：Key 必须以 `wwmcp_` 开头；不符合则提示「格式不对，Key 应以 wwmcp_ 开头，请重新复制」并重试
4. 写入 Key——以下文件**都要更新**（用 Edit 工具逐一替换 `X-MCP-API-Key` 字段值）：
   - `~/.config/drama-workshop-skills/short-drama-remake/.mcp.json`（必须，所有平台；按包内 `.mcp.example.json` 结构创建；不得写入公开仓 skill 目录）
   - `~/.workbuddy/mcp.json`（若文件存在则更新，WorkBuddy connector 注册表）
5. 输出：「✅ 配置完成！请重启 WorkBuddy / Claude Code，重启后 /仿写 发现 和 /仿写 换皮 热度验证即可调用真实榜单数据。」

**Key 已配置时：** 优先读取 `~/.config/drama-workshop-skills/short-drama-remake/.mcp.json` 中当前 Key，提示前 8 位，询问是否更换。若只发现旧版包内 MCP 配置文件，仅作为迁移来源读取，不得继续写入 skill 目录。

---

### /仿写 发现 [关键词/剧名/题材]

**功能：** 无剧本入口——从热播榜单数据中提炼可复刻骨架，适合没有源剧本的用户探索方向。

**依赖：** 需要 `wangwen-bigdata` MCP 工具已配置。未配置时输出：「需要配置网文大数据 Key，在对话里输入 `/配置数据` 即可完成设置。」

**调用示例：** `/仿写 发现 逆袭总裁` | `/仿写 发现 女频甜宠` | `/仿写 发现`（不填则展示近期综合热度 TOP 5）

**执行流程：**

1. 确认 Credits 消耗：「💡 即将查询网文大数据 MCP 榜单（消耗约 2-4 Credits），是否继续？(Y/n)」用户确认后执行
2. 先读 `resource://domain-video` 获取当前表结构（以服务端实际字段名为准），再查询热播榜单：从 `lg_hongguo_video_snapshot`（或服务端对应表）按关键词/题材筛选近 14 天热度 TOP 3-5 剧目，获取 `video_name`、`video_desc`、`video_tags`、`gender`、`episode_count`、`like_count_by_episode`
3. 调取 AI 分析：`lg_video_analysis`（或服务端对应表）获取对应剧目的 `emotion_conflict_analysis`、`core_tags_analysis`
4. **输出骨架报告**（每部剧一张）：
   - **剧名 + 分集数 + 受众（男/女频）**
   - **剧情摘要**（来自 `video_desc`，精简 1-2 句）
   - **核心冲突结构**（来自 `emotion_conflict_analysis`）
   - **爽点分布**（基于 `like_count_by_episode`，指出哪几集是高潮峰值集）
   - **核心标签**（来自 `core_tags_analysis`）
   - **可复刻骨架要素**：权力关系、情感节奏、反转位置（标注 `[推断自摘要]`，非完整剧本拆解）
   - **局限性说明**：「⚠️ 本骨架基于平台摘要和 AI 分析，非完整剧本拆解。细节可信度低于用户直接提供剧本，建议用于方向探索；正式立项前建议补充源剧本。」
5. 输出后询问：「继续生成换皮方向？选一部剧继续 `/仿写 换皮`，或提供完整剧本获取精细骨架。」

**与标准流程的衔接：** `/仿写 发现` 产出的骨架可替代标准流程中「用户提供剧本」作为 `/仿写 换皮` 的输入，但 `source_scope = mcp_summary`（不等同于 `complete`）。换皮概念生成时每个方向必须注明「骨架来源：MCP 摘要」，中后段反转和终局标为 `[待确认]`。

---

### /仿写 换皮 MCP 热度验证（可选增强）

在 `/仿写 换皮` 生成换皮方向**之前**，若 `wangwen-bigdata` MCP 可用，询问：

「💡 是否在生成换皮方向前验证各题材在当前榜单的热度？（约 1-2 Credits，可帮助筛选赛道，Y/n）」

确认后执行：
- 提取用户骨架中隐含的 2-4 个候选题材
- 先读 `resource://domain-video` 确认表结构，再查询 `lg_hongguo_video_snapshot`（或服务端对应表）该题材近 14 天在榜数量和平均热度
- 在换皮方向里为每个方向附加：`📊 赛道热度：[高/中/低]，近14天在榜 N 部`

MCP 不可用或用户跳过时，正常生成换皮方向，末尾追加：
`> 📊 提示：输入 /配置数据 可配置网文大数据 Key，换皮时可自动验证题材热度。`

---

## Stage Contract

Keep each stage dependent on the previous artifact. If the user asks for a downstream stage without enough upstream material, state exactly what is missing and provide a copy-paste command to generate it. Do not silently invent missing skeletons, concepts, or outlines.

Required upstream artifacts:

- **Concept generation** requires a reusable skeleton table or equivalent拆解. If `target_market=overseas`, concept generation must produce overseas-adapted directions from the start, not domestic concepts for later translation.
- **Overseas adaptation** requires the skeleton plus a selected overseas-adapted concept number or concept text. It produces a market adaptation report, not a script body.
- **Project planning** requires the skeleton plus a selected concept number or concept text. If `target_market` is overseas or differs from `source_market`, it also requires an accepted `market_adaptation_report`; otherwise run `/仿写 出海` first and do not create `project-bible.md`.
- **Episode outlining** requires the skeleton plus the selected project plan.
- **Script drafting** requires the project plan plus the target episode outline and episode number.

If the user provides a file path, read it. If the conversation already contains the needed artifact, use it and name the artifact being used.

Source scope gates override stage readiness. A `基于已提供集数的样本骨架` can unlock only sample/opening concepts unless `allow_full_series_concepts` is true. `complete` means the source coverage appears complete; it does not replace post-ingest checks or progressive reading.

## Project Gate Protocol

Use this skill as the authoritative entry for `/仿写`, reference-script拆解, remake concepting, managed remake projects, and remake episode scripts. Do not execute remake work by loading `short-drama` first.

For managed remake projects, use the Phase 4 contract files instead of relying on memory or ad hoc file search:

- `references/schema/artifact-registry.yaml` defines artifact status, derived gate status, current pointers, transaction refs, and forbidden paths.
- `references/schema/node-route-table.yaml` defines route boundaries and the fixed `script_draft.preflight` order.
- `references/schema/reports.yaml` defines SIR/RMR/FGR/preflight/postflight report fields. Reports use `report_status`; only the registry owns `gate_status`.
- `references/checker/deterministic-checker.md` defines deterministic checker scope and the LLM review boundary.
- `references/three-layer-control.md` defines which constraints can block generation and which belong to creative review.
- `references/market/` defines target-market adaptation contracts. Start with `references/market/layer-taxonomy.md`, then use the market files for `/仿写 出海`; do not import `short-drama/references/overseas/*` into remake nodes.
- `references/fixtures/` contains regression fixture contracts and initial samples.

Before drafting a script in a managed project, run or mentally apply `script_draft.preflight`. This gate is the only script-generation entry; do not skip from project plan or episode outline directly to an episode body.

1. Restore project state through `resume.restore` only when entering from a new/uncertain context. P10 consumes a valid `resume_packet`; it must not rerun full restore.
2. Verify the target episode has an accepted current `execution_card` with `decision_id` and committed transaction.
3. Consume the latest `fact_gate_report`, `source_integrity_report`, and `reference_mapping_report`. Do not rejudge P9/P12 inside script drafting.
4. If the project target market is overseas or differs from the source market, consume the latest `market_adaptation_report`. Do not draft overseas remake scripts without the target-market adaptation layer.
5. Verify `reference-expression-guide.md`, `factor-scorecard.yaml`, `remake-risk-audit.md`, `project-state.md`, and accepted canon are registered and readable.
6. Reject forbidden reads: `short-drama/SKILL.md`, `short-drama/references/*.md`, raw source bundles, `research-notes.md`, `_legacy_review/**`, `09_experiments/**`, candidates, drafts, and tmp files.
7. Apply the three-layer boundary: preflight blocks only Foundation/Skeleton failures. Flesh concerns such as weak dialogue texture, bland sensory detail, or generic sentence rhythm may be warnings for postflight, but must not by themselves block body generation.
8. If blocked, return one user-visible blocking summary and set `body_generated=false`. Do not create an episode script.

The blocking summary must include: blocking reason, affected scope, whether it blocks only the target episode or the whole project, recommended next step, and available user actions. Render it for the user as:

```text
卡在：...
影响：...
为什么不能继续：...
复制这句继续：`...`
```

Do not expose the full internal registry, gate, trace, or transaction fields unless the user explicitly asks for debug detail.

After drafting, run `script_draft.postflight` before unlocking the next episode. A script is not complete until quality passes, user review accepts it, canon is committed, state is updated, risk/sync checks pass, read trace is clean, and the next episode gate is unlocked. `quality_gate_status=passed` alone is not enough; continuation must use top-level `postflight_report.report_status == passed`.

Postflight must include a Flesh-layer memorability check: name the one concrete moment, line, action, or image a viewer can remember. If the answer is only "the process passed" or "the hook exists", mark the episode as process-clean but creatively weak and request revision before treating it as quality-passed.

Postflight must also run a lightweight script-craft scan without reading `short-drama/references/*`: first-screen effective information, event hook, character-entry information, anti-AI dialogue, and meaningless repeated dialogue. Local definitions: first-screen effective information means the opening quickly gives a concrete conflict, pressure, relationship, goal, or visible action; event hook means the ending can answer "who will do what next"; character-entry information means an important first entrance carries identity, situation, relationship, goal, pressure, or action style; anti-AI dialogue means avoiding essay-like connective phrasing, generic summary lines, and dialogue that does not fit the speaker under pressure; meaningless repeated dialogue means repeated questions, confirmations, or explanations that add no new pressure, evidence, action, or choice. Treat these as Flesh/Skeleton review signals: they can request revision or lower quality status, but they do not override source truth, canon, compliance, remake distance, or locked episode function.

Command-layer aliases do not weaken this rule. `/仿写 写集 N`, `/仿写 继续写第 N 集`, and any natural-language continuation request must still pass through the same preflight/postflight protocol.

For deterministic validation, run:

```text
python3 scripts/remake_gate_checker.py --self-test
python3 scripts/remake_gate_checker.py --fixture references/fixtures/missing_outline_blocks_script/fixture.yaml
find references/fixtures -name fixture.yaml -print0 | xargs -0 -n1 python3 scripts/remake_gate_checker.py --fixture
PYTHONPYCACHEPREFIX=/private/tmp/short-drama-remake-pycache python3 -m py_compile scripts/remake_gate_checker.py
```

## Source Ingest And File Gates

For long script files (`.docx`, `.pdf`, `.txt`, `.md`), prefer running [scripts/split_short_drama_source.py](scripts/split_short_drama_source.py) before analysis. The script creates the standard project structure, `manifest.yaml`, `00_source/source-index.json`, source modules, episode files, and 10-episode bundles. If the script is unavailable or cannot read the format, fall back to manual progressive reading and state the limitation.

The default minimum granularity is **episode**. Do not split into scenes by default. Only do scene-level analysis for a target episode when the user asks for single-episode revision, shooting breakdown, or scene-level review.

The script is a reading aid, not a substitute for reading. `source-index.json` and `episode-map.md` are navigation and evidence layers; their `[待确认]` fields are not facts. Before extracting a reusable skeleton, read `manifest.yaml`, `00_source/source-index.json`, `00_source/synopsis.md`, `00_source/story-outline.md`, `00_source/characters.md`, `00_source/episode-outline.md`, `00_source/episode-map.md`, and the first 10-episode bundle. For complete sources, roll through later bundles before finalizing the full-series skeleton.

Always inspect `source-index.json.scope` or `manifest.yaml.gates`:

- `complete`: full-series skeleton claims are allowed only after progressive reading across the whole source.
- `partial`: only sample/opening-segment analysis is allowed. Do not claim full-series structure, middle/late reversals, ending payoffs, or complete commercial model.
- `incomplete` or `unknown`: state the limitation and mark unverified full-series claims as `[待确认]`.

If the user only provides the first 3/5/10 episodes, a trial read, sample chapters, or a fragment, label the output as `基于已提供集数的样本骨架`. Do not present it as a full-series skeleton unless the missing source is later provided.

For PDFs, check `source-index.json.heading_diagnostics` and `validation.warnings`. PDFs often contain both a `分集梗概` heading run and a formal script heading run; a successful split is not enough if the selected run or episode count conflicts with the declared source range.

For the standard project structure, ingest modes, validation checks, and the authoritative downstream reading matrix, read [references/ingest-and-file-management.md](references/ingest-and-file-management.md) when the task involves long files, partial files, PDF extraction, project-file organization, or continuity management.

## Functional Replacement

Preserve episode **function**, not the reference's event template. At every remake stage, check whether the output merely renames the original surface events. When that happens, replace the event mechanics while keeping the same dramatic job.

Use this distinction:

- Keep: humiliation before recognition, false safety before real crisis, public proof, delayed reveal,反噬, next-case hook.
- Replace: exact venue, ceremony type, death method, proof device, family secret mechanics, profession, prop, dialogue beat, and visual business.

For each selected concept, perform a second-layer replacement pass before outlining: ask what the new genre naturally provides, then redesign the concrete incidents from that genre rather than copying the reference's incident order.

## Workflow

1. **Ingest the reference**
   - If the user provides a script, read it directly or through ingest-generated source files before generating creative artifacts.
   - For long script files, ingest into `00_source/` first when possible, then progressively read the generated files.
   - For partial sources, state that only a sample/opening skeleton can be extracted.
   - If the user provides a video, extract metadata, sample key frames, and transcribe/OCR when available. Use visible prompts and outputs as evidence.
   - State what was actually observed and what is uncertain.

2. **拆骨架 before writing**
   - Analyze story core, power relations, episode function, emotional curve,爽点, reversals, and payment/retention hooks.
   - Do not rewrite yet.
   - For managed projects, create both `01_skeleton/reference-skeleton.md` and `01_skeleton/reference-expression-guide.md`; use `01_skeleton/factor-scorecard.yaml` for evidence-based transferable factors.

3. **Make a reusable skeleton table**
   - Per episode: use the `three-layer-control.md#Skeleton Table Contract` fields: `locked_episode_function`, `locked_viewer_emotion`, `locked_hook_function`, `locked_payoff_or_setup`, `must_replace_surface`, `free_implementation_zone`, and `distance_test`.

4. **换皮不换骨**
   - Generate multiple concept skins that keep the skeleton but change genre, world, identities, power tokens, scenes, and dialogue logic.
   - Favor simple high-conflict premises suitable for Red Fruit/Douyin users.
   - If `target_market=overseas`, do not generate domestic-facing concepts first. Generate overseas-adapted concept skins directly: overseas-native genre promise, relationship grammar, power/status system, public proof mechanism, and paywall pressure must fit the target market.
   - Diversify the concepts by audience, production cost, genre distance, and conflict engine.
   - Include a short risk note when a concept is too close to the reference or too expensive/confusing to shoot.

5. **Deepen selected concept**
   - Produce project plan, logline, audience, world rules, character bios, relationship map, protagonist oppression source, comeback resource, key props, and first 10 episodes.
   - Explain the replacement logic for the core resource, power system, public proof scene, antagonist profit model, and long-term emotional hook.
   - Include a雷同风险自检 that lists which surface elements must still be changed before scripting.
   - Include a `复刻权限表`: Foundation locked items, Skeleton locked functions, and Flesh free zones. This table prevents later drafts from treating optional texture choices as hard constraints.

6. **Write detailed episode outlines**
   - For each episode, use 起、承、转、合.
   - Include exact episode function and ending hook.
   - Make each episode script-ready: visible opening conflict, pressure action, reversal action, concrete prop/evidence, and a shootable ending image.
   - Avoid outlines that only restate the project plan. Each episode needs new incident detail.
   - For managed projects, convert the target episode outline into `04_outlines/episodes/epXXX.execution-card.md` before script drafting. The execution card is the direct control surface for script generation and must separate `locked_story_job`, `locked_entry_pressure`, `locked_turning_point`, `locked_exit_hook`, `free_scene_options`, `free_dialogue_options`, and `surface_replacement_notes`.

7. **Draft shooting-ready script**
   - In managed projects, script drafting starts only after `script_draft.preflight` passes. Missing execution card, stale source/reference reports, open blocking risks, unverified direct facts, or forbidden reads block the draft.
   - Use scene headings, cast, props, visible action, character-fit scene-functional dialogue, and SFX.
   - Dialogue must fit the speaker's identity, power position, emotional state, relationship, and current scene objective.
   - Every line should carry at least one function: pressure, counterattack, information, misdirection, reveal, hook, or emotional release.
   - Place exposition inside conflict, props, actions, interruptions, opponent questions, or visible reactions.
   - Avoid novelistic inner monologue. Use V.O. only for fast setup.
   - Ensure the first 10 seconds enter conflict.
   - If the user does not specify length, keep a single episode focused on its assigned episode function, usually 3-5 scenes.
   - Do not spend the first episode explaining the full mythology; reveal only what the scene conflict needs.

8. **Audit and strengthen**
   - Review as a short-drama platform editor.
   - Cut dead dialogue, increase pressure, clarify hooks, and rewrite weak scenes.
   - Judge dialogue by character fit, scene pressure, plot function, and short-drama rhythm.
   - Check stage leakage: if a script draft starts doing concept planning or if a concept list starts writing full scenes, return it to the requested stage.
   - Check remake distance: preserve the emotional/functional skeleton while increasing the distance of specific incidents from the reference.
   - Apply the three-layer boundary: fix Foundation/Skeleton violations decisively, but treat Flesh-layer choices as craft suggestions unless they copy protected expression, break character core, violate compliance, or erase the locked story job.
   - Always answer: "What is the one concrete moment a viewer remembers from this episode?" If no concrete moment can be named, ask for revision instead of declaring creative quality passed.
   - In managed projects, use postflight status as the only next-episode unlock signal. Do not unlock continuation from a partial quality pass or from a draft that has not been accepted into canon and state.
   - If a candidate script exists but postflight is missing, incomplete, not user-accepted, or not committed to canon/state, block continuation and return a user-visible postflight blocking summary instead of writing the next episode.

## Continuation Guidance

Always end substantial outputs with `下一步可执行指令`. Give 2-4 exact copy-paste prompts, matched to the current stage. These are instructions the user can send directly in the next turn, not vague suggestions.

Rules:
- Write each option as a complete user prompt, preferably inside a fenced `text` block or inline code.
- Replace placeholders with known project names, concept numbers, episode numbers, or file names when available.
- If the next stage has one clearly best path, label it `推荐下一步`.
- Do not write only "可以继续生成..." or "建议深化..." without a complete instruction.
- Before the command list, add one sentence explaining why this is the correct next stage.
- If `manifest.yaml.gates.allow_full_series_concepts` is false or the artifact is labeled `样本骨架`, the next-step prompts must either ask for the missing full source or explicitly say `基于已提供集数`. Do not offer full-series concepts, full project plans, or full-series claims from partial material.

- After **reference skeleton / 骨架表**:
  - For partial/sample skeletons: `基于已提供集数的样本骨架，生成 10 个样本创意方向。每个方向只判断开局冲突、人物关系、权力凭证、前 N 集可复刻节奏和雷同风险；中后段反转、终局爽点和完整商业模型均标为 [待确认]。`
  - For complete skeletons: `基于上面的完整可复刻骨架，生成 10 个彻底换皮的短剧创意方向。每个方向包含剧名、题材、一句话卖点、主角身份、男主身份、核心反派、关键权力凭证、前 10 集节奏和最大爽点。`
  - For overseas target market: `基于上面的可复刻骨架，生成 10 个海外适配换皮方向。每个方向必须从一开始就按海外目标市场设计，包含剧名、目标平台/受众、海外-native 题材承诺、主角/男主身份、核心反派、权力/身份凭证、前 10 集节奏、最大爽点、必须替换的源市场机制和雷同风险。`
  - For complete skeletons: `把上面的可复刻骨架压缩成 20 集版本，保留原来的剧情功能、情绪节奏、爽点位置和结尾钩子。`
  - `指出上面参考剧本最值得复刻的 5 个爽点机制，并说明每个机制适合换成哪些现代/古装/奇幻表皮。`
- After **10 concepts**:
  - For overseas concept lists: `对第【编号】个海外适配方向生成 market-adaptation-report.md，逐项说明哪些剧情功能可迁移、哪些源市场机制必须替换、目标市场约束、雷同风险和写集前阻断项。`
  - `深化第【编号】个创意，输出完整项目策划案：剧名、类型、一句话卖点、目标受众、核心爽点、故事梗概、世界观、人设、人物关系网、前 10 集大纲和每集钩子。`
  - `对比第【编号】和第【编号】个创意，从开局冲突、用户理解成本、爽点密度、拍摄成本、长线付费钩子判断哪个更适合红果/抖音。`
- After **project plan**:
  - `基于这个项目，生成前 10 集详细集纲。每集用起、承、转、合写清楚开场冲突、主角受压、反派动作、爽点/憋屈点、具体证据/道具和结尾钩子。`
  - `强化这个项目的开局 3 集，让冲突更快、误会更狠、反派更可恨、结尾钩子更强，并说明改动理由。`
- After **episode outline**:
  - `把第【集数】集写成正式短剧剧本，严格使用：剧名、集数、场次、出场人物、主要道具、可拍摄动作、角色台词、SFX。`
  - `审查前 10 集集纲，找出节奏拖慢、爽点不清、钩子不够强的地方，并给出修改后的集纲版本。`
- After **script draft**:
  - `以红果/抖音短剧审稿人标准，检查并强化这集剧本。重点看开局 10 秒、台词是否符合人物设定和场景压力、反派压迫感、爽点释放和结尾钩子。`
  - `继续写第【下一集】集，必须直接承接上一集结尾钩子，并保持同样的格式、节奏和人物口吻。`

Do not leave the user at a dead end. If the latest request is ambiguous, recommend the most logical next stage instead of asking broad questions.

## Prompt Library

Read [references/prompt-chain.md](references/prompt-chain.md) only when the user explicitly asks for complete staged prompts, reusable copy-paste prompts, or a full workflow. If the user asks only for a skeleton,拆解,换皮 direction,集纲, or script, do not append the prompt library by default.

## Output Standards

- Lead with the conclusion or next usable artifact.
- Keep stages separate; do not collapse analysis, concepting, outlining, and scripting into one prompt unless the user explicitly asks for a single all-in-one prompt.
- Do not output staged prompts unless the user's latest request explicitly includes words such as `提示词`, `prompt`, `分阶段`, `工作流`, or `可复制`.
- End substantial outputs with `下一步可执行指令` and exact copy-paste prompts.
- When creating prompts, include placeholders such as `【填写编号】`, `【粘贴参考剧本】`, and `【填写集数】`.
- For script drafts, enforce clear formatting:
  - `剧名：`
  - `集数：`
  - `场 X-XX：内/外 时间 地点`
  - `【出场人物】`
  - `【主要道具】`
  - `△ 可拍摄动作`
  - `角色名（动作/神态）：台词`
  - `[SFX：音效/画面提示]`
