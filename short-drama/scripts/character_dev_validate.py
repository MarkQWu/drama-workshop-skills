#!/usr/bin/env python3
"""
/角色开发分片与最终 characters.md 结构验收工具。

用法:
    python3 scripts/character_dev_validate.py batch --file characters.parts/chars-xxx/01-core.md --roles 昭昭,王珩
    python3 scripts/character_dev_validate.py final --file characters.md --role-plan characters.parts/chars-xxx/00-role-plan.json --project-dir .
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROLE_REQUIRED_FIELDS = [
    "姓名",
    "年龄",
    "外貌特征",
    "性格关键词",
    "公开身份",
    "真实身份",
    "核心动机",
    "欲望-恐惧对位",
    "动机形成契机",
    "盲点/弱点",
    "最大冲突点",
    "爽点功能",
    "表面功能 vs 真实功能",
    "声音指纹 + voice 样本集",
    "应激模式",
    "视觉提示词",
]

BATCH_REQUIRED_FIELDS = [
    "姓名",
    "年龄",
    "外貌特征",
    "性格关键词",
    "声音指纹 + voice 样本集",
    "应激模式",
    "视觉提示词",
]

FINAL_REQUIRED_SECTIONS = [
    "主要角色",
    "称呼关系表",
    "角色弧线",
]



def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def load_roles(args: argparse.Namespace) -> list[str]:
    names: list[str] = []
    if getattr(args, "roles", ""):
        names.extend([item.strip() for item in args.roles.split(",") if item.strip()])
    if getattr(args, "role_plan", None):
        data = json.loads(Path(args.role_plan).read_text(encoding="utf-8"))
        role_plan = data.get("rolePlan")
        if role_plan is None and isinstance(data.get("characterDevStatus"), dict):
            role_plan = data["characterDevStatus"].get("rolePlan")
        if role_plan is None:
            role_plan = data

        if isinstance(role_plan, dict):
            roles = role_plan.get("roles", [])
        elif isinstance(role_plan, list):
            roles = role_plan
        else:
            roles = []

        for role in roles:
            if isinstance(role, str):
                name = role.strip()
            elif isinstance(role, dict):
                name = role.get("name", "").strip()
            else:
                name = ""
            if name:
                names.append(name)
    return list(dict.fromkeys(names))


def field_pattern(field: str) -> re.Pattern[str]:
    escaped = re.escape(field).replace("\\ ", r"\s*")
    return re.compile(rf"\*\*{escaped}\*\*\s*[：:：]?", re.IGNORECASE)


def section_heading_pattern(title: str) -> re.Pattern[str]:
    return re.compile(rf"^##+\s*{re.escape(title)}\s*$", re.MULTILINE)


def extract_role_block(content: str, role: str) -> str:
    match = re.search(rf"^###\s*{re.escape(role)}\s*$", content, re.MULTILINE)
    if not match:
        # Some generators use display names in headings and keep canonical name in **姓名**.
        name_match = re.search(
            rf"^###\s*(.+?)\s*$[\s\S]*?\*\*姓名\*\*\s*[：:]\s*{re.escape(role)}(?:\s|$)",
            content,
            re.MULTILINE,
        )
        if not name_match:
            return ""
        match = name_match

    start = match.start()
    next_heading = re.search(r"^###\s+", content[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(content)
    return content[start:end]


def validate_roles(content: str, roles: list[str], required_fields: list[str]) -> list[str]:
    errors: list[str] = []
    for role in roles:
        block = extract_role_block(content, role)
        if not block:
            errors.append(f"缺角色标题: ### {role}")
            continue
        for field in required_fields:
            if not field_pattern(field).search(block):
                errors.append(f"{role}: 缺字段 **{field}**")
        if "声音指纹 + voice 样本集" in required_fields and not re.search(r"禁用", block):
            errors.append(f"{role}: 声音指纹缺 禁用 行")
        if "应激模式" in required_fields and not re.search(r"触发情境|实际反应|豁免条件", block):
            errors.append(f"{role}: 应激模式缺表头或触发/豁免说明")
    return errors


def validate_batch(args: argparse.Namespace) -> dict:
    content = read_text(Path(args.file))
    roles = load_roles(args)
    errors: list[str] = []
    if not roles:
        errors.append("未提供 roles；用 --roles A,B 或 --role-plan path")
    errors.extend(validate_roles(content, roles, BATCH_REQUIRED_FIELDS))
    return {"mode": "batch", "ok": not errors, "errors": errors, "roles": roles}


def has_strong_villain(content: str) -> bool:
    return bool(re.search(r"反派|Boss|对手|压迫者", content, re.IGNORECASE))


def run_command(command: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc.returncode, proc.stdout.strip()


def validate_final(args: argparse.Namespace) -> dict:
    path = Path(args.file)
    content = read_text(path)
    roles = load_roles(args)
    errors: list[str] = []
    warnings: list[str] = []

    if not roles:
        errors.append("未提供 rolePlan/roles，无法校验角色遗漏")

    for section in FINAL_REQUIRED_SECTIONS:
        if not section_heading_pattern(section).search(content):
            errors.append(f"缺关键 section: ## {section}")

    if has_strong_villain(content) and not section_heading_pattern("反派体系").search(content):
        errors.append("强反派题材缺关键 section: ## 反派体系")

    errors.extend(validate_roles(content, roles, ROLE_REQUIRED_FIELDS))
    project_dir = Path(args.project_dir).resolve() if args.project_dir else path.parent.resolve()
    skill_dir = Path(__file__).resolve().parents[1]

    if args.run_consistency:
        checker = skill_dir / "scripts" / "character_consistency_check.py"
        if checker.exists():
            code, output = run_command(
                [sys.executable, str(checker), "--dir", str(project_dir), "--format", "json"],
                project_dir,
            )
            if "未找到剧集文件" in output:
                warnings.append("项目尚无 episodes/*.md，跳过跨集一致性扫描；角色字段解析已由本 validator 覆盖")
            elif code != 0:
                try:
                    json.loads(output)
                    warnings.append("character_consistency_check.py 已运行；现有剧集存在一致性问题，finalize 不因此阻断")
                except json.JSONDecodeError:
                    errors.append(f"character_consistency_check.py 失败: {output[:500]}")
            elif '"characters": []' in output or output.strip() == "[]":
                warnings.append("character_consistency_check.py 未发现跨集问题；角色字段解析已由本 validator 覆盖")
        else:
            warnings.append("未找到 character_consistency_check.py，跳过解析验收")

    if args.run_viz:
        viz = skill_dir / "scripts" / "viz_gen.py"
        if viz.exists():
            code, output = run_command(
                [sys.executable, str(viz), str(path), "--type", "characters"],
                project_dir,
            )
            if code != 0:
                errors.append(f"viz_gen.py 失败: {output[:500]}")
            elif re.search(r"0\s*角色", output):
                errors.append("viz_gen.py 生成结果为空角色卡")
        else:
            warnings.append("未找到 viz_gen.py，跳过可视化验收")

    return {
        "mode": "final",
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "roles": roles,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="/角色开发分片与最终结构验收")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    batch = subparsers.add_parser("batch", help="验收单个角色分片")
    batch.add_argument("--file", required=True)
    batch.add_argument("--roles", default="")
    batch.add_argument("--role-plan")

    final = subparsers.add_parser("final", help="验收最终 characters.md")
    final.add_argument("--file", required=True)
    final.add_argument("--roles", default="")
    final.add_argument("--role-plan")
    final.add_argument("--project-dir")
    final.add_argument("--run-consistency", action="store_true")
    final.add_argument("--run-viz", action="store_true")

    args = parser.parse_args()

    try:
        result = validate_batch(args) if args.mode == "batch" else validate_final(args)
    except Exception as exc:
        result = {"mode": args.mode, "ok": False, "errors": [str(exc)]}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
