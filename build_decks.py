#!/usr/bin/env python3
"""IDMナレッジベース デッキHTMLビルドスクリプト

各HTMLデッキをJSONソースから再生成するためのビルドスクリプト。
DECK_MANIFESTに登録されたHTMLファイルとそのJSONソースを管理し、
build_deck()で各テンプレートを呼び出してHTMLを生成する。

Usage:
    python3 build_decks.py            # 全デッキを再生成
    python3 build_decks.py --dry-run  # 生成対象一覧を表示
    python3 build_decks.py --index    # index.htmlのみ再生成
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
HTML_DIR = BASE_DIR / "02_html_decks"

# ---------------------------------------------------------------------------
# DECK_MANIFEST
# キー: 出力HTMLファイル名 (02_html_decks/ 相対)
# 値:   {"title": str, "sources": [JSONパス(BASE_DIR相対)], "template": str}
# ---------------------------------------------------------------------------
DECK_MANIFEST: dict[str, dict] = {
    "architecture_patterns_detail.html": {
        "title": "ID基盤アーキテクチャ 4パターン詳解",
        "description": "オンプレミスから始める移行設計 — ITアーキテクト/SE/情報システム部長向け",
        "sources": [
            "07_migration_patterns/ad_to_entra_migration.json",
            "03_identity_architecture/identity_landscape.json",
        ],
        "template": "architecture_patterns",
    },
    "assessment_current_state.html": {
        "title": "現状アセスメント — AD健全性チェックリスト",
        "description": "移行前の棚卸し・現状把握ガイド",
        "sources": [
            "03_identity_architecture/ad_current_state.json",
            "07_migration_patterns/ad_to_entra_migration.json",
        ],
        "template": "assessment",
    },
    "roadmap_ad_modernization.html": {
        "title": "AD近代化ロードマップ",
        "description": "段階的移行計画の設計と実行",
        "sources": [
            "07_migration_patterns/ad_to_entra_migration.json",
            "03_identity_architecture/identity_landscape.json",
            "05_hybrid_scenarios/entra_hybrid_join.json",
        ],
        "template": "roadmap",
    },
    "idm_products_japan.html": {
        "title": "日本市場向けIDM製品比較",
        "description": "主要IAM/IDM製品の機能・コスト・導入実績比較",
        "sources": [
            "03_identity_architecture/iam_product_landscape_japan.json",
            "03_identity_architecture/idp_comparison.json",
        ],
        "template": "product_comparison",
    },
    "comparison_pam_products.html": {
        "title": "PAM製品比較ガイド",
        "description": "CyberArk / Delinea / Senhasegura / ManageEngine 比較",
        "sources": [
            "03_identity_architecture/pam_tool_comparison.json",
        ],
        "template": "product_comparison",
    },
    "mfa_practical_guide.html": {
        "title": "MFA実践ガイド",
        "description": "多要素認証の展開戦略と運用ノウハウ",
        "sources": [
            "03_identity_architecture/identity_landscape.json",
            "06_security_hardening/privileged_access_management.json",
        ],
        "template": "practical_guide",
    },
    "zerotrust_migration_guide.html": {
        "title": "ゼロトラスト移行ガイド",
        "description": "境界防御からゼロトラストへの実践的移行手順",
        "sources": [
            "03_identity_architecture/zero_trust_architecture.json",
            "06_security_hardening/privileged_access_management.json",
        ],
        "template": "zerotrust",
    },
    "vendor_access_pam.html": {
        "title": "ベンダー・外部委託アクセス管理",
        "description": "SIer/保守ベンダーのID統制とPAM連携",
        "sources": [
            "06_security_hardening/privileged_access_management.json",
            "07_migration_patterns/ad_to_entra_migration.json",
        ],
        "template": "vendor_access",
    },
    "oracle_auth_audit_wbs.html": {
        "title": "Oracle Database 認証・監査近代化 WBS",
        "description": "実装プロジェクト WBSガイド",
        "sources": [
            "04_server_auth/kerberos_cifs_auth.json",
        ],
        "template": "oracle_wbs",
    },
    "protocol_comparison_saml_scim_oauth.html": {
        "title": "プロトコル比較: SAML / SCIM / OAuth / OIDC",
        "description": "ID連携プロトコルの選択ガイド",
        "sources": [
            "03_identity_architecture/identity_landscape.json",
        ],
        "template": "protocol_comparison",
    },
    "iga_selection_guide.html": {
        "title": "IGA製品選定ガイド",
        "description": "Identity Governance & Administration 製品比較",
        "sources": [
            "03_identity_architecture/iga_tool_comparison.json",
        ],
        "template": "iga_guide",
    },
    "budget_security_guide.html": {
        "title": "IDセキュリティ予算策定ガイド",
        "description": "情報システム部門向けROI・コスト試算",
        "sources": [
            "03_identity_architecture/iam_capability_product_matrix.json",
        ],
        "template": "budget_guide",
    },
    "incident_response_id.html": {
        "title": "ID侵害インシデント対応手順",
        "description": "認証情報漏洩・特権アカウント侵害の対応フロー",
        "sources": [
            "06_security_hardening/privileged_access_management.json",
            "06_security_hardening/ransomware_defense.json",
        ],
        "template": "incident_response",
    },
    "group_id_integration_roadmap.html": {
        "title": "グループ会社ID統合ロードマップ",
        "description": "持株会社・子会社間のID統合設計",
        "sources": [
            "07_migration_patterns/ma_identity_integration.json",
            "07_migration_patterns/ad_to_entra_migration.json",
        ],
        "template": "roadmap",
    },
    "external_id_management.html": {
        "title": "外部ID管理ガイド",
        "description": "B2B連携・パートナー・顧客IDの統合管理",
        "sources": [
            "03_identity_architecture/identity_landscape.json",
        ],
        "template": "external_id",
    },
    "non_human_id_management.html": {
        "title": "非人間系ID管理（サービスアカウント・API）",
        "description": "マシンID・ワークロードIDのライフサイクル管理",
        "sources": [
            "07_migration_patterns/ad_to_entra_migration.json",
            "03_identity_architecture/microservices_id.json",
        ],
        "template": "machine_id",
    },
    "shadow_it_governance.html": {
        "title": "シャドーIT ガバナンス",
        "description": "未承認SaaS・外部クラウドの可視化と統制",
        "sources": [
            "03_identity_architecture/identity_landscape.json",
        ],
        "template": "shadow_it",
    },
    "saas_sso_quickstart.html": {
        "title": "SaaS SSO クイックスタート",
        "description": "Entra ID / Okta 経由SSOの素早い展開手順",
        "sources": [
            "03_identity_architecture/identity_landscape.json",
            "03_identity_architecture/idp_comparison.json",
        ],
        "template": "sso_quickstart",
    },
    "contractor_id_management.html": {
        "title": "契約社員・派遣社員ID管理",
        "description": "非正規雇用者のID発行・停止・棚卸し",
        "sources": [
            "07_migration_patterns/ad_to_entra_migration.json",
        ],
        "template": "contractor_id",
    },
    "hr_id_automation.html": {
        "title": "人事連携IDライフサイクル自動化",
        "description": "入社・異動・退職に連動したID自動プロビジョニング",
        "sources": [
            "03_identity_architecture/iga_tool_comparison.json",
        ],
        "template": "hr_automation",
    },
}


def load_json(path: Path) -> dict:
    """JSONファイルを読み込んで辞書として返す。

    Args:
        path: JSONファイルの絶対パス

    Returns:
        解析済みJSONデータ

    Raises:
        FileNotFoundError: ファイルが存在しない場合
        json.JSONDecodeError: JSON形式エラーの場合
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, path: Path) -> None:
    """辞書をJSONファイルとして保存する (ensure_ascii=False, indent=2)。

    Args:
        data: 保存するデータ
        path: 出力先パス
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _build_toc_html(manifest: dict[str, dict]) -> str:
    """マニフェストからナビゲーションカードHTML断片を生成する。"""
    cards = []
    categories = {
        "アーキテクチャ・設計": [
            "architecture_patterns_detail.html",
            "assessment_current_state.html",
            "roadmap_ad_modernization.html",
            "zerotrust_migration_guide.html",
        ],
        "製品・プロトコル比較": [
            "idm_products_japan.html",
            "comparison_pam_products.html",
            "protocol_comparison_saml_scim_oauth.html",
            "iga_selection_guide.html",
        ],
        "運用・ガバナンス": [
            "mfa_practical_guide.html",
            "vendor_access_pam.html",
            "oracle_auth_audit_wbs.html",
            "incident_response_id.html",
            "shadow_it_governance.html",
        ],
        "IDライフサイクル": [
            "hr_id_automation.html",
            "contractor_id_management.html",
            "non_human_id_management.html",
            "external_id_management.html",
        ],
        "グループ・統合": [
            "group_id_integration_roadmap.html",
            "saas_sso_quickstart.html",
            "budget_security_guide.html",
        ],
    }

    html_parts = []
    for category, filenames in categories.items():
        html_parts.append(f'<h2 class="cat-title">{category}</h2>\n<div class="card-grid">')
        for fname in filenames:
            if fname not in manifest:
                continue
            info = manifest[fname]
            html_parts.append(
                f'  <a class="deck-card" href="02_html_decks/{fname}">\n'
                f'    <div class="deck-title">{info["title"]}</div>\n'
                f'    <div class="deck-desc">{info["description"]}</div>\n'
                f'    <div class="deck-sources">ソース: {len(info["sources"])}ファイル</div>\n'
                f'  </a>'
            )
        html_parts.append("</div>")
    return "\n".join(html_parts)


def build_index(deck_manifest: dict[str, dict], dry_run: bool = False) -> None:
    """index.htmlをマニフェストからカードグリッドナビゲーションとして生成する。

    Args:
        deck_manifest: DECKマニフェスト辞書
        dry_run: Trueの場合はファイル書き込みを行わず内容を表示する
    """
    output_path = BASE_DIR / "index.html"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(deck_manifest)

    nav_html = _build_toc_html(deck_manifest)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IDMナレッジベース — エンタープライズID管理設計ガイド</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Helvetica Neue','Hiragino Kaku Gothic ProN','Meiryo',sans-serif;background:#f1f5f9;color:#1e293b;font-size:14px}}
header{{background:#0f172a;color:#fff;padding:24px 40px;border-bottom:3px solid #2563eb}}
header h1{{font-size:1.4rem;font-weight:700;margin-bottom:4px}}
header .sub{{color:#94a3b8;font-size:.85rem}}
main{{max-width:1200px;margin:0 auto;padding:32px 40px}}
.cat-title{{font-size:1rem;font-weight:700;color:#1e3a5f;margin:28px 0 12px;padding-bottom:6px;border-bottom:2px solid #3b82f6}}
.card-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin-bottom:16px}}
.deck-card{{background:#fff;border-radius:8px;border:1px solid #e2e8f0;padding:14px 16px;text-decoration:none;color:inherit;display:block;transition:box-shadow .15s,transform .15s}}
.deck-card:hover{{box-shadow:0 4px 12px rgba(0,0,0,.1);transform:translateY(-2px)}}
.deck-title{{font-weight:700;color:#1e3a5f;font-size:.9rem;margin-bottom:4px}}
.deck-desc{{color:#475569;font-size:.8rem;line-height:1.5;margin-bottom:8px}}
.deck-sources{{font-size:.72rem;color:#94a3b8}}
footer{{text-align:center;color:#94a3b8;font-size:.78rem;padding:32px;border-top:1px solid #e2e8f0}}
</style>
</head>
<body>
<header>
  <h1>📘 IDMナレッジベース</h1>
  <div class="sub">エンタープライズID管理設計ガイド — 日本企業のオンプレミス残存環境を含む次世代ID基盤設計 | {total}デッキ | 更新: {now}</div>
</header>
<main>
{nav_html}
</main>
<footer>IDMナレッジベース — build_decks.py で生成 | {now}</footer>
</body>
</html>"""

    if dry_run:
        print(f"[DRY-RUN] index.html ({len(html)} bytes) → {output_path}")
        return

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ index.html 生成完了 ({len(html):,} bytes)")


def build_deck(
    deck_name: str,
    info: dict,
    dry_run: bool = False,
) -> bool:
    """特定のデッキHTMLを生成する（現バージョンはスタブ）。

    実際の生成ロジックはテンプレートごとに実装する。
    各テンプレートはJSONソースを読み込み、HTMLを生成して output_path に書き込む。

    Args:
        deck_name: 出力HTMLファイル名 (02_html_decks/ 相対)
        info: マニフェストの情報 (title, sources, template)
        dry_run: Trueの場合はファイル書き込みを行わない

    Returns:
        生成に成功した場合True、スキップした場合False
    """
    output_path = HTML_DIR / deck_name
    template_name = info.get("template", "generic")
    sources = info.get("sources", [])

    # ソースJSONを読み込む
    source_data = []
    missing_sources = []
    for src in sources:
        src_path = BASE_DIR / src
        if not src_path.exists():
            missing_sources.append(src)
            continue
        try:
            source_data.append(load_json(src_path))
        except (json.JSONDecodeError, OSError) as e:
            print(f"  ⚠️  {src}: 読み込み失敗 — {e}", file=sys.stderr)

    if dry_run:
        status = "✅" if output_path.exists() else "🆕"
        src_status = f"{len(source_data)}/{len(sources)} ソース利用可能"
        if missing_sources:
            src_status += f" (未存在: {', '.join(missing_sources)})"
        print(f"  {status} {deck_name:55s} template={template_name:25s} {src_status}")
        return True

    # テンプレート別生成ロジック（スタブ: 既存ファイルがあれば維持）
    # 各テンプレートはここに elif ブロックを追加して実装する
    if output_path.exists():
        # 既存HTMLが存在する場合はスキップ（手動編集を保護）
        print(f"  ⏭️  {deck_name} — 既存ファイルをスキップ (手動編集保護)")
        return False

    # フォールバック: 最小限のHTMLプレースホルダーを生成
    _write_placeholder(deck_name, info, output_path, source_data)
    return True


def _write_placeholder(
    deck_name: str,
    info: dict,
    output_path: Path,
    source_data: list[dict],
) -> None:
    """ビルド未実装デッキ向けのプレースホルダーHTMLを書き込む。

    Args:
        deck_name: 出力ファイル名
        info: マニフェスト情報
        output_path: 出力先パス
        source_data: 読み込み済みJSONデータのリスト
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    node_count = sum(len(d.get("nodes", [])) for d in source_data)
    edge_count = sum(len(d.get("edges", [])) for d in source_data)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{info['title']}</title>
<style>
body{{font-family:'Helvetica Neue',sans-serif;background:#f1f5f9;color:#1e293b;padding:40px;font-size:14px}}
.container{{max-width:800px;margin:0 auto;background:#fff;border-radius:12px;padding:32px;border:1px solid #e2e8f0}}
h1{{color:#1e3a5f;font-size:1.3rem;margin-bottom:8px}}
.badge{{display:inline-block;background:#dbeafe;color:#1e40af;padding:3px 10px;border-radius:12px;font-size:.75rem;margin-bottom:16px}}
p{{color:#475569;margin-bottom:12px}}
.stat{{background:#f8fafc;border-radius:8px;padding:12px;margin-top:16px;font-size:.85rem;color:#64748b}}
</style>
</head>
<body>
<div class="container">
  <h1>{info['title']}</h1>
  <span class="badge">template: {info.get('template', 'generic')}</span>
  <p>{info['description']}</p>
  <p>このデッキは build_decks.py で生成されたプレースホルダーです。
  <code>build_deck()</code> に <code>{info.get('template', 'generic')}</code> テンプレートの実装を追加してください。</p>
  <div class="stat">
    📊 ソースJSONから読み込んだデータ: ノード {node_count}件、エッジ {edge_count}件<br>
    🕐 生成日時: {now}
  </div>
</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  🆕 {deck_name} — プレースホルダー生成完了")


def main() -> None:
    """全デッキを一括再生成するメインエントリーポイント。

    コマンドライン引数:
        --dry-run: 実際の書き込みは行わず、ビルド対象一覧を表示する
        --index:   index.htmlのみを再生成する
        --deck:    特定のデッキのみを再生成する (例: --deck architecture_patterns_detail.html)
    """
    parser = argparse.ArgumentParser(
        description="IDMナレッジベース デッキHTMLビルドスクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python3 build_decks.py              全デッキを再生成
  python3 build_decks.py --dry-run    ビルド対象一覧を表示（書き込みなし）
  python3 build_decks.py --index      index.html のみ再生成
  python3 build_decks.py --deck architecture_patterns_detail.html
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際の書き込みは行わず、ビルド対象一覧を表示する",
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="index.html のみを再生成する",
    )
    parser.add_argument(
        "--deck",
        metavar="FILENAME",
        help="特定デッキのみを再生成する (02_html_decks/ 内のファイル名)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("IDMナレッジベース デッキビルダー")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"HTML_DIR: {HTML_DIR}")
    if args.dry_run:
        print("[DRY-RUN モード — ファイル書き込みなし]")
    print("=" * 60)

    # index.html のみの場合
    if args.index:
        print("\n📄 index.html を生成中...")
        build_index(DECK_MANIFEST, dry_run=args.dry_run)
        return

    # 特定デッキのみの場合
    if args.deck:
        if args.deck not in DECK_MANIFEST:
            print(f"❌ エラー: '{args.deck}' はマニフェストに登録されていません。", file=sys.stderr)
            print("登録済みデッキ一覧:")
            for name in DECK_MANIFEST:
                print(f"  - {name}")
            sys.exit(1)
        print(f"\n🔨 {args.deck} を生成中...")
        success = build_deck(args.deck, DECK_MANIFEST[args.deck], dry_run=args.dry_run)
        if success:
            print("✅ 完了")
        return

    # 全デッキ生成
    print(f"\n📦 デッキ数: {len(DECK_MANIFEST)}")
    print("\n--- index.html ---")
    build_index(DECK_MANIFEST, dry_run=args.dry_run)

    print(f"\n--- デッキHTML ({len(DECK_MANIFEST)}件) ---")
    built = 0
    skipped = 0
    for deck_name, info in DECK_MANIFEST.items():
        success = build_deck(deck_name, info, dry_run=args.dry_run)
        if success:
            built += 1
        else:
            skipped += 1

    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"[DRY-RUN] 対象デッキ: {len(DECK_MANIFEST)}件")
    else:
        print(f"✅ 生成: {built}件 ／ ⏭️  スキップ: {skipped}件")
    print("=" * 60)


if __name__ == "__main__":
    main()
