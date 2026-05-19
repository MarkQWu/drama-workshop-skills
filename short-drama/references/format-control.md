---
layer: foundation
control: hard_gate
authority_id: short-drama.format-control
canonical_path: references/format-control.md
read_when: every command before output generation
---

# 格式控制（所有命令强制前置）

## 格式锚定步骤（每个命令执行前自动执行）

1. **读取状态**：读取 `.drama-state.json`，提取 `mode`（domestic/overseas）、`language`（zh-CN/en）和 `scriptFormat`（cn-shortdrama/hollywood）。
2. **确定内容规则**：`mode: "overseas"` 只决定故事内容、平台规则、文化/合规/题材适配；不自动决定输出语言或剧本格式。
3. **确定输出语言**：`language: "zh-CN"` 或未设置 → 中文呈现；`language: "en"` / `"en-US"` / `"en-GB"` → 英文呈现。
4. **确定剧本格式**：`scriptFormat: "cn-shortdrama"` 或未设置 → 中文短剧格式；`scriptFormat: "hollywood"` → Hollywood master-scene 格式。`mode=overseas` 默认仍是 `zh-CN + cn-shortdrama`，除非用户明确要求“英文交付 / 英文剧本格式 / Hollywood format / 投海外平台英文稿”。
5. **锚定声明**：重读本命令的输出模板区块（见 `references/output-templates.md`），严格按模板输出，不混用呈现版本。

## 格式封闭原则（强制扣分/阻断）

禁止添加模板外内容（如导演手记/创作心得/拍摄建议）、禁止格式漂移、禁止无规则中英混杂；中文呈现用中文术语（视觉锚点/中景/近景/特写/内景/外景），英文呈现用英文术语（VISUAL ANCHOR/CLOSE-UP/INT./EXT.）。出海中文呈现允许英文角色名、剧名、平台名、地名、组织名和必要类型词，其他说明、动作、对白默认中文。行业缩写（BGM/CTA）保留；所有标记用纯文字方括号（[关键]/[付费]/[锚点]），禁用 emoji。

**对白与破折号规则（按呈现格式分化，详见 `references/quality-rules.md#对白与叙事语言规则`）：** `scriptFormat=cn-shortdrama` 用 `**角色名**：台词` 格式，禁用双引号包裹对白内容；`scriptFormat=hollywood` 用 `**CHARACTER NAME** (tone direction): "dialogue"`。出海中文呈现时，角色名保留英文，但对白、动作、场景描述用中文。剧本正文禁止破折号：`——`、`—`、`--` 均不得出现。停顿、被打断、补充说明、心理独白引出，一律改用动作描写、换对话轮次、完整句、句号、逗号或中文省略号「…」。

## 新格式规范（生成时遵守；违反 → 自检以【建议】标签提示，不扣分）

**国内模式（mode=domestic）**：

1. **场景标题元素顺序**：`## 场号 · 内/外 · 地点 · 日/夜`（不得时间前置，工业主流顺序：内外→地点→时间）
2. **音乐/音效标注**：氛围铺底用 `（BGM：描述）`；点状音效用 `（音效：描述）`；**禁用** `[音乐] ...` 写法
3. **OS/VO 粗体只包裹角色名**：`**角色名**（OS）：台词` 和 `**角色名**（VO）：台词`（**不是** `**角色名（OS）**：` 形式——OS/VO 技术标记不加粗，便于扫读谁在说）
4. **本集考据引用作为附录**：位于剧本正文结束后的双分隔线 + `<!-- 剧本正文到此结束 -->` 边界标记之外；`/导出` 默认剥离，`/分镜` 不参与拆分

**出海英文交付（mode=overseas + scriptFormat=hollywood）**：

- OS/VO 粗体位置规则同第 3 条（好莱坞标准本来如此：`**JANE** (V.O.)` 而非 `**JANE (V.O.)**`）
- 音乐标注暂保持 `[音乐] Music cue:`（本版不改，后续评估）
- 场景头保持英文格式 `INT./EXT. LOCATION - DAY/NIGHT`

**出海中文呈现（mode=overseas + scriptFormat=cn-shortdrama，默认）**：

- 内容必须按海外资料层执行：target market、genre promise、relationship grammar、paid pressure、IP/文化/合规风险按 `references/overseas/` 判定。
- 呈现使用中文短剧格式：`## 场号 · 内/外 · 地点 · 日/夜`、`△` 场景描写、`**英文角色名**：中文台词`。
- 角色名保留英文，地点/组织/专有名词可保留英文；其余说明、对白、动作、OS/VO 默认中文。

**与上段「格式封闭原则」的区别**：本段是"新格式规范"，违反 → 自检以【建议】标签提示，不扣分、不阻断。上段的规则（对白引号、破折号禁用、emoji 禁用等）违反扣分或阻断 /导出。两段并列，不混用"强制"语义。
