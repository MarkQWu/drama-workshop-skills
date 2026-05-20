#!/usr/bin/env python3
"""export_docx.py 的测试套件

运行: python3 scripts/test_export_docx.py
依赖: pandoc（已安装）、export_docx.py（同目录）
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EXPORT_SCRIPT = SCRIPT_DIR / "export_docx.py"
SKILL_DIR = SCRIPT_DIR.parent
REF_DOC = SKILL_DIR / "assets" / "drama-reference.docx"

passed = 0
failed = 0
errors = []


def run_export(input_path, output_path, ref_doc=None, expect_exit=0):
    """调用 export_docx.py，返回 (exit_code, stdout, stderr)"""
    cmd = [sys.executable, str(EXPORT_SCRIPT), str(input_path), str(output_path)]
    if ref_doc:
        cmd.append(str(ref_doc))
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def docx_to_text(docx_path):
    """用 pandoc 把 docx 转回纯文本，用于内容验证"""
    result = subprocess.run(
        ["pandoc", str(docx_path), "-t", "plain", "--wrap=none"],
        capture_output=True, text=True,
    )
    return result.stdout


def assert_true(condition, test_name, detail=""):
    global passed, failed, errors
    if condition:
        passed += 1
        print(f"  ✓ {test_name}")
    else:
        failed += 1
        msg = f"  ✗ {test_name}" + (f" — {detail}" if detail else "")
        print(msg)
        errors.append(msg)


# =============================================================
# 测试用例
# =============================================================

def test_normal_export_with_template():
    """正常导出：第三参数（旧 reference-doc）被静默忽略，仍正常生成 docx"""
    print("\n[TEST] 正常导出（有模板）")
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "test.md"
        docx = Path(tmp) / "test.docx"
        md.write_text("# 测试剧本\n\n第一行内容", encoding="utf-8")

        # v1.38.0 起不再使用 reference-doc，第三参数静默忽略
        code, out, err = run_export(md, docx, ref_doc=REF_DOC)
        assert_true(code == 0, "exit code 为 0", f"实际: {code}")
        assert_true(docx.exists(), "docx 文件已生成")
        assert_true("[完成]" in out, "stdout 含 [完成]")


def test_normal_export_without_template():
    """正常导出：不传第三参数，正常生成 docx"""
    print("\n[TEST] 正常导出（无模板）")
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "test.md"
        docx = Path(tmp) / "test.docx"
        md.write_text("# 测试\n\n内容", encoding="utf-8")

        code, out, err = run_export(md, docx, ref_doc="/nonexistent/fake.docx")
        assert_true(code == 0, "exit code 为 0", f"实际: {code}")
        assert_true(docx.exists(), "docx 文件已生成")
        assert_true("[完成]" in out, "stdout 含 [完成]")


def test_input_not_found():
    """输入文件不存在：不生成 docx，stderr 含错误，exit 1"""
    print("\n[TEST] 输入文件不存在")
    with tempfile.TemporaryDirectory() as tmp:
        docx = Path(tmp) / "test.docx"
        code, out, err = run_export("/nonexistent/fake.md", docx)
        assert_true(code == 1, "exit code 为 1", f"实际: {code}")
        assert_true(not docx.exists(), "docx 文件未生成")
        assert_true("[错误]" in err, "stderr 含 [错误]")


def test_insufficient_args():
    """参数不足：输出用法提示，exit 1"""
    print("\n[TEST] 参数不足")
    result = subprocess.run(
        [sys.executable, str(EXPORT_SCRIPT)],
        capture_output=True, text=True,
    )
    assert_true(result.returncode == 1, "exit code 为 1", f"实际: {result.returncode}")
    assert_true("用法" in result.stdout, "stdout 含用法提示")


def test_help_flag():
    """--help：输出用法提示，exit 0"""
    print("\n[TEST] --help")
    result = subprocess.run(
        [sys.executable, str(EXPORT_SCRIPT), "--help"],
        capture_output=True, text=True,
    )
    assert_true(result.returncode == 0, "exit code 为 0", f"实际: {result.returncode}")
    assert_true("用法" in result.stdout, "stdout 含用法提示")


def test_chinese_filename():
    """中文文件名：正常生成"""
    print("\n[TEST] 中文文件名")
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "命运的约定-完整剧本.md"
        docx = Path(tmp) / "命运的约定-完整剧本.docx"
        md.write_text("# 命运的约定\n\n第一集内容", encoding="utf-8")

        code, out, err = run_export(md, docx, ref_doc=REF_DOC)
        assert_true(code == 0, "exit code 为 0", f"实际: {code}")
        assert_true(docx.exists(), "docx 文件已生成")


def test_empty_file():
    """空文件：正常生成（空 docx）"""
    print("\n[TEST] 空文件")
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "empty.md"
        docx = Path(tmp) / "empty.docx"
        md.write_text("", encoding="utf-8")

        code, out, err = run_export(md, docx, ref_doc=REF_DOC)
        assert_true(code == 0, "exit code 为 0", f"实际: {code}")
        assert_true(docx.exists(), "docx 文件已生成")


def test_large_file_50_episodes():
    """大文件：50集剧本，正常生成"""
    print("\n[TEST] 大文件（50集）")
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "large.md"
        docx = Path(tmp) / "large.docx"

        content = "# 测试大剧本\n\n"
        for i in range(1, 51):
            content += f"### 第{i}集：标题{i}\n\n"
            content += f"## {i}-1 日 内 场景A\n\n"
            content += f"**出场人物：** 角色A，角色B\n\n"
            content += f"△ 场景描写第{i}集。\n\n"
            content += f"**角色A**（语气）：这是第{i}集的台词。\n\n"
            content += f"**角色B（OS）**：第{i}集内心独白。\n\n"
            content += "---\n\n"
        md.write_text(content, encoding="utf-8")

        code, out, err = run_export(md, docx, ref_doc=REF_DOC)
        assert_true(code == 0, "exit code 为 0", f"实际: {code}")
        assert_true(docx.exists(), "docx 文件已生成")
        assert_true(docx.stat().st_size > 10000, "docx 文件大小合理", f"实际: {docx.stat().st_size} bytes")


def test_industry_markers_preserved():
    """行业标记保留：OS/VO/闪回/闪出/字幕/音乐/△ 在 docx 中完整存在"""
    print("\n[TEST] 行业标记保留")
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "markers.md"
        docx = Path(tmp) / "markers.docx"

        md.write_text("""\
# 第1集：测试标记

## 1-1 日 内 测试场景

**出场人物：** 角色A，角色B

△ 这是动作描写。

（字幕：九重天，诛仙台）

**角色A**（惊恐）：这是普通台词

**角色A（OS）**：这是内心独白

**角色A（VO）**：这是旁白画外音

【闪回】

△ 回忆画面描写。

【闪出】

[音乐] 紧张悬疑氛围
""", encoding="utf-8")

        code, out, err = run_export(md, docx, ref_doc=REF_DOC)
        assert_true(code == 0, "exit code 为 0", f"实际: {code}")

        text = docx_to_text(docx)
        assert_true("△" in text, "△ 动作标记保留")
        assert_true("（字幕：" in text, "（字幕）标记保留")
        assert_true("（OS）" in text, "OS 内心独白标记保留")
        assert_true("（VO）" in text, "VO 旁白标记保留")
        assert_true("【闪回】" in text, "【闪回】标记保留")
        assert_true("【闪出】" in text, "【闪出】标记保留")
        assert_true("[音乐]" in text, "[音乐] 标记保留")


def test_export_template_structure():
    """导出模板三段式结构：故事梗概+人物小传+正文在 docx 中正确呈现"""
    print("\n[TEST] 导出模板三段式结构")
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "structure.md"
        docx = Path(tmp) / "structure.docx"

        md.write_text("""\
# 命运的约定

## 一、故事梗概

九天玄女因话痨被罚下诛仙台，魂穿林府真千金。她在凡间遇到冷面三哥林邵阳，从互相嫌弃到默契协作，最终识破家族阴谋、找回真爱。

## 二、人物小传

### 林雨欣

林雨欣，20岁。

外貌：明眸皓齿，一头乌黑长发，气质清冷中透着灵动。

身份与关系：林雨欣对外是林府真千金，实际是被罚下凡的九天玄女。与三哥林邵阳从互相嫌弃到默契协作，是并肩识破家族阴谋的战友。

性格：话痨、善良，遇事冷静但嘴上停不下来。

角色发展：从天宫仙女被罚下凡的不服气，到在凡间体察人情世故的成长，最终在面对家族抉择时展现出真正的担当。

### 林邵阳

林邵阳，25岁。

外貌：身形挺拔，眉目冷峻。

身份与关系：林邵阳是林府嫡三子，真实身份是暗中调查家族秘密的守护者。与妹妹林雨欣是异母兄妹，从最初的疏远到后来的守护默契。

性格：外冷内热，寡言少语。

角色发展：对妹妹从最初的疏远警惕，到并肩作战后的守护信任。

## 三、正文

### 第1集：仙女下凡

## 1-1 日 内 九重天

**出场人物：** 林雨欣，天将A

△ 诛仙台上，仙气缭绕。

**林雨欣**（惊恐）：从这跳下去会死仙女的！

---

### 第2集：回府

## 2-1 日 外 林府大门

**出场人物：** 林雨欣，林芊芊

△ 马车停在林府门前。

**林芊芊**（柔弱）：姐姐，你终于回来了。
""", encoding="utf-8")

        code, out, err = run_export(md, docx, ref_doc=REF_DOC)
        assert_true(code == 0, "exit code 为 0", f"实际: {code}")

        text = docx_to_text(docx)

        # 三段式结构验证
        assert_true("命运的约定" in text, "剧名存在")
        assert_true("九天玄女" in text, "故事梗概内容存在")
        assert_true("林雨欣" in text, "人物小传存在")
        assert_true("林邵阳" in text, "人物小传完整")
        assert_true("外冷内热" in text, "角色性格字段存在")
        assert_true("九天玄女" in text, "林雨欣身份与关系段存在")
        assert_true("守护者" in text, "林邵阳身份与关系段存在")
        assert_true("第1集" in text, "第1集存在")
        assert_true("第2集" in text, "第2集存在")

        # 验证顺序：故事梗概 → 人物小传 → 正文
        idx_synopsis = text.find("九天玄女")
        idx_character = text.find("外冷内热")
        idx_ep1 = text.find("仙女下凡")
        assert_true(idx_synopsis < idx_character < idx_ep1,
                    "三段式顺序正确：故事梗概→人物小传→正文",
                    f"位置: synopsis={idx_synopsis}, character={idx_character}, ep1={idx_ep1}")


def test_output_dir_auto_create():
    """输出目录不存在时自动创建"""
    print("\n[TEST] 输出目录自动创建")
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "test.md"
        docx = Path(tmp) / "sub" / "dir" / "test.docx"
        md.write_text("# 测试", encoding="utf-8")

        code, out, err = run_export(md, docx, ref_doc=REF_DOC)
        assert_true(code == 0, "exit code 为 0", f"实际: {code}")
        assert_true(docx.exists(), "docx 文件已生成（嵌套目录）")


# =============================================================
# 运行所有测试
# =============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("export_docx.py 测试套件")
    print("=" * 60)

    tests = [
        test_normal_export_with_template,
        test_normal_export_without_template,
        test_input_not_found,
        test_insufficient_args,
        test_help_flag,
        test_chinese_filename,
        test_empty_file,
        test_large_file_50_episodes,
        test_industry_markers_preserved,
        test_export_template_structure,
        test_output_dir_auto_create,
    ]

    for t in tests:
        try:
            t()
        except Exception as e:
            failed += 1
            msg = f"  ✗ {t.__name__} 抛出异常: {e}"
            print(msg)
            errors.append(msg)

    print("\n" + "=" * 60)
    print(f"结果: {passed} 通过, {failed} 失败, 共 {passed + failed} 项")
    if errors:
        print("\n失败项:")
        for e in errors:
            print(e)
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)
