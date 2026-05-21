# gobuildit 社区 Skills 一键安装 (Windows)
param(
    [switch]$McpOnly
)
$ErrorActionPreference = "Stop"

$repoGitHub = "https://github.com/MarkQWu/drama-workshop-skills.git"
$repoMirror = "https://ghfast.top/https://github.com/MarkQWu/drama-workshop-skills.git"
$cache = Join-Path $env:USERPROFILE ".gobuildit\skill-repos\drama-workshop-skills"
$scriptDir = if ($PSCommandPath) { Split-Path -Parent $PSCommandPath } else { "" }

Write-Host "=== gobuildit Skills 安装器 ===" -ForegroundColor Cyan
Write-Host ""

# ── MCP 配置辅助函数 ─────────────────────────────────────────────────────────

function Get-WangwenKey {
    $claudeConfig = Join-Path $env:USERPROFILE ".claude\settings.json"
    $wbConfig     = Join-Path $env:USERPROFILE ".workbuddy\mcp.json"

    # 读已有 key（先查 Claude Code，再查 WorkBuddy）
    # 兼容 PS5.1 老版本写入的 UTF-8 BOM 文件：剥 BOM 后再 ConvertFrom-Json
    $existingKey = ""
    foreach ($f in @($claudeConfig, $wbConfig)) {
        if (Test-Path $f) {
            try {
                $raw = (Get-Content $f -Raw -Encoding UTF8).TrimStart([char]0xFEFF)
                $c = $raw | ConvertFrom-Json
                $k = $c.mcpServers.'wangwen-bigdata'.headers.'X-MCP-API-Key'
                if ($k -and $k -ne "YOUR_KEY_HERE") { $existingKey = $k; break }
            } catch {}
        }
    }

    if ($existingKey) {
        Write-Host ""
        Write-Host "  检测到已有 Key：$($existingKey.Substring(0,[Math]::Min(8,$existingKey.Length)))***"
        Write-Host "  [1] 保留现有 Key（直接回车）"
        Write-Host "  [2] 换新 Key"
        $choice = Read-Host "  请选择 [1/2，默认 1]"
        if ($choice -eq "2") {
            $newKey = (Read-Host "  请粘贴新 Key（wwmcp_ 开头）").Trim()
            if ($newKey -and $newKey -notmatch '^wwmcp_') {
                Write-Host "  [警告] Key 不是 wwmcp_ 开头，请确认粘贴是否正确" -ForegroundColor Yellow
            }
            return $newKey
        }
        return $existingKey
    }

    Write-Host ""
    Write-Host "  还没有 Key？免费注册（首次 1000 Credits，约够查 200 次榜单）："
    Write-Host "  https://wangwendashuju.com/mcp  →  注册后在「个人中心 → API Key」页面复制"
    Write-Host ""
    $newKey = (Read-Host "  请粘贴你的 Key（wwmcp_ 开头，没有可直接回车跳过）").Trim()
    if ($newKey -and $newKey -notmatch '^wwmcp_') {
        Write-Host "  [警告] Key 不是 wwmcp_ 开头，请确认粘贴是否正确" -ForegroundColor Yellow
    }
    return $newKey
}

function Write-McpConfig($configPath, $type, $key) {
    $backup = "$configPath.bak.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    if (Test-Path $configPath) { Copy-Item $configPath $backup }

    # 检测文件是否带 UTF-8 BOM（老版本 install.ps1 用 Set-Content -Encoding UTF8 写入的遗留）
    # → BOM 存在时即使 key 相同也必须强制重写一次（剥 BOM），否则老用户重跑安装永远修不好
    $hasBom = $false
    if (Test-Path $configPath) {
        try {
            $firstBytes = [System.IO.File]::ReadAllBytes($configPath)
            if ($firstBytes.Length -ge 3 -and $firstBytes[0] -eq 0xEF -and $firstBytes[1] -eq 0xBB -and $firstBytes[2] -eq 0xBF) {
                $hasBom = $true
            }
        } catch {}
    }

    $c = if (Test-Path $configPath) {
        try {
            # 兼容 PS5.1 老版本写入的 UTF-8 BOM 文件
            $raw = (Get-Content $configPath -Raw -Encoding UTF8).TrimStart([char]0xFEFF)
            $raw | ConvertFrom-Json
        } catch { [PSCustomObject]@{} }
    } else { [PSCustomObject]@{} }

    if (-not $c.PSObject.Properties['mcpServers']) {
        $c | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([PSCustomObject]@{})
    }

    # idempotent：已有完全相同的 key 且文件无 BOM 才跳过；文件带 BOM 必须强制重写剥 BOM
    $existingEntry = $c.mcpServers.PSObject.Properties['wangwen-bigdata']
    $existingEntryKey = if ($existingEntry) { $existingEntry.Value.headers.'X-MCP-API-Key' } else { $null }
    if (-not $hasBom -and $existingEntryKey -and $existingEntryKey -ne "YOUR_KEY_HERE" -and $existingEntryKey -eq $key) {
        return
    }
    if ($hasBom) {
        Write-Host "  [修复] 检测到旧 BOM 编码，自动剥离重写（v1.38.7 hotfix）" -ForegroundColor DarkGray
    }

    $c.mcpServers | Add-Member -NotePropertyName 'wangwen-bigdata' -NotePropertyValue ([PSCustomObject]@{
        type    = $type
        url     = "https://wwdsj-mcp.lingjingai.cn/mcp"
        headers = [PSCustomObject]@{ 'X-MCP-API-Key' = $key }
    }) -Force

    $tmp = "$configPath.tmp"
    # 必须用 .NET API 无 BOM 写入：PS5.1 的 `-Encoding UTF8` 会写带 BOM 的 UTF-8（EF BB BF），
    # WorkBuddy / Claude Code 的 Node.js JSON.parse 不接受 BOM，会抛 SyntaxError 导致整个
    # MCP connector 加载失败，用户实际体感是「网址错了 / 连不上 / 405 nginx」。
    # PS7+ 的 `-Encoding UTF8NoBOM` 也可，但 Windows 10 默认 PS5.1 不支持，统一用 .NET API 兜底。
    $json = $c | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($tmp, $json, (New-Object System.Text.UTF8Encoding $false))
    Move-Item $tmp $configPath -Force
}

function Invoke-McpSetup {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host "【推荐】接入网文大数据 MCP"
    Write-Host "提供番茄/红果/抖音漫剧实时榜单"
    Write-Host "让 /选题 /市场 /创作方案 调用真实数据"
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host ""

    $setup = Read-Host "是否现在配置？(Y/n，默认 Y)"
    if (-not $setup) { $setup = "Y" }

    if ($setup -notmatch "^[Yy]$") {
        Write-Host "[注意]  已跳过，稍后可单独配置：.\install.ps1 -McpOnly" -ForegroundColor Yellow
        return
    }

    $key = Get-WangwenKey
    if (-not $key) {
        Write-Host "[注意]  未填入 Key，跳过 MCP 配置" -ForegroundColor Yellow
        Write-Host "         → 稍后可单独配置：.\install.ps1 -McpOnly"
        return
    }

    $claudeConfig = Join-Path $env:USERPROFILE ".claude\settings.json"
    $wbConfig     = Join-Path $env:USERPROFILE ".workbuddy\mcp.json"
    $configured   = $false

    # 初始化空 JSON 文件时也必须无 BOM（理由同 Write-McpConfig 内的注释）
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false

    if (Test-Path (Join-Path $env:USERPROFILE ".claude")) {
        if (-not (Test-Path $claudeConfig)) { [System.IO.File]::WriteAllText($claudeConfig, '{}', $utf8NoBom) }
        try {
            Write-McpConfig $claudeConfig "http" $key
            Write-Host "[OK]    Claude Code MCP 配置完成" -ForegroundColor Green
            Write-Host "         → 写入文件: $claudeConfig" -ForegroundColor DarkGray
            Write-Host "         → MCP endpoint: https://wwdsj-mcp.lingjingai.cn/mcp" -ForegroundColor DarkGray
            $configured = $true
        } catch { Write-Host "[错误]  Claude Code 配置失败：$_" -ForegroundColor Red }
    }

    if (Test-Path (Join-Path $env:USERPROFILE ".workbuddy")) {
        if (-not (Test-Path $wbConfig)) { [System.IO.File]::WriteAllText($wbConfig, '{}', $utf8NoBom) }
        try {
            Write-McpConfig $wbConfig "streamableHttp" $key
            Write-Host "[OK]    WorkBuddy MCP 配置完成" -ForegroundColor Green
            Write-Host "         → 写入文件: $wbConfig" -ForegroundColor DarkGray
            Write-Host "         → MCP endpoint: https://wwdsj-mcp.lingjingai.cn/mcp" -ForegroundColor DarkGray
            $configured = $true
        } catch { Write-Host "[错误]  WorkBuddy 配置失败：$_" -ForegroundColor Red }
    }

    if (-not $configured) {
        Write-Host "[注意]  未检测到 Claude Code 或 WorkBuddy" -ForegroundColor Yellow
        Write-Host "         → 手动配置：https://wangwendashuju.com/mcp"
    } else {
        Write-Host ""
        Write-Host "[OK]    配置完成！重启 Claude Code / WorkBuddy 后即可使用" -ForegroundColor Green
        Write-Host "         → 试试输入：用网文数据帮我查一下近期红果最热门的题材"
    }
}

# ── McpOnly 模式 ──────────────────────────────────────────────────────────────
if ($McpOnly) {
    Invoke-McpSetup
    exit 0
}

function Get-Timestamp {
    return (Get-Date -Format "yyyyMMdd-HHmmss")
}

function Move-EmbeddedTrash($skillsDir) {
    $trashDir = Join-Path $skillsDir ".trash"
    if (-not (Test-Path $trashDir)) { return }

    # WorkBuddy may recursively scan every SKILL.md under skills\. Keep backups
    # outside the scanned skills tree so old skills cannot shadow current ones.
    $ownerDir = Split-Path $skillsDir -Parent
    $safeRoot = Join-Path $ownerDir ".skill-trash"
    if (-not (Test-Path $safeRoot)) { New-Item -ItemType Directory -Path $safeRoot -Force | Out-Null }

    $dest = Join-Path $safeRoot ("from-skills-trash-" + (Get-Timestamp))
    if (Test-Path $dest) {
        $dest = "$dest-$PID"
    }

    try {
        Move-Item -Path $trashDir -Destination $dest -Force
        Write-Host "  已迁移旧备份: $trashDir → $dest" -ForegroundColor Yellow
    } catch {
        Write-Host "  警告：无法迁移 $trashDir，请手动移出 skills 目录，避免旧 skill 被扫描。" -ForegroundColor Yellow
    }
}

function Get-LinkTarget($path) {
    $item = Get-Item $path -Force -ErrorAction SilentlyContinue
    if (-not $item -or -not $item.LinkType) { return "" }
    if ($item.Target -is [array]) { return ($item.Target | Select-Object -First 1) }
    return [string]$item.Target
}

function New-SkillLink($target, $source) {
    try {
        New-Item -ItemType Junction -Path $target -Target $source -ErrorAction Stop | Out-Null
        return
    } catch {
        try {
            New-Item -ItemType SymbolicLink -Path $target -Target $source -ErrorAction Stop | Out-Null
            return
        } catch {
            throw "无法完成安装。请以管理员身份运行终端，或开启 Windows 开发者模式后重试。"
        }
    }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "错误：未找到 git。请先安装 Git 后重新运行本安装命令。" -ForegroundColor Red
    Write-Host ""
    Write-Host "Windows 可让 AI agent 运行：" -ForegroundColor Yellow
    Write-Host "  winget install --id Git.Git -e --source winget" -ForegroundColor Yellow
    Write-Host "安装完成后重新打开终端，再运行安装命令。" -ForegroundColor Yellow
    throw "git not found"
}

# 尝试 clone，GitHub 失败则自动切镜像
function Try-Clone($dest) {
    Write-Host "正在下载..."
    & git clone $repoGitHub $dest 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { return $true }

    Write-Host "GitHub 连接失败，切换镜像源..." -ForegroundColor Yellow
    & git clone $repoMirror $dest 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        # 把 remote 改回 GitHub（镜像只用于首次下载）
        & git -C "$dest" remote set-url origin $repoGitHub
        return $true
    }

    Write-Host ""
    Write-Host "错误：GitHub 下载失败。请打开全局代理后重新运行安装命令。" -ForegroundColor Red
    return $false
}

# 尝试 pull，GitHub 失败则通过镜像 fetch
function Try-Pull($dir) {
    Write-Host "检测到已安装，正在更新..."
    & git -C "$dir" pull --ff-only 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { return $true }

    Write-Host "GitHub 连接失败，切换镜像源..." -ForegroundColor Yellow
    & git -C "$dir" remote set-url origin $repoMirror
    & git -C "$dir" pull --ff-only 2>&1 | Out-Null
    $pullOk = $LASTEXITCODE -eq 0
    & git -C "$dir" remote set-url origin $repoGitHub
    if ($pullOk) { return $true }

    Write-Host "更新失败，正在重新安装..." -ForegroundColor Yellow
    Move-Item -Path $dir -Destination "$dir.backup-$(Get-Timestamp)" -Force -ErrorAction SilentlyContinue
    if (Test-Path $dir) { return $false }
    return (Try-Clone $dir)
}

# Clone 或更新仓库到唯一 canonical 目录。
# 本地从完整 repo 运行时直接引用当前 checkout；irm | iex 时使用 ~/.gobuildit/skill-repos 下的唯一缓存 repo。
if ($scriptDir -and (Test-Path (Join-Path $scriptDir "short-drama\SKILL.md")) -and (Test-Path (Join-Path $scriptDir ".git"))) {
    $cache = $scriptDir
    Write-Host "使用本地仓库安装。" -ForegroundColor Gray
} else {
    $cacheParent = Split-Path $cache -Parent
    if (-not (Test-Path $cacheParent)) { New-Item -ItemType Directory -Path $cacheParent -Force | Out-Null }

    if (Test-Path (Join-Path $cache ".git")) {
        $ok = Try-Pull $cache
    } else {
        if (Test-Path $cache) {
            Move-Item -Path $cache -Destination "$cache.backup-$(Get-Timestamp)" -Force -ErrorAction SilentlyContinue
            if (Test-Path $cache) { throw "无法准备安装目录，请关闭正在占用它的程序后重试。" }
        }
        $ok = Try-Clone $cache
    }
    if (-not $ok) {
        Write-Host ""
        Write-Host "错误：下载失败。请确认已安装 Git，并打开全局代理后重新运行安装命令。" -ForegroundColor Red
        throw "安装失败"
    }
}

# 检测平台并收集目标目录
$targets = @()

# Claude Code
$claudeDir = Join-Path $env:USERPROFILE ".claude"
if (Test-Path $claudeDir) {
    $targets += Join-Path $claudeDir "skills"
}

# Codex / OpenClaw / WorkBuddy
foreach ($name in @(".codex", ".openclaw", ".workbuddy")) {
    $dir = Join-Path $env:USERPROFILE $name
    if (Test-Path $dir) {
        $targets += Join-Path $dir "skills"
    }
}

# 都没检测到，默认装 Claude Code 目录
if ($targets.Count -eq 0) {
    $targets += Join-Path $env:USERPROFILE ".claude\skills"
}

# 安装 skill 到所有检测到的平台：skills\<name> 只保留 junction，内容只存在于 $cache。
$installed = 0
foreach ($skillsDir in $targets) {
    if (-not (Test-Path $skillsDir)) { New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null }
    Move-EmbeddedTrash $skillsDir
    Get-ChildItem "$cache" -Directory | Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } | ForEach-Object {
        $target = Join-Path $skillsDir $_.Name
        $existingTarget = Get-LinkTarget $target
        if ($existingTarget -and ((Resolve-Path $existingTarget -ErrorAction SilentlyContinue).Path -eq $_.FullName)) {
            $installed++
            return
        }
        if ($existingTarget -and -not (Test-Path $existingTarget)) {
            $safeRoot = Join-Path (Split-Path $skillsDir -Parent) ".skill-trash"
            if (-not (Test-Path $safeRoot)) { New-Item -ItemType Directory -Path $safeRoot -Force | Out-Null }
            $backup = Join-Path $safeRoot ("broken-link-" + $_.Name + "-" + (Get-Timestamp))
            Move-Item -Path $target -Destination $backup -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path $target) {
            $safeRoot = Join-Path (Split-Path $skillsDir -Parent) ".skill-trash"
            if (-not (Test-Path $safeRoot)) { New-Item -ItemType Directory -Path $safeRoot -Force | Out-Null }
            $backup = Join-Path $safeRoot ("reinstall-" + $_.Name + "-" + (Get-Timestamp))
            Move-Item -Path $target -Destination $backup -Force -ErrorAction SilentlyContinue
            if (Test-Path $target) {
                Write-Host "  警告：无法备份旧目录 $target，请关闭占用它的程序后重试。" -ForegroundColor Yellow
                return
            }
        }
        New-SkillLink $target $_.FullName
        Write-Host "  已安装: $($_.Name)"
        $installed++
    }
}

foreach ($packageDir in Get-ChildItem "$cache" -Directory -ErrorAction SilentlyContinue) {
    $binDir = Join-Path $packageDir.FullName "bin"
    if (Test-Path $binDir) {
        Get-ChildItem $binDir -File -ErrorAction SilentlyContinue | ForEach-Object {
            $_.Attributes = $_.Attributes -band (-bnot [System.IO.FileAttributes]::ReadOnly)
        }
    }
}

# 读取版本号（来自仓库 VERSION 文件，由发版流程维护）
$version = ""
$mainVersion = Join-Path $cache "short-drama\VERSION"
if (Test-Path $mainVersion) {
    $version = (Get-Content $mainVersion -TotalCount 1 -ErrorAction SilentlyContinue)
} else {
    Get-ChildItem "$cache" -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $_.FullName "VERSION") } | Select-Object -First 1 | ForEach-Object {
        $version = (Get-Content (Join-Path $_.FullName "VERSION") -TotalCount 1 -ErrorAction SilentlyContinue)
    }
}
if ((-not $version) -and (Get-Command git -ErrorAction SilentlyContinue)) { $version = (& git -C "$cache" log -1 --format="%h" 2>$null) }
if (-not $version) { $version = "unknown" }

Write-Host ""
if ($installed -gt 0) {
    Write-Host "安装成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "版本：$version" -ForegroundColor Gray
    Write-Host ""
    Write-Host "关闭当前 Claude Code / Codex / OpenClaw 会话，重新打开后输入 /开始 即可使用。"
    Write-Host "WorkBuddy 用户：需要从工作空间移除/关闭当前项目再重新打开，单独新建对话可能仍沿用旧 skill 缓存。"
    Write-Host "这不会删除 ~/short-drama-projects/ 下的剧本项目。"
} else {
    Write-Host "警告：未找到任何 Skill，请检查仓库内容。" -ForegroundColor Yellow
}

# MCP 配置（skill 安装成功后推荐接入）
Invoke-McpSetup
