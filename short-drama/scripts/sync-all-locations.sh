#!/usr/bin/env bash
# 将 master short-drama/ 同步到 5 个已知副本位置（含 master 自己，等效无操作）
#
# 使用场景：每次 release（git push + tag + GitHub Release）后运行一次，
# 消除 5 副本不同步问题（详见 memory/feedback_openclaw-sync-all-locations.md）
#
# 5 副本清单（所有均指 short-drama/ 子目录）：
#   1. ~/.claude/skills/                    （权威版本，主开发位置）
#   2. ~/.claude/.skill-repos/drama-workshop-skills/  （git 仓库，push origin）
#   3. ~/.workbuddy/skills/                 （WorkBuddy 运行时）
#   4. ~/.openclaw/skills/                  （OpenClaw 运行时）
#   5. ~/碳基生命数据库/.tools/drama-workshop-skills/  （vault 内独立 git 仓库，rsync 等效 git pull）
#
# 用法：
#   bash scripts/sync-all-locations.sh          # 实际同步
#   bash scripts/sync-all-locations.sh --dry    # 预览将要做什么
#
# Maintainer-only 文件物理隔离（2026-04-26 v1.20.0 OPTIMIZATION_PLAN.md 泄漏复盘新增）：
#   master 下任何放在 `.maintainer/` 子目录里的文件**不会被 sync 到 5 副本**——
#   即不会进 drama-workshop-skills 公开仓。用法：
#     - 升级动议草稿、设计 journal、内部分析文档 → 放 `.maintainer/`
#     - 用户文档、SKILL.md、references/ 等照常放 master 顶层（会被 sync）
#   起源：`feedback_meta-rule-application-failure.md` 复发案例 2026-04-26（公开仓准入规则未主动唤起）。
#   设计原则：物理隔离 > 协议约束（reference_ai-agent-engineering-principles.md）。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MASTER_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ ! -f "$MASTER_DIR/SKILL.md" ]]; then
  echo "❌ 未在 master short-drama 目录下：$MASTER_DIR" >&2
  exit 1
fi

DRY_RUN=""
if [[ "${1:-}" == "--dry" ]]; then
  DRY_RUN="--dry-run"
  echo "[DRY RUN] 不实际同步，仅展示将要做的操作"
fi

DESTINATIONS=(
  "$HOME/.claude/.skill-repos/drama-workshop-skills/short-drama"
  "$HOME/.claude/skills/short-drama"
  "$HOME/.workbuddy/skills/short-drama"
  "$HOME/.openclaw/skills/short-drama"
  "$HOME/碳基生命数据库/.tools/drama-workshop-skills/short-drama"
)

MASTER_VERSION=$(cat "$MASTER_DIR/VERSION" 2>/dev/null || echo "unknown")
echo "Master 版本: $MASTER_VERSION"
echo "Master 路径: $MASTER_DIR"
echo ""

SYNCED=0
SKIPPED=0
for DEST in "${DESTINATIONS[@]}"; do
  PARENT_DIR="$(dirname "$DEST")"

  if [[ ! -d "$PARENT_DIR" ]]; then
    echo "⚠ 跳过（父目录不存在）: $PARENT_DIR"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  if [[ -n "$DRY_RUN" ]]; then
    echo "[预览] rsync → $DEST"
    rsync -a --delete $DRY_RUN \
      --exclude='.git/' \
      --exclude='__pycache__/' \
      --exclude='*.pyc' \
      --exclude='.maintainer/' \
      --exclude='.last-version-shown' \
      --exclude='.mcp.json' \
      "$MASTER_DIR/" "$DEST/" | head -5
    continue
  fi

  mkdir -p "$DEST"
  rsync -a --delete \
    --exclude='.git/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.maintainer/' \
    --exclude='.last-version-shown' \
    --exclude='.mcp.json' \
    "$MASTER_DIR/" "$DEST/"

  DEST_VERSION=$(cat "$DEST/VERSION" 2>/dev/null || echo "unknown")
  if [[ "$DEST_VERSION" == "$MASTER_VERSION" ]]; then
    echo "✅ $DEST (VERSION=$DEST_VERSION)"
    SYNCED=$((SYNCED + 1))
  else
    echo "❌ $DEST (同步后 VERSION=$DEST_VERSION ≠ master $MASTER_VERSION)" >&2
    SKIPPED=$((SKIPPED + 1))
  fi
done

echo ""
if [[ -n "$DRY_RUN" ]]; then
  echo "[DRY RUN 完毕] 共 ${#DESTINATIONS[@]} 个目标"
else
  echo "同步完成：$SYNCED 成功，$SKIPPED 跳过/失败（共 ${#DESTINATIONS[@]} 个）"
  echo ""
  echo "验证所有 5 副本（含 master）版本："
  echo "  $MASTER_DIR/VERSION → $MASTER_VERSION"
  for DEST in "${DESTINATIONS[@]}"; do
    if [[ -f "$DEST/VERSION" ]]; then
      printf "  %s/VERSION → %s\n" "$DEST" "$(cat "$DEST/VERSION")"
    fi
  done
fi
