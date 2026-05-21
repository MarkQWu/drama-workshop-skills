#!/usr/bin/env python3
"""Prepare short-drama export markdown before DOCX rendering.

This script owns deterministic export work:
- parse episode ranges like "前10集", "1-10", "5,8,12"
- validate episode files
- strip appendices / CONTINUITY blocks
- extract available episode summaries from episode-directory.md
- print the fixed A/B/C/D menu
- build the temporary markdown consumed by export_docx.py

It intentionally does not invent semantic blocks. If synopsis or character
introductions are requested but no prepared block file is supplied, the script
reports missing blocks so the LLM can generate them explicitly.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable


BODY_MARKER = "<!-- 剧本正文到此结束 -->"
CONTINUITY_RE = re.compile(r"<!--\s*CONTINUITY\b.*?-->", re.DOTALL)

MENU_TEXT = """本次导出范围：{scope}
行业稿标准顺序固定为：剧情介绍 → 剧情脉络 → 人物介绍 → 分集梗概 → 正文/分集。

可选内容要素：
1. 剧情介绍（可选）：3-5 段完整梗概，说明整体设定、主线冲突、关键转折和结局方向。
2. 剧情脉络（可选）：按篇章或集数段概括，如“（1-10集）：开局篇……”，适合前 10 集试读或阶段交付。
3. 人物介绍（可选）：主要角色自然段介绍，包含身份、关系、性格和角色发展；不保留字段表。
4. 分集梗概（可选）：逐集短梗概，如“第一集……”，用于正文前快速看全局；可来自 episode-directory 或每集正文压缩。
5. 正文/分集（必选）：本次选定范围内的剧本正文。

请选择导出方案：
A. 标准行业稿（推荐）：1 + 2 + 3 + 4 + 5
B. 试读精简稿：2 + 3 + 4 + 5
C. 纯正文：5
D. 自定义：回复要包含的编号，如“1+3+5”"""

PROFILE_BLOCKS = {
    "standard": [1, 2, 3, 4, 5],
    "preview": [2, 3, 4, 5],
    "body": [5],
}

BLOCK_NAMES = {
    1: "剧情介绍",
    2: "剧情脉络",
    3: "人物介绍",
    4: "分集梗概",
    5: "正文",
}

INVALID_FILENAME_CHARS_RE = re.compile(r'[\\/:*?"<>|]')
BODY_START_RE = re.compile(
    r"^(?:△|【|（|#{1,3}\s+|\d+\s*[-－]\s*\d+|第[一二三四五六七八九十\d]+\s*场|"
    r"\*\*[^*：:]{1,20}\*\*(?:（[^）]+）)?[：:])"
)


def chinese_number(n: int) -> str:
    digits = "零一二三四五六七八九"
    if n < 10:
        return digits[n]
    if n == 10:
        return "十"
    if n < 20:
        return "十" + digits[n % 10]
    if n < 100:
        tens, ones = divmod(n, 10)
        return digits[tens] + "十" + (digits[ones] if ones else "")
    return str(n)


def episode_stem(n: int) -> str:
    return f"ep{n:03d}"


def parse_state(project_dir: Path) -> dict:
    state_path = project_dir / ".drama-state.json"
    if not state_path.exists():
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[错误] state JSON 解析失败: {state_path} ({exc})")


def completed_episode_numbers(state: dict, project_dir: Path) -> list[int]:
    completed = state.get("completedEpisodes")
    if isinstance(completed, list):
        nums = []
        for item in completed:
            m = re.search(r"\d+", str(item))
            if m:
                nums.append(int(m.group(0)))
        if nums:
            return sorted(set(nums))
    if isinstance(completed, int) and completed > 0:
        return list(range(1, completed + 1))

    episodes_dir = project_dir / "episodes"
    nums = []
    for path in episodes_dir.glob("ep*.md"):
        m = re.match(r"ep0*(\d+)", path.stem)
        if m:
            nums.append(int(m.group(1)))
    return sorted(set(nums))


def parse_range(expr: str | None, available: Iterable[int]) -> list[int]:
    available_nums = sorted(set(available))
    if not expr or expr in {"all", "全部", "全剧"}:
        return available_nums

    s = expr.strip()
    m = re.fullmatch(r"前\s*(\d+)\s*集?", s)
    if m:
        end = int(m.group(1))
        return list(range(1, end + 1))

    m = re.fullmatch(r"(\d+)\s*[-~—–]\s*(\d+)", s)
    if m:
        start, end = int(m.group(1)), int(m.group(2))
        if start > end:
            raise SystemExit(f"[错误] 集数范围必须升序: {expr}")
        return list(range(start, end + 1))

    if re.fullmatch(r"\d+(?:\s*[,，]\s*\d+)*", s):
        return sorted({int(part) for part in re.split(r"\s*[,，]\s*", s)})

    if re.fullmatch(r"\d+", s):
        return [int(s)]

    raise SystemExit(f"[错误] 无法解析导出范围: {expr}")


def parse_episode_file_map(project_dir: Path, value: str | None) -> dict[int, Path]:
    if not value:
        return {}
    mapping: dict[int, Path] = {}
    for item in re.split(r"\s*[,，]\s*", value.strip()):
        if not item:
            continue
        if "=" not in item:
            raise SystemExit(f"[错误] --episode-file-map 格式错误: {item}，应为 1=文件名.md")
        key, raw_path = item.split("=", 1)
        key = key.strip()
        if not key.isdigit():
            raise SystemExit(f"[错误] --episode-file-map 集数必须是数字: {key}")
        path = Path(raw_path.strip()).expanduser()
        if not path.is_absolute():
            path = project_dir / "episodes" / path
        if path.suffix.lower() != ".md":
            raise SystemExit(f"[错误] 剧集映射文件必须是 .md: {path}")
        mapping[int(key)] = path
    return mapping


def validate_episode_files(project_dir: Path, episodes: list[int], overrides: dict[int, Path] | None = None) -> dict[int, Path]:
    overrides = overrides or {}
    paths = {
        n: overrides.get(n, project_dir / "episodes" / f"{episode_stem(n)}.md")
        for n in episodes
    }
    missing = [n for n, path in paths.items() if not path.exists()]
    if missing:
        raise SystemExit(episode_missing_message(project_dir, missing))
    return paths


def episode_candidate_files(project_dir: Path, episode_num: int) -> list[Path]:
    episodes_dir = project_dir / "episodes"
    if not episodes_dir.exists():
        return []
    padded = f"{episode_num:03d}"
    unpadded = str(episode_num)
    chinese = chinese_number(episode_num)
    patterns = [
        rf"ep0*{episode_num}(?:\D|$)",
        rf"第\s*{episode_num}\s*集",
        rf"第\s*{chinese}\s*集",
        rf"(?:^|\D){padded}(?:\D|$)",
    ]
    candidates = []
    for path in sorted(episodes_dir.glob("*.md")):
        name = path.stem
        if path.name == f"{episode_stem(episode_num)}.md":
            continue
        if any(re.search(pattern, name, re.IGNORECASE) for pattern in patterns):
            candidates.append(path)
            continue
        # Last-resort match for simple names like "1.md"; avoid matching any digit inside long titles.
        if name == unpadded:
            candidates.append(path)
    return candidates


def episode_missing_message(project_dir: Path, missing: list[int]) -> str:
    lines = ["[需要确认集数文件]"]
    lines.append("导出范围内缺少标准命名的剧集文件：")
    for n in missing:
        lines.append(f"- episodes/{episode_stem(n)}.md")
    lines.append("")

    any_candidates = False
    for n in missing:
        candidates = episode_candidate_files(project_dir, n)
        if not candidates:
            continue
        any_candidates = True
        lines.append(f"可能是第 {n} 集的改名文件：")
        for idx, path in enumerate(candidates[:5], 1):
            lines.append(f"{idx}. {path.name}")
        if len(candidates) > 5:
            lines.append(f"... 另有 {len(candidates) - 5} 个候选")
        lines.append("")

    if any_candidates:
        lines.extend([
            "请先确认如何处理，避免导错版本：",
            "A. 把候选文件重命名为标准文件名（例如 ep001.md）后重跑导出",
            "B. 明确告诉我要使用哪个候选文件作为对应集数（一次性本次导出，不改名；脚本会用 --episode-file-map 重跑）",
            "C. 取消导出，先整理 episodes/ 目录",
        ])
    else:
        lines.extend([
            "未找到明显候选文件。",
            "请先补齐对应集数剧本，或把已改名文件放回 episodes/ 并改为标准命名（例如 ep001.md）后重跑导出。",
        ])
    return "\n".join(lines)


def strip_episode_text(text: str, with_bible_ref: bool = False) -> str:
    if with_bible_ref:
        return CONTINUITY_RE.sub("", text).strip()
    if BODY_MARKER in text:
        text = text.split(BODY_MARKER, 1)[0]
    return CONTINUITY_RE.sub("", text).strip()


def clean_internal_front_matter(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    skipping = False
    for raw in lines:
        stripped = raw.strip()
        label = stripped.replace("*", "").rstrip("：:")
        if label.startswith("分集定位") or label.startswith("本集骨架"):
            skipping = True
            continue
        if skipping:
            if stripped == "---":
                skipping = False
                continue
            if not stripped:
                continue
            if BODY_START_RE.match(stripped):
                skipping = False
            elif stripped.startswith(("-", "+")) or re.match(r"^\*\s+", stripped):
                continue
            else:
                skipping = False
        out.append(raw)
    return "\n".join(out).strip()


def read_episode_body(path: Path, with_bible_ref: bool = False) -> str:
    text = path.read_text(encoding="utf-8")
    return clean_internal_front_matter(strip_episode_text(text, with_bible_ref))


def extract_episode_summaries(project_dir: Path, episodes: list[int]) -> dict[int, str]:
    directory = project_dir / "episode-directory.md"
    if not directory.exists():
        return {}
    content = directory.read_text(encoding="utf-8")
    wanted = set(episodes)
    summaries: dict[int, str] = {}
    pattern = re.compile(r"^第(\d+)集[：:]\s*(.+)$", re.MULTILINE)
    for match in pattern.finditer(content):
        num = int(match.group(1))
        if num not in wanted:
            continue
        text = match.group(2).strip()
        text = re.sub(r"\s*\[[^\]]+\]", "", text).strip()
        summaries[num] = f"第{chinese_number(num)}集{text}"
    return summaries


def range_label(episodes: list[int]) -> str:
    if not episodes:
        return "空范围"
    if len(episodes) == 1:
        return f"第 {episodes[0]} 集"
    if episodes == list(range(episodes[0], episodes[-1] + 1)):
        return f"第 {episodes[0]}-{episodes[-1]} 集"
    return "第 " + ",".join(str(n) for n in episodes) + " 集"


def clean_title(value: object) -> str:
    return str(value or "").strip()


def title_mismatch_warnings(project_dir: Path, state: dict) -> list[str]:
    warnings: list[str] = []
    dir_name = project_dir.name
    project_name = clean_title(state.get("projectName"))
    drama_title = clean_title(state.get("dramaTitle"))
    if project_name and project_name != dir_name:
        warnings.append(f"projectName 与目录名不一致: projectName={project_name} / dir={dir_name}")
    if drama_title and project_name and drama_title != project_name:
        warnings.append(f"dramaTitle 与 projectName 不一致: dramaTitle={drama_title} / projectName={project_name}")
    if drama_title and not project_name and drama_title != dir_name:
        warnings.append(f"dramaTitle 与目录名不一致: dramaTitle={drama_title} / dir={dir_name}")
    return warnings


def title_choice_message(project_dir: Path, state: dict) -> str:
    dir_name = project_dir.name
    project_name = clean_title(state.get("projectName")) or "[空]"
    drama_title = clean_title(state.get("dramaTitle")) or "[空]"
    return f"""[需要确认导出名]
检测到项目名称不一致：
- dramaTitle：{drama_title}
- projectName：{project_name}
- 目录名：{dir_name}

请先选择本次导出文件名，避免生成错误命名的 docx：
A. 使用 dramaTitle：{drama_title}
B. 使用 projectName：{project_name}
C. 使用目录名：{dir_name}
D. 手动输入一个新的导出名
E. 同步修正 .drama-state.json 的 dramaTitle/projectName 后再导出（需要明确授权，会修改 state）

如果只是本次导出改名，请回复 A/B/C/D；选择后将用 --title 重跑，不修改项目 state。"""


def resolve_title(project_dir: Path, state: dict, explicit_title: str | None = None) -> tuple[str, list[str]]:
    project_name = clean_title(state.get("projectName"))
    drama_title = clean_title(state.get("dramaTitle"))
    explicit = clean_title(explicit_title)
    warnings = title_mismatch_warnings(project_dir, state)
    dir_name = project_dir.name

    if explicit:
        title = explicit
    else:
        if warnings:
            raise SystemExit(title_choice_message(project_dir, state))
        title = drama_title or project_name or project_dir.name

    if explicit and explicit != (drama_title or project_name or dir_name):
        warnings.append(f"使用 --title 覆盖导出名: {explicit}")

    if not title:
        raise SystemExit("[错误] 无法确定导出名，请传 --title")
    if INVALID_FILENAME_CHARS_RE.search(title):
        raise SystemExit(f"[错误] 导出名含非法文件名字符: {title}")
    if title in {".", ".."}:
        raise SystemExit(f"[错误] 导出名非法: {title}")
    return title, warnings


def output_basename(
    project_dir: Path,
    episodes: list[int],
    state: dict,
    explicit_title: str | None = None,
    full_export: bool = False,
) -> tuple[str, list[str]]:
    title, warnings = resolve_title(project_dir, state, explicit_title)
    if full_export:
        return f"{title}-完整剧本", warnings
    if len(episodes) == 1:
        return f"{title}-{episode_stem(episodes[0])}", warnings
    if episodes == list(range(episodes[0], episodes[-1] + 1)):
        return f"{title}-{episode_stem(episodes[0])}-{episode_stem(episodes[-1])}", warnings
    return f"{title}-episodes", warnings


def parse_include(profile: str, include: str | None) -> list[int]:
    if profile == "custom":
        if not include:
            raise SystemExit("[错误] custom profile 需要 --include，例如 --include 1+3+5")
        parts = re.split(r"\s*[+,，]\s*", include.strip())
        blocks = []
        for part in parts:
            if not part:
                continue
            if not part.isdigit():
                raise SystemExit(f"[错误] 内容块编号必须是数字: {part}")
            blocks.append(int(part))
    else:
        blocks = PROFILE_BLOCKS[profile]
    invalid = [b for b in blocks if b not in BLOCK_NAMES]
    if invalid:
        raise SystemExit(f"[错误] 未知内容块编号: {invalid}")
    if 5 not in blocks:
        raise SystemExit("[错误] 正文/分集是必选内容块 5")
    return blocks


def read_optional_file(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).expanduser().read_text(encoding="utf-8").strip()


def build_markdown(args, project_dir: Path, state: dict, episodes: list[int], file_overrides: dict[int, Path]) -> tuple[str, list[str]]:
    blocks = parse_include(args.profile, args.include)
    missing: list[str] = []

    synopsis = read_optional_file(args.synopsis_file)
    if 1 in blocks and not synopsis:
        cache = project_dir / ".drama-state" / "synopsis-cache.md"
        if cache.exists():
            synopsis = cache.read_text(encoding="utf-8").strip()
    if 1 in blocks and not synopsis:
        missing.append("1:剧情介绍")

    plot_arc = read_optional_file(args.plot_arc_file)
    if 2 in blocks and not plot_arc:
        summaries = extract_episode_summaries(project_dir, episodes)
        if summaries:
            plot_arc = "\n\n".join(summaries[n] for n in episodes if n in summaries)
    if 2 in blocks and not plot_arc:
        missing.append("2:剧情脉络")

    characters = read_optional_file(args.characters_file)
    if 3 in blocks and not characters:
        missing.append("3:人物介绍")

    episode_summaries = read_optional_file(args.episode_summaries_file)
    if 4 in blocks and not episode_summaries:
        summaries = extract_episode_summaries(project_dir, episodes)
        if summaries:
            episode_summaries = "\n\n".join(summaries[n] for n in episodes if n in summaries)
    if 4 in blocks and not episode_summaries:
        missing.append("4:分集梗概")

    if missing and not args.allow_missing:
        raise SystemExit("[缺少内容块] " + "；".join(missing))

    episode_paths = validate_episode_files(project_dir, episodes, file_overrides)
    bodies = [read_episode_body(episode_paths[n], args.with_bible_ref) for n in episodes]

    sections: list[tuple[str, str]] = []
    if 1 in blocks and synopsis:
        sections.append(("剧情介绍", synopsis))
    if 2 in blocks and plot_arc:
        sections.append(("剧情脉络", plot_arc))
    if 3 in blocks and characters:
        sections.append(("人物介绍", characters))
    if 4 in blocks and episode_summaries:
        sections.append(("分集梗概", episode_summaries))
    sections.append(("正文", "\n\n".join(bodies)))

    md_parts = [f"## {title}\n\n{body.strip()}" for title, body in sections if body.strip()]
    return "\n\n".join(md_parts).strip() + "\n", missing


def make_plan(
    project_dir: Path,
    state: dict,
    episodes: list[int],
    profile: str,
    include: str | None,
    title: str | None,
    full_export: bool = False,
) -> dict:
    basename, warnings = output_basename(project_dir, episodes, state, title, full_export)
    resolved_title, _ = resolve_title(project_dir, state, title)
    export_dir = project_dir / "export"
    blocks = parse_include(profile, include)
    return {
        "projectDir": str(project_dir),
        "title": resolved_title,
        "range": range_label(episodes),
        "episodes": episodes,
        "blocks": [{"id": b, "name": BLOCK_NAMES[b]} for b in blocks],
        "tempMarkdown": str(export_dir / f".tmp-{episode_stem(episodes[0])}-{episode_stem(episodes[-1])}-prepared.md"),
        "docx": str(export_dir / f"{basename}.docx"),
        "warnings": warnings,
        "menu": MENU_TEXT.format(scope=range_label(episodes)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare short-drama export markdown")
    parser.add_argument("--project-dir", required=True, help="短剧项目目录")
    parser.add_argument("--range", default=None, help="导出范围，如 前10集 / 1-10 / 5,8,12")
    parser.add_argument("--profile", choices=["standard", "preview", "body", "custom"], default="body")
    parser.add_argument("--include", default=None, help="custom profile 内容块，如 1+3+5")
    parser.add_argument("--menu", action="store_true", help="只输出固定选择菜单")
    parser.add_argument("--plan", action="store_true", help="输出 JSON 导出计划，不写文件")
    parser.add_argument("--json", action="store_true", help="构建后输出 JSON 摘要")
    parser.add_argument("--output-md", default=None, help="输出 markdown 路径")
    parser.add_argument("--full", action="store_true", help="按完整剧本命名输出，如 剧名-完整剧本.docx")
    parser.add_argument("--title", default=None, help="显式导出名/剧名，覆盖 state 中的 dramaTitle/projectName")
    parser.add_argument("--synopsis-file", default=None, help="剧情介绍 markdown 文件")
    parser.add_argument("--plot-arc-file", default=None, help="剧情脉络 markdown 文件")
    parser.add_argument("--characters-file", default=None, help="人物介绍 markdown 文件")
    parser.add_argument("--episode-summaries-file", default=None, help="分集梗概 markdown 文件")
    parser.add_argument("--with-bible-ref", action="store_true", help="保留考据附录但删除 CONTINUITY")
    parser.add_argument("--allow-missing", action="store_true", help="允许跳过缺失的可选语义块")
    parser.add_argument(
        "--episode-file-map",
        default=None,
        help="一次性剧集文件映射，如 '1=第1集-新版.md,2=/abs/ep2.md'；不修改文件名",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    state = parse_state(project_dir)
    episodes = parse_range(args.range, completed_episode_numbers(state, project_dir))
    if not episodes:
        raise SystemExit("[错误] 没有可导出的集数")
    file_overrides = parse_episode_file_map(project_dir, args.episode_file_map)
    full_export = args.full or args.range is None or str(args.range).strip() in {"all", "全部", "全剧"}

    if args.menu:
        print(MENU_TEXT.format(scope=range_label(episodes)))
        return 0

    validate_episode_files(project_dir, episodes, file_overrides)

    if args.plan:
        print(json.dumps(
            make_plan(project_dir, state, episodes, args.profile, args.include, args.title, full_export),
            ensure_ascii=False,
            indent=2,
        ))
        return 0

    markdown, missing = build_markdown(args, project_dir, state, episodes, file_overrides)
    basename, warnings = output_basename(project_dir, episodes, state, args.title, full_export)
    default_output = project_dir / "export" / f".tmp-{episode_stem(episodes[0])}-{episode_stem(episodes[-1])}-prepared.md"
    output_path = Path(args.output_md).expanduser() if args.output_md else default_output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    summary = {
        "ok": True,
        "range": range_label(episodes),
        "episodes": episodes,
        "markdown": str(output_path),
        "docx": str(project_dir / "export" / f"{basename}.docx"),
        "missing": missing,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"[完成] 导出 Markdown 已准备: {output_path}")
        print(f"[范围] {summary['range']}")
        for warning in warnings:
            print(f"[warn] {warning}")
        print(f"[建议 DOCX] {summary['docx']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
