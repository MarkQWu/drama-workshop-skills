#!/usr/bin/env python3
"""prepare_export.py test suite."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPT = SCRIPT_DIR / "prepare_export.py"

passed = 0
failed = 0
errors = []


def assert_true(condition, name, detail=""):
    global passed, failed, errors
    if condition:
        passed += 1
        print(f"  ✓ {name}")
    else:
        failed += 1
        msg = f"  ✗ {name}" + (f" — {detail}" if detail else "")
        print(msg)
        errors.append(msg)


def run_cmd(args, expect=0):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )
    assert_true(result.returncode == expect, f"exit code 为 {expect}", f"实际: {result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


def make_project(root: Path) -> Path:
    project = root / "测试项目"
    (project / "episodes").mkdir(parents=True)
    (project / "export").mkdir()
    (project / ".drama-state.json").write_text(json.dumps({
        "projectName": "测试项目",
        "dramaTitle": "测试项目",
        "completedEpisodes": 3,
    }, ensure_ascii=False), encoding="utf-8")
    (project / "episode-directory.md").write_text("""\
# 测试项目：分集目录

第1集：开局：女主醒来，发现自己重回出事前一天 [关键]
第2集：试探：女主开始观察第一个嫌疑人
第3集：反击：女主拿到第一份证据 [付费]
""", encoding="utf-8")
    for i in range(1, 4):
        (project / "episodes" / f"ep{i:03d}.md").write_text(f"""\
# 第{i}集：标题{i}

**分集定位：** 内部定位不应导出

**本集骨架：**

- story job：内部骨架不应导出

---

△ 第{i}集正文第一句。

<!-- CONTINUITY
机器块不应进入默认导出
-->

<!-- 剧本正文到此结束 -->

---

**本集商业账本：** 不应进入默认导出
""", encoding="utf-8")
    return project


def test_menu_and_plan():
    print("\n[TEST] 菜单与计划")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        menu = run_cmd(["--project-dir", str(project), "--range", "前2集", "--menu"]).stdout
        assert_true("标准行业稿" in menu, "菜单含标准行业稿")
        assert_true("分集梗概" in menu, "菜单含分集梗概")
        assert_true("第 1-2 集" in menu, "菜单显示范围")

        plan = run_cmd(["--project-dir", str(project), "--range", "1-2", "--profile", "preview", "--plan"]).stdout
        data = json.loads(plan)
        assert_true(data["episodes"] == [1, 2], "计划解析 1-2")
        assert_true([b["id"] for b in data["blocks"]] == [2, 3, 4, 5], "preview 内容块正确")


def test_body_build_strips_internal_content():
    print("\n[TEST] 纯正文构建与剥离")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        result = run_cmd([
            "--project-dir", str(project),
            "--range", "1-2",
            "--profile", "body",
            "--json",
        ]).stdout
        data = json.loads(result)
        md = Path(data["markdown"])
        text = md.read_text(encoding="utf-8")
        assert_true("第1集正文第一句" in text and "第2集正文第一句" in text, "正文保留")
        assert_true("分集定位" not in text, "分集定位被剥离")
        assert_true("story job" not in text, "本集骨架被剥离")
        assert_true("CONTINUITY" not in text, "CONTINUITY 被剥离")
        assert_true("商业账本" not in text, "附录被剥离")


def test_preview_requires_character_block():
    print("\n[TEST] preview 缺人物介绍时阻断")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        result = run_cmd([
            "--project-dir", str(project),
            "--range", "前2集",
            "--profile", "preview",
        ], expect=1)
        combined = result.stdout + result.stderr
        assert_true("3:人物介绍" in combined, "明确缺人物介绍")


def test_preview_with_character_file_and_summaries():
    print("\n[TEST] preview 使用人物文件与分集摘要")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        char_file = Path(tmp) / "characters-export.md"
        char_file.write_text("宋以安：重生女主，冷静推进复仇。", encoding="utf-8")
        result = run_cmd([
            "--project-dir", str(project),
            "--range", "前2集",
            "--profile", "preview",
            "--characters-file", str(char_file),
            "--json",
        ]).stdout
        data = json.loads(result)
        text = Path(data["markdown"]).read_text(encoding="utf-8")
        assert_true("## 剧情脉络" in text, "含剧情脉络")
        assert_true("## 人物介绍" in text, "含人物介绍")
        assert_true("## 分集梗概" in text, "含分集梗概")
        assert_true("第一集开局" in text, "第 1 集摘要被抽取")
        assert_true("第二集试探" in text, "第 2 集摘要被抽取")


def test_title_mismatch_warning_and_override():
    print("\n[TEST] 名称不一致检测与 --title 覆盖")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        state_path = project / ".drama-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["projectName"] = "旧项目名"
        state["dramaTitle"] = "旧剧名"
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

        plan = run_cmd([
            "--project-dir", str(project),
            "--range", "1",
            "--profile", "body",
            "--title", "新剧名",
            "--plan",
        ]).stdout
        data = json.loads(plan)
        assert_true(data["title"] == "新剧名", "--title 覆盖标题")
        assert_true(data["docx"].endswith("新剧名-ep001.docx"), "docx 使用覆盖名")
        assert_true(any("projectName 与目录名不一致" in w for w in data["warnings"]),
                    "报告 projectName/目录名不一致")
        assert_true(any("dramaTitle 与 projectName 不一致" in w for w in data["warnings"]),
                    "报告 dramaTitle/projectName 不一致")
        assert_true(any("使用 --title 覆盖导出名" in w for w in data["warnings"]),
                    "报告 title 覆盖")


def test_title_mismatch_requires_choice_without_override():
    print("\n[TEST] 名称不一致且无 --title 时输出具体选择要求")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        state_path = project / ".drama-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["projectName"] = "旧项目名"
        state["dramaTitle"] = "旧剧名"
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

        result = run_cmd([
            "--project-dir", str(project),
            "--range", "1",
            "--profile", "body",
            "--plan",
        ], expect=1)
        combined = result.stdout + result.stderr
        assert_true("请先选择本次导出文件名" in combined, "输出具体确认要求")
        assert_true("A. 使用 dramaTitle" in combined, "包含 A 选项")
        assert_true("B. 使用 projectName" in combined, "包含 B 选项")
        assert_true("C. 使用目录名" in combined, "包含 C 选项")
        assert_true("D. 手动输入一个新的导出名" in combined, "包含 D 选项")
        assert_true("E. 同步修正 .drama-state.json" in combined, "包含 E 选项")


def test_invalid_title_blocks():
    print("\n[TEST] 非法导出名阻断")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        result = run_cmd([
            "--project-dir", str(project),
            "--range", "1",
            "--profile", "body",
            "--title", "坏/名字",
            "--plan",
        ], expect=1)
        assert_true("非法文件名字符" in (result.stdout + result.stderr), "非法文件名字符被阻断")


def test_full_export_uses_complete_script_name():
    print("\n[TEST] 完整导出文件名")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        full_plan = run_cmd([
            "--project-dir", str(project),
            "--profile", "body",
            "--plan",
        ]).stdout
        full_data = json.loads(full_plan)
        assert_true(full_data["docx"].endswith("测试项目-完整剧本.docx"), "无范围导出使用完整剧本命名")

        range_plan = run_cmd([
            "--project-dir", str(project),
            "--range", "1-3",
            "--profile", "body",
            "--plan",
        ]).stdout
        range_data = json.loads(range_plan)
        assert_true(range_data["docx"].endswith("测试项目-ep001-ep003.docx"), "范围导出使用集数命名")


def test_menu_outputs_before_file_validation():
    print("\n[TEST] 菜单先于缺集校验")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        (project / "episodes" / "ep001.md").unlink()
        result = run_cmd([
            "--project-dir", str(project),
            "--range", "1",
            "--menu",
        ])
        assert_true("请选择导出方案" in result.stdout, "缺集时仍先输出菜单")


def test_front_matter_without_separator_keeps_body():
    print("\n[TEST] 无分隔线骨架剥离不吞正文")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        (project / "episodes" / "ep001.md").write_text("""\
# 第1集：无分隔线

**分集定位：** 内部定位不应导出

**本集骨架：**

- story job：内部骨架不应导出

△ 第1集正文第一句。
""", encoding="utf-8")
        result = run_cmd([
            "--project-dir", str(project),
            "--range", "1",
            "--profile", "body",
            "--json",
        ]).stdout
        data = json.loads(result)
        text = Path(data["markdown"]).read_text(encoding="utf-8")
        assert_true("第1集正文第一句" in text, "正文保留")
        assert_true("story job" not in text, "内部骨架仍被剥离")


def test_episode_summary_missing_reports_llm_work():
    print("\n[TEST] 缺分集梗概时阻断并交给 LLM")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        (project / "episode-directory.md").unlink()
        result = run_cmd([
            "--project-dir", str(project),
            "--range", "1",
            "--profile", "custom",
            "--include", "4+5",
        ], expect=1)
        combined = result.stdout + result.stderr
        assert_true("4:分集梗概" in combined, "明确缺分集梗概")


def test_custom_include_non_numeric_is_friendly():
    print("\n[TEST] 自定义内容块非数字友好报错")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        result = run_cmd([
            "--project-dir", str(project),
            "--range", "1",
            "--profile", "custom",
            "--include", "abc+5",
            "--plan",
        ], expect=1)
        combined = result.stdout + result.stderr
        assert_true("内容块编号必须是数字" in combined, "输出友好错误")
        assert_true("Traceback" not in combined, "不输出 Python traceback")


def test_renamed_episode_requires_choice_and_map_override():
    print("\n[TEST] 剧集文件改名检测与一次性映射")
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        original = project / "episodes" / "ep001.md"
        renamed = project / "episodes" / "第1集-新版.md"
        original.rename(renamed)

        result = run_cmd([
            "--project-dir", str(project),
            "--range", "1",
            "--profile", "body",
            "--plan",
        ], expect=1)
        combined = result.stdout + result.stderr
        assert_true("需要确认集数文件" in combined, "输出集数文件确认要求")
        assert_true("episodes/ep001.md" in combined, "列出缺失标准文件")
        assert_true("第1集-新版.md" in combined, "列出候选改名文件")
        assert_true("--episode-file-map" in combined, "提示一次性映射参数")

        built = run_cmd([
            "--project-dir", str(project),
            "--range", "1",
            "--profile", "body",
            "--episode-file-map", "1=第1集-新版.md",
            "--json",
        ]).stdout
        data = json.loads(built)
        text = Path(data["markdown"]).read_text(encoding="utf-8")
        assert_true("第1集正文第一句" in text, "一次性映射使用候选文件")


if __name__ == "__main__":
    print("=" * 60)
    print("prepare_export.py 测试套件")
    print("=" * 60)
    tests = [
        test_menu_and_plan,
        test_body_build_strips_internal_content,
        test_preview_requires_character_block,
        test_preview_with_character_file_and_summaries,
        test_title_mismatch_warning_and_override,
        test_title_mismatch_requires_choice_without_override,
        test_invalid_title_blocks,
        test_full_export_uses_complete_script_name,
        test_menu_outputs_before_file_validation,
        test_front_matter_without_separator_keeps_body,
        test_episode_summary_missing_reports_llm_work,
        test_custom_include_non_numeric_is_friendly,
        test_renamed_episode_requires_choice_and_map_override,
    ]
    for test in tests:
        try:
            test()
        except Exception as exc:
            failed += 1
            msg = f"  ✗ {test.__name__} 抛出异常: {exc}"
            print(msg)
            errors.append(msg)
    print("\n" + "=" * 60)
    print(f"结果: {passed} 通过, {failed} 失败, 共 {passed + failed} 项")
    if errors:
        print("\n失败项:")
        for error in errors:
            print(error)
    print("=" * 60)
    raise SystemExit(0 if failed == 0 else 1)
