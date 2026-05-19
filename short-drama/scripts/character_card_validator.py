#!/usr/bin/env python3
"""
角色卡格式校验工具

用法:
    python scripts/character_card_validator.py
    python scripts/character_card_validator.py --dir /path/to/project
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


REQUIRED_SECTIONS = ["基础外观", "Prompt 前缀"]
OPTIONAL_SECTIONS = ["服装方案", "参考图路径", "来源"]
PROMPT_MIN_WORDS = 15
PROMPT_MAX_WORDS = 40


def count_chinese_words(text: str) -> int:
    """粗略计算中文文本词数（中文字符 + 英文单词）"""
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    english_words = len(re.findall(r"[a-zA-Z]+", text))
    return chinese_chars + english_words


def validate_card(path: Path, characters_names: Optional[set[str]]) -> list[str]:
    """校验单个角色卡，返回问题列表"""
    issues = []
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # 提取角色名（从标题或文件名）
    card_name = None
    for line in lines:
        m = re.match(r"#\s+角色视觉卡[：:]\s*(.+)", line)
        if m:
            card_name = m.group(1).strip()
            break
    if not card_name:
        card_name = path.stem
        issues.append(f"⚠ 缺少标题行（# 角色视觉卡：{{角色名}}）")

    # 检查必填 section
    for section in REQUIRED_SECTIONS:
        if f"## {section}" not in content:
            issues.append(f"❌ 缺少必填 section: {section}")

    # 检查 Prompt 前缀长度
    prompt_match = re.search(
        r"## Prompt 前缀.*?\n(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    if prompt_match:
        prompt_text = prompt_match.group(1).strip()
        # 去掉示例标记行
        prompt_lines = [
            l for l in prompt_text.splitlines()
            if l.strip() and not l.strip().startswith("示例") and not l.strip().startswith("{")
        ]
        if prompt_lines:
            actual_prompt = prompt_lines[0]
            word_count = count_chinese_words(actual_prompt)
            if word_count < PROMPT_MIN_WORDS:
                issues.append(
                    f"⚠ Prompt 前缀过短（{word_count} 词，建议 ≥{PROMPT_MIN_WORDS}）"
                )
            elif word_count > PROMPT_MAX_WORDS:
                issues.append(
                    f"⚠ Prompt 前缀过长（{word_count} 词，建议 ≤{PROMPT_MAX_WORDS}）"
                )
        else:
            issues.append("❌ Prompt 前缀 section 为空")

    # 检查角色名与 characters.md 一致性
    if characters_names and card_name and card_name not in characters_names:
        issues.append(
            f"⚠ 角色名「{card_name}」未在 characters.md 中找到"
        )

    return issues


def load_character_names(project_dir: Path) -> Optional[set[str]]:
    """从 characters.md 提取角色名列表"""
    chars_file = project_dir / "characters.md"
    if not chars_file.exists():
        return None

    names = set()
    content = chars_file.read_text(encoding="utf-8")
    # 匹配 "姓名：XXX" 或 "**姓名：** XXX" 格式
    for m in re.finditer(r"姓名[：:]\s*\**\s*(.+?)[\s\*]", content):
        names.add(m.group(1).strip())
    # 匹配 "## XXX" 角色标题格式
    for m in re.finditer(r"^##\s+(.+?)(?:\s*[（(]|$)", content, re.MULTILINE):
        name = m.group(1).strip()
        if len(name) <= 6:  # 角色名一般不超过 6 字
            names.add(name)
    return names if names else None


def main():
    parser = argparse.ArgumentParser(description="角色卡格式校验")
    parser.add_argument("--dir", type=str, default=".", help="项目目录（默认当前目录）")
    args = parser.parse_args()

    project_dir = Path(args.dir)
    cards_dir = project_dir / "character-cards"

    if not cards_dir.exists():
        print(f"❌ 角色卡目录不存在: {cards_dir}", file=sys.stderr)
        sys.exit(1)

    card_files = sorted(cards_dir.glob("*.md"))
    if not card_files:
        print("❌ 未找到任何角色卡文件", file=sys.stderr)
        sys.exit(1)

    character_names = load_character_names(project_dir)

    print("=" * 50)
    print("📋 角色卡校验报告")
    print("=" * 50)

    total_issues = 0
    for card_path in card_files:
        issues = validate_card(card_path, character_names)
        status = "✅" if not issues else "⚠"
        print(f"\n{status} {card_path.name}")
        if issues:
            for issue in issues:
                print(f"   {issue}")
            total_issues += len(issues)

    print(f"\n{'=' * 50}")
    print(f"共检查 {len(card_files)} 张角色卡，发现 {total_issues} 个问题")
    if total_issues == 0:
        print("🎉 全部通过！")
    print("=" * 50)

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
