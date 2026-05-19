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
| 5 · docx 写入 | 按 `references/output-templates.md#导出` 三段式渲染 | docx 合法 Word 2007+ |
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
| 2 · 标题 + 首句 | `### {姓名}` + `{姓名}，{年龄}。` | 格式一致 |
| 3 · 外貌段 | LLM 轻润色 `外貌特征` → 1-2 句自然描述 | 无 bullet / 表格痕迹 |
| 4 · 身份与关系段 | 合成前 Exception 扫描（`质量rules.md` Type 6 词）；公开+真实身份→首句；从关系图/称呼表取显式关系，补充从动机/冲突推断隐式关系 | 须有字段支撑，不编造情感色彩；所有字段缺失 → 整段写 `[待补充]` |
| 5 · 性格段 | LLM 轻润色 `性格关键词` → 1-2 句 | 无 bullet 残留 |
| 6 · 角色发展段 | LLM 融合 `角色弧线` + `感情线弧线` → 2-3 句叙述 | 体裁 bullet→段落，不增删事实 |

### 润色原则

- 允许：关系图（Mermaid 节点语义）/ 称呼表转为自然语言
- 禁止：补充字段未出现的情感色彩（如"暗流涌动的张力"/"命运般的相遇"除非字段明示）
- 只改体裁（bullet → 段落），不增删事实；不扩写未在字段中的情节
- 不使用 AI slop 辞藻（参见 `quality-rules.md` 禁用词表 Type 1-5 全局 + Type 6 仅本合成路径）
- 润色后**不回写** `characters.md`

---

## 考据引用附录与 CONTINUITY 处理

默认剥离：读取每集 `episodes/ep{NNN}.md` 按 `<!-- 剧本正文到此结束 -->` 切分，只保留边界之前的剧本正文。

- 传 `--with-bible-ref` 时：先删 `<!-- CONTINUITY ... -->` 机器块，再保留正文 + 考据附录
- `CONTINUITY` 永远不得进入 docx 正文或梗概输入
- 此剥离规则同时适用于梗概综合 LLM 输入（hash 计算与正文输入）与 docx 写入
- Fallback：未检测到边界（老集数 v1.15.7-）→ 保留全文；多个边界 → 以第一个为准
