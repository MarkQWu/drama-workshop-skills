---
layer: foundation
control: hard_gate
authority_id: short-drama.update-mechanism
canonical_path: references/update-mechanism.md
read_when: every skill activation update check and explicit /更新 command
---

# 版本更新机制（Update Mechanism）

> **重要：** `/更新` 是仓库级更新。它必须从 `drama-workshop-skills` 仓库拉取最新版，并重新安装仓库内全部 sibling skills（当前至少包含 `short-drama` 与 `short-drama-remake`）。不得再只覆盖 `short-drama/` 单目录。

> **用户心智约束：** 本仓库面向非技术用户。用户只需要输入 `/更新` 或在自动提示中选择更新；对话里不得解释底层安装实现细节。除非更新失败且需要排障，否则只输出“正在检查 / 正在更新 / 更新完成 / 更新失败请重试或打开代理”这类用户可理解话术。

## 精确路由优先级

用户最新消息去除首尾空白后，若精确等于 `/更新`，或以 `/更新 ` 开头，必须直接执行本文件的 `/更新 命令详细流程`。

不得把 `/更新` 当成：

- `/项目状态` 的“更新当前项目 README”
- 恢复上次剧本进度
- 生成项目状态表
- 推进当前剧本下一步

`/更新` 不读取当前活跃剧本项目，不扫描 `~/short-drama-projects/`，不输出项目阶段表。

## 版本更新检测（每次激活自动执行）

**本 skill 被激活时（用户输入任何命令前），必须先执行以下检测：**

Mac/Linux：
```bash
bash "$(dirname "$(find ~/.claude/skills ~/.codex/skills ~/.openclaw/skills ~/.workbuddy/skills -name update-check -path "*/short-drama/*" 2>/dev/null | head -1)")/update-check" 2>/dev/null || true
```

Windows（PowerShell）：
```powershell
$roots = @("$HOME\.claude\skills","$HOME\.codex\skills","$HOME\.openclaw\skills","$HOME\.workbuddy\skills"); $base = "https://raw.githubusercontent.com/MarkQWu/drama-workshop-skills/main"; $skills = @("short-drama","short-drama-remake"); $local = @(); $remote = @(); foreach ($name in $skills) { $v = Get-ChildItem $roots -ErrorAction SilentlyContinue -Filter VERSION -Recurse | Where-Object { $_.FullName -match "\\$name\\VERSION$" } | Select-Object -First 1; $local += "$name=" + ($(if ($v) { (Get-Content $v.FullName -TotalCount 1).Trim() -replace '^v','' } else { "missing" })); try { $rv = ((Invoke-WebRequest -Uri "$base/$name/VERSION" -TimeoutSec 5 -ErrorAction Stop).Content -split "`n")[0].Trim() -replace '^v',''; $remote += "$name=$rv" } catch {} }; if ($remote.Count -eq $skills.Count -and (($local -join ';') -ne ($remote -join ';'))) { "UPGRADE_AVAILABLE " + ($local -join ';') + " " + ($remote -join ';') }
```

### 输出处理

根据输出决定行为：

- **无输出** → 已是最新，正常进入创作流程
- **`UPGRADE_AVAILABLE <旧版本> <新版本>`** → 用 `AskUserQuestion` 让用户选择（不要先回答用户命令再问，直接先问）：

  问题：「[锚点] 新版本可用（当前 {旧版本}，远端 {新版本}），是否更新？」

  选项：
  1. **立即更新** → 执行下方升级流程
  2. **开启自动更新** → 写入配置 `auto_upgrade: true`（以后静默升级），然后执行升级
  3. **暂不** → 写入递增退避 snooze（24h→48h→7d），继续响应用户原始命令
  4. **永远不提醒** → 写入 `update_check: false`，继续响应用户原始命令

- **`AUTO_UPGRADE <旧版本> <新版本>`** → 用户已开启自动更新，不询问，直接执行升级流程，完成后显示：
  > [完成] 已自动升级到 {新版本}（从 {旧版本}）。下次对话生效。

  然后继续响应用户原始命令。

- **`JUST_UPGRADED <旧版本> <新版本>`** → 显示升级成功信息并展示更新内容：
  > [完成] 已从 {旧版本} 升级到 {新版本}！
  
  然后读取仓库内各 skill 的 `WHATSNEW.md`，逐行原文输出匹配当前版本的内容（保留换行与分段，不合并，不精简）。若某个 `WHATSNEW.md` 缺失或首个版本号与当前版本不一致，只提示该 skill “无匹配更新说明”：

  **本次更新内容：**

  {`short-drama/WHATSNEW.md` 与 `short-drama-remake/WHATSNEW.md` 中与当前 VERSION 匹配的内容。若某个文件缺失或首个版本号与 VERSION 不一致，输出该 skill 名称和“无匹配更新说明”。}

- **`CHECK_FAILED 7d`** → 网络连续 7 天无法检查更新，显示淡提示：
  > [提示] 已超过 7 天未能检查更新（网络问题）。可手动运行 `/更新` 检查，或确认网络连通后自动恢复。

**重要**：版本检测只在每次对话的**首次命令**时执行一次，后续命令不再检测。网络失败时静默跳过，不影响正常使用。

---

## /更新 命令详细流程

**功能：** 检查最新版本并升级。

**边界：** 本命令必须更新整个 `drama-workshop-skills` 仓库并重新安装所有 sibling skills。当前不得只更新 `short-drama`，否则会漏掉 `short-drama-remake` 的 schema、checker、fixtures 或版本说明。

### 步骤 1：强制检查版本

```bash
SKILL_DIR="$(find ~/.claude/skills ~/.codex/skills ~/.openclaw/skills ~/.workbuddy/skills -name update-check -path "*/short-drama/*" 2>/dev/null | head -1 | xargs dirname | xargs dirname)"
bash "$SKILL_DIR/bin/update-check" --force 2>/dev/null || true
```

### 步骤 2：根据输出决定行为

**无输出（已是最新）：**
> [完成] 当前已是最新版本：{版本号}，无需更新。

**`UPGRADE_AVAILABLE <旧版本> <新版本>`：**

询问用户选择：
- **立即更新** → 执行步骤 3
- **开启自动更新**（以后不再问）→ 写入配置后执行步骤 3
- **暂不更新** → 写入暂缓文件（递增退避：24h → 48h → 7d）
- **永远不提醒** → 禁用更新检测

### 步骤 3：执行升级

执行前先对用户输出：
> 正在更新短剧 Skill，请稍等。更新完成后，重新打开会话即可使用新版。

Mac / Linux：

```bash
STATE_DIR="$HOME/.openclaw"
mkdir -p "$STATE_DIR"

collect_versions() {
  for root in "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.openclaw/skills" "$HOME/.workbuddy/skills"; do
    [ -d "$root" ] || continue
    if [ -d "$root/short-drama" ] || [ -L "$root/short-drama" ]; then
      SKILLS_ROOT="$root"
      break
    fi
  done
  for name in short-drama short-drama-remake; do
    vf="$SKILLS_ROOT/$name/VERSION"
    if [ -f "$vf" ]; then
      printf "%s=%s;" "$name" "$(head -1 "$vf" | sed 's/^v//' | awk '{print $1}')"
    else
      printf "%s=missing;" "$name"
    fi
  done | sed 's/;$//'
}
OLD_VER="$(collect_versions)"
echo "$OLD_VER" > "$STATE_DIR/just-upgraded-from"

curl -fsSL https://raw.githubusercontent.com/MarkQWu/drama-workshop-skills/main/install.sh | bash

rm -f "$STATE_DIR/last-update-check"
rm -f "$STATE_DIR/update-snoozed"

NEW_VER="$(collect_versions)"
echo "升级完成：$OLD_VER → $NEW_VER"
```

Windows（PowerShell）：

```powershell
$stateDir = Join-Path $HOME ".openclaw"
New-Item -ItemType Directory -Path $stateDir -Force | Out-Null

function Collect-Versions {
  $roots = @("$HOME\.claude\skills","$HOME\.codex\skills","$HOME\.openclaw\skills","$HOME\.workbuddy\skills")
  $skillsRoot = $roots | Where-Object { Test-Path (Join-Path $_ "short-drama") } | Select-Object -First 1
  $parts = @()
  foreach ($name in @("short-drama","short-drama-remake")) {
    $vf = if ($skillsRoot) { Join-Path $skillsRoot "$name\VERSION" } else { "" }
    if ($vf -and (Test-Path $vf)) {
      $parts += "$name=$((Get-Content $vf -TotalCount 1).Trim() -replace '^v','')"
    } else {
      $parts += "$name=missing"
    }
  }
  return ($parts -join ';')
}

$oldVer = Collect-Versions
Set-Content -Path (Join-Path $stateDir "just-upgraded-from") -Value $oldVer -Encoding UTF8

irm https://raw.githubusercontent.com/MarkQWu/drama-workshop-skills/main/install.ps1 | iex

Remove-Item -Path (Join-Path $stateDir "last-update-check") -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $stateDir "update-snoozed") -Force -ErrorAction SilentlyContinue

$newVer = Collect-Versions
"升级完成：$oldVer → $newVer"
```

4. 读取仓库内各 skill 的 `WHATSNEW.md`，逐行原文输出匹配当前版本的内容（保留换行与分段，不合并，不精简）。若某个 `WHATSNEW.md` 缺失或首个版本号与当前版本不一致，只提示该 skill “无匹配更新说明”：

   **本次更新内容：**

   {逐个读取 `short-drama/WHATSNEW.md` 与 `short-drama-remake/WHATSNEW.md`，匹配各自 VERSION 后原文输出；不再输出旧迁移提示。}

5. 提示用户：
> [完成] 升级完成！新版本在**下次对话**中生效（当前对话仍使用旧版 SKILL.md）。

若升级命令失败，只输出：
> [失败] 更新没有完成。请确认网络可访问 GitHub；如果在国内网络环境，请打开全局代理后再次输入 `/更新`。

不得把内部路径、底层安装实现或错误堆栈直接贴给普通用户；需要排障时先给一句简短原因，再让用户重试 `/更新`。

---

## 辅助脚本

### 暂缓写入（用户选「暂不更新」时）

```bash
STATE_DIR="$HOME/.openclaw"
SNOOZE_FILE="$STATE_DIR/update-snoozed"
SKILL_DIR="$(find ~/.claude/skills ~/.openclaw/skills ~/.workbuddy/skills -name VERSION -path "*/short-drama/*" 2>/dev/null | head -1 | xargs dirname)"
mkdir -p "$STATE_DIR"

# 从缓存读取远程版本号
REMOTE_VER="$(awk '/^UPGRADE_AVAILABLE/{print $3}' "$STATE_DIR/last-update-check" 2>/dev/null)"

# 读取当前 snooze level，递增
CURRENT_LEVEL=0
if [ -f "$SNOOZE_FILE" ]; then
  CURRENT_LEVEL="$(awk '{print $2}' "$SNOOZE_FILE" 2>/dev/null || echo 0)"
fi
NEW_LEVEL=$((CURRENT_LEVEL + 1))

echo "$REMOTE_VER $NEW_LEVEL $(date +%s)" > "$SNOOZE_FILE"
```

### 自动更新配置写入

```bash
STATE_DIR="$HOME/.openclaw"; mkdir -p "$STATE_DIR"
echo "auto_upgrade: true" >> "$STATE_DIR/config.yaml"
```

### 禁用更新检测

```bash
STATE_DIR="$HOME/.openclaw"; mkdir -p "$STATE_DIR"
echo "update_check: false" > "$STATE_DIR/config.yaml"
```
