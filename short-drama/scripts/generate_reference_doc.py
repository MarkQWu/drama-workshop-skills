#!/usr/bin/env python3
"""生成 pandoc reference-doc 模板，用于短剧剧本 Word 导出。

用法: python3 scripts/generate_reference_doc.py [输出路径]
默认输出: assets/drama-reference.docx
"""

import sys
from pathlib import Path


def create_reference_doc(output_path: str):
    try:
        from docx import Document
        from docx.shared import Pt, Cm
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        print("[错误] 需要 python-docx: pip3 install python-docx", file=sys.stderr)
        sys.exit(1)

    doc = Document()

    # --- 页面设置 (A4) ---
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)

    # --- 样式定义 ---
    # space_before/space_after 单位 Pt；line_spacing 为倍数
    style_config = {
        # Normal：正文基础样式，space_after=6 防止段落视觉粘连
        "Normal": {
            "font": "宋体", "font_en": "Times New Roman",
            "size": 12, "line_spacing": 1.5,
            "space_before": 0, "space_after": 6,
        },
        "Heading 1": {
            "font": "黑体", "font_en": "Arial",
            "size": 22, "bold": True,
            "space_before": 24, "space_after": 12,
        },
        # Heading 2：场景标题（## N-M · 地点 · 日夜）
        "Heading 2": {
            "font": "黑体", "font_en": "Arial",
            "size": 14, "bold": True,
            "space_before": 18, "space_after": 6,
        },
        # Heading 3：集标题（### 第N集：...）
        "Heading 3": {
            "font": "黑体", "font_en": "Arial",
            "size": 16, "bold": True,
            "space_before": 24, "space_after": 8,
        },
        "Title": {
            "font": "黑体", "font_en": "Arial",
            "size": 26, "bold": True,
            "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        },
    }

    for style_name, cfg in style_config.items():
        try:
            style = doc.styles[style_name]
        except KeyError:
            continue

        font = style.font
        font.name = cfg["font_en"]
        font.size = Pt(cfg["size"])
        if cfg.get("bold"):
            font.bold = True

        # 中文字体通过 rFonts 设置
        from docx.oxml.ns import qn
        from lxml import etree
        rPr = style.element.get_or_add_rPr()
        rFonts_elem = rPr.find(qn("w:rFonts"))
        if rFonts_elem is None:
            rFonts_elem = etree.SubElement(rPr, qn("w:rFonts"))
        rFonts_elem.set(qn("w:eastAsia"), cfg["font"])

        pf = style.paragraph_format
        if "line_spacing" in cfg:
            pf.line_spacing = cfg["line_spacing"]
        if "space_before" in cfg:
            pf.space_before = Pt(cfg["space_before"])
        if "space_after" in cfg:
            pf.space_after = Pt(cfg["space_after"])
        if "alignment" in cfg:
            pf.alignment = cfg["alignment"]

    # pandoc reference-doc 需要至少一个段落才能正确识别样式
    doc.add_paragraph("")

    doc.save(output_path)
    print(f"[完成] 模板已生成: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] in {"-h", "--help"}:
        print("用法: python3 generate_reference_doc.py [输出路径]")
        sys.exit(0)

    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent
    default_output = skill_dir / "assets" / "drama-reference.docx"

    output = sys.argv[1] if len(sys.argv) > 1 else str(default_output)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    create_reference_doc(output)
