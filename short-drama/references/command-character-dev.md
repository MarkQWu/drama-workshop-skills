# /角色开发执行协议

> 本文件由 `/角色开发` 读取，承接分批写入状态机、恢复检查、finalize 合并和结束提示。
> SKILL.md 只保留功能入口、加载参考和不可变硬约束。

---

## 入口行为

### `/角色开发`

1. `status=not_started` 或无 state 且无 `characters.md`：
   - 读取 `creative-plan.md` 和当前 state。
   - 冻结 `rolePlan`：按 `core | long_arc | functional` 分层，并按每批 2-3 个角色分配 `batchId`（第一批必须覆盖主角、核心关系对象、主反派/核心压迫者）。
   - 写 `characters.parts/{runId}/00-role-plan.md`（人类可读）和 `00-role-plan.json`（供 validator 使用）。
   - 写入 `characterDevStatus`：`status=in_progress`、`runId`、`rolePlan`、`batches`、`currentBatchId`。
   - 只生成第一批分片，保存到 `characters.parts/{runId}/{batchId}.md`。
   - 执行分片验收；通过则标 batch=`validated`，失败则 batch=`failed` 且 `status=failed`。
2. `status=in_progress | rerun_in_progress | failed`：
   - 等价执行 `/角色开发 继续`，不重建 `rolePlan`。
3. `status=ready_to_finalize`：
   - 提示所有角色分片已完成，唯一下一步是 `/角色开发 finalize`。
4. `status=finalized`：
   - 提示已有 `characters.md`。若用户明确要求重跑，创建新 `runId`，状态置 `rerun_in_progress`；旧 `characters.md` 保留到新 runId finalize 通过后才覆盖。

### `/角色开发 继续`

1. 读取 `characterDevStatus`，只处理当前 `runId`。
2. 执行恢复检查：
   - `pending/written` 且分片存在并通过验收 → 修复为 `validated`。
   - `validated` 但分片不存在 → 标 `failed`，提示重新生成该 batch。
   - `failed` → 重新生成该 batch。
   - `status=finalized` 但 `characters.md` 不存在 → 降级 `ready_to_finalize`。
3. 找第一个 `pending/failed` batch，生成该分片并保存。
4. 执行分片验收命令：
   ```bash
   python3 {skill目录}/scripts/character_dev_validate.py batch \
     --file "{项目目录}/characters.parts/{runId}/{batchId}.md" \
     --roles "角色A,角色B"
   ```
5. 读取 validator JSON：`errors` 非空按失败处理；`warnings` 非空时仍可通过结构验收，但必须先尝试修正当前分片 voice 一次并复验。复验后若仍有 warnings，写入 `characters.parts/{runId}/validation-report.md`，并在对话框展示 `[声纹质量提醒]` 摘要，不得只报“完成”。
6. 验收通过：batch=`validated`，更新 `completedRoles/pendingRoles/currentBatchId/updatedAt`。
7. 所有 batch 均 `validated`：置 `status=ready_to_finalize`，输出唯一下一步 `/角色开发 finalize`。

### `/角色开发 finalize`

0. 即使当前 `status=finalized`，用户显式输入 `/角色开发 finalize` 时也必须重新执行 finalize 验收；若现有 `characters.md` 不通过，先把 `status` 降级为 `ready_to_finalize`，不得沿用旧 finalized。
1. 确认所有 batch 均为 `validated`；否则阻断并提示 `/角色开发 继续`。
2. 读取当前 `runId` 下所有分片。
3. 生成 `90-finalize.md`，只包含全局 section；禁止跳过本步直接拼接分片：
   - `## 角色-语言风格映射表`（短版声音差异索引，每角色一行）
   - `## 称呼关系表`（核心互动称呼表 + 非互动默认规则）
   - `## 角色关系图`（默认核心关系摘要；Mermaid 可选，不在最小版强制）
   - `## 三角张力动态`
   - `## 角色弧线`
   - `## 感情线弧线`
   - `## 关键互动场景预设`
   - `## 反派体系`
4. 合并生成最终 `characters.md`：`# 剧名：角色档案` + `## 主要角色` + 全部分片角色档案 + `90-finalize.md`。最终文件必须至少包含这些一级二级标题：`## 主要角色`、`## 角色-语言风格映射表`、`## 称呼关系表`、`## 角色关系图`、`## 三角张力动态`、`## 角色弧线`、`## 关键互动场景预设`；若有强反派/对手/压迫者，则必须包含 `## 反派体系`。
5. 执行 finalize 验收；只有脚本 exit code = 0 才能写 finalized：
   ```bash
   python3 {skill目录}/scripts/character_dev_validate.py final \
     --file "{项目目录}/characters.md" \
     --role-plan "{项目目录}/characters.parts/{runId}/00-role-plan.json" \
     --project-dir "{项目目录}" \
     --run-consistency \
     --run-viz
   ```
6. 读取 validator JSON：`errors` 非空按失败处理；`warnings` 非空时不阻断 finalized，但必须写入 `characters.parts/{runId}/validation-report.md` 并在对话框展示 `[声纹质量提醒]` 摘要，说明 voice 结构可用但口吻质量需人工或后续修正。
7. 验收通过后写 `status=finalized`、`finalize.status=validated`、`finalCharactersPath=characters.md`。
8. 验收失败：不得写 `status=finalized`；若此前误写为 finalized，必须回滚为 `ready_to_finalize`；错误写入 `characters.parts/{runId}/validation-report.md`；输出唯一下一步 `/角色开发 finalize`。

## 角色分片生成内容

每个计划内角色必须包含完整角色块：姓名、年龄、外貌、性格、公开/真实身份、核心动机、欲望-恐惧对位、动机形成契机、盲点/弱点、冲突点、爽点功能、表面/真实功能、声音指纹 + voice 样本集（句长倾向 / 说话路径 / 躲闪方式 / 情绪失控语言 / ≥5 条示例台词 + ≥3 条禁用模式）、应激模式、视觉提示词。

`functional` 角色也要有可被下游解析的最小完整字段，不降级成名单。voice 样本必须是带对象、压力和真实意图的短场景对白，不写作者旁白、漂亮比喻、完整前史自白或主题宣言；情绪失控语言只写语言如何变形，不写摘眼镜、手在抖、整理卷宗、茶杯等动作/物件锚。

## 输出与结束提示

输出格式见 `references/output-templates-core.md#角色开发`。

分片保存到 `characters.parts/{runId}/`；`/角色开发 finalize` 验收通过后保存最终 `characters.md`。

根据题材考据强度（见 `genre-guide.md#考据强度判定`）输出结束提示：

- 分片未完成：`[进度] 已完成 {已完成角色数}/{总角色数} 个角色 → {分片路径}。继续输入 /角色开发 继续`
- `ready_to_finalize`：`[进度] 所有角色分片已通过验收。输入 /角色开发 finalize 生成 characters.md`
- `finalized` 厚型/中型：`[完成] 角色档案已保存！输入 /考据 auto 建立世界观/专业知识底座（厚型必做）`
- `finalized` 轻型：`[完成] 角色档案已保存！输入 /分集目录 规划全剧分集`
