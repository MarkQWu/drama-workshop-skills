---
layer: foundation
control: hard_gate
authority_id: short-drama.project-management
canonical_path: references/project-management.md
read_when: /开始, /新建, /分集, /自检, and any command that reads or writes project state
---

# 项目管理（Project Management）

本文件定义 short-drama skill v1.13.0 起的**活跃项目指针架构**。所有 `/开始` / `/新建` / `/分集` / `/自检` 等命令均依赖此规范。

## 核心架构变更（v1.13.0）

放弃 v1.10-v1.12 的 **cwd-based 项目隔离**（依赖用户切换工作目录），改为 **scan-based + state.projectName** 架构：

- **`/开始` 扫描 `~/short-drama-projects/*/` 列出所有项目**，用户显式选择要操作哪本
- **选中后 LLM 用绝对路径读写** `~/short-drama-projects/<projectName>/`，cwd 完全不再影响
- **WorkBuddy 用户零切换**：不再需要 `cd` 或改 WorkBuddy 工作目录
- **跨 session 继承**：每次 `/开始` 都让用户显式选，不依赖隐式记忆

## 项目目录约定

### 默认位置

所有项目统一在 `~/short-drama-projects/<项目名>/`。路径由 `pathlib.Path.home() / "short-drama-projects" / project_name` 解析，跨平台自动展开（macOS/Linux/Windows）。

### 项目内文件清单

所有产出走绝对路径，保存在项目目录下：

```
{项目目录}/
├── brainstorm.md            # 构思记录（选中+淘汰方向 + 原始冲动记录 + 配置决策历史，/开始 写入）
├── README.md                # 项目自述（/项目状态 生成/更新）
├── creative-plan.md          # 创作方案
├── characters.md             # 角色档案
├── setting-bible.md          # 考据 bible（/考据 生成，厚型题材必有）
├── research-cache/           # /考据 auto 检索原始缓存
├── episode-directory.md      # 分集目录
├── used-lines.md             # 跨集台词去重清单（/分集 自动追加 + /自检 扫描）
├── continuity-ledger.md       # 连续性台账（/分集 自动创建/维护）
├── episodes/                 # 分集剧本
│   ├── ep001.md
│   ├── ep002.md
│   └── ...
├── compliance-report.md      # 合规报告（如生成）
├── clashes/                  # 选题会记录（/选题会 生成）
│   ├── clash-20260501-1430.md
│   └── ...
├── roundtables/              # 圆桌诊断记录（/圆桌诊断 生成）
│   ├── rt-ep001-20260501-1450.md
│   └── ...
├── checks/                   # 自检评分详情（/自检 生成，供 /圆桌诊断 读取）
│   ├── ep001-check.md
│   └── ...
├── character-cards/          # 角色视觉卡（/角色卡 生成）
│   ├── {角色名}.md
│   └── ...
├── storyboards/              # 分镜表（/分镜 生成）
│   ├── ep001-storyboard.md
│   ├── prompts-only.txt      # 纯 prompt 列表（脚本提取）
│   └── merged-storyboard.md  # 合并分镜（脚本生成）
├── scripts/                  # Python 工具脚本
│   ├── merge_storyboard.py
│   ├── character_card_validator.py
│   ├── generate_reference_doc.py
│   └── export_docx.py
└── export/                   # 导出目录
    ├── {剧名}-完整剧本.md
    └── {剧名}-完整剧本.docx  # Word 版（可选）
```

## 项目名验证（`/新建` 必走）

拒绝并要求重输的 case：

| 情形 | 错误提示 |
|---|---|
| 空字符串 / 仅空格 | "项目名不能为空" |
| 含路径分隔符 `/` `\` | "项目名不能含路径分隔符" |
| 含 Windows 非法字符 `:` `*` `?` `"` `<` `>` `|` | "项目名含非法字符（Windows 不允许 `:*?\"<>|`）" |
| 是 `.` 或 `..` | "项目名不能是 . 或 .." |
| 长度 > 50 字符 | "项目名超长，确认继续？" |

**合法处理**：两端空格自动 trim；允许中文、数字、英文字母、常见标点（`-` `_` 等）、空格（中间）；emoji 允许但 `/项目列表` 展示可能乱码。

## /开始 扫描 + 列表行为（v1.13.0）

```
/开始 → 扫 ~/short-drama-projects/*/ 收集合法 .drama-state.json
  │
  ├─ 0 项目 + cwd 有 state（v1.10-v1.12 老用户 fallback）
  │   → 加载 cwd state，询问"[1] 就地继续 / [2] 迁移到标准位置"
  │   → 选 2 执行 mv + state 补 projectName 字段
  │
  ├─ 0 项目 + cwd 无 state
  │   → 询问项目名 → 走 /新建 语义
  │
  ├─ 1 项目
  │   → "欢迎回来《X》阶段 Y 进度 N/M。继续？[Y/新建]"
  │
  └─ ≥2 项目（按 mtime 降序列表）
      → "1. 《A》阶段(mtime)
          2. 《B》阶段(mtime)
          ...
          N+1. 新建一本
          
          回复数字或新剧名"
      → 数字选项目 / 新剧名走 /新建
```

**选中后分支**：

- `currentStep` 非空（在建项目）→ 欢迎回来 + 展示进度 + 等下一步命令，不进 Step 3
- `currentStep` 为空（`/新建` 刚建的 stub）→ "欢迎来到《X》" + 直接进 Step 3 锁定观众

**活跃项目锚定**：选中后 LLM 本会话所有产出走绝对路径 `~/short-drama-projects/<projectName>/`。不再读写 cwd。

## /新建 stub state 模板（26 字段完整）

`/新建 <项目名>` 写入 `~/short-drama-projects/<项目名>/.drama-state.json`：

```json
{
  "projectName": "<项目名>",
  "dramaTitle": "<项目名>",
  "currentStep": "",
  "genre": [],
  "audience": "",
  "tone": "",
  "totalEpisodes": 0,
  "completedEpisodes": [],
  "characterCardsGenerated": [],
  "storyboardedEpisodes": [],
  "qualityScores": {},
  "language": "zh-CN",
  "mode": "domestic",
  "medium": "ai_live",
  "shotDensity": "",
  "seedIdea": "",
  "logline": "",
  "settingBibleStatus": "none",
  "bibleScope": [],
  "researchIntensity": "",
  "lastSynopsisTimestamp": "",
  "lastSynopsisEpisodeCount": 0,
  "lastSynopsisEpisodeHash": "",
  "lastSynopsisPath": "",
  "clashes": [],
  "roundtables": {}
}
```

**关键**：必须写 **26 字段全集** 而非仅 2 字段，否则下游 Step 5 存 state 时 overwrite 会丢字段。

### 字段说明：clashes / roundtables（v1.25.0 新增）

**`clashes`**：数组，记录历次 `/选题会` 产出。每个元素结构：
```json
{"file": "clashes/clash-20260501-1430.md", "topic": "会议主题一句话", "timestamp": "2026-05-01 14:30"}
```

**`roundtables`**：对象，键为集数字符串（如 `"1"`、`"5"`），值记录该集最新圆桌诊断。结构：
```json
{"1": {"file": "roundtables/rt-ep001-20260501-1450.md", "timestamp": "2026-05-01 14:50", "diagnosis": "诊断焦点一句话"}}
```

向后兼容：老项目（v1.24.x 及之前）state 无 `clashes` / `roundtables` → 加载时视为 `[]` / `{}`，不破坏现有行为。

### 字段说明：medium（v1.16.0 新增）

`medium` 枚举 `"ai_live"` / `"comic"` 标识承制介质：
- `"ai_live"`（默认）= 仿真人 AI 剧（3-5 场、单条台词 ≤2 句、微表情禁用等）
- `"comic"` = 漫剧 / 动态漫画（≤3 场、单条台词 ≤6 句、OS/VO 带情绪标签等）

向后兼容：老项目（v1.15.x 及之前）state 无 `medium` 字段 → 加载时视为 `"ai_live"` 默认值，不破坏现有生成/自检行为。`/开始` 加载老 state 时会交互询问一次以补齐字段（见 SKILL.md `/开始` 迁移检测逻辑）。

### 字段说明：lastSynopsis*（v1.18.1 新增，PR2）

4 字段共同构成 `/导出 --docx` **最终梗概段**的分离式幂等性缓存。**Scope 限定**：本缓存仅覆盖梗概段（"## 一、故事梗概"），**人物小传段（"## 二、人物小传"）每次 `/导出 --docx` 都会重新跑 LLM 6 步合成流程**——因此同一项目两次导出的 docx 之间，梗概段字节级一致，人物小传段可能字节略异（语义一致但 LLM 润色随机）。扩展 characters 缓存（独立 `lastCharactersHash` + `.drama-state/characters-cache.md`）归 v1.19.0 scope。

| 字段 | 类型 | 语义 |
|------|------|------|
| `lastSynopsisTimestamp` | string (ISO 8601, e.g. `"2026-04-24T10:30:00+08:00"`) | 上次成功综合并用户选 Y 的时间戳 |
| `lastSynopsisEpisodeCount` | number | 上次综合时 `len(completedEpisodes)` 字面快照——**取列表长度，不是实际参与 hash 计算的集数**（某些 entry 对应的 `ep{entry}.md` 可能因移入 `.trash` 等原因缺失而被 hash 跳过+warn，但 count 仍存完整列表长度，与 step 1 双条件的 `当前 completedEpisodes.length` 比对保持口径一致）|
| `lastSynopsisEpisodeHash` | string (md5 十六进制, 32 字符) | `md5(按 completedEpisodes 字典序升序拼接所有完成集 ep{entry}.md 剥离考据附录后正文，经 LF 归一 + 两端 strip + \n---EP_BOUNDARY---\n 分隔)`——作者改已有集正文会让缓存失效 |
| `lastSynopsisPath` | string | 缓存梗概正文相对路径，固定为 `".drama-state/synopsis-cache.md"` |

**缓存命中双条件**（同时满足才命中）：
1. `lastSynopsisEpisodeCount == 当前 completedEpisodes.length`
2. `lastSynopsisEpisodeHash == md5(当前所有完成集剥离考据附录后正文按字典序升序拼接，经规范化)`

**写入时机**：仅当用户在 `/导出 --docx` 三选一提示中选 Y 时，按 Read-Modify-Write 写回 state 并将综合梗概正文落 `.drama-state/synopsis-cache.md`。N / E 分支均不写缓存，也不写 state 4 字段（保持前次值，含空值）。

**向后兼容**：老项目（v1.17.3 及以前）state 无这 4 字段 → 加载时视为 cache miss（自然首次综合），无需显式迁移脚本或交互询问。首次 Y 分支完成后 4 字段落地。`lastSynopsisPath == ""` 时不尝试读缓存文件（视为 miss）。

**`.drama-state/synopsis-cache.md` 格式**：纯 markdown 正文（无 YAML front matter，无 header）。该文件由 LLM 读入重用，不做结构化解析。目录 `.drama-state/` 是 v1.18.1 新增的项目级缓存目录，与同级 `.drama-state.json` 共享命名空间；未来可扩展放其他缓存件。缓存目录首次写入时由 `/导出 --docx` 的步骤 6 执行 `mkdir -p`。

**命名空间说明**：`.drama-state.json`（单文件 state）与 `.drama-state/`（缓存目录）在项目根目录平级共存，命名空间相邻但无内容嵌套关系。未来若 state schema 继续扩展缓存类字段，一律指向 `.drama-state/` 子目录内文件，不嵌入 JSON，避免 Read-Modify-Write 日志膨胀。

**示例**：

`.drama-state.json` 片段：
```json
"lastSynopsisTimestamp": "2026-04-24T10:30:00+08:00",
"lastSynopsisEpisodeCount": 80,
"lastSynopsisEpisodeHash": "a3f5b8c9d2e4f1a6b7c8d9e0f1a2b3c4",
"lastSynopsisPath": ".drama-state/synopsis-cache.md"
```

`.drama-state/synopsis-cache.md`：
```markdown
（第一段叙事梗概）...

（第二段）...

（第三段）...
```

## 重名保护（`/新建` 强制，防覆盖已有项目）

`/新建 X` 前检查 `~/short-drama-projects/X/.drama-state.json`：

| state 状态 | 行为 |
|---|---|
| 存在 + 合法 JSON + `currentStep` 非空（在建项目）| **拒绝**：`"《X》已存在（阶段 Y, 进度 N/M）。继续用 /开始 选该项目，或换新名"` |
| 存在 + 合法 JSON + `currentStep` 为空（stub 残留）| 安全覆盖（前次 `/新建` 中断遗留）|
| 存在 + 损坏/非法 JSON | 询问"state 文件损坏，是否覆盖重建？" |
| 不存在 | 正常建 |

## State 写入协议（强制，防数据损坏）

所有修改 `.drama-state.json` 的操作 **必须** Read-Modify-Write：

```python
# 正确（merge 语义）
state = json.load(open(path))
state["currentStep"] = "创作方案"
state["genre"] = ["古装"]
json.dump(state, open(path, "w"), ensure_ascii=False, indent=2)

# ❌ 错误（overwrite 会丢失其他字段）
json.dump({"currentStep": "创作方案", "genre": ["古装"]}, open(path, "w"))
```

**禁止** 使用 Write 工具直接用部分字段 overwrite state。违反 = 数据损坏。

## 活跃项目识别 fallback（用户未显式 /开始）

用户直接输入 `/分集 N`、`/自检 N` 等命令而未先 `/开始`：

1. 本会话 LLM context 已加载过活跃项目 → 沿用
2. 否则扫 `~/short-drama-projects/*/` 按 mtime desc：
   - 1 个 → 自动加载 + "当前加载《X》（唯一项目）"
   - ≥2 个 → 自动加载 **最近修改** + 明确告知："当前加载《X》（最近项目 mtime），如需切换用 `/开始` 重选"
3. 列表为空 → "请先 `/开始` 或 `/新建 <项目名>`"

## 向后兼容 fallback（v1.10-v1.12 老用户迁移）

`/开始` 触发 fallback 的条件（宽松版，防已有项目失联）：

- **条件 A**：扫描 `~/short-drama-projects/*/` 为空 AND cwd 有合法 `.drama-state.json`
- **条件 B**：扫描结果中没有匹配 cwd 路径的项目，但 cwd 本身有合法 `.drama-state.json`（例：作者在别处手动建过 `~/short-drama-projects/测试/`，但真实项目仍在另一 cwd）

满足 A 或 B → fallback 流程：

1. 加载 cwd state，展示进度
2. 询问两个选项：
   - **[1] 就地继续（兼容模式）**：保留在原 cwd，不迁移。仅当会话内 `/分集` 等命令需要时，LLM 用 cwd 绝对路径读写。**警告**：`/项目列表` 看不到此项目；本会话一结束，下次 `/开始` 再问一次
   - **[2] 迁移到标准位置（推荐）**：按「迁移白名单 + 目标冲突检查」流程执行

### 迁移操作规范（强制，防数据破坏）

**目标冲突检查**：`mv` 之前检查 `~/short-drama-projects/<dramaTitle>/` 是否已存在：
- 不存在 → `mkdir -p` 后 mv
- 存在且 state 合法 + `currentStep` 非空 → 目标已有真实项目，**拒绝迁移**，建议改名（`<dramaTitle>-from-cwd-YYYYMMDD`）让用户确认
- 存在但为空/仅 stub state → 可覆盖（安全）

**迁移文件白名单**（严格，只 mv 以下项，其他文件**不移动**）：

| 文件/目录 | 说明 |
|---|---|
| `.drama-state.json` | 项目状态 |
| `brainstorm.md` | 构思记录 |
| `creative-plan.md` | 创作方案 |
| `characters.md` | 角色档案 |
| `setting-bible.md` | 考据 bible |
| `episode-directory.md` | 分集目录 |
| `continuity-ledger.md` | 连续性台账 |
| `compliance-report.md` | 合规报告 |
| `README.md` | 项目自述（/项目状态 生成的才 mv，项目目录里其他同名 README.md 谨慎）|
| `episodes/` | 分集剧本目录 |
| `character-cards/` | 角色视觉卡 |
| `storyboards/` | 分镜目录 |
| `research-cache/` | 考据缓存 |
| `export/` | 导出目录 |

**白名单外**（例 SKILL.md、scripts/、references/、LICENSE 等 skill 源文件，或用户桌面其他文件）→ **绝不移动**。

## 状态类协议边界

| 文件 | 职责 |
|---|---|
| `project-management.md` | 项目状态、目录结构、迁移白名单、state Read-Modify-Write |
| `used-lines-protocol.md` | 表达记忆，管理已用高复读风险台词和 callback 复用 |
| `continuity-protocol.md` | 剧情记忆，管理角色动态状态、活跃主线伏笔、分集索引和尾钩义务 |

**迁移前强制用户确认**：LLM 列出待 mv 的具体文件清单（包括跳过的非白名单文件）+ 目标路径 + state 变更（补 `projectName` 字段），让用户回复 "确认" 后才执行。

**老 state 补齐 `projectName`**：v1.10-v1.12 的 state 没有 `projectName` 字段。迁移执行时用 `dramaTitle` 值填入（走 State 写入协议 Read-Modify-Write）。

## /项目列表 实现约定

调用 `python3 {skill目录}/scripts/list_projects.py`：

1. 扫 `~/short-drama-projects/*/`，支持 `--dir` 自定义路径
2. 读关键字段：`projectName` / `dramaTitle` / `currentStep` / `completedEpisodes` / `totalEpisodes`
3. `currentStep` 为空标记为 `-（未开始）`区分 stub 项目
4. mtime 排序，输出 Markdown/JSON 表格
5. 无匹配项目 → "暂无项目，使用 `/开始` 或 `/新建` 创建"

## /项目状态 实现约定

在活跃项目上下文中：

1. 读活跃项目 `.drama-state.json`
2. 按 `output-templates-aux.md#README` 模板生成 `~/short-drama-projects/<projectName>/README.md`（绝对路径，不依赖 cwd）
3. 输出"README.md 已更新"

## 跨平台路径处理（强制）

- 所有 Python 脚本用 `pathlib.Path` 而非字符串拼接
- `~` 展开用 `Path.home()` 或 `Path.expanduser()`
- 中文路径确保 UTF-8（Python 3 默认，Windows 某些 shell 需 `encoding='utf-8'`）
- shebang 统一 `#!/usr/bin/env python3`

## 反模式（禁止）

- 硬编码绝对路径（如 `/Users/xxx/short-drama-projects/`）
- cwd-based 项目隔离（v1.10-v1.12 遗留，已废弃）
- Write 直接 overwrite `.drama-state.json`（违反 State 写入协议）
- `/新建` 不做重名保护（会覆盖用户在建项目）

## 迭代记录

- 2026-04-20 v1.12.0 首版：cwd-based 项目目录约定 + 向后兼容 + `/项目列表` `/项目状态`
- 2026-04-20 v1.12.1：`/新建 <项目名>` 独立命令替换 `/开始 --new` flag
- 2026-04-20 v1.13.0：**架构重做**。放弃 cwd-based，改为 scan-based + state.projectName。修复 4 个 🔴 bug：
  - Bug 1：`/新建 <已存在项目名>` 重名覆盖 → 加重名保护
  - Bug 2：Step 5 保存 state 丢字段 → 加「State 写入协议」强制 Read-Modify-Write
  - Bug 3：`/开始 --new` 一小时窗口兼容 → `/开始` 扫描 + 列表，即使用户误输 `--new` 也能从列表找到项目
  - Bug 4：WorkBuddy 默认 cwd 死局 → 完全不再依赖 cwd，用户零切换
  - 新增老用户兼容 fallback（v1.10-v1.12 cwd-state 自动迁移或就地继续两选项）
