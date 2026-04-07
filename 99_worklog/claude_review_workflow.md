# Claude レビューワークフロー

## 役割分担

| タスク | 担当 | 理由 |
|--------|------|------|
| Web調査・情報収集・JSON構造化 | Codex (`codex exec -s danger-full-access`) | 大量生成・並列化・Web検索 |
| 日本語表現レビュー・リライト | Claude (`claude --dangerously-skip-permissions`) | 文脈理解・スタイルガイド適用 |
| HTML品質確認・図表説明文 | Claude | 読みやすさ・コンサル文脈 |
| 複雑なロジック統合・矛盾検出 | Copilot（直接） | 大コンテキスト処理 |

## 日本語スタイルルール（このプロジェクト固有）

- セキュリティ用語は日本語慣用表現を優先（「認証」「認可」「侵害」）
- 製品名は英語表記を維持（Entra ID / Active Directory / CyberArk）
- 「ゼロトラスト」はカタカナ（Zero Trustの和訳として定着）
- 略語初出時は日本語を添える（PAM（特権アクセス管理））
- 誇張表現を避ける（「完璧」「最強」→「高い信頼性」「業界標準」）
- SIer営業文脈では「課題」「対策」「効果」の三点セットで説明
- 数値・根拠を添える（「約7割の企業が…（出典：○○調査）」）

## Claude レビュー起動テンプレート

```bash
# 単一JSONの日本語レビュー
claude --dangerously-skip-permissions -p "
/home/imksoo/works/20260407_idm/99_worklog/claude_review_workflow.md のスタイルルールに従い、
以下のJSONファイルのknowledge[].contentおよびdescriptionフィールドの日本語表現を
レビューして修正してください。上書き保存すること。
対象: /home/imksoo/works/20260407_idm/<対象ファイル>
"

# HTMLの日本語レビュー
claude --dangerously-skip-permissions -p "
スタイルルール: /home/imksoo/works/20260407_idm/99_worklog/claude_review_workflow.md
対象HTML: /home/imksoo/works/20260407_idm/index.html
図の説明文・ツールチップ・カードテキストの日本語を修正して上書き保存。
"
```

## Mermaid 図作成ルール（重要）

### NG パターン（レンダリングされない）
```
sequenceDiagram
  Note: 説明文\nの改行
  A->>B: 長いメッセージ\n改行したい
```

### OK パターン
```
sequenceDiagram
  Note over A,B: 改行は使わず短いラベルにする
  A->>B: 短く書く
  Note right of B: 補足説明は<br/>でなくNoteで分割
```

### ラベルが長い場合
- ラベルを20文字以内に収める
- 補足はNoteブロックで別行に
- HTMLラベル記法 `["ラベル<br/>2行目"]` はflowchartのみ有効
- sequenceDiagramではHTML記法不可

### 推奨: Mermaid の代わりにEChartsカスタム図
複雑なフロー図はMermaidではなくECharts custom seriesまたはSVGで直接描画する。
