# AGENTS.md — AI エージェント向けナレッジベース操作ガイド

このリポジトリは **日本企業の情報システム部門・CISO・SIer SE が、オンプレミス残存環境を含む次世代 ID 管理基盤を設計・移行するためのナレッジベース**である。
コードリポジトリではない。JSON が知識源、HTML が人間向け表示層、`01_entry/` が全ての入口。

> **セッション開始時**: 大きな作業を始める前に `AGENTS.md` 全体を読み、ナレッジベースの設計思想を把握してから作業に着手すること。

---

## このナレッジベースが扱う問題領域

### コアテーマ

1. **オンプレミス OS 認証の現状と将来** — Windows Server / RHEL 等に直接ログインするシステム管理ユーザーの管理
2. **サーバーサイドプロセス認証** — SQL Server / IIS / PostgreSQL 等が CIFS(Kerberos)・連携システムと認証する方式
3. **ハイブリッドシナリオ** — Entra Hybrid Join / Entra ID / Okta / ADFS の共存・移行
4. **セキュリティ侵害対応設計** — ランサムウェア対策・特権アカウント封じ込め・サーバー検疫
5. **グループポリシー代替** — Intune / Ansible / Chef / Puppet などによる代替手段
6. **日本型 IT の文脈** — 内製 SE が少ない・レガシーシステム多い・SIer 依存構造

---

## リポジトリ構造（重要度順）

```
01_entry/                  ★ 常にここから引く（索引・グラフ・シソーラス）
  knowledge_graph.json       ノード・エッジの知識グラフ
  navigation_indices.json    主訴/ペルソナ/技術領域/移行ステージ別索引
  thesaurus_controlled_vocabulary.json  SKOS準拠統制語彙
  fact_retrieval_index.json  クエリパターン別検索ガイド

02_html_decks/             人間向け HTML スライド・解説
03_identity_architecture/  ID 管理アーキテクチャ全体像 JSON
04_server_auth/            サーバー OS・プロセス認証の詳細 JSON
05_hybrid_scenarios/       ハイブリッド構成・移行シナリオ JSON
06_security_hardening/     セキュリティ強化・ゼロトラスト JSON
07_migration_patterns/     AD→次世代移行パターン JSON
99_worklog/                作業ログ・スタイルガイド
```

---

## よく使う JSON ファイル（目的別）

| 目的 | ファイル |
|------|---------|
| 全体技術地図 | `03_identity_architecture/identity_landscape.json` |
| AD 現状診断チェックリスト | `03_identity_architecture/ad_current_state.json` |
| OS 認証詳細 | `04_server_auth/os_auth_methods.json` |
| Kerberos/CIFS 認証 | `04_server_auth/kerberos_cifs_auth.json` |
| Entra Hybrid Join 詳細 | `05_hybrid_scenarios/entra_hybrid_join.json` |
| 特権管理・PAM | `06_security_hardening/privileged_access_management.json` |
| ランサムウェア対策 | `06_security_hardening/ransomware_defense.json` |
| GP 代替手段 | `06_security_hardening/group_policy_alternatives.json` |
| AD→Entra 移行パターン | `07_migration_patterns/ad_to_entra_migration.json` |

---

## JSON ファイルのスキーマ規約

```json
{
  "metadata": {
    "id": "topic_XXX",
    "title": "トピックタイトル",
    "version": "1.0",
    "created": "2026-04-07",
    "updated": "2026-04-07",
    "tags": ["タグ1", "タグ2"],
    "related_files": ["other_file.json"]
  },
  "nodes": [
    {
      "id": "node_001",
      "label": "ノード名",
      "object_type": "concept|product|protocol|risk|pattern",
      "description": "説明",
      "properties": {}
    }
  ],
  "edges": [
    {
      "from": "node_001",
      "to": "node_002",
      "relationship": "implements|replaces|requires|mitigates|complements|example_of",
      "description": "関係の説明"
    }
  ],
  "knowledge": []
}
```

---

## サブエージェント起動パターン

```bash
# Codex（大量 JSON 生成向け）
codex exec -s danger-full-access - < /tmp/prompt.txt

# Claude（日本語品質・複雑な調査向け）
claude --dangerously-skip-permissions -p "<プロンプト>"

# 並列バックグラウンド実行
nohup codex exec -s danger-full-access - < /tmp/prompt_a.txt > /tmp/log_a.txt 2>&1 &
nohup claude --dangerously-skip-permissions -p "..." > /tmp/log_b.txt 2>&1 &
disown -a
```

---

## 厳守ルール

- JSON を顧客に直接見せない。人間には `02_html_decks/*.html` を使う
- 製品名・用語は `thesaurus_controlled_vocabulary.json` の `preferred_label` のみ使用
- JSON 読み書きは必ず `ensure_ascii=False` + `indent=2`
- ファイルを追加したら `knowledge_graph.json` / `navigation_indices.json` を更新する

---

## 禁止事項

- 1 つの JSON だけ読んで結論を出す（複数ファイルを横断する設計）
- シソーラスを無視して独自の検索語を使う
- `null` や空値フィールドを根拠として引用する
- `pkill` / `killall` を使う（`kill <PID>` で個別指定すること）

---

## エージェント役割分担（重要）

| タスク | 使用ツール |
|--------|-----------|
| Web調査・JSON大量生成・並列処理 | `codex exec -s danger-full-access` |
| 日本語レビュー・リライト・HTML品質 | `claude --dangerously-skip-permissions` |
| 大コンテキスト統合・矛盾検出 | Copilot（直接） |

## Mermaid 図の禁止事項

- `\n` をラベル・メッセージ内で使わない（レンダリングされずそのまま表示される）
- sequenceDiagram でのHTMLラベル（`<br/>`）は使わない
- ラベルは20文字以内に収める
- 長い補足はNoteブロックで分離する
- 複雑なフローはMermaidではなくECharts custom またはSVGで実装する

## 日本語品質ルール

- 製品名は英語維持（Entra ID, Active Directory, CyberArk等）
- 略語初出は日本語を添える（PAM（特権アクセス管理））
- 誇張表現禁止（「完璧」「最強」→「高い信頼性」「業界標準」）
- 数値・根拠を添える
- 詳細: `99_worklog/claude_review_workflow.md`
