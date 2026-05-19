#!/usr/bin/env python3
"""短剧剧本 Markdown → Word 导出脚本（跨平台）

用法: python3 scripts/export_docx.py <输入.md> <输出.docx> [reference-doc路径]

功能:
  1. 检测 pandoc 是否安装
  2. 未安装时自动安装（macOS/Windows/Linux）
  3. 调用 pandoc 转换 MD → DOCX
"""

import os
import subprocess
import sys
import shutil
import platform
from pathlib import Path


def detect_os():
    s = platform.system()
    if s == "Darwin":
        return "mac"
    elif s == "Windows":
        return "win"
    else:
        return "linux"


def pandoc_available():
    return shutil.which("pandoc") is not None


def install_pandoc():
    os_type = detect_os()
    print("[检测] pandoc 未安装")
    print("[说明] pandoc 是开源文档转换工具（https://pandoc.org），用于将剧本导出为 Word 格式")
    print("[说明] 仅需安装一次，后续导出直接使用")
    print("")
    print("[安装] 正在自动安装...")

    try:
        if os_type == "mac":
            if shutil.which("brew"):
                print("[安装] brew install pandoc")
                subprocess.run(["brew", "install", "pandoc"], check=True)
            else:
                print("[错误] Homebrew 未安装，无法自动安装 pandoc", file=sys.stderr)
                return False

        elif os_type == "win":
            if shutil.which("winget"):
                print("[安装] winget install pandoc")
                subprocess.run(
                    ["winget", "install", "--id", "JohnMacFarlane.Pandoc", "-e", "--accept-source-agreements"],
                    check=True,
                )
            elif shutil.which("choco"):
                print("[安装] choco install pandoc")
                subprocess.run(["choco", "install", "pandoc", "-y"], check=True)
            elif shutil.which("scoop"):
                print("[安装] scoop install pandoc")
                subprocess.run(["scoop", "install", "pandoc"], check=True)
            else:
                print("[错误] 未找到 winget/choco/scoop，无法自动安装", file=sys.stderr)
                return False

        else:  # linux
            if shutil.which("apt"):
                print("[安装] apt install pandoc")
                subprocess.run(["sudo", "apt", "install", "-y", "pandoc"], check=True)
            elif shutil.which("dnf"):
                print("[安装] dnf install pandoc")
                subprocess.run(["sudo", "dnf", "install", "-y", "pandoc"], check=True)
            else:
                print("[错误] 未找到 apt/dnf，无法自动安装", file=sys.stderr)
                return False

        # 验证安装结果（Windows 安装后 PATH 可能未刷新，尝试常见安装路径）
        if pandoc_available():
            pass
        elif os_type == "win":
            win_paths = [
                Path(os.environ.get("LOCALAPPDATA", ""), "Pandoc"),
                Path("C:/Program Files/Pandoc"),
                Path(os.environ.get("USERPROFILE", ""), "scoop", "shims"),
            ]
            for p in win_paths:
                if (p / "pandoc.exe").exists():
                    os.environ["PATH"] = str(p) + os.pathsep + os.environ.get("PATH", "")
                    break

        if pandoc_available():
            result = subprocess.run(["pandoc", "--version"], capture_output=True, text=True)
            version = result.stdout.split("\n")[0] if result.stdout else "unknown"
            print(f"[成功] pandoc 安装完成: {version}")
            return True
        else:
            print("[错误] 安装命令执行完毕但 pandoc 仍不可用", file=sys.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"[错误] 安装失败: {e}", file=sys.stderr)
        return False


def print_manual_install_help():
    print("[提示] pandoc 自动安装失败，请手动安装后重试")
    print("[Mac]   brew install pandoc")
    print("[Win]   winget install --id JohnMacFarlane.Pandoc -e")
    print("[Linux] sudo apt install -y pandoc")
    print("[备选]  在线转换: https://markdowntoword.io/zh")


def export_docx(input_path, output_path, ref_doc=None):
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        print(f"[错误] 输入文件不存在: {input_path}", file=sys.stderr)
        return False

    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 构建 pandoc 命令
    cmd = ["pandoc", str(input_file), "-o", str(output_file), "--wrap=none"]

    if ref_doc and Path(ref_doc).exists():
        cmd.append(f"--reference-doc={ref_doc}")
        print(f"[样式] 使用模板: {Path(ref_doc).name}")

    try:
        subprocess.run(cmd, check=True)
        print(f"[完成] Word 文件已生成: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[错误] pandoc 转换失败: {e}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) == 2 and sys.argv[1] in {"-h", "--help"}:
        print("用法: python3 export_docx.py <输入.md> <输出.docx> [reference-doc]")
        sys.exit(0)

    if len(sys.argv) < 3:
        print("用法: python3 export_docx.py <输入.md> <输出.docx> [reference-doc]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # reference-doc 默认路径
    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent
    default_ref = skill_dir / "assets" / "drama-reference.docx"
    ref_doc = sys.argv[3] if len(sys.argv) > 3 else str(default_ref)

    # Step 1: 检测 pandoc
    if not pandoc_available():
        # Step 2: 自动安装
        if not install_pandoc():
            print_manual_install_help()
            sys.exit(1)

    # Step 3: 转换
    if not export_docx(input_path, output_path, ref_doc):
        sys.exit(1)


if __name__ == "__main__":
    main()
