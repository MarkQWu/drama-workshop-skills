#!/usr/bin/env python3
"""
viz_gen.py — Markdown → HTML 可视化生成器（短剧 Skill 配套）

用法:
    python3 viz_gen.py creative-plan.md --type plan
    python3 viz_gen.py characters.md --type characters
    python3 viz_gen.py creative-plan.md characters.md   # 自动识别类型

输出:
    creative-plan.md  → creative-plan-viz.html（同目录）
    characters.md     → characters-viz.html（同目录）

零外部依赖，纯 Python 3.8+ 标准库。
设计风格：浅灰底 Light（#f5f6f8），清爽阅读体验。
"""

import re
import sys
import os
from pathlib import Path

# ════════════════════════════════════════
#  Design Tokens（从参考 HTML 提取）
# ════════════════════════════════════════

CSS_BASE = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", sans-serif;
  background: #f5f6f8; color: #1f2328;
  padding: 32px 24px; line-height: 1.6;
  max-width: 1100px; margin: 0 auto;
}
h1 { font-size: 1.6rem; color: #1f2328; margin-bottom: 4px; }
.subtitle { color: #656d76; font-size: 0.875rem; margin-bottom: 8px; }
.badge {
  display: inline-block; background: #eef1f4; border: 1px solid #d0d7de;
  border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; margin-right: 6px; color: #656d76;
}
.badge.green { background: #dafbe1; border-color: #2da44e; color: #1a7f37; }
.badge.blue { background: #ddf4ff; border-color: #218bff; color: #0969da; }
.section {
  background: #ffffff; border: 1px solid #d0d7de;
  border-radius: 10px; padding: 24px; margin-bottom: 28px;
  box-shadow: 0 1px 3px rgba(31,35,40,0.04);
}
.section.mcp { border-color: #2da44e; background: #f0fff4; }
.section-title {
  font-size: 0.9rem; font-weight: 600; color: #656d76;
  text-transform: uppercase; letter-spacing: 0.08em;
  margin-bottom: 20px; display: flex; align-items: center; gap: 8px;
}
.section-title::before {
  content: ''; display: inline-block; width: 3px; height: 14px;
  background: var(--accent, #0969da); border-radius: 2px;
}
table { width: 100%; border-collapse: collapse; font-size: 0.83rem; margin-top: 8px; }
th, td { padding: 10px 14px; border-bottom: 1px solid #d8dee4; text-align: left; }
th { color: #656d76; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }
td { color: #1f2328; }
tr:hover td { background: rgba(0,0,0,0.02); }
.text-block { font-size: 0.85rem; color: #1f2328; line-height: 1.7; }
.text-block p { margin-bottom: 12px; }
.text-block strong { color: #1f2328; font-weight: 700; }
.text-block li { margin-bottom: 6px; margin-left: 16px; }
blockquote {
  border-left: 3px solid #d0d7de; padding: 8px 16px; margin: 12px 0;
  color: #656d76; font-size: 0.83rem;
}

/* ── Acts Bar ── */
.acts { display: flex; gap: 0; border-radius: 8px; overflow: hidden; margin-bottom: 16px; }
.act { display: flex; flex-direction: column; padding: 16px; gap: 6px; }
.act-label { font-size: 0.7rem; color: #656d76; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
.act-ep { font-size: 0.85rem; font-weight: 700; color: #1f2328; }
.act-name { font-size: 0.8rem; color: #424a53; }
.act-1 { background: #dbeafe; flex: 15; border-right: 2px solid #f5f6f8; }
.act-2a { background: #dcfce7; flex: 15; border-right: 2px solid #f5f6f8; }
.act-2b { background: #fee2e2; flex: 18; border-right: 2px solid #f5f6f8; }
.act-3 { background: #ede9fe; flex: 12; }
.event-tag {
  display: inline-block; font-size: 0.7rem; padding: 2px 6px;
  border-radius: 3px; margin: 2px 2px 2px 0;
}
.tag-pay { background: #fef3c7; color: #a16207; border: 1px solid #e3a000; }
.tag-key { background: #ede9fe; color: #7c3aed; border: 1px solid #a78bfa; }
.tag-low { background: #d1fae5; color: #047857; border: 1px solid #6ee7b7; }

/* ── Bar Charts ── */
.bar-wrap { margin-bottom: 14px; }
.bar-label { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px; }
.bar-name { color: #1f2328; }
.bar-pct { color: #656d76; }
.bar-track { background: #e1e4e8; border-radius: 4px; height: 10px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; }

/* ── Paywall List ── */
.paywall-list { display: flex; flex-direction: column; gap: 12px; }
.paywall-item { display: flex; gap: 14px; align-items: flex-start; }
.paywall-ep {
  min-width: 52px; text-align: center; background: #fff8e6;
  border: 1px solid #e3a000; border-radius: 6px;
  padding: 4px 6px; font-size: 0.75rem; font-weight: 700; color: #a16207;
}
.paywall-content { flex: 1; }
.paywall-type { font-size: 0.7rem; color: #656d76; margin-bottom: 2px; }
.paywall-desc { font-size: 0.85rem; color: #1f2328; }

/* ── Pressure Track ── */
.pressure-track { display: flex; gap: 0; border-radius: 8px; overflow: hidden; min-height: 64px; }
.pressure-seg {
  display: flex; align-items: center; justify-content: center;
  font-size: 0.68rem; font-weight: 600; text-align: center;
  padding: 6px 8px; line-height: 1.4;
}

/* ── Clue Lines ── */
.clue-line { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.clue-dot { width: 10px; height: 10px; background: #cf222e; border-radius: 50%; flex-shrink: 0; }
.clue-text { font-size: 0.82rem; color: #1f2328; }
.clue-ep { font-size: 0.7rem; padding: 2px 8px; border-radius: 3px; background: #eef1f4; color: #656d76; white-space: nowrap; }

/* ── Comp Cards ── */
.comp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.comp-card {
  background: #ffffff; border: 1px solid #d0d7de;
  border-radius: 8px; padding: 14px; position: relative;
  box-shadow: 0 1px 2px rgba(31,35,40,0.04);
}
.comp-card.direct { border-color: #cf222e; }
.comp-card.ref { border-color: #d97706; }
.comp-card.gap { border-color: #1a7f37; border-style: dashed; }
.comp-title { font-size: 0.9rem; font-weight: 700; color: #1f2328; margin-bottom: 6px; }
.comp-tag-row { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 10px; }
.comp-tag {
  font-size: 0.68rem; padding: 1px 6px; border-radius: 3px;
  background: #eef1f4; color: #656d76;
}
.comp-heat-bar { background: #e1e4e8; border-radius: 3px; height: 6px; margin-bottom: 6px; overflow: hidden; }
.comp-heat-fill { height: 100%; border-radius: 3px; }
.comp-meta { font-size: 0.72rem; color: #656d76; }
.comp-diff { font-size: 0.75rem; color: #1f2328; margin-top: 8px; border-top: 1px solid #d8dee4; padding-top: 8px; }
.comp-diff em { color: #1a7f37; font-style: normal; }
.comp-badge-label {
  position: absolute; top: 10px; right: 10px;
  font-size: 0.65rem; padding: 1px 6px; border-radius: 3px; font-weight: 700;
}
.badge-direct { background: #ffebe9; color: #cf222e; }
.badge-ref { background: #fff8e6; color: #d97706; }
.badge-gap { background: #dafbe1; color: #1a7f37; }

/* ── Dual Table ── */
.dual-table th:nth-child(2) { color: #656d76; }
.dual-table .col-think { color: #1f2328; }
.dual-table .col-real { color: #1a7f37; }

/* ── Characters specific ── */
.overview-strip { display: flex; gap: 10px; margin-bottom: 32px; flex-wrap: wrap; }
.mini-card {
  flex: 1 1 140px; background: #ffffff; border: 1px solid #d0d7de;
  border-radius: 8px; padding: 12px 14px; cursor: pointer;
  transition: border-color 0.15s, transform 0.1s;
  text-decoration: none; color: inherit;
  box-shadow: 0 1px 2px rgba(31,35,40,0.04);
}
.mini-card:hover { transform: translateY(-2px); border-color: var(--accent, #0969da); }
.mc-name { font-size: 1rem; font-weight: 700; margin-bottom: 4px; }
.mc-role { font-size: 0.72rem; color: #656d76; margin-bottom: 8px; }
.mc-bar { height: 3px; border-radius: 2px; margin-top: 6px; background: var(--accent, #0969da); }
.mc-kw { font-size: 0.7rem; color: #656d76; }
.char-card {
  border-radius: 10px; overflow: hidden; margin-bottom: 24px;
  border: 1px solid var(--border, #d0d7de); background: var(--bg, #ffffff);
  box-shadow: 0 1px 3px rgba(31,35,40,0.04);
}
.char-header {
  padding: 18px 24px 14px; display: flex; align-items: flex-start; gap: 16px;
}
.char-avatar {
  width: 52px; height: 52px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; font-weight: 800; flex-shrink: 0;
  background: var(--avatar-bg, #eef1f4); color: var(--accent, #0969da);
}
.char-meta { flex: 1; }
.char-name { font-size: 1.3rem; font-weight: 700; color: var(--accent, #0969da); }
.char-age-role { font-size: 0.8rem; color: #656d76; margin-top: 2px; }
.role-chip {
  display: inline-block; padding: 2px 8px; border-radius: 10px;
  font-size: 0.7rem; font-weight: 600; margin-left: 8px;
  background: var(--avatar-bg, #eef1f4); color: var(--accent, #0969da);
}
.char-kw-row { margin-top: 8px; display: flex; gap: 6px; flex-wrap: wrap; }
.kw-chip {
  font-size: 0.72rem; padding: 2px 8px; border-radius: 4px;
  background: rgba(0,0,0,0.04); color: #424a53;
}
.char-body { padding: 0 24px 20px; }
.char-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.field-label {
  font-size: 0.7rem; font-weight: 600; color: #656d76;
  text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 4px;
}
.field-value { font-size: 0.85rem; color: #1f2328; line-height: 1.5; }
.identity-row { display: flex; gap: 12px; margin-bottom: 16px; }
.identity-box { flex: 1; padding: 10px 14px; border-radius: 8px; }
.id-pub { background: rgba(0,0,0,0.02); border: 1px solid #d0d7de; }
.id-real { background: color-mix(in srgb, var(--accent, #0969da) 8%, transparent); border: 1px solid color-mix(in srgb, var(--accent, #0969da) 25%, transparent); }
.id-label { font-size: 0.68rem; color: #656d76; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
.id-value { font-size: 0.83rem; }
.id-real .id-value { color: var(--accent, #0969da); }
.fd-pair {
  display: flex; align-items: flex-start; gap: 8px;
  margin-bottom: 8px; font-size: 0.8rem; padding: 8px 10px;
  background: rgba(0,0,0,0.02); border-radius: 6px;
}
.fd-desire { color: #0550ae; flex: 1; }
.fd-arrow { color: #8b949e; flex-shrink: 0; padding-top: 1px; font-size: 0.9rem; }
.fd-fear { color: #bc4c00; flex: 1; text-align: right; }
.voice-bubble {
  padding: 8px 12px; border-radius: 8px; font-size: 0.8rem; line-height: 1.5;
  border-left: 3px solid var(--accent, #0969da);
  background: rgba(0,0,0,0.02); margin-bottom: 8px;
}
.voice-scene { font-size: 0.68rem; color: #8b949e; margin-bottom: 2px; }
.voice-text { color: #1f2328; }
.voice-ban {
  margin-top: 8px; padding: 7px 12px; border-radius: 6px;
  font-size: 0.75rem; color: #cf222e;
  background: rgba(207, 34, 46, 0.06); border: 1px solid rgba(207, 34, 46, 0.2);
}
.voice-ban::before { content: '禁用 '; font-weight: 600; }
.stress-table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 0.78rem; }
.stress-table th {
  text-align: left; padding: 6px 10px;
  background: rgba(0,0,0,0.03); color: #656d76;
  font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;
}
.stress-table td { padding: 8px 10px; border-top: 1px solid #d8dee4; vertical-align: top; }
.divider { height: 1px; background: #d8dee4; margin: 16px 0; }

/* arc timeline */
.arc-container { padding: 8px 0; }
.arc-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.arc-label { width: 80px; font-size: 0.82rem; font-weight: 600; text-align: right; flex-shrink: 0; }
.arc-track { flex: 1; height: 28px; background: rgba(0,0,0,0.04); border-radius: 4px; position: relative; overflow: hidden; }
.arc-fill {
  position: absolute; top: 0; height: 100%; border-radius: 4px;
  display: flex; align-items: center; padding: 0 8px;
  font-size: 0.68rem; color: rgba(255,255,255,0.9); white-space: nowrap;
}
.arc-ep { font-size: 0.7rem; color: #656d76; width: 90px; flex-shrink: 0; }

/* villain layers */
.villain-pyramid { display: flex; flex-direction: column; gap: 12px; }
.vl-row {
  display: flex; align-items: center; gap: 16px; padding: 14px 18px;
  border-radius: 8px; border: 1px solid transparent;
}
.vl-layer { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; width: 100px; flex-shrink: 0; }
.vl-name { font-size: 0.9rem; font-weight: 700; margin-bottom: 3px; }
.vl-desc { font-size: 0.78rem; color: #656d76; }

@media (max-width: 760px) {
  .char-grid { grid-template-columns: 1fr; }
  .identity-row { flex-direction: column; }
  .overview-strip { gap: 8px; }
  .mini-card { flex: 1 1 120px; }
  .comp-grid { grid-template-columns: 1fr; }
  .acts { flex-direction: column; }
}
"""


def esc(text: str) -> str:
    """HTML escape."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def strip_bold(text: str) -> str:
    """Remove markdown bold markers."""
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)


def parse_md_table(text: str) -> list[dict]:
    """Parse a markdown table into list of dicts. Returns [] if no table found."""
    lines = [l.strip() for l in text.strip().split('\n') if l.strip().startswith('|')]
    if len(lines) < 3:
        return []
    headers = [h.strip() for h in lines[0].split('|')[1:-1]]
    rows = []
    for line in lines[2:]:  # skip header + separator
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) == len(headers):
            row = {}
            for i, h in enumerate(headers):
                row[strip_bold(h)] = strip_bold(cells[i])
            rows.append(row)
    return rows


def split_sections(md: str) -> dict[str, str]:
    """Split markdown into {heading: content} by ## headings."""
    sections = {}
    current_key = '__header__'
    current_lines = []
    for line in md.split('\n'):
        m = re.match(r'^##\s+(.+)', line)
        if m:
            sections[current_key] = '\n'.join(current_lines)
            current_key = m.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)
    sections[current_key] = '\n'.join(current_lines)
    return sections


def split_h3(text: str) -> dict[str, str]:
    """Split text by ### headings."""
    sections = {}
    current_key = '__intro__'
    current_lines = []
    for line in text.split('\n'):
        m = re.match(r'^###\s+(.+)', line)
        if m:
            sections[current_key] = '\n'.join(current_lines)
            current_key = m.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)
    sections[current_key] = '\n'.join(current_lines)
    return sections


def extract_list_items(text: str) -> list[str]:
    """Extract markdown list items."""
    items = []
    for line in text.split('\n'):
        m = re.match(r'^[-*]\s+(.+)', line.strip())
        if m:
            items.append(strip_bold(m.group(1)))
    return items


def render_table_html(rows: list[dict]) -> str:
    if not rows:
        return ''
    headers = list(rows[0].keys())
    html = '<table><thead><tr>'
    for h in headers:
        html += f'<th>{esc(h)}</th>'
    html += '</tr></thead><tbody>'
    for row in rows:
        html += '<tr>'
        for h in headers:
            html += f'<td>{esc(row.get(h, ""))}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html


def md_to_html_inline(text: str) -> str:
    """Convert minimal markdown inline formatting to HTML."""
    text = esc(text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)  # won't match after esc but keep
    return text


# ════════════════════════════════════════
#  Creative Plan Generator
# ════════════════════════════════════════

def generate_plan_html(md_path: str) -> str:
    md = Path(md_path).read_text(encoding='utf-8')
    sections = split_sections(md)
    header = sections.get('__header__', '')

    # Extract title
    title_match = re.search(r'^#\s+(.+)', md, re.MULTILINE)
    title = strip_bold(title_match.group(1)) if title_match else '创作方案'

    # Extract drama name from title (e.g. "与会测试：创作方案" → "与会测试")
    drama_name = title.split('：')[0].split(':')[0].strip() if ('：' in title or ':' in title) else title

    # Extract anchor
    anchor_match = re.search(r'>\s*anchor:\s*(.+)', md)
    anchor = strip_bold(anchor_match.group(1).strip()) if anchor_match else ''

    parts = []
    parts.append(f'<h1>《{esc(drama_name)}》创作方案可视化</h1>')

    # Badges from various sections
    badge_html = ''
    # Try to find genre/episode info from 时空背景 or header
    for sec_name, sec_text in sections.items():
        if '集' in sec_text:
            ep_match = re.search(r'(\d+)集', sec_text)
            if ep_match:
                badge_html += f'<span class="badge">{ep_match.group(1)}集</span>'
                break

    if anchor:
        short_anchor = anchor.split('—')[0].strip() if '—' in anchor else anchor[:30]
        badge_html += f'<span class="badge">anchor: {esc(short_anchor)}</span>'

    # MCP badge if MCP section exists
    mcp_sec = sections.get('MCP 数据校准（2026-05-20）', '') or sections.get([k for k in sections if 'MCP' in k][0], '') if any('MCP' in k for k in sections) else ''
    if mcp_sec:
        badge_html += '<span class="badge green">MCP 数据校准</span>'

    parts.append(f'<p class="subtitle">{badge_html}</p>')

    # ── MCP Section ──
    mcp_key = next((k for k in sections if 'MCP' in k), None)
    if mcp_key:
        mcp_text = sections[mcp_key]
        mcp_subs = split_h3(mcp_text)

        # Competitor table
        comp_key = next((k for k in mcp_subs if '竞品' in k), None)
        if comp_key:
            comp_text = mcp_subs[comp_key]
            comp_rows = parse_md_table(comp_text)

            # 校准结论
            conclusion_match = re.search(r'\*\*校准结论[：:]\*\*\s*(.+)', comp_text)
            conclusion = strip_bold(conclusion_match.group(1)) if conclusion_match else ''

            if conclusion:
                parts.append(f'<p class="subtitle" style="margin-bottom:24px">{esc(conclusion)}</p>')

            if comp_rows:
                # Max heat for scaling
                max_heat = 60  # M
                parts.append('<div class="section mcp" style="--accent:#1a7f37">')
                parts.append('<div class="section-title">MCP 竞品图谱</div>')
                parts.append('<div class="comp-grid">')
                for row in comp_rows:
                    name = row.get('剧名', '')
                    heat_str = row.get('热度', '0')
                    heat_num = int(re.search(r'(\d+)', heat_str).group(1)) if re.search(r'(\d+)', heat_str) else 0
                    plays = row.get('播放量', '')
                    tags = row.get('标签组合', '')
                    channel = row.get('频道', '')
                    diff = row.get('与本项目差异', '')
                    pct = min(100, int(heat_num / max_heat * 100))

                    # Classify card type
                    card_class = 'ref'
                    badge_class = 'badge-ref'
                    badge_label = '参考'
                    if '直接' in diff or channel == '女频':
                        if tags.count('+') >= 3 or '豪门' in tags:
                            card_class = 'direct'
                            badge_class = 'badge-direct'
                            badge_label = '直接竞品'

                    parts.append(f'<div class="comp-card {card_class}">')
                    parts.append(f'<span class="comp-badge-label {badge_class}">{badge_label}</span>')
                    parts.append(f'<div class="comp-title">{esc(name)}</div>')
                    # Tags
                    parts.append('<div class="comp-tag-row">')
                    for tag in tags.split('+'):
                        tag = tag.strip()
                        if tag:
                            parts.append(f'<span class="comp-tag">{esc(tag)}</span>')
                    if channel:
                        parts.append(f'<span class="comp-tag">{esc(channel)}</span>')
                    parts.append('</div>')
                    # Heat bar
                    color = 'linear-gradient(90deg,#cf222e,#a40e26)' if card_class == 'direct' else 'linear-gradient(90deg,#d97706,#a16207)'
                    parts.append(f'<div class="comp-heat-bar"><div class="comp-heat-fill" style="width:{pct}%;background:{color}"></div></div>')
                    parts.append(f'<div class="comp-meta">热度 {esc(heat_str)} · 播放 {esc(plays)}</div>')
                    if diff:
                        parts.append(f'<div class="comp-diff">{esc(diff)}</div>')
                    parts.append('</div>')
                parts.append('</div></div>')

        # Heat expectation
        heat_key = next((k for k in mcp_subs if '热度预期' in k), None)
        if heat_key:
            heat_items = extract_list_items(mcp_subs[heat_key])
            if heat_items:
                parts.append('<div class="section mcp" style="--accent:#1a7f37">')
                parts.append('<div class="section-title">热度预期（数据支撑）</div>')
                # Parse heat numbers and render bars
                max_h = 60
                for item in heat_items:
                    nums = re.findall(r'(\d+)M', item)
                    if nums:
                        val = int(nums[0])
                        pct = min(100, int(val / max_h * 100))
                        label = item.split('：')[0] if '：' in item else item[:20]
                        is_target = '本项目' in item
                        color = '#1a7f37' if is_target else '#0969da'
                        fw = ' font-weight:700;' if is_target else ''
                        parts.append(f'<div class="bar-wrap">')
                        parts.append(f'<div class="bar-label"><span class="bar-name" style="color:{color};{fw}">{esc(label)}</span><span class="bar-pct">{val}M</span></div>')
                        parts.append(f'<div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>')
                        parts.append('</div>')
                parts.append('</div>')

        # Revision table
        rev_key = next((k for k in mcp_subs if '修订' in k), None)
        if rev_key:
            rev_rows = parse_md_table(mcp_subs[rev_key])
            if rev_rows:
                parts.append('<div class="section mcp" style="--accent:#1a7f37">')
                parts.append('<div class="section-title">MCP 修订建议</div>')
                parts.append(render_table_html(rev_rows))
                parts.append('</div>')

    # ── Story Line & Core Conflict ──
    story_key = next((k for k in sections if '故事线' in k or '核心冲突' in k), None)
    if story_key:
        st = sections[story_key]
        items = extract_list_items(st)
        parts.append('<div class="section" style="--accent:#0969da">')
        parts.append('<div class="section-title">故事线与核心冲突</div>')
        for item in items:
            label_match = re.match(r'(.+?)[：:](.+)', item)
            if label_match:
                parts.append(f'<p class="text-block"><strong>{esc(label_match.group(1))}：</strong>{esc(label_match.group(2))}</p>')
            else:
                parts.append(f'<p class="text-block">{esc(item)}</p>')
        parts.append('</div>')

    # ── Synopsis ──
    syn_key = next((k for k in sections if '梗概' in k), None)
    if syn_key:
        syn_text = sections[syn_key].strip()
        # Remove leading blockquotes and blank lines
        syn_paras = [p.strip() for p in syn_text.split('\n\n') if p.strip() and not p.strip().startswith('>') and p.strip() != '---']
        if syn_paras:
            parts.append('<div class="section" style="--accent:#8250df">')
            parts.append('<div class="section-title">故事梗概</div>')
            parts.append('<div class="text-block">')
            for p in syn_paras:
                parts.append(f'<p>{esc(strip_bold(p))}</p>')
            parts.append('</div></div>')

    # ── Three Act Structure ──
    act_key = next((k for k in sections if '三幕' in k), None)
    if act_key:
        act_text = sections[act_key]
        act_subs = split_h3(act_text)

        parts.append('<div class="section" style="--accent:#0969da">')
        parts.append('<div class="section-title">三幕结构</div>')

        # Visual act bar
        parts.append('<div class="acts">')
        act_configs = [
            ('act-1', '第一幕', '建置', '第1-15集'),
            ('act-2a', '第二幕A', '棋局第一轮', '第16-30集'),
            ('act-2b', '第二幕B', '棋局加速', '第31-48集'),
            ('act-3', '第三幕', '高潮/结局', '第49-60集'),
        ]
        for cls, label, name, ep_range in act_configs:
            parts.append(f'<div class="{cls}">')
            parts.append(f'<span class="act-label">{esc(label)}</span>')
            parts.append(f'<span class="act-ep">{esc(ep_range)}</span>')
            parts.append(f'<span class="act-name">{esc(name)}</span>')
            parts.append('</div>')
        parts.append('</div>')

        # Dual table if exists
        dual_key = next((k for k in act_subs if '双层' in k or '对照' in k), None)
        if dual_key:
            dual_rows = parse_md_table(act_subs[dual_key])
            if dual_rows:
                parts.append(render_table_html(dual_rows))

        parts.append('</div>')

    # ── Wave Chart (text summary) ──
    wave_key = next((k for k in sections if '波形' in k or '节奏' in k), None)
    if wave_key:
        wave_text = sections[wave_key]
        items = extract_list_items(wave_text)
        if items:
            parts.append('<div class="section" style="--accent:#7c3aed">')
            parts.append('<div class="section-title">全剧节奏波形</div>')

            # Parse high/low/paywall points and render SVG
            highs = []
            lows = []
            paywalls = []
            for item in items:
                eps = re.findall(r'第(\d+)集', item)
                if '高潮' in item and eps:
                    highs = [int(e) for e in eps]
                elif '低谷' in item and eps:
                    lows = [int(e) for e in eps]
                elif '付费' in item and eps:
                    paywalls = [int(e) for e in eps]

            if highs or lows:
                total_eps = 60
                w, h_svg = 700, 200
                pad_x, pad_y = 50, 30

                # Build intensity curve from highs and lows
                all_points = {}
                for ep in highs:
                    all_points[ep] = 0.85 + (0.15 if ep > 50 else 0)
                for ep in lows:
                    all_points[ep] = 0.25
                # Add start and end
                all_points[1] = 0.7
                all_points[total_eps] = 0.9

                sorted_eps = sorted(all_points.keys())
                # Interpolate
                def get_y(ep):
                    if ep in all_points:
                        return all_points[ep]
                    # Linear interp
                    prev_ep = max(e for e in sorted_eps if e <= ep) if any(e <= ep for e in sorted_eps) else sorted_eps[0]
                    next_ep = min(e for e in sorted_eps if e >= ep) if any(e >= ep for e in sorted_eps) else sorted_eps[-1]
                    if prev_ep == next_ep:
                        return all_points[prev_ep]
                    t = (ep - prev_ep) / (next_ep - prev_ep)
                    return all_points[prev_ep] + t * (all_points[next_ep] - all_points[prev_ep])

                def ep_to_x(ep):
                    return pad_x + (ep - 1) / (total_eps - 1) * (w - 2 * pad_x)

                def val_to_y(val):
                    return pad_y + (1 - val) * (h_svg - 2 * pad_y)

                # Build smooth path
                path_points = []
                for ep in range(1, total_eps + 1):
                    path_points.append((ep_to_x(ep), val_to_y(get_y(ep))))

                path_d = f'M {path_points[0][0]:.1f} {path_points[0][1]:.1f}'
                for i in range(1, len(path_points)):
                    path_d += f' L {path_points[i][0]:.1f} {path_points[i][1]:.1f}'

                # Area fill
                area_d = path_d + f' L {path_points[-1][0]:.1f} {h_svg - pad_y} L {path_points[0][0]:.1f} {h_svg - pad_y} Z'

                svg = f'<svg viewBox="0 0 {w} {h_svg}" style="width:100%;height:auto;display:block;margin-top:12px">'
                svg += '<defs><linearGradient id="wg" x1="0" y1="0" x2="0" y2="1">'
                svg += '<stop offset="0%" stop-color="#0969da" stop-opacity="0.2"/>'
                svg += '<stop offset="100%" stop-color="#0969da" stop-opacity="0.02"/>'
                svg += '</linearGradient></defs>'

                # Grid lines
                for v in [0.25, 0.5, 0.75]:
                    y = val_to_y(v)
                    svg += f'<line x1="{pad_x}" y1="{y:.1f}" x2="{w-pad_x}" y2="{y:.1f}" stroke="#d8dee4" stroke-width="1"/>'

                # X axis
                svg += f'<line x1="{pad_x}" y1="{h_svg-pad_y}" x2="{w-pad_x}" y2="{h_svg-pad_y}" stroke="#afb8c1" stroke-width="1"/>'

                # Episode ticks
                for ep in [1, 10, 20, 30, 40, 50, 60]:
                    x = ep_to_x(ep)
                    svg += f'<text x="{x:.1f}" y="{h_svg-8}" text-anchor="middle" font-size="10" fill="#656d76">EP{ep}</text>'

                # Area + line
                svg += f'<path d="{area_d}" fill="url(#wg)"/>'
                svg += f'<path d="{path_d}" fill="none" stroke="#0969da" stroke-width="2"/>'

                # High points
                for ep in highs:
                    x, y = ep_to_x(ep), val_to_y(get_y(ep))
                    svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#0969da"/>'
                    svg += f'<text x="{x:.1f}" y="{y-10:.1f}" text-anchor="middle" font-size="9" fill="#0969da">EP{ep}</text>'

                # Low points
                for ep in lows:
                    x, y = ep_to_x(ep), val_to_y(get_y(ep))
                    svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#cf222e"/>'
                    svg += f'<text x="{x:.1f}" y="{y+16:.1f}" text-anchor="middle" font-size="9" fill="#cf222e">EP{ep}</text>'

                # Paywall markers
                for ep in paywalls:
                    x = ep_to_x(ep)
                    svg += f'<line x1="{x:.1f}" y1="{pad_y}" x2="{x:.1f}" y2="{h_svg-pad_y}" stroke="#a16207" stroke-width="1" stroke-dasharray="3,3"/>'
                    svg += f'<text x="{x:.1f}" y="{pad_y-4}" text-anchor="middle" font-size="8" fill="#a16207">💰</text>'

                svg += '</svg>'
                parts.append(svg)

            # Legend
            parts.append('<div style="display:flex;gap:20px;margin-top:12px;font-size:0.72rem">')
            parts.append('<span style="color:#0969da">● 高潮点</span>')
            parts.append('<span style="color:#cf222e">● 低谷点</span>')
            parts.append('<span style="color:#a16207">┆ 付费卡点</span>')
            parts.append('</div>')
            parts.append('</div>')

    # ── Paywall Design ──
    pay_key = next((k for k in sections if '付费卡点规划' in k), None)
    if pay_key:
        pay_rows = parse_md_table(sections[pay_key])
        if pay_rows:
            parts.append('<div class="section" style="--accent:#9a6700">')
            parts.append('<div class="section-title">付费卡点规划</div>')
            parts.append('<div class="paywall-list">')
            for row in pay_rows:
                ep = row.get('集数', '')
                ptype = row.get('卡点类型', '')
                desc = row.get('悬念设计', '')
                parts.append('<div class="paywall-item">')
                parts.append(f'<div class="paywall-ep">{esc(ep)}</div>')
                parts.append(f'<div class="paywall-content"><div class="paywall-type">{esc(ptype)}</div><div class="paywall-desc">{esc(desc)}</div></div>')
                parts.append('</div>')
            parts.append('</div></div>')

    # ── Satisfaction Matrix ──
    sat_key = next((k for k in sections if '爽点矩阵' in k), None)
    if sat_key:
        sat_rows = parse_md_table(sections[sat_key])
        if sat_rows:
            parts.append('<div class="section" style="--accent:#7c3aed">')
            parts.append('<div class="section-title">爽点矩阵</div>')
            parts.append(render_table_html(sat_rows))
            parts.append('</div>')

    # ── Commercial Ledger ──
    biz_key = next((k for k in sections if '商业账本' in k), None)
    if biz_key:
        biz_text = sections[biz_key]
        biz_subs = split_h3(biz_text)

        parts.append('<div class="section" style="--accent:#9a6700">')
        parts.append('<div class="section-title">商业账本</div>')

        # Intro text
        intro = biz_subs.get('__intro__', '').strip()
        intro_items = extract_list_items(intro)
        if intro_items:
            for item in intro_items:
                parts.append(f'<p class="text-block">{esc(item)}</p>')

        # Sub-tables
        for sub_name, sub_text in biz_subs.items():
            if sub_name == '__intro__':
                continue
            sub_rows = parse_md_table(sub_text)
            if sub_rows:
                parts.append(f'<div class="divider"></div>')
                parts.append(f'<div style="font-size:0.8rem;font-weight:600;color:#656d76;margin-bottom:12px">{esc(sub_name)}</div>')
                # Check for blockquote (MCP note)
                bq_match = re.search(r'>\s*(.+)', sub_text)
                if bq_match:
                    parts.append(f'<blockquote>{esc(strip_bold(bq_match.group(1)))}</blockquote>')
                parts.append(render_table_html(sub_rows))

        parts.append('</div>')

    # ── Ending ──
    end_key = next((k for k in sections if '结局' in k), None)
    if end_key:
        end_text = sections[end_key]
        items = extract_list_items(end_text)
        if items:
            parts.append('<div class="section" style="--accent:#8250df">')
            parts.append('<div class="section-title">结局设计</div>')
            for item in items:
                label_match = re.match(r'(.+?)[：:](.+)', item)
                if label_match:
                    parts.append(f'<p class="text-block"><strong>{esc(label_match.group(1))}：</strong>{esc(label_match.group(2))}</p>')
                else:
                    parts.append(f'<p class="text-block">{esc(item)}</p>')
            parts.append('</div>')

    body = '\n'.join(parts)
    return wrap_html(f'《{drama_name}》创作方案可视化', body)


# ════════════════════════════════════════
#  Characters Generator
# ════════════════════════════════════════

# Color palette for characters (up to 10)
CHAR_COLORS = [
    {'accent': '#0969da', 'bg': '#f6faff', 'border': '#b6d4fe', 'avatar_bg': '#ddf4ff'},
    {'accent': '#bc4c00', 'bg': '#fff8f3', 'border': '#ffd8b5', 'avatar_bg': '#fff1e5'},
    {'accent': '#4e6a8a', 'bg': '#f6f8fa', 'border': '#c8d1da', 'avatar_bg': '#e8edf2'},
    {'accent': '#9a6700', 'bg': '#fffcf0', 'border': '#f0d860', 'avatar_bg': '#fff8c5'},
    {'accent': '#1a7f37', 'bg': '#f0fff4', 'border': '#a7f3d0', 'avatar_bg': '#dafbe1'},
    {'accent': '#7c6930', 'bg': '#faf8f0', 'border': '#e0d8b0', 'avatar_bg': '#f0ecdc'},
    {'accent': '#cf222e', 'bg': '#fff5f5', 'border': '#fecaca', 'avatar_bg': '#ffebe9'},
    {'accent': '#8250df', 'bg': '#faf5ff', 'border': '#d8b4fe', 'avatar_bg': '#ede9fe'},
    {'accent': '#e05070', 'bg': '#fff5f7', 'border': '#fbb6ce', 'avatar_bg': '#ffe0ea'},
    {'accent': '#0e8585', 'bg': '#f0fafa', 'border': '#a0d8d8', 'avatar_bg': '#d5f0f0'},
]


def parse_character_block(text: str) -> dict:
    """Parse a single character block (### Name ... ---) into a dict of fields."""
    fields = {}
    current_field = None
    current_lines = []

    for line in text.split('\n'):
        field_match = re.match(r'^-\s+\*\*(.+?)\*\*[：:]\s*(.*)', line)
        if field_match:
            if current_field:
                fields[current_field] = '\n'.join(current_lines).strip()
            current_field = field_match.group(1).strip()
            current_lines = [field_match.group(2).strip()]
        elif current_field:
            current_lines.append(line)

    if current_field:
        fields[current_field] = '\n'.join(current_lines).strip()

    return fields


def parse_voice_samples(voice_text: str) -> dict:
    """Parse voice fingerprint section into structured data."""
    result = {'traits': [], 'samples': [], 'banned': ''}
    lines = voice_text.split('\n')
    current_context = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('- **声音指纹'):
            continue

        # Trait lines
        trait_match = re.match(r'-\s+(.+?)[：:](.+)', stripped)
        if trait_match and trait_match.group(1).strip() in ['句长倾向', '说话路径', '常用动词与称呼', '躲闪方式', '情绪失控语言']:
            result['traits'].append({'label': trait_match.group(1).strip(), 'value': strip_bold(trait_match.group(2).strip())})
            continue

        # Context headers
        if stripped.startswith('- 公开场合') or stripped.startswith('- **公开场合'):
            current_context = '公开场合'
            continue
        elif stripped.startswith('- 私下') or stripped.startswith('- **私下'):
            current_context = '私下'
            continue
        elif stripped.startswith('- 情绪爆发') or stripped.startswith('- **情绪爆发'):
            current_context = '情绪爆发'
            continue
        elif stripped.startswith('- 禁用') or stripped.startswith('- **禁用'):
            current_context = None
            ban_match = re.match(r'-\s+(?:\*\*)?禁用(?:\*\*)?[：:]\s*(.*)', stripped)
            if ban_match:
                result['banned'] = strip_bold(ban_match.group(1))
            continue

        # Sample lines
        if current_context and stripped.startswith('-'):
            sample_text = re.sub(r'^-\s+', '', stripped)
            result['samples'].append({'context': current_context, 'text': strip_bold(sample_text)})

    return result


def render_character_card(name: str, fields: dict, color: dict, char_id: str) -> str:
    """Render a single character card HTML."""
    accent = color['accent']
    style = f'--accent:{accent};--bg:{color["bg"]};--border:{color["border"]};--avatar-bg:{color["avatar_bg"]}'

    parts = []
    parts.append(f'<div class="char-card" id="{char_id}" style="{style}">')

    # Header
    avatar_char = name[0] if name else '?'
    age = fields.get('年龄', '')
    public_id = fields.get('公开身份', '')
    keywords = fields.get('性格关键词', '')
    real_id = fields.get('真实身份', '')

    # Determine role chip
    func = fields.get('表面功能 vs 真实功能', '')
    role_chip = ''
    if '女主' in func or '棋手' in func or '主角' in func:
        role_chip = '女主 · 棋手'
    elif '嫌疑人' in func:
        idx_match = re.search(r'嫌疑人(\d)', fields.get('爽点功能', '') + func)
        role_chip = f'嫌疑人{idx_match.group(1)}' if idx_match else '嫌疑人'
    elif '信任锚' in func or '道德' in func or '外婆' in public_id:
        role_chip = '信任锚'
    elif '凶手' in name or '反派' in func:
        role_chip = '终极反派'

    parts.append('<div class="char-header">')
    parts.append(f'<div class="char-avatar">{esc(avatar_char)}</div>')
    parts.append('<div class="char-meta">')
    parts.append(f'<div class="char-name">{esc(name)}')
    if role_chip:
        parts.append(f' <span class="role-chip">{esc(role_chip)}</span>')
    parts.append('</div>')
    parts.append(f'<div class="char-age-role">{esc(age)} · {esc(public_id)}</div>')

    if keywords:
        parts.append('<div class="char-kw-row">')
        for kw in re.split(r'[、，,]', keywords):
            kw = kw.strip()
            if kw:
                parts.append(f'<span class="kw-chip">{esc(kw)}</span>')
        parts.append('</div>')
    parts.append('</div></div>')

    # Body
    parts.append('<div class="char-body">')

    # Identity row
    if public_id or real_id:
        parts.append('<div class="identity-row">')
        if public_id:
            parts.append(f'<div class="identity-box id-pub"><div class="id-label">公开身份</div><div class="id-value">{esc(strip_bold(public_id))}</div></div>')
        if real_id:
            parts.append(f'<div class="identity-box id-real"><div class="id-label">真实身份</div><div class="id-value">{esc(strip_bold(real_id))}</div></div>')
        parts.append('</div>')

    # Core fields in grid
    grid_fields = [
        ('核心动机', '核心动机'),
        ('动机形成契机', '动机形成契机'),
        ('盲点/弱点', '盲点/弱点'),
        ('最大冲突点', '最大冲突点'),
        ('爽点功能', '爽点功能'),
    ]
    grid_items = [(label, fields.get(key, '')) for label, key in grid_fields if fields.get(key)]
    if grid_items:
        parts.append('<div class="char-grid">')
        for label, value in grid_items:
            parts.append(f'<div><div class="field-label">{esc(label)}</div><div class="field-value">{esc(strip_bold(value))}</div></div>')
        parts.append('</div>')

    # Desire-Fear pairs
    fd_text = fields.get('欲望-恐惧对位', '')
    if fd_text:
        fd_pairs = re.findall(r'渴望(.+?)↔\s*怕(.+?)(?:\n|$)', fd_text)
        if fd_pairs:
            parts.append('<div class="field-label" style="margin-bottom:8px">欲望 ↔ 恐惧</div>')
            for desire, fear in fd_pairs:
                parts.append('<div class="fd-pair">')
                parts.append(f'<span class="fd-desire">{esc(desire.strip())}</span>')
                parts.append('<span class="fd-arrow">↔</span>')
                parts.append(f'<span class="fd-fear">{esc(fear.strip())}</span>')
                parts.append('</div>')

    # Surface vs Real function
    surface_real = fields.get('表面功能 vs 真实功能', '')
    if surface_real:
        sr_match = re.match(r'观众以为(.+?)[/／](.+)', surface_real)
        if sr_match:
            parts.append('<div class="divider"></div>')
            parts.append('<div class="field-label">表面 vs 真实功能</div>')
            parts.append(f'<div class="fd-pair"><span class="fd-desire">观众以为：{esc(strip_bold(sr_match.group(1).strip()))}</span><span class="fd-arrow">→</span><span class="fd-fear">{esc(strip_bold(sr_match.group(2).strip()))}</span></div>')

    # Voice samples
    voice_text = fields.get('声音指纹 + voice 样本集', '')
    if voice_text:
        voice = parse_voice_samples(voice_text)
        if voice['samples'] or voice['banned']:
            parts.append('<div class="divider"></div>')
            parts.append('<div class="field-label" style="margin-bottom:10px">声音指纹</div>')

            for sample in voice['samples'][:4]:  # Limit to 4 samples
                parts.append(f'<div class="voice-bubble"><div class="voice-scene">{esc(sample["context"])}</div><div class="voice-text">{esc(sample["text"])}</div></div>')

            if voice['banned']:
                parts.append(f'<div class="voice-ban">{esc(voice["banned"])}</div>')

    # Stress table
    stress_text = fields.get('应激模式', '')
    if stress_text and '触发情境' in stress_text:
        stress_rows = parse_md_table(stress_text)
        if stress_rows:
            parts.append('<div class="divider"></div>')
            parts.append('<div class="field-label" style="margin-bottom:8px">应激模式</div>')
            parts.append('<table class="stress-table"><thead><tr><th>触发</th><th>反应</th><th>豁免</th></tr></thead><tbody>')
            for row in stress_rows:
                trigger = row.get('触发情境', '')
                reaction = row.get('实际反应', '')
                exempt = row.get('豁免条件', '')
                parts.append(f'<tr><td>{esc(trigger)}</td><td>{esc(reaction)}</td><td style="color:#656d76">{esc(exempt)}</td></tr>')
            parts.append('</tbody></table>')

    parts.append('</div></div>')
    return '\n'.join(parts)


def generate_characters_html(md_path: str) -> str:
    md = Path(md_path).read_text(encoding='utf-8')
    sections = split_sections(md)

    # Title
    title_match = re.search(r'^#\s+(.+)', md, re.MULTILINE)
    title = strip_bold(title_match.group(1)) if title_match else '角色档案'
    drama_name = title.split('：')[0].split(':')[0].strip()

    # Parse characters from ### headings under "主要角色" or directly
    char_section = sections.get('主要角色', '')
    if not char_section:
        # Try to find characters in the main content
        for k, v in sections.items():
            if '姓名' in v and '年龄' in v:
                char_section = v
                break

    # Split by ### to get individual characters
    char_blocks = re.split(r'(?=^###\s)', char_section, flags=re.MULTILINE)
    characters = []
    for block in char_blocks:
        name_match = re.match(r'###\s+(.+)', block.strip())
        if name_match:
            name = name_match.group(1).strip()
            # Remove (外婆) etc from display but keep for parsing
            fields = parse_character_block(block)
            characters.append((name, fields))

    # Also check for villain section
    villain_key = next((k for k in sections if '反派体系' in k), None)
    villain_data = None
    if villain_key:
        villain_text = sections[villain_key]
        villain_subs = split_h3(villain_text)
        villain_data = villain_subs

    parts = []

    # Header
    parts.append(f'<div style="margin-bottom:36px;border-bottom:1px solid #d0d7de;padding-bottom:24px">')
    parts.append(f'<div style="font-size:1.8rem;color:#1f2328;font-weight:700;margin-bottom:6px">《{esc(drama_name)}》角色档案</div>')
    parts.append(f'<span class="badge">{len(characters)} 角色</span>')
    parts.append(f'<span class="badge green">viz_gen.py 自动生成</span>')
    parts.append('</div>')

    # Overview strip
    parts.append('<div class="overview-strip">')
    for i, (name, fields) in enumerate(characters):
        color = CHAR_COLORS[i % len(CHAR_COLORS)]
        char_id = f'c{i}'
        keywords = fields.get('性格关键词', '')
        public_id = fields.get('公开身份', '')
        # Short role
        role_short = public_id[:12] + '…' if len(public_id) > 12 else public_id
        parts.append(f'<a class="mini-card" href="#{char_id}" style="--accent:{color["accent"]}">')
        parts.append(f'<div class="mc-name">{esc(name)}</div>')
        parts.append(f'<div class="mc-role">{esc(role_short)}</div>')
        parts.append(f'<div class="mc-kw">{esc(keywords)}</div>')
        parts.append(f'<div class="mc-bar"></div>')
        parts.append('</a>')
    parts.append('</div>')

    # Character cards
    for i, (name, fields) in enumerate(characters):
        color = CHAR_COLORS[i % len(CHAR_COLORS)]
        char_id = f'c{i}'
        parts.append(render_character_card(name, fields, color, char_id))

    # Additional sections: 称呼关系表, 角色弧线, etc.
    # Voice mapping table
    voice_map_key = next((k for k in sections if '语言风格映射' in k), None)
    if voice_map_key:
        vm_rows = parse_md_table(sections[voice_map_key])
        if vm_rows:
            parts.append('<div class="section" style="--accent:#8250df">')
            parts.append('<div class="section-title">角色-语言风格映射</div>')
            parts.append(render_table_html(vm_rows))
            parts.append('</div>')

    # Naming table
    naming_key = next((k for k in sections if '称呼' in k), None)
    if naming_key:
        naming_rows = parse_md_table(sections[naming_key])
        if naming_rows:
            parts.append('<div class="section" style="--accent:#1a7f37">')
            parts.append('<div class="section-title">称呼关系表</div>')
            parts.append(render_table_html(naming_rows))
            parts.append('</div>')

    # Arc section
    arc_key = next((k for k in sections if '角色弧线' in k), None)
    if arc_key:
        arc_text = sections[arc_key]
        arc_subs = split_h3(arc_text)

        parts.append('<div class="section" style="--accent:#bc4c00">')
        parts.append('<div class="section-title">角色弧线</div>')
        parts.append('<div class="arc-container">')

        total_eps = 60
        arc_colors = ['#0969da', '#bc4c00', '#4e6a8a', '#9a6700', '#1a7f37', '#7c6930', '#cf222e']

        for idx, (char_name, char_arc) in enumerate(arc_subs.items()):
            if char_name == '__intro__':
                continue
            # Extract episode numbers
            eps = re.findall(r'第(\d+)集', char_arc)
            if not eps:
                continue
            ep_nums = [int(e) for e in eps]
            start_ep = min(ep_nums)
            end_ep = max(ep_nums)
            color_hex = arc_colors[idx % len(arc_colors)]

            left_pct = (start_ep - 1) / total_eps * 100
            width_pct = max(5, (end_ep - start_ep + 1) / total_eps * 100)

            parts.append('<div class="arc-row">')
            parts.append(f'<div class="arc-label" style="color:{color_hex}">{esc(char_name)}</div>')
            parts.append('<div class="arc-track">')
            parts.append(f'<div class="arc-fill" style="left:{left_pct:.1f}%;width:{width_pct:.1f}%;background:{color_hex}">EP{start_ep}-{end_ep}</div>')
            parts.append('</div>')
            parts.append(f'<div class="arc-ep">EP{start_ep} → EP{end_ep}</div>')
            parts.append('</div>')

        parts.append('</div></div>')

    # Villain pyramid
    if villain_data:
        parts.append('<div class="section" style="--accent:#cf222e">')
        parts.append('<div class="section-title">反派体系</div>')
        parts.append('<div class="villain-pyramid">')

        layer_styles = [
            {'bg': 'rgba(9,105,218,0.06)', 'border': '#218bff', 'color': '#0550ae'},
            {'bg': 'rgba(217,119,6,0.06)', 'border': '#d97706', 'color': '#9a6700'},
            {'bg': 'rgba(207,34,46,0.06)', 'border': '#cf222e', 'color': '#cf222e'},
            {'bg': 'rgba(0,0,0,0.03)', 'border': '#afb8c1', 'color': '#656d76'},
        ]

        for idx, (layer_name, layer_text) in enumerate(villain_data.items()):
            if layer_name == '__intro__':
                continue
            style = layer_styles[idx % len(layer_styles)]
            # Extract positioning — try multiple field names
            pos_match = re.search(r'\*\*(定位|功能)\*\*[：:]\s*(.+)', layer_text)
            positioning = strip_bold(pos_match.group(2)) if pos_match else ''

            # Extract character names
            char_match = re.search(r'\*\*角色\*\*[：:]\s*(.+)', layer_text)
            char_names = strip_bold(char_match.group(1)) if char_match else ''

            # Fallback for layers without **定位**/**角色** (e.g. 终极反派 section with inline content)
            if not positioning and not char_names:
                # Try to extract first bold name as character
                bold_name = re.search(r'\*\*(.+?)\*\*[：:]', layer_text)
                if bold_name:
                    char_names = bold_name.group(1)
                # Use first meaningful line as description
                lines = [l.strip() for l in layer_text.strip().split('\n') if l.strip() and not l.strip().startswith('#')]
                if lines:
                    # Skip lines that are just the bold name we already got
                    desc_lines = [l for l in lines if not (bold_name and bold_name.group(0) in l)]
                    if desc_lines:
                        positioning = strip_bold(desc_lines[0])[:120]

            short_name = layer_name.split('（')[0].strip() if '（' in layer_name else layer_name[:6]

            parts.append(f'<div class="vl-row" style="background:{style["bg"]};border-color:{style["border"]}">')
            parts.append(f'<div class="vl-layer" style="color:{style["color"]}">{esc(short_name)}</div>')
            parts.append('<div>')
            if char_names:
                parts.append(f'<div class="vl-name" style="color:{style["color"]}">{esc(char_names)}</div>')
            parts.append(f'<div class="vl-desc">{esc(positioning)}</div>')
            parts.append('</div></div>')

        parts.append('</div></div>')

    body = '\n'.join(parts)
    return wrap_html(f'《{drama_name}》角色档案', body)


# ════════════════════════════════════════
#  Common
# ════════════════════════════════════════

def wrap_html(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<style>
{CSS_BASE}
</style>
</head>
<body>
{body}
</body>
</html>"""


def detect_type(path: str) -> str:
    """Auto-detect file type from filename."""
    name = Path(path).stem.lower()
    if 'creative-plan' in name or 'plan' in name:
        return 'plan'
    elif 'character' in name:
        return 'characters'
    return 'unknown'


def main():
    if len(sys.argv) < 2:
        print("用法: python3 viz_gen.py <file.md> [--type plan|characters]")
        print("      python3 viz_gen.py creative-plan.md characters.md  # 批量")
        sys.exit(1)

    files = []
    force_type = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--type' and i + 1 < len(sys.argv):
            force_type = sys.argv[i + 1]
            i += 2
        else:
            files.append(sys.argv[i])
            i += 1

    for f in files:
        if not os.path.exists(f):
            print(f"❌ 文件不存在: {f}")
            continue

        ftype = force_type or detect_type(f)
        out_path = str(Path(f).with_stem(Path(f).stem + '-viz').with_suffix('.html'))

        if ftype == 'plan':
            html = generate_plan_html(f)
        elif ftype == 'characters':
            html = generate_characters_html(f)
        else:
            print(f"⚠️ 无法识别文件类型: {f}，跳过。用 --type plan|characters 指定")
            continue

        Path(out_path).write_text(html, encoding='utf-8')
        print(f"✅ {Path(f).name} → {Path(out_path).name} ({os.path.getsize(out_path):,} bytes)")


if __name__ == '__main__':
    main()
