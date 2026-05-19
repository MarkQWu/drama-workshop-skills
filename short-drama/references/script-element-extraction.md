# Script Element Extraction Methods — 剧本 5 类元素独立 Pipeline

> **用途**：Script agent 写 vertical drama EP1-3 时的硬约束。每类元素有独立提炼 pipeline，**不得一次性写完整集**
> **适用对象**：Bible / Characters / Script agent 写作时均需遵守，Audit 3 借鉴 vs 重组 balance 审查的执行依据
> **来源**：vertical drama demo 项目 2026-04-15 v2.6 补录。Dark Web of Desire / Fatal Attraction / Once Upon A Breakup / Mafia Bride Auction 四份 ReelShort/DramaBox 真实 transcript 反向提取
> **搭配读物**：本文件依赖 hard-rules.md（Rule 1-13 + P1-P3）+ anti-patterns.md（C-drama 红旗 + AP-V2~V6）+ dialogue-craft.md（L1/L2/L3 voice 分层）

---

## 核心原则

**vertical drama 剧本 ≠ 小说散文 ≠ prestige TV**。90 秒压缩对白 DNA 要求：
- 分层生成（不得一次写完）
- 先框架再填充（先定战略后 pull craft）
- 真实 transcript 做**骨架参照**，不做**内容源**

---

## ① 台词 (Dialogue) 5 步 Pipeline

**核心原则**：先写再对照，防污染。让 LLM 先凭 bible/characters 生成，真实样本**校准骨架**，不是**填充内容**。

```
Step 1: 按 bible + characters 先写一版草稿台词
        禁止动作：此刻打开 transcript
        目的：LLM 从剧情逻辑出发，不从"我见过的好台词"出发

Step 2: 按场景类型拉同类参照
        场景类型白名单：
          - threat (威胁)
          - possession (占有宣告)
          - confession (表白 / 关系推进)
          - revelation (身份揭露 / 真相)
          - cliff (EP 末悬崖)
          - refusal (拒绝)
          - bargain (交易 / 合约)
        从 4 份 transcript grep 关键词找 5-10 行参照

Step 3: 对照"句式骨架"（只看骨架不抄内容），问 3 问：
  Q1: 句长分布对齐吗？
      短句 <8 词应占 60%+
      允许 3-5 条"戏剧功能长句"（激动/威胁/揭露/表白/反派诗化独白）
      超过 5 条长句 = voice 漂移

  Q2: 用的动词是 ReelShort 高频词还是 AI slop？
      ✅ ReelShort 高频：want / mine / stay / protect / kill / break / owe / choose（罕用）
      ❌ AI slop：love (过度使用) / feel / understand / realize / emotion 系列抽象动词

  Q3: 去情境化反问——这行"去掉本剧情境"后还能用吗？
      能 → 太通用，没抓住 craft，重写
      不能 → 方向对，这行只在此剧可能出现

Step 4: 15 词自然性检查
        超 15 词必走判断：
          - 读出声自然 → 保留
          - 凑信息粘意思 → 拆或删
        自然优先，不为短而短

Step 5: 反抄袭 grep
        禁止出现 Dark Web / Mafia Bride / Fatal Attraction / Once Upon Breakup 原句
        命中 = 改写
```

---

## ② 场景 (Scene Descriptions) 3 问

**每个场景写前必问：**

```
Q1: 为什么是这个地点？
    场景地点必须服务 bible 世界观
    例：Wharton 图书馆（知识/古典权力）vs 家族 penthouse（财富/血缘权力）
       vs 地下俱乐部（犯罪/身体权力）vs 私人医务室（脆弱/秘密）
    不能"随便选个酒吧"

Q2: 为什么是这个时间？
    日 / 夜 / 晨对调性影响大
    - 夜 = 危险 / 诱惑 / 反派主场 / dark academia 本位
    - 日 = 公开身份 / 权力展示 / 校园场面
    - 晨 = 余波 / 关系状态变化 / reveal

Q3: 这个场景提供什么 TikTok 广告帧？
    每场景必须至少 1 个可截图当广告封面的瞬间
    找不到 → 场景可能多余，考虑删或合并
```

**写法模板（好莱坞行业标准 + AI 全链路 dub 适配）：**

```
INT./EXT. [LOCATION, SPECIFIC] - DAY/NIGHT
[VISUAL ANCHOR — 建立世界观元素：典故词/品牌/家族继承符号]
[MEDIUM SHOT — 人物动作]
[CLOSE-UP — 情绪爆点 / money shot]
```

---

## ③ 插入 (Money Shots) 4 类型 + 3 问验证

**每集至少 3-5 个 money shot**，按类型分布：

| 类型 | 用途 | Dark Web 对照（学形状，禁抄原帧）|
|---|---|---|
| **IDENTITY** | 身份建立 / 反差 | Chloe 黑衣擦血 vs 礼服 L16-22 |
| **POWER** | 权力展示 / 占有宣告 | Sean 第一次下令 L17 |
| **DESIRE** | 情欲 / 危险交汇 | 首次对视 / 触碰 |
| **CLIFF** | EP 末悬崖 / 付费卡点 | 协议签字瞬间 / reveal 帧 |

**3 问验证（三问全 YES 才标 money shot）：**

```
Q1: 这一帧截图发 TikTok，路人会停下吗？
    是 → 视觉冲击成立
    否 → 太平淡，不是 money shot

Q2: 能独立讲一个故事吗？（脱离上下文）
    能 → 广告帧可用
    否 → 只是剧情过场

Q3: 配 3 秒音乐能情绪锁定吗？
    能 → 情感能量足
    否 → 缺少戏剧张力
```

**标注格式：**
```
\*** [MONEY SHOT — IDENTITY] ***
*描述画面（谁在做什么，视觉元素，情绪）*
*适用广告素材：15s / 30s*
```

---

## ④ 景别 (Shot Types) 配比规则

**每场次景别多样性要求**：

| 景别 | 配比 | 用途 |
|---|---|---|
| **WIDE (全景)** | 1-2 次/场次 | 开场/结场 / 世界观建立 / 多人群像 |
| **MEDIUM (中景)** | 60-70% 主干 | 人物动作 / 对话对抗 |
| **CLOSE-UP (特写)** | 2-3 次/场次 | 情绪峰值 / 道具细节 / money shot |

**执行约定（2026-04-15 修订）**：

v2 剧本格式采用 **Final Draft master-scene 现代约定**——每场**显式**标
1 个 `WIDE ON:` / `CLOSE ON:` / `MEDIUM SHOT:` slug-line 作为导演主锚，
其余景别**隐式于 action prose**（"她跪下抹布按下"= 隐式 medium；
"钢梁高悬于她之上"= 隐式 wide）。导演在 prose 中读出景别，符合
Succession / Sex Education / Industry 现代剧本惯例。

**废止项（2026-04-15）**：旧规则"每场次显式 ≥3 种景别标签"作废。理由：
强制每场 3 个显式 slug-line 产生 stub shot block 膨胀，且破坏 vertical
drama 100 秒节奏；现代 master-scene 约定把景别判断交给导演是行业主流。

**保留硬规则**：
- 单场次**连续 3 帧同景别 = failure**（视觉节奏断裂，prose 层也适用）
- CLOSE-UP 必须服务情绪爆点，不能用来"补填"
- WIDE 如果没有 money shot 价值 → 降级为 MEDIUM
- 每场至少 1 个显式 slug-line（`WIDE ON:` / `CLOSE ON:` / `MEDIUM SHOT:`）
  作为导演主锚点

---

## ⑤ 人物指示 (Parenthetical) Dub 硬约束

**B-dub-4 规则**（AI 全链路制作约束——视频由另一拨人后期配音）：

parenthetical 必须精确到**单一情绪词 + 单一动作**，让配音演员不用猜。

### ✅ 好范例

```
CARL (softly, reaching for her hand): "Stay."
CHLOE (backing away, jaw tight): "No."
SEAN (cold, gun raised): "One more step."
VICTOR (laughing, leaning back): "You don't get it yet."
```

规则：
- 一个情绪副词（softly / cold / bitter / hollow）
- 一个精确动作（reaching / backing away / gun raised / leaning back）
- 配音演员能直接出声

### ❌ 坏范例

```
CARL (with a complex mix of longing and regret): ...   ← 配音猜不出
CHLOE (conflicted): ...                                  ← 太抽象
SEAN (feeling the weight of generations of family expectation): ... ← 小说叙述
VICTOR (both amused and threatening): ...                ← 复合情绪
```

问题：
- 复合情绪 / 抽象概念 / 内心叙述 → dub 无法产出
- 配音演员会 guess → 质量失控 → dub 团队打回重配 = 成本暴涨

### 检查问题

**每个 parenthetical 问**：
- 配音演员能**从文字直接产出语气**吗？不能 → 重写
- 是**一个情绪**还是**复合情绪**？复合 → 拆分到多个 parenthetical

---

## 整合使用流程（Script agent 写 EP1 时）

```
For each scene (3-5 scenes per episode):
  1. 应用【② 场景 3 问】确定 INT/EXT + 时间 + 地点
  2. 应用【④ 景别配比规则】设计 shot 序列
  3. 应用【③ money shot 4 类型】决定插入点
  4. 应用【① 台词 5 步 pipeline】生成每句对白
  5. 应用【⑤ parenthetical dub 硬约束】加语气指示
  6. 自检：读出声，有没有 slop 感 / 小说感 / prestige fragment 误用

Full episode self-check:
  - 全集短句 <8 词 占 60%+？
  - money shot 3-5 个覆盖 4 类型？
  - 每场次 ≥1 个显式景别 slug-line + prose 隐式覆盖剩余景别？
  - 每集前 7 秒 detonate 不 ease-in？
  - EP 末 cliff 是"不可撤回的协议/反转/揭露/威胁"四类之一？
  - 反抄袭 grep 全部零命中？
```

---

## 与其他 references 的关系

- **hard-rules.md**：规则约束层（什么必须做、什么绝对禁止）。本文件是**方法论**（怎么做）
- **anti-patterns.md**：反模式清单（什么不要做）。本文件是**正面 pipeline**
- **dialogue-craft.md**：voice 分层理论（L1/L2/L3 prestige vs platform 对照）。本文件是**操作执行**
- **platform-knowledge.md**：平台约定（VO / paywall / CC formula）。本文件是**具体生成步骤**

4 份 references 各司其职，互为冗余但不矛盾。Script agent 必须全部加载。

---

## 变更记录

- 2026-04-15 v1 初稿。vertical drama demo 项目 2026-04-15 写作时催生，基于 Dark Web of Desire 等 4 份真实 transcript 反向提取
