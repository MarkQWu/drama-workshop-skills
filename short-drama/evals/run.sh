#!/usr/bin/env bash
# short-drama skill 评测半手动 runner
#
# 用法：
#   bash evals/run.sh <project-dir> <sample-name>
#
# 例：
#   bash evals/run.sh ~/short-drama-projects/重回十八岁那年的盛夏 domestic-test
#   bash evals/run.sh ~/short-drama-projects/CEO-Hidden-Heir overseas-test
#
# 前置条件：
#   1. 已用 sample 内容跑完 /开始 → /策划 → /分集目录 → /分集 1 → /自检 1
#   2. 项目目录下有 episodes/ep001.md + checks/ep001-check.md（或旧 reviews/ep001-review.md）+ creative-plan.md

set -uo pipefail

PROJECT_DIR="${1:-}"
SAMPLE="${2:-}"

if [[ -z "$PROJECT_DIR" || -z "$SAMPLE" ]]; then
  echo "用法：bash evals/run.sh <project-dir> <sample-name>"
  echo "  sample-name: domestic-test | overseas-test"
  exit 1
fi

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "❌ 项目目录不存在：$PROJECT_DIR"
  exit 1
fi

EP1="$PROJECT_DIR/episodes/ep001.md"
REVIEW="$PROJECT_DIR/checks/ep001-check.md"
if [[ ! -f "$REVIEW" && -f "$PROJECT_DIR/reviews/ep001-review.md" ]]; then
  REVIEW="$PROJECT_DIR/reviews/ep001-review.md"
fi
PLAN="$PROJECT_DIR/creative-plan.md"

for f in "$EP1" "$REVIEW" "$PLAN"; do
  if [[ ! -f "$f" ]]; then
    echo "❌ 缺文件：$f"
    echo "   请先跑完 /策划 + /分集 1 + /自检 1"
    exit 1
  fi
done

PASS=0
FAIL=0
NA=0

check() {
  local name="$1"
  local result="$2"
  local detail="${3:-}"
  case "$result" in
    PASS) echo "  ✅ $name PASS  $detail"; PASS=$((PASS+1));;
    FAIL) echo "  ❌ $name FAIL  $detail"; FAIL=$((FAIL+1));;
    NA)   echo "  ⚪ $name N/A   $detail"; NA=$((NA+1));;
    *)    echo "  ⚠️  $name UNKNOWN $detail";;
  esac
}

echo "=== short-drama skill eval: $SAMPLE ==="
echo "Project: $PROJECT_DIR"
echo ""

# 判定是否海外模式
IS_OVERSEAS=0
if grep -qE '"mode"\s*:\s*"overseas"' "$PROJECT_DIR/.drama-state.json" 2>/dev/null; then
  IS_OVERSEAS=1
fi

# A1: anchor 字段（全 13 题材）
echo "## A1 anchor 字段触发"
if grep -qE "都市情感|霸道总裁|甜宠|重生穿越|古装宫廷|励志逆袭|悬疑探案|战神归来|家庭伦理|萌宝|软科幻|末日重生|喜剧" "$PLAN"; then
  if grep -qE "^## anchor|^### anchor|^- anchor:|anchor:" "$PLAN"; then
    check "A1" "PASS" "(creative-plan.md 含 anchor 字段)"
  else
    check "A1" "FAIL" "(国内 13 题材但 creative-plan 缺 anchor 字段 → anchor-trigger.md 未生效)"
  fi
else
  check "A1" "NA" "(题材未命中国内 13 题材，或出海模式)"
fi

# A2: 前 1/3 字数有冲突词
echo ""
echo "## A2 开场冲突字数位置"
TOTAL_CHARS=$(grep -v '^>' "$EP1" | grep -v '^---' | grep -v '^<!--' | wc -m | tr -d ' ')
THIRD=$((TOTAL_CHARS / 3))
HEAD_CONTENT=$(head -c $THIRD "$EP1")
CONFLICT_COUNT=$(echo "$HEAD_CONTENT" | grep -cE "打|撞|推|摔|抓|逃|追|跪|怒吼|咆哮|尖叫|怒斥|质问|背叛|撕破脸|当众|打脸|揭穿|血|刀|枪|急诊|trembling|frozen|shock|scream|grab|push|crash" || true)
if [[ "$CONFLICT_COUNT" -ge 1 ]]; then
  check "A2" "PASS" "(前 1/3 命中 $CONFLICT_COUNT 次冲突词)"
else
  check "A2" "FAIL" "(前 1/3 字数 0 冲突 → opening-rules.md 未生效)"
fi

# A3: 海外模式呈现格式（仅 overseas）
echo ""
echo "## A3 海外模式呈现格式 + 反中式弧"
if [[ "$IS_OVERSEAS" -eq 1 ]]; then
  IS_HOLLYWOOD=0
  if grep -qE '"scriptFormat"\s*:\s*"hollywood"' "$PROJECT_DIR/.drama-state.json" 2>/dev/null; then
    IS_HOLLYWOOD=1
  fi
  if [[ "$IS_HOLLYWOOD" -eq 1 ]]; then
    FORMAT_HEAD=$(grep -cE "^INT\.|^EXT\." "$EP1" || true)
    FORMAT_MARK=$(grep -cE "VISUAL ANCHOR|CLOSE-UP|MEDIUM SHOT" "$EP1" || true)
  else
    FORMAT_HEAD=$(grep -cE "^## [0-9]+-[0-9]+ · (内|外)" "$EP1" || true)
    FORMAT_MARK=$(grep -cE "视觉锚点|特写|近景" "$EP1" || true)
  fi
  CHINESE_ARC=$(grep -cE "赘婿|逆袭|打脸|废柴|战神|神医归来|凤凰涅槃" "$EP1" || true)
  if [[ "$FORMAT_HEAD" -ge 1 && "$FORMAT_MARK" -ge 1 && "$CHINESE_ARC" -eq 0 ]]; then
    check "A3" "PASS" "(formatHead=$FORMAT_HEAD, formatMark=$FORMAT_MARK, 中式弧禁词=0)"
  else
    check "A3" "FAIL" "(formatHead=$FORMAT_HEAD, formatMark=$FORMAT_MARK, 中式弧禁词=$CHINESE_ARC)"
  fi
else
  check "A3" "NA" "(mode=domestic)"
fi

# A4: 自检 7 维度齐全
echo ""
echo "## A4 自检 7 维度齐全"
DIM_COUNT=0
for dim in "节奏" "爽点" "台词" "格式与可拍性" "主线与连贯性" "反抽象" "AI Slop"; do
  if grep -q "$dim" "$REVIEW"; then
    DIM_COUNT=$((DIM_COUNT+1))
  else
    echo "    ⚠️ 缺维度：$dim"
  fi
done
if [[ "$DIM_COUNT" -ge 7 ]]; then
  check "A4" "PASS" "($DIM_COUNT/7 维度命中)"
else
  check "A4" "FAIL" "($DIM_COUNT/7 维度，缺 $((7-DIM_COUNT)) 个 → quality-rubric.md 未加载完整)"
fi

# A5: dramatic-truth 4 症状触发
echo ""
echo "## A5 dramatic-truth 4 症状触发（v1.19.0 新增）"
DT_COUNT=$(grep -cE "Trailer-Speak|Metaphor Overdose|As-You-Know-Bob|Urgency Mismatch" "$REVIEW" || true)
if [[ "$DT_COUNT" -ge 1 ]]; then
  check "A5" "PASS" "(4 症状清单中 $DT_COUNT 个被触发记录 → dramatic-truth.md 已加载)"
else
  check "A5" "FAIL" "(0 症状 → SKILL.md L300 引用 silent-fail，dramatic-truth.md 未读)"
fi

# A6: 中式表达扣分（仅 overseas）
echo ""
echo "## A6 海外模式中式表达扣分"
if [[ "$IS_OVERSEAS" -eq 1 ]]; then
  CN_EXPR_IN_EP1=$(grep -cE "心如刀绞|双瞳如墨|星眸|面如冠玉|肤白胜雪|提到嗓子眼|走马灯般|胸口憋着|魂七魄|骨头都酥|五脏六腑" "$EP1" || true)
  CN_EXPR_FLAGGED=$(grep -E "心如刀绞|双瞳如墨|星眸|面如冠玉|肤白胜雪|提到嗓子眼|走马灯般" "$REVIEW" 2>/dev/null | grep -cE "扣分|建议|【严重】|【建议】|改写|flagged|deduct" || true)
  if [[ "$CN_EXPR_IN_EP1" -eq 0 ]]; then
    check "A6" "NA" "(剧本未含中式表达 → 自检无需标记)"
  elif [[ "$CN_EXPR_FLAGGED" -ge 1 ]]; then
    check "A6" "PASS" "(剧本含 $CN_EXPR_IN_EP1 处中式表达，自检标记 $CN_EXPR_FLAGGED 处)"
  else
    check "A6" "FAIL" "(剧本含 $CN_EXPR_IN_EP1 处中式表达但自检 0 标记 → anti-patterns.md 禁词表失效)"
  fi
else
  check "A6" "NA" "(mode=domestic)"
fi

echo ""
echo "## A7 CONTINUITY 块位置与字段"
BOUNDARY_LINE=$(grep -n "<!-- 剧本正文到此结束 -->" "$EP1" | head -1 | cut -d: -f1 || true)
CONTINUITY_LINE=$(grep -n "<!-- CONTINUITY" "$EP1" | head -1 | cut -d: -f1 || true)
CONTINUITY_FIELDS=$(grep -cE "角色状态变化：|伏笔与回收：|尾钩义务：" "$EP1" || true)
OLD_FIELDS=$(grep -cE "核心事件：|新增伏笔：|回收伏笔：|需要后续强化：" "$EP1" || true)
if [[ -n "$BOUNDARY_LINE" && -n "$CONTINUITY_LINE" && "$CONTINUITY_LINE" -gt "$BOUNDARY_LINE" && "$CONTINUITY_FIELDS" -ge 3 && "$OLD_FIELDS" -eq 0 ]]; then
  check "A7" "PASS" "(boundary=$BOUNDARY_LINE, continuity=$CONTINUITY_LINE, fields=$CONTINUITY_FIELDS)"
else
  check "A7" "FAIL" "(boundary=${BOUNDARY_LINE:-missing}, continuity=${CONTINUITY_LINE:-missing}, fields=$CONTINUITY_FIELDS, oldFields=$OLD_FIELDS)"
fi

echo ""
echo "## A8 ledger 创建与分集索引"
LEDGER="$PROJECT_DIR/continuity-ledger.md"
if [[ -f "$LEDGER" ]]; then
  LEDGER_SECTIONS=$(grep -cE "^## 角色动态状态|^## 活跃主线伏笔|^## 分集索引" "$LEDGER" || true)
  LEDGER_EP1=$(grep -cE "^\| *1 *\||第1集|ep001" "$LEDGER" || true)
  if [[ "$LEDGER_SECTIONS" -ge 3 && "$LEDGER_EP1" -ge 1 ]]; then
    check "A8" "PASS" "(sections=$LEDGER_SECTIONS, ep1=$LEDGER_EP1)"
  else
    check "A8" "FAIL" "(sections=$LEDGER_SECTIONS, ep1=$LEDGER_EP1)"
  fi
else
  check "A8" "FAIL" "(continuity-ledger.md 不存在)"
fi

echo ""
echo "## A9 尾钩义务承接"
EP2="$PROJECT_DIR/episodes/ep002.md"
CHECK2="$PROJECT_DIR/checks/ep002-check.md"
if [[ -f "$EP2" ]]; then
  HOOK_CARRY=$(head -n 80 "$EP2" | grep -cE "匿名短信|报告不是原件|尾钩|上一集" || true)
  CHECK_CARRY=0
  if [[ -f "$CHECK2" ]]; then
    CHECK_CARRY=$(grep -cE "尾钩义务|承接上一集|连续性" "$CHECK2" || true)
  fi
  if [[ "$HOOK_CARRY" -ge 1 && "$CHECK_CARRY" -ge 1 ]]; then
    check "A9" "PASS" "(ep2 head carry=$HOOK_CARRY, check=$CHECK_CARRY)"
  else
    check "A9" "FAIL" "(ep2 head carry=$HOOK_CARRY, check=$CHECK_CARRY)"
  fi
else
  check "A9" "NA" "(未提供 ep002 连续性 fixture)"
fi

echo ""
echo "## A10 交付路径剥离 CONTINUITY"
LEAK_COUNT=0
if [[ -d "$PROJECT_DIR/export" ]]; then
  LEAK_COUNT=$((LEAK_COUNT + $(grep -R -cE "CONTINUITY|角色状态变化：|伏笔与回收：|尾钩义务：" "$PROJECT_DIR/export" 2>/dev/null | awk -F: '{s+=$2} END{print s+0}')))
fi
if [[ -d "$PROJECT_DIR/storyboards" ]]; then
  LEAK_COUNT=$((LEAK_COUNT + $(grep -R -cE "CONTINUITY|角色状态变化：|伏笔与回收：|尾钩义务：" "$PROJECT_DIR/storyboards" 2>/dev/null | awk -F: '{s+=$2} END{print s+0}')))
fi
if [[ "$LEAK_COUNT" -eq 0 ]]; then
  check "A10" "PASS" "(export/storyboards 未检出机器块)"
else
  check "A10" "FAIL" "(export/storyboards 检出 $LEAK_COUNT 处机器块)"
fi

echo ""
echo "## A11 老项目 bootstrap"
if [[ -f "$LEDGER" ]]; then
  BOOTSTRAP_INDEX=$(grep -cE "^## 分集索引" "$LEDGER" || true)
  BOOTSTRAP_RECENT=$(grep -cE "1|2|3|ep001|ep002|ep003|第1集|第2集|第3集" "$LEDGER" || true)
  BOOTSTRAP_HOOK=$(grep -cE "尾钩|义务|下一集" "$LEDGER" || true)
  if [[ "$BOOTSTRAP_INDEX" -ge 1 && "$BOOTSTRAP_RECENT" -ge 3 && "$BOOTSTRAP_HOOK" -ge 1 ]]; then
    check "A11" "PASS" "(index=$BOOTSTRAP_INDEX, recent=$BOOTSTRAP_RECENT, hook=$BOOTSTRAP_HOOK)"
  else
    check "A11" "NA" "(非老项目 bootstrap fixture，index=$BOOTSTRAP_INDEX, recent=$BOOTSTRAP_RECENT, hook=$BOOTSTRAP_HOOK)"
  fi
else
  check "A11" "NA" "(无 ledger，非 bootstrap fixture 或 A8 已失败)"
fi

# 汇总
echo ""
echo "=== 汇总 ==="
echo "PASS: $PASS / FAIL: $FAIL / N/A: $NA"

if [[ "$FAIL" -gt 0 ]]; then
  echo "❌ 有 $FAIL 条断言不通过 — 检查上方 FAIL 详情"
  echo ""
  echo "建议下一步："
  echo "  1. 记录失败 case 到 baseline-vX.X.X.md"
  echo "  2. 调查根因（SKILL.md 引用断 / references/ 文件丢失 / 模型未读）"
  echo "  3. 修正后重跑"
  exit 1
fi

echo "✅ 全部断言通过（含 N/A）"
echo ""
echo "建议下一步："
echo "  1. 把本次结果记录为 baseline-vX.X.X.md（首次跑）或与上一 baseline 对比（回归测试）"
echo "  2. 主观维度（voice / 90s 节奏 / 平台适配感）人工评 1-10 也记录到 baseline"
exit 0
