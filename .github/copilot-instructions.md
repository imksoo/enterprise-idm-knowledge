# GitHub Copilot Instructions — Enterprise IDM Knowledge Base

このリポジトリは **日本のオンプレミス残存環境を含む次世代エンタープライズ ID 管理**に関するナレッジベース。

## リポジトリの性質

- コードリポジトリではなく**知識ベース**
- `01_entry/` が全ての入口（知識グラフ・シソーラス・索引）
- `03_〜07_/` ディレクトリに JSON 形式で知識を蓄積
- `02_html_decks/` が人間向け HTML 表示層

## 対象領域

1. オンプレミス OS 認証（Windows Server / RHEL の直接ログイン管理）
2. サーバーサイドプロセス認証（Kerberos / CIFS / SQL Server / IIS / PostgreSQL）
3. ハイブリッドシナリオ（Entra Hybrid Join / Okta / ADFS 共存）
4. 特権管理・ランサムウェア対策・サーバー検疫
5. グループポリシー代替（Intune / Ansible / Chef / Puppet）
6. AD → Entra ID 移行パターン

## JSON スキーマ規約

```json
{
  "metadata": { "id": "...", "title": "...", "version": "1.0", "tags": [] },
  "nodes": [{ "id": "node_001", "label": "...", "object_type": "concept|product|protocol|risk|pattern", "description": "..." }],
  "edges": [{ "from": "node_001", "to": "node_002", "relationship": "implements|replaces|requires|mitigates|complements", "description": "..." }],
  "knowledge": []
}
```

## サブエージェント呼び出し

```bash
codex exec -s danger-full-access - < /tmp/prompt.txt
claude --dangerously-skip-permissions -p "<プロンプト>"
```
