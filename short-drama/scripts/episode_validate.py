#!/usr/bin/env python3
"""集级格式 validator（机械化地基层检查）。

规则来源（规则变更时同步本脚本）：
- references/output-templates-core.md#分集国内模式 / #分集国内模式-comic / #分集出海模式
- SKILL.md /分集 生成规则（破折号禁用、对白段落边界、同名 cue 合并）

哲学：写作过程只 warn 不阻断；exit code 2 仅在 HARD 项失败时返回，
供调用方（/分集 保存后校验、CI、批量质检）判断是否需要修复。

用法：
  python3 episode_validate.py <episode.md> [--medium ai_live|comic|auto]
      [--mode domestic|overseas|auto] [--project DIR] [--json]

medium/mode 解析优先级：显式参数 > --project 的 .drama-state.json > 内容推断。
exit: 0 = 无 HARD 失败；1 = 用法/IO 错误；2 = 存在 HARD 失败。
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

BOUNDARY = "<!-- 剧本正文到此结束 -->"
SCENE_AI_LIVE = re.compile(r"^## \d+-\d+ · [内外] · .+ · [日夜]\s*$")
SCENE_COMIC = re.compile(r"^## \d+-\d+[日夜]/[内外] .+$")
SCENE_EN = re.compile(r"^## Scene \d+\s*$")
SCENE_ANY_DIGIT = re.compile(r"^## \d")
TITLE_CN = re.compile(r"^# 第\d+集：.+")
TITLE_EN = re.compile(r"^# Episode \d+: .+")
SPEAKER_CUE = re.compile(r"\*\*[^*\n]{1,20}\*\*(（[^）]*）)?(\(OS\)|\(VO\))?：")
# E015：裸对白 cue（角色名未 **加粗**）。行首排除模板合法前缀后再匹配。
# 半角冒号要求后随空白（排除 http:// 与 12:30）；角色名可含空格，总长 ≤20 防叙述句误判。
BARE_CUE_SKIP_PREFIX = ("**", "△", ">", "#", "【", "（", "(", "[", "-", "|", "`")
BARE_SPEAKER_CUE = re.compile(r"^([^：:*（）()\n]{1,20})(（[^）]*）|\([^)]*\))?(?:：|:(?=\s))")
# E016：加粗 cue 解析（含 comic 变体 `**名字**OS(情绪)：`）。
BOLD_SPEAKER_CUE = re.compile(
    r"^\*\*([^*\n]{1,20})\*\*\s*(OS|VO)?\s*(（[^）]*）|\([^)]*\))?\s*(?:：|:(?=\s))")
# E014：markdown 表格分隔行（`| --- |`、`|---|---|`、`|:---|---:|`）豁免。
TABLE_SEP_LINE = re.compile(r"^[|\-:\s]+$")


def parse_cue(stripped):
    """解析台词 cue 行，返回 (speaker, form) 或 None（非台词行）。

    form 枚举：normal / OS / VO。语气括号（OS/VO 以外的括号内容）不影响 form。
    """
    m = BOLD_SPEAKER_CUE.match(stripped)
    if m:
        speaker, token, paren = m.group(1).strip(), m.group(2), m.group(3)
    elif stripped.startswith(BARE_CUE_SKIP_PREFIX):
        return None
    else:
        bm = BARE_SPEAKER_CUE.match(stripped)
        if not bm:
            return None
        speaker, token, paren = bm.group(1).strip(), None, bm.group(2)
    if token in ("OS", "VO"):
        form = token
    elif paren:
        inner = paren[1:-1].strip().upper()
        form = "OS" if inner.startswith("OS") else "VO" if inner.startswith("VO") else "normal"
    else:
        form = "normal"
    return speaker, form


def add(findings, severity, code, msg):
    findings.append({"severity": severity, "code": code, "message": msg})


def split_body(lines):
    """返回 (body_lines, boundary_count)。body = 首行到边界标记前。"""
    boundary_idx = [i for i, l in enumerate(lines) if l.strip() == BOUNDARY]
    end = boundary_idx[0] if boundary_idx else len(lines)
    return lines[:end], len(boundary_idx)


def detect_medium(text):
    if any(SCENE_COMIC.match(l) for l in text.splitlines()):
        return "comic"
    return "ai_live"


def detect_mode(text):
    if TITLE_EN.match(text.splitlines()[0] if text.splitlines() else ""):
        return "overseas"
    return "domestic"


def validate(text, medium, mode, project_dir=None, episode_num=None):
    findings = []
    lines = text.splitlines()
    body, boundary_count = split_body(lines)

    # E008 边界标记
    if boundary_count == 0:
        add(findings, "HARD", "E008", f"缺少边界标记 {BOUNDARY}")
    elif boundary_count > 1:
        add(findings, "HARD", "E008", f"边界标记出现 {boundary_count} 次（应恰好 1 次）")

    # E001 标题
    first = next((l for l in lines if l.strip()), "")
    if mode == "overseas":
        if not (TITLE_CN.match(first) or TITLE_EN.match(first)):
            add(findings, "HARD", "E001", f"首行标题不合规：{first[:40]!r}（应为 `# 第N集：标题` 或 `# Episode N: Title`）")
    elif not TITLE_CN.match(first):
        add(findings, "HARD", "E001", f"首行标题不合规：{first[:40]!r}（应为 `# 第N集：标题`）")

    # E002/E003 元数据（国内）
    if mode == "domestic":
        if not any(l.startswith("> 本集关键词：") for l in body):
            add(findings, "HARD", "E002", "缺少 `> 本集关键词：` 元数据行")
        if not any(l.startswith("> 本集爽点：") for l in body):
            add(findings, "HARD", "E003", "缺少 `> 本集爽点：` 元数据行")
        if not any(l.startswith("> 前情提要：") for l in body):
            add(findings, "WARN", "W001", "缺少 `> 前情提要：` 行（第 1 集可写 `无`）")

    # E005 场景头。模板规定正文「不添加模板外区块」，故正文内所有 `## ` 标题
    # 都按场景头校验——backtick / 错分隔 / 自创区块标题一律捕获。
    scene_re = SCENE_COMIC if medium == "comic" else SCENE_AI_LIVE
    h2_headings = [l for l in body if l.startswith("## ")]
    scene_headings = [l for l in h2_headings if scene_re.match(l)]
    if mode == "overseas":
        en_scenes = [l for l in body if SCENE_EN.match(l)]
        if not (scene_headings or en_scenes or h2_headings):
            add(findings, "HARD", "E005", "未找到任何场景头")
        scene_headings = scene_headings or en_scenes or h2_headings
    else:
        if not h2_headings:
            add(findings, "HARD", "E005", "未找到任何场景头（`## N-N ...`）")
        else:
            bad = [l for l in h2_headings if not scene_re.match(l)]
            for l in bad[:5]:
                expected = "`## N-N日/内 地点`（comic 紧凑格式）" if medium == "comic" else "`## N-N · 内|外 · 地点 · 日|夜`"
                add(findings, "HARD", "E005", f"场景头格式不合规：{l[:50]!r}（应为 {expected}，无 backtick）")

    n_scenes = len(scene_headings)

    # E013 comic 场景数 H1
    if medium == "comic" and mode == "domestic" and n_scenes > 3:
        add(findings, "HARD", "E013", f"comic 场景数 {n_scenes} > 3（H1 硬约束）")

    # E006/E007 出场人物/道具（国内）
    if mode == "domestic" and n_scenes:
        n_chars = sum(1 for l in body if l.startswith("**出场人物：**"))
        n_props = sum(1 for l in body if l.startswith("**出场道具：**"))
        if n_chars < n_scenes:
            add(findings, "HARD", "E006", f"`**出场人物：**` 行 {n_chars} 个 < 场景数 {n_scenes}（每场必填）")
        if n_props < n_scenes:
            add(findings, "HARD", "E007", f"`**出场道具：**` 行 {n_props} 个 < 场景数 {n_scenes}（每场必填，可留空值）")

    # E009 CONTINUITY 块
    cont_match = re.search(r"<!-- CONTINUITY\n(.*?)-->", text, re.S)
    if not cont_match:
        add(findings, "HARD", "E009", "缺少 `<!-- CONTINUITY ... -->` 注释块")
    else:
        cont = cont_match.group(1)
        for field in ("角色状态变化：", "伏笔与回收：", "尾钩义务："):
            if field not in cont:
                add(findings, "HARD", "E009", f"CONTINUITY 块缺少字段 `{field[:-1]}`")
        m = re.search(r"尾钩义务：(.*)", cont)
        if m is not None and not m.group(1).strip():
            add(findings, "WARN", "W005", "CONTINUITY 尾钩义务为空（最后一集可为空，其余集必须有）")

    # E010/E011 钩子与预告
    if not any(re.match(r"^> \[钩子\]", l) for l in body):
        add(findings, "HARD", "E010", "缺少 `> [钩子]` 行")
    if not any(re.match(r"^> \[预告\]", l) for l in body):
        add(findings, "HARD", "E011", "缺少 `> [预告]` 行")

    # E012 集末自查（国内）
    if mode == "domestic":
        for tag, code in (("[锚点]", "E012"), ("[爽点]", "E012"), ("[商业]", "E012")):
            if not any(tag in l and l.startswith(">") for l in body):
                add(findings, "HARD", code, f"集末自查缺少 `{tag}` 行")
        sat = next((l for l in body if l.startswith(">") and "[爽点]" in l), "")
        if sat and len(re.findall(r"\d+\.", sat)) < 3:
            add(findings, "WARN", "W002", "集末自查爽点清单不足 3 个独立条目")

    # E014 破折号禁用（剧本正文范围：首个场景头 → 边界标记）
    start = next((i for i, l in enumerate(body) if SCENE_ANY_DIGIT.match(l) or SCENE_EN.match(l)), 0)
    for i, l in enumerate(body[start:], start + 1):
        if re.search(r"——|—", l):
            add(findings, "HARD", "E014", f"第 {i} 行出现破折号（——/— 正文禁用）：{l.strip()[:40]!r}")
        elif ("--" in l and not re.match(r"^-{3,}\s*$", l) and "<!--" not in l and "-->" not in l
              and not ("|" in l and TABLE_SEP_LINE.match(l))):
            add(findings, "HARD", "E014", f"第 {i} 行出现 `--`（正文禁用）：{l.strip()[:40]!r}")

    # E015 裸对白 cue（角色名未加粗，剧本正文范围同 E014：首个场景头 → 边界标记）
    for i, l in enumerate(body[start:], start + 1):
        stripped = l.lstrip()
        if not stripped or stripped.startswith(BARE_CUE_SKIP_PREFIX):
            continue
        if BARE_SPEAKER_CUE.match(stripped):
            add(findings, "HARD", "E015",
                f"第 {i} 行裸对白 cue（角色名未加粗）：{stripped[:40]!r}（应为 `**角色名**：台词`）")

    # E016 相邻同名同形态 cue（范围同 E014/E015）。空行不隔断；任何非台词行重置。
    # 关键豁免：同名但 form 不同（台词后接同名 OS/VO）不报——模板推荐的合法拆层写法。
    last_cue = None
    for i, l in enumerate(body[start:], start + 1):
        stripped = l.strip()
        if not stripped:
            continue
        cue = parse_cue(stripped)
        if cue is None:
            last_cue = None
            continue
        if cue == last_cue:
            add(findings, "HARD", "E016",
                f"第 {i} 行与上一条台词同角色同形态（{cue[0]}/{cue[1]}）："
                f"同一角色连续发言应合并为一条台词")
        last_cue = cue

    # W004 对白段落边界（同一段落两个 speaker cue）
    for para in re.split(r"\n\s*\n", "\n".join(body[start:])):
        if len(SPEAKER_CUE.findall(para)) >= 2:
            add(findings, "WARN", "W004", f"同一段落出现多个对白 cue（应独占段落）：{para.strip()[:40]!r}")

    # W003 BGM/音效（ai_live 国内）
    if medium == "ai_live" and mode == "domestic":
        if not any(("（BGM：" in l or "（音效：" in l or "(BGM：" in l) for l in body):
            add(findings, "WARN", "W003", "全集无 BGM/音效标注（模板建议至少 1 处）")

    return findings


def main():
    ap = argparse.ArgumentParser(description="集级格式 validator")
    ap.add_argument("episode", help="episodes/ep{NNN}.md 路径")
    ap.add_argument("--medium", choices=["ai_live", "comic", "auto"], default="auto")
    ap.add_argument("--mode", choices=["domestic", "overseas", "auto"], default="auto")
    ap.add_argument("--project", help="项目根目录（读 .drama-state.json 解析 medium/mode）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    path = Path(args.episode)
    if not path.is_file():
        print(f"[错误] 文件不存在：{path}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")

    medium, mode = args.medium, args.mode
    if args.project:
        state_file = Path(args.project) / ".drama-state.json"
        if state_file.is_file():
            try:
                state = json.loads(state_file.read_text(encoding="utf-8"))
                if medium == "auto":
                    medium = state.get("medium") or "ai_live"
                if mode == "auto":
                    mode = state.get("mode") or "domestic"
            except (json.JSONDecodeError, OSError):
                pass
    if medium == "auto":
        medium = detect_medium(text)
    if mode == "auto":
        mode = detect_mode(text)

    ep_num = None
    m = re.search(r"ep(\d{3})", path.name)
    if m:
        ep_num = int(m.group(1))

    findings = validate(text, medium, mode, project_dir=args.project, episode_num=ep_num)
    hard = [f for f in findings if f["severity"] == "HARD"]
    warn = [f for f in findings if f["severity"] == "WARN"]

    if args.json:
        print(json.dumps({
            "file": str(path), "medium": medium, "mode": mode,
            "hard_count": len(hard), "warn_count": len(warn), "findings": findings,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"[validator] {path.name} medium={medium} mode={mode}")
        for f in findings:
            print(f"  {'✗' if f['severity'] == 'HARD' else '⚠'} {f['code']} {f['message']}")
        if not findings:
            print("  ✓ 全部通过")
        else:
            print(f"  小计：HARD {len(hard)} / WARN {len(warn)}")
    return 2 if hard else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    sys.exit(main())
