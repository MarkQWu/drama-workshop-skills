---
layer: foundation
control: hard_gate
authority_id: short-drama.continuity-protocol
canonical_path: references/continuity-protocol.md
read_when: /分集, /自检, /角色一致性, /导出, /分镜
---

# 连续性协议（Continuity Protocol）

本协议负责原创短剧的跨集剧情记忆。目标是让长篇项目继续使用 `/分集 next`，但不再依赖模型临时记忆硬撑。

## 职责边界

| 文件 | 职责 |
|---|---|
| `creative-plan.md` | 全剧前提、结局方向、原始创作承诺 |
| `characters.md` | 角色静态档案、性格、身份、称呼、voice 样本 |
| `episode-directory.md` | 每集预定功能 |
| `continuity-ledger.md` | 角色动态状态、活跃主线伏笔、分集索引 |
| `used-lines.md` | 已用高复读风险表达和首集传播句 |
| `episodes/epNNN.md` | 剧本正文和本集隐藏 `CONTINUITY` 摘要 |

`continuity-ledger.md` 管“剧情现在处于什么状态”；`used-lines.md` 管“哪些表达已经用过”。二者不得混写。

## 项目文件：continuity-ledger.md

`continuity-ledger.md` 放在项目根目录：

```text
~/short-drama-projects/<项目名>/continuity-ledger.md
```

首次创建模板：

```md
# 连续性台账

> 由 /分集 自动维护。用于跨集承接、角色动态状态、主线伏笔和分集索引。

## 角色动态状态

| 角色 | 当前状态 | 关键信息或秘密 | 关系变化 | 最近更新集 |
|---|---|---|---|---:|

## 活跃主线伏笔

| ID | 内容 | 埋设集 | 预期处理 | 关联角色或主线 | 状态 |
|---|---|---:|---|---|---|

状态枚举：`active` / `reinforced` / `paid_off` / `archived`

## 分集索引

| 集数 | 核心事件 | 事实变化 | 尾钩或下一集义务 | 主线伏笔变化 |
|---:|---|---|---|---|
```

Phase 1A 不复制全剧红线全文。全剧红线仍以 `creative-plan.md`、`characters.md`、`setting-bible.md` 为源，ledger 只引用和更新动态状态。

## 每集隐藏块：CONTINUITY

每集只能有一个 `CONTINUITY` 块，必须放在：

```md
<!-- 剧本正文到此结束 -->
```

之后、考据附录之前。

固定字段：

```md
<!-- CONTINUITY
角色状态变化：
伏笔与回收：
尾钩义务：
-->
```

字段含义：

| 字段 | 写什么 |
|---|---|
| 角色状态变化 | 位置、知道/不知道的信息、关系、身份、能力、伤病变化 |
| 伏笔与回收 | 新增主线伏笔、强化、延期、回收方式 |
| 尾钩义务 | 下一集必须承接的具体动作、信息或冲突 |

不要使用 5 字段版本，不要新增商业账本字段。

## /分集 读写流程

生成前：

1. 读取 `.drama-state.json`，确认 active project、mode、medium、completedEpisodes。
2. 读取 `creative-plan.md`、`characters.md`、`episode-directory.md`。
3. 判断 `continuity-ledger.md` 是否存在。
4. 若 ledger 不存在且 `completedEpisodes > 0`，先执行“老项目 bootstrap”，不得先创建空模板。
5. 若 ledger 不存在且 `completedEpisodes` 为空，按本协议创建空模板。
6. 读取 `used-lines.md`。
7. 读取上一集全文。
8. N ≤ 10 可读取全部已完成正文；N > 10 读取 ledger + 上一集全文 + 近 2-3 集 `CONTINUITY` / 分集索引，必要时按伏笔证据精确读取远期正文。

生成中：

1. 不违反 `creative-plan.md`、`characters.md`、`setting-bible.md` 的已确认事实。
2. 若上一集 `尾钩义务` 非空，本集前 3 个动作/对白单元必须承接。
3. 新增身份、关键道具、隐瞒、反转、付费承诺等主线级伏笔时，必须写入 `CONTINUITY` 的 `伏笔与回收`。
4. 回收伏笔时必须写明回收方式。
5. 结尾制造下一集义务时，必须写入 `尾钩义务`。

生成后：

1. 保存 `episodes/epNNN.md`。
2. 追加 `used-lines.md`。
3. 抽取本集 `CONTINUITY`。
4. Read-Modify-Write 更新 `continuity-ledger.md`。
5. Read-Modify-Write 更新 `.drama-state.json#completedEpisodes`。

批量 `/分集 5-8` 时，每写完一集必须先更新 ledger，再写下一集。

## 老项目 bootstrap

老项目已有完成集但没有 `continuity-ledger.md` 时，不得只创建空模板后继续写。

触发条件：

```text
completedEpisodes.length > 0
AND continuity-ledger.md 不存在
```

输入优先级：

1. `episode-directory.md`
2. 最近 3 集正文
3. 已有 `checks/` 摘要
4. 必要时按伏笔或角色状态冲突精确读取更早集

最小产物：

1. `## 分集索引` 至少覆盖最近 3 集；若总完成集少于 3 集，则覆盖全部已完成集。
2. 若上一集有尾钩，写入上一集“尾钩或下一集义务”。
3. 能确认的角色动态状态写入 `## 角色动态状态`。
4. 能确认的主线伏笔写入 `## 活跃主线伏笔`。

输出提示：

```text
[连续性] 已为老项目生成连续性台账初版，建议继续写 1-2 集后再补全远期索引。
```

## /自检 连续性对账

`/自检` 的“主线与连贯性”维度增加三问：

1. 是否承接上一集 `尾钩义务`。
2. 是否无事件触发地改写角色状态、关系或已发生事实。
3. 是否出现主线级伏笔但未登记到 `CONTINUITY` / ledger。

hard gate 分层：

| 问题 | 分层 |
|---|---|
| 无事件触发改写角色已知信息 | `[地基层阻断]` |
| 遗漏上一集尾钩承接 | `[骨架层修复]` |
| 主线级伏笔未登记 | `[骨架层修复]` |
| 角色口吻弱或辨识度不足 | `[血肉层建议]` |

主线级伏笔未登记不阻断当前集保存，但阻断继续 `/分集 next` 前的状态闭环。

## /角色一致性 对账

加载资料：

```text
characters.md + continuity-ledger.md + 目标集正文
```

检查重点：

1. 静态角色档案是否被违反。
2. 动态状态是否连续。
3. 角色知道/不知道的信息是否错乱。
4. 关系进度是否跳跃。
5. 能力、伤病、身份是否前后矛盾。

抽样优先用 `continuity-ledger.md#分集索引` 定位相关集；ledger 证据不足再 grep 全文。

## /导出 健康提示与梗概输入

导出前提示：

| 情况 | 行为 |
|---|---|
| ledger 缺失 | 提示建议补连续性台账，不阻断 |
| 已自检不合格集数 | 沿用现有阻断 |
| `CONTINUITY` 缺失 | 提示状态闭环不完整，不单独阻断导出 |

最终梗概综合输入优先级：

1. `creative-plan.md` 白名单字段
2. `continuity-ledger.md#分集索引`
3. 必要时读取剥离后的 `episodes/` 正文

`/导出 {N}` 单集导出必须先生成剥离后的临时 markdown，再调用 `export_docx.py`。不得直接把包含 `CONTINUITY` 的 `episodes/epNNN.md` 交给 pandoc。

`/导出 --with-bible-ref` 的剥离规则必须分两步：

1. 删除 `<!-- CONTINUITY ... -->` 机器块。
2. 保留正文结束边界之后的考据附录。

也就是说，默认导出是“只保留正文边界前内容”；`--with-bible-ref` 是“保留正文 + 考据附录，但删除 `CONTINUITY` 块”。

## /分镜 正文剥离规则

`/分镜` 只处理 `<!-- 剧本正文到此结束 -->` 之前的正文。

`CONTINUITY` 和考据附录一样跳过，不进入镜头拆分、prompt 汇总或合并分镜。

## 失败处理

| 失败 | 处理 |
|---|---|
| ledger 不存在 | `/分集` 前创建；老项目先 bootstrap |
| 本集缺 `CONTINUITY` | 当前集可保存，但阻断继续 `/分集 next` |
| 主线级伏笔未登记 | 标 `[骨架层修复]`，补 `CONTINUITY` 和 ledger |
| ledger 与正文冲突 | 以正文证据为准，要求修 ledger 或修正文，不得静默覆盖 |
| `/导出` 误含 `CONTINUITY` | 先查边界位置和单集导出临时文件逻辑 |
| `/分镜` 误拆 `CONTINUITY` | 先查正文边界剥离说明 |
