# 爆款剧本工坊 | Drama Workshop

**当前版本：v1.35.0**（2026-05-19）· 版本历史见 [GitHub Releases](https://github.com/MarkQWu/drama-workshop-skills/releases) · 小白看 [使用说明](short-drama/使用说明.md)

用 AI 写能拍的微短剧，也能拆解参考短剧做换皮复刻——从选题到分镜，一条命令链走完。

支持所有能加载 Skill 的 AI agent（Claude Code / Codex / OpenClaw / WorkBuddy 等）。

## 它能做什么

仓库包含两个并列能力，安装脚本会一起安装：

- **short-drama**：原创短剧主流程，负责 `/开始`、`/策划`、`/分集`、`/分镜`、`/导出`
- **short-drama-remake**：参考剧本拆解复刻，负责参考剧本 ingest、可复刻骨架、换皮方向、集纲和正式剧本

- **剧本创作**：50-100 集完整微短剧（国内+出海双模式），国内用爽点矩阵/付费卡点，出海用 target market / genre promise / paid pressure 分层；出海默认中文呈现，角色名保留英文
- **拆解复刻**：从参考剧本提炼商业骨架，生成换皮方向、项目策划、详细集纲和正式剧本
- **质量管控**：7 维度 + 考据可追溯 8 维度自检（先推理再评分）、AI Slop 检测、过稿预估、不合格阻断导出
- **三层控制模型**（v1.31.19 起）：原创创作按地基层 / 骨架层 / 血肉层分级，区分必须阻断、结构修复和创作建议，避免规则不足或过度模板化
- **商业账本**（v1.35.0 起）：国内原创会追踪观众买单理由、付费卡点、爽点兑现和反派压力轨迹，避免只写事件不写商业因果
- **出海资料分层**（v1.31.22 起完善）：按平台事实、目标市场、题材承诺、关系/权力语法、结构付费压力、媒介可拍、对白工艺、合规/IP 和反污染分类；hard gate、review、soft craft 分级，避免把国内模板或长剧范式带进海外项目
- **分镜输出**：剧本→逐镜分镜表 + [即梦 AI](https://jimeng.jianying.com) prompt，一步生成视频
- **Anchor 触发机制**（v1.23.0 起全 13 题材）：`/创作方案` 根据选定题材自动推荐中文现象级 IP（覆盖都市情感 / 霸道总裁 / 甜宠 / 重生穿越 / 古装宫廷 / 励志逆袭 / 悬疑探案 / 战神归来 / 家庭伦理 / 萌宝 / 软科幻 / 末日重生 / 喜剧全部 13 题材），借世界观厚度 / 角色调性 / 情绪锚点，**不借节奏**（节奏仍由 skill 自身规则硬约束）
- **付费卡点商业模式分层**（v1.14.0 起）：IAP / IAA / 混合三种付费结构分开设计，适配国内 IAA 主导市场
- **多项目管理**（v1.13.0 起）：`/开始` 先问新建/继续，选继续再按需扫描，`/新建 剧名` 直接开新本，互不干扰，WorkBuddy 用户零切换目录
- **跨集角色一致性**（v1.21.0 起）：`/角色一致性` 脚本层（年龄/发色/眼色/身高矛盾）+ LLM 语义层（性格/动机/弧线漂移）两层扫描，定位到具体集数和上下文
- **呈现格式分化**：`/出海` 默认中文短剧格式 + 中文对白，角色名保留英文；只有 `/出海 英文交付` 或明确要求英文投稿稿时才使用英文 + Hollywood 格式；剧本正文破折号完全禁用

## 安装

前置条件：已安装 [Claude Code](https://docs.anthropic.com/en/docs/claude-code)、Codex、[OpenClaw](https://github.com/nicekate/OpenClaw) 或 [WorkBuddy](https://workbuddy.app) 任意一个，并已安装 [Git](https://git-scm.com/downloads)。如果 GitHub 下载失败，请打开全局代理后重试。

**Mac / Linux**（打开终端，粘贴）：

```bash
curl -fsSL https://raw.githubusercontent.com/MarkQWu/drama-workshop-skills/main/install.sh | bash
```

**Windows**（按 `Win+X` → 选「终端」，粘贴）：

```powershell
irm https://raw.githubusercontent.com/MarkQWu/drama-workshop-skills/main/install.ps1 | iex
```

安装完成后**关闭当前会话，重新打开**，输入 `/开始` 看到引导就说明装好了。

安装脚本会自动让 Claude / Codex / OpenClaw / WorkBuddy 共用同一份本地 Skill，普通使用和 `/更新` 不需要处理目录路径。

安装脚本会自动把 `~/.workbuddy/skills/.trash`、`~/.openclaw/skills/.trash`、`~/.codex/skills/.trash`、`~/.claude/skills/.trash` 这类旧备份迁移到同级 `.skill-trash/`，避免 WorkBuddy 递归扫描旧版 `SKILL.md`。

> WorkBuddy 用户注意：同一个工作空间项目可能缓存旧 skill。重装后如果仍显示旧版本，请从工作空间移除/关闭当前项目，再重新打开该项目；这不会删除 `~/short-drama-projects/` 下的剧本项目。

> 不想跑脚本？见底部[手动安装](#手动安装)。

## 5 分钟上手

### 写出第一集

```
你：/开始
AI：问你想写什么题材（霸总？甜宠？逆袭？），有故事想法可以直接说

你：我想写一个霸总剧，女主是替嫁新娘
AI：确认题材、受众、集数等配置

你：/创作方案
AI：生成完整故事骨架——三幕结构、付费卡点、爽点分布

你：/角色开发
AI：生成角色档案——性格、语言风格、视觉描述、关系图

你：/目录
AI：全剧分集目录，标注 [关键] 集和 [付费] 卡点集

你：/分集 1
AI：写出第一集完整剧本 ↓
```

<details>
<summary>剧本长这样（点击展开）</summary>

```
## 场次一

**场景：** 内景 · 总裁办公室 · 夜

△ （全景）落地窗外城市灯火，办公桌上摊开的文件被风吹动

**陆砚辰**（头也不抬）："门没锁。"

△ （中景）女主推门进来，手里攥着一张化验单，指节发白

**苏晚宁**（声音发抖）："陆砚辰，你看看这个。"

[锚点] △ （特写）化验单上的名字不是苏晚宁的

> [钩子] 本集钩子：化验单上的名字是谁的？
```

</details>

```
你：/自检 1
AI：7 个维度打分，告诉你哪里写得好、哪里要改、怎么改
```

### 从剧本到视频

```
你：/角色卡
AI：为每个角色生成视觉描述，锁定角色形象一致性

你：/分镜 1
AI：把第一集拆成逐镜分镜表，每个镜头附带即梦 AI prompt ↓
```

<details>
<summary>分镜表 + prompt 长这样（点击展开）</summary>

| 镜号 | 景别 | 镜头运动 | 画面描述 | 台词/音效 | 时长 | 转场 |
|------|------|---------|---------|----------|------|------|
| 1 | 全景 | 缓推 | 雨夜高层办公室，落地窗外城市霓虹 | [音乐] 低沉钢琴 | 3s | 无 |
| 2 | 中景→近景 | 跟拍 | 女主推门而入，手攥化验单 | 苏晚宁：陆砚辰，你看看这个 | 4s | 硬切 |
| 3 | 特写 | 固定 | 化验单上的名字不是苏晚宁的 | （无） | 2s | 闪白 |

每个镜头自动生成即梦 AI「全能多参」prompt：

```
镜头 2：
  @图片1 作为角色参考。镜头从门口跟拍，年轻女性快步推门走入办公室，
  右手紧握白色纸张指节泛白，米色风衣下摆随动作摆动，走廊冷白灯光，
  电影质感，4K，同一角色，服装一致，发型不变
```

> 「全能多参」是即梦 Seedance 2.0 的视频生成模式，上传角色图 + 粘贴 prompt，一步出视频。

</details>

```
→ 打开即梦 AI → 选「全能参考」模式 → 上传角色图 + 粘贴 prompt → 生成视频
→ 用剪映按分镜表排列 → 加字幕配音 → 成片
```

### 常用技巧

- **批量写**：`/分集 5-8` 一次写 4 集
- **续写**：`/分集 next` 自动写下一集
- **自动修复**：`/自检 3 --fix` 检查完直接帮你改
- **只拆分镜**：`/分镜` 可独立使用，直接粘贴任意文本就能拆
- **海外项目**：海外 vertical drama（ReelShort / DramaBox / mafia romance / dark romance 等）由主 skill 内置支持，输入 `/出海` 命令切换为出海内容规则；默认中文呈现，角色名保留英文。需要英文投稿稿时用 `/出海 英文交付`

## 命令速查

### 剧本创作

| 命令 | 做什么 |
|------|--------|
| `/开始` | 选新建剧本或继续已有项目，然后选题材、定方向 |
| `/创作方案` | 三幕结构 + 爽点矩阵 + 付费卡点规划 |
| `/角色开发` | 角色档案 + 语言风格映射 + 视觉提示词 |
| `/目录` | 全剧分集目录 |
| `/分集 {N}` | 写第 N 集（批量：`/分集 5-8`，续写：`/分集 next`） |
| `/自检 {N}` | 7 维度质检 + AI Slop 检测（`--fix` 自动修复） |
| `/合规` | 国内发行合规审核 |
| `/导出` | 打包完整剧本（自检 <30 分会拦截） |
| `/出海` | 切换为出海内容规则（默认中文呈现 + 中文短剧格式，角色名保留英文） |
| `/出海 英文交付` | 切换为英文 + Hollywood 格式，用于海外平台投稿稿 |

### 拆解复刻

| 命令 | 做什么 |
|------|--------|
| `/仿写 <参考>` | 兼容入口：自动切换到新版 short-drama-remake 拆解复刻能力 |
| `/仿写 帮助` | 查看复刻流程、子命令和换新对话恢复方法 |
| `/仿写 状态 PROJECT_DIR` | 只读查看复刻项目进度、已生成文件和下一步 |
| `/仿写 继续 PROJECT_DIR` | 恢复复刻项目并推荐下一步，不自动写正文 |
| `/仿写 出海` | 为选定复刻方向生成海外目标市场迁移层，不直接写正文 |
| `/仿写 写集 N` | 写第 N 集，仍必须通过 remake preflight/postflight |
| `/仿写 方向会` / `/仿写 方案会` / `/仿写 诊断会 N` | 可选评审入口，不解锁 gate |
| `$short-drama-remake` | 显式调用参考剧本拆解复刻能力，适合长剧本 ingest、换皮方向、集纲和正式剧本 |

### 分镜 & 视频

| 命令 | 做什么 |
|------|--------|
| `/角色卡` | 生成或导入角色视觉描述 |
| `/分镜 {N}` | 剧本→分镜表 + [即梦 AI](https://jimeng.jianying.com) prompt（可独立使用） |
| `/工作流` | 打印完整创作→视频链路说明 |

### 圆桌诊断

| 命令 | 做什么 |
|------|--------|
| `/选题会` | 召集跨域专家对当前题材做结构性碰撞，产出创作处方 |
| `/圆桌诊断 {N}` | 对已自检集数做三视角质量诊断（需先跑 `/自检 N`） |
| `/查看碰撞` | 列出已保存的选题碰撞记录 |
| `/查看诊断 [N]` | 列出已保存的圆桌诊断记录（可按集数筛选） |

### 工具

| 命令 | 做什么 |
|------|--------|
| `/角色一致性` | 跨集扫描：年龄/发色/眼色/身高矛盾（脚本层）+ 性格/动机/弧线漂移（LLM 层）|
| `/更新` | 检查并安装 `drama-workshop-skills` 仓库最新版，同时更新 short-drama 和 short-drama-remake |
| `/帮助` | 显示所有命令和版本号 |

## 更新

**v1.5.0 起支持自动检测**：每次开新对话时自动检查新版本，有更新会让你选：

- **立即升级** — 自动下载安装，重启会话生效
- **开启自动更新** — 以后静默升级，不再询问
- **暂不** — 24h 后再提醒（连续选暂不会递增到 48h → 7 天）
- **永远不提醒** — 关闭检测，之后想更新随时输 `/更新`

> [提示] 老用户首次升级到 v1.5.0 需要手动跑一次安装命令（上面的安装步骤），之后就自动了。

`/更新` 现在是仓库级更新，会重新安装仓库里的全部 skills，包括 `short-drama` 和 `short-drama-remake`。如果自动检测不可用（网络问题等），也可以随时在终端重新跑安装命令来手动更新。

## 常见问题

**Q：安装/更新命令报错、下载失败**
A：先确认已安装 [Git](https://git-scm.com/downloads)。Windows 可让 AI agent 运行 `winget install --id Git.Git -e --source winget`。如果已经有 Git 但仍下载失败，请打开全局代理后重新运行安装命令。

**Q：`/仿写` 还提示旧流程、扫描旧项目，或没有新版能力**
A：新版 `/仿写` 会自动切换到同级 `short-drama-remake`。如果仍提示旧流程或扫描旧项目，说明当前会话或 WorkBuddy 工作空间还挂着旧 skill，或 `~/.workbuddy/skills/.trash` 里有旧版 `short-drama/SKILL.md` 被递归扫描。请重跑安装命令，安装器会把 `.trash` 移出 skills 扫描范围；然后从 WorkBuddy 工作空间移除/关闭当前项目，再重新打开。

**Q：新版拆解复刻项目会写进原创短剧项目目录吗？**
A：不会自动混写。原创主流程仍使用 `~/short-drama-projects/<项目>/.drama-state.json`、`episodes/`、`characters.md`、`creative-plan.md`；新版拆解复刻会生成独立的 `manifest.yaml`、`00_source/`、`01_skeleton/`、`02_concepts/`、`03_plan/`、`04_outlines/`、`05_scripts/`、`06_state/`。需要接到原创主流程时，人工复制或导入已确认的设定。换新对话后用 `/仿写 状态 PROJECT_DIR` 或 `/仿写 继续 PROJECT_DIR` 恢复，不用原创 `/开始`。

**Q：装完后输入 `/开始` 没反应**
A：关闭旧会话，重新打开新会话。WorkBuddy 如果仍不生效，需要从工作空间移除/关闭当前项目再重新打开。Skill 只在工作空间重新加载后生效。

**Q：怎么确认版本号？**
A：输入 `/帮助`，底部显示版本号。

**Q：每次开对话都提醒更新，太烦了**
A：选「暂不」会递增退避（24h→48h→7d），选「永远不提醒」彻底关闭。

## 附录

### 手动安装

**Claude Code 用户：**

```bash
if [ -d drama-workshop-skills/.git ]; then
  git -C drama-workshop-skills pull --ff-only
else
  git clone https://github.com/MarkQWu/drama-workshop-skills.git
fi
stamp=$(date +%Y%m%d-%H%M%S)
mkdir -p ~/.claude/skills ~/.claude/.skill-trash/manual-$stamp
[ -d ~/.claude/skills/short-drama ] && mv ~/.claude/skills/short-drama ~/.claude/.skill-trash/manual-$stamp/
[ -d ~/.claude/skills/short-drama-remake ] && mv ~/.claude/skills/short-drama-remake ~/.claude/.skill-trash/manual-$stamp/
ln -s "$(pwd)/drama-workshop-skills/short-drama" ~/.claude/skills/short-drama
ln -s "$(pwd)/drama-workshop-skills/short-drama-remake" ~/.claude/skills/short-drama-remake
```

**Codex / OpenClaw / WorkBuddy 用户：**

```bash
if [ -d drama-workshop-skills/.git ]; then
  git -C drama-workshop-skills pull --ff-only
else
  git clone https://github.com/MarkQWu/drama-workshop-skills.git
fi
stamp=$(date +%Y%m%d-%H%M%S)
mkdir -p ~/.codex/skills ~/.openclaw/skills ~/.workbuddy/skills ~/.codex/.skill-trash/manual-$stamp ~/.openclaw/.skill-trash/manual-$stamp ~/.workbuddy/.skill-trash/manual-$stamp
[ -d ~/.codex/skills/short-drama ] && mv ~/.codex/skills/short-drama ~/.codex/.skill-trash/manual-$stamp/
[ -d ~/.openclaw/skills/short-drama ] && mv ~/.openclaw/skills/short-drama ~/.openclaw/.skill-trash/manual-$stamp/
[ -d ~/.workbuddy/skills/short-drama ] && mv ~/.workbuddy/skills/short-drama ~/.workbuddy/.skill-trash/manual-$stamp/
[ -d ~/.codex/skills/short-drama-remake ] && mv ~/.codex/skills/short-drama-remake ~/.codex/.skill-trash/manual-$stamp/
[ -d ~/.openclaw/skills/short-drama-remake ] && mv ~/.openclaw/skills/short-drama-remake ~/.openclaw/.skill-trash/manual-$stamp/
[ -d ~/.workbuddy/skills/short-drama-remake ] && mv ~/.workbuddy/skills/short-drama-remake ~/.workbuddy/.skill-trash/manual-$stamp/
ln -s "$(pwd)/drama-workshop-skills/short-drama" ~/.codex/skills/short-drama    # Codex
ln -s "$(pwd)/drama-workshop-skills/short-drama" ~/.openclaw/skills/short-drama   # OpenClaw
ln -s "$(pwd)/drama-workshop-skills/short-drama" ~/.workbuddy/skills/short-drama  # WorkBuddy
ln -s "$(pwd)/drama-workshop-skills/short-drama-remake" ~/.codex/skills/short-drama-remake    # Codex
ln -s "$(pwd)/drama-workshop-skills/short-drama-remake" ~/.openclaw/skills/short-drama-remake   # OpenClaw
ln -s "$(pwd)/drama-workshop-skills/short-drama-remake" ~/.workbuddy/skills/short-drama-remake  # WorkBuddy
```

手动安装前，如果 `~/.workbuddy/skills/.trash`、`~/.openclaw/skills/.trash`、`~/.codex/skills/.trash` 或 `~/.claude/skills/.trash` 存在，请先把它们移动到同级 `.skill-trash/`，不要留在 `skills/` 目录内。

## License

- **Skill 骨架**（SKILL.md、scripts/、安装脚本）：基于 [0xsline/short-drama](https://github.com/0xsline/short-drama) 的 MIT License；`short-drama-remake/scripts/` 同样按 MIT License 分发
- **创作方法论**（各 skill 的 `references/` 目录下所有文件）：© 2026 gobuildit. All rights reserved. 未经许可不得再分发或商用

## 致谢

基于 [0xsline/short-drama](https://github.com/0xsline/short-drama)（MIT License）定制，由 [gobuildit](https://github.com/MarkQWu) 社区维护。
