# short-drama skill 评测断言（assertions）

> 用途：每次 minor/major release 前后跑一次，与 baseline 对比检查是否回归。
> 形式：11 条 assertion，机器（grep/正则）+ 半机器（grep 触发 + 人工裁定）。
> 跑法：见 `run.sh` 和 `README.md`。

---

## A1：anchor 字段触发（mech）

**断言**：当 `/策划` 选定的题材命中国内全 13 题材之一（都市情感 / 霸道总裁 / 甜宠 / 重生穿越 / 古装宫廷 / 励志逆袭 / 悬疑探案 / 战神归来 / 家庭伦理 / 萌宝 / 软科幻 / 末日重生 / 喜剧）时，`creative-plan.md` 输出**必须**包含 `anchor` 字段。

**检查命令**：
```bash
grep -E "^## anchor|^### anchor|^- anchor:" creative-plan.md
```

**通过标准**：exit 0（命中至少一条）
**不通过**：exit 1（缺 anchor 字段）→ 维度违反 `anchor-trigger.md` 强制规则

---

## A2：开场冲突字数位置（mech）

**断言**：`/分集 1` 输出剧本正文**前 1/3 字数**内必须出现至少 1 次冲突/爆点关键词。

**触发词清单**（任一即算命中）：
- 动作类：`打` `撞` `推` `摔` `抓` `逃` `追` `跪`
- 情绪类：`怒吼` `咆哮` `尖叫` `怒斥` `质问` `逼问`
- 关系类：`背叛` `撕破脸` `当众` `打脸` `揭穿`
- 场景类：`血` `刀` `枪` `救护` `急诊` `报警`

**检查命令**：
```bash
# 需先用 scripts/wc-cn.py 算出剧本正文字数（去除元信息）
TOTAL=$(python3 scripts/wc-cn.py episodes/ep001.md)
THIRD=$((TOTAL / 3))
HEAD_TEXT=$(python3 scripts/extract-head.py episodes/ep001.md $THIRD)
echo "$HEAD_TEXT" | grep -cE "打|撞|推|摔|抓|逃|追|跪|怒吼|咆哮|尖叫|背叛|撕破脸|血|刀"
```

**通过标准**：count ≥ 1
**不通过**：count = 0 → SKILL.md `quality-rules.md` "前 30s 钩子位置扫描" 维度违反

---

## A3：海外模式呈现格式 + 反中式弧（mech，仅 mode=overseas 跑）

**断言**：`mode=overseas` 时 `/分集 1` 输出**必须**：
- 默认中文呈现：包含中文短剧场景头 `## 1-1 · 内/外 · 地点 · 日/夜`，且包含 `视觉锚点` / `特写` / `近景` 任一
- 英文交付（`scriptFormat=hollywood`）：包含好莱坞场景头格式 `INT.` 或 `EXT.` 至少各一次，且包含 `VISUAL ANCHOR` / `CLOSE-UP` / `MEDIUM SHOT` 任一
- **不包含**中式 humiliation→power 弧关键词：`赘婿` / `逆袭` / `打脸` / `废柴` / `战神` / `神医归来`

**检查命令**：
```bash
# 正向（二选一，按 .drama-state.json#scriptFormat 执行）
# cn-shortdrama（默认中文呈现）
grep -cE "^## [0-9]+-[0-9]+ · (内|外)" episodes/ep001.md   # 默认中文呈现 ≥1
grep -cE "视觉锚点|特写|近景" episodes/ep001.md   # 默认中文呈现 ≥1

# hollywood（仅英文交付）
grep -cE "^INT\.|^EXT\." episodes/ep001.md   # 英文交付 ≥2
grep -cE "VISUAL ANCHOR|CLOSE-UP|MEDIUM SHOT" episodes/ep001.md   # 英文交付 ≥1

# 反向（必须 0 命中）
grep -cE "赘婿|逆袭|打脸|废柴|战神|神医归来|凤凰涅槃" episodes/ep001.md   # =0
```

**通过标准**：正向 ≥ 阈值 AND 反向 = 0
**不通过**：违反 `references/overseas/anti-patterns.md` 禁词表 / `hard-rules.md` Rule 4

---

## A4：自检 7 维度齐全（mech）

**断言**：`/自检 1` 输出**必须**包含全部 7 个维度（含考据维度时为 8）的评分行。

**检查命令**：
```bash
grep -cE "节奏|爽点|台词|格式与可拍性|主线与连贯性|反抽象|AI Slop" reviews/ep001-review.md
# ≥ 7
# 厚型/中型题材额外
grep -c "考据可追溯性" reviews/ep001-review.md   # ≥1
```

**通过标准**：所有维度名各 ≥ 1 次出现
**不通过**：缺维度 → 自检不完整，违反 `quality-rubric.md` 评分流程

---

## A5：dramatic-truth 4 症状触发记录（mixed，v1.19.0 新增）

**断言**：`/自检 1` 在扫角色长台词（≥10 词）时，**必须**输出 4 症状清单中至少 1 个症状名（无论命中或未命中——能扫到 0 命中也算执行了校验）。

**4 症状名**：
- `Trailer-Speak`（预告片体）
- `Metaphor Overdose`（比喻堆叠）
- `As-You-Know-Bob`（信息倾倒）
- `Urgency Mismatch`（紧迫感错位）

**检查命令**：
```bash
grep -cE "Trailer-Speak|Metaphor Overdose|As-You-Know-Bob|Urgency Mismatch" reviews/ep001-review.md
# ≥1
```

**通过标准**：count ≥ 1（说明 dramatic-truth 校验环节被触发）
**不通过**：count = 0 → SKILL.md `/自检` 加载参考行的 `dramatic-truth.md` 没被模型读 → 引用 silent-fail

**人工裁定**：触发后 grep 同时记录"哪条台词被标 X 症状"，人工评估命中是否合理（评分时间 ≤2 min）

---

## A6：海外模式中式表达扣分（mixed，仅 mode=overseas 跑）

**断言**：`mode=overseas` 时 `/自检 1` 在自检阶段**必须能识别中式直译表达**并标注扣分。

**触发词清单**（中式高语境表达，英文场景下应为雷区）：
- 比喻：`心如刀绞` / `双瞳如墨` / `星眸潋滟` / `面如冠玉` / `肤白胜雪`
- 心理：`一颗心提到嗓子眼` / `脑海中走马灯般闪过` / `胸口憋着一团火`
- 状态：`三魂七魄被勾走了` / `骨头都酥了` / `五脏六腑都翻江倒海`

**检查命令**：
```bash
# 自检报告中是否对这些词标记
grep -E "心如刀绞|双瞳如墨|星眸|面如冠玉|肤白胜雪|提到嗓子眼|走马灯般|胸口憋着|魂七魄|骨头都酥|五脏六腑" reviews/ep001-review.md | grep -E "扣分|建议|【严重】|【建议】|改写"
```

**通过标准**：如剧本中含中式表达，自检报告中**有标注**（无论扣分还是建议）
**不通过**：剧本含中式表达但自检 0 标注 → `references/overseas/anti-patterns.md` 禁词表机制失效

**人工裁定**：剧本本身**未含**中式表达时，本断言 N/A 跳过

---

## A7：CONTINUITY 块位置与字段（mech）

**断言**：`/分集 1` 输出必须包含正文结束边界，且 `CONTINUITY` 块位于边界之后；块内只出现 3 个字段：`角色状态变化` / `伏笔与回收` / `尾钩义务`。

**检查命令**：
```bash
grep -n "<!-- 剧本正文到此结束 -->" episodes/ep001.md
grep -n "<!-- CONTINUITY" episodes/ep001.md
grep -E "角色状态变化：|伏笔与回收：|尾钩义务：" episodes/ep001.md
grep -E "核心事件：|新增伏笔：|回收伏笔：|需要后续强化：" episodes/ep001.md && exit 1 || exit 0
```

**通过标准**：边界存在；`CONTINUITY` 行号大于边界行号；3 字段均存在；5 字段旧版本字段 0 命中。
**不通过**：诊断 `references/output-templates.md#分集`。

---

## A8：ledger 创建与分集索引（mech）

**断言**：`/分集 1` 后项目根必须存在 `continuity-ledger.md`，且含 3 个核心 section 与第 1 集索引记录。

**检查命令**：
```bash
test -f continuity-ledger.md
grep -E "^## 角色动态状态|^## 活跃主线伏笔|^## 分集索引" continuity-ledger.md
grep -E "^\| *1 *\||第1集|ep001" continuity-ledger.md
```

**通过标准**：文件存在，3 个 section 均命中，分集索引出现第 1 集记录。
**不通过**：诊断 `SKILL.md /分集` 与 `references/continuity-protocol.md`。

---

## A9：尾钩义务承接（mixed）

**断言**：fixture 中 ep001 的 `尾钩义务` 指定 ep002 前 3 单元必须出现“匿名短信：报告不是原件”；ep002 前 3 单元必须承接该事件，且 `/自检 2` 提到尾钩义务承接检查。

**检查命令**：
```bash
grep -E "匿名短信|报告不是原件" episodes/ep002.md
grep -E "尾钩义务|承接上一集|连续性" checks/ep002-check.md
```

**通过标准**：ep002 前 3 个动作/对白单元出现该事件；自检报告有连续性对账痕迹。
**不通过**：诊断 `SKILL.md /分集`、`SKILL.md /自检`。

**人工裁定**：grep 命中后人工确认是否在前 3 单元内。

---

## A10：交付路径剥离 CONTINUITY（mech）

**断言**：`/导出 1` 单集 docx 输入或生成内容不含 `CONTINUITY`；完整 `/导出` 的梗概输入和 docx 内容不含 `CONTINUITY`；`/分镜 1` 输出不含 `CONTINUITY` 或 3 个机器字段。

**检查命令**：
```bash
grep -R "CONTINUITY\\|角色状态变化：\\|伏笔与回收：\\|尾钩义务：" export/ storyboards/ && exit 1 || exit 0
```

**通过标准**：export 与 storyboards 交付物 0 命中。
**不通过**：诊断 `/导出`、`/分镜`、单集导出临时文件逻辑或 `output-templates.md`。

---

## A11：老项目 bootstrap（mixed）

**断言**：fixture 预置 `completedEpisodes=3`、存在 ep001-ep003、无 `continuity-ledger.md`；执行 `/分集 next` 前必须创建台账初版，`## 分集索引` 至少含第 1-3 集摘要或最近 3 集摘要，且 ep003 尾钩义务能被 ep004 承接。

**检查命令**：
```bash
test -f continuity-ledger.md
grep -E "^## 分集索引" continuity-ledger.md
grep -E "1|2|3|ep001|ep002|ep003|第1集|第2集|第3集" continuity-ledger.md
grep -E "尾钩|义务|下一集" continuity-ledger.md
```

**通过标准**：ledger 初版存在，分集索引覆盖最近 3 集或全部已完成集，上一集尾钩被记录并在下一集承接。
**不通过**：诊断 `references/continuity-protocol.md#老项目-bootstrap` 与 `SKILL.md /分集`。

---

## 跑法约定

- 每次 minor/major release（patch 不强制）后，按 `samples/domestic-test.md` + `samples/overseas-test.md` 跑一次 `/分集 1` + `/自检 1`
- 11 条 assertion 全过 = 通过；任一不过 = 调查 + 修正。A9/A11 需要连续性 fixture；没有 fixture 时标 N/A，不视为通过完整 release gate
- 第一次跑结果作为 baseline 存到 `baseline-vX.X.X.md`
- 后续 release 与 baseline 对比，看是否回归

## 已知限制

- 不覆盖：`/策划` 完整逻辑、`/分镜` 输出、`/角色开发` voice 准确性、跨集 used-lines 复用扫描——这些是后续 assertion 扩展点
- 当前仅 1 国内 + 1 海外 sample，不覆盖跨题材（古装/悬疑/重生）差异——MVP 验证流程后再扩
- 主观维度（voice 一致性 / 情感真实度）需人工评，eval 不替代
