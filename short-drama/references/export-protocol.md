# 导出执行协议

> 本文件由 `/导出` 命令读取，包含梗概综合、人物小传、hash 规范化的完整执行规则。
> 概览与质量门控见 SKILL.md `/导出` 段。

---

## 梗概综合执行协议

### 输入字段白名单

加载规则：字段缺失静默跳过，不报错；不得读取白名单外字段。

- `creative-plan.md`：一句话故事线 / 核心冲突 / **时空背景** / 国内字段（三幕结构 / 付费卡点规划 / 爽点矩阵）或出海字段（target market / genre promise / relationship grammar / power system / story function map / paid-pressure map）/ 结局设计 / anchor（如有）
- `.drama-state.json`：`logline` / `lastSynopsisTimestamp` / `lastSynopsisEpisodeCount` / `lastSynopsisEpisodeHash` / `lastSynopsisPath`
- `continuity-ledger.md`：优先读取 `## 分集索引`；文件缺失时静默跳过并提示建议补台账
- `episodes/`：`completedEpisodes` 列表中每个 entry 对应的 `ep{entry}.md` 正文（按考据附录剥离规则剥离后的版本）

### 字段名模糊匹配规则

适用于 `creative-plan.md` 字段定位：
- 忽略开头的中文序号 + 全/半角顿号 + 空格（正则 `^[一二三四五六七八九十]+[、.]\s*`）
- 忽略后续的括号附注（如 "（IAP 模式）"）
- 按核心语义字段名匹配（如 "时空背景" 命中 "## 三、时空背景"）

### episodes/ 文件映射规则

- 按 entry 字面值组路径（entry="001" → `ep001.md`；entry="001-v2" → `ep001-v2.md`）
- 文件不存在 → 跳过该 entry + 打印 `[warn] completedEpisodes 含 {entry} 但 ep{entry}.md 不存在，已跳过 hash 计算`

### hash 规范化规则

保证 LLM 驱动的 md5 确定性：
1. 每集正文读入后：按 `<!-- 剧本正文到此结束 -->` 边界剥离附录
2. 字符串规范化：`content.replace('\r\n', '\n').strip()`（LF 归一 + 两端空白 strip）
3. 按 `sorted(completedEpisodes)` **字典序升序**拼接
4. 集间分隔符：`\n---EP_BOUNDARY---\n`（防段落粘连）
5. 算法：`hashlib.md5(joined.encode('utf-8')).hexdigest()`
6. 执行：LLM 用 Bash tool 调 `python3 -c "import hashlib; ..."` 算 hash，不在 LLM 上下文里目视 hash

### 执行步骤

| 步骤 | 执行逻辑 | 校验断点 |
|------|---------|---------|
| 1 · 幂等性检测 | 读 state 的 `lastSynopsisEpisodeCount` 与 `lastSynopsisEpisodeHash`，算当前 hash 对比 | 双条件均匹配 → 读 `.drama-state/synopsis-cache.md` 直接进 docx（跳至步骤 5）。`--force-resynth` / 缓存不存在 → cache miss |
| 2 · 长度探测 | 按 `completedEpisodes` 数判定 | ≤60 → 全文模式；>60 → 分批蒸馏（beats + 白名单骨架字段同时进 LLM） |
| 3 · LLM 综合 | 按白名单加载 → 生成最终梗概（3-5 段叙事） | 输出 3-5 段 / 禁用词表扫描通过 |
| 4 · 自动采用 | 展示综合梗概预览，自动写入 Word + 缓存，**不回写 `creative-plan.md`** | — |
| 5 · docx 写入 | 按 `references/output-templates-aux.md#导出` 组装内容块；行业稿标准顺序为剧情介绍（可选）→剧情脉络（可选）→人物介绍（可选）→分集梗概（可选）→正文/分集（必选）。若用户未明确选择内容块，先输出选择提示；除非用户明确要求重排，否则顺序不变 | docx 合法 Word 2007+；版式必须是《女相师》类行业交付稿 |
| 6 · 缓存写入 | 综合梗概落 `.drama-state/synopsis-cache.md`；state 更新 4 个 `lastSynopsis*` 字段 | Read-Modify-Write 不覆盖其他字段 |

### 老项目 fallback / migration

- `creative-plan.md` 不含故事梗概段 → 从其他白名单字段综合，缺失字段静默跳过
- 老项目 state 无 `lastSynopsis*` 4 字段 → 视为 cache miss，自然生成；无需迁移脚本
- `lastSynopsisPath == ""` 时不尝试读缓存文件

---

## 人物小传合成协议

### 输入字段白名单

字段缺失标 `[待补充]`，不阻断生成。

- `characters.md`：姓名 / 年龄 / 外貌特征 / 性格关键词 / **公开身份** / **真实身份** / 核心动机 / 冲突点 / 角色弧线（起点→转折→终点）/ 感情线弧线 / **角色关系图**（Mermaid graph TD）/ **称呼关系表**（N×N）
- `.drama-state.json`：`characterCardsGenerated`（按列表顺序取前 2 位作为"主要角色参照"）

**注意**：身份与关系段是导出派生内容，不新增 `characters.md` 字段。

### 执行步骤

| 步骤 | 执行逻辑 | 校验断点 |
|------|---------|---------|
| 1 · 遍历角色 | 读 `characterCardsGenerated` 前 2 位作为主要角色参照。数量不足 2 → 以可用数量参照 + warn | 所有角色各一段 |
| 2 · 首句 | `{姓名}：{年龄/身份/关系...}`，最终导出为单个自然段，不使用 `###` 小标题 | 格式一致 |
| 3 · 外貌段 | LLM 轻润色 `外貌特征` → 1-2 句自然描述 | 无 bullet / 表格痕迹 |
| 4 · 身份与关系段 | 合成前 Exception 扫描（`质量rules.md` Type 6 词）；公开+真实身份→首句；从关系图/称呼表取显式关系，补充从动机/冲突推断隐式关系 | 须有字段支撑，不编造情感色彩；所有字段缺失 → 整段写 `[待补充]` |
| 5 · 性格句 | LLM 轻润色 `性格关键词` → 1-2 句，合入同一自然段 | 无 bullet 残留 |
| 6 · 角色发展句 | LLM 融合 `角色弧线` + `感情线弧线` → 2-3 句叙述，合入同一自然段 | 体裁 bullet→段落，不增删事实 |

### 润色原则

- 允许：关系图（Mermaid 节点语义）/ 称呼表转为自然语言
- 禁止：补充字段未出现的情感色彩（如"暗流涌动的张力"/"命运般的相遇"除非字段明示）
- 只改体裁（bullet → 段落），不增删事实；不扩写未在字段中的情节
- 不使用 AI slop 辞藻（参见 `quality-rules.md` 禁用词表 Type 1-5 全局 + Type 6 仅本合成路径）
- 润色后**不回写** `characters.md`

## Word 版式协议

- `prepare_export.py` 是导出准备层：负责范围解析、缺集检查、正文剥离、集数合并、固定菜单、分集梗概抽取、导出名解析、名称不一致确认和临时 Markdown 构建。
- `export_docx.py` 是 Word 渲染层：只负责把准备好的 Markdown 转成 `.docx`，并兜底版式与 Markdown 清理。
- 导出脚本负责最终版式兜底：A4，左右 1.25 inch / 上下 1 inch，宋体 12pt，全文加粗，1.5 倍行距。
- Markdown 标记不得进入 Word：`#` / `##` / `###`、`**`、反引号、代码围栏、分隔线均需清理。
- 单集/多集范围导出默认剥离内部创作骨架：每集的 `分集定位`、`本集骨架` 及其紧随的空行、bullet、字段行不进入交付稿；若没有分隔线，遇到 `△`、场景头、集标题或角色对白等正文起点必须停止剥离，不能吞掉正文。
- 多集范围导出必须先用 `prepare_export.py` 按集数升序合并剥离后的正文，再调用 `export_docx.py`；`export_docx.py` 不得重新读取项目目录或自行推断集数范围。
- 完整导出必须传 `--full` 或等价完整导出标记，输出文件名为 `export/{剧名}-完整剧本.docx`；局部范围导出使用 `export/{剧名}-ep{AAA}-ep{BBB}.docx`，避免完整稿与范围稿混淆。
- 剧集文件标准命名为 `episodes/ep001.md`、`episodes/ep002.md`。若导出范围内标准文件缺失，但 `episodes/` 下存在疑似改名文件（如 `第1集-新版.md`、`001-开局.md`），`prepare_export.py` 必须阻断并输出具体选择：A 重命名为标准文件名后重跑；B 明确指定本次导出使用哪个文件，脚本用 `--episode-file-map "1=第1集-新版.md"` 重跑且不改文件名；C 取消导出并先整理目录。不得自动猜测候选文件。
- 完整导出和多集范围导出的内容块由上层按用户选择组装；脚本只做版式与 Markdown 清理，不替用户新增不存在的剧情信息。
- 多集范围导出若未说明内容块，必须先引导用户选择 A/B/C/D：标准行业稿（剧情介绍+剧情脉络+人物介绍+分集梗概+正文）、试读精简稿（剧情脉络+人物介绍+分集梗概+正文）、纯正文、自定义编号。
- 若 `prepare_export.py` 对所选方案报告缺少语义块，LLM 必须生成对应临时块文件后重跑，不得让占位符进入最终 docx。
- 若用户改名，优先传 `--title "{新剧名}"`；若未传，脚本按 `dramaTitle > projectName > 目录名` 解析导出名。若 `dramaTitle/projectName/目录名` 不一致，脚本必须阻断并输出具体选择要求：A 使用 dramaTitle、B 使用 projectName、C 使用目录名、D 手动输入新导出名、E 同步修正 `.drama-state.json` 后再导出。A/B/C/D 只影响本次导出名，用 `--title` 重跑，不修改 state；E 必须有用户明确授权。含 `/ \ : * ? " < > |` 的导出名必须阻断。

## 分集梗概协议

- 分集梗概是正文前的可选内容块，位置固定在人物介绍之后、正文之前。
- 完整导出覆盖全部已完成集数；范围导出只覆盖选定集数，如前 10 集只生成第一集至第十集梗概。
- 优先来源：`episode-directory.md` 中对应集数的分集一句话/分集摘要；若缺失，脚本只报告缺少 `4:分集梗概`，由 LLM 基于剥离后的 `episodes/ep{NNN}.md` 生成临时分集梗概文件，再用 `--episode-summaries-file` 重跑。脚本不得自行压缩正文生成语义摘要。
- 分集梗概是交付稿摘要，不包含 `分集定位`、`本集骨架`、商业账本、连续性注记或考据附录。

---

## 考据引用附录与 CONTINUITY 处理

默认剥离：读取每集 `episodes/ep{NNN}.md` 按 `<!-- 剧本正文到此结束 -->` 切分，只保留边界之前的剧本正文。

- 传 `--with-bible-ref` 时：先删 `<!-- CONTINUITY ... -->` 机器块，再保留正文 + 考据附录
- `CONTINUITY` 永远不得进入 docx 正文或梗概输入
- 此剥离规则同时适用于梗概综合 LLM 输入（hash 计算与正文输入）与 docx 写入
- Fallback：未检测到边界（老集数 v1.15.7-）→ 保留全文；多个边界 → 以第一个为准
