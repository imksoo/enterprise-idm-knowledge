content = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SAML / OIDC / OAuth 2.0 / SCIM プロトコル比較ガイド</title>
<style>
  :root {
    --saml: #e67e22;
    --saml-light: #fef3e2;
    --saml-dark: #b85c00;
    --oidc: #2980b9;
    --oidc-light: #eaf4fb;
    --oidc-dark: #1a5c8a;
    --scim: #27ae60;
    --scim-light: #e8f8ef;
    --scim-dark: #1a7d44;
    --bg: #f8fafc;
    --surface: #ffffff;
    --border: #e2e8f0;
    --text: #1e293b;
    --text-muted: #64748b;
    --sidebar-w: 240px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Meirio", "Yu Gothic", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    font-size: 15px;
  }
  /* ─── Sidebar ─── */
  #sidebar {
    position: fixed;
    top: 0; left: 0;
    width: var(--sidebar-w);
    height: 100vh;
    background: #1e293b;
    color: #cbd5e1;
    overflow-y: auto;
    z-index: 100;
    display: flex;
    flex-direction: column;
  }
  #sidebar .logo {
    padding: 20px 16px 12px;
    font-size: 13px;
    font-weight: 700;
    color: #f1f5f9;
    border-bottom: 1px solid #334155;
    letter-spacing: 0.05em;
    line-height: 1.4;
  }
  #sidebar nav { flex: 1; padding: 12px 0; }
  #sidebar nav a {
    display: block;
    padding: 8px 16px;
    color: #94a3b8;
    text-decoration: none;
    font-size: 13px;
    border-left: 3px solid transparent;
    transition: all 0.2s;
  }
  #sidebar nav a:hover {
    color: #f1f5f9;
    background: #334155;
    border-left-color: #60a5fa;
  }
  #sidebar nav a.saml { border-left-color: transparent; }
  #sidebar nav a.saml:hover { border-left-color: var(--saml); }
  #sidebar nav a.oidc:hover { border-left-color: var(--oidc); }
  #sidebar nav a.scim:hover { border-left-color: var(--scim); }
  #sidebar .section-label {
    padding: 16px 16px 4px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #475569;
  }
  /* ─── Main ─── */
  #main {
    margin-left: var(--sidebar-w);
    min-height: 100vh;
  }
  .page-header {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    color: #f1f5f9;
    padding: 48px 48px 40px;
    border-bottom: 4px solid #3b82f6;
  }
  .page-header h1 {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
    line-height: 1.3;
  }
  .page-header .subtitle {
    font-size: 14px;
    color: #94a3b8;
    max-width: 680px;
  }
  .badge-row {
    display: flex;
    gap: 8px;
    margin-top: 20px;
    flex-wrap: wrap;
  }
  .badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
  }
  .badge.saml { background: var(--saml); color: #fff; }
  .badge.oidc { background: var(--oidc); color: #fff; }
  .badge.scim { background: var(--scim); color: #fff; }
  .badge.outline { background: transparent; border: 1px solid #475569; color: #94a3b8; }
  /* ─── Content sections ─── */
  .content { padding: 0 48px 64px; }
  section { padding-top: 56px; }
  section h2 {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
  }
  section h2 .sec-num {
    background: #1e293b;
    color: #fff;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 800;
    flex-shrink: 0;
  }
  h3 {
    font-size: 16px;
    font-weight: 700;
    margin: 28px 0 12px;
    color: #1e293b;
  }
  p { margin-bottom: 12px; color: #334155; }
  /* ─── Protocol cards (Section 1 grid) ─── */
  .plane-grid {
    display: grid;
    grid-template-columns: 160px 1fr 1fr 1fr 1fr;
    gap: 2px;
    border: 2px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    margin: 20px 0 32px;
    font-size: 13px;
  }
  .plane-grid .cell {
    padding: 14px 16px;
    background: var(--surface);
    line-height: 1.5;
  }
  .plane-grid .header-row {
    display: contents;
  }
  .plane-grid .header-row .cell {
    background: #1e293b;
    color: #f1f5f9;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }
  .plane-label {
    background: #f1f5f9 !important;
    font-weight: 700;
    color: #475569 !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .check { color: #16a34a; font-size: 16px; font-weight: 700; }
  .partial { color: #d97706; font-size: 14px; }
  .no { color: #dc2626; font-size: 16px; }
  /* ─── Protocol detail cards ─── */
  .proto-card {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 32px;
    background: var(--surface);
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .proto-card .card-header {
    padding: 16px 24px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.03em;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .proto-card.saml .card-header { background: var(--saml); }
  .proto-card.oidc .card-header { background: var(--oidc); }
  .proto-card.scim .card-header { background: var(--scim); }
  .proto-card .card-body { padding: 20px 24px; }
  /* ─── Strength/weakness lists ─── */
  .sw-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin: 16px 0;
  }
  .sw-box {
    border-radius: 8px;
    padding: 14px 16px;
  }
  .sw-box.strength { background: #f0fdf4; border: 1px solid #86efac; }
  .sw-box.weakness { background: #fff7ed; border: 1px solid #fed7aa; }
  .sw-box h4 {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
  }
  .sw-box.strength h4 { color: #16a34a; }
  .sw-box.weakness h4 { color: #d97706; }
  .sw-box ul { list-style: none; padding: 0; }
  .sw-box ul li {
    font-size: 13px;
    padding: 3px 0;
    padding-left: 18px;
    position: relative;
    color: #374151;
  }
  .sw-box.strength ul li::before { content: "✓"; position: absolute; left: 0; color: #16a34a; font-weight: 700; }
  .sw-box.weakness ul li::before { content: "△"; position: absolute; left: 0; color: #d97706; }
  /* ─── Flow diagrams ─── */
  .flow-box {
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 24px;
    margin: 16px 0;
  }
  .flow-title {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 16px;
  }
  .flow-row {
    display: flex;
    align-items: center;
    gap: 0;
    flex-wrap: wrap;
    margin: 8px 0;
  }
  .flow-node {
    padding: 9px 14px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    color: #fff;
    text-align: center;
    line-height: 1.3;
    min-width: 80px;
  }
  .flow-node.user { background: #6366f1; }
  .flow-node.sp { background: #0891b2; }
  .flow-node.idp { background: #dc2626; }
  .flow-node.authz { background: var(--oidc); }
  .flow-node.resource { background: #0f766e; }
  .flow-node.client { background: #7c3aed; }
  .flow-node.scim-client { background: #059669; }
  .flow-node.scim-server { background: #0f766e; }
  .flow-node.hr { background: #6b7280; }
  .flow-arrow {
    font-size: 16px;
    color: #94a3b8;
    padding: 0 6px;
    font-weight: 400;
  }
  .flow-step {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin: 6px 0;
  }
  .step-num {
    background: #1e293b;
    color: #fff;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 2px;
  }
  .step-desc { font-size: 13px; color: #374151; }
  .step-desc strong { color: #1e293b; }
  /* ─── XML/Code block ─── */
  .code-block {
    background: #1e293b;
    border-radius: 8px;
    padding: 16px 20px;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 12px;
    line-height: 1.6;
    overflow-x: auto;
    margin: 16px 0;
    color: #e2e8f0;
  }
  .code-block .tag { color: #7dd3fc; }
  .code-block .attr { color: #86efac; }
  .code-block .val { color: #fbbf24; }
  .code-block .comment { color: #94a3b8; font-style: italic; }
  /* ─── Comparison table ─── */
  .cmp-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 13px;
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
  }
  .cmp-table thead tr {
    background: #1e293b;
    color: #f1f5f9;
  }
  .cmp-table th {
    padding: 14px 16px;
    text-align: left;
    font-weight: 700;
    font-size: 13px;
  }
  .cmp-table th.saml { background: var(--saml); }
  .cmp-table th.oidc { background: var(--oidc); }
  .cmp-table th.scim { background: var(--scim); }
  .cmp-table tbody tr { border-bottom: 1px solid var(--border); }
  .cmp-table tbody tr:last-child { border-bottom: none; }
  .cmp-table tbody tr:hover { background: #f8fafc; }
  .cmp-table td { padding: 12px 16px; vertical-align: top; }
  .cmp-table td.row-label {
    font-weight: 700;
    color: #475569;
    background: #f8fafc;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    white-space: nowrap;
    width: 140px;
  }
  /* ─── Scenario cards ─── */
  .scenario-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin: 20px 0;
  }
  .scenario-card {
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 20px;
    background: var(--surface);
  }
  .scenario-card .scenario-q {
    font-size: 13px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 8px;
    display: flex;
    align-items: flex-start;
    gap: 8px;
  }
  .scenario-card .scenario-q .q-icon {
    background: #f1f5f9;
    color: #475569;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 1px;
  }
  .scenario-card .answer {
    font-size: 13px;
    color: #374151;
    margin-top: 8px;
    line-height: 1.6;
  }
  .answer .proto-tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
    margin-right: 4px;
    color: #fff;
  }
  .proto-tag.saml { background: var(--saml); }
  .proto-tag.oidc { background: var(--oidc); }
  .proto-tag.scim { background: var(--scim); }
  .proto-tag.combo { background: #7c3aed; }
  /* ─── Info/warning callout ─── */
  .callout {
    border-radius: 8px;
    padding: 14px 18px;
    margin: 16px 0;
    font-size: 13px;
    display: flex;
    gap: 12px;
    align-items: flex-start;
    line-height: 1.6;
  }
  .callout.info { background: #eff6ff; border-left: 4px solid #3b82f6; color: #1e40af; }
  .callout.warn { background: #fffbeb; border-left: 4px solid #f59e0b; color: #92400e; }
  .callout.success { background: #f0fdf4; border-left: 4px solid #22c55e; color: #166534; }
  .callout .icon { font-size: 16px; flex-shrink: 0; margin-top: 1px; }
  /* ─── Token anatomy ─── */
  .token-card {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin: 8px 0;
  }
  .token-card .t-header {
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 700;
    color: #fff;
    background: var(--oidc);
  }
  .token-card .t-body {
    padding: 10px 14px;
    font-size: 12px;
    background: var(--surface);
    color: #374151;
  }
  .token-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    margin: 16px 0;
  }
  /* ─── SCIM resource ─── */
  .scim-resource {
    background: var(--scim-light);
    border: 1px solid #86efac;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
    font-size: 13px;
  }
  .scim-resource h4 { color: var(--scim-dark); margin-bottom: 8px; font-size: 13px; }
  /* ─── Responsive ─── */
  @media (max-width: 900px) {
    :root { --sidebar-w: 200px; }
    .content { padding: 0 24px 48px; }
    .page-header { padding: 32px 24px; }
    .sw-grid { grid-template-columns: 1fr; }
    .scenario-grid { grid-template-columns: 1fr; }
    .plane-grid { grid-template-columns: 120px 1fr 1fr 1fr 1fr; font-size: 11px; }
    .token-row { grid-template-columns: 1fr; }
  }
  @media (max-width: 768px) {
    #sidebar { display: none; }
    #main { margin-left: 0; }
    .page-header h1 { font-size: 22px; }
    .content { padding: 0 16px 32px; }
    .cmp-table { font-size: 12px; }
  }
</style>
</head>
<body>

<!-- ===================== SIDEBAR ===================== -->
<nav id="sidebar">
  <div class="logo">IDM知識ベース<br>プロトコル比較ガイド</div>
  <nav>
    <span class="section-label">はじめに</span>
    <a href="#overview">プロトコル全体マップ</a>
    <span class="section-label">プロトコル詳解</span>
    <a href="#saml" class="saml">SAML 2.0</a>
    <a href="#oidc" class="oidc">OIDC / OAuth 2.0</a>
    <a href="#scim" class="scim">SCIM 2.0</a>
    <span class="section-label">選択支援</span>
    <a href="#comparison">比較表</a>
    <a href="#guide">選択ガイド</a>
    <a href="#japan">日本企業の実態</a>
  </nav>
</nav>

<!-- ===================== MAIN ===================== -->
<div id="main">

<!-- ─── Page Header ─── -->
<div class="page-header">
  <h1>SAML / OIDC / OAuth 2.0 / SCIM<br>プロトコル比較・選択ガイド</h1>
  <p class="subtitle">
    エンタープライズ ID 管理を支える4大プロトコルの仕組み・強み・弱み・
    適用シーンを整理し、日本企業の IT アーキテクトが正しく選択・説明できるよう設計したリファレンス。
  </p>
  <div class="badge-row">
    <span class="badge saml">SAML 2.0</span>
    <span class="badge oidc">OIDC / OAuth 2.0</span>
    <span class="badge scim">SCIM 2.0</span>
    <span class="badge outline">対象：IT アーキテクト・SE</span>
    <span class="badge outline">更新：2026年4月</span>
  </div>
</div>

<!-- ─── Content ─── -->
<div class="content">

<!-- ================================================================
     Section 1: プロトコル全体マップ
     ================================================================ -->
<section id="overview">
  <h2><span class="sec-num">1</span>プロトコル全体マップ</h2>

  <p>
    ID 管理プロトコルは役割別に3つの<strong>プレーン（層）</strong>に分類される。
    「誰が誰であるか」を確認する<strong>認証（AuthN）</strong>、
    「何ができるか」を制御する<strong>認可（AuthZ）</strong>、
    そしてアカウントを自動で作成・変更・削除する<strong>プロビジョニング</strong>だ。
    プロトコルを選ぶ前に、自分たちが解決しようとしている課題がどのプレーンに属するかを明確にする。
  </p>

  <div class="plane-grid">
    <!-- header -->
    <div class="cell header-row" style="display:contents;">
      <div class="cell" style="background:#1e293b;color:#f1f5f9;font-weight:700;font-size:12px;">プレーン / 役割</div>
      <div class="cell" style="background:var(--saml);color:#fff;font-weight:700;font-size:12px;text-align:center;">SAML 2.0</div>
      <div class="cell" style="background:var(--oidc);color:#fff;font-weight:700;font-size:12px;text-align:center;">OAuth 2.0</div>
      <div class="cell" style="background:#1761a0;color:#fff;font-weight:700;font-size:12px;text-align:center;">OpenID Connect</div>
      <div class="cell" style="background:var(--scim);color:#fff;font-weight:700;font-size:12px;text-align:center;">SCIM 2.0</div>
    </div>
    <!-- AuthN -->
    <div class="cell plane-label">認証 (AuthN)<br>誰であるか</div>
    <div class="cell" style="text-align:center;"><span class="check">✓</span><br><small>主用途</small></div>
    <div class="cell" style="text-align:center;"><span class="no">✗</span><br><small>対象外</small></div>
    <div class="cell" style="text-align:center;"><span class="check">✓</span><br><small>主用途</small></div>
    <div class="cell" style="text-align:center;"><span class="no">✗</span><br><small>対象外</small></div>
    <!-- AuthZ -->
    <div class="cell plane-label">認可 (AuthZ)<br>何ができるか</div>
    <div class="cell" style="text-align:center;"><span class="partial">△</span><br><small>属性経由</small></div>
    <div class="cell" style="text-align:center;"><span class="check">✓</span><br><small>主用途</small></div>
    <div class="cell" style="text-align:center;"><span class="check">✓</span><br><small>継承</small></div>
    <div class="cell" style="text-align:center;"><span class="no">✗</span><br><small>対象外</small></div>
    <!-- Provisioning -->
    <div class="cell plane-label">プロビジョニング<br>アカウント管理</div>
    <div class="cell" style="text-align:center;"><span class="no">✗</span><br><small>対象外</small></div>
    <div class="cell" style="text-align:center;"><span class="no">✗</span><br><small>対象外</small></div>
    <div class="cell" style="text-align:center;"><span class="no">✗</span><br><small>対象外</small></div>
    <div class="cell" style="text-align:center;"><span class="check">✓</span><br><small>主用途</small></div>
    <!-- Format -->
    <div class="cell plane-label">メッセージ形式</div>
    <div class="cell"><small>XML / SOAP<br>HTTP-POST</small></div>
    <div class="cell"><small>HTTP リダイレクト<br>JSON / JWT</small></div>
    <div class="cell"><small>HTTP リダイレクト<br>JSON / JWT</small></div>
    <div class="cell"><small>REST API<br>JSON</small></div>
    <!-- Year -->
    <div class="cell plane-label">標準化年</div>
    <div class="cell"><small>2005年<br>OASIS</small></div>
    <div class="cell"><small>2012年<br>IETF RFC 6749</small></div>
    <div class="cell"><small>2014年<br>OpenID Foundation</small></div>
    <div class="cell"><small>2015年<br>IETF RFC 7644</small></div>
    <!-- Typical IdP -->
    <div class="cell plane-label">主な IdP/製品</div>
    <div class="cell"><small>Entra ID, Okta, ADFS, PingFederate</small></div>
    <div class="cell"><small>Entra ID, Okta, Google, Auth0</small></div>
    <div class="cell"><small>Entra ID, Okta, Keycloak</small></div>
    <div class="cell"><small>Entra ID, Okta, SailPoint, Saviynt</small></div>
  </div>

  <div class="callout info">
    <span class="icon">💡</span>
    <div>
      <strong>重要な原則：</strong> 1つのシステムで複数プロトコルを組み合わせるのが現代の正解。
      典型例は「OIDC で SSO → OAuth 2.0 で API 保護 → SCIM でアカウント自動同期」。
      SAML は既存レガシー連携の維持目的に限定し、新規構築は OIDC/OAuth 2.0 を優先する。
    </div>
  </div>
</section>

<!-- ================================================================
     Section 2: SAML 2.0 詳解
     ================================================================ -->
<section id="saml">
  <h2><span class="sec-num">2</span>SAML 2.0 詳解</h2>

  <div class="proto-card saml">
    <div class="card-header">
      <span style="font-size:20px;">🏛</span>
      SAML 2.0（Security Assertion Markup Language）— 2005年 OASIS 標準
    </div>
    <div class="card-body">
      <p>
        SAML は、<strong>異なる組織間で認証情報（アサーション）を XML で交換する</strong>フェデレーション標準。
        「ユーザーが既にログイン済みであること」を信頼できる形で伝搬し、
        複数システムへの SSO（シングルサインオン）を実現する。
        2005年の設計当初からエンタープライズ用途を前提としており、
        日本の大手企業・官公庁が採用したレガシー SaaS（Salesforce, SAP, ServiceNow 旧版等）の多くが SAML のみに対応している。
      </p>

      <h3>登場人物と用語</h3>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:12px 0;">
        <div style="background:var(--saml-light);border:1px solid #fed7aa;border-radius:8px;padding:12px 14px;">
          <div style="font-weight:700;color:var(--saml-dark);font-size:13px;margin-bottom:4px;">Principal（主体）</div>
          <div style="font-size:12px;color:#374151;">認証を受けるエンドユーザー。ブラウザを通じてリソースにアクセスする。</div>
        </div>
        <div style="background:var(--saml-light);border:1px solid #fed7aa;border-radius:8px;padding:12px 14px;">
          <div style="font-weight:700;color:var(--saml-dark);font-size:13px;margin-bottom:4px;">IdP（Identity Provider）</div>
          <div style="font-size:12px;color:#374151;">ユーザーを認証し SAML アサーションを発行する。Entra ID / Okta / ADFS が代表例。</div>
        </div>
        <div style="background:var(--saml-light);border:1px solid #fed7aa;border-radius:8px;padding:12px 14px;">
          <div style="font-weight:700;color:var(--saml-dark);font-size:13px;margin-bottom:4px;">SP（Service Provider）</div>
          <div style="font-size:12px;color:#374151;">リソースを提供する側。IdP からのアサーションを検証してアクセスを許可する。</div>
        </div>
      </div>
      <div style="margin:12px 0;padding:10px 14px;background:var(--saml-light);border-radius:8px;font-size:13px;color:#374151;">
        <strong>アサーション（Assertion）</strong>とは：「Aさんは 2026-04-07T09:00Z に IdP で認証された。
        メールアドレスは a@corp.jp。グループは admin」という形式で発行される署名付き XML 文書。
        SP はこの署名を検証して信頼性を確認する。
      </div>

      <h3>① SP-initiated SSO フロー（最も一般的）</h3>
      <div class="flow-box">
        <div class="flow-title">SP 起点の SSO — ユーザーが SP に直接アクセスした場合</div>
        <div class="flow-row">
          <div class="flow-node user">ユーザー<br><small style="font-size:10px;">ブラウザ</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node sp">SP<br><small style="font-size:10px;">例: Salesforce</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node idp">IdP<br><small style="font-size:10px;">例: Entra ID</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node sp">SP<br><small style="font-size:10px;">アサーション検証</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node resource">リソース<br><small style="font-size:10px;">アクセス許可</small></div>
        </div>
        <div style="margin-top:16px;">
          <div class="flow-step">
            <div class="step-num">1</div>
            <div class="step-desc"><strong>リクエスト：</strong> ユーザーが SP の URL にアクセス。SP はユーザーが未認証であることを検出し、<strong>AuthnRequest（XML）</strong>を生成して IdP へリダイレクト。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">2</div>
            <div class="step-desc"><strong>認証：</strong> IdP がユーザーを認証（パスワード・MFA 等）。認証成功後、<strong>SAML Response（XML アサーション）</strong>を生成し、署名を付与。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">3</div>
            <div class="step-desc"><strong>ポスト：</strong> ブラウザが HTTP POST で SAML Response を SP のエンドポイント（ACS URL）に送信。アサーションは Base64 エンコード済み。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">4</div>
            <div class="step-desc"><strong>検証：</strong> SP が IdP の公開鍵でアサーションの署名を検証。Subject（ユーザー識別子）・Audience・有効期限を確認。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">5</div>
            <div class="step-desc"><strong>アクセス許可：</strong> 検証成功後、SP はセッションを確立。アサーション内の属性（roles, department 等）を元にアクセス制御を適用。</div>
          </div>
        </div>
      </div>

      <h3>② IdP-initiated SSO フロー</h3>
      <div class="flow-box">
        <div class="flow-title">IdP 起点の SSO — ポータルからアプリを起動する場合</div>
        <div class="flow-row">
          <div class="flow-node user">ユーザー<br><small style="font-size:10px;">ブラウザ</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node idp">IdP ポータル<br><small style="font-size:10px;">Entra ID / Okta</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node sp">SP<br><small style="font-size:10px;">アサーション受信</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node resource">リソース<br><small style="font-size:10px;">アクセス許可</small></div>
        </div>
        <div style="margin-top:12px;font-size:13px;color:#374151;">
          IdP ポータル（Entra ID My Apps 等）でアプリアイコンをクリックすると、
          IdP がアサーションを発行して SP に直接 POST する。
          AuthnRequest なしに開始するため、<strong>SP 側で InResponseTo の検証をスキップできる</strong>が、
          セキュリティ上 SP-initiated を推奨する設計者も多い。
        </div>
      </div>

      <h3>SAML アサーションの構造（簡略）</h3>
      <div class="code-block">
<span class="tag">&lt;samlp:Response</span> <span class="attr">xmlns:samlp</span>=<span class="val">"urn:oasis:names:tc:SAML:2.0:protocol"</span><span class="tag">&gt;</span>
  <span class="comment">&lt;!-- IdP の発行者情報 --&gt;</span>
  <span class="tag">&lt;saml:Issuer&gt;</span>https://idp.corp.jp/saml<span class="tag">&lt;/saml:Issuer&gt;</span>

  <span class="tag">&lt;saml:Assertion&gt;</span>
    <span class="comment">&lt;!-- 誰についての情報か --&gt;</span>
    <span class="tag">&lt;saml:Subject&gt;</span>
      <span class="tag">&lt;saml:NameID</span> <span class="attr">Format</span>=<span class="val">"emailAddress"</span><span class="tag">&gt;</span>user@corp.jp<span class="tag">&lt;/saml:NameID&gt;</span>
    <span class="tag">&lt;/saml:Subject&gt;</span>

    <span class="comment">&lt;!-- 有効期間 --&gt;</span>
    <span class="tag">&lt;saml:Conditions</span>
      <span class="attr">NotBefore</span>=<span class="val">"2026-04-07T09:00:00Z"</span>
      <span class="attr">NotOnOrAfter</span>=<span class="val">"2026-04-07T09:10:00Z"</span><span class="tag">&gt;</span>
      <span class="tag">&lt;saml:AudienceRestriction&gt;</span>
        <span class="tag">&lt;saml:Audience&gt;</span>https://sp.saas-app.com<span class="tag">&lt;/saml:Audience&gt;</span>
      <span class="tag">&lt;/saml:AudienceRestriction&gt;</span>
    <span class="tag">&lt;/saml:Conditions&gt;</span>

    <span class="comment">&lt;!-- 属性（グループ・部門等）--&gt;</span>
    <span class="tag">&lt;saml:AttributeStatement&gt;</span>
      <span class="tag">&lt;saml:Attribute</span> <span class="attr">Name</span>=<span class="val">"groups"</span><span class="tag">&gt;</span>
        <span class="tag">&lt;saml:AttributeValue&gt;</span>admin<span class="tag">&lt;/saml:AttributeValue&gt;</span>
      <span class="tag">&lt;/saml:Attribute&gt;</span>
    <span class="tag">&lt;/saml:AttributeStatement&gt;</span>
  <span class="tag">&lt;/saml:Assertion&gt;</span>
  <span class="comment">&lt;!-- ds:Signature — IdP の秘密鍵による署名 --&gt;</span>
<span class="tag">&lt;/samlp:Response&gt;</span>
      </div>

      <div class="sw-grid">
        <div class="sw-box strength">
          <h4>強み（Strengths）</h4>
          <ul>
            <li>エンタープライズ実績 20年以上</li>
            <li>豊富な属性（グループ・役職等）を伝搬可能</li>
            <li>フェデレーション（B2B 連携）に対応</li>
            <li>日本の大手 SaaS との接続実績が豊富</li>
            <li>Entra ID / Okta / ADFS で安定サポート</li>
            <li>ベンダーメタデータ交換による設定標準化</li>
          </ul>
        </div>
        <div class="sw-box weakness">
          <h4>弱み（Weaknesses）</h4>
          <ul>
            <li>XML／SOAP の実装複雑性が高い</li>
            <li>ブラウザ依存（モバイル・API 非対応）</li>
            <li>API アクセストークン発行機能なし</li>
            <li>デバッグに専門知識が必要</li>
            <li>標準化が 2005年のため新機能拡張が遅い</li>
            <li>セッション管理は SP に委ねられ統一困難</li>
          </ul>
        </div>
      </div>

      <div class="callout warn">
        <span class="icon">⚠️</span>
        <div>
          <strong>日本企業での採用状況：</strong>
          2015年前後に SaaS 導入した企業の多くが SAML SSO を採用。
          現在も Salesforce・SAP S/4HANA・ServiceNow・Workday との連携では SAML が主流。
          新規システムでは OIDC への移行が進んでいるが、<strong>既存 SAML 連携は最低 5〜10年は維持が必要</strong>なケースが多い。
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ================================================================
     Section 3: OIDC / OAuth 2.0 詳解
     ================================================================ -->
<section id="oidc">
  <h2><span class="sec-num">3</span>OpenID Connect / OAuth 2.0 詳解</h2>

  <div class="proto-card oidc">
    <div class="card-header">
      <span style="font-size:20px;">🔐</span>
      OAuth 2.0（RFC 6749）＋ OpenID Connect 1.0 — 2012〜2014年 IETF/OpenID Foundation 標準
    </div>
    <div class="card-body">

      <div class="callout info">
        <span class="icon">📌</span>
        <div>
          <strong>よくある誤解：</strong>
          「OAuth 2.0 は認証プロトコルだ」—— これは<strong>誤り</strong>。
          OAuth 2.0 は<strong>認可フレームワーク</strong>であり、「Aアプリが Bサービスのデータに、ユーザーの許可を得てアクセスする」ことを標準化する。
          認証（誰であるか）を扱うのは、OAuth 2.0 の上に構築された <strong>OpenID Connect（OIDC）</strong> だ。
        </div>
      </div>

      <h3>OAuth 2.0 の役割と登場人物</h3>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0;">
        <div style="background:var(--oidc-light);border:1px solid #bfdbfe;border-radius:8px;padding:12px 14px;">
          <div style="font-weight:700;color:var(--oidc-dark);font-size:12px;margin-bottom:4px;">Resource Owner</div>
          <div style="font-size:12px;color:#374151;">データの所有者（通常エンドユーザー）。アクセスを許可する主体。</div>
        </div>
        <div style="background:var(--oidc-light);border:1px solid #bfdbfe;border-radius:8px;padding:12px 14px;">
          <div style="font-weight:700;color:var(--oidc-dark);font-size:12px;margin-bottom:4px;">Client</div>
          <div style="font-size:12px;color:#374151;">リソースにアクセスしたいアプリ（Web アプリ・SPA・モバイル等）。</div>
        </div>
        <div style="background:var(--oidc-light);border:1px solid #bfdbfe;border-radius:8px;padding:12px 14px;">
          <div style="font-weight:700;color:var(--oidc-dark);font-size:12px;margin-bottom:4px;">Authorization Server</div>
          <div style="font-size:12px;color:#374151;">トークンを発行する認可サーバー。Entra ID / Okta / Keycloak 等。</div>
        </div>
        <div style="background:var(--oidc-light);border:1px solid #bfdbfe;border-radius:8px;padding:12px 14px;">
          <div style="font-weight:700;color:var(--oidc-dark);font-size:12px;margin-bottom:4px;">Resource Server</div>
          <div style="font-size:12px;color:#374151;">保護された API（Microsoft Graph, Salesforce API 等）。</div>
        </div>
      </div>

      <h3>Authorization Code Flow with PKCE（推奨フロー）</h3>
      <div class="flow-box">
        <div class="flow-title">Authorization Code + PKCE — Web アプリ・SPA・モバイルアプリ共通の推奨フロー</div>
        <div class="flow-row">
          <div class="flow-node client">クライアント<br><small style="font-size:10px;">Web / SPA</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node authz">認可サーバー<br><small style="font-size:10px;">Entra ID</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node client">クライアント<br><small style="font-size:10px;">コード受信</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node authz">トークンエンドポイント<br><small style="font-size:10px;">Token 発行</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node resource">API<br><small style="font-size:10px;">保護されたリソース</small></div>
        </div>
        <div style="margin-top:16px;">
          <div class="flow-step">
            <div class="step-num">1</div>
            <div class="step-desc"><strong>PKCE 準備：</strong> クライアントが <code style="background:#f1f5f9;padding:1px 4px;border-radius:3px;">code_verifier</code>（ランダム値）を生成し、その SHA-256 ハッシュ <code style="background:#f1f5f9;padding:1px 4px;border-radius:3px;">code_challenge</code> を計算。認可リクエストに <code>code_challenge</code> を添付して認可サーバーへリダイレクト。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">2</div>
            <div class="step-desc"><strong>ユーザー認証・同意：</strong> 認可サーバーがユーザーを認証（ID/PW + MFA）し、要求スコープへの同意を確認。認証成功後、<strong>認可コード（Authorization Code）</strong>を生成してクライアントの redirect_uri にリダイレクト。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">3</div>
            <div class="step-desc"><strong>トークン交換：</strong> クライアントが認可コードと <code>code_verifier</code> をトークンエンドポイントに POST。認可サーバーが <code>code_verifier</code> を検証（PKCE）し、<strong>Access Token・Refresh Token・ID Token</strong> を返却。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">4</div>
            <div class="step-desc"><strong>API 呼び出し：</strong> クライアントが <code>Authorization: Bearer &lt;access_token&gt;</code> ヘッダーを付与して Resource Server（API）を呼び出す。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">5</div>
            <div class="step-desc"><strong>トークン検証：</strong> Resource Server が Access Token の署名・有効期限・スコープを検証しレスポンスを返す。Access Token 期限切れ後は Refresh Token で再取得。</div>
          </div>
        </div>
      </div>

      <h3>3種類のトークン</h3>
      <div class="token-row">
        <div class="token-card">
          <div class="t-header" style="background:#2563eb;">Access Token</div>
          <div class="t-body">
            <strong>用途：</strong>API への認可証明<br>
            <strong>形式：</strong>JWT または Opaque<br>
            <strong>有効期間：</strong>短め（1時間程度）<br>
            <strong>含む情報：</strong>sub, scope, exp, iss<br>
            <strong>注意：</strong>リボーク不可（JWTの場合）
          </div>
        </div>
        <div class="token-card">
          <div class="t-header" style="background:#7c3aed;">ID Token（OIDC）</div>
          <div class="t-body">
            <strong>用途：</strong>ユーザー認証の証明<br>
            <strong>形式：</strong>JWT（署名必須）<br>
            <strong>有効期間：</strong>短め（1時間程度）<br>
            <strong>含む情報：</strong>sub, email, name, iss, aud<br>
            <strong>注意：</strong>API 呼び出しには使用しない
          </div>
        </div>
        <div class="token-card">
          <div class="t-header" style="background:#059669;">Refresh Token</div>
          <div class="t-body">
            <strong>用途：</strong>Access Token の再取得<br>
            <strong>形式：</strong>Opaque（秘密値）<br>
            <strong>有効期間：</strong>長め（日〜月単位）<br>
            <strong>含む情報：</strong>不透明（サーバー管理）<br>
            <strong>注意：</strong>安全なストレージに保管必須
          </div>
        </div>
      </div>

      <h3>JWT（JSON Web Token）の構造</h3>
      <div class="code-block">
<span class="comment">// ヘッダー (Base64URL デコード後)</span>
{ <span class="attr">"alg"</span>: <span class="val">"RS256"</span>, <span class="attr">"typ"</span>: <span class="val">"JWT"</span>, <span class="attr">"kid"</span>: <span class="val">"ABC123"</span> }

<span class="comment">// ペイロード (Base64URL デコード後)</span>
{
  <span class="attr">"iss"</span>: <span class="val">"https://login.microsoftonline.com/{tenant}/v2.0"</span>,
  <span class="attr">"sub"</span>: <span class="val">"abc123def456"</span>,         <span class="comment">// ユーザー固有 ID</span>
  <span class="attr">"aud"</span>: <span class="val">"api://myapp.corp.jp"</span>,  <span class="comment">// 受信者（Resource Server）</span>
  <span class="attr">"exp"</span>: <span class="val">1744000000</span>,              <span class="comment">// Unix タイムスタンプ</span>
  <span class="attr">"iat"</span>: <span class="val">1743996400</span>,              <span class="comment">// 発行時刻</span>
  <span class="attr">"scp"</span>: <span class="val">"User.Read Mail.Read"</span>, <span class="comment">// 付与スコープ</span>
  <span class="attr">"roles"</span>: [<span class="val">"Admin"</span>, <span class="val">"Reader"</span>]  <span class="comment">// アプリロール</span>
}

<span class="comment">// 署名: Header + Payload を IdP の秘密鍵（RSA/EC）で署名</span>
      </div>

      <div class="sw-grid">
        <div class="sw-box strength">
          <h4>強み（Strengths）</h4>
          <ul>
            <li>モバイル・SPA・API 保護すべてに対応</li>
            <li>JSON / HTTP ベースで実装が容易</li>
            <li>スコープ・クレームで細粒度の認可が可能</li>
            <li>標準ライブラリが全言語で整備済み</li>
            <li>SaaS の新規対応はほぼ OIDC に移行済み</li>
            <li>PKCE により認可コード横取り攻撃を防止</li>
          </ul>
        </div>
        <div class="sw-box weakness">
          <h4>弱み（Weaknesses）</h4>
          <ul>
            <li>OAuth 2.0 単体では認証ではなく認可のみ</li>
            <li>JWT リボーク（失効）が難しい</li>
            <li>フロー選択の誤りがセキュリティリスクに</li>
            <li>レガシーアプリ（IE 依存等）では対応困難</li>
            <li>SAML に比べて大手 SaaS の古いインスタンスでは未対応</li>
          </ul>
        </div>
      </div>

      <div class="callout success">
        <span class="icon">✅</span>
        <div>
          <strong>設計推奨：</strong>
          新規 SaaS 選定では「OIDC 対応」を必須要件として RFP に明記する。
          API ゲートウェイは OAuth 2.0 Bearer Token による保護を標準化し、
          Entra ID または Okta を Authorization Server として一元化する。
          社内 API も含め「すべての API コールにアクセストークン検証」を原則とする。
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ================================================================
     Section 4: SCIM 2.0 詳解
     ================================================================ -->
<section id="scim">
  <h2><span class="sec-num">4</span>SCIM 2.0 詳解</h2>

  <div class="proto-card scim">
    <div class="card-header">
      <span style="font-size:20px;">🔄</span>
      SCIM 2.0（System for Cross-domain Identity Management）— 2015年 IETF RFC 7643/7644
    </div>
    <div class="card-body">
      <p>
        SCIM は<strong>ユーザー・グループのプロビジョニング（作成・更新・削除）を自動化するための REST API 標準</strong>。
        認証や認可は対象外。人事システム（HR）から IdP へのアカウント同期、
        IdP から SaaS へのアカウント伝搬、退職者の一括無効化など、
        「JML（Joiner-Mover-Leaver）プロセス」の自動化に特化する。
      </p>

      <h3>SCIM が解決する課題</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0 20px;">
        <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:14px 16px;">
          <div style="font-weight:700;color:#c2410c;font-size:13px;margin-bottom:8px;">❌ SCIM なしの世界</div>
          <div style="font-size:12px;color:#374151;line-height:1.7;">
            ・退職者が翌日も SaaS にログインできる<br>
            ・ID/PW をメールで配布する手動オンボード<br>
            ・部署異動後も旧部署のデータにアクセス可能<br>
            ・監査時に「誰が何にアクセスできるか」不明<br>
            ・アカウント削除漏れによる不正アクセスリスク
          </div>
        </div>
        <div style="background:var(--scim-light);border:1px solid #86efac;border-radius:8px;padding:14px 16px;">
          <div style="font-weight:700;color:var(--scim-dark);font-size:13px;margin-bottom:8px;">✅ SCIM ありの世界</div>
          <div style="font-size:12px;color:#374151;line-height:1.7;">
            ・HR での退職処理 → 30分以内に全 SaaS 無効化<br>
            ・入社当日から必要なアプリにアクセス可能<br>
            ・役職変更 → 権限が自動更新される<br>
            ・全 SaaS のアカウント状態を IdP で一元管理<br>
            ・IGA（ガバナンス）ツールがリアルタイム把握
          </div>
        </div>
      </div>

      <h3>SCIM 2.0 のアーキテクチャ</h3>
      <div class="flow-box">
        <div class="flow-title">SCIM プロビジョニング フロー — HR → IdP → SaaS</div>
        <div class="flow-row">
          <div class="flow-node hr">HRシステム<br><small style="font-size:10px;">SAP/Workday</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node idp">IdP<br><small style="font-size:10px;">Entra ID / Okta</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node scim-client">SCIMクライアント<br><small style="font-size:10px;">プロビジョニング</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-node scim-server">SCIMサーバー<br><small style="font-size:10px;">SaaS / アプリ</small></div>
        </div>
        <div style="margin-top:16px;">
          <div class="flow-step">
            <div class="step-num">1</div>
            <div class="step-desc"><strong>HR イベント：</strong> 人事システムで「入社」「部署異動」「退職」のイベントが発生。IdP（Entra ID 等）がユーザーレコードを更新。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">2</div>
            <div class="step-desc"><strong>プロビジョニングエンジン起動：</strong> IdP 内の SCIM クライアントが変更を検出し、対象 SaaS の SCIM エンドポイントへ HTTP リクエストを送信。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">3</div>
            <div class="step-desc"><strong>CRUD 操作：</strong> 入社 → POST /Users、情報更新 → PUT/PATCH /Users/{id}、退職 → DELETE または active=false で PATCH。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">4</div>
            <div class="step-desc"><strong>グループ同期：</strong> SCIM /Groups エンドポイントでグループメンバーシップも同期。SaaS 側のロール割当に反映。</div>
          </div>
          <div class="flow-step">
            <div class="step-num">5</div>
            <div class="step-desc"><strong>確認・監査：</strong> IGA ツール（SailPoint, Saviynt 等）が SCIM GET でアカウント状態を定期確認し、棚卸・認定プロセスに使用。</div>
          </div>
        </div>
      </div>

      <h3>SCIM リソース（RFC 7643 定義）</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0;">
        <div class="scim-resource">
          <h4>User リソース（/scim/v2/Users）</h4>
          <div class="code-block" style="margin:0;padding:10px 12px;font-size:11px;">
{
  <span class="attr">"schemas"</span>: [<span class="val">"urn:ietf:params:scim:schemas:core:2.0:User"</span>],
  <span class="attr">"id"</span>: <span class="val">"abc-123"</span>,
  <span class="attr">"userName"</span>: <span class="val">"user@corp.jp"</span>,
  <span class="attr">"displayName"</span>: <span class="val">"山田 太郎"</span>,
  <span class="attr">"active"</span>: <span class="val">true</span>,
  <span class="attr">"emails"</span>: [{<span class="attr">"value"</span>: <span class="val">"user@corp.jp"</span>, <span class="attr">"primary"</span>: <span class="val">true</span>}],
  <span class="attr">"title"</span>: <span class="val">"シニアエンジニア"</span>,
  <span class="attr">"department"</span>: <span class="val">"情報システム部"</span>
}
          </div>
        </div>
        <div class="scim-resource">
          <h4>Group リソース（/scim/v2/Groups）</h4>
          <div class="code-block" style="margin:0;padding:10px 12px;font-size:11px;">
{
  <span class="attr">"schemas"</span>: [<span class="val">"urn:ietf:params:scim:schemas:core:2.0:Group"</span>],
  <span class="attr">"id"</span>: <span class="val">"grp-456"</span>,
  <span class="attr">"displayName"</span>: <span class="val">"情報システム部"</span>,
  <span class="attr">"members"</span>: [
    {<span class="attr">"value"</span>: <span class="val">"abc-123"</span>, <span class="attr">"display"</span>: <span class="val">"山田 太郎"</span>},
    {<span class="attr">"value"</span>: <span class="val">"xyz-789"</span>, <span class="attr">"display"</span>: <span class="val">"鈴木 花子"</span>}
  ]
}
          </div>
        </div>
      </div>

      <h3>SCIM HTTP メソッドと操作</h3>
      <table class="cmp-table" style="margin:12px 0;">
        <thead>
          <tr>
            <th style="background:#1e293b;">操作</th>
            <th style="background:#1e293b;">HTTP メソッド</th>
            <th style="background:#1e293b;">エンドポイント例</th>
            <th style="background:#1e293b;">ユースケース</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>ユーザー作成</td>
            <td><code>POST</code></td>
            <td><code>/scim/v2/Users</code></td>
            <td>入社・新規アカウント</td>
          </tr>
          <tr>
            <td>ユーザー取得</td>
            <td><code>GET</code></td>
            <td><code>/scim/v2/Users/{id}</code></td>
            <td>棚卸・監査</td>
          </tr>
          <tr>
            <td>完全更新</td>
            <td><code>PUT</code></td>
            <td><code>/scim/v2/Users/{id}</code></td>
            <td>属性全置換</td>
          </tr>
          <tr>
            <td>部分更新</td>
            <td><code>PATCH</code></td>
            <td><code>/scim/v2/Users/{id}</code></td>
            <td>部署異動・無効化</td>
          </tr>
          <tr>
            <td>ユーザー削除</td>
            <td><code>DELETE</code></td>
            <td><code>/scim/v2/Users/{id}</code></td>
            <td>退職（完全削除）</td>
          </tr>
          <tr>
            <td>一覧・検索</td>
            <td><code>GET</code></td>
            <td><code>/scim/v2/Users?filter=...</code></td>
            <td>棚卸・差分確認</td>
          </tr>
        </tbody>
      </table>

      <div class="sw-grid">
        <div class="sw-box strength">
          <h4>強み（Strengths）</h4>
          <ul>
            <li>JML プロセスを完全自動化できる</li>
            <li>REST + JSON で実装・デバッグが容易</li>
            <li>Entra ID / Okta が標準サポート</li>
            <li>SailPoint / Saviynt の IGA とネイティブ統合</li>
            <li>人的ミスによるアカウント削除漏れを排除</li>
            <li>コンプライアンス・監査対応コストを削減</li>
          </ul>
        </div>
        <div class="sw-box weakness">
          <h4>弱み（Weaknesses）</h4>
          <ul>
            <li>認証・認可は対象外（SSO とは別途設定）</li>
            <li>SaaS 側の SCIM 実装品質にばらつきがある</li>
            <li>大量ユーザーの初期同期には時間を要する</li>
            <li>エラー処理・リトライ設計が重要</li>
            <li>オンプレミスアプリへの適用には追加実装が必要</li>
          </ul>
        </div>
      </div>

      <div class="callout info">
        <span class="icon">🏭</span>
        <div>
          <strong>日本企業の JML 自動化：</strong>
          退職者アカウントの無効化遅延（翌営業日〜数日）は日本企業に多い課題。
          SCIM を Workday/SAP SuccessFactors と Entra ID/Okta の間に導入することで、
          HR での退職処理後 30 分以内に全連携 SaaS を無効化できる。
          この「退職即時無効化」はランサムウェア対策・内部不正防止の基本施策でもある。
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ================================================================
     Section 5: 比較表
     ================================================================ -->
<section id="comparison">
  <h2><span class="sec-num">5</span>プロトコル比較表</h2>

  <table class="cmp-table">
    <thead>
      <tr>
        <th style="background:#1e293b;width:140px;">項目</th>
        <th class="saml">SAML 2.0</th>
        <th class="oidc">OIDC / OAuth 2.0</th>
        <th class="scim">SCIM 2.0</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="row-label">主な用途</td>
        <td>エンタープライズ SSO（ブラウザ経由）、フェデレーション</td>
        <td>現代的 SSO・API 保護・モバイル認証</td>
        <td>ユーザー/グループのプロビジョニング自動化</td>
      </tr>
      <tr>
        <td class="row-label">対象プレーン</td>
        <td>認証（AuthN）、一部認可（属性経由）</td>
        <td>認証（OIDC）＋ 認可（OAuth 2.0）</td>
        <td>プロビジョニング（JML）</td>
      </tr>
      <tr>
        <td class="row-label">メッセージ形式</td>
        <td>XML / Base64 / HTTP-POST or Redirect</td>
        <td>JSON / JWT / HTTP(S) リダイレクト</td>
        <td>JSON / REST API（HTTP CRUD）</td>
      </tr>
      <tr>
        <td class="row-label">標準化年</td>
        <td>2005年（OASIS）</td>
        <td>OAuth 2.0: 2012年（IETF）<br>OIDC: 2014年（OpenID Foundation）</td>
        <td>2015年（IETF RFC 7643/7644）</td>
      </tr>
      <tr>
        <td class="row-label">主要実装</td>
        <td>Entra ID, Okta, ADFS, PingFederate, Shibboleth</td>
        <td>Entra ID, Okta, Keycloak, Auth0, Google</td>
        <td>Entra ID, Okta, SailPoint, Saviynt, Ping</td>
      </tr>
      <tr>
        <td class="row-label">モバイル対応</td>
        <td>❌ 非対応（ブラウザ前提）</td>
        <td>✅ ネイティブ対応（PKCE 必須）</td>
        <td>✅ REST のため環境非依存</td>
      </tr>
      <tr>
        <td class="row-label">API 保護</td>
        <td>❌ 非対応</td>
        <td>✅ OAuth 2.0 Bearer Token</td>
        <td>✅（SCIM 自体が API）</td>
      </tr>
      <tr>
        <td class="row-label">実装の複雑さ</td>
        <td>高（XML 署名・メタデータ交換）</td>
        <td>中（フロー選択が重要）</td>
        <td>低〜中（REST だが SaaS 実装差異あり）</td>
      </tr>
      <tr>
        <td class="row-label">セキュリティ強み</td>
        <td>XML 署名・暗号化・フェデレーション信頼</td>
        <td>PKCE・短命 Token・スコープ制限</td>
        <td>IdP 管理下でアクセストークン認証</td>
      </tr>
      <tr>
        <td class="row-label">日本市場採用</td>
        <td>既存 SaaS・大企業で広く採用<br>（2010〜2020年代前半）</td>
        <td>新規 SaaS 導入で急速に普及<br>（2020年代〜）</td>
        <td>IGA 導入企業・大規模組織で普及中</td>
      </tr>
      <tr>
        <td class="row-label">レガシー対応</td>
        <td>✅ 強み（多くのレガシー SaaS が対応）</td>
        <td>△ 新しいシステムのみ対応</td>
        <td>△ オンプレミスは追加実装が必要</td>
      </tr>
      <tr>
        <td class="row-label">推奨シーン</td>
        <td>既存 SAML SaaS との継続連携、B2B フェデレーション</td>
        <td>新規 SaaS・API ゲートウェイ・スマートフォンアプリ</td>
        <td>HR 連携・ライフサイクル自動化・IGA 統合</td>
      </tr>
    </tbody>
  </table>
</section>

<!-- ================================================================
     Section 6: 選択ガイド
     ================================================================ -->
<section id="guide">
  <h2><span class="sec-num">6</span>シナリオ別 選択ガイド</h2>

  <p>プロトコル選択は「現在の課題」と「接続先システムの対応状況」で決まる。以下のシナリオ別ガイドを参照し、適切なプロトコル（またはその組み合わせ）を選択する。</p>

  <div class="scenario-grid">

    <div class="scenario-card">
      <div class="scenario-q">
        <div class="q-icon">Q1</div>
        <div>新しい SaaS（Salesforce / ServiceNow / Slack 等）の SSO を導入したい</div>
      </div>
      <div class="answer">
        <span class="proto-tag oidc">OIDC 優先</span> <span class="proto-tag saml">SAML（レガシー必要時）</span><br>
        まず SaaS が OIDC/OAuth 2.0 に対応しているか確認。
        現代的な SaaS はほぼ OIDC に対応しているため OIDC を選択。
        OIDC 未対応の場合のみ SAML を使用する。
        Entra ID または Okta をハブとして統一し、
        プロトコル混在を IdP 側で吸収する設計が推奨。
      </div>
    </div>

    <div class="scenario-card">
      <div class="scenario-q">
        <div class="q-icon">Q2</div>
        <div>10年前に導入したレガシー SaaS との連携を維持したい</div>
      </div>
      <div class="answer">
        <span class="proto-tag saml">SAML 継続</span><br>
        レガシーシステムが SAML のみ対応の場合、無理に OIDC へ移行しない。
        IdP 側で SAML フェデレーションを維持しつつ、
        次期リプレース時に OIDC 対応を選定条件に加える。
        SAML 設定は IdP のテンプレート（Entra ID Gallery 等）を活用し、
        手動 XML 設定を最小化する。
      </div>
    </div>

    <div class="scenario-card">
      <div class="scenario-q">
        <div class="q-icon">Q3</div>
        <div>社内・社外向け API を保護し、マイクロサービス間の認可を制御したい</div>
      </div>
      <div class="answer">
        <span class="proto-tag oidc">OAuth 2.0</span><br>
        API ゲートウェイ（APIM / Kong / AWS API Gateway 等）に
        OAuth 2.0 Bearer Token 検証を組み込む。
        サービス間通信には Client Credentials フローを使用。
        スコープ・ロールでリソース単位の細粒度アクセス制御を実装。
        全 API に「認可なき呼び出しは 401 返却」を標準とする。
      </div>
    </div>

    <div class="scenario-card">
      <div class="scenario-q">
        <div class="q-icon">Q4</div>
        <div>入退社・部署異動のたびに手動でアカウントを作成・削除しているのを自動化したい</div>
      </div>
      <div class="answer">
        <span class="proto-tag scim">SCIM</span><br>
        HR システム（Workday / SAP SuccessFactors / COMPANY HR 等）と
        IdP（Entra ID / Okta）を接続し、
        JML イベントを SCIM で伝搬する。
        さらに IdP から各 SaaS へ SCIM プロビジョニングを構成。
        退職者の全 SaaS 無効化を 30 分以内に自動化できる。
      </div>
    </div>

    <div class="scenario-card">
      <div class="scenario-q">
        <div class="q-icon">Q5</div>
        <div>IGA（アクセスガバナンス）ツールを導入し、アクセス認定・棚卸を自動化したい</div>
      </div>
      <div class="answer">
        <span class="proto-tag combo">SCIM + OIDC 組み合わせ</span><br>
        IGA ツール（SailPoint Identity Security Cloud, Saviynt 等）が
        SCIM GET で全 SaaS のアカウント状態を収集し、
        認定（Access Review）プロセスを実施。
        IGA ツール自体の認証には OIDC SSO を使用。
        Entra ID を Authoritative Source として IdP + SCIM の統合ポイントとする。
      </div>
    </div>

    <div class="scenario-card">
      <div class="scenario-q">
        <div class="q-icon">Q6</div>
        <div>取引先・パートナー企業のユーザーに自社システムへのアクセスを安全に提供したい</div>
      </div>
      <div class="answer">
        <span class="proto-tag saml">SAML フェデレーション</span> または <span class="proto-tag oidc">OIDC</span><br>
        B2B フェデレーションでは SAML または OIDC どちらも使用可能。
        相手組織が Entra ID / Okta の場合は OIDC 連携（Entra B2B / Okta Org2Org）が容易。
        相手が ADFS や古い IdP の場合は SAML フェデレーション。
        ゲストアカウントのライフサイクル管理には SCIM も組み合わせる。
      </div>
    </div>

    <div class="scenario-card">
      <div class="scenario-q">
        <div class="q-icon">Q7</div>
        <div>スマートフォンアプリに社内システムへのセキュアなログインを実装したい</div>
      </div>
      <div class="answer">
        <span class="proto-tag oidc">OIDC + PKCE</span><br>
        モバイルアプリでは必ず PKCE 付き Authorization Code Flow を使用。
        Implicit Flow は使用禁止（RFC 6749 で非推奨）。
        Refresh Token はデバイスのセキュアストレージ（iOS Keychain / Android Keystore）に保管。
        Entra ID や Okta の Mobile SDK（MSAL, okta-auth-js）の活用が最短経路。
      </div>
    </div>

    <div class="scenario-card">
      <div class="scenario-q">
        <div class="q-icon">Q8</div>
        <div>ゼロトラスト推進として、すべてのアクセスに「継続的な認証・認可」を適用したい</div>
      </div>
      <div class="answer">
        <span class="proto-tag oidc">OIDC + CAE</span> <span class="proto-tag scim">SCIM</span><br>
        Entra ID の CAE（Continuous Access Evaluation）と
        OIDC を組み合わせることで、
        パスワード変更・MFA 再要求・デバイスコンプライアンス違反を
        リアルタイムでセッションに反映可能。
        SCIM で退職者の即時無効化と組み合わせ、
        「アクセスの継続的検証」を実現する。
      </div>
    </div>

  </div>

  <div class="callout success">
    <span class="icon">📋</span>
    <div>
      <strong>アーキテクチャ設計の原則：</strong><br>
      ① <strong>新規 SaaS 導入では OIDC 対応を選定必須条件</strong>にする（RFP に明記）。<br>
      ② <strong>SAML は既存レガシー連携の維持目的のみ</strong>。新規設計では使わない。<br>
      ③ <strong>すべての API を OAuth 2.0 で保護</strong>し、SAML アサーションを API 認可に転用しない。<br>
      ④ <strong>SCIM を「認証の前提」</strong>として位置付ける——ユーザーが存在しなければ SSO も機能しない。<br>
      ⑤ Entra ID または Okta を <strong>すべてのプロトコルのハブ</strong>として統一し、分散管理を防ぐ。
    </div>
  </div>
</section>

<!-- ================================================================
     Section 7: 日本企業の実態
     ================================================================ -->
<section id="japan">
  <h2><span class="sec-num">7</span>日本企業における実態と移行の考え方</h2>

  <h3>現状の典型的な構成（2025〜2026年）</h3>
  <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:20px 24px;margin:16px 0;">
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;font-size:13px;">
      <div>
        <div style="font-weight:700;color:var(--saml-dark);margin-bottom:8px;font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">SAML 連携中のシステム</div>
        <ul style="list-style:none;padding:0;color:#374151;line-height:2;">
          <li>• Salesforce（Sales Cloud / Service Cloud）</li>
          <li>• SAP S/4HANA / SuccessFactors</li>
          <li>• ServiceNow（旧バージョン）</li>
          <li>• Workday</li>
          <li>• Box / Dropbox Business</li>
          <li>• 社内 SharePoint / Confluence</li>
        </ul>
      </div>
      <div>
        <div style="font-weight:700;color:var(--oidc-dark);margin-bottom:8px;font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">OIDC/OAuth 対応済み</div>
        <ul style="list-style:none;padding:0;color:#374151;line-height:2;">
          <li>• Microsoft 365 / Teams</li>
          <li>• Google Workspace</li>
          <li>• Slack（Enterprise Grid）</li>
          <li>• GitHub Enterprise</li>
          <li>• Zoom</li>
          <li>• 新規開発の社内 API</li>
        </ul>
      </div>
      <div>
        <div style="font-weight:700;color:var(--scim-dark);margin-bottom:8px;font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">SCIM 対応状況</div>
        <ul style="list-style:none;padding:0;color:#374151;line-height:2;">
          <li>• Entra ID ↔ Salesforce: 対応済</li>
          <li>• Entra ID ↔ ServiceNow: 対応済</li>
          <li>• Okta ↔ Slack: 対応済</li>
          <li>• 国産パッケージへの対応: △</li>
          <li>• オンプレミス業務系: 未対応多数</li>
          <li>• IGA 製品との連携: 普及中</li>
        </ul>
      </div>
    </div>
  </div>

  <h3>移行優先度マトリクス</h3>
  <table class="cmp-table" style="margin:16px 0;">
    <thead>
      <tr>
        <th style="background:#1e293b;">状況</th>
        <th style="background:#1e293b;">推奨アクション</th>
        <th style="background:#1e293b;">プロトコル</th>
        <th style="background:#1e293b;">優先度</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>退職者の SaaS 無効化が翌営業日以降</td>
        <td>SCIM プロビジョニング導入（Entra ID / Okta 経由）</td>
        <td><span class="proto-tag scim" style="display:inline-block;padding:2px 8px;background:var(--scim);color:#fff;border-radius:10px;font-size:11px;font-weight:700;">SCIM</span></td>
        <td style="color:#dc2626;font-weight:700;">🔴 最優先</td>
      </tr>
      <tr>
        <td>新規 SaaS 導入で SSO を検討中</td>
        <td>OIDC 対応 SaaS を選定条件に。IdP はエンタープライズ版を使用</td>
        <td><span class="proto-tag oidc" style="display:inline-block;padding:2px 8px;background:var(--oidc);color:#fff;border-radius:10px;font-size:11px;font-weight:700;">OIDC</span></td>
        <td style="color:#d97706;font-weight:700;">🟠 高優先</td>
      </tr>
      <tr>
        <td>社内 API が認証なしで呼び出し可能</td>
        <td>API ゲートウェイに OAuth 2.0 Bearer Token 検証を実装</td>
        <td><span class="proto-tag oidc" style="display:inline-block;padding:2px 8px;background:var(--oidc);color:#fff;border-radius:10px;font-size:11px;font-weight:700;">OAuth 2.0</span></td>
        <td style="color:#d97706;font-weight:700;">🟠 高優先</td>
      </tr>
      <tr>
        <td>既存 SAML SaaS が安定稼働中</td>
        <td>現状維持。次期更改時に OIDC 対応バージョンへ移行</td>
        <td><span class="proto-tag saml" style="display:inline-block;padding:2px 8px;background:var(--saml);color:#fff;border-radius:10px;font-size:11px;font-weight:700;">SAML</span></td>
        <td style="color:#16a34a;font-weight:700;">🟢 低優先</td>
      </tr>
      <tr>
        <td>IGA 未導入でアクセス棚卸が手動</td>
        <td>SailPoint / Saviynt / Entra ID Governance を評価し SCIM 連携</td>
        <td><span class="proto-tag scim" style="display:inline-block;padding:2px 8px;background:var(--scim);color:#fff;border-radius:10px;font-size:11px;font-weight:700;">SCIM</span></td>
        <td style="color:#d97706;font-weight:700;">🟠 高優先</td>
      </tr>
      <tr>
        <td>ADFS を社内で運用中（オンプレミス）</td>
        <td>Entra ID Connect Cloud Sync への移行を検討。ADFS は廃止方向で計画</td>
        <td><span class="proto-tag oidc" style="display:inline-block;padding:2px 8px;background:var(--oidc);color:#fff;border-radius:10px;font-size:11px;font-weight:700;">OIDC</span></td>
        <td style="color:#d97706;font-weight:700;">🟠 中優先</td>
      </tr>
    </tbody>
  </table>

  <div class="callout warn">
    <span class="icon">⚠️</span>
    <div>
      <strong>よくある失敗パターン：</strong>
      「SAML で SSO を入れたから ID 管理は完了」——SSO（認証）とプロビジョニング（アカウント管理）は別課題。
      SSO だけ導入して SCIM を入れないと、
      退職者アカウントが SaaS に残り続けるリスクが残る。
      「認証（SAML/OIDC）× プロビジョニング（SCIM）× 認可（OAuth 2.0）」の3層を
      セットで設計することが ID 管理基盤の本質だ。
    </div>
  </div>

  <h3>ステークホルダーへの説明テンプレート</h3>
  <div style="background:#f8fafc;border:1px solid var(--border);border-radius:10px;padding:20px 24px;margin:16px 0;">
    <div style="font-size:13px;font-weight:700;color:#475569;margin-bottom:12px;text-transform:uppercase;letter-spacing:0.06em;">経営層・ビジネス部門向け 1分説明</div>
    <div style="font-size:14px;color:#1e293b;line-height:1.8;">
      「ID 管理プロトコルには3つの役割があります。<br>
      <strong>SAML/OIDC</strong>は『社員証』にあたり、一度認証すれば複数システムにログインできます（SSO）。<br>
      <strong>OAuth 2.0</strong>は『アクセス許可証』で、アプリが必要なデータだけにアクセスできる権限を渡します。<br>
      <strong>SCIM</strong>は『社員証の自動発行・回収システム』で、入社・退社に合わせてアカウントを自動管理します。<br>
      3つがそろって初めて、セキュアで効率的な ID 管理基盤が完成します。」
    </div>
  </div>

</section>

</div><!-- /.content -->
</div><!-- /#main -->

</body>
</html>"""

with open('/home/imksoo/works/20260407_idm/02_html_decks/protocol_comparison_saml_scim_oauth.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Written {len(content)} chars, {content.count(chr(10))} lines")
