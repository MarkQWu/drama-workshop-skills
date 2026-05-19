**v0.4.4**（2026-05-15）

Tighten Overseas Boundary：`remake_gate_checker.py` 默认禁止读取 `short-drama/references/` 前缀，避免新增原创出海资料绕过隔离；`market_adaptation_report` 契约补齐 R0-R5 字段校验；`references/market/` 从占位升级为 remake-native active scaffold，用本 skill 自己的目标市场迁移分类表达海外规则。

---

**v0.4.3**（2026-05-15）

Market Layer Taxonomy：新增 `references/market/layer-taxonomy.md`，把 `/仿写 出海` 的资料准入拆成 source truth、target market、non-transferables、target replacement、genre promise / paid pressure、similarity distance 和 script flesh。`concept.generate` / `market_adapt.validate` 明确 allowed market references，海外 concept/report 需要带 layer classification，避免 remake 直接读取原创 `short-drama/references/overseas/*`。

---

**v0.4.2**（2026-05-14）

Overseas Concept Adaptation：`/仿写 出海` 从换皮方向阶段就进入海外目标市场，不再先生成国内方向再迁移。

- `/仿写 出海` 未指定方向时，先基于骨架生成海外适配换皮方向。
- `/仿写 出海 [方向编号]` 已选方向时，生成或刷新 `market-adaptation-report.md`。
- 海外换皮方向必须包含 target market、海外-native 题材承诺、关系/权力语法、必须替换的源市场机制和付费压力。

---

**v0.4.1**（2026-05-14）

Overseas Adaptation Structure：先补 `/仿写 出海` 的结构，不填满具体海外方法论。

- 新增 `/仿写 出海` 命令路由，用于为选定换皮方向生成海外目标市场迁移层，不直接写正文。
- 新增 `market_adaptation_report` artifact / report / route contract；目标市场为 overseas 或 source/target market 不一致时，正文 preflight 必须消费该报告。
- 新增 `references/market/` 占位规则文件，后续再补具体海外平台、文化禁区和迁移规则。
- 明确 remake 不直接读取 `short-drama/references/overseas/*`，避免原创出海规则污染复刻节点。

---

**v0.4.0**（2026-05-11）

Command Layer：新增轻量 `/仿写` 子命令层，不改 gate/schema/checker。

- 新增 `references/command-layer.md`，统一 `/仿写 开始 / 状态 / 继续 / 帮助 / 骨架 / 换皮 / 定案 / 集纲 / 写集 N / 审稿 N` 的入口映射。
- 新增可选增强入口：`/仿写 方向会`、`/仿写 方案会`、`/仿写 诊断会 N`。这些只做 advisory，不解锁 gate，不生成正文，不写 registry current pointer。
- 明确 `/仿写 状态 PROJECT_DIR` 是只读恢复入口，`/仿写 继续 PROJECT_DIR` 只推荐下一步，不越权写正文。
- 明确 `/仿写 写集 N` 仍必须经过 `script_draft.preflight`，下一集继续仍以 `script_draft.postflight` 为唯一解锁信号。
- 每一步输出必须交代已生成文件、文件作用、推荐下一步和可选增强项。

**v0.3.1**（2026-05-11）

UX Patch：补齐 `/仿写` 普通用户引导，不改 gate/schema/checker。

- 新增首轮 `/仿写` 引导契约：说明当前是参考剧本拆解复刻、需要上传/粘贴/提供剧本路径、会先判断材料范围和拆骨架。
- 新增阶段完成摘要要求：输出当前阶段、已完成内容、关键文件/产物、当前限制和为什么推荐下一步。
- 新增导入后文件地图模板，解释 `manifest.yaml`、`source-index.json`、`episode-map.md`、`01_skeleton/`、`02_concepts/` 等文件的用户用途。
- 新增用户可读 blocking summary 模板：卡在哪里、影响什么、为什么不能继续、复制哪句话继续。
- 修正 `short-drama/使用说明.md` 的 `/仿写` 示例，避免已安装用户被误导去重装。

**v0.3.0**（2026-05-10）

Postflight Reliability：增强 managed remake 项目的写后 gate，防止候选剧本未闭环就误解锁下一集。

- 新增 postflight fixture：`postflight_missing_user_review_blocks_next_episode`，覆盖“候选稿已生成、质量初审通过，但用户未确认 / canon 未提交 / state 未更新时不能继续下一集”的失败路径。
- 扩展 deterministic checker：校验 postflight `report_status` 枚举、passed 所需子状态、非 passed 禁止 downstream unlock、postflight report 不得写 registry-owned 字段、postflight 必须消费上游 report 和候选稿 artifact。
- 补充 `postflight_report` schema 字段与禁止字段，明确 `quality_gate_status=passed` 不等于下一集可解锁。
- 新增极薄 agent contract：`agents/contracts/script-postflight-auditor.yaml`，只作为 `script_draft.postflight` 的角色边界，不引入平台级 agent runtime。
- 更新 `short-drama-remake/README.md` 的 postflight 使用说明。

**v0.2.0**（2026-05-09）

Phase 6 Packaging & Release：把 Phase 4/5 的 managed project gate 打包成可发布版本。

- 新增正文前硬闸门使用路径：`/仿写` 进入 `short-drama-remake`，正文生成前必须通过 `script_draft.preflight`，被阻断时只输出一个 user-visible blocking summary，且 `body_generated=false`。
- 新增 schema contract：`references/schema/artifact-registry.yaml`、`node-route-table.yaml`、`reports.yaml`，统一 `artifact_status`、注册表派生 `gate_status`、report `report_status`、current pointer、transaction ref 和 forbidden reads。
- 新增 deterministic checker 与回归矩阵：`scripts/remake_gate_checker.py`、`references/checker/deterministic-checker.md`、`references/fixtures/`，覆盖原始失败案例、P9/P10/P11/P12 交叉 gate、反冗余和 forbidden read。
- 明确 P10 反冗余：正文前 gate 只消费 `resume_packet`、FGR、SIR、RMR，不重跑 P9/P11/P12 完整节点。
- 更新发布验证命令：self-test、全部 fixture dry run、`py_compile`。

**v0.1.0**（2026-05-07）

首版短剧拆解复刻能力：支持长剧本 ingest、完整/部分源文件 gate、可复刻骨架、换皮方向、项目策划、集纲和正式剧本。
