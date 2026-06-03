# /分集执行协议

> 本文件由 `/分集 {N}` 读取，承接引用加载、生成规则、Ep1 设计卡、medium 分叉、连续性台账、used-lines 写入和结束提示。
> SKILL.md 只保留入口、前置条件和协议指针。

---

## 加载参考

**A. 基础加载（永远读）**
- `three-layer-control.md` — 锁本集 story job / entry pressure / turning point / exit hook
- `dialogue-craft-cn.md` — 对白三问 + 对白下限

**B. medium 分叉（按 `.drama-state.json#medium` 选 1）**
- `medium="ai_live"`（默认/缺失）→ Read `ai-live-rules.md`
- `medium="comic"` → Read `comic-rules.md`

**C. mode 分叉（按 `.drama-state.json#mode` 选 1）**
- `mode="domestic"`（默认）→ Read `commercial-ledger-cn.md`
- `mode="overseas"` → Read `references/overseas/` 分层资料（详见 /出海 命令完整清单），不读国内商业账本

**D. 条件加载（按条件 if 触发）**
- `opening-rules.md` — 仅 N=1 时 Read（第 1 集首集留存强建议），N≥2 跳过
- `continuity-protocol.md` — 仅 N>1 时 Read（跨集剧情记忆）
- `hook-design.md` — 仅写集末钩子时 Read 核心 30 行（事件钩定义段）
- `setting-bible.md` — 存在则读（专业细节强制引用）
- `used-lines.md` — 存在则读（跨集台词去重；加载/写入协议见 `used-lines-protocol.md`）
- `continuity-ledger.md` — 存在则读；不存在按 `continuity-protocol.md` 创建或 bootstrap
- `characters.md` — 存在则读；只读「声音指纹#禁用清单」+「应激模式」两个字段
- `creative-intent-ledger.md` — 仅当 creative-plan.md 缺失 intent 字段时 Read（防分集背离原始前提）
- `vertical-drama-craft.md` — 仅 `episodes/ep{NNN}.md` 已存在（重写/精修）或 `--refine` 标志或上一轮 /自检 有工艺类问题时 Read
- `dramatic-truth.md` — 仅 `episodes/ep{NNN}.md` 已存在（重写）时 Read
- `script-element-extraction.md` — 从 /分集 移除，仅 /分镜 时 Read（/分集 生成剧本正文不需要元素分层管线）

**E. 输出格式指针（按 medium 路由 anchor，section read）**
- `medium="ai_live"` → `references/output-templates-core.md#分集国内模式`
- `medium="comic"` → `references/output-templates-core.md#分集国内模式-comic`
- `mode="overseas"` → `references/output-templates-core.md#分集出海模式`

## 生成前上下文注入

**anchor inline + `--fix anchor-rhythm` 子命令：** 如 `creative-plan.md` 有 `anchor` 字段，按 `references/anchor-trigger.md#分集-anchor-inline` 把 anchor prompt 模板 inline 到分集生成 prompt；无 `anchor` 字段则跳过。节奏污染时 `/分集 N --fix anchor-rhythm` 重写（详见 `references/anchor-trigger.md#fix-anchor-rhythm-子命令`）。

**圆桌处方加载（重写/修改场景）：** 当 `episodes/ep{NNN}.md` 已存在时（重写/修改场景），优先加载 `roundtables/` 目录下 ep{NNN} 对应的最新诊断文件。若文件存在，提取 `<!-- PRESCRIPTIONS -->` 块，将处方列表 inline 到重写 prompt 前置上下文中（格式：`[圆桌处方] 处方1 | 处方2 | ...`）。无文件则跳过，不影响正常生成流程。

## 生成规则

- **破折号禁用：** 剧本正文不出现破折号。禁止 `——`、`—`、`--`，包括台词停顿、被打断、场景补充说明、心理独白引出。需要停顿或打断时，用动作描写、换对话轮次、完整句、句号、逗号或中文省略号「…」替代。不把它留给 /自检 再返工。双层防线：生成层禁用 + 自检层出现即标【严重】。
- **画面可拍性实时节制：** 写 △ 段落时问自己：摄影机能拍到这句吗？OS/VO 层允许诗意比喻（anchor 红利承载位），△ 场景叙事层必须可拍（物件 / 动作 / 环境 / 表情）。生成阶段只执行本句内联原则，不额外读取 `quality-rules.md`；详细扣分留给 `/自检`。
- **专业细节引用规则：** bible 存在时，所有专业术语/官名/制度/数字/药物剂量/法条必须映射到 bible，否则改模糊或标 `[虚构]`；不额外读取 `quality-rules.md`，考据追溯评分留给 `/自检`。
- **三层生成边界：** 生成时硬控地基层和骨架层，不把血肉层的具体台词、微动作、比喻数量、句式节奏写成固定模板。若血肉选择无法完成本集 `locked_episode_job`，先修骨架执行；若只是风格强弱，留给 `/自检` 或 `/圆桌诊断` 做建议。
- **商业账本对账（国内模式）：** 生成前读取 `creative-plan.md#商业账本` 和 `episode-directory.md` 的目录版商业职责；本集写完后在集末自查补齐本集买单理由、付费/尾钩压力、爽点兑现状态、反派压力变化。缺失时先补结构职责，不用空泛口号代替。
- **对白下限 + 三问：** 写每场对白前先按 `dialogue-craft-cn.md#对白合理性下限` 情境驱动准则确保本场对白下限达标（≥2 角色同框有戏剧动态、关键剧情节点、独角戏外部触发等场景必须有对白），再按 `dialogue-craft-cn.md#/分集：对白三问` 优化已写对白的质量。三问是优化工具，不是用来削减对白到下限以下。

## Ep1 设计卡流程

N=1 且 `mode=domestic` 专用；N≥2 或 `mode=overseas` 跳过本段。

执行 `/分集 1` 前先读取 `.drama-state.json#mode`。若 `mode="overseas"`，跳过国内 Ep1 设计卡流程，改按 `references/overseas/hard-rules.md` Rule 10 + `references/overseas/anti-patterns.md` 的海外首集规则执行：首集优先 active conflict / mid-conflict 直入，不能套用国内冷开场强建议、有效爽点判定、事件钩首集规则或首集传播句提取。

第 1 集是首集留存的决战场。国内模式下，`/分集 1` 不直接写正文，按以下三步走，无 fast-track。

**Step 0：生成 Ep1 设计卡**

产出文件：`episodes/ep001-design-card.md`。10 字段必填，缺任一即重生设计卡：

1. 开场路径：传统路径（人物→冲突→困境）/ 高燃路径（5 秒爆点直入）——二选一
2. 开场模板：从 `opening-rules.md` 6 模板中选 1（直接打脸 / 身份反转 / 极端困境 / 误会激化 / 关键决断 / 危机降临）
3. 首屏冲突：第 1 个动作/对白单元具体演什么（不是“被羞辱”，而是“哪句话/哪个动作落到主角身上”）
4. 主角痛点：主角被什么具体的人/事/物压制（具象不抽象）
5. 压迫者动作：压迫者用哪个具体动作建立力量优势
6. 信息差：观众知道什么主角不知道？或主角知道什么旁人不知道？（首集至少 1 个）
7. 完整爽点弧（4 节点）：痛点 → 蓄力 → 小释放 → 余震，逐节点写一句话；生成阶段不额外读取 `satisfaction-matrix.md`，只按“具体痛点 / 明确蓄力 / 可见小释放 / 余震反应”四项至少三项成立判断
8. 观众承诺：本集结束观众会期待第 2 集兑现什么具体钩子？（不是“看下去”，而是“看 X 怎么发生”）
9. 尾钩事件：能回答“下一秒谁要做什么”的事件钩；OS 立誓 / 独白 / 回忆 / 抽象质问不接受为单独尾钩（按加载规则仅在写集末钩子时读取 `hook-design.md` 核心 30 行）
10. 第 2 集承接：尾钩在第 2 集前 3 单元怎么兑现的具体动作

**Step 1：先写前 30 秒并自检**

- 设计卡通过后，只写前 30 秒（约前 3 个动作/对白单元）正文，不写全集。
- 自检 2 项留存风险：
  - `opening-rules.md#首集冷开场强建议` 4 项优先满足（可见冲突 / 弱势处境 / 明确压迫者 / 信息差或身份差）
  - 0-3s 冲突点 `[锚点]` 标记齐
- 缺任一项 → 标为首集留存风险，优先微调或重写前 30 秒；若 3 轮仍不理想，回炉 Step 0 改设计卡。

**Step 2：写完整集 + 提取首集传播句**

- 前 30 秒达标后再写到 EP01 完整正文。
- 写完后按常规自检流程，额外提取 1 条 `[首集传播句]`（≤12 字优先 / 角色化 / 可回收）写入 `used-lines.md`，详见 `used-lines-protocol.md#首集传播句`。

## medium 分化生成流程

- `medium="ai_live"`（默认）→ 自由文本生成，遵循 `ai-live-rules.md` 规则（3-5 场 / 长台词按节奏风险评估 / 微表情按可控性评估）。
- `medium="comic"` → 两步结构化生成：
  1. Step 1 先产 JSON 场次清单：`[{"scene_id": "1-1", "time": "日|夜", "loc_type": "内|外", "location": "...", "purpose": "一句话"}]`，数组 `length ∈ [1, 3]`（H1 硬约束）。
  2. Step 2 按清单逐场展开（△ 分镜 + 对白 + OS/VO 情绪标签 + 场景头用 `N-N日/外或内 地点` 格式）。
  3. JSON 解析失败容错：重试 1 次 → 仍失败则 fallback 到自由文本 + 强 prompt 提醒“≤3 场 · 严格分场头格式”，自检后必须复审。

## 输出与质量要求

输出格式先按 `.drama-state.json#mode` 判断：`mode="overseas"` 优先使用出海模板；否则再按 `.drama-state.json#medium` 路由：

- `medium="ai_live"` 或缺失 → `references/output-templates-core.md#分集国内模式`
- `medium="comic"` → `references/output-templates-core.md#分集国内模式-comic`
- `mode="overseas"` → `references/output-templates-core.md#分集出海模式`

本集必须完成 `three-layer-control.md` 锁定的 story job，场景可拍，专业细节有据，连续性承接清楚，格式 marker 齐全；完整评分 rubric 留给 `/自检`。

保存为 `episodes/ep{NNN}.md`（三位数补零）。

## 连续性台账

- 生成阶段按 `continuity-ledger.md`、上一集尾钩义务和近集 `CONTINUITY` 承接；发现无法承接时先修本集开头，不继续生成完整集。
- N ≤ 10 可读全部已完成正文；N > 10 不默认读全部历史正文，改读 ledger + 上一集全文 + 近 2-3 集 `CONTINUITY` / 分集索引，必要时按伏笔证据精确读取远期正文。
- 生成前读取或创建项目根 `continuity-ledger.md`。若老项目 `completedEpisodes > 0` 且 ledger 不存在，先按 `references/continuity-protocol.md#老项目-bootstrap` 生成轻量台账，再写下一集。
- 若上一集 `CONTINUITY` 的 `尾钩义务` 非空，本集前 3 个动作/对白单元必须承接；无法承接时先修本集开头，不继续生成完整集。
- 生成中出现身份、关键道具、隐瞒、主线反转、付费承诺、关系转折前置线索时，必须写入本集 3 字段 `CONTINUITY`。
- 生成后按 Read-Modify-Write 更新 `continuity-ledger.md`，再更新 `.drama-state.json#completedEpisodes`。批量 `/分集 5-8` 时，每写完一集先更新 ledger，再写下一集。
- 更新 ledger 前检查其“分集索引”section 实际行数：若 > 15 行（实际集数 > 13），先按 `references/continuity-protocol.md#ledger-归档协议` 执行归档（活跃伏笔中 paid_off/archived 条目移出，分集索引保留最近 10 集 + 1 行归档摘要），再写入本集；若 ≤ 15 行直接更新，无需归档。

## used-lines 写入

本集保存后，提取 3-5 条“高复读风险台词”（情绪锚句 / 遗言告别 / 口头禅 / 3 字以上标志性形容词组合 / 特殊意象），按 Read-Modify-Write 协议追加到 `used-lines.md` 新 section `## ep{NNN}`。

格式：`- "台词原文" [角色][场景 one-liner][类别]`。硬下限 3 条，少于 3 条视为未执行。详细判定标准/反模式见 `references/used-lines-protocol.md#写入规则`。

追加前先统计 `used-lines.md` 中 `## ep` section 数量：若 > 15，先按 `references/used-lines-protocol.md#归档协议` 执行归档（将最早的 ep001~ep(N-10) 移至 `used-lines-archive.md`，活跃层保留最近 10 集），再追加本集；若 ≤ 15 直接追加，无需归档。

## 结束提示

- N < totalEpisodes（非最后一集）：`[完成] 第{N}集已保存！输入 /分集 {N+1} 继续，或 /自检 {N} 检查质量`
- N == totalEpisodes（最后一集）：
  ```text
  [完成] 第{N}集已保存！全剧 {totalEpisodes} 集正文写完。
  ▸ 下一步：/自检 all 批量质检所有集数
  ▸ 或先逐集检查：/自检 {N}
  ```

## /导出门控说明

未跑 /自检 的集数在 /导出 时只会标黄提示不阻断；只有 /自检 不合格（低于阈值）的集数才阻断 /导出。自检非强制但推荐。
