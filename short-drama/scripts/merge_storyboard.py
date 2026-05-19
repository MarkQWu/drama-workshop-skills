#!/usr/bin/env python3
"""
合并分镜表 + 提取纯 prompt 列表

用法:
    python scripts/merge_storyboard.py --episodes 1-10
    python scripts/merge_storyboard.py --episodes 3,5,7
    python scripts/merge_storyboard.py --all
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


def parse_episode_range(spec: str) -> list[int]:
    """解析集数参数：'1-10' 或 '3,5,7' 或 'all'"""
    episodes = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            episodes.extend(range(int(start), int(end) + 1))
        else:
            episodes.append(int(part))
    return sorted(set(episodes))


def find_storyboard_files(storyboards_dir: Path, episodes: Optional[list[int]]) -> list[Path]:
    """查找分镜文件，按集数排序"""
    if episodes is None:  # --all
        files = sorted(storyboards_dir.glob("ep*-storyboard.md"))
    else:
        files = []
        for ep in episodes:
            pattern = f"ep{ep:03d}-storyboard.md"
            path = storyboards_dir / pattern
            if path.exists():
                files.append(path)
            else:
                print(f"⚠ 未找到: {pattern}", file=sys.stderr)
    return files


def extract_prompts(content: str) -> list[str]:
    """从分镜表中提取即梦 Prompt 列"""
    prompts = []
    in_prompt_section = False

    for line in content.splitlines():
        # 方式一：从 Prompt 汇总区提取
        if re.match(r"^##\s+Prompt\s+汇总", line):
            in_prompt_section = True
            continue
        if in_prompt_section:
            if line.startswith("### 镜头"):
                continue
            if line.startswith("## ") or line.startswith("# "):
                in_prompt_section = False
                continue
            stripped = line.strip()
            if stripped and not stripped.startswith(">"):
                prompts.append(stripped)
                continue

        # 方式二：从表格最后一列提取（即梦 Prompt 列）
        if line.strip().startswith("|") and "即梦" not in line and "镜号" not in line and "---" not in line:
            cells = [c.strip() for c in line.split("|")]
            # 表格有 9 列（含首尾空），最后一个非空是 prompt
            non_empty = [c for c in cells if c]
            if len(non_empty) >= 7:
                prompt = non_empty[-1]
                if prompt and prompt != "—" and len(prompt) > 10:
                    prompts.append(prompt)

    return prompts


def merge(files: list[Path], output_dir: Path) -> None:
    """合并分镜文件 + 提取 prompt"""
    merged_lines = ["# 合并分镜表\n"]
    all_prompts = []
    total_shots = 0

    for f in files:
        content = f.read_text(encoding="utf-8")
        merged_lines.append(f"\n---\n\n")
        merged_lines.append(content)

        # 统计镜头数（表格行，排除表头和分隔行）
        for line in content.splitlines():
            if line.strip().startswith("|") and "镜号" not in line and "---" not in line and "景别" not in line:
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if cells and cells[0].isdigit():
                    total_shots += 1

        # 提取 prompt
        prompts = extract_prompts(content)
        if prompts:
            ep_match = re.search(r"ep(\d+)", f.name)
            ep_label = f"第{int(ep_match.group(1))}集" if ep_match else f.stem
            all_prompts.append(f"\n## {ep_label}\n")
            for i, p in enumerate(prompts, 1):
                all_prompts.append(f"{i}. {p}\n")

    # 写合并文件
    merged_path = output_dir / "merged-storyboard.md"
    merged_path.write_text("".join(merged_lines), encoding="utf-8")
    print(f"✅ 合并完成: {merged_path}")
    print(f"   文件数: {len(files)}")
    print(f"   总镜头数: {total_shots}")

    # 写纯 prompt 文件
    if all_prompts:
        prompts_path = output_dir / "prompts-only.txt"
        prompts_path.write_text("".join(all_prompts), encoding="utf-8")
        prompt_count = sum(1 for line in all_prompts if line[0].isdigit())
        print(f"✅ Prompt 提取: {prompts_path} ({prompt_count} 条)")
    else:
        print("⚠ 未提取到任何 prompt")


def main():
    parser = argparse.ArgumentParser(description="合并分镜表 + 提取 prompt")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--episodes", type=str, help="集数范围，如 1-10 或 3,5,7")
    group.add_argument("--all", action="store_true", help="合并所有分镜文件")
    parser.add_argument("--dir", type=str, default=".", help="项目目录（默认当前目录）")

    args = parser.parse_args()
    project_dir = Path(args.dir)
    storyboards_dir = project_dir / "storyboards"

    if not storyboards_dir.exists():
        print(f"❌ 分镜目录不存在: {storyboards_dir}", file=sys.stderr)
        sys.exit(1)

    episodes = None if args.all else parse_episode_range(args.episodes)
    files = find_storyboard_files(storyboards_dir, episodes)

    if not files:
        print("❌ 未找到任何分镜文件", file=sys.stderr)
        sys.exit(1)

    merge(files, storyboards_dir)


if __name__ == "__main__":
    main()
