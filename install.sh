#!/usr/bin/env bash
# gobuildit 社区 Skills 一键安装
set -euo pipefail

REPO_GITHUB="https://github.com/MarkQWu/drama-workshop-skills.git"
REPO_MIRROR="https://ghfast.top/https://github.com/MarkQWu/drama-workshop-skills.git"
CACHE="$HOME/.gobuildit/skill-repos/drama-workshop-skills"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && { pwd -P || pwd; })"

# 解析参数
MCP_ONLY=0
for arg in "$@"; do
  [[ "$arg" == "--mcp-only" ]] && MCP_ONLY=1
done

echo "=== gobuildit Skills 安装器 ==="
echo ""

timestamp() {
  date +"%Y%m%d-%H%M%S"
}

# 输出辅助函数
say()  { printf '\033[32m[OK]\033[0m    %s\n' "$*"; }
warn() { printf '\033[33m[注意]\033[0m  %s\n' "$*"; }
err()  { printf '\033[31m[错误]\033[0m  %s\n' "$*" >&2; }
hint() { printf '         → %s\n' "$*"; }

# 读已有 key（先查 Claude Code，再查 WorkBuddy）
_read_existing_key() {
  local key=""
  if [[ -f "$HOME/.claude/settings.json" ]]; then
    key=$(node -e "try{const c=require('$HOME/.claude/settings.json');
      console.log(c.mcpServers?.['wangwen-bigdata']?.headers?.['X-MCP-API-Key']||'')}catch(e){}" 2>/dev/null || true)
  fi
  if [[ -z "$key" || "$key" == "YOUR_KEY_HERE" ]] && [[ -f "$HOME/.workbuddy/mcp.json" ]]; then
    key=$(node -e "try{const c=require('$HOME/.workbuddy/mcp.json');
      console.log(c.mcpServers?.['wangwen-bigdata']?.headers?.['X-MCP-API-Key']||'')}catch(e){}" 2>/dev/null || true)
  fi
  echo "$key"
}

# terminal 内 prompt 收 key，返回 1 表示用户跳过
_prompt_key() {
  local existing
  existing=$(_read_existing_key)

  if [[ -n "$existing" && "$existing" != "YOUR_KEY_HERE" ]]; then
    echo ""
    echo "  检测到已有 Key：${existing:0:8}***"
    echo "  [1] 保留现有 Key（直接回车）"
    echo "  [2] 换新 Key"
    local choice
    read -r -p "  请选择 [1/2，默认 1]：" choice </dev/tty 2>/dev/null || { warn "无交互终端，跳过 MCP 配置"; return 1; }
    if [[ "$choice" == "2" ]]; then
      read -r -p "  请粘贴新 Key（wwmcp_ 开头）：" WANGWEN_KEY </dev/tty 2>/dev/null || return 1
      # 剥 Win 终端粘贴尾部 \r（Git Bash 在 Windows 上常见）
      WANGWEN_KEY="${WANGWEN_KEY%$'\r'}"
    else
      WANGWEN_KEY="$existing"
      say "保留现有 Key"
    fi
  else
    echo ""
    echo "  还没有 Key？免费注册获取（首次 1000 Credits，约够查 200 次榜单）："
    echo "  https://wangwendashuju.com/mcp  →  注册后在「个人中心 → API Key」页面复制"
    echo ""
    local key_input
    read -r -p "  请粘贴你的 Key（wwmcp_ 开头，没有可直接回车跳过）：" key_input </dev/tty 2>/dev/null || { warn "无交互终端，跳过 MCP 配置"; return 1; }
    # 剥 Win 终端粘贴尾部 \r
    key_input="${key_input%$'\r'}"
    WANGWEN_KEY="$key_input"
  fi

  # Key 格式简单校验（Trim 后再检查）：警告不强阻塞，允许特殊场景
  if [[ -n "$WANGWEN_KEY" && "$WANGWEN_KEY" != "$existing" && "$WANGWEN_KEY" != wwmcp_* ]]; then
    warn "Key 不是 wwmcp_ 开头，请确认粘贴是否正确（继续写入）"
  fi

  if [[ -z "$WANGWEN_KEY" ]]; then
    warn "未填入 Key，跳过 MCP 配置"
    hint "稍后可单独配置：bash install.sh --mcp-only"
    return 1
  fi
  export WANGWEN_KEY
}

# 写入 JSON（jq → node → python3 降级链，写前备份，原子替换）
_write_mcp_config() {
  local config="$1" type="$2" key="$3"
  local backup
  backup="${config}.bak.$(timestamp)"
  local tmp="${config}.tmp.$$"

  [[ -f "$config" ]] && cp "$config" "$backup"

  if command -v jq >/dev/null 2>&1; then
    jq --arg k "$key" --arg t "$type" --arg u "https://wwdsj-mcp.lingjingai.cn/mcp" \
      '.mcpServers["wangwen-bigdata"] = {"type":$t,"url":$u,"headers":{"X-MCP-API-Key":$k}}' \
      "${config:-/dev/null}" 2>/dev/null > "$tmp" || true
  elif command -v node >/dev/null 2>&1; then
    # key 通过环境变量传入，避免特殊字符注入
    WANGWEN_KEY_SAFE="$key" node -e "
const fs=require('fs'), p=process.argv[1];
const k=process.env.WANGWEN_KEY_SAFE;
const t='$type', u='https://wwdsj-mcp.lingjingai.cn/mcp';
const tmp='$tmp';
const c=fs.existsSync(p)?JSON.parse(fs.readFileSync(p,'utf8')):{};
(c.mcpServers=c.mcpServers||{})['wangwen-bigdata']={type:t,url:u,headers:{'X-MCP-API-Key':k}};
fs.writeFileSync(tmp,JSON.stringify(c,null,2));" "$config" 2>/dev/null || true
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c "
import json,os,sys
p,t=sys.argv[1],'$type'
k=os.environ['WANGWEN_KEY_SAFE']
c=json.load(open(p)) if os.path.exists(p) else {}
c.setdefault('mcpServers',{})['wangwen-bigdata']={'type':t,'url':'https://wwdsj-mcp.lingjingai.cn/mcp','headers':{'X-MCP-API-Key':k}}
json.dump(c,open('$tmp','w'),indent=2,ensure_ascii=False)" "$config" 2>/dev/null || true
  else
    err "未找到 jq / node / python3，无法自动写入"
    hint "请手动在 $config 的 mcpServers 段填入 Key"
    [[ -f "$backup" ]] && rm -f "$backup"
    return 1
  fi

  # 校验 JSON 合法
  local valid=0
  if command -v jq >/dev/null 2>&1 && jq empty "$tmp" >/dev/null 2>&1; then
    valid=1
  elif command -v node >/dev/null 2>&1 && node -e "JSON.parse(require('fs').readFileSync('$tmp','utf8'))" >/dev/null 2>&1; then
    valid=1
  fi

  if [[ $valid -eq 0 ]]; then
    err "生成的 JSON 不合法，原文件未动"
    hint "备份：$backup"
    rm -f "$tmp"
    return 1
  fi

  mv "$tmp" "$config"
}

# MCP 配置主流程（subshell 隔离，失败不影响 skill 主体安装）
_setup_mcp() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "【推荐】接入网文大数据 MCP"
  echo "提供番茄/红果/抖音漫剧实时榜单"
  echo "让 /选题 /市场 /创作方案 调用真实数据替代主观经验"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  local setup_mcp
  read -r -p "是否现在配置？(Y/n，默认 Y)：" setup_mcp </dev/tty 2>/dev/null || { warn "无交互终端，跳过 MCP 配置"; return 0; }
  setup_mcp="${setup_mcp:-Y}"

  if [[ ! "$setup_mcp" =~ ^[Yy]$ ]]; then
    warn "已跳过 MCP 配置"
    hint "稍后可单独配置：bash install.sh --mcp-only"
    return 0
  fi

  (
    _prompt_key || exit 0

    local configured=0
    local claude_settings="$HOME/.claude/settings.json"
    local wb_config="$HOME/.workbuddy/mcp.json"

    if [[ -d "$HOME/.claude" ]]; then
      # 确保文件存在（至少是空 JSON 对象）
      [[ -f "$claude_settings" ]] || echo '{}' > "$claude_settings"
      if WANGWEN_KEY_SAFE="$WANGWEN_KEY" _write_mcp_config "$claude_settings" "http" "$WANGWEN_KEY"; then
        say "Claude Code MCP 配置完成"
        hint "写入文件: $claude_settings"
        hint "MCP endpoint: https://wwdsj-mcp.lingjingai.cn/mcp"
        configured=1
      fi
    fi

    if [[ -d "$HOME/.workbuddy" ]]; then
      [[ -f "$wb_config" ]] || echo '{}' > "$wb_config"
      if WANGWEN_KEY_SAFE="$WANGWEN_KEY" _write_mcp_config "$wb_config" "streamableHttp" "$WANGWEN_KEY"; then
        say "WorkBuddy MCP 配置完成"
        hint "写入文件: $wb_config"
        hint "MCP endpoint: https://wwdsj-mcp.lingjingai.cn/mcp"
        configured=1
      fi
    fi

    if [[ $configured -eq 0 ]]; then
      warn "未检测到 Claude Code 或 WorkBuddy"
      hint "手动配置：https://wangwendashuju.com/mcp"
    else
      echo ""
      say "配置完成！重启 Claude Code / WorkBuddy 后即可使用"
      hint "试试输入：用网文数据帮我查一下近期红果最热门的题材"
    fi
  ) || warn "MCP 配置跳过，skill 主体安装不受影响"
}

migrate_embedded_trash() {
  local skills_dir="$1"
  local trash_dir="$skills_dir/.trash"

  if [ ! -d "$trash_dir" ]; then
    return 0
  fi

  # WorkBuddy may recursively scan every SKILL.md under skills/. Keep backups
  # outside the scanned skills tree so old skills cannot shadow current ones.
  local owner_dir
  owner_dir="$(dirname "$skills_dir")"
  local safe_root="$owner_dir/.skill-trash"
  local dest
  dest="$safe_root/from-skills-trash-$(timestamp)"

  mkdir -p "$safe_root"
  if [ -e "$dest" ]; then
    dest="$dest-$$"
  fi

  if mv "$trash_dir" "$dest" 2>/dev/null; then
    echo "  已迁移旧备份: $trash_dir → $dest"
  else
    echo "  警告：无法迁移 $trash_dir，请手动移出 skills 目录，避免旧 skill 被扫描。" >&2
  fi
}

# --mcp-only 模式：跳过 skill 安装，直接配置 MCP
if [[ $MCP_ONLY -eq 1 ]]; then
  _setup_mcp
  exit 0
fi

if ! command -v git >/dev/null 2>&1; then
  echo "错误：未找到 git。请先安装 Git 后重新运行本安装命令。" >&2
  echo "" >&2
  echo "Mac 可运行：xcode-select --install" >&2
  echo "或安装 Homebrew 后运行：brew install git" >&2
  echo "Windows 可让 AI agent 运行：winget install --id Git.Git -e --source winget" >&2
  exit 1
fi

# 尝试 clone，GitHub 失败则自动切镜像
try_clone() {
  local dest="$1"
  echo "正在下载..."
  if git clone "$REPO_GITHUB" "$dest" 2>/dev/null; then
    return 0
  fi
  echo "GitHub 连接失败，切换镜像源..."
  if git clone "$REPO_MIRROR" "$dest" 2>/dev/null; then
    # 把 remote 改回 GitHub（镜像只用于首次下载）
    git -C "$dest" remote set-url origin "$REPO_GITHUB"
    return 0
  fi
  echo ""
  echo "错误：GitHub 下载失败。请打开全局代理后重新运行安装命令。" >&2
  return 1
}

# 尝试 pull，GitHub 失败则通过镜像 fetch
try_pull() {
  local dir="$1"
  echo "检测到已安装，正在更新..."
  if git -C "$dir" pull --ff-only 2>/dev/null; then
    return 0
  fi
  # pull 失败：可能是网络问题或本地有改动
  # 先试镜像
  echo "GitHub 连接失败，切换镜像源..."
  git -C "$dir" remote set-url origin "$REPO_MIRROR"
  if git -C "$dir" pull --ff-only 2>/dev/null; then
    git -C "$dir" remote set-url origin "$REPO_GITHUB"
    return 0
  fi
  git -C "$dir" remote set-url origin "$REPO_GITHUB"
  # 镜像也失败，重新 clone
  echo "更新失败，正在重新安装..."
  mv "$dir" "$dir.backup-$(timestamp)" 2>/dev/null || return 1
  try_clone "$dir"
}

# Clone 或更新仓库到唯一 canonical 目录。
# 本地从完整 repo 运行时直接引用当前 checkout；curl | bash 时使用 ~/.gobuildit/skill-repos 下的唯一缓存 repo。
if [ -f "$SCRIPT_DIR/short-drama/SKILL.md" ] && [ -d "$SCRIPT_DIR/.git" ]; then
  CACHE="$SCRIPT_DIR"
  echo "使用本地仓库安装。"
else
  mkdir -p "$(dirname "$CACHE")"
  if [ -d "$CACHE/.git" ]; then
    try_pull "$CACHE"
  else
    if [ -d "$CACHE" ]; then mv "$CACHE" "$CACHE.backup-$(timestamp)" 2>/dev/null || true; fi
    try_clone "$CACHE"
  fi
fi

if [ ! -d "$CACHE" ]; then
  echo ""
  echo "错误：下载失败。请确认已安装 Git，并打开全局代理后重新运行安装命令。" >&2
  exit 1
fi

# 检测平台并安装到对应目录
installed=0
targets=()

# Claude Code
if [ -d "$HOME/.claude" ]; then
  mkdir -p "$CLAUDE_SKILLS_DIR"
  targets+=("$CLAUDE_SKILLS_DIR")
fi

# Codex / OpenClaw / WorkBuddy
for ocdir in "$HOME/.codex" "$HOME/.openclaw" "$HOME/.workbuddy"; do
  if [ -d "$ocdir" ]; then
    oc_skills="$ocdir/skills"
    mkdir -p "$oc_skills"
    targets+=("$oc_skills")
  fi
done

# 都没检测到，默认装 Claude Code 目录
if [ ${#targets[@]} -eq 0 ]; then
  mkdir -p "$CLAUDE_SKILLS_DIR"
  targets+=("$CLAUDE_SKILLS_DIR")
fi

# skills/<name> 只保留 symlink，内容只存在于 $CACHE。
for skills_dir in "${targets[@]}"; do
  migrate_embedded_trash "$skills_dir"
  for d in "$CACHE"/*/; do
    if [ -f "$d/SKILL.md" ]; then
      skill_name="$(basename "$d")"
      target="$skills_dir/$skill_name"
      if [ -L "$target" ] && [ "$(readlink "$target")" = "${d%/}" ]; then
        installed=$((installed + 1))
        continue
      fi
      if [ -e "$target" ] || [ -L "$target" ]; then
        safe_root="$(dirname "$skills_dir")/.skill-trash"
        mkdir -p "$safe_root"
        mv "$target" "$safe_root/reinstall-$skill_name-$(timestamp)" 2>/dev/null || {
          echo "  警告：无法备份旧目录 $target，请关闭占用它的程序后重试。" >&2
          continue
        }
      fi
      ln -s "${d%/}" "$target"
      installed=$((installed + 1))
    fi
  done
done

# 设置可执行权限（canonical repo 的 bin/ 目录）
for d in "$CACHE"/*/; do
  if [ -d "$d/bin" ]; then
    chmod +x "$d/bin/"* 2>/dev/null || true
  fi
done

check_duplicate_real_dirs() {
  for skills_dir in "${targets[@]}"; do
    for source_dir in "$CACHE"/*/; do
      if [ -f "$source_dir/SKILL.md" ]; then
        skill_name="$(basename "$source_dir")"
        target="$skills_dir/$skill_name"
        if [ -f "$target/SKILL.md" ] && [ ! -L "$target" ]; then
          echo "  警告：发现实体 skill 目录仍存在：$target。请移到同级 .skill-trash，避免多版本并存。" >&2
        fi
      fi
    done
  done
}
check_duplicate_real_dirs

# 读取版本号（来自仓库 VERSION 文件，由发版流程维护）
version=""
if [ -f "$CACHE/short-drama/VERSION" ]; then
  version="$(head -1 "$CACHE/short-drama/VERSION" 2>/dev/null)"
else
  for d in "$CACHE"/*/; do
    if [ -f "$d/VERSION" ]; then
      version="$(head -1 "$d/VERSION" 2>/dev/null)"
      break
    fi
  done
fi
if [ -z "$version" ] && command -v git >/dev/null 2>&1; then
  version=$(git -C "$CACHE" log -1 --format="%h" 2>/dev/null || echo "unknown")
fi
[ -z "$version" ] && version="unknown"

echo ""
if [ "$installed" -gt 0 ]; then
  echo "安装成功！"
  echo ""
  echo "版本：$version"
  echo ""
  echo "关闭当前 Claude Code / Codex / OpenClaw 会话，重新打开后输入 /开始 即可使用。"
  echo "WorkBuddy 用户：需要从工作空间移除/关闭当前项目再重新打开，单独新建对话可能仍沿用旧 skill 缓存。"
  echo "这不会删除 ~/short-drama-projects/ 下的剧本项目。"
else
  echo "警告：未找到任何 Skill，请检查仓库内容。"
fi

# MCP 配置（skill 安装成功后推荐接入）
_setup_mcp
