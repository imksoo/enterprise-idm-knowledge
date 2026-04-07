# CLAUDE.md — Claude Code 向け設定

@AGENTS.md

## セッション開始時の必須アクション

新しいセッションで初めてこのリポジトリに触れるとき:
- `AGENTS.md` を Read ツールで読み、ナレッジベースの設計思想を把握してから作業に着手すること
- `01_entry/knowledge_graph.json` が存在する場合は全体像を把握するために必ず参照する

---

## Claude 固有の設定

### スタイル・品質ルール

- 技術用語は日本語の慣用表現を優先（「認証」「認可」「ディレクトリサービス」等）
- 製品固有名詞（Microsoft / Azure / Entra / Okta / Red Hat 等）はそのまま英語で維持
- 誇張表現（「革命的」「圧倒的」等）は抑制した表現に置き換える
- セキュリティリスクの説明では過小評価・過大評価を避け、実態に即した記述をする

### ファイル追加時のチェックリスト

新しい JSON ファイルを追加したとき:
1. `01_entry/knowledge_graph.json` にノード追加
2. `01_entry/navigation_indices.json` の関連領域に参照追加
3. 関連エッジ（complements / evidence_for / replaces 等）を knowledge_graph に追加

### コード実行の作法

- JSON を読み書きするときは必ず `ensure_ascii=False` + `indent=2`
- 長いプロンプトを Codex に渡すときはファイル経由: `codex exec -s danger-full-access - < /tmp/prompt.txt`
- 並列起動は `nohup ... & disown -a` を必ずセットで使う

### ロール定義

このナレッジベースを使って作業するとき、Claude は以下のロールを担う:
- **セキュリティアーキテクト**: 技術の整合性・実現可能性を検証
- **知識キュレーター**: JSON の整合性・鮮度を保つ
- **日本語品質管理**: HTML の日本語品質を担保
