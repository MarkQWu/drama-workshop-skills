#!/usr/bin/env python3
"""
角色跨集一致性检查工具

用法:
    python scripts/character_consistency_check.py
    python scripts/character_consistency_check.py --dir /path/to/project
    python scripts/character_consistency_check.py --dir /path/to/project --episodes 1-20
    python scripts/character_consistency_check.py --dir /path/to/project --format json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


# ── 外貌锚定词表 ──────────────────────────────────────────────────────────────

HAIR_COLOR_WORDS = [
    "黑发", "金发", "红发", "棕发", "白发", "银发", "青发", "紫发", "蓝发",
    "黑色头发", "金色头发", "红色头发", "棕色头发", "白色头发",
    "乌发", "乌黑头发", "乌黑",
]

EYE_COLOR_WORDS = [
    "黑眸", "棕眸", "蓝眸", "绿眸", "金眸", "琥珀眸",
    "黑眼", "棕眼", "蓝眼", "绿眼", "金眼",
    "黑色眼", "蓝色眼", "绿色眼", "棕色眼",
]

HAIR_COLOR_GROUPS = {
    "黑": {"黑发", "乌发", "黑色头发", "乌黑头发", "乌黑"},
    "金": {"金发", "金色头发"},
    "红": {"红发", "红色头发"},
    "棕": {"棕发", "棕色头发"},
    "白/银": {"白发", "银发", "白色头发"},
    "其他": {"青发", "紫发", "蓝发"},
}

EYE_COLOR_GROUPS = {
    "黑": {"黑眸", "黑眼", "黑色眼"},
    "棕/琥珀": {"棕眸", "棕眼", "棕色眼", "琥珀眸"},
    "蓝": {"蓝眸", "蓝眼", "蓝色眼"},
    "绿": {"绿眸", "绿眼", "绿色眼"},
    "金": {"金眸", "金眼"},
}


def get_color_group(word: str, groups: dict) -> Optional[str]:
    for group_name, members in groups.items():
        if word in members:
            return group_name
    return None


# ── 解析 characters.md ────────────────────────────────────────────────────────

def parse_characters(project_dir: Path) -> list[dict]:
    chars_file = project_dir / "characters.md"
    if not chars_file.exists():
        return []

    content = chars_file.read_text(encoding="utf-8")
    characters = []

    # 按角色 section 切分（以 ## 或 ### 开头的标题块）
    sections = re.split(r"\n(?=#{2,3}\s)", content)

    for section in sections:
        name_match = re.search(r"\*\*姓名\*\*[：:]\s*(.+?)(?:\s*[\n\*])", section)
        if not name_match:
            continue

        name = name_match.group(1).strip()
        if not name or len(name) > 12:
            continue

        # 年龄
        age_match = re.search(r"\*\*年龄\*\*[：:]\s*(\d+)", section)
        age = int(age_match.group(1)) if age_match else None

        # 外貌特征
        appear_match = re.search(
            r"\*\*外貌特征\*\*[：:]\s*(.+?)(?=\n\*\*|\Z)", section, re.DOTALL
        )
        appearance = appear_match.group(1).strip() if appear_match else ""

        # 性格关键词
        personality_match = re.search(r"\*\*性格关键词\*\*[：:]\s*(.+?)(?=\n|\Z)", section)
        personality = personality_match.group(1).strip() if personality_match else ""

        # 角色弧线
        arc_match = re.search(
            r"\*\*角色弧线[^*]*\*\*[：:]\s*(.+?)(?=\n\*\*|\Z)", section, re.DOTALL
        )
        arc = arc_match.group(1).strip() if arc_match else ""

        characters.append({
            "name": name,
            "age": age,
            "appearance": appearance,
            "personality": personality,
            "arc": arc,
        })

    return characters


# ── 外貌锚定提取 ──────────────────────────────────────────────────────────────

def extract_appearance_anchors(appearance_text: str) -> dict:
    anchors = {}

    for word in HAIR_COLOR_WORDS:
        if word in appearance_text:
            anchors["hair_color"] = word
            anchors["hair_group"] = get_color_group(word, HAIR_COLOR_GROUPS)
            break

    for word in EYE_COLOR_WORDS:
        if word in appearance_text:
            anchors["eye_color"] = word
            anchors["eye_group"] = get_color_group(word, EYE_COLOR_GROUPS)
            break

    height_match = re.search(r"(\d{3})\s*(?:cm|厘米)", appearance_text)
    if height_match:
        anchors["height_cm"] = int(height_match.group(1))

    return anchors


# ── 集数文件获取 ──────────────────────────────────────────────────────────────

def get_episode_files(project_dir: Path, ep_range: Optional[tuple] = None) -> list[Path]:
    episodes_dir = project_dir / "episodes"
    if not episodes_dir.exists():
        return []

    files = sorted(episodes_dir.glob("ep*.md"))

    if ep_range is None:
        return files

    start, end = ep_range
    filtered = []
    for f in files:
        m = re.match(r"ep0*(\d+)", f.stem)
        if m and start <= int(m.group(1)) <= end:
            filtered.append(f)
    return filtered


def ep_label(ep_path: Path) -> str:
    m = re.match(r"ep0*(\d+)", ep_path.stem)
    return f"ep{m.group(1)}" if m else ep_path.stem


# ── 单集扫描 ──────────────────────────────────────────────────────────────────

def strip_bible_appendix(content: str) -> str:
    """剥离考据附录（与 /分集 / /导出 逻辑一致）"""
    marker = "<!-- 剧本正文到此结束 -->"
    if marker in content:
        return content[: content.index(marker)]
    return content


def scan_episode(ep_path: Path, char: dict) -> list[dict]:
    raw = ep_path.read_text(encoding="utf-8")
    content = strip_bible_appendix(raw)
    label = ep_label(ep_path)
    issues = []

    if char["name"] not in content:
        return []

    name = char["name"]

    # ─ 1. 年龄一致性 ─
    if char["age"]:
        for m in re.finditer(re.escape(name), content):
            window = content[max(0, m.start() - 120) : m.end() + 120]
            for age_match in re.finditer(r"(\d+)\s*岁", window):
                found_age = int(age_match.group(1))
                # 排除不合理数字（年代数字、集数等）；允许 ±1（生日当天）
                if found_age < 10 or found_age > 100:
                    continue
                if abs(found_age - char["age"]) > 1:
                    issues.append({
                        "type": "age_mismatch",
                        "severity": "error",
                        "ep": label,
                        "char": name,
                        "expected": f"{char['age']}岁",
                        "found": f"{found_age}岁",
                        "context": window.strip()[:100],
                    })

    # ─ 2. 外貌颜色一致性 ─
    if char["appearance"]:
        anchors = extract_appearance_anchors(char["appearance"])

        if "hair_group" in anchors:
            for m in re.finditer(re.escape(name), content):
                window = content[max(0, m.start() - 60) : m.end() + 120]
                for word in HAIR_COLOR_WORDS:
                    if word in window:
                        found_group = get_color_group(word, HAIR_COLOR_GROUPS)
                        if found_group and found_group != anchors["hair_group"]:
                            issues.append({
                                "type": "appearance_conflict",
                                "severity": "warning",
                                "ep": label,
                                "char": name,
                                "attr": "发色",
                                "expected": f"{anchors['hair_group']}系（{anchors['hair_color']}）",
                                "found": word,
                                "context": window.strip()[:100],
                            })

        if "eye_group" in anchors:
            for m in re.finditer(re.escape(name), content):
                window = content[max(0, m.start() - 60) : m.end() + 120]
                for word in EYE_COLOR_WORDS:
                    if word in window:
                        found_group = get_color_group(word, EYE_COLOR_GROUPS)
                        if found_group and found_group != anchors["eye_group"]:
                            issues.append({
                                "type": "appearance_conflict",
                                "severity": "warning",
                                "ep": label,
                                "char": name,
                                "attr": "眼色",
                                "expected": f"{anchors['eye_group']}系（{anchors['eye_color']}）",
                                "found": word,
                                "context": window.strip()[:100],
                            })

        if "height_cm" in anchors:
            for m in re.finditer(re.escape(name), content):
                window = content[max(0, m.start() - 80) : m.end() + 80]
                for hm in re.finditer(r"(\d{3})\s*(?:cm|厘米)", window):
                    found_h = int(hm.group(1))
                    if abs(found_h - anchors["height_cm"]) > 3:
                        issues.append({
                            "type": "appearance_conflict",
                            "severity": "warning",
                            "ep": label,
                            "char": name,
                            "attr": "身高",
                            "expected": f"{anchors['height_cm']}cm",
                            "found": f"{found_h}cm",
                            "context": window.strip()[:100],
                        })

    # ─ 3. 去重（同类型+同集+同角色+同找到值）─
    seen: set[tuple] = set()
    deduped = []
    for issue in issues:
        key = (issue["type"], issue["ep"], issue["char"], issue.get("found", ""))
        if key not in seen:
            seen.add(key)
            deduped.append(issue)

    return deduped


# ── 主流程 ───────────────────────────────────────────────────────────────────

def parse_ep_range(s: Optional[str]) -> Optional[tuple]:
    if not s:
        return None
    m = re.match(r"^(\d+)(?:-(\d+))?$", s)
    if not m:
        return None
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else start
    return (start, end)


def main() -> int:
    parser = argparse.ArgumentParser(description="角色跨集一致性检查（硬事实层）")
    parser.add_argument("--dir", default=".", help="项目目录（默认当前目录）")
    parser.add_argument("--episodes", default=None, help="集数范围，如 1-20")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    project_dir = Path(args.dir).expanduser().resolve()
    ep_range = parse_ep_range(args.episodes)

    characters = parse_characters(project_dir)
    if not characters:
        print("❌ characters.md 不存在或未解析到角色信息", file=sys.stderr)
        return 1

    episode_files = get_episode_files(project_dir, ep_range)
    if not episode_files:
        print("❌ 未找到剧集文件（episodes/*.md）", file=sys.stderr)
        return 1

    all_issues: list[dict] = []
    for ep_file in episode_files:
        for char in characters:
            all_issues.extend(scan_episode(ep_file, char))

    if args.format == "json":
        print(json.dumps(all_issues, ensure_ascii=False, indent=2))
        return 1 if any(i["severity"] == "error" for i in all_issues) else 0

    # ── 文本报告 ──
    print("=" * 60)
    print("🎭 角色一致性检查报告（硬事实层）")
    print(f"   项目：{project_dir.name}")
    print(f"   扫描：{len(episode_files)} 集 / {len(characters)} 个角色")
    range_desc = f"ep{ep_range[0]}-ep{ep_range[1]}" if ep_range else "全部"
    print(f"   范围：{range_desc}")
    print("=" * 60)

    if not all_issues:
        print("\n✅ 未发现硬性矛盾（年龄 / 外貌颜色 / 身高）")
    else:
        by_char: dict[str, list] = {}
        for issue in all_issues:
            by_char.setdefault(issue["char"], []).append(issue)

        for char_name, issues in by_char.items():
            print(f"\n⚠  {char_name}")
            for issue in sorted(issues, key=lambda x: (x["severity"], x["ep"])):
                marker = "❌" if issue["severity"] == "error" else "⚠ "
                if issue["type"] == "age_mismatch":
                    print(f"  {marker} [{issue['ep']}] 年龄矛盾")
                    print(f"       设定：{issue['expected']}  |  本集出现：{issue['found']}")
                elif issue["type"] == "appearance_conflict":
                    print(f"  {marker} [{issue['ep']}] {issue['attr']}可能矛盾")
                    print(f"       设定：{issue['expected']}  |  本集出现：{issue['found']}")
                print(f"       上下文：「{issue['context'][:80]}」")

    errors = sum(1 for i in all_issues if i["severity"] == "error")
    warnings = sum(1 for i in all_issues if i["severity"] == "warning")

    print(f"\n{'=' * 60}")
    print(f"❌ 严重（必修）：{errors} 项  ⚠  待核查：{warnings} 项")
    if all_issues:
        print("说明：外貌矛盾需人工确认（可能是描写其他角色）")
    print("=" * 60)

    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
