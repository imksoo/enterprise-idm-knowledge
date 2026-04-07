#!/usr/bin/env python3
"""
マルチビュー合成 HTML 生成フレームワーク
複数の JSON 知識ファイルを統合し、読者視点ごとに最適化した HTML を生成する。

Usage:
    python3 build_multiview.py
"""
import json
import os
import html as html_escape_module
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "02_html_decks" / "multiview"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TODAY = date.today().isoformat()

# =============================================================================
# ビュー設定
# =============================================================================
VIEW_CONFIG = {
    "exec": {
        "label": "役員・経営層向け",
        "color_primary": "#1a1a2e",
        "color_accent": "#f4a261",
        "color_bg": "#f8f4ee",
        "color_card": "#fff8f0",
        "icon": "👔",
        "reading_time": "5分",
        "tone": "経営判断・リスク・投資対効果",
    },
    "technical": {
        "label": "IT技術者・SE向け",
        "color_primary": "#1b4332",
        "color_accent": "#40c9a2",
        "color_bg": "#f0faf5",
        "color_card": "#e8f5ee",
        "icon": "⚙️",
        "reading_time": "30分",
        "tone": "設計・実装・製品比較・コマンド例",
    },
    "compliance": {
        "label": "監査・コンプライアンス担当者向け",
        "color_primary": "#3d0066",
        "color_accent": "#c77dff",
        "color_bg": "#f8f0ff",
        "color_card": "#f0e0ff",
        "icon": "📋",
        "reading_time": "25分",
        "tone": "規制対応・証跡要件・内部統制",
    },
    "sales": {
        "label": "営業・プリセールス向け",
        "color_primary": "#7c2d00",
        "color_accent": "#f59e0b",
        "color_bg": "#fffbf0",
        "color_card": "#fff3cd",
        "icon": "💼",
        "reading_time": "15分",
        "tone": "顧客課題・提案論理・競合ポジション",
    },
    "beginner": {
        "label": "非専門家・新任担当者向け",
        "color_primary": "#0f3460",
        "color_accent": "#4cc9f0",
        "color_bg": "#f0f8ff",
        "color_card": "#e0f0ff",
        "icon": "🌱",
        "reading_time": "10分",
        "tone": "入門・わかりやすい解説・最初のアクション",
    },
}

# =============================================================================
# JSON 読み込みとデータ統合
# =============================================================================

def load_json(path: Path) -> dict:
    """JSON ファイルを読み込む。存在しない場合は空 dict を返す。"""
    if not path.exists():
        print(f"  [SKIP] {path} が見つかりません")
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"  [ERROR] {path}: {e}")
        return {}


def _extract_nonstandard_knowledge(data: dict, source_title: str) -> tuple[list, list, list]:
    """非標準スキーマの JSON から nodes / knowledge / products を抽出する。"""
    nodes = []
    knowledge = []
    products = []

    # iga_framework.json 等: core_capabilities → knowledge
    for cap in data.get("core_capabilities", []):
        cap_name = cap.get("capability", "")
        desc = cap.get("description", "")
        knowledge.append({"topic": cap_name, "summary": desc, "_source": source_title})
        # maturity_levels → 追加ノード
        for ml in cap.get("maturity_levels", []):
            nodes.append({
                "id": f"ml_{cap_name}_{ml.get('level','')}",
                "label": f"{cap_name} - Lv{ml.get('level','')} {ml.get('name','')}",
                "object_type": "pattern",
                "description": ml.get("description", ""),
                "_source": source_title,
            })
        # common_issues → knowledge
        issues = cap.get("common_issues", [])
        if issues:
            knowledge.append({
                "topic": f"{cap_name} — よくある問題",
                "summary": " / ".join(issues),
                "_source": source_title,
            })

    # product_comparison → products
    for p in data.get("product_comparison", []):
        products.append({
            "name": p.get("product", ""),
            "vendor": p.get("vendor", ""),
            "strength": p.get("strength", ""),
            "weakness": p.get("weakness", ""),
            "japan_adoption": p.get("japan_adoption", ""),
            "_source": source_title,
        })

    # iga_vs_idm_vs_iam → knowledge
    compare_block = data.get("iga_vs_idm_vs_iam", {})
    if compare_block:
        terms = compare_block.get("comparison", [])
        if terms:
            summary = " | ".join(
                f"{t.get('term','')}: {t.get('focus','')} ({t.get('governance','')})" for t in terms
            )
            knowledge.append({
                "topic": "IDM / IAM / IGA の違い",
                "summary": summary + (" — " + compare_block.get("driver", "")) if compare_block.get("driver") else summary,
                "_source": source_title,
            })

    # implementation_phases → knowledge
    for phase in data.get("implementation_phases", []):
        knowledge.append({
            "topic": f"実装フェーズ {phase.get('phase','')}: {phase.get('name','')}",
            "summary": phase.get("description", "") + " 期間: " + str(phase.get("duration", "")),
            "_source": source_title,
        })

    # kpis → knowledge
    kpis = data.get("kpis", [])
    if kpis:
        kpi_summary = " / ".join(
            f"{k.get('kpi','')}: {k.get('target','')} ({k.get('measurement','')})" for k in kpis[:5]
        )
        knowledge.append({
            "topic": "主要 KPI（Key Performance Indicators）",
            "summary": kpi_summary,
            "_source": source_title,
        })

    # overview → knowledge
    if "overview" in data and not data.get("nodes"):
        knowledge.insert(0, {
            "topic": data.get("title", source_title),
            "summary": data.get("overview", ""),
            "_source": source_title,
        })

    # overview-based node
    if data.get("overview") and not data.get("nodes"):
        nodes.insert(0, {
            "id": "overview_node",
            "label": data.get("title", source_title),
            "object_type": "concept",
            "description": data.get("overview", ""),
            "_source": source_title,
        })

    return nodes, knowledge, products


def merge_json_files(file_paths: list[str]) -> dict:
    """複数の JSON ファイルを統合する。標準・非標準スキーマ両対応。"""
    merged = {
        "titles": [],
        "tags": [],
        "nodes": [],
        "edges": [],
        "knowledge": [],
        "products": [],          # iga_tool_comparison 等の product 配列
        "comparison_axes": [],
        "raw": [],               # 生データ保持
    }
    node_ids_seen = set()

    for rel_path in file_paths:
        full_path = BASE_DIR / rel_path
        data = load_json(full_path)
        if not data:
            continue

        merged["raw"].append(data)

        # タイトル・タグ取得（標準スキーマ優先、なければ直接キー）
        meta = data.get("metadata", {})
        title = meta.get("title") or data.get("title") or rel_path
        merged["titles"].append(title)
        merged["tags"].extend(meta.get("tags", []))

        # 標準スキーマのノード
        for node in data.get("nodes", []):
            node_id = f"{rel_path}::{node.get('id', '')}"
            if node_id not in node_ids_seen:
                node_ids_seen.add(node_id)
                merged["nodes"].append({**node, "_source": title})

        merged["edges"].extend(data.get("edges", []))
        merged["knowledge"].extend(data.get("knowledge", []))
        merged["products"].extend(data.get("products", []))
        merged["comparison_axes"].extend(data.get("comparison_axes", []))

        # 非標準スキーマから追加抽出
        ns_nodes, ns_knowledge, ns_products = _extract_nonstandard_knowledge(data, title)
        for node in ns_nodes:
            node_id = f"{rel_path}::ns::{node.get('id', '')}"
            if node_id not in node_ids_seen:
                node_ids_seen.add(node_id)
                merged["nodes"].append(node)
        merged["knowledge"].extend(ns_knowledge)
        merged["products"].extend(ns_products)

    merged["tags"] = list(dict.fromkeys(merged["tags"]))  # deduplicate
    return merged


# =============================================================================
# HTML ユーティリティ
# =============================================================================

def esc(text: str) -> str:
    return html_escape_module.escape(str(text))


def common_head(title: str, view: str) -> str:
    cfg = VIEW_CONFIG[view]
    primary = cfg["color_primary"]
    accent = cfg["color_accent"]
    bg = cfg["color_bg"]
    card = cfg["color_card"]
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} | {cfg['label']}</title>
<style>
  :root {{
    --primary: {primary};
    --accent: {accent};
    --bg: {bg};
    --card: {card};
    --text: #1a1a1a;
    --muted: #666;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: "Hiragino Kaku Gothic ProN", "Meiryo", "Yu Gothic", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
  }}
  header {{
    background: var(--primary);
    color: #fff;
    padding: 2rem;
    border-bottom: 4px solid var(--accent);
  }}
  header h1 {{ font-size: 1.8rem; margin-bottom: 0.3rem; }}
  header .view-badge {{
    display: inline-block;
    background: var(--accent);
    color: var(--primary);
    font-weight: bold;
    padding: 0.2rem 0.8rem;
    border-radius: 999px;
    font-size: 0.85rem;
    margin-bottom: 0.8rem;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }}
  .about-banner {{
    background: var(--card);
    border-left: 5px solid var(--accent);
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 2rem;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem 2rem;
  }}
  .about-banner h2 {{ grid-column: 1/-1; color: var(--primary); font-size: 1rem; margin-bottom: 0.5rem; }}
  .about-banner .item {{ font-size: 0.9rem; }}
  .about-banner .item strong {{ color: var(--primary); }}
  section {{
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 2rem;
    overflow: hidden;
  }}
  section .sec-header {{
    background: var(--primary);
    color: #fff;
    padding: 0.8rem 1.5rem;
    font-size: 1.1rem;
    font-weight: bold;
  }}
  section .sec-body {{ padding: 1.5rem; }}
  .highlight-box {{
    background: var(--card);
    border: 2px solid var(--accent);
    border-radius: 8px;
    padding: 1.2rem;
    margin-bottom: 1rem;
  }}
  .highlight-box h3 {{ color: var(--primary); margin-bottom: 0.5rem; font-size: 1rem; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
    margin-top: 0.5rem;
  }}
  th {{
    background: var(--primary);
    color: #fff;
    padding: 0.6rem 0.8rem;
    text-align: left;
  }}
  td {{
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid #e0e0e0;
    vertical-align: top;
  }}
  tr:nth-child(even) td {{ background: var(--bg); }}
  .tag {{
    display: inline-block;
    background: var(--accent);
    color: var(--primary);
    font-size: 0.75rem;
    padding: 0.1rem 0.5rem;
    border-radius: 4px;
    margin: 0.1rem;
    font-weight: bold;
  }}
  .node-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }}
  .node-card {{
    background: var(--card);
    border-radius: 8px;
    padding: 1rem;
    border-top: 3px solid var(--accent);
  }}
  .node-card h4 {{ color: var(--primary); margin-bottom: 0.4rem; font-size: 0.95rem; }}
  .node-card p {{ font-size: 0.88rem; color: var(--muted); }}
  .knowledge-item {{
    border-bottom: 1px solid #eee;
    padding: 1rem 0;
  }}
  .knowledge-item:last-child {{ border-bottom: none; }}
  .knowledge-item h4 {{ color: var(--primary); margin-bottom: 0.3rem; }}
  .knowledge-item p {{ font-size: 0.9rem; }}
  .checklist {{ list-style: none; padding: 0; }}
  .checklist li {{
    padding: 0.5rem 0.5rem 0.5rem 2rem;
    position: relative;
    border-bottom: 1px solid #eee;
    font-size: 0.92rem;
  }}
  .checklist li::before {{
    content: "☐";
    position: absolute;
    left: 0.3rem;
    color: var(--accent);
    font-size: 1.1rem;
  }}
  .sources {{
    font-size: 0.8rem;
    color: var(--muted);
    border-top: 1px solid #ddd;
    padding-top: 1rem;
    margin-top: 2rem;
  }}
  footer {{
    text-align: center;
    padding: 1.5rem;
    color: var(--muted);
    font-size: 0.8rem;
    border-top: 1px solid #ddd;
    margin-top: 2rem;
  }}
  @media (max-width: 600px) {{
    .about-banner {{ grid-template-columns: 1fr; }}
    .node-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
"""


def render_header(title: str, view: str, merged: dict) -> str:
    cfg = VIEW_CONFIG[view]
    tags_html = " ".join(f'<span class="tag">{esc(t)}</span>' for t in merged["tags"][:8])
    sources = " / ".join(esc(t) for t in merged["titles"])
    return f"""
<header>
  <div class="view-badge">{cfg['icon']} {esc(cfg['label'])}</div>
  <h1>{esc(title)}</h1>
  <div style="margin-top:0.5rem;font-size:0.85rem;opacity:0.8">
    データソース: {sources}
  </div>
  <div style="margin-top:0.5rem">{tags_html}</div>
</header>
"""


def render_about_banner(view: str, title: str, related_views: list[tuple]) -> str:
    cfg = VIEW_CONFIG[view]
    related_html = " | ".join(
        f'<a href="{esc(href)}" style="color:var(--accent)">{esc(label)}</a>'
        for label, href in related_views
    )
    view_descriptions = {
        "exec": "経営判断に必要なリスク・投資・決断ポイントが分かる",
        "technical": "設計・実装・製品選定に必要な技術詳細が分かる",
        "compliance": "規制対応・監査証跡・内部統制の要件が分かる",
        "sales": "顧客提案に使える課題整理・競合比較・提案構成が分かる",
        "beginner": "専門知識なしで基礎概念と最初の行動ステップが分かる",
    }
    return f"""
<div class="container">
  <div class="about-banner">
    <h2>📄 このドキュメントについて</h2>
    <div class="item"><strong>対象読者:</strong> {esc(cfg['label'])}</div>
    <div class="item"><strong>所要時間:</strong> {esc(cfg['reading_time'])}</div>
    <div class="item"><strong>このドキュメントで分かること:</strong> {view_descriptions[view]}</div>
    <div class="item"><strong>関連ビュー:</strong> {related_html if related_html else "—"}</div>
  </div>
"""


def render_footer(merged: dict) -> str:
    sources = "、".join(esc(t) for t in merged["titles"])
    return f"""
  <div class="sources">
    ソースデータ: {sources}<br>
    生成日: {TODAY} | ナレッジベース自動生成
  </div>
</div>
<footer>
  Enterprise IDM Knowledge Base — 本ドキュメントはナレッジベースから自動生成されています。最新情報は各製品公式ドキュメントを参照してください。
</footer>
</body>
</html>
"""


# =============================================================================
# ビュー別 HTML レンダラー
# =============================================================================

def render_exec(title: str, merged: dict, related_views: list[tuple]) -> str:
    """役員・経営層向けビュー"""
    nodes = merged["nodes"]
    knowledge = merged["knowledge"]

    risk_nodes = [n for n in nodes if n.get("object_type") == "risk"][:5]
    concept_nodes = [n for n in nodes if n.get("object_type") in ("concept", "pattern")][:6]

    decision_points = [k for k in knowledge if any(
        kw in k.get("topic", "") + k.get("summary", "")
        for kw in ["投資", "コスト", "費用", "リスク", "優先", "判断", "意思決定", "承認", "予算", "ビジネス"]
    )][:3]
    if not decision_points:
        decision_points = knowledge[:3]

    html = common_head(title, "exec")
    html += render_header(title, "exec", merged)
    html += render_about_banner("exec", title, related_views)

    # 今日決めてほしいこと
    html += '<section>'
    html += '<div class="sec-header">🎯 今日決めてほしいこと（3点）</div>'
    html += '<div class="sec-body">'
    decision_items = []
    for i, k in enumerate(decision_points[:3]):
        topic = k.get("topic", f"重要事項 {i+1}")
        summary = k.get("summary", "")
        summary_short = summary[:150] + ("…" if len(summary) > 150 else "")
        decision_items.append((topic, summary_short))
    if not decision_items:
        decision_items = [
            ("ID管理基盤への投資判断", "現状の認証基盤はセキュリティリスクを内包しており、早期対応が求められます。"),
            ("移行スケジュールの承認", "2029年サポート終了に向けた計画的な移行が必要です。"),
            ("セキュリティ予算の確保", "インシデント対応コストは予防投資の数倍に達するため、先行投資が合理的です。"),
        ]
    for i, (topic, summary) in enumerate(decision_items[:3]):
        html += f'''
        <div class="highlight-box">
          <h3>決断 {i+1}: {esc(topic)}</h3>
          <p>{esc(summary)}</p>
        </div>'''
    html += '</div></section>'

    # リスクサマリー
    html += '<section>'
    html += '<div class="sec-header">⚠️ 経営に直結するリスク</div>'
    html += '<div class="sec-body">'
    html += '<table><thead><tr><th>リスク</th><th>事業への影響</th><th>対応の緊急度</th></tr></thead><tbody>'
    risk_display = []
    if risk_nodes:
        for n in risk_nodes:
            risk_display.append((n.get("label", ""), n.get("description", ""), "高"))
    else:
        risk_kn = [k for k in knowledge if any(
            kw in k.get("topic", "") + k.get("summary", "")
            for kw in ["侵害", "漏洩", "攻撃", "被害", "インシデント", "リスク", "脆弱性", "停止"]
        )][:5]
        for k in risk_kn:
            risk_display.append((k.get("topic", ""), k.get("summary", "")[:100], "高"))
    if not risk_display:
        for k in knowledge[:3]:
            risk_display.append((k.get("topic", ""), k.get("summary", "")[:100], "中"))
    for label, desc, urgency in risk_display[:5]:
        html += f'<tr><td><strong>{esc(label)}</strong></td><td>{esc(desc[:120])}</td><td><span style="color:#e53e3e;font-weight:bold">{esc(urgency)}</span></td></tr>'
    html += '</tbody></table>'
    html += '''
    <div style="background:#fff5f5;border-left:4px solid #e53e3e;border-radius:0 8px 8px 0;padding:1rem;margin-top:1rem">
      <strong>💡 経営層への補足:</strong>
      ID管理の不備は「内部不正」「ランサムウェア」「情報漏洩」の全てに関連します。
      一つの脆弱なアカウントが侵害されるだけで、システム全体への横展開が起きるリスクがあります。
    </div>'''
    html += '</div></section>'

    # 投資対効果サマリー
    html += '<section>'
    html += '<div class="sec-header">💰 投資対効果の考え方</div>'
    html += '<div class="sec-body">'
    roi_knowledge = [k for k in knowledge if any(
        kw in k.get("topic", "") + k.get("summary", "")
        for kw in ["コスト", "投資", "効果", "ROI", "削減", "改善", "自動化", "効率"]
    )][:3]
    if not roi_knowledge:
        roi_knowledge = knowledge[:3]
    for k in roi_knowledge:
        html += f'''
        <div class="highlight-box">
          <h3>{esc(k.get("topic", ""))}</h3>
          <p>{esc(k.get("summary", ""))}</p>
        </div>'''
    html += '''
    <div style="overflow-x:auto;margin-top:1rem"><table>
      <thead><tr><th>シナリオ</th><th>コスト/損失規模</th><th>備考</th></tr></thead>
      <tbody>
        <tr><td>ランサムウェアインシデント（中規模企業）</td><td><strong>5,000万〜3億円</strong></td><td>身代金+復旧費+機会損失</td></tr>
        <tr><td>情報漏洩（個人情報）</td><td><strong>1件あたり最大1,000万円</strong></td><td>課徴金+被害者対応+信頼毀損</td></tr>
        <tr><td>内部不正による不正送金</td><td><strong>数百万〜数億円</strong></td><td>SOD未設定が主因</td></tr>
        <tr><td>ID管理自動化による削減効果</td><td><strong>年間500〜2,000万円</strong></td><td>IT工数削減+ヘルプデスク削減</td></tr>
        <tr><td>PAM導入による特権管理改善</td><td><strong>ROI 200〜400%（3年）</strong></td><td>Forrester Research 試算</td></tr>
      </tbody>
    </table></div>
    <div style="background:#fff3cd;border-radius:8px;padding:1rem;margin-top:1rem;border-left:4px solid #f59e0b">
      <strong>📌 経営判断のポイント:</strong>
      セキュリティインシデント1件あたりの平均対応コストは数億円規模に達します。
      ID管理基盤への先行投資は、インシデント発生時の損失額と比較すると合理的な選択です。
      「予防コスト」は「復旧コスト」の平均10分の1以下です。
    </div>'''
    html += '</div></section>'

    # 概要：何が課題で何をすべきか
    html += '<section>'
    html += '<div class="sec-header">📊 現状分析と対応方針</div>'
    html += '<div class="sec-body">'
    for node in concept_nodes[:4]:
        html += f'''
        <div style="margin-bottom:1.2rem;padding:1rem;border-radius:8px;background:var(--card)">
          <h3 style="color:var(--primary);margin-bottom:0.4rem">{esc(node.get("label", ""))}</h3>
          <p style="font-size:0.92rem">{esc(node.get("description", ""))}</p>
        </div>'''
    if not concept_nodes:
        for k in knowledge[:4]:
            html += f'''
            <div style="margin-bottom:1.2rem;padding:1rem;border-radius:8px;background:var(--card)">
              <h3 style="color:var(--primary);margin-bottom:0.4rem">{esc(k.get("topic", ""))}</h3>
              <p style="font-size:0.92rem">{esc(k.get("summary", ""))}</p>
            </div>'''
    html += '</div></section>'

    # 推奨ロードマップ
    html += '<section>'
    html += '<div class="sec-header">🗺️ 推奨対応ロードマップ</div>'
    html += '<div class="sec-body">'
    html += '<div style="overflow-x:auto"><table>'
    html += '<thead><tr><th>フェーズ</th><th>期間目安</th><th>主な取組み</th><th>期待効果</th></tr></thead><tbody>'
    roadmap = [
        ("フェーズ1: 現状把握・リスク評価", "1〜2ヶ月",
         "既存ID棚卸し・特権アカウント調査・セキュリティギャップ分析",
         "優先対応箇所の特定・リスク可視化"),
        ("フェーズ2: 緊急対応", "2〜4ヶ月",
         "MFA全適用・特権アカウント統制・退職者アカウント即時無効化",
         "高リスクの即時低減・インシデント発生確率の大幅削減"),
        ("フェーズ3: 基盤整備", "4〜12ヶ月",
         "ID管理ツール導入・自動プロビジョニング・クラウド移行計画策定",
         "運用効率化・コンプライアンス対応基盤の確立"),
        ("フェーズ4: 高度化・自動化", "12〜24ヶ月",
         "IGA導入・ゼロトラスト移行・AI活用によるリスク検知強化",
         "継続的なセキュリティ改善・先進的ID統治体制の確立"),
    ]
    for phase, duration, actions, effect in roadmap:
        html += f'''<tr>
          <td><strong>{esc(phase)}</strong></td>
          <td style="white-space:nowrap">{esc(duration)}</td>
          <td style="font-size:0.88rem">{esc(actions)}</td>
          <td style="font-size:0.88rem;color:#2d6a4f">{esc(effect)}</td>
        </tr>'''
    html += '</tbody></table></div></div></section>'

    # このテーマ固有の要点
    html += '<section>'
    html += '<div class="sec-header">🔑 このテーマの重要ポイント（技術詳細なし）</div>'
    html += '<div class="sec-body">'
    already_shown = set(id(k) for k in decision_points + roi_knowledge)
    exec_knowledge = [k for k in knowledge if id(k) not in already_shown][:8]
    if not exec_knowledge:
        exec_knowledge = knowledge[3:11]
    for k in exec_knowledge:
        topic = k.get("topic", "")
        summary = k.get("summary", "")
        summary_exec = summary[:200] + ("…（詳細は技術者向けビューを参照）" if len(summary) > 200 else "")
        if topic:
            html += f'''
            <div style="border-bottom:1px solid #eee;padding:0.8rem 0">
              <strong style="color:var(--primary)">{esc(topic)}</strong>
              <p style="font-size:0.9rem;margin-top:0.3rem">{esc(summary_exec)}</p>
            </div>'''
    html += '</div></section>'

    # 関連ノード概要（経営者向けに概念を示す）
    concept_all = [n for n in nodes if n.get("object_type") in ("concept", "pattern")]
    if concept_all:
        html += '<section>'
        html += '<div class="sec-header">🧩 主要コンセプト概要</div>'
        html += '<div class="sec-body"><div class="node-grid">'
        for node in concept_all[:6]:
            html += f'''
            <div class="node-card">
              <h4>{esc(node.get("label",""))}</h4>
              <p>{esc(node.get("description","")[:100])}</p>
            </div>'''
        html += '</div></div></section>'

    # Q&A（経営層がよく聞く質問）
    html += '<section>'
    html += '<div class="sec-header">❓ 経営層からよくある質問 Q&amp;A</div>'
    html += '<div class="sec-body">'
    qa_items = [
        ("「なぜ今このタイミングで？」",
         "Windows Server 2012/2016のサポート終了（2023〜2027年）と2029年問題が重なる「移行の最終機会」です。放置するほどリスクと移行コストが増大します。"),
        ("「クラウドに移行すれば安全になるのか？」",
         "クラウドは手段であり、ID管理の設計が不適切なら従来と同じリスクが残ります。重要なのは「誰が何にアクセスできるか」を正しく制御することです。"),
        ("「既存ベンダーに任せればよいのでは？」",
         "ID管理は全システムの「鍵管理」です。特定ベンダー依存は長期リスクになります。オープン標準ベースの設計で依存度を下げることが重要です。"),
        ("「何から始めればよいか？」",
         "まず「特権アカウントの棚卸し」と「退職者アカウントの確認」から着手できます。コストゼロで高リスクを即座に可視化できます。"),
        ("「セキュリティ投資は費用対効果が見えにくいのでは？」",
         "インシデント発生時のコスト（復旧・賠償・信頼毀損）と比較すれば定量化できます。保険料と同じ発想で、「発生確率×損失額」で評価することを推奨します。"),
    ]
    for q, a in qa_items:
        html += f'''
        <div style="margin-bottom:1.2rem">
          <div style="font-weight:bold;color:var(--primary);padding:0.5rem;background:var(--card);border-radius:6px 6px 0 0">{esc(q)}</div>
          <div style="padding:0.8rem;border:1px solid #e0e0e0;border-top:none;border-radius:0 0 6px 6px;font-size:0.92rem">{esc(a)}</div>
        </div>'''
    html += '</div></section>'

    html += render_footer(merged)
    return html


def render_technical(title: str, merged: dict, related_views: list[tuple]) -> str:
    """IT技術者・SE向けビュー"""
    nodes = merged["nodes"]
    knowledge = merged["knowledge"]
    products = merged["products"]

    html = common_head(title, "technical")
    html += render_header(title, "technical", merged)
    html += render_about_banner("technical", title, related_views)

    # アーキテクチャ概要（ノード一覧をタイプ別に整理）
    html += '<section>'
    html += '<div class="sec-header">🏗️ アーキテクチャ概要・コンポーネント</div>'
    html += '<div class="sec-body">'

    type_groups = {}
    for n in nodes:
        t = n.get("object_type", "other")
        type_groups.setdefault(t, []).append(n)

    for obj_type, type_nodes in type_groups.items():
        if not type_nodes:
            continue
        type_label = {
            "concept": "概念・設計原則",
            "product": "製品・ソリューション",
            "protocol": "プロトコル・標準",
            "risk": "リスク・脅威",
            "pattern": "設計パターン",
        }.get(obj_type, obj_type)
        html += f'<h3 style="margin:1rem 0 0.5rem;color:var(--primary);font-size:1rem">{esc(type_label)}</h3>'
        html += '<div class="node-grid">'
        for node in type_nodes[:8]:
            props = node.get("properties", {})
            props_html = ""
            if props:
                for k, v in list(props.items())[:3]:
                    if isinstance(v, list):
                        v = ", ".join(str(i) for i in v[:5])
                    props_html += f'<div style="font-size:0.8rem;color:#888;margin-top:0.2rem"><strong>{esc(k)}:</strong> {esc(str(v)[:60])}</div>'
            source_badge = f'<span style="font-size:0.75rem;color:#aaa">[{esc(node.get("_source","")[:20])}]</span>' if node.get("_source") else ""
            html += f'''
            <div class="node-card">
              <h4>{esc(node.get("label",""))}</h4>
              <p>{esc(node.get("description","")[:120])}</p>
              {props_html}
              {source_badge}
            </div>'''
        html += '</div>'
    html += '</div></section>'

    # 製品比較表
    if products:
        html += '<section>'
        html += '<div class="sec-header">📊 製品・ソリューション比較</div>'
        html += '<div class="sec-body">'
        # 全製品の属性キーを収集
        all_keys = set()
        for p in products:
            all_keys.update(p.keys())
        all_keys -= {"id", "name"}
        col_keys = sorted(all_keys)[:6]  # 最大6列
        html += '<div style="overflow-x:auto"><table><thead><tr>'
        html += '<th>製品名</th>'
        for k in col_keys:
            html += f'<th>{esc(k)}</th>'
        html += '</tr></thead><tbody>'
        for p in products[:12]:
            html += f'<tr><td><strong>{esc(p.get("name", p.get("id", "")))}</strong></td>'
            for k in col_keys:
                val = p.get(k, "—")
                if isinstance(val, list):
                    val = "<br>".join(esc(str(v)) for v in val[:3])
                elif isinstance(val, dict):
                    val = esc(str(val)[:80])
                else:
                    val = esc(str(val)[:80])
                html += f'<td>{val}</td>'
            html += '</tr>'
        html += '</tbody></table></div>'
        html += '</div></section>'
    else:
        # products が空の場合、ノードから product 型を表として整理
        prod_nodes = [n for n in nodes if n.get("object_type") == "product"]
        if prod_nodes:
            html += '<section>'
            html += '<div class="sec-header">📊 製品・ソリューション一覧</div>'
            html += '<div class="sec-body"><div style="overflow-x:auto"><table>'
            html += '<thead><tr><th>製品名</th><th>概要</th><th>ソース</th></tr></thead><tbody>'
            for p in prod_nodes[:15]:
                html += f'''<tr>
                  <td><strong>{esc(p.get("label",""))}</strong></td>
                  <td>{esc(p.get("description","")[:120])}</td>
                  <td style="font-size:0.8rem;color:#888">{esc(p.get("_source",""))}</td>
                </tr>'''
            html += '</tbody></table></div></div></section>'

    # 技術知識ベース
    html += '<section>'
    html += '<div class="sec-header">📚 技術知識・設計ポイント</div>'
    html += '<div class="sec-body">'
    for k in knowledge:
        html += f'''
        <div class="knowledge-item">
          <h4>{esc(k.get("topic",""))}</h4>
          <p>{esc(k.get("summary",""))}</p>
          {"<p style='margin-top:0.3rem'><strong>詳細:</strong> " + esc(k.get("detail","")[:200]) + "</p>" if k.get("detail") else ""}
        </div>'''
    if not knowledge:
        for n in nodes[:10]:
            html += f'''
            <div class="knowledge-item">
              <h4>{esc(n.get("label",""))}</h4>
              <p>{esc(n.get("description",""))}</p>
            </div>'''
    html += '</div></section>'

    # 実装ステップ
    html += '<section>'
    html += '<div class="sec-header">🔧 実装・設定ステップ</div>'
    html += '<div class="sec-body">'
    impl_knowledge = [k for k in knowledge if any(
        kw in k.get("topic", "") + k.get("summary", "")
        for kw in ["設定", "手順", "ステップ", "構成", "デプロイ", "インストール", "移行", "実装", "設計"]
    )]
    if not impl_knowledge:
        impl_knowledge = knowledge[:5]
    html += '<ol style="padding-left:1.5rem">'
    for i, k in enumerate(impl_knowledge[:8]):
        html += f'''
        <li style="margin-bottom:1rem">
          <strong>{esc(k.get("topic",""))}</strong>
          <p style="font-size:0.9rem;margin-top:0.3rem">{esc(k.get("summary",""))}</p>
        </li>'''
    html += '</ol>'

    # コマンド例（技術ビューのみ）
    html += '''
    <div style="background:#1a1a2e;color:#40c9a2;padding:1.2rem;border-radius:8px;margin-top:1.5rem;font-family:monospace;font-size:0.88rem">
      <div style="color:#f4a261;margin-bottom:0.5rem"># PowerShell / Entra CLI コマンド例</div>
      <div># Entra ID 条件付きアクセスポリシー確認</div>
      <div>Get-MgIdentityConditionalAccessPolicy | Format-Table DisplayName, State</div>
      <div style="margin-top:0.5rem"># Azure AD Connect 同期状態確認</div>
      <div>Get-ADSyncScheduler</div>
      <div style="margin-top:0.5rem"># 特権ロール割り当て一覧</div>
      <div>Get-MgRoleManagementDirectoryRoleAssignment | Where-Object {$_.PrincipalId -ne $null}</div>
      <div style="margin-top:0.5rem"># PAM セッション一覧（CyberArk CLI 例）</div>
      <div>Get-PVSession -safe "Windows_Domain_Admins"</div>
    </div>'''
    html += '</div></section>'

    # 評価軸 × 製品 比較マトリクス（comparison_axes がある場合）
    axes = merged["comparison_axes"]
    products_with_axes = [p for p in merged["products"] if "axes" in p or "label" in p]
    if axes and products_with_axes:
        html += '<section>'
        html += '<div class="sec-header">📐 評価軸 × 製品 詳細比較マトリクス</div>'
        html += '<div class="sec-body">'
        html += '<div style="overflow-x:auto"><table style="min-width:900px">'
        html += '<thead><tr><th style="min-width:200px">評価軸</th>'
        prod_names = []
        for p in products_with_axes[:6]:
            name = p.get("label") or p.get("name") or p.get("id", "")
            prod_names.append((name, p))
            html += f'<th style="min-width:120px">{esc(name[:30])}</th>'
        html += '</tr></thead><tbody>'
        assessment_colors = {"strong": "#2d6a4f", "moderate": "#856404", "weak": "#842029", "limited": "#842029"}
        assessment_labels = {"strong": "◎ 強", "moderate": "○ 中", "weak": "△ 弱", "limited": "× 限定"}
        for ax in axes[:12]:
            ax_id = ax.get("id", "")
            ax_label = ax.get("label", "")
            ax_desc = ax.get("description", "")
            html += f'<tr><td><strong>{esc(ax_label)}</strong><div style="font-size:0.78rem;color:#888;margin-top:0.2rem">{esc(ax_desc[:60])}</div></td>'
            for name, p in prod_names:
                ax_data = (p.get("axes") or {}).get(ax_id, {})
                assessment = ax_data.get("assessment", "—")
                note = ax_data.get("note", "")
                color = assessment_colors.get(assessment, "#555")
                label = assessment_labels.get(assessment, assessment)
                html += f'<td><span style="color:{color};font-weight:bold;font-size:0.85rem">{esc(label)}</span>'
                if note:
                    html += f'<div style="font-size:0.75rem;color:#666;margin-top:0.2rem">{esc(note[:80])}</div>'
                html += '</td>'
            html += '</tr>'
        html += '</tbody></table></div></div></section>'

    # エッジ（依存関係）
    if merged["edges"]:
        html += '<section>'
        html += '<div class="sec-header">🔗 コンポーネント依存関係・連携</div>'
        html += '<div class="sec-body"><div style="overflow-x:auto"><table>'
        html += '<thead><tr><th>From</th><th>関係</th><th>To</th><th>説明</th></tr></thead><tbody>'
        for e in merged["edges"][:20]:
            html += f'''<tr>
              <td>{esc(e.get("from",""))}</td>
              <td><span class="tag">{esc(e.get("relationship",""))}</span></td>
              <td>{esc(e.get("to",""))}</td>
              <td style="font-size:0.85rem">{esc(e.get("description",""))}</td>
            </tr>'''
        html += '</tbody></table></div></div></section>'

    # トラブルシューティング・設計上の注意点
    html += '<section>'
    html += '<div class="sec-header">🔧 トラブルシューティング・設計上の注意点</div>'
    html += '<div class="sec-body">'
    trouble_knowledge = [k for k in knowledge if any(
        kw in k.get("topic", "") + k.get("summary", "")
        for kw in ["問題", "注意", "失敗", "エラー", "課題", "リスク", "制約", "制限", "よくある"]
    )][:5]
    if not trouble_knowledge:
        trouble_knowledge = knowledge[-5:] if len(knowledge) > 5 else knowledge
    html += '<div style="overflow-x:auto"><table>'
    html += '<thead><tr><th>症状・問題</th><th>原因・背景</th><th>対応方法</th></tr></thead><tbody>'
    for k in trouble_knowledge:
        topic = k.get("topic", "")
        summary = k.get("summary", "")
        mid = len(summary) // 2
        html += f'''<tr>
          <td><strong>{esc(topic)}</strong></td>
          <td style="font-size:0.85rem">{esc(summary[:mid])}</td>
          <td style="font-size:0.85rem">{esc(summary[mid:mid+100])}</td>
        </tr>'''
    if not trouble_knowledge:
        html += '<tr><td colspan="3">詳細な技術者向けビューでは JSON ソースを直接参照してください。</td></tr>'
    html += '</tbody></table></div></div></section>'

    html += render_footer(merged)
    return html


def render_compliance(title: str, merged: dict, related_views: list[tuple]) -> str:
    """監査・コンプライアンス向けビュー"""
    nodes = merged["nodes"]
    knowledge = merged["knowledge"]

    html = common_head(title, "compliance")
    html += render_header(title, "compliance", merged)
    html += render_about_banner("compliance", title, related_views)

    # 規制対応マトリクス
    html += '<section>'
    html += '<div class="sec-header">📜 規制対応マトリクス</div>'
    html += '<div class="sec-body">'
    html += '<div style="overflow-x:auto"><table>'
    html += '<thead><tr><th>規制・フレームワーク</th><th>対応要件</th><th>証跡・ログ</th><th>対応状況</th></tr></thead><tbody>'
    regulations = [
        ("個人情報保護法 (改正)", "アクセスログ取得・本人確認強化・第三者提供記録", "アクセスログ90日以上保存、権限変更記録", "要確認"),
        ("NISC サイバーセキュリティガイドライン", "特権アカウント管理・多要素認証・ログ監視", "特権操作ログ1年保存、MFA適用証跡", "対応必須"),
        ("ISMS (ISO 27001)", "アクセス制御方針・レビュー手順・インシデント管理", "四半期レビュー記録・インシデント対応記録", "要整備"),
        ("PCI DSS v4.0", "最小権限原則・定期アクセスレビュー・ログ保存", "アクセスログ12ヶ月保存・四半期棚卸し", "対応必須"),
        ("SOC 2 Type II", "認証・認可制御の継続的監視・変更管理", "変更承認記録・定期テスト記録", "要確認"),
        ("金融庁 システム管理基準", "ID・パスワード管理・特権ID管理・操作ログ", "管理者操作ログ3年保存", "金融機関必須"),
    ]
    for reg, req, evidence, status in regulations:
        color = "#e53e3e" if status == "対応必須" else ("#f59e0b" if status == "要確認" else "#38a169")
        html += f'''<tr>
          <td><strong>{esc(reg)}</strong></td>
          <td style="font-size:0.88rem">{esc(req)}</td>
          <td style="font-size:0.88rem">{esc(evidence)}</td>
          <td><span style="color:{color};font-weight:bold">{esc(status)}</span></td>
        </tr>'''
    html += '</tbody></table></div></div></section>'

    # 監査証跡の保存要件
    html += '<section>'
    html += '<div class="sec-header">🗄️ 監査証跡・ログ保存要件</div>'
    html += '<div class="sec-body">'
    html += '<div style="overflow-x:auto"><table>'
    html += '<thead><tr><th>ログ種別</th><th>保存期間</th><th>保存形式</th><th>アクセス制御</th></tr></thead><tbody>'
    log_reqs = [
        ("認証ログ（成功・失敗）", "1年以上", "SIEM転送・改ざん防止署名付き", "セキュリティ担当のみ閲覧"),
        ("特権操作ログ", "3年以上", "不変ストレージ（Write-Once）", "CISO承認者のみ閲覧"),
        ("ID プロビジョニング変更ログ", "5年以上", "JSON/CSV 構造化ログ", "監査担当・管理者"),
        ("アクセスレビュー記録", "5年以上", "電子署名付き PDF + 原本", "コンプライアンス担当"),
        ("インシデント対応記録", "7年以上", "タイムスタンプ付きドキュメント", "法務・CISO"),
        ("MFA 登録・変更ログ", "1年以上", "IdP ネイティブログ", "IT管理者・セキュリティ担当"),
    ]
    for log_type, period, fmt, access in log_reqs:
        html += f'''<tr>
          <td><strong>{esc(log_type)}</strong></td>
          <td>{esc(period)}</td>
          <td style="font-size:0.85rem">{esc(fmt)}</td>
          <td style="font-size:0.85rem">{esc(access)}</td>
        </tr>'''
    html += '</tbody></table></div></div></section>'

    # 技術知識の コンプライアンス観点整理
    html += '<section>'
    html += '<div class="sec-header">🔍 コンプライアンス観点での技術要件</div>'
    html += '<div class="sec-body">'
    for k in knowledge[:12]:
        html += f'''
        <div class="knowledge-item">
          <h4>{esc(k.get("topic",""))}</h4>
          <p>{esc(k.get("summary",""))}</p>
        </div>'''
    if not knowledge:
        for n in nodes[:8]:
            html += f'''
            <div class="knowledge-item">
              <h4>{esc(n.get("label",""))}</h4>
              <p>{esc(n.get("description",""))}</p>
            </div>'''
    html += '</div></section>'

    # ノードベースのコンプライアンス要件詳細
    html += '<section>'
    html += '<div class="sec-header">🔐 コンポーネント別コンプライアンス要件</div>'
    html += '<div class="sec-body"><div style="overflow-x:auto"><table>'
    html += '<thead><tr><th>コンポーネント</th><th>種別</th><th>コンプライアンス要件</th></tr></thead><tbody>'
    for n in nodes[:10]:
        n_label = n.get("label", "")
        n_type = n.get("object_type", "")
        n_desc = n.get("description", "")
        if n_label:
            html += f'''<tr>
              <td><strong>{esc(n_label)}</strong></td>
              <td><span class="tag">{esc(n_type)}</span></td>
              <td style="font-size:0.85rem">{esc(n_desc[:150])}</td>
            </tr>'''
    html += '</tbody></table></div></div></section>'

    # 定期棚卸し・レビュー手順
    html += '<section>'
    html += '<div class="sec-header">📅 定期棚卸し・レビュースケジュール</div>'
    html += '<div class="sec-body">'
    html += '<div style="overflow-x:auto"><table>'
    html += '<thead><tr><th>レビュー項目</th><th>頻度</th><th>担当</th><th>証跡</th></tr></thead><tbody>'
    reviews = [
        ("特権アカウント棚卸し", "月次", "セキュリティ担当・IT管理者", "棚卸しシート・承認記録"),
        ("一般ユーザーアクセスレビュー", "四半期", "部門マネージャー + IT", "承認済み権限リスト"),
        ("サービスアカウント棚卸し", "半期", "IT管理者", "アカウント棚卸し台帳"),
        ("MFA 適用状況確認", "月次", "セキュリティ担当", "MFA非適用アカウントレポート"),
        ("ゲスト・外部ユーザーレビュー", "四半期", "部門担当・IT", "ゲストアカウント棚卸し"),
        ("ポリシー・手順書レビュー", "年次", "CISO・コンプライアンス担当", "改訂履歴・承認記録"),
        ("インシデント対応訓練", "年次", "全IT部門", "訓練実施記録・改善報告"),
    ]
    for item, freq, owner, evidence in reviews:
        html += f'''<tr>
          <td><strong>{esc(item)}</strong></td>
          <td>{esc(freq)}</td>
          <td style="font-size:0.85rem">{esc(owner)}</td>
          <td style="font-size:0.85rem">{esc(evidence)}</td>
        </tr>'''
    html += '</tbody></table></div></div></section>'

    # 内部統制チェックリスト
    html += '<section>'
    html += '<div class="sec-header">✅ 内部統制チェックリスト</div>'
    html += '<div class="sec-body">'
    checklists = [
        "すべての特権アカウントが登録・文書化されているか",
        "退職者・異動者のアカウントが即時無効化される手順があるか",
        "アクセスレビューの結果が文書化・保存されているか",
        "多要素認証（MFA）が管理者アカウントに必須適用されているか",
        "ログが改ざん防止ストレージに保存されているか",
        "特権操作に承認ワークフロー（4Eyes原則）が適用されているか",
        "インシデント対応手順が最新化・訓練済みか",
        "外部ベンダーのアクセス権が業務終了後に即時回収されているか",
        "パスワードポリシーが規定通りに適用されているか",
        "セキュリティイベントの SIEM アラートが設定・監視されているか",
    ]
    html += '<ul class="checklist">'
    for item in checklists:
        html += f'<li>{esc(item)}</li>'
    # knowledge から追加チェック項目を生成
    for k in knowledge[:5]:
        topic = k.get("topic", "")
        if topic:
            html += f'<li>[{esc(merged["titles"][0] if merged["titles"] else "")}] {esc(topic)} の管理手順が文書化されているか</li>'
    html += '</ul></div></section>'

    # リスクマトリクス（ナレッジから）
    html += '<section>'
    html += '<div class="sec-header">🎯 リスクアセスメントマトリクス</div>'
    html += '<div class="sec-body">'
    html += '<div style="overflow-x:auto"><table>'
    html += '<thead><tr><th>リスク項目</th><th>発生可能性</th><th>影響度</th><th>リスクレベル</th><th>対応要件</th></tr></thead><tbody>'
    risk_matrix = [
        ("特権アカウントの不正利用", "高", "最大", "🔴 Critical", "PAM導入・最小権限原則・セッション録画"),
        ("退職者アカウントの放置", "中", "高", "🔴 High", "HR連携自動無効化・定期棚卸し"),
        ("過剰なアクセス権付与", "高", "中", "🟠 Medium", "四半期レビュー・RBAC整理"),
        ("弱い認証（パスワードのみ）", "高", "高", "🔴 High", "MFA必須化・PAWの導入"),
        ("サービスアカウントの野放し", "高", "高", "🔴 High", "棚卸し・証明書化・Managed ID"),
        ("監査ログの欠落・改ざん", "中", "最大", "🔴 Critical", "不変ストレージ・SIEM連携"),
        ("外部ベンダーのアクセス管理不備", "中", "高", "🟠 Medium", "Just-In-Time・セッション制限"),
        ("SOD違反（職務分離未設定）", "中", "高", "🟠 Medium", "IGA導入・自動検知・四半期是正"),
    ]
    for item, prob, impact, level, req in risk_matrix:
        html += f'''<tr>
          <td><strong>{esc(item)}</strong></td>
          <td style="text-align:center">{esc(prob)}</td>
          <td style="text-align:center">{esc(impact)}</td>
          <td style="text-align:center">{level}</td>
          <td style="font-size:0.85rem">{esc(req)}</td>
        </tr>'''
    html += '</tbody></table></div></div></section>'

    # ナレッジベース由来のコンプライアンス要件
    html += '<section>'
    html += '<div class="sec-header">📋 知識ベース由来のコンプライアンス要件</div>'
    html += '<div class="sec-body">'
    for k in knowledge[8:16]:
        html += f'''
        <div class="knowledge-item">
          <h4>{esc(k.get("topic",""))}</h4>
          <p>{esc(k.get("summary",""))}</p>
        </div>'''
    if len(knowledge) < 8:
        for n in nodes[:5]:
            html += f'''
            <div class="knowledge-item">
              <h4>{esc(n.get("label",""))}</h4>
              <p>{esc(n.get("description",""))}</p>
            </div>'''
    html += '</div></section>'

    # 証跡収集・レポーティング方法
    html += '<section>'
    html += '<div class="sec-header">📊 証跡収集・コンプライアンスレポーティング</div>'
    html += '<div class="sec-body">'
    html += '<div style="overflow-x:auto"><table>'
    html += '<thead><tr><th>ツール/製品</th><th>収集できる証跡</th><th>レポート形式</th></tr></thead><tbody>'
    reporting_tools = [
        ("Microsoft Entra ID", "サインインログ・監査ログ・リスクイベント・条件付きアクセス", "CSV/JSON エクスポート・Azure Monitor"),
        ("Active Directory", "Security Event Log (4624/4625/4648 等)", "Windows Event Forwarding・SIEM"),
        ("CyberArk PAM", "特権セッション録画・コマンドログ・チェックアウト記録", "XML/CSV・Vault報告書"),
        ("SailPoint IGA", "アクセスレビュー結果・SOD違反・プロビジョニング履歴", "自動化証跡レポート"),
        ("Microsoft Sentinel", "統合ログ・アラート・インシデント対応記録", "KQL クエリ・Workbook"),
        ("Splunk SIEM", "全ログ統合・コンプライアンスダッシュボード", "Compliance Report App"),
    ]
    for tool, evidence, fmt in reporting_tools:
        html += f'''<tr>
          <td><strong>{esc(tool)}</strong></td>
          <td style="font-size:0.85rem">{esc(evidence)}</td>
          <td style="font-size:0.85rem">{esc(fmt)}</td>
        </tr>'''
    html += '</tbody></table></div></div></section>'

    html += render_footer(merged)
    return html


def render_sales(title: str, merged: dict, related_views: list[tuple]) -> str:
    """営業・プリセールス向けビュー"""
    nodes = merged["nodes"]
    knowledge = merged["knowledge"]

    html = common_head(title, "sales")
    html += render_header(title, "sales", merged)
    html += render_about_banner("sales", title, related_views)

    # 顧客ヒアリングチェックリスト
    html += '<section>'
    html += '<div class="sec-header">🎤 顧客ヒアリングチェックリスト（現状把握）</div>'
    html += '<div class="sec-body">'
    hearing_items = [
        ("インフラ現状", [
            "Active Directory（AD）のドメイン数・サイト数は？",
            "Windows Server / Linux サーバーの台数・バージョンは？",
            "クラウドサービス（Azure / M365 / AWS）の利用状況は？",
            "現在のID管理ツール（MIM/IDM製品など）は何を使用中？",
        ]),
        ("セキュリティ現状", [
            "特権アカウントの管理方法（PAMツール導入済みか？）",
            "MFA（多要素認証）の適用範囲は？",
            "最近のセキュリティインシデント（ヒヤリハット含む）はあるか？",
            "ランサムウェア対策・EDRの導入状況は？",
        ]),
        ("課題・懸念", [
            "2029年Windows Server EOLへの対応計画は？",
            "退職者・異動者のアカウント棚卸しはどう行っているか？",
            "監査・コンプライアンス対応で困っていることは？",
            "ID管理の運用工数・人員配置は？",
        ]),
        ("予算・意思決定", [
            "セキュリティ・ID管理の年間予算規模は？",
            "意思決定者は誰か（CISO/CIO/情シス部長）？",
            "導入検討のタイムラインは？",
            "既存ベンダー・SIerとの契約状況は？",
        ]),
    ]
    for category, questions in hearing_items:
        html += f'<h3 style="margin:1rem 0 0.5rem;color:var(--primary)">{esc(category)}</h3>'
        html += '<ul class="checklist">'
        for q in questions:
            html += f'<li>{esc(q)}</li>'
        html += '</ul>'

    # 知識ベースからの追加ヒアリング項目
    html += '<h3 style="margin:1rem 0 0.5rem;color:var(--primary)">このテーマ固有の確認事項</h3>'
    html += '<ul class="checklist">'
    for k in knowledge[:5]:
        topic = k.get("topic", "")
        if topic:
            html += f'<li>{esc(topic)} に関する現状・課題は？</li>'
    html += '</ul></div></section>'

    # よくある「NO」と切り返し
    html += '<section>'
    html += '<div class="sec-header">🔄 よくある「NO」と切り返しトーク</div>'
    html += '<div class="sec-body">'
    objections = [
        (
            "「今すぐ変える必要はない」",
            "2029年のWindows Server EOLまでに移行しなければ、サポート終了後のセキュリティリスクが急増します。計画的に始めるほど移行コストを抑えられます。",
        ),
        (
            "「予算がない」",
            "インシデント1件の対応コストは数千万〜数億円。予防投資との比較で経営層に提案できます。補助金・SECURITY ACTION制度も活用可能です。",
        ),
        (
            "「既存システムで十分」",
            "攻撃者は認証の弱点を狙います。現在の設定が最新の攻撃手法（Pass-the-Hash等）に対して有効かどうか、無料アセスメントで確認できます。",
        ),
        (
            "「人手が足りない」",
            "むしろ、ID管理の自動化・クラウド移行で運用工数を削減できます。現状の手動対応の工数を計算し、ROIを示すことが効果的です。",
        ),
        (
            "「ベンダーロックインが心配」",
            "オープン標準（SAML/OIDC/SCIM）ベースの設計を採用することで、ロックインリスクを最小化できます。",
        ),
    ]
    for objection, counter in objections:
        html += f'''
        <div class="highlight-box" style="margin-bottom:1rem">
          <h3 style="color:#7c2d00">顧客の声: {esc(objection)}</h3>
          <p><strong>切り返し:</strong> {esc(counter)}</p>
        </div>'''
    html += '</div></section>'

    # 提案書の構成テンプレート
    html += '<section>'
    html += '<div class="sec-header">📄 提案書構成テンプレート</div>'
    html += '<div class="sec-body">'
    html += '<ol style="padding-left:1.5rem">'
    proposal_sections = [
        ("エグゼクティブサマリー（1枚）", "現状の課題・推奨対応・投資対効果の概要"),
        ("現状分析（2〜3枚）", "ヒアリング結果に基づく課題整理・リスクマップ"),
        ("ソリューション概要（3〜4枚）", "提案するソリューション・アーキテクチャ図・主要機能"),
        ("製品比較・選定理由（1〜2枚）", "競合との比較表・推奨理由・PoC結果"),
        ("実装ロードマップ（2枚）", "フェーズ計画・マイルストーン・リソース要件"),
        ("費用・投資対効果（1〜2枚）", "初期費用・ランニングコスト・ROI試算"),
        ("リスクと緩和策（1枚）", "導入リスク・依存関係・移行時の注意点"),
        ("サポート・保守体制（1枚）", "実装支援・運用支援・SLA"),
        ("次のステップ（1枚）", "PoC提案・契約条件・スケジュール確認"),
    ]
    for section, desc in proposal_sections:
        html += f'<li style="margin-bottom:0.8rem"><strong>{esc(section)}</strong><br><span style="font-size:0.9rem;color:#666">{esc(desc)}</span></li>'
    html += '</ol></div></section>'

    # 競合ポジション・差別化ポイント（ノードから抽出）
    html += '<section>'
    html += '<div class="sec-header">🏆 競合ポジション・差別化ポイント</div>'
    html += '<div class="sec-body">'
    html += '<div class="node-grid">'
    prod_nodes = [n for n in nodes if n.get("object_type") == "product"][:6]
    if not prod_nodes:
        prod_nodes = nodes[:6]
    for node in prod_nodes:
        html += f'''
        <div class="node-card">
          <h4>{esc(node.get("label",""))}</h4>
          <p>{esc(node.get("description","")[:120])}</p>
        </div>'''
    html += '</div></div></section>'

    html += render_footer(merged)
    return html


def render_beginner(title: str, merged: dict, related_views: list[tuple]) -> str:
    """非専門家・新任担当者向けビュー"""
    nodes = merged["nodes"]
    knowledge = merged["knowledge"]

    html = common_head(title, "beginner")
    html += render_header(title, "beginner", merged)
    html += render_about_banner("beginner", title, related_views)

    # なぜ知らないとヤバいか
    html += '<section>'
    html += '<div class="sec-header">🚨 これを知らないとヤバい理由</div>'
    html += '<div class="sec-body">'
    html += '''
    <div class="highlight-box" style="border-color:#e53e3e">
      <h3 style="color:#e53e3e">💡 日常語で理解するリスク</h3>
      <p>会社のコンピュータシステムへの「鍵（パスワード・アカウント）」を正しく管理しないと、
         外部の攻撃者に侵入されたり、退職した元社員が無断でアクセスし続けたりするリスクがあります。
         これは「玄関の鍵を交換しないまま退去者に鍵を持たせ続ける」のと同じ状態です。</p>
    </div>'''
    risk_knowledge = [k for k in knowledge if any(
        kw in k.get("topic", "") + k.get("summary", "")
        for kw in ["侵害", "攻撃", "漏洩", "リスク", "被害", "脆弱性"]
    )][:3]
    if not risk_knowledge:
        risk_knowledge = knowledge[:3]
    for k in risk_knowledge:
        html += f'''
        <div style="padding:1rem;border-radius:8px;background:var(--card);margin-top:0.8rem">
          <strong>{esc(k.get("topic",""))}</strong>
          <p style="margin-top:0.3rem;font-size:0.92rem">{esc(k.get("summary",""))}</p>
        </div>'''
    html += '</div></section>'

    # 用語解説
    html += '<section>'
    html += '<div class="sec-header">📖 専門用語をわかりやすく</div>'
    html += '<div class="sec-body">'
    html += '<div style="overflow-x:auto"><table>'
    html += '<thead><tr><th>専門用語</th><th>わかりやすい言い換え</th></tr></thead><tbody>'
    glossary = [
        ("Active Directory (AD)", "会社全体のユーザーアカウントや権限を管理する「社員名簿＋鍵管理台帳」"),
        ("Entra ID", "クラウド版のAD。インターネット経由でアカウント管理ができる"),
        ("MFA（多要素認証）", "ログイン時にパスワード＋スマホ認証など2つ以上の確認を行うこと"),
        ("PAM（特権アクセス管理）", "システム管理者の強力な権限を厳重に管理し、使用時に記録を残す仕組み"),
        ("SSO（シングルサインオン）", "一度ログインすれば複数のサービスを使い回せる仕組み"),
        ("ゼロトラスト", "社内ネットワークにいても全員を一度疑って確認する考え方（城壁を作らない）"),
        ("プロビジョニング", "新入社員のアカウントを自動的に作成・設定すること"),
        ("デプロビジョニング", "退職者のアカウントを自動的に停止・削除すること"),
        ("SAML / OIDC", "異なるシステム間でログイン情報を安全に受け渡すための規格"),
        ("インシデント", "セキュリティ上の問題が発生した事態（情報漏えい・不正アクセスなど）"),
    ]
    for term, explanation in glossary:
        html += f'<tr><td><strong>{esc(term)}</strong></td><td>{esc(explanation)}</td></tr>'
    # ノードから追加用語を生成
    for node in nodes[:5]:
        label = node.get("label", "")
        desc = node.get("description", "")
        if label and desc:
            html += f'<tr><td><strong>{esc(label)}</strong></td><td>{esc(desc[:80])}</td></tr>'
    html += '</tbody></table></div></div></section>'

    # まず今週やること
    html += '<section>'
    html += '<div class="sec-header">✅ まず今週やること（アクションリスト）</div>'
    html += '<div class="sec-body">'
    actions = [
        "自分のアカウントのパスワードを強力なものに変更し、MFAを設定する",
        "部門の特権アカウント（管理者アカウント）の一覧を確認し、不要なものを洗い出す",
        "退職・異動した人のアカウントが残っていないかIT担当に確認する",
        "直近のセキュリティインシデント報告書（あれば）を読む",
        "担当製品の最新パッチ・アップデートの適用状況を確認する",
        "「情報セキュリティポリシー」を読み、自分の役割を確認する",
    ]
    html += '<ul class="checklist">'
    for action in actions:
        html += f'<li>{esc(action)}</li>'
    html += '</ul>'
    html += '''
    <div style="background:var(--card);border-radius:8px;padding:1rem;margin-top:1rem">
      <strong>📚 学習ロードマップ（1ヶ月）</strong>
      <ol style="padding-left:1.5rem;margin-top:0.5rem">
        <li style="margin-bottom:0.5rem"><strong>Week 1:</strong> MFA・SSO・パスワード管理の基礎を学ぶ</li>
        <li style="margin-bottom:0.5rem"><strong>Week 2:</strong> Active Directory / Entra ID の役割を理解する</li>
        <li style="margin-bottom:0.5rem"><strong>Week 3:</strong> 自社のID管理ツールを実際に触ってみる</li>
        <li><strong>Week 4:</strong> セキュリティインシデント対応手順を確認・訓練する</li>
      </ol>
    </div>'''
    html += '</div></section>'

    # 基礎知識（knowledge ベース）
    html += '<section>'
    html += '<div class="sec-header">💡 押さえておきたい基礎知識</div>'
    html += '<div class="sec-body">'
    for k in knowledge[:6]:
        html += f'''
        <div class="knowledge-item">
          <h4>{esc(k.get("topic",""))}</h4>
          <p>{esc(k.get("summary",""))}</p>
        </div>'''
    if not knowledge:
        for n in nodes[:6]:
            html += f'''
            <div class="knowledge-item">
              <h4>{esc(n.get("label",""))}</h4>
              <p>{esc(n.get("description",""))}</p>
            </div>'''
    html += '</div></section>'

    html += render_footer(merged)
    return html


# =============================================================================
# ビュー別ディスパッチ
# =============================================================================

RENDERERS = {
    "exec": render_exec,
    "technical": render_technical,
    "compliance": render_compliance,
    "sales": render_sales,
    "beginner": render_beginner,
}


def generate_html(
    base_title: str,
    file_key: str,
    view: str,
    source_files: list[str],
    all_views_for_topic: dict[str, str],
) -> None:
    """HTML を生成してファイルに書き込む。"""
    output_filename = f"{file_key}_{view}.html"
    output_path = OUTPUT_DIR / output_filename

    print(f"  生成中: {output_filename}")
    merged = merge_json_files(source_files)

    if not merged["titles"]:
        print(f"  [WARN] ソースデータが空です。スキップ: {output_filename}")
        return

    # 関連ビューのリンク（同トピックの他ビュー）
    related_views = [
        (f"{VIEW_CONFIG[v]['icon']} {VIEW_CONFIG[v]['label']}", f"{file_key}_{v}.html")
        for v, fname in all_views_for_topic.items()
        if v != view
    ]

    cfg = VIEW_CONFIG[view]
    renderer = RENDERERS[view]
    html_content = renderer(base_title, merged, related_views)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    size_kb = output_path.stat().st_size / 1024
    print(f"  -> {output_path.name} ({size_kb:.1f} KB)")


# =============================================================================
# 合成定義
# =============================================================================

SYNTHESIS_DEFINITIONS = [
    # A. ランサムウェア × ID 統合防御
    {
        "base_title": "ランサムウェア×ID統合防御ガイド",
        "file_key": "ransomware_id_defense",
        "views": ["exec", "technical", "sales"],
        "source_files": [
            "06_security_hardening/ransomware_defense.json",
            "06_security_hardening/privileged_access_management.json",
            "06_security_hardening/ransomware_id_attack_scenarios.json",
        ],
    },
    # B. IGA 完全ガイド
    {
        "base_title": "IGA（Identity Governance & Administration）完全ガイド",
        "file_key": "iga_complete",
        "views": ["exec", "technical", "compliance"],
        "source_files": [
            "09_iga/iga_framework.json",
            "09_iga/jml_process_design.json",
            "03_identity_architecture/iga_tool_comparison.json",
            "10_lifecycle/hr_lifecycle.json",
        ],
    },
    # C. AD モダナイゼーション × 2029 年問題
    {
        "base_title": "ADモダナイゼーション × 2029年問題対応ガイド",
        "file_key": "ad_modernization_2029",
        "views": ["exec", "technical", "sales"],
        "source_files": [
            "03_identity_architecture/identity_landscape.json",
            "05_hybrid_scenarios/entra_hybrid_join.json",
            "07_migration_patterns/ad_to_entra_migration.json",
            "07_migration_patterns/legacy_modernization.json",
        ],
    },
    # D. 外部 ID 管理トータルガイド
    {
        "base_title": "外部ID管理トータルガイド（B2B・サプライチェーン）",
        "file_key": "external_id_total",
        "views": ["technical", "compliance", "sales"],
        "source_files": [
            "09_external_connections/b2b_federation.json",
            "09_external_connections/supply_chain_security.json",
            "09_external_connections/b2b_partner_id.json",
            "06_security_hardening/privileged_access_management.json",
        ],
    },
    # E. M&A 後 ID 統合プレイブック
    {
        "base_title": "M&A後ID統合プレイブック",
        "file_key": "ma_id_playbook",
        "views": ["exec", "technical"],
        "source_files": [
            "07_migration_patterns/ad_to_entra_migration.json",
            "03_identity_architecture/multi_forest_consolidation.json",
            "10_lifecycle/id_ops_framework.json",
        ],
    },
]


# =============================================================================
# メイン
# =============================================================================

def main():
    print(f"=== マルチビュー合成 HTML 生成フレームワーク ===")
    print(f"出力先: {OUTPUT_DIR}")
    print()

    total = sum(len(d["views"]) for d in SYNTHESIS_DEFINITIONS)
    generated = 0

    for definition in SYNTHESIS_DEFINITIONS:
        base_title = definition["base_title"]
        file_key = definition["file_key"]
        views = definition["views"]
        source_files = definition["source_files"]

        print(f"[{file_key}] {base_title}")
        print(f"  ソース: {', '.join(source_files)}")
        print(f"  ビュー: {', '.join(views)}")

        all_views_for_topic = {v: f"{file_key}_{v}.html" for v in views}

        for view in views:
            try:
                generate_html(
                    base_title=base_title,
                    file_key=file_key,
                    view=view,
                    source_files=source_files,
                    all_views_for_topic=all_views_for_topic,
                )
                generated += 1
            except Exception as e:
                print(f"  [ERROR] {file_key}_{view}: {e}")
                import traceback
                traceback.print_exc()
        print()

    print(f"=== 完了: {generated}/{total} 件生成 ===")
    print(f"出力先: {OUTPUT_DIR}")
    
    # 生成ファイルの一覧とサイズを表示
    print()
    print("生成済みファイル一覧:")
    for html_file in sorted(OUTPUT_DIR.glob("*.html")):
        size_kb = html_file.stat().st_size / 1024
        print(f"  {html_file.name:55s} {size_kb:6.1f} KB")


if __name__ == "__main__":
    main()
