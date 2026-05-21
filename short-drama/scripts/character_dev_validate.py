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

VOICE_ACTION_ANCHORS = [
    "笔尖",
    "摘眼镜",
    "眼镜",
    "整理",
    "卷宗",
    "文件",
    "手套",
    "茶杯",
    "手在抖",
    "微笑",
    "红茶",
    "滚水",
]

VOICE_EXPOSITION_PATTERNS = [
    r"十一年前.*(我|卷宗|案子)",
    r"当年.*(我|你|他|她)",
    r"我不是你.*想象",
    r"我沉默.*(时间|错|罪)",
    r"你以为我.*(不知道|不想|没有)",
    r"我为什么.*因为",
    r"没有资格审判",
    r"真相.*刀",
    r"体面.*命",
]

VOICE_SAMPLE_CONTEXT_PATTERNS = [
    r"对[^，:：]{1,20}[，,]?\s*在[^，:：]{1,40}(下|时)[，,]?\s*为了",
    r"对[^，:：]{1,20}[，,]?\s*面对[^，:：]{1,40}[，,]?\s*为了",
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


def extract_field_block(block: str, field: str) -> str:
    pattern = field_pattern(field)
    match = pattern.search(block)
    if not match:
        return ""
    next_field = re.search(r"\n-\s+\*\*[^*\n]+?\*\*", block[match.end() :])
    end = match.end() + next_field.start() if next_field else len(block)
    return block[match.start() : end]


def quoted_texts(text: str) -> list[str]:
    return re.findall(r"[\"“](.+?)[\"”]", text)


def visible_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def voice_sample_texts(voice: str) -> list[str]:
    quoted = quoted_texts(voice)
    if quoted:
        return quoted

    samples: list[str] = []
    for line in voice.splitlines():
        if not re.search(r"公开场合|私下|真实身份|情绪爆发", line):
            continue
        parts = re.split(r"[：:]", line, maxsplit=1)
        if len(parts) == 2:
            samples.append(parts[1].strip())
    return samples


def validate_voice_quality(content: str, roles: list[str]) -> list[str]:
    warnings: list[str] = []
    for role in roles:
        block = extract_role_block(content, role)
        if not block:
            continue
        voice = extract_field_block(block, "声音指纹 + voice 样本集")
        if not voice:
            continue

        emotional_line = ""
        for line in voice.splitlines():
            if "情绪失控语言" in line:
                emotional_line = line
                break
        for anchor in VOICE_ACTION_ANCHORS:
            if anchor in emotional_line:
                warnings.append(f"{role}: 情绪失控语言疑似混入动作/作者修辞锚点「{anchor}」")
                break

        samples = voice_sample_texts(voice)
        for sample in samples:
            if visible_len(sample) > 70:
                warnings.append(f"{role}: voice 样本过长，疑似角色自白或设定说明: {sample[:30]}...")
                break

        if samples:
            for pattern in VOICE_EXPOSITION_PATTERNS:
                if any(re.search(pattern, sample) for sample in samples):
                    warnings.append(f"{role}: voice 样本疑似直接讲前史/动机/主题宣言")
                    break

        sample_lines = [
            line
            for line in voice.splitlines()
            if re.match(r"\s*-\s+(公开场合|真实身份\s*/\s*私下|私下场合|情绪爆发)", line)
        ]
        if sample_lines and not all(
            any(re.search(pattern, line) for pattern in VOICE_SAMPLE_CONTEXT_PATTERNS)
            for line in sample_lines
        ):
            warnings.append(f"{role}: voice 样本未显式标注对象/压力/真实意图，后续分集可执行性偏弱")

        if "禁用" in voice and not re.search(r"触发情境|替代路径|豁免条件", voice):
            warnings.append(f"{role}: 禁用项仍是纯禁止结构，建议改为 触发情境/禁用误写/替代路径/豁免条件")
    return warnings


def warning_summary(warnings: list[str], limit: int = 8) -> str:
    if not warnings:
        return ""
    shown = warnings[:limit]
    text = "\n".join(f"- {item}" for item in shown)
    if len(warnings) > limit:
        text += f"\n- ... 另有 {len(warnings) - limit} 条"
    return "[声纹质量提醒]\n" + text


def validate_batch(args: argparse.Namespace) -> dict:
    content = read_text(Path(args.file))
    roles = load_roles(args)
    errors: list[str] = []
    warnings: list[str] = []
    if not roles:
        errors.append("未提供 roles；用 --roles A,B 或 --role-plan path")
    errors.extend(validate_roles(content, roles, BATCH_REQUIRED_FIELDS))
    warnings.extend(validate_voice_quality(content, roles))
    return {
        "mode": "batch",
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "warningSummary": warning_summary(warnings),
        "roles": roles,
    }


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
    warnings.extend(validate_voice_quality(content, roles))

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
        "warningSummary": warning_summary(warnings),
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
