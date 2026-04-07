#!/usr/bin/env python3
"""Build detail.html - comprehensive HTML reference for NSSol SEs and sales staff."""

import json
import html
import glob
import os
from pathlib import Path

BASE = Path(__file__).parent

# ── helpers ────────────────────────────────────────────────────────────────────

def e(s):
    """html.escape a value; handle None/non-string gracefully."""
    if s is None:
        return ""
    return html.escape(str(s))

def load(path):
    with open(BASE / path, encoding="utf-8") as f:
        return json.load(f)

def badge(text, color="blue"):
    colors = {
        "red":    "#dc2626", "orange": "#ea580c", "green":  "#16a34a",
        "blue":   "#2563eb", "purple": "#7c3aed", "gray":   "#6b7280",
        "yellow": "#ca8a04", "teal":   "#0d9488",
    }
    bg = colors.get(color, colors["blue"])
    return (f'<span style="background:{bg};color:#fff;padding:2px 8px;'
            f'border-radius:4px;font-size:.75rem;font-weight:600;white-space:nowrap">{e(text)}</span>')

def severity_color(s):
    s = str(s).lower()
    if s in ("critical", "high"):  return "red"
    if s in ("medium",):           return "orange"
    if s in ("low",):              return "green"
    return "blue"

def list_items(lst, bullet="•"):
    if not lst:
        return ""
    items = "".join(f"<li>{e(i)}</li>" for i in lst)
    return f"<ul style='margin:.3em 0 .3em 1.2em;padding:0'>{items}</ul>"

def card(content, border_left_color=None, extra_style=""):
    brd = f"border-left:4px solid {border_left_color};" if border_left_color else ""
    return (f'<div style="background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.1);'
            f'padding:16px 20px;margin-bottom:14px;{brd}{extra_style}">{content}</div>')

def grid(items_html, cols=3, gap="12px"):
    return (f'<div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:{gap};margin-bottom:16px">'
            + "".join(items_html) + "</div>")

def section_wrap(sec_id, title, content):
    return (f'<div id="{sec_id}" class="sec" style="display:none">'
            f'<h1 style="margin:0 0 20px;font-size:1.6rem;color:#1e293b;border-bottom:3px solid #3b82f6;'
            f'padding-bottom:10px">{e(title)}</h1>'
            + content +
            f'</div>')

def table(headers, rows, caption=None):
    th = "".join(f'<th style="background:#1e293b;color:#fff;padding:8px 12px;text-align:left;white-space:nowrap">{e(h)}</th>' for h in headers)
    body = ""
    for i, row in enumerate(rows):
        bg = "#f8fafc" if i % 2 == 0 else "#fff"
        tds = "".join(f'<td style="padding:7px 12px;border-bottom:1px solid #e2e8f0;vertical-align:top">{cell}</td>' for cell in row)
        body += f'<tr style="background:{bg}">{tds}</tr>'
    cap = f'<caption style="caption-side:top;font-weight:700;color:#1e293b;margin-bottom:6px;text-align:left">{e(caption)}</caption>' if caption else ""
    return (f'<div style="overflow-x:auto;margin-bottom:20px">'
            f'<table style="border-collapse:collapse;width:100%;font-size:.88rem">'
            f'{cap}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>')

# ── CSS ────────────────────────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; }
body { margin: 0; font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif;
       background: #f1f5f9; color: #334155; font-size: 14px; line-height: 1.6; }
#sidebar { position: fixed; left: 0; top: 0; bottom: 0; width: 220px; background: #1e293b;
           overflow-y: auto; z-index: 100; padding: 0 0 20px; }
#sidebar h2 { color: #94a3b8; font-size: .7rem; letter-spacing: .1em; text-transform: uppercase;
              padding: 14px 16px 6px; margin: 0; }
#sidebar a { display: block; color: #cbd5e1; text-decoration: none; padding: 7px 16px;
             font-size: .83rem; transition: background .15s; }
#sidebar a:hover, #sidebar a.active { background: #334155; color: #fff; }
#main { margin-left: 220px; padding: 28px 32px; min-height: 100vh; }
.sec h2 { color: #1e293b; margin: 28px 0 10px; font-size: 1.15rem; }
.sec h3 { color: #334155; margin: 18px 0 8px; font-size: 1rem; }
.toc-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
           padding: 14px 20px; margin-bottom: 20px; }
.toc-box a { color: #2563eb; text-decoration: none; display: block; padding: 3px 0;
             font-size: .88rem; }
.toc-box a:hover { text-decoration: underline; }
.key-takeaway { background: #eff6ff; border-left: 4px solid #3b82f6; padding: 10px 14px;
                margin: 12px 0; border-radius: 0 6px 6px 0; font-size: .88rem; }
.callout-red { background: #fef2f2; border-left: 4px solid #dc2626; padding: 12px 16px;
               margin-bottom: 20px; border-radius: 0 8px 8px 0; }
.dialogue-left { background: #f0f9ff; border-radius: 0 12px 12px 12px; padding: 10px 14px;
                 margin: 6px 0 6px 0; max-width: 85%; font-size: .88rem; }
.dialogue-right { background: #f0fdf4; border-radius: 12px 0 12px 12px; padding: 10px 14px;
                  margin: 6px 0 6px auto; max-width: 85%; font-size: .88rem; }
.subtext { color: #64748b; font-size: .78rem; margin-top: 4px; font-style: italic; }
.speaker-label { font-weight: 700; font-size: .78rem; color: #475569; margin-bottom: 3px; }
.phase-block { background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.1);
               padding: 14px; margin-bottom: 16px; }
.phase-cols { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; }
.phase-col { background: #f8fafc; border-radius: 6px; padding: 10px 12px; }
.phase-col h4 { margin: 0 0 8px; font-size: .8rem; color: #64748b; text-transform: uppercase;
                letter-spacing: .05em; }
.tab-btn { background: #e2e8f0; border: none; padding: 7px 14px; cursor: pointer;
           border-radius: 6px 6px 0 0; font-size: .83rem; margin-right: 4px; }
.tab-btn.active { background: #2563eb; color: #fff; }
.tab-panel { display: none; }
.tab-panel.active { display: block; }
.roadmap { display: flex; gap: 0; margin-bottom: 20px; overflow-x: auto; }
.roadmap-step { background: #3b82f6; color: #fff; padding: 10px 16px; flex: 1; min-width: 120px;
                text-align: center; font-size: .8rem; position: relative; }
.roadmap-step:not(:last-child)::after { content: '▶'; position: absolute; right: -10px; top: 50%;
   transform: translateY(-50%); z-index: 1; color: #3b82f6; font-size: 1.2rem; }
.roadmap-step:nth-child(2n) { background: #1d4ed8; }
.matrix-table th { position: sticky; top: 0; background: #1e293b; color: #fff; }
.score-native { color: #16a34a; font-weight: 700; }
.score-strong  { color: #2563eb; font-weight: 600; }
.score-partial { color: #ea580c; }
.score-none    { color: #94a3b8; }
@media print {
  #sidebar { display: none; }
  #main { margin-left: 0; padding: 20px; }
  .sec { display: block !important; }
  .tab-panel { display: block !important; }
}
"""

# ── JS ─────────────────────────────────────────────────────────────────────────

JS = """
function showSection(id) {
  document.querySelectorAll('.sec').forEach(s => s.style.display = 'none');
  var el = document.getElementById(id);
  if (el) el.style.display = 'block';
  document.querySelectorAll('#sidebar a').forEach(a => {
    a.classList.toggle('active', a.dataset.sec === id);
  });
  window.scrollTo(0,0);
}
function showTab(groupId, tabId) {
  document.querySelectorAll('#'+groupId+' .tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('#'+groupId+' .tab-btn').forEach(b => b.classList.remove('active'));
  var panel = document.getElementById(tabId);
  if (panel) panel.classList.add('active');
  event.target.classList.add('active');
}
document.addEventListener('DOMContentLoaded', function() {
  showSection('sec-ad-primer');
});
"""

# ── SIDEBAR ────────────────────────────────────────────────────────────────────

NAV_GROUPS = [
    ("Active Directory", [
        ("sec-ad-primer",   "🏛️ AD入門"),
        ("sec-ad-legacy",   "⚔️ ADの功罪"),
    ]),
    ("セキュリティ", [
        ("sec-ransomware",  "🦠 ランサムウェア"),
    ]),
    ("アーキテクチャ", [
        ("sec-multi-forest","🌲 マルチフォレスト"),
        ("sec-ma",          "🤝 M&A統合"),
        ("sec-vpn-sase",    "🌐 VPN・SASE"),
    ]),
    ("製品比較", [
        ("sec-idp",         "🔐 IdP比較"),
        ("sec-pam",         "🔑 PAM比較"),
        ("sec-iam-matrix",  "📊 IAMマトリクス"),
        ("sec-ldap",        "📂 LDAP比較"),
    ]),
    ("ライフサイクル・規制", [
        ("sec-os-lifecycle","📅 OSライフサイクル"),
        ("sec-frameworks",  "⚖️ フレームワーク"),
    ]),
    ("IGA・運用", [
        ("sec-iga",         "🏛️ IGAフレームワーク"),
        ("sec-jml",         "🔄 JMLプロセス"),
    ]),
    ("業種別", [
        ("sec-industry-finance",  "🏦 金融業"),
        ("sec-industry-mfg",      "🏭 製造業"),
        ("sec-industry-energy",   "⚡ エネルギー業"),
    ]),
    ("DBセキュリティ", [
        ("sec-oracle",      "🗄️ Oracle DB認証"),
    ]),
    ("シナリオ", [
        ("sec-scenarios",   "🎭 シナリオ対話"),
    ]),
]

def build_sidebar():
    parts = ['<div id="sidebar">']
    parts.append('<div style="padding:16px;border-bottom:1px solid #334155">'
                 '<h1 style="color:#fff;margin:0;font-size:.95rem;font-weight:700">IDM参照ドキュメント</h1>'
                 '<p style="color:#94a3b8;margin:4px 0 0;font-size:.72rem">NSSol SE・営業向け</p>'
                 '</div>')
    for grp_name, links in NAV_GROUPS:
        parts.append(f'<h2>{e(grp_name)}</h2>')
        for sec_id, label in links:
            parts.append(f'<a href="#" onclick="showSection(\'{sec_id}\');return false" '
                         f'data-sec="{sec_id}">{e(label)}</a>')
    parts.append('</div>')
    return "".join(parts)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

# ── 1. AD Primer ───────────────────────────────────────────────────────────────

def build_ad_primer():
    data = load("04_server_auth/active_directory_primer.json")
    chapters = data.get("chapters", [])
    glossary = data.get("glossary", [])

    # TOC
    toc_items = "".join(
        f'<a href="#" onclick="document.getElementById(\'ch-{e(c.get("chapter_id",""))}\').scrollIntoView({{behavior:\'smooth\'}});return false">'
        f'第{i+1}章: {e(c.get("title",""))}</a>'
        for i, c in enumerate(chapters)
    )
    toc = f'<div class="toc-box"><strong>目次</strong><br>{toc_items}</div>'

    # Prologue
    prologue = data.get("prologue", {})
    pro_html = ""
    if prologue:
        pro_html = card(
            f'<h3 style="margin:0 0 8px;color:#1e293b">{e(prologue.get("title","はじめに"))}</h3>'
            f'<p style="margin:0">{e(prologue.get("body", ""))}</p>',
            extra_style="background:#f0f9ff;border:1px solid #bae6fd"
        )

    # Chapters
    chaps_html = ""
    for i, ch in enumerate(chapters):
        ch_id = ch.get("chapter_id", f"ch{i}")
        sections = ch.get("sections", [])
        sec_html = ""
        for s in sections:
            kp = s.get("key_point", "")
            sec_html += (
                f'<h3 style="color:#1d4ed8;margin:16px 0 8px">{e(s.get("title",""))}</h3>'
                f'<p style="margin:0 0 8px">{e(s.get("body",""))}</p>'
            )
            if kp:
                sec_html += f'<div class="key-takeaway">💡 {e(kp)}</div>'
        chaps_html += (
            f'<div id="ch-{e(ch_id)}" style="background:#fff;border-radius:8px;'
            f'box-shadow:0 1px 4px rgba(0,0,0,.1);padding:20px 24px;margin-bottom:16px">'
            f'<h2 style="margin:0 0 4px;color:#1e293b">第{i+1}章: {e(ch.get("title",""))}</h2>'
            f'<p style="margin:0 0 12px;color:#64748b;font-size:.85rem">{e(ch.get("subtitle",""))}</p>'
            f'{sec_html}'
            f'</div>'
        )

    # Glossary
    glos_html = ""
    if glossary:
        dl_items = "".join(
            f'<dt style="font-weight:700;color:#1e293b;margin-top:10px">{e(g.get("term",""))}'
            f'<span style="font-weight:400;color:#64748b;font-size:.82rem"> [{e(g.get("reading",""))}]</span></dt>'
            f'<dd style="margin:2px 0 0 1.5em;color:#475569">{e(g.get("explanation",""))}</dd>'
            for g in glossary
        )
        glos_html = (
            f'<div style="background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.1);'
            f'padding:20px 24px;margin-top:24px">'
            f'<h2 style="margin:0 0 14px;color:#1e293b">📖 用語集</h2>'
            f'<dl style="margin:0">{dl_items}</dl>'
            f'</div>'
        )

    content = toc + pro_html + chaps_html + glos_html
    return section_wrap("sec-ad-primer", "🏛️ Active Directory 入門", content)


# ── 2. AD Legacy ───────────────────────────────────────────────────────────────

def build_ad_legacy():
    data = load("04_server_auth/active_directory_legacy.json")

    # Strengths (list of strings)
    strengths = data.get("strengths", [])
    merit_cards = "".join(
        card(f'<p style="margin:0">✅ {e(s)}</p>', border_left_color="#16a34a")
        for s in strengths
    )
    merits_html = (
        f'<h2>✅ ADのメリット</h2>'
        + merit_cards
    )

    # Weaknesses (list of objects)
    weaknesses = data.get("weaknesses", [])
    demerit_rows = []
    for w in weaknesses:
        sev = w.get("severity", "")
        demerit_rows.append([
            e(w.get("name", "")),
            badge(sev, severity_color(sev)),
            e(w.get("description", "")),
            e(w.get("mitigation", "")),
        ])
    demerits_html = (
        f'<h2>⚠️ ADの問題点・デメリット</h2>'
        + table(["名称", "深刻度", "説明", "対策"], demerit_rows)
    )

    # Japan-specific problems
    jp_probs = data.get("japan_specific_problems", [])
    jp_html = ""
    if jp_probs:
        jp_items = "".join(
            card(
                f'<strong>{e(p.get("problem",""))}</strong>'
                f'<p style="margin:6px 0 0;color:#475569;font-size:.88rem">{e(p.get("background",""))}</p>'
                f'<p style="margin:6px 0 0;font-size:.85rem"><em>推奨:</em> {e(p.get("recommended_approach",""))}</p>'
            )
            for p in jp_probs if isinstance(p, dict)
        )
        jp_html = f'<h2>🇯🇵 日本特有の課題</h2>{jp_items}'

    # Attack techniques from weaknesses
    attack_related = [w for w in weaknesses if w.get("attack_technique")]
    if attack_related:
        atk_html = '<h2>🔴 攻撃技術・悪用パターン</h2>'
        for w in attack_related:
            sev = w.get("severity", "")
            example = w.get("real_world_example", "")
            atk_html += card(
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
                f'<span style="color:#dc2626;font-weight:700;font-size:1rem">{e(w.get("name",""))}</span>'
                f'{badge(sev, severity_color(sev))}'
                f'</div>'
                f'<p style="margin:0 0 6px"><strong>攻撃手法:</strong> {e(w.get("attack_technique",""))}</p>'
                + (f'<p style="margin:0 0 6px;font-size:.85rem;color:#dc2626">'
                   f'<strong>実例:</strong> {e(example)}</p>' if example else "")
                + f'<p style="margin:0;font-size:.85rem"><strong>対策:</strong> {e(w.get("mitigation",""))}</p>',
                border_left_color="#dc2626"
            )
    else:
        atk_html = ""

    # Migration to Entra
    mte = data.get("migration_to_entra", {})
    hybrid_options = mte.get("hybrid_options", [])
    migration_steps = mte.get("migration_steps", [])
    challenges = mte.get("challenges", [])

    mig_html = '<h2>🚀 Entraへの移行</h2>'
    if hybrid_options:
        opts = "".join(
            card(
                f'<strong>{e(o.get("option",""))}</strong>'
                f'<p style="margin:6px 0 3px;font-size:.87rem"><span style="color:#16a34a">✔ 適用場面: </span>{e(o.get("fit",""))}</p>'
                f'<p style="margin:0;font-size:.87rem"><span style="color:#ea580c">⚠ 制限: </span>{e(o.get("limit",""))}</p>'
            )
            for o in hybrid_options
        )
        mig_html += f'<h3>ハイブリッド移行オプション</h3>{opts}'
    if migration_steps:
        steps_html = "".join(f'<li style="margin-bottom:6px">{e(s)}</li>' for s in migration_steps)
        mig_html += f'<h3>移行ステップ</h3><ol style="padding-left:1.5em">{steps_html}</ol>'
    if challenges:
        ch_cards = "".join(
            card(f'<p style="margin:0">⚡ {e(c)}</p>', border_left_color="#ea580c")
            for c in challenges if isinstance(c, str)
        )
        if ch_cards:
            mig_html += f'<h3>移行の課題</h3>{ch_cards}'

    content = merits_html + demerits_html + jp_html + atk_html + mig_html
    return section_wrap("sec-ad-legacy", "⚔️ ADの功罪", content)


# ── 3. Ransomware ──────────────────────────────────────────────────────────────

def build_ransomware():
    data = load("06_security_hardening/ransomware_id_attack_scenarios.json")

    # Why ID matters
    wim = data.get("why_id_matters_to_attackers", {})
    why_html = ""
    if wim:
        why_html = (
            f'<div class="callout-red">'
            f'<h2 style="margin:0 0 8px;color:#dc2626">🚨 なぜ攻撃者はIDを狙うか</h2>'
            f'<p style="margin:0 0 8px"><strong>概要:</strong> {e(wim.get("overview",""))}</p>'
            f'<p style="margin:0 0 8px"><strong>攻撃者の思考:</strong> {e(wim.get("attacker_mindset",""))}</p>'
        )
        timeline = wim.get("typical_timeline_hours", {})
        if timeline:
            why_html += (
                f'<p style="margin:4px 0"><strong>典型的な侵害タイムライン:</strong> '
                f'初期侵害={e(str(timeline.get("initial_compromise","")))}h → '
                f'ラテラルムーブ={e(str(timeline.get("lateral_movement","")))}h → '
                f'ドメイン掌握={e(str(timeline.get("domain_dominance","")))}h → '
                f'展開={e(str(timeline.get("ransomware_deployment","")))}h</p>'
            )
        why_html += '</div>'

    # Kill chain
    kill_chain = data.get("kill_chain_id_mapping", [])
    kc_html = '<h2>💀 キルチェーン × ID管理失敗</h2>'
    for kc in kill_chain:
        kc_html += (
            f'<div class="phase-block">'
            f'<div style="font-weight:700;font-size:1rem;color:#1e293b;margin-bottom:10px">'
            f'Phase {e(str(kc.get("phase","")))} — {e(kc.get("phase_name",""))}</div>'
            f'<div class="phase-cols">'
            f'<div class="phase-col"><h4>🔴 攻撃技術</h4>{list_items(kc.get("attack_techniques",[]))}</div>'
            f'<div class="phase-col"><h4>❌ ID管理の失敗</h4>{list_items(kc.get("id_management_failures",[]))}</div>'
            f'<div class="phase-col"><h4>🛡️ 対策</h4>{list_items(kc.get("countermeasures",[]))}</div>'
            f'</div></div>'
        )

    # Incident scenarios
    scenarios = data.get("incident_scenarios", [])
    sc_html = '<h2>📋 インシデントシナリオ</h2>'
    for sc in scenarios:
        timeline = sc.get("timeline", [])
        tl_html = ""
        for tl in timeline:
            hr = tl.get("hour", "")
            ev = tl.get("event", "")
            tl_html += (
                f'<div style="display:flex;gap:10px;margin-bottom:6px;font-size:.85rem">'
                f'<span style="background:#dc2626;color:#fff;padding:2px 6px;border-radius:4px;'
                f'white-space:nowrap;min-width:50px;text-align:center">+{e(str(hr))}h</span>'
                f'<span>{e(ev)}</span></div>'
            )
        lessons = sc.get("post_incident_lessons", [])
        les_html = list_items(lessons)
        id_fails = sc.get("id_failures_identified", [])
        id_html = list_items(id_fails)

        sc_html += card(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
            f'<h3 style="margin:0;color:#1e293b">{e(sc.get("title",""))}</h3>'
            f'{badge(sc.get("industry",""), "blue")}'
            f'</div>'
            f'<p style="margin:0 0 10px;color:#475569">{e(sc.get("story",""))}</p>'
            f'<p style="margin:0 0 4px"><strong>被害範囲:</strong> {e(sc.get("damage_scope",""))}</p>'
            f'<h4 style="margin:12px 0 4px;color:#dc2626">⏱️ タイムライン</h4>{tl_html}'
            f'<h4 style="margin:12px 0 4px;color:#dc2626">❌ 特定されたID管理の失敗</h4>{id_html}'
            f'<h4 style="margin:12px 0 4px;color:#16a34a">💡 事後の教訓</h4>{les_html}',
            border_left_color="#dc2626"
        )

    # ID Investment
    iitm = data.get("id_investment_true_meaning", {})
    invest_html = ""
    if iitm:
        invest_html = card(
            f'<h3 style="margin:0 0 8px;color:#1e293b">💰 ID投資の本質的意味</h3>'
            f'<p><strong>誤解:</strong> {e(iitm.get("misconception",""))}</p>'
            f'<p><strong>現実:</strong> {e(iitm.get("reality",""))}</p>'
            f'<p><strong>アーキテクチャへの影響:</strong> {e(iitm.get("architecture_impact",""))}</p>'
            f'<p style="margin:0"><strong>ROI論拠:</strong> {e(iitm.get("roi_argument",""))}</p>',
            extra_style="background:#f0fdf4;border:1px solid #bbf7d0"
        )

    content = why_html + kc_html + sc_html + invest_html
    return section_wrap("sec-ransomware", "🦠 ランサムウェアとID管理", content)


# ── 4. Multi-Forest ────────────────────────────────────────────────────────────

def build_multi_forest():
    data = load("03_identity_architecture/multi_forest_consolidation.json")

    # Why multi-forest
    wmf = data.get("why_multi_forest", {})
    reasons_html = '<h2>🌲 マルチフォレストが生まれる理由</h2>'
    col_items = []
    for key, title in [("historical_reasons","🏛️ 歴史的背景"),
                        ("security_reasons","🔒 セキュリティ上の理由"),
                        ("organizational_reasons","🏢 組織的理由")]:
        reasons = wmf.get(key, [])
        col_items.append(
            f'<div style="background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.1);padding:14px">'
            f'<h3 style="margin:0 0 10px;font-size:.95rem">{title}</h3>'
            + list_items(reasons) +
            f'</div>'
        )
    reasons_html += grid(col_items)

    # Forest trust types
    trust_types = data.get("forest_trust_types", [])
    trust_rows = []
    for t in trust_types:
        rl = t.get("risk_level", "")
        trust_rows.append([
            e(t.get("trust_type", "")),
            e(t.get("direction", "")),
            e(t.get("transitivity", "")),
            badge(rl, severity_color(rl)),
            e(t.get("use_case", "")),
            badge("日本で一般的" if t.get("japan_common") else "まれ", "green" if t.get("japan_common") else "gray"),
        ])
    trust_html = '<h2>🔗 フォレスト信頼タイプ</h2>' + table(
        ["信頼タイプ", "方向", "推移性", "リスク", "用途", "日本実情"], trust_rows
    )

    # Consolidation patterns
    patterns = data.get("consolidation_patterns", [])
    patt_html = '<h2>🏗️ 統合パターン</h2>'
    for p in patterns:
        pros = p.get("pros", [])
        cons = p.get("cons", [])
        pros_html = list_items(pros)
        cons_html = list_items(cons)
        case = p.get("case_example", "")
        patt_html += card(
            f'<h3 style="margin:0 0 8px;color:#1e293b">{e(p.get("name",""))}</h3>'
            f'<p style="margin:0 0 8px">{e(p.get("description",""))}</p>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:10px">'
            f'<div><strong style="color:#16a34a">メリット</strong>{pros_html}</div>'
            f'<div><strong style="color:#dc2626">デメリット</strong>{cons_html}</div>'
            f'</div>'
            + (f'<div style="background:#f8fafc;border-radius:6px;padding:8px 12px;font-size:.85rem">'
               f'<strong>事例:</strong> {e(case)}</div>' if case else "")
        )

    # Technical challenges
    tc = data.get("technical_challenges", [])
    tc_items = []
    for t in tc:
        tc_items.append(
            card(
                f'<strong>{e(t.get("challenge",""))}</strong>'
                f'<p style="margin:6px 0 0;font-size:.87rem;color:#475569">{e(t.get("description",""))}</p>'
            )
        )
    tc_html = f'<h2>⚡ 技術的課題</h2><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px">{"".join(tc_items)}</div>'

    content = reasons_html + trust_html + patt_html + tc_html
    return section_wrap("sec-multi-forest", "🌲 マルチフォレスト統合", content)


# ── 5. M&A ─────────────────────────────────────────────────────────────────────

def build_ma():
    data = load("07_migration_patterns/ma_identity_integration.json")

    # Overview
    overview = data.get("overview", {})
    ov_html = ""
    if isinstance(overview, dict) and overview:
        ov_html = card(
            f'<p style="margin:0">{e(overview.get("summary", str(overview)))}</p>',
            extra_style="background:#f0f9ff;border:1px solid #bae6fd"
        )

    # Integration phases - roadmap + detail
    phases = data.get("integration_phases", [])
    roadmap_steps = "".join(
        f'<div class="roadmap-step"><div style="font-weight:700">Phase {e(str(ph.get("phase","")))}:</div>'
        f'<div>{e(ph.get("name",""))}</div>'
        f'<div style="font-size:.75rem;margin-top:4px;opacity:.85">{e(ph.get("timing",""))}</div></div>'
        for ph in phases
    )
    phases_html = (
        f'<h2>📅 統合フェーズ</h2>'
        f'<div class="roadmap">{roadmap_steps}</div>'
    )
    for ph in phases:
        tasks = ph.get("id_tasks", [])
        csf = ph.get("critical_success_factors", "")
        dur = ph.get("typical_duration", "")
        phases_html += card(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
            f'<span style="background:#3b82f6;color:#fff;padding:3px 10px;border-radius:20px;font-weight:700">'
            f'Phase {e(str(ph.get("phase","")))}</span>'
            f'<strong>{e(ph.get("name",""))}</strong>'
            f'{badge(dur, "gray") if dur else ""}'
            f'</div>'
            f'<p style="margin:0 0 6px;font-size:.85rem;color:#64748b">{e(ph.get("timing",""))}</p>'
            + list_items(tasks)
            + (f'<p style="margin:8px 0 0;font-size:.85rem"><strong>成功要因:</strong> {e(csf)}</p>' if csf else "")
        )

    # Scenarios
    scenarios = data.get("integration_scenarios", [])
    sc_html = '<h2>📋 統合シナリオ</h2>'
    for sc in scenarios:
        chal = sc.get("key_challenges", [])
        lessons = sc.get("lessons_learned", [])
        sc_html += card(
            f'<h3 style="margin:0 0 10px;color:#1e293b">{e(sc.get("title",""))}</h3>'
            f'<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:12px;font-size:.87rem">'
            f'<div><strong>買収側:</strong> {e(sc.get("acquirer_profile",""))}</div>'
            f'<div><strong>対象側:</strong> {e(sc.get("target_profile",""))}</div>'
            f'<div><strong>統合期間:</strong> {e(str(sc.get("timeline_months","")))}ヶ月</div>'
            f'<div><strong>統合アプローチ:</strong> {e(sc.get("integration_approach",""))}</div>'
            f'</div>'
            f'<div style="background:#eff6ff;border-radius:6px;padding:10px 14px;margin-bottom:10px">'
            f'<strong>Day1ソリューション:</strong> {e(sc.get("day1_solution",""))}</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">'
            f'<div><strong style="color:#dc2626">主な課題</strong>{list_items(chal if isinstance(chal, list) else [chal])}</div>'
            f'<div><strong style="color:#16a34a">教訓</strong>{list_items(lessons if isinstance(lessons, list) else [lessons])}</div>'
            f'</div>'
        )

    # Day1 checklist
    checklist = data.get("day1_checklist", [])
    ck_rows = []
    for item in checklist:
        if isinstance(item, dict):
            pri = item.get("priority", "")
            ck_rows.append([
                e(item.get("item", "")),
                badge(pri, "red" if pri == "must" else "orange" if pri == "should" else "gray"),
                e(item.get("typical_solution", "")),
                e(item.get("time_required", "")),
            ])
    ck_html = '<h2>✅ Day1チェックリスト</h2>' + table(["項目", "優先度", "典型的解決策", "所要時間"], ck_rows)

    # Failure patterns
    fps = data.get("failure_patterns", [])
    fp_items = "".join(
        card(
            f'<strong style="color:#dc2626">{e(fp.get("pattern",""))}</strong>'
            f'<p style="margin:6px 0 3px;font-size:.87rem"><strong>原因:</strong> {e(fp.get("cause",""))}</p>'
            f'<p style="margin:0 0 3px;font-size:.87rem"><strong>結果:</strong> {e(fp.get("consequence",""))}</p>'
            f'<p style="margin:0;font-size:.87rem"><strong>予防:</strong> {e(fp.get("prevention",""))}</p>',
            border_left_color="#dc2626"
        )
        for fp in fps
    )
    fp_html = f'<h2>⚠️ 失敗パターン</h2><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px">{fp_items}</div>'

    content = ov_html + phases_html + sc_html + ck_html + fp_html
    return section_wrap("sec-ma", "🤝 M&A アイデンティティ統合", content)


# ── 6. VPN / SASE ──────────────────────────────────────────────────────────────

def build_vpn_sase():
    data = load("05_hybrid_scenarios/vpn_sase_identity.json")

    html_parts = []

    # Traditional VPN
    tvpn = data.get("traditional_vpn", {})
    vpn_products = tvpn.get("products", [])
    prod_cards = "".join(
        card(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
            f'<strong>{e(vp.get("product",""))}</strong>'
            f'{badge("Legacy", "orange")}'
            f'<span style="color:#64748b;font-size:.82rem">{e(vp.get("vendor",""))}</span>'
            f'</div>'
            f'<p style="margin:0 0 4px;font-size:.87rem"><strong>認証:</strong> {e(", ".join(vp.get("auth_protocols",[])))}</p>'
            f'<p style="margin:0 0 4px;font-size:.87rem"><strong>AD連携:</strong> {e(vp.get("ad_integration",""))}</p>'
            f'<p style="margin:0;font-size:.87rem"><strong>MFA:</strong> {e(vp.get("mfa_support",""))}</p>'
        )
        for vp in vpn_products
    )
    html_parts.append(f'<h2>🔒 従来型VPN</h2>')
    if tvpn.get("problems"):
        probs = tvpn["problems"]
        html_parts.append(card(
            f'<strong style="color:#dc2626">⚠️ VPNの問題点</strong>'
            + list_items(probs if isinstance(probs, list) else [probs])
        ))
    html_parts.append(f'<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px">{prod_cards}</div>')

    # SASE
    sase = data.get("sase", {})
    sase_vendors = sase.get("vendors", [])
    sv_cards = "".join(
        card(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
            f'<strong>{e(sv.get("product",""))}</strong>'
            f'{badge("Modern", "green")}'
            f'<span style="color:#64748b;font-size:.82rem">{e(sv.get("vendor",""))}</span>'
            f'</div>'
            f'<p style="margin:0 0 4px;font-size:.83rem">{e(sv.get("japan_availability",""))}</p>'
            f'<p style="margin:0 0 4px;font-size:.83rem"><strong>ID連携:</strong> {e(sv.get("id_integration",""))}</p>'
            + list_items(sv.get("strengths", []))
        )
        for sv in sase_vendors
    )
    html_parts.append(f'<h2>☁️ SASE</h2>')
    if sase.get("definition"):
        html_parts.append(card(f'<p style="margin:0">{e(sase["definition"])}</p>',
                              extra_style="background:#f0f9ff;border:1px solid #bae6fd"))
    html_parts.append(f'<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px">{sv_cards}</div>')

    # ZTNA
    ztna = data.get("ztna", {})
    ztna_products = ztna.get("products", [])
    ztna_concept = e(ztna.get("concept", ""))
    ztna_html = (
        f'<h2>🛡️ ZTNA</h2>'
        + card(f'<p style="margin:0">{ztna_concept}</p>')
    )
    if ztna_products:
        if isinstance(ztna_products, list):
            zp_items = "".join(
                card(
                    f'<strong>{e(zp.get("product","") if isinstance(zp, dict) else str(zp))}</strong>'
                    + (f'<p style="margin:4px 0 0;font-size:.87rem">{e(zp.get("notes",""))}</p>'
                       if isinstance(zp, dict) and zp.get("notes") else "")
                )
                for zp in ztna_products[:6]
            )
            ztna_html += f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">{zp_items}</div>'
    html_parts.append(ztna_html)

    # ID integration patterns (list of strings)
    patterns = data.get("id_integration_patterns", [])
    if patterns:
        pat_items = "".join(
            card(f'<p style="margin:0">🔗 {e(p)}</p>')
            for p in patterns if isinstance(p, str)
        )
        html_parts.append(f'<h2>🔄 ID統合パターン</h2>{pat_items}')

    content = "".join(html_parts)
    return section_wrap("sec-vpn-sase", "🌐 VPN・SASE とアイデンティティ", content)


# ── 7. IdP Comparison ──────────────────────────────────────────────────────────

def build_idp():
    data = load("03_identity_architecture/idp_comparison.json")
    products = data.get("products", [])

    html_parts = []
    for p in products:
        feats = p.get("features", {})
        tier = p.get("tier", "")
        tier_color = "purple" if "enterprise" in tier.lower() else "blue" if "standard" in tier.lower() else "gray"

        feat_rows = []
        feat_map = {
            "sso_protocols": "SSOプロトコル",
            "mfa_methods": "MFA方式",
            "passwordless": "パスワードレス",
            "directory_features": "ディレクトリ機能",
            "on_prem_integration": "オンプレ連携",
            "saas_connectors": "SaaSコネクタ",
        }
        for fk, flabel in feat_map.items():
            fval = feats.get(fk, [])
            if isinstance(fval, list):
                fval_str = ", ".join(str(v) for v in fval[:5])
            else:
                fval_str = str(fval)
            if fval_str:
                feat_rows.append(f'<tr><td style="padding:3px 8px;color:#64748b;font-size:.8rem">{e(flabel)}</td>'
                                  f'<td style="padding:3px 8px;font-size:.8rem">{e(fval_str)}</td></tr>')

        strengths = p.get("strengths", [])
        str_badges = " ".join(badge(s, "green") for s in (strengths if isinstance(strengths, list) else [strengths])[:5])

        html_parts.append(card(
            f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;flex-wrap:wrap">'
            f'<h3 style="margin:0;color:#1e293b">{e(p.get("name",""))}</h3>'
            f'{badge(tier, tier_color)}'
            f'<span style="color:#64748b;font-size:.85rem">{e(p.get("vendor",""))}</span>'
            f'{badge("日本GA" if p.get("japan_ga") else "未GA", "green" if p.get("japan_ga") else "orange")}'
            f'</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">'
            f'<div><table style="width:100%;border-collapse:collapse">{"".join(feat_rows)}</table></div>'
            f'<div>'
            f'<p style="margin:0 0 6px;font-size:.85rem"><strong>日本向けノート:</strong> {e(p.get("japan_notes",""))}</p>'
            f'<p style="margin:0;font-size:.82rem"><strong>強み: </strong>{str_badges}</p>'
            f'</div></div>'
        ))

    content = "".join(html_parts)
    return section_wrap("sec-idp", "🔐 IdP製品比較", content)


# ── 8. PAM Comparison ──────────────────────────────────────────────────────────

def build_pam():
    data = load("03_identity_architecture/pam_tool_comparison.json")
    products = data.get("products", [])

    html_parts = []
    for p in products:
        str_tags = p.get("strength_tags", [])
        wo_tags = p.get("watchout_tags", [])
        str_html = " ".join(badge(t, "green") for t in (str_tags if isinstance(str_tags, list) else [str_tags])[:6])
        wo_html = " ".join(badge(t, "orange") for t in (wo_tags if isinstance(wo_tags, list) else [wo_tags])[:6])
        cost = p.get("indicative_entry_cost_band", "")
        dm = p.get("deployment_models", [])

        html_parts.append(card(
            f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;flex-wrap:wrap">'
            f'<h3 style="margin:0;color:#1e293b">{e(p.get("label",""))}</h3>'
            f'<span style="color:#64748b;font-size:.85rem">{e(p.get("vendor",""))}</span>'
            f'{badge(cost, "purple") if cost else ""}'
            f'</div>'
            f'<p style="margin:0 0 8px;font-size:.9rem">{e(p.get("summary",""))}</p>'
            f'<p style="margin:0 0 4px;font-size:.83rem"><strong>デプロイ: </strong>{e(", ".join(dm if isinstance(dm, list) else [str(dm)]))}</p>'
            f'<p style="margin:0 0 4px;font-size:.83rem"><strong>日本市場: </strong>{e(p.get("japan_market",""))}</p>'
            f'<div style="margin-top:8px"><strong style="font-size:.82rem">強み: </strong>{str_html}</div>'
            f'<div style="margin-top:4px"><strong style="font-size:.82rem">注意点: </strong>{wo_html}</div>'
        ))

    content = "".join(html_parts)
    return section_wrap("sec-pam", "🔑 PAM製品比較", content)


# ── 9. IAM Matrix ──────────────────────────────────────────────────────────────

def build_iam_matrix():
    data = load("03_identity_architecture/iam_capability_product_matrix.json")
    categories = data.get("capability_categories", [])
    products = data.get("products", [])

    # Category overview
    cat_items = "".join(
        card(
            f'<strong>{e(c.get("name",""))}</strong>'
            f'<p style="margin:4px 0 0;font-size:.85rem;color:#475569">{e(c.get("description",""))}</p>'
        )
        for c in categories
    )
    cats_html = (
        f'<h2>📋 ケイパビリティカテゴリ</h2>'
        f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:20px">{cat_items}</div>'
    )

    # Matrix table
    cat_ids = [c["category_id"] for c in categories]
    cat_names = [c["name"] for c in categories]

    score_sym = {
        "native": ("●", "score-native"),
        "strong": ("◎", "score-strong"),
        "partial": ("△", "score-partial"),
        "none": ("−", "score-none"),
        "limited": ("△", "score-partial"),
        "addon": ("＋", "score-partial"),
    }

    headers = ["製品", "ベンダー"] + cat_names
    rows = []
    for prod in products:
        caps = prod.get("capabilities", {})
        cells = [e(prod.get("name", "")), e(prod.get("vendor", ""))]
        for cid in cat_ids:
            cap = caps.get(cid, {})
            if isinstance(cap, dict):
                score = cap.get("score", "none").lower()
                notes = cap.get("notes", "")
            else:
                score = str(cap).lower()
                notes = ""
            sym, cls = score_sym.get(score, ("?", ""))
            cells.append(
                f'<span class="{cls}" title="{e(notes)}" style="cursor:help;font-size:1rem">{sym}</span>'
            )
        rows.append(cells)

    matrix_html = (
        f'<h2>📊 製品 × ケイパビリティマトリクス</h2>'
        f'<p style="font-size:.82rem;color:#64748b">● ネイティブ対応 ◎ 強い ＋ アドオン △ 一部対応 − 非対応 ※セルにカーソルで詳細</p>'
        + table(headers, rows)
    )

    content = cats_html + matrix_html
    return section_wrap("sec-iam-matrix", "📊 IAM ケイパビリティマトリクス", content)


# ── 10. LDAP Comparison ────────────────────────────────────────────────────────

def build_ldap():
    data = load("04_server_auth/ldap_directory_comparison.json")
    products = data.get("products", [])
    depr = data.get("rhel_openldap_deprecation", {})

    # RHEL OpenLDAP alert
    alert_html = ""
    if depr:
        alert_html = (
            f'<div class="callout-red">'
            f'<strong>🚨 RHEL OpenLDAP廃止について</strong><br>'
            f'<p style="margin:6px 0 0">{e(depr.get("impact",""))}</p>'
            + list_items(depr.get("migration_options", []))
            + f'</div>'
        )

    prod_html = ""
    for p in products:
        rhel = p.get("rhel_support", "")
        rhel_ok = "deprecated" not in str(rhel).lower() and "なし" not in str(rhel).lower()
        rhel_badge = badge(rhel[:40] if len(str(rhel)) > 40 else rhel,
                           "green" if rhel_ok else "red")
        strengths = p.get("strengths", [])
        weaknesses = p.get("weaknesses", [])

        prod_html += card(
            f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;flex-wrap:wrap">'
            f'<h3 style="margin:0;color:#1e293b">{e(p.get("name",""))}</h3>'
            f'<span style="color:#64748b;font-size:.85rem">{e(p.get("vendor",""))}</span>'
            f'{badge(p.get("license",""), "gray")}'
            f'{badge(p.get("eol_risk","low"), severity_color(p.get("eol_risk","low")))}'
            f'</div>'
            f'<p style="margin:0 0 6px;font-size:.88rem">{e(p.get("description",""))}</p>'
            f'<p style="margin:0 0 8px;font-size:.82rem"><strong>RHEL対応:</strong> {rhel_badge}</p>'
            f'<p style="margin:0 0 4px;font-size:.82rem"><strong>日本での採用:</strong> {e(p.get("japan_adoption",""))}</p>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px">'
            f'<div><strong style="color:#16a34a;font-size:.82rem">強み</strong>'
            + list_items(strengths if isinstance(strengths, list) else [strengths])
            + f'</div><div><strong style="color:#dc2626;font-size:.82rem">弱点</strong>'
            + list_items(weaknesses if isinstance(weaknesses, list) else [weaknesses])
            + f'</div></div>'
        )

    content = alert_html + prod_html
    return section_wrap("sec-ldap", "📂 LDAPディレクトリ比較", content)


# ── 11. OS Lifecycle ───────────────────────────────────────────────────────────

def build_os_lifecycle():
    data = load("10_lifecycle/os_lifecycle_id_tools.json")
    entries = data.get("os_entries", [])

    # 2029 alert
    alert = (
        f'<div style="background:#fef3c7;border:1px solid #fbbf24;border-radius:8px;'
        f'padding:12px 16px;margin-bottom:20px">'
        f'⚠️ <strong>2029年問題:</strong> Windows Server 2019 / Windows 10 など主要OSの延長サポートが終了します。'
        f'早期のリプレース計画が必要です。</div>'
    )

    rows = []
    for entry in sorted(entries, key=lambda x: x.get("extended_support_end", "") or ""):
        status = entry.get("support_status_as_of", "")
        eol = "eol" in status.lower() or "end" in status.lower()
        expiring = "expiring" in status.lower() or "warning" in status.lower()

        row_style = ""
        if eol:
            row_style = "background:#fef2f2"
        elif expiring:
            row_style = "background:#fffbeb"

        status_badge = badge(status,
                             "red" if eol else "orange" if expiring else "green")

        rows.append((row_style, [
            e(entry.get("os_name", "")),
            e(entry.get("vendor", "")),
            e(entry.get("mainstream_support_end", "")),
            e(entry.get("extended_support_end", "")),
            status_badge,
            badge("利用可" if entry.get("esu_available") else "なし",
                  "blue" if entry.get("esu_available") else "gray"),
            e(str(entry.get("id_management_impact", ""))[:80]),
        ]))

    # Build table with per-row styling
    headers = ["OS名", "ベンダー", "メインストリーム終了", "延長サポート終了", "現在のステータス", "ESU", "ID管理への影響"]
    th_html = "".join(
        f'<th style="background:#1e293b;color:#fff;padding:8px 12px;text-align:left;white-space:nowrap">{e(h)}</th>'
        for h in headers
    )
    body_html = ""
    for row_style, cells in rows:
        tds = "".join(
            f'<td style="padding:7px 12px;border-bottom:1px solid #e2e8f0;vertical-align:top;{row_style}">{cell}</td>'
            for cell in cells
        )
        body_html += f'<tr style="{row_style}">{tds}</tr>'

    tbl = (
        f'<div style="overflow-x:auto"><table style="border-collapse:collapse;width:100%;font-size:.85rem">'
        f'<thead><tr>{th_html}</tr></thead><tbody>{body_html}</tbody></table></div>'
    )

    content = alert + tbl
    return section_wrap("sec-os-lifecycle", "📅 OSライフサイクルとID管理", content)


# ── 12. Security Frameworks ────────────────────────────────────────────────────

def build_frameworks():
    data = load("07_migration_patterns/japan_security_frameworks.json")
    frameworks = data.get("frameworks", [])

    html_parts = []
    for fw in frameworks:
        reqs = fw.get("id_management_requirements", [])
        req_rows = []
        for r in reqs:
            if isinstance(r, dict):
                rel = r.get("id_relevance", "")
                req_rows.append([
                    e(r.get("requirement_id", "")),
                    e(r.get("title", "")),
                    e(str(r.get("content", ""))[:100] + ("..." if len(str(r.get("content",""))) > 100 else "")),
                    badge(rel, "red" if rel == "critical" else "orange" if rel == "high" else "blue"),
                ])
        req_tbl = table(["要件ID", "タイトル", "内容", "ID関連度"], req_rows) if req_rows else ""

        penalty = fw.get("penalty_non_compliance", "")
        html_parts.append(card(
            f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;flex-wrap:wrap">'
            f'<h3 style="margin:0;color:#1e293b">{e(fw.get("name",""))}</h3>'
            f'<span style="color:#64748b;font-size:.82rem">{e(fw.get("name_en",""))}</span>'
            f'{badge(fw.get("latest_version",""), "gray")}'
            f'{badge(fw.get("target_industry","全業種"), "blue")}'
            f'</div>'
            f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:10px;font-size:.85rem">'
            f'<div><strong>発行者:</strong> {e(fw.get("issuer",""))}</div>'
            f'<div><strong>対象:</strong> {e(fw.get("target_scale",""))}</div>'
            f'<div><strong>法的根拠:</strong> {e(fw.get("legal_basis",""))}</div>'
            f'</div>'
            f'{req_tbl}'
            + (f'<p style="margin:6px 0 0;font-size:.83rem;color:#dc2626">'
               f'<strong>非遵守ペナルティ:</strong> {e(penalty)}</p>' if penalty else "")
        ))

    content = "".join(html_parts)
    return section_wrap("sec-frameworks", "⚖️ 日本セキュリティフレームワーク", content)


# ── 13. Scenarios ──────────────────────────────────────────────────────────────

INDUSTRY_LABELS = {
    "cross_industry": "🌐 全業種",
    "finance":        "🏦 金融",
    "securities":     "📈 証券",
    "manufacturing":  "🏭 製造",
    "energy":         "⚡ エネルギー",
    "healthcare":     "🏥 医療",
    "public":         "🏛️ 官公庁",
}

def build_scenarios():
    sim_files = sorted(glob.glob(str(BASE / "11_simulations/**/*.json"), recursive=True))

    # Group by industry
    by_industry = {}
    for fp in sim_files:
        industry = Path(fp).parent.name  # e.g. 'cross_industry'
        by_industry.setdefault(industry, []).append(fp)

    industries = list(by_industry.keys())

    # Tab buttons
    tab_btns = "".join(
        f'<button class="tab-btn{"" if i else " active"}" '
        f'onclick="showTab(\'scenarios-tabs\',\'tab-{ind}\')">'
        f'{INDUSTRY_LABELS.get(ind, ind)}</button>'
        for i, ind in enumerate(industries)
    )

    # Tab panels
    tab_panels = []
    for i, ind in enumerate(industries):
        files = by_industry[ind]
        panels_html = ""
        for fp in files:
            try:
                sim = json.load(open(fp, encoding="utf-8"))
            except Exception:
                continue

            meta = sim.get("metadata", {})
            title = meta.get("title", Path(fp).stem)
            personas = sim.get("personas", [])
            # Build persona map: id -> (name, role)
            persona_map = {p["id"]: p for p in personas}

            # Determine "right-aligned" roles (SE/consultant side)
            right_roles = {"SIer提案SE", "SIer営業部長", "NSSol SE", "コンサルタント",
                           "提案SE", "SE", "営業", "NSSolコンサルタント"}

            # Persona chips
            chip_html = " ".join(
                f'<span style="background:#e2e8f0;border-radius:20px;padding:3px 10px;'
                f'font-size:.78rem;margin-right:4px">'
                f'{e(p.get("name",""))}<span style="color:#64748b"> / {e(p.get("role",""))}</span></span>'
                for p in personas
            )

            # Scenes
            scenes_html = ""
            for scene in sim.get("scenes", []):
                dia_html = ""
                for dl in scene.get("dialogue", []):
                    speaker_id = dl.get("speaker", "")
                    persona = persona_map.get(speaker_id, {})
                    name = persona.get("name", speaker_id)
                    role = persona.get("role", "")
                    text = dl.get("text", "")
                    subtext = dl.get("subtext", "")
                    is_right = role in right_roles or "SE" in role or "SIer" in role

                    align_class = "dialogue-right" if is_right else "dialogue-left"
                    margin_style = "margin-left:auto" if is_right else ""

                    dia_html += (
                        f'<div style="margin-bottom:10px">'
                        f'<div class="speaker-label" style="text-align:{"right" if is_right else "left"}">'
                        f'{e(name)} / {e(role)}</div>'
                        f'<div class="{align_class}" style="{margin_style}">'
                        f'{e(text)}'
                        + (f'<div class="subtext">{e(subtext)}</div>' if subtext else "")
                        + f'</div></div>'
                    )

                issues = scene.get("issues_surfaced", [])
                scenes_html += (
                    f'<div style="margin-bottom:16px">'
                    f'<h4 style="margin:0 0 6px;color:#1e293b">{e(scene.get("title",""))}</h4>'
                    f'<p style="margin:0 0 8px;font-size:.82rem;color:#64748b">{e(scene.get("setting",""))}</p>'
                    f'{dia_html}'
                    + (f'<div style="background:#fefce8;border-radius:6px;padding:8px 12px;margin-top:8px;font-size:.82rem">'
                       f'<strong>論点:</strong> {e(", ".join(issues))}</div>' if issues else "")
                    + f'</div>'
                )

            # Gap analysis
            gap = sim.get("gap_analysis", [])
            gap_rows = []
            for g in gap:
                pri = g.get("priority", "")
                gap_rows.append([
                    e(g.get("category", "")),
                    e(g.get("current", "")),
                    e(g.get("target", "")),
                    e(g.get("gap", "")),
                    badge(pri, severity_color(pri)),
                ])
            gap_html = table(["カテゴリ", "現状", "目標", "ギャップ", "優先度"], gap_rows) if gap_rows else ""

            panels_html += card(
                f'<h3 style="margin:0 0 10px;color:#1e293b">{e(title)}</h3>'
                f'<div style="margin-bottom:12px">{chip_html}</div>'
                f'{scenes_html}'
                + (f'<h4 style="margin:16px 0 8px;color:#1e293b">📊 ギャップ分析</h4>{gap_html}' if gap_html else "")
            )

        active = "active" if i == 0 else ""
        tab_panels.append(
            f'<div id="tab-{ind}" class="tab-panel {active}">{panels_html}</div>'
        )

    content = (
        f'<div id="scenarios-tabs" style="margin-bottom:20px">'
        f'<div style="margin-bottom:0">{tab_btns}</div>'
        f'<div style="background:#fff;border-radius:0 8px 8px 8px;box-shadow:0 1px 4px rgba(0,0,0,.1);padding:20px">'
        + "".join(tab_panels)
        + f'</div></div>'
    )
    return section_wrap("sec-scenarios", "🎭 シナリオ対話", content)


# ── 14. Industry: Finance ──────────────────────────────────────────────────────

def build_industry_finance():
    d = load("02_industries/identity_finance.json")
    parts = [f'<p style="color:#475569;margin-bottom:20px">{e(d.get("overview",""))}</p>']

    reg = d.get("regulatory_landscape", {})
    fws = reg.get("frameworks", [])
    if fws:
        parts.append('<h2>📜 規制フレームワーク</h2>')
        for fw in fws:
            reqs = fw.get("key_id_requirements", fw.get("key_requirements", []))
            req_html = "".join(f"<li>{e(r)}</li>" for r in reqs)
            penalty = fw.get("penalty", fw.get("penalty_non_compliance", ""))
            parts.append(card(
                f'<strong>{e(fw.get("name",""))}</strong>'
                + (f' <span style="color:#64748b;font-size:.82em">{e(fw.get("version",""))}</span>' if fw.get("version") else "")
                + f'<ul style="margin:6px 0 0;padding-left:18px;font-size:.88em">{req_html}</ul>'
                + (f'<p style="margin:6px 0 0;font-size:.82em;color:#991b1b">⚠️ 非準拠時: {e(str(penalty))}</p>' if penalty else ""),
                border_left_color="#8b5cf6"
            ))

    envs = d.get("typical_it_environments", [])
    if envs:
        parts.append('<h2>🏦 業態別IT環境</h2>')
        for env in envs:
            chars = "".join(f"<li>{e(c)}</li>" for c in env.get("characteristics", []))
            chs = "".join(f"<li>{e(c)}</li>" for c in env.get("id_challenges", []))
            parts.append(card(
                f'<strong style="font-size:1em">{e(env.get("segment",""))}</strong>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px">'
                f'<div><h4 style="font-size:.82em;color:#475569;margin-bottom:4px">システム構成</h4><ul style="padding-left:16px;font-size:.84em">{chars}</ul></div>'
                f'<div><h4 style="font-size:.82em;color:#991b1b;margin-bottom:4px">ID管理課題</h4><ul style="padding-left:16px;font-size:.84em;color:#991b1b">{chs}</ul></div>'
                f'</div>',
                border_left_color="#3b82f6"
            ))

    pam = d.get("privileged_access_management", {})
    if pam:
        tools = pam.get("common_tools_japan", [])
        cs = pam.get("case_study", {})
        parts.append(
            '<h2>🔑 特権アクセス管理（PAM）</h2>'
            + '<div style="margin-bottom:12px">'
            + "".join(badge(t, "purple") for t in tools)
            + "</div>"
        )
        if cs:
            parts.append(card(
                f'<strong>事例: {e(cs.get("bank_type",""))}</strong>'
                f'<p style="margin:5px 0;font-size:.88em"><strong>課題:</strong> {e(cs.get("challenge",""))}</p>'
                f'<p style="margin:5px 0;font-size:.88em"><strong>対策:</strong> {e(cs.get("solution",""))}</p>'
                f'<p style="margin:5px 0;font-size:.88em;color:#166534"><strong>効果:</strong> {e(cs.get("result",""))}</p>',
                border_left_color="#22c55e"
            ))

    return section_wrap("sec-industry-finance", "🏦 金融業のID管理", "".join(parts))


# ── 15. Industry: Manufacturing ───────────────────────────────────────────────

def build_industry_mfg():
    d = load("02_industries/identity_manufacturing.json")
    parts = [f'<p style="color:#475569;margin-bottom:20px">{e(d.get("overview",""))}</p>']

    env = d.get("typical_it_ot_environment", {})
    it_layer = env.get("it_layer", {})
    ot_layer = env.get("ot_layer", {})
    conv = env.get("convergence_zone", {})
    if it_layer or ot_layer:
        it_html = "".join(f"<li>{e(c)}</li>" for c in it_layer.get("components", []))
        ot_html = "".join(f"<li>{e(c)}</li>" for c in ot_layer.get("components", []))
        conv_html = "".join(f"<li>{e(c)}</li>" for c in conv.get("challenges", []))
        parts.append(
            '<h2>🏭 IT/OT環境</h2>'
            + '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">'
            + card(f'<h4>💻 IT層</h4><p style="font-size:.82em;color:#64748b">{e(it_layer.get("description",""))}</p><ul style="padding-left:14px;font-size:.84em">{it_html}</ul><p style="font-size:.82em;color:#64748b;margin-top:6px">{e(it_layer.get("id_management",""))}</p>', border_left_color="#3b82f6")
            + card(f'<h4>⚙️ OT層</h4><p style="font-size:.82em;color:#64748b">{e(ot_layer.get("description",""))}</p><ul style="padding-left:14px;font-size:.84em">{ot_html}</ul><p style="font-size:.82em;color:#ef4444;margin-top:6px">{e(ot_layer.get("id_management",""))}</p>', border_left_color="#f97316")
            + card(f'<h4>⚠️ IT/OT境界</h4><ul style="padding-left:14px;font-size:.84em;color:#991b1b">{conv_html}</ul>', border_left_color="#ef4444")
            + '</div>'
        )

    sap = d.get("sap_id_management", {})
    if sap:
        issues = sap.get("common_issues", [])
        tools = sap.get("governance_tools", [])
        iss_rows = "".join(
            f'<tr><td>{e(i.get("issue",""))}</td><td>{e(i.get("description",""))}</td>'
            f'<td>{badge(i.get("frequency",""), "orange" if i.get("frequency")=="非常に多い" else "yellow")}</td></tr>'
            for i in issues
        )
        parts.append(
            '<h2>💼 SAP ID管理</h2>'
            + f'<p style="margin-bottom:10px">{e(sap.get("overview",""))}</p>'
            + table(["問題", "説明", "頻度"], [])
            .replace("</tbody>", iss_rows + "</tbody>")
            + '<div style="margin:8px 0">' + "".join(badge(t, "blue") for t in tools) + "</div>"
        )

    sc = d.get("supply_chain_identity", {})
    if sc:
        patterns = sc.get("access_patterns", [])
        p_html = "".join(
            card(f'<strong>{e(p.get("pattern",""))}</strong><p style="font-size:.88em;margin-top:4px">{e(p.get("description",""))}</p>')
            for p in patterns
        )
        parts.append(f'<h2>🔗 サプライチェーンID管理</h2><p>{e(sc.get("overview",""))}</p>' + grid(p_html, cols=2))

    return section_wrap("sec-industry-mfg", "🏭 製造業のID管理", "".join(parts))


# ── 16. Industry: Energy ──────────────────────────────────────────────────────

def build_industry_energy():
    d = load("02_industries/identity_energy.json")
    parts = [f'<p style="color:#475569;margin-bottom:20px">{e(d.get("overview",""))}</p>']

    reqs = d.get("regulatory_requirements", [])
    if reqs:
        parts.append('<h2>📋 規制要件</h2>')
        for req in reqs:
            kr = req.get("key_requirements", [])
            kr_html = "".join(f"<li>{e(r)}</li>" for r in kr)
            parts.append(card(
                f'<strong>{e(req.get("name",""))}</strong>'
                + (f' <span style="color:#64748b;font-size:.82em">（{e(req.get("issuer",""))}）</span>' if req.get("issuer") else "")
                + f'<ul style="padding-left:16px;font-size:.85em;margin-top:6px">{kr_html}</ul>',
                border_left_color="#8b5cf6"
            ))

    challenges = d.get("unique_challenges", [])
    if challenges:
        parts.append('<h2>⚡ 固有の課題</h2>')
        rows = "".join(
            f'<tr><td><strong>{e(ch.get("challenge",""))}</strong></td>'
            f'<td style="font-size:.88em">{e(ch.get("description",""))}</td>'
            f'<td style="font-size:.88em;color:#166534">{e(ch.get("mitigation",""))}</td></tr>'
            for ch in challenges
        )
        parts.append(table(["課題", "詳細", "対策"], []).replace("</tbody>", rows + "</tbody>"))

    attacks = d.get("attack_case_studies", [])
    if attacks:
        parts.append('<h2>🔴 重大インシデント事例</h2>')
        for atk in attacks:
            parts.append(card(
                f'<strong style="color:#dc2626">{e(atk.get("title",""))}</strong>'
                f'<p style="margin:6px 0;font-size:.88em">{e(atk.get("description",""))}</p>'
                f'<p style="margin:4px 0;font-size:.85em;color:#1d4ed8">💡 ID教訓: {e(atk.get("id_lesson",""))}</p>',
                border_left_color="#ef4444"
            ))

    return section_wrap("sec-industry-energy", "⚡ エネルギー業のID管理", "".join(parts))


# ── 17. IGA Framework ─────────────────────────────────────────────────────────

def build_iga():
    d = load("09_iga/iga_framework.json")
    parts = [f'<p style="color:#475569;margin-bottom:20px">{e(d.get("overview",""))}</p>']

    comp = d.get("iga_vs_idm_vs_iam", {})
    if comp.get("comparison"):
        rows = "".join(
            f'<tr><td><strong>{e(c.get("term",""))}</strong></td><td>{e(c.get("focus",""))}</td>'
            f'<td>{e(c.get("scope",""))}</td><td>{badge(c.get("governance",""), "green" if c.get("governance")=="強い" else "yellow" if c.get("governance")=="中程度" else "gray")}</td></tr>'
            for c in comp["comparison"]
        )
        parts.append('<h2>📊 IDM / IAM / IGA の違い</h2>' + table(["用語", "フォーカス", "スコープ", "ガバナンス"], []).replace("</tbody>", rows + "</tbody>"))
        parts.append(f'<p style="background:#eff6ff;padding:10px 14px;border-radius:7px;margin-bottom:16px;font-size:.9em">{e(comp.get("driver",""))}</p>')

    caps = d.get("core_capabilities", [])
    if caps:
        parts.append('<h2>🔧 コア機能</h2>')
        for cap in caps:
            levels = cap.get("maturity_levels", [])
            issues = cap.get("common_issues", [])
            examples = cap.get("example_violations", [])
            inner = f'<p style="font-size:.88em;margin-bottom:6px">{e(cap.get("description",""))}</p>'
            if levels:
                inner += '<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:6px">'
                for lv in levels:
                    color = ["gray","yellow","orange","green","blue"][min(lv.get("level",0), 4)]
                    inner += f'<div style="flex:1;min-width:120px;background:#f8f9fc;border-radius:5px;padding:7px;font-size:.8em"><strong>Lv{lv.get("level","")}: {e(lv.get("name",""))}</strong><br><span style="color:#64748b">{e(lv.get("description",""))}</span></div>'
                inner += '</div>'
            if issues:
                inner += '<ul style="padding-left:16px;margin-top:6px;font-size:.85em;color:#991b1b">' + "".join(f"<li>{e(i)}</li>" for i in issues) + "</ul>"
            if examples:
                inner += '<ul style="padding-left:16px;margin-top:6px;font-size:.85em;color:#b45309">' + "".join(f"<li>{e(x)}</li>" for x in examples) + "</ul>"
            parts.append(card(f'<strong>{e(cap.get("capability",""))}</strong>' + inner, border_left_color="#3b82f6"))

    prods = d.get("product_comparison", [])
    if prods:
        parts.append('<h2>🛒 IGA製品比較</h2>')
        rows = "".join(
            f'<tr><td><strong>{e(p.get("product",""))}</strong><br><span style="color:#64748b;font-size:.8em">{e(p.get("vendor",""))}</span></td>'
            f'<td style="font-size:.85em">{e(p.get("strength",""))}</td>'
            f'<td style="font-size:.85em;color:#991b1b">{e(p.get("weakness",""))}</td>'
            f'<td style="font-size:.82em">{e(p.get("japan_adoption",""))}</td></tr>'
            for p in prods
        )
        parts.append(table(["製品名", "強み", "弱み", "日本採用"], []).replace("</tbody>", rows + "</tbody>"))

    kpis = d.get("kpis", [])
    if kpis:
        parts.append('<h2>📈 KPI指標</h2>')
        rows = "".join(
            f'<tr><td>{e(k.get("kpi",""))}</td><td><strong>{e(str(k.get("target","")))}</strong></td>'
            f'<td style="color:#d97706">{e(k.get("current_avg_japan",""))}</td></tr>'
            for k in kpis
        )
        parts.append(table(["KPI", "目標値", "現状（日本平均）"], []).replace("</tbody>", rows + "</tbody>"))

    return section_wrap("sec-iga", "🏛️ IGAフレームワーク", "".join(parts))


# ── 18. JML Process ───────────────────────────────────────────────────────────

def build_jml():
    d = load("09_iga/jml_process_design.json")
    parts = [f'<p style="color:#475569;margin-bottom:20px">{e(d.get("overview",""))}</p>']

    joiner = d.get("joiner_process", {})
    if joiner:
        tl = joiner.get("best_practice_timeline", [])
        tl_html = ""
        for step in tl:
            acts = "".join(f"<li>{e(a)}</li>" for a in step.get("actions", []))
            tl_html += f'<div style="border-left:3px solid #3b82f6;padding:8px 12px;margin-bottom:8px"><strong>{e(step.get("timing",""))}</strong><ul style="padding-left:14px;margin-top:4px;font-size:.85em">{acts}</ul></div>'
        fails = "".join(f"<li style='color:#991b1b'>{e(f)}</li>" for f in joiner.get("common_failures", []))
        parts.append(
            '<h2>➡️ Joiner（入社）</h2>'
            + f'<p style="background:#f0fdf4;padding:8px 12px;border-radius:6px;font-size:.88em">{e(joiner.get("trigger",""))}</p>'
            + tl_html
            + f'<ul style="padding-left:16px;font-size:.85em;margin-bottom:14px">{fails}</ul>'
        )

    mover = d.get("mover_process", {})
    if mover:
        principle = mover.get("key_principle", "")
        scenarios = mover.get("scenarios", [])
        sc_rows = "".join(
            f'<tr><td>{e(sc.get("scenario",""))}</td>'
            f'<td style="font-size:.84em">{e("; ".join(sc.get("actions",[])))}</td>'
            f'<td style="font-size:.84em;color:#b45309">{e(sc.get("risk",""))}</td></tr>'
            for sc in scenarios
        )
        parts.append(
            '<h2>🔄 Mover（異動）</h2>'
            + f'<p style="background:#fffbeb;padding:8px 12px;border-radius:6px;font-size:.9em;margin-bottom:10px">{e(principle)}</p>'
            + table(["シナリオ", "対応アクション", "リスク"], []).replace("</tbody>", sc_rows + "</tbody>")
        )

    leaver = d.get("leaver_process", {})
    if leaver:
        tl_data = leaver.get("recommended_timeline", {})
        fails = leaver.get("common_failures", [])
        fail_rows = "".join(
            f'<tr><td>{e(f.get("failure",""))}</td>'
            f'<td>{badge(f.get("prevalence",""), "red" if f.get("prevalence")=="非常に多い" else "orange")}</td>'
            f'<td style="font-size:.84em">{e(f.get("mitigation",""))}</td></tr>'
            for f in fails
        )
        parts.append(
            '<h2>⬅️ Leaver（退職）</h2>'
            + f'<p style="background:#fef2f2;padding:8px 12px;border-radius:6px;margin-bottom:10px;font-size:.9em"><strong>⚠️ 最重要プロセス：</strong> {e(leaver.get("criticality",""))}</p>'
            + '<h4>よくある失敗パターン</h4>'
            + table(["失敗", "頻度", "対策"], []).replace("</tbody>", fail_rows + "</tbody>")
        )

    hr = d.get("hr_it_integration", {})
    if hr:
        methods = hr.get("integration_methods", [])
        hris = hr.get("common_hris_japan", [])
        m_rows = "".join(
            f'<tr><td>{e(m.get("method",""))}</td><td style="color:#166534;font-size:.85em">{e(m.get("pros",""))}</td>'
            f'<td style="color:#991b1b;font-size:.85em">{e(m.get("cons",""))}</td>'
            f'<td>{badge(m.get("maturity",""), "green" if m.get("maturity")=="高" else "yellow" if m.get("maturity")=="中" else "gray")}</td></tr>'
            for m in methods
        )
        parts.append(
            '<h2>🔗 HR・IT連携</h2>'
            + f'<p style="margin-bottom:8px">{e(hr.get("overview",""))}</p>'
            + '<div style="margin-bottom:8px">' + "".join(badge(h, "teal") for h in hris) + "</div>"
            + table(["連携方式", "メリット", "デメリット", "成熟度"], []).replace("</tbody>", m_rows + "</tbody>")
        )

    return section_wrap("sec-jml", "🔄 JMLプロセス設計", "".join(parts))


# ── 19. Oracle Auth ───────────────────────────────────────────────────────────

def build_oracle():
    d = load("04_server_auth/oracle_database_auth.json")
    parts = [f'<p style="color:#475569;margin-bottom:20px">{e(d.get("overview",""))}</p>']

    id_types = d.get("oracle_id_types", [])
    if id_types:
        risk_color_map = {"高": "orange", "極高": "red", "低": "green", "低〜中": "yellow", "中": "yellow"}
        rows = "".join(
            f'<tr><td><strong>{e(t.get("type",""))}</strong></td>'
            f'<td style="font-size:.85em">{e(t.get("description",""))}</td>'
            f'<td>{badge(t.get("risk",""), risk_color_map.get(t.get("risk",""), "gray"))}</td></tr>'
            for t in id_types
        )
        parts.append('<h2>🔐 Oracle DBのIDタイプ</h2>' + table(["IDタイプ", "説明", "リスク"], []).replace("</tbody>", rows + "</tbody>"))

    pam = d.get("privileged_account_management", {})
    if pam:
        sys_sec = pam.get("sys_and_system", {})
        app_sec = pam.get("application_schemas", {})
        if sys_sec or app_sec:
            parts.append('<h2>🛡️ 特権アカウント管理</h2>')
        if sys_sec:
            bps = "".join(f"<li>{e(bp)}</li>" for bp in sys_sec.get("best_practices", []))
            parts.append(card(f'<strong>SYS / SYSTEM アカウント</strong><p style="font-size:.88em;margin:6px 0">{e(sys_sec.get("description",""))}</p><ul style="padding-left:14px;font-size:.85em">{bps}</ul>', border_left_color="#ef4444"))
        if app_sec:
            bps = "".join(f"<li>{e(bp)}</li>" for bp in app_sec.get("best_practices", []))
            parts.append(card(f'<strong>アプリケーションスキーマ</strong><p style="font-size:.88em;margin:6px 0">{e(app_sec.get("description",""))}</p><ul style="padding-left:14px;font-size:.85em">{bps}</ul>', border_left_color="#f97316"))

    audit = d.get("auditing", {})
    if audit:
        ua = audit.get("unified_auditing", {})
        dam = audit.get("database_activity_monitoring", {})
        siem = audit.get("siem_integration", {})
        parts.append('<h2>📋 監査・ログ管理</h2>')
        for title, sec in [("Unified Auditing", ua), ("Database Activity Monitoring (DAM)", dam), ("SIEM連携", siem)]:
            if sec:
                desc = sec.get("description", "")
                storage = sec.get("storage", "")
                parts.append(card(
                    f'<strong>{e(title)}</strong><p style="font-size:.88em;margin:5px 0">{e(desc)}</p>'
                    + (f'<p style="font-size:.82em;color:#64748b">格納先: {e(storage)}</p>' if storage else ""),
                    border_left_color="#3b82f6"
                ))

    ja = d.get("japan_adoption", {})
    if ja:
        users = ja.get("typical_users", [])
        parts.append('<h2>🇯🇵 日本市場での採用</h2>')
        parts.append(card(
            f'<p style="margin-bottom:8px">{e(ja.get("overview",""))}</p>'
            + '<ul style="padding-left:16px">' + "".join(f"<li>{e(u)}</li>" for u in users) + "</ul>"
        ))

    return section_wrap("sec-oracle", "🗄️ Oracle DB認証", "".join(parts))


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("Building sections…")
    sections = [
        build_ad_primer(),
        build_ad_legacy(),
        build_ransomware(),
        build_multi_forest(),
        build_ma(),
        build_vpn_sase(),
        build_idp(),
        build_pam(),
        build_iam_matrix(),
        build_ldap(),
        build_os_lifecycle(),
        build_frameworks(),
        build_iga(),
        build_jml(),
        build_industry_finance(),
        build_industry_mfg(),
        build_industry_energy(),
        build_oracle(),
        build_scenarios(),
    ]
    print("All sections built.")

    sidebar = build_sidebar()

    html_doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IDM参照ドキュメント — NSSol SE・営業向け</title>
<style>{CSS}</style>
</head>
<body>
{sidebar}
<div id="main">
{"".join(sections)}
</div>
<script>{JS}</script>
</body>
</html>"""

    out = BASE / "detail.html"
    out.write_text(html_doc, encoding="utf-8")
    size = out.stat().st_size
    print(f"Written: {out}")
    print(f"Size: {size:,} bytes ({size/1024:.1f} KB)")
    if size < 500_000:
        print("WARNING: file is smaller than expected 500KB")

if __name__ == "__main__":
    main()
