#!/usr/bin/env python3
"""
IDM Knowledge Base Viewer Builder

IDMナレッジベースのJSONファイル群から、SIerコンサルタントが顧客プレゼンに使える
視覚的に豊富な自己完結型HTMLを生成するビルドスクリプト。

使い方: python3 build_idm_viewer.py
出力:   index.html
"""

import json
from pathlib import Path

BASE_DIR = Path('/home/imksoo/works/20260407_idm')

# ─────────────────────────────────────────────────────────────────
# Data Loading
# ─────────────────────────────────────────────────────────────────

def load_all_json():
    """全JSONファイルを読み込み、パス→データのdictを返す"""
    data = {}
    for p in BASE_DIR.rglob('*.json'):
        if any(skip in str(p) for skip in ['.git', 'node_modules']):
            continue
        try:
            data[str(p.relative_to(BASE_DIR))] = json.load(open(p, encoding='utf-8'))
        except Exception:
            pass
    return data


def extract_graph(all_data):
    """全JSONのnodes/edgesを収集してECharts force graph用データに変換する"""
    TYPE_COLOR = {
        'identity_provider': '#1B4F8A',
        'product':           '#6A1B9A',
        'protocol':          '#00838F',
        'concept':           '#E65100',
        'risk':              '#C62828',
        'pattern':           '#2E7D32',
        'regulation':        '#4E342E',
    }
    node_map = {}
    edges = []
    for path, data in all_data.items():
        for node in data.get('nodes', []):
            nid = node.get('id', '')
            if nid and nid not in node_map:
                node_map[nid] = node
        for edge in data.get('edges', []):
            if edge.get('from') and edge.get('to'):
                edges.append(edge)

    echarts_nodes = []
    for nid, node in node_map.items():
        otype = node.get('object_type', 'concept')
        color = TYPE_COLOR.get(otype, '#78909C')
        size = 38 if otype == 'identity_provider' else 28 if otype == 'product' else 20
        props = node.get('properties', {})
        vendor = props.get('vendor', '') if isinstance(props, dict) else ''
        echarts_nodes.append({
            'id': nid,
            'name': node.get('label', nid),
            'category': otype,
            'symbolSize': size,
            'itemStyle': {'color': color},
            'desc': node.get('description', ''),
            'vendor': vendor,
        })

    echarts_edges = []
    for edge in edges:
        echarts_edges.append({
            'source': edge.get('from', ''),
            'target': edge.get('to', ''),
            'relationship': edge.get('relationship', ''),
            'desc': edge.get('description', ''),
            'lineStyle': {'width': 1.5, 'curveness': 0.1},
        })

    return echarts_nodes, echarts_edges


def extract_all_knowledge(all_data):
    """全JSONのknowledge[]配列を収集してカード表示用に変換する"""
    knowledge = []
    for path, data in all_data.items():
        for k in data.get('knowledge', []):
            if not isinstance(k, dict):
                continue
            topic = k.get('topic', k.get('title', k.get('id', '')))
            content = k.get('content', k.get('summary', ''))
            details_raw = k.get('details', [])
            if isinstance(details_raw, list):
                details_str = ' / '.join(str(d)[:100] for d in details_raw[:3])
            else:
                details_str = str(details_raw)[:200]
            tags = k.get('tags', [])
            if not isinstance(tags, list):
                tags = []
            # ソースパスからタグ推定
            if '04_server_auth' in path:
                tags = list(dict.fromkeys(tags + ['サーバー認証', 'Kerberos']))
            elif '06_security_hardening' in path:
                tags = list(dict.fromkeys(tags + ['セキュリティ強化', 'PAM']))
            elif '07_migration' in path:
                tags = list(dict.fromkeys(tags + ['移行', 'AD→Entra']))
            elif '05_hybrid' in path:
                tags = list(dict.fromkeys(tags + ['ハイブリッド', 'Entra連携']))
            elif '03_identity_architecture' in path:
                tags = list(dict.fromkeys(tags + ['アーキテクチャ', 'IdP']))
            knowledge.append({
                'id': k.get('id', ''),
                'topic': topic,
                'content': content,
                'details': details_str,
                'evidence_level': k.get('evidence_level', ''),
                'japan_specific': bool(k.get('japan_specific', False)),
                'tags': tags[:8],
                'category': k.get('category', ''),
                'source': path,
            })
    return knowledge


# ─────────────────────────────────────────────────────────────────
# Sample / Fallback Data for Charts
# ─────────────────────────────────────────────────────────────────

IDP_RADAR = {
    'indicators': [
        {'name': 'AD連携', 'max': 100},
        {'name': 'クラウド対応', 'max': 100},
        {'name': '日本語サポート', 'max': 100},
        {'name': 'MFA強度', 'max': 100},
        {'name': 'ガバナンス', 'max': 100},
        {'name': 'コスト競争力', 'max': 100},
    ],
    'series': [
        {'name': 'Entra ID',      'color': '#1B4F8A', 'values': [95, 90, 85, 90, 85, 70]},
        {'name': 'Okta',          'color': '#0097A7', 'values': [75, 95, 60, 90, 80, 65]},
        {'name': 'Ping Identity', 'color': '#6A1B9A', 'values': [80, 85, 55, 85, 90, 60]},
        {'name': 'JumpCloud',     'color': '#2E7D32', 'values': [70, 88, 50, 80, 70, 80]},
        {'name': 'OneLogin',      'color': '#E65100', 'values': [65, 85, 45, 75, 65, 75]},
    ],
}

PAM_RADAR = {
    'indicators': [
        {'name': 'パスワードVaulting', 'max': 100},
        {'name': 'セッション録画',     'max': 100},
        {'name': 'JIT特権',           'max': 100},
        {'name': 'Linux対応',         'max': 100},
        {'name': 'DevOps対応',        'max': 100},
        {'name': '価格競争力',         'max': 100},
        {'name': '日本実績',           'max': 100},
    ],
    'series': [
        {'name': 'CyberArk',        'color': '#C62828', 'values': [98, 95, 90, 85, 80, 40, 85]},
        {'name': 'BeyondTrust',     'color': '#1B4F8A', 'values': [90, 88, 85, 80, 75, 50, 75]},
        {'name': 'Delinea',         'color': '#6A1B9A', 'values': [88, 85, 80, 75, 70, 55, 70]},
        {'name': 'HashiCorp Vault', 'color': '#00838F', 'values': [85, 60, 88, 90, 95, 70, 60]},
        {'name': 'Microsoft内蔵',   'color': '#2E7D32', 'values': [70, 65, 75, 60, 65, 90, 90]},
    ],
}

RISK_HEATMAP = {
    'x': ['Pass-the-Hash', 'Kerberoasting', 'Golden Ticket', 'フィッシング', '内部不正', 'サプライチェーン'],
    'y': ['ドメコン', '特権アカウント', 'サービスアカウント', '一般ユーザー', '外部連携'],
    'data': [
        [0,0,95],[1,0,90],[2,0,98],[3,0,60],[4,0,70],[5,0,75],
        [0,1,88],[1,1,85],[2,1,92],[3,1,75],[4,1,82],[5,1,70],
        [0,2,80],[1,2,88],[2,2,70],[3,2,50],[4,2,60],[5,2,65],
        [0,3,40],[1,3,35],[2,3,45],[3,3,90],[4,3,78],[5,3,55],
        [0,4,50],[1,4,45],[2,4,55],[3,4,65],[4,4,70],[5,4,85],
    ],
}

FRAMEWORK_HEATMAP = {
    'x': ['MFA強制', '特権管理', 'ログ監査', '外部委託管理', '職務分離', '暗号化', '脆弱性管理'],
    'y': ['FISC', 'PCI DSS', 'JSDA', 'SWIFT CSP', 'NIST CSF', 'ISO 27001', 'NERC CIP'],
    'data': [
        [0,0,3],[1,0,3],[2,0,3],[3,0,3],[4,0,2],[5,0,3],[6,0,2],
        [0,1,3],[1,1,3],[2,1,3],[3,1,3],[4,1,3],[5,1,3],[6,1,3],
        [0,2,3],[1,2,2],[2,2,3],[3,2,3],[4,2,2],[5,2,2],[6,2,2],
        [0,3,3],[1,3,3],[2,3,3],[3,3,3],[4,3,3],[5,3,3],[6,3,3],
        [0,4,2],[1,4,2],[2,4,3],[3,4,2],[4,4,3],[5,4,2],[6,4,3],
        [0,5,2],[1,5,2],[2,5,3],[3,5,2],[4,5,2],[5,5,3],[6,5,3],
        [0,6,3],[1,6,3],[2,6,3],[3,6,2],[4,6,3],[5,6,3],[6,6,3],
    ],
    'labels': ['N/A', '任意', '推奨', '必須'],
}

SANKEY = {
    'nodes': [
        {'name': 'Azure VM'}, {'name': 'AWS EC2'}, {'name': 'GCP CE'},
        {'name': 'App Service'}, {'name': 'Lambda'}, {'name': 'AKS/EKS'}, {'name': 'Cloud Run'},
        {'name': 'Microsoft 365'}, {'name': 'Salesforce'}, {'name': 'SAP'}, {'name': 'ServiceNow'},
    ],
    'links': [
        {'source': 'Azure VM',   'target': 'App Service', 'value': 8},
        {'source': 'Azure VM',   'target': 'AKS/EKS',     'value': 6},
        {'source': 'AWS EC2',    'target': 'Lambda',       'value': 7},
        {'source': 'AWS EC2',    'target': 'AKS/EKS',     'value': 5},
        {'source': 'GCP CE',     'target': 'Cloud Run',   'value': 5},
        {'source': 'GCP CE',     'target': 'AKS/EKS',     'value': 4},
        {'source': 'App Service','target': 'Microsoft 365','value': 6},
        {'source': 'App Service','target': 'Salesforce',  'value': 4},
        {'source': 'Lambda',     'target': 'Salesforce',  'value': 5},
        {'source': 'Lambda',     'target': 'ServiceNow',  'value': 3},
        {'source': 'AKS/EKS',   'target': 'Microsoft 365','value': 4},
        {'source': 'AKS/EKS',   'target': 'SAP',          'value': 5},
        {'source': 'AKS/EKS',   'target': 'ServiceNow',  'value': 4},
        {'source': 'Cloud Run',  'target': 'Salesforce',  'value': 3},
        {'source': 'Cloud Run',  'target': 'ServiceNow',  'value': 3},
    ],
}

GANTT = [
    {'name': 'Phase 1: Entra Connect + PHS',
     'start': 0, 'end': 3, 'color': '#1B4F8A',
     'milestones': ['Entra Connect設定', 'PHS有効化', '初回同期完了'],
     'desc': 'パスワードハッシュ同期によりクラウド認証を開始。オンプレAD維持。'},
    {'name': 'Phase 2: Hybrid Join + 条件付きアクセス',
     'start': 3, 'end': 9, 'color': '#0097A7',
     'milestones': ['Hybrid Join展開', 'CA PoC', 'MFA全社展開'],
     'desc': 'デバイス管理と条件付きアクセスポリシーを実装。SSPR導入。'},
    {'name': 'Phase 3: LAPS + JIT特権管理',
     'start': 9, 'end': 18, 'color': '#2E7D32',
     'milestones': ['Windows LAPS展開', 'PIM設定', 'PAMツール評価・導入'],
     'desc': 'ローカル管理者パスワード管理とJITアクセスを確立。特権最小化。'},
    {'name': 'Phase 4: ADフリー化',
     'start': 18, 'end': 24, 'color': '#6A1B9A',
     'milestones': ['Entra Join全社展開', 'AD依存アプリ移行', 'ADサービス縮小'],
     'desc': 'オンプレミスAD依存を段階的に解消。クラウドネイティブID完成。'},
]

IDENTITY_TREE = {
    'name': 'ID主体',
    'children': [
        {'name': '社内人間', 'itemStyle': {'color': '#1B4F8A'},
         'children': [{'name': '正社員'}, {'name': '契約社員'}, {'name': 'パート/アルバイト'},
                      {'name': '出向者'}, {'name': '役員・経営陣'}]},
        {'name': '外部人間', 'itemStyle': {'color': '#6A1B9A'},
         'children': [{'name': 'SIer常駐SE'}, {'name': '派遣社員'}, {'name': '外部監査人'},
                      {'name': '顧客・パートナー'}, {'name': 'サプライヤー担当者'}]},
        {'name': '非人間（機械）', 'itemStyle': {'color': '#00838F'},
         'children': [{'name': 'サービスアカウント'}, {'name': 'マネージドID'},
                      {'name': 'APIキー/シークレット'}, {'name': 'スクリプト/Bot'}, {'name': 'バッチジョブ'}]},
        {'name': 'デバイス', 'itemStyle': {'color': '#2E7D32'},
         'children': [{'name': 'Windows PC'}, {'name': 'Mac'}, {'name': 'スマートフォン'},
                      {'name': 'IoTデバイス'}, {'name': 'サーバー'}]},
        {'name': '外部システム接続', 'itemStyle': {'color': '#E65100'},
         'children': [{'name': 'EDI連携'}, {'name': 'B2B API'}, {'name': 'フェデレーションIdP'},
                      {'name': 'SCIM Provisioning'}, {'name': 'OAuth クライアント'}]},
    ],
}

RISK_MATRIX = [
    {'subject': '正社員', 'category': '社内人間',
     'risks': 'パスワード流出, フィッシング, シャドーIT',
     'controls': 'MFA必須, セキュリティ教育, SaaS管理',
     'products': 'Entra ID MFA, Defender for Cloud Apps',
     'level': 'medium'},
    {'subject': '役員・経営陣', 'category': '社内人間',
     'risks': '標的型攻撃, ホエーリング, デバイス紛失',
     'controls': 'VIP保護, MDM強制, アクセス監視',
     'products': 'Entra ID Protection, Intune, Sentinel',
     'level': 'high'},
    {'subject': 'SIer常駐SE', 'category': '外部人間',
     'risks': '過剰権限, 退場後アカウント残存, 内部不正',
     'controls': 'JIT特権, 定期アクセスレビュー, セッション録画',
     'products': 'Entra PIM, CyberArk, BeyondTrust',
     'level': 'high'},
    {'subject': '派遣社員', 'category': '外部人間',
     'risks': '権限変更漏れ, 身元確認不足',
     'controls': '最小権限付与, 契約終了時即時失効',
     'products': 'Entra ID Governance, IGA製品',
     'level': 'medium'},
    {'subject': 'サービスアカウント', 'category': '非人間',
     'risks': 'Kerberoasting, パスワード管理不備, 長期有効期限',
     'controls': 'gMSA使用, LAPS管理, Vault保管',
     'products': 'Windows LAPS, HashiCorp Vault, CyberArk',
     'level': 'high'},
    {'subject': 'マネージドID', 'category': '非人間',
     'risks': '過剰スコープ, キーローテ不備',
     'controls': '最小権限, 自動ローテーション',
     'products': 'Entra Managed Identity, Azure Key Vault',
     'level': 'medium'},
    {'subject': 'APIキー/シークレット', 'category': '非人間',
     'risks': 'リポジトリ漏洩, 無期限有効',
     'controls': 'Vault化, TTL設定, Secrets Scanning',
     'products': 'HashiCorp Vault, Azure Key Vault, GitHub GHAS',
     'level': 'high'},
    {'subject': 'EDI連携', 'category': '外部システム',
     'risks': 'サプライチェーン攻撃, 認証情報平文保存',
     'controls': 'mTLS強制, 接続元IP制限',
     'products': 'Azure API Management, Entra B2B',
     'level': 'high'},
    {'subject': 'B2B API', 'category': '外部システム',
     'risks': 'OAuth不正, スコープ過剰',
     'controls': 'OAuth2.1強制, スコープ最小化',
     'products': 'Azure APIM, Entra External ID',
     'level': 'medium'},
]

MERMAID_FLOWS = {
    'kerberos': """sequenceDiagram
    participant C as クライアント
    participant KDC as KDC (DC)
    participant SRV as サービスサーバー
    Note over C,KDC: 1. AS-REQ (認証要求)
    C->>KDC: AS-REQ (ユーザー名 + タイムスタンプ暗号化)
    KDC-->>C: AS-REP (TGT + セッションキー)
    Note over C,KDC: 2. TGS-REQ (サービスチケット要求)
    C->>KDC: TGS-REQ (TGT + SPN指定)
    KDC-->>C: TGS-REP (サービスチケット)
    Note over C,SRV: 3. AP-REQ (サービス認証)
    C->>SRV: AP-REQ (サービスチケット + Authenticator)
    SRV-->>C: AP-REP (相互認証完了)
    Note over C,SRV: 認証完了 — リソースアクセス開始""",
    'oidc': """sequenceDiagram
    participant U as ユーザー
    participant APP as アプリ (RP)
    participant IdP as Entra ID (IdP)
    participant API as バックエンドAPI
    U->>APP: ログインボタンクリック
    APP->>IdP: 認可リクエスト (PKCE + state)
    IdP-->>U: ログイン画面 + MFAプロンプト
    U->>IdP: 認証情報 + MFA
    IdP-->>APP: 認可コード (code)
    APP->>IdP: トークン交換 (code + code_verifier)
    IdP-->>APP: id_token + access_token + refresh_token
    APP->>API: Bearer access_token
    API-->>APP: 保護されたリソース
    Note over APP,IdP: access_token有効期限切れ
    APP->>IdP: refresh_token でサイレント更新""",
    'saml': """sequenceDiagram
    participant U as ユーザー
    participant SP as サービスプロバイダー
    participant IdP as Entra ID (IdP)
    U->>SP: 保護リソースへアクセス
    SP-->>U: SAMLリクエスト (Redirect)
    U->>IdP: SAMLリクエスト転送
    IdP-->>U: 認証画面 (未認証の場合)
    U->>IdP: 認証情報 + MFA
    IdP-->>U: SAMLレスポンス (署名付きアサーション)
    U->>SP: SAMLレスポンス POST
    SP->>SP: 署名検証 + アサーション解析
    SP-->>U: ログイン完了 (セッション確立)
    Note over SP,IdP: シングルサインオン完了""",
}

DASHBOARD_STATS = [
    {'label': 'ID主体分類', 'value': '5カテゴリ', 'icon': '👥', 'color': '#1B4F8A'},
    {'label': '認証プロトコル', 'value': '10+種', 'icon': '🔐', 'color': '#0097A7'},
    {'label': 'IdP製品比較', 'value': '5製品', 'icon': '🏢', 'color': '#6A1B9A'},
    {'label': 'PAM製品比較', 'value': '5製品', 'icon': '🛡️', 'color': '#C62828'},
    {'label': '移行フェーズ', 'value': '4段階', 'icon': '🗺️', 'color': '#2E7D32'},
    {'label': 'フレームワーク', 'value': '7種対応', 'icon': '📋', 'color': '#E65100'},
]


# ─────────────────────────────────────────────────────────────────
# HTML Generation
# ─────────────────────────────────────────────────────────────────

def safe_json(obj):
    """HTML埋め込み用JSON - </script>タグを安全にエスケープ"""
    s = json.dumps(obj, ensure_ascii=False)
    s = s.replace('</', '<\\/')
    return s


def generate_html(graph_nodes, graph_edges, knowledge, all_data):
    # Serialize all data
    gn_js      = safe_json(graph_nodes)
    ge_js      = safe_json(graph_edges)
    kn_js      = safe_json(knowledge)
    idp_js     = safe_json(IDP_RADAR)
    pam_js     = safe_json(PAM_RADAR)
    risk_js    = safe_json(RISK_HEATMAP)
    fw_js      = safe_json(FRAMEWORK_HEATMAP)
    sankey_js  = safe_json(SANKEY)
    gantt_js   = safe_json(GANTT)
    tree_js    = safe_json(IDENTITY_TREE)
    matrix_js  = safe_json(RISK_MATRIX)
    flows_js   = safe_json(MERMAID_FLOWS)
    stats_js   = safe_json(DASHBOARD_STATS)

    # Build risk matrix HTML rows
    matrix_rows = []
    for row in RISK_MATRIX:
        lvl_class = 'level-high' if row['level'] == 'high' else 'level-medium'
        lvl_label = '🔴 高' if row['level'] == 'high' else '🟡 中'
        matrix_rows.append(f'''
        <tr class="{lvl_class}">
          <td><strong>{row['subject']}</strong><br><small class="badge-cat">{row['category']}</small></td>
          <td>{row['risks']}</td>
          <td>{row['controls']}</td>
          <td><small>{row['products']}</small></td>
          <td class="risk-badge">{lvl_label}</td>
        </tr>''')
    matrix_rows_html = '\n'.join(matrix_rows)

    # Dashboard stat cards
    stat_cards = []
    for s in DASHBOARD_STATS:
        stat_cards.append(f'''
        <div class="stat-card" style="border-top: 4px solid {s['color']}">
          <div class="stat-icon">{s['icon']}</div>
          <div class="stat-value" style="color:{s['color']}">{s['value']}</div>
          <div class="stat-label">{s['label']}</div>
        </div>''')
    stat_cards_html = '\n'.join(stat_cards)

    # Industry guide cards
    industry_cards = '''
    <div class="card-grid">
      <div class="info-card">
        <div class="info-card-header" style="background:#1B4F8A">🏦 金融・証券</div>
        <div class="info-card-body">
          <p><strong>主な規制:</strong> FISC安全対策基準 / JSDA / 金融庁ガイドライン</p>
          <p><strong>必須要件:</strong> MFA強制, 特権管理, 操作ログ7年保存, SOD徹底</p>
          <p><strong>重点テーマ:</strong> 証券取引系システムの内部不正防止, EDI連携先管理</p>
          <p><strong>推奨製品:</strong> Entra PIM + CyberArk + Sentinel</p>
        </div>
      </div>
      <div class="info-card">
        <div class="info-card-header" style="background:#6A1B9A">🏥 医療・製薬</div>
        <div class="info-card-body">
          <p><strong>主な規制:</strong> 医療情報システム安全管理ガイドライン / GxP</p>
          <p><strong>必須要件:</strong> 電子署名, アクセス制御, 監査証跡, 患者データ保護</p>
          <p><strong>重点テーマ:</strong> 医療機器IoT認証, 外部委託先(CRO)管理, 研究データアクセス</p>
          <p><strong>推奨製品:</strong> Entra ID + Intune + Azure AD B2B</p>
        </div>
      </div>
      <div class="info-card">
        <div class="info-card-header" style="background:#00838F">🏭 製造業</div>
        <div class="info-card-body">
          <p><strong>主な規制:</strong> ISMS / サプライチェーンセキュリティガイドライン</p>
          <p><strong>必須要件:</strong> OT/IT統合ID管理, グローバルフェデレーション, 設計データ保護</p>
          <p><strong>重点テーマ:</strong> 製造ラインIoT認証, 海外拠点統合, サプライヤー管理</p>
          <p><strong>推奨製品:</strong> Entra External ID + Okta + JumpCloud</p>
        </div>
      </div>
      <div class="info-card">
        <div class="info-card-header" style="background:#2E7D32">🏛️ 公共・官公庁</div>
        <div class="info-card-body">
          <p><strong>主な規制:</strong> 政府情報セキュリティ基準 / マイナンバー法</p>
          <p><strong>必須要件:</strong> ゼロトラスト移行, クラウド利用拡大, マイナンバー保護</p>
          <p><strong>重点テーマ:</strong> 府省庁間連携, LGWAN, 委託業者管理</p>
          <p><strong>推奨製品:</strong> Entra ID + Government Cloud対応製品</p>
        </div>
      </div>
      <div class="info-card">
        <div class="info-card-header" style="background:#E65100">⚡ エネルギー・インフラ</div>
        <div class="info-card-body">
          <p><strong>主な規制:</strong> NERC CIP / 電力インフラセキュリティガイドライン</p>
          <p><strong>必須要件:</strong> OT/ICS保護, 強制MFA, ジャンプサーバー</p>
          <p><strong>重点テーマ:</strong> 制御系システム認証, 物理-論理アクセス統合</p>
          <p><strong>推奨製品:</strong> CyberArk + Delinea + Entra PIM</p>
        </div>
      </div>
      <div class="info-card">
        <div class="info-card-header" style="background:#4E342E">🛍️ 流通・小売</div>
        <div class="info-card-body">
          <p><strong>主な規制:</strong> PCI DSS / 個人情報保護法</p>
          <p><strong>必須要件:</strong> 決済系アクセス制御, 加盟店管理, フランチャイズID統合</p>
          <p><strong>重点テーマ:</strong> 店舗スタッフ多数管理, 季節労働者, POSシステム認証</p>
          <p><strong>推奨製品:</strong> Entra ID + Okta Customer Identity</p>
        </div>
      </div>
    </div>'''

    # Scenarios section content
    scenario_cards = '''
    <div class="card-grid">
      <div class="scenario-card">
        <div class="scenario-title">🔄 AD→Entra ID 段階移行</div>
        <div class="scenario-body">
          <p>オンプレADを段階的にEntra IDへ移行するシナリオ。Entra Connectを起点にハイブリッド構成を経て最終的にADフリーを目指す4フェーズのロードマップ。</p>
          <div class="scenario-tags">
            <span class="tag">移行</span><span class="tag">ハイブリッド</span><span class="tag">Entra</span>
          </div>
        </div>
      </div>
      <div class="scenario-card">
        <div class="scenario-title">🔐 ゼロトラスト段階導入</div>
        <div class="scenario-body">
          <p>NEVER TRUST, ALWAYS VERIFYの原則をID中心で実装。MFA→条件付きアクセス→デバイスコンプライアンス→継続的評価の段階展開。</p>
          <div class="scenario-tags">
            <span class="tag">ゼロトラスト</span><span class="tag">条件付きアクセス</span>
          </div>
        </div>
      </div>
      <div class="scenario-card">
        <div class="scenario-title">🏗️ SIer常駐SE 特権管理</div>
        <div class="scenario-body">
          <p>外部SIerエンジニアへのJITアクセス付与とセッション監視。プロジェクト期間中のみ必要最小権限を付与し、終了時に自動失効するワークフロー。</p>
          <div class="scenario-tags">
            <span class="tag">PAM</span><span class="tag">JIT</span><span class="tag">外部委託</span>
          </div>
        </div>
      </div>
      <div class="scenario-card">
        <div class="scenario-title">⚙️ DevSecOps シークレット管理</div>
        <div class="scenario-body">
          <p>CI/CDパイプラインでのシークレット管理をコード外に移行。HashiCorp VaultまたはAzure Key VaultとGitHub ActionsのOIDC統合によりシークレットレス化。</p>
          <div class="scenario-tags">
            <span class="tag">DevSecOps</span><span class="tag">HashiCorp Vault</span><span class="tag">OIDC</span>
          </div>
        </div>
      </div>
      <div class="scenario-card">
        <div class="scenario-title">🌐 グローバル統合ID基盤</div>
        <div class="scenario-body">
          <p>海外拠点含む多国間でのID統合。各国のADフォレストをEntra IDテナントに集約し、グローバルSSO・統一条件付きアクセスを実現。</p>
          <div class="scenario-tags">
            <span class="tag">グローバル</span><span class="tag">フェデレーション</span><span class="tag">SSO</span>
          </div>
        </div>
      </div>
      <div class="scenario-card">
        <div class="scenario-title">🔄 ランサムウェア対策強化</div>
        <div class="scenario-body">
          <p>ランサムウェアの横展開を阻止するID中心防衛戦略。SMB/RDP制限、管理者アカウント分離、LAPS展開、バックアップアカウント保護を組み合わせる。</p>
          <div class="scenario-tags">
            <span class="tag">ランサムウェア</span><span class="tag">横展開阻止</span><span class="tag">LAPS</span>
          </div>
        </div>
      </div>
    </div>'''

    # Build architecture section content
    architecture_content = '''
    <div class="arch-grid">
      <div class="arch-pattern">
        <div class="arch-title">🏗️ Lift &amp; Shift パターン</div>
        <div class="arch-desc">AD構成を変えずにAzure VM上へ移行。短期間のデータセンター閉鎖に対応。Entra Domain Servicesで補完。</div>
        <div class="arch-pros-cons">
          <div><span class="pros">✅ メリット</span>: 移行リスク最小, 既存運用維持, 短期実現</div>
          <div><span class="cons">⚠️ 注意</span>: クラウド機能活用限定, 長期コスト増</div>
        </div>
      </div>
      <div class="arch-pattern">
        <div class="arch-title">🔄 Hybrid Coexistence パターン</div>
        <div class="arch-desc">Entra Connect同期でAD/Entra IDを並行稼働。日本企業の現実的な主流アプローチ。段階的移行が可能。</div>
        <div class="arch-pros-cons">
          <div><span class="pros">✅ メリット</span>: 段階的移行, リスク分散, 既存資産活用</div>
          <div><span class="cons">⚠️ 注意</span>: 複雑性増加, 2環境管理コスト</div>
        </div>
      </div>
      <div class="arch-pattern">
        <div class="arch-title">☁️ Cloud Native パターン</div>
        <div class="arch-desc">Entra IDのみでクラウドファーストのID管理。新規事業・スタートアップ向け。AD不要でIntune+Entra完結。</div>
        <div class="arch-pros-cons">
          <div><span class="pros">✅ メリット</span>: 運用シンプル, コスト最適, 最新機能利用</div>
          <div><span class="cons">⚠️ 注意</span>: レガシーアプリ非対応, 移行コスト大</div>
        </div>
      </div>
      <div class="arch-pattern">
        <div class="arch-title">🌐 Multi-IdP Federation パターン</div>
        <div class="arch-desc">Entra ID + Okta + 社内ADを組み合わせたフェデレーション。グローバル企業やM&amp;A後の統合に対応。</div>
        <div class="arch-pros-cons">
          <div><span class="pros">✅ メリット</span>: 柔軟性高, 買収先統合容易</div>
          <div><span class="cons">⚠️ 注意</span>: 設計複雑, 全体ガバナンス必要</div>
        </div>
      </div>
    </div>'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IDM Knowledge Base — SIerコンサルタント向けビューア</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<style>
:root {{
  --primary: #1B4F8A;
  --accent:  #0097A7;
  --warn:    #E65100;
  --ok:      #2E7D32;
  --bg:      #F5F7FA;
  --surface: #FFFFFF;
  --border:  #DDE1E7;
  --text:    #1A1A2E;
  --sidebar-w: 240px;
}}
*, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: 'Noto Sans JP', 'Hiragino Sans', sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.6;
}}

/* ── Layout ─────────────────────────────────── */
.app {{ display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}

.header {{
  background: linear-gradient(135deg, var(--primary) 0%, #0d3666 100%);
  color: white;
  padding: 10px 20px;
  position: sticky; top: 0; z-index: 200;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3);
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
}}
.header h1 {{ font-size: 1.15em; font-weight: 700; white-space: nowrap; }}
.header .subtitle {{ font-size: 0.78em; opacity: 0.85; white-space: nowrap; }}
.header-title {{ display: flex; flex-direction: column; }}
.search-wrap {{ flex: 1; min-width: 200px; }}
.search-wrap input {{
  width: 100%; padding: 7px 14px;
  border: none; border-radius: 20px;
  font-size: 0.9em; font-family: inherit;
  background: rgba(255,255,255,0.15); color: white;
  outline: none; transition: background 0.2s;
}}
.search-wrap input::placeholder {{ color: rgba(255,255,255,0.6); }}
.search-wrap input:focus {{ background: rgba(255,255,255,0.25); }}

.body-wrap {{ display: flex; flex: 1; overflow: hidden; }}

/* ── Sidebar ─────────────────────────────────── */
.sidebar {{
  width: var(--sidebar-w); min-width: var(--sidebar-w);
  background: var(--surface);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  flex-shrink: 0;
}}
.sidebar-header {{
  padding: 14px 16px 10px;
  font-size: 0.72em; font-weight: 700; letter-spacing: 0.08em;
  color: #888; text-transform: uppercase;
  border-bottom: 1px solid var(--border);
}}
.nav-item {{
  display: flex; align-items: center; gap: 8px;
  padding: 10px 16px;
  cursor: pointer; font-size: 0.88em;
  border-left: 3px solid transparent;
  transition: all 0.15s;
  color: var(--text);
}}
.nav-item:hover {{ background: #f0f4ff; color: var(--primary); }}
.nav-item.active {{
  background: #e8eeff; color: var(--primary);
  border-left-color: var(--primary); font-weight: 700;
}}
.nav-icon {{ font-size: 1.1em; width: 22px; text-align: center; }}

/* ── Main Content ─────────────────────────────── */
.main {{
  flex: 1; overflow-y: auto;
  padding: 24px 28px;
  background: var(--bg);
}}
.section {{ display: none; }}
.section.active {{ display: block; }}

.section-title {{
  font-size: 1.4em; font-weight: 700;
  color: var(--primary); margin-bottom: 6px;
  padding-bottom: 10px; border-bottom: 2px solid var(--border);
  display: flex; align-items: center; gap: 10px;
}}
.section-desc {{ color: #666; margin-bottom: 20px; font-size: 0.9em; }}

/* ── Dashboard ─────────────────────────────────── */
.stat-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px;
  margin-bottom: 24px;
}}
.stat-card {{
  background: var(--surface); border-radius: 10px;
  padding: 16px; text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: transform 0.2s;
}}
.stat-card:hover {{ transform: translateY(-2px); }}
.stat-icon {{ font-size: 1.8em; margin-bottom: 6px; }}
.stat-value {{ font-size: 1.3em; font-weight: 700; margin-bottom: 2px; }}
.stat-label {{ font-size: 0.78em; color: #666; }}

/* ── Charts ─────────────────────────────────── */
.chart-container {{
  background: var(--surface); border-radius: 12px;
  padding: 20px; margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}}
.chart-title {{
  font-size: 1em; font-weight: 700;
  color: var(--primary); margin-bottom: 14px;
  display: flex; align-items: center; gap: 8px;
}}
.chart-subtitle {{ font-size: 0.8em; color: #888; margin-left: auto; }}
.echarts-wrap {{ width: 100%; height: 480px; }}
.echarts-wrap-lg {{ width: 100%; height: 560px; }}
.echarts-wrap-sm {{ width: 100%; height: 360px; }}
.echarts-wrap-gantt {{ width: 100%; height: 320px; }}

.chart-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
@media (max-width: 900px) {{ .chart-row {{ grid-template-columns: 1fr; }} }}

/* ── Knowledge Cards ─────────────────────────── */
.filter-bar {{
  display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; align-items: center;
}}
.filter-bar input, .filter-bar select {{
  padding: 7px 12px; border: 1px solid var(--border); border-radius: 8px;
  font-size: 0.88em; font-family: inherit; color: var(--text);
  background: var(--surface); outline: none;
}}
.filter-bar input:focus, .filter-bar select:focus {{ border-color: var(--accent); }}
.filter-count {{ font-size: 0.82em; color: #888; margin-left: auto; }}

.knowledge-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 14px;
}}
.k-card {{
  background: var(--surface); border-radius: 10px;
  padding: 16px; border: 1px solid var(--border);
  transition: box-shadow 0.2s, border-color 0.2s;
  cursor: default;
}}
.k-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.1); border-color: var(--accent); }}
.k-card.hidden {{ display: none; }}
.k-topic {{ font-size: 0.98em; font-weight: 700; color: var(--primary); margin-bottom: 6px; }}
.k-content {{ font-size: 0.85em; color: #444; margin-bottom: 8px; line-height: 1.65; }}
.k-details {{ font-size: 0.8em; color: #777; margin-bottom: 8px; }}
.k-footer {{ display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }}
.tag {{
  display: inline-block; padding: 2px 8px; border-radius: 10px;
  font-size: 0.72em; background: #e8eeff; color: var(--primary); font-weight: 500;
}}
.badge-jp {{
  background: #e8f5e9; color: var(--ok);
  padding: 2px 8px; border-radius: 10px; font-size: 0.72em; font-weight: 700;
}}
.badge-ev {{
  padding: 2px 8px; border-radius: 10px; font-size: 0.72em; font-weight: 500;
}}
.badge-ev.high {{ background: #fce4ec; color: #c62828; }}
.badge-ev.medium {{ background: #fff8e1; color: #f57f17; }}
.badge-ev.low {{ background: #f3e5f5; color: #6a1b9a; }}
.badge-cat {{ font-size: 0.72em; color: #888; padding: 1px 6px; background: #f5f5f5; border-radius: 8px; }}
.k-source {{ font-size: 0.7em; color: #aaa; margin-top: 6px; }}

/* ── Risk Matrix Table ─────────────────────────── */
.risk-table {{ width: 100%; border-collapse: collapse; font-size: 0.85em; }}
.risk-table th {{
  background: var(--primary); color: white;
  padding: 10px 14px; text-align: left;
}}
.risk-table td {{ padding: 10px 14px; border-bottom: 1px solid var(--border); vertical-align: top; }}
.risk-table tr:hover td {{ background: #f8f9ff; }}
.level-high td {{ border-left: 3px solid var(--warn); }}
.level-medium td {{ border-left: 3px solid #f9a825; }}
.risk-badge {{ font-weight: 700; white-space: nowrap; }}

/* ── Arch Patterns ─────────────────────────────── */
.arch-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px;
  margin-bottom: 20px;
}}
.arch-pattern {{
  background: var(--surface); border-radius: 10px; padding: 18px;
  border: 1px solid var(--border);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}}
.arch-title {{ font-weight: 700; font-size: 0.95em; color: var(--primary); margin-bottom: 8px; }}
.arch-desc {{ font-size: 0.85em; color: #555; margin-bottom: 10px; line-height: 1.65; }}
.arch-pros-cons {{ font-size: 0.8em; line-height: 1.8; }}
.pros {{ color: var(--ok); font-weight: 700; }}
.cons {{ color: var(--warn); font-weight: 700; }}

/* ── Industry Guide ─────────────────────────────── */
.card-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px;
  margin-bottom: 20px;
}}
.info-card {{ background: var(--surface); border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.info-card-header {{ color: white; padding: 12px 16px; font-weight: 700; font-size: 0.95em; }}
.info-card-body {{ padding: 14px 16px; }}
.info-card-body p {{ font-size: 0.83em; margin-bottom: 6px; line-height: 1.6; }}

/* ── Scenario Cards ─────────────────────────────── */
.scenario-card {{
  background: var(--surface); border-radius: 10px; overflow: hidden;
  border: 1px solid var(--border); box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}}
.scenario-title {{
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white; padding: 12px 16px; font-weight: 700; font-size: 0.92em;
}}
.scenario-body {{ padding: 14px 16px; font-size: 0.85em; color: #444; line-height: 1.65; }}
.scenario-tags {{ margin-top: 10px; display: flex; gap: 6px; flex-wrap: wrap; }}

/* ── Mermaid / Auth Flow ────────────────────────── */
.auth-tabs {{ display: flex; gap: 8px; margin-bottom: 16px; }}
.auth-tab {{
  padding: 7px 16px; border-radius: 20px; cursor: pointer;
  font-size: 0.85em; background: #e8eeff; color: var(--primary);
  border: 1px solid var(--border); transition: all 0.2s;
}}
.auth-tab:hover {{ background: var(--primary); color: white; }}
.auth-tab.active {{ background: var(--primary); color: white; font-weight: 700; }}
.mermaid-wrap {{
  background: var(--surface); border-radius: 10px; padding: 20px;
  border: 1px solid var(--border); overflow-x: auto;
}}
.mermaid-pane {{ display: none; }}
.mermaid-pane.active {{ display: block; }}

/* ── Legend ─────────────────────────────────── */
.legend {{
  display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 16px;
}}
.legend-item {{
  display: flex; align-items: center; gap: 5px; font-size: 0.8em;
}}
.legend-dot {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}

/* ── Empty State ─────────────────────────────── */
.empty-state {{
  text-align: center; padding: 60px 20px; color: #bbb; font-size: 1em;
}}

/* ── Print ─────────────────────────────────── */
@media print {{
  .sidebar, .header .search-wrap, .auth-tabs, .filter-bar {{ display: none !important; }}
  .body-wrap {{ display: block; }}
  .main {{ padding: 0; }}
  .chart-container {{ break-inside: avoid; }}
  .echarts-wrap, .echarts-wrap-lg {{ height: 320px; }}
}}
</style>
</head>
<body>

<div class="app">

  <!-- ── Header ── -->
  <div class="header">
    <div class="header-title">
      <h1>🔐 IDM Knowledge Base</h1>
      <div class="subtitle">Identity &amp; Access Management — SIerコンサルタント向けビューア</div>
    </div>
    <div class="search-wrap">
      <input type="text" id="globalSearch" placeholder="🔍 ノード名・説明・タグで検索..." oninput="onGlobalSearch(this.value)">
    </div>
  </div>

  <div class="body-wrap">

    <!-- ── Sidebar ── -->
    <nav class="sidebar">
      <div class="sidebar-header">ナビゲーション</div>
      <div class="nav-item active" onclick="showSection('dashboard')"><span class="nav-icon">🏠</span> ダッシュボード</div>
      <div class="nav-item" onclick="showSection('subjects')"><span class="nav-icon">👥</span> ID主体分類</div>
      <div class="nav-item" onclick="showSection('auth')"><span class="nav-icon">🔐</span> 認証・技術マップ</div>
      <div class="nav-item" onclick="showSection('products')"><span class="nav-icon">🏢</span> 製品・ツール比較</div>
      <div class="nav-item" onclick="showSection('architecture')"><span class="nav-icon">🏗️</span> アーキテクチャ設計</div>
      <div class="nav-item" onclick="showSection('industry')"><span class="nav-icon">🏭</span> 業種別ガイド</div>
      <div class="nav-item" onclick="showSection('security')"><span class="nav-icon">🛡️</span> セキュリティ強化</div>
      <div class="nav-item" onclick="showSection('migration')"><span class="nav-icon">🗺️</span> 移行パターン</div>
      <div class="nav-item" onclick="showSection('frameworks')"><span class="nav-icon">📋</span> フレームワーク</div>
      <div class="nav-item" onclick="showSection('scenarios')"><span class="nav-icon">🎬</span> シナリオ</div>
      <div class="nav-item" onclick="showSection('knowledge-graph')"><span class="nav-icon">🕸️</span> 知識グラフ</div>
    </nav>

    <!-- ── Main Content ── -->
    <main class="main" id="mainContent">

      <!-- 0. Dashboard -->
      <section id="dashboard" class="section active">
        <div class="section-title">🏠 ダッシュボード <span style="font-size:0.6em;font-weight:400;color:#888">IDM Knowledge Base Overview</span></div>
        <div class="section-desc">IDナレッジベースの全体像。各セクションへのクイックアクセスと主要指標を表示します。</div>
        <div class="stat-grid" id="statGrid">{stat_cards_html}</div>

        <div class="chart-container">
          <div class="chart-title">📊 ナレッジ分布 — ソースファイル別エントリ数</div>
          <div id="dashKnowledgeChart" class="echarts-wrap-sm"></div>
        </div>

        <div class="chart-row">
          <div class="chart-container">
            <div class="chart-title">🕸️ ノードタイプ分布</div>
            <div id="dashNodeTypeChart" style="height:280px"></div>
          </div>
          <div class="chart-container">
            <div class="chart-title">🔗 エッジ関係タイプ分布</div>
            <div id="dashEdgeTypeChart" style="height:280px"></div>
          </div>
        </div>
      </section>

      <!-- 1. ID主体分類 -->
      <section id="subjects" class="section">
        <div class="section-title">👥 ID主体分類 <span style="font-size:0.6em;font-weight:400;color:#888">Identity Subjects</span></div>
        <div class="section-desc">エンタープライズ環境に存在するすべてのID主体を5カテゴリに分類します。</div>

        <div class="chart-container">
          <div class="chart-title">🌳 ID主体分類ツリー <span class="chart-subtitle">ノードをクリックすると展開/折りたたみ</span></div>
          <div id="subjectTreeChart" class="echarts-wrap-lg"></div>
        </div>

        <div class="chart-container">
          <div class="chart-title">⚠️ ID主体 × リスク × 対策マトリクス</div>
          <div style="overflow-x:auto">
            <table class="risk-table">
              <thead>
                <tr>
                  <th>ID主体</th>
                  <th>主要リスク</th>
                  <th>推奨対策</th>
                  <th>対応製品</th>
                  <th>リスクレベル</th>
                </tr>
              </thead>
              <tbody id="riskMatrixBody">
{matrix_rows_html}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- 2. 認証・技術マップ -->
      <section id="auth" class="section">
        <div class="section-title">🔐 認証・技術マップ <span style="font-size:0.6em;font-weight:400;color:#888">Authentication Technology Map</span></div>
        <div class="section-desc">認証フローをシーケンス図で可視化。Kerberos / OIDC / SAML の3方式を比較します。</div>

        <div class="chart-container">
          <div class="chart-title">📊 認証フロー図</div>
          <div class="auth-tabs">
            <div class="auth-tab active" onclick="switchAuthTab('kerberos', this)">🔑 Kerberos認証</div>
            <div class="auth-tab" onclick="switchAuthTab('oidc', this)">🌐 OIDC認証</div>
            <div class="auth-tab" onclick="switchAuthTab('saml', this)">📋 SAML SSO</div>
          </div>
          <div class="mermaid-wrap">
            <div class="mermaid-pane active" id="mermaid-kerberos">
              <pre class="mermaid" id="mmd-kerberos"></pre>
            </div>
            <div class="mermaid-pane" id="mermaid-oidc">
              <pre class="mermaid" id="mmd-oidc"></pre>
            </div>
            <div class="mermaid-pane" id="mermaid-saml">
              <pre class="mermaid" id="mmd-saml"></pre>
            </div>
          </div>
        </div>

        <div class="filter-bar">
          <input type="text" id="authSearch" placeholder="認証ナレッジを検索..." oninput="filterKnowledge('authKnowledgeGrid', this.value, '')">
          <span class="filter-count" id="authCount"></span>
        </div>
        <div class="knowledge-grid" id="authKnowledgeGrid"></div>
      </section>

      <!-- 3. 製品・ツール比較 -->
      <section id="products" class="section">
        <div class="section-title">🏢 製品・ツール比較 <span style="font-size:0.6em;font-weight:400;color:#888">Product Comparison</span></div>
        <div class="section-desc">IdP製品とPAM製品の能力をレーダーチャートで比較します。</div>

        <div class="chart-row">
          <div class="chart-container">
            <div class="chart-title">🎯 IdP製品能力比較</div>
            <div id="idpRadarChart" class="echarts-wrap"></div>
          </div>
          <div class="chart-container">
            <div class="chart-title">🛡️ PAM製品能力比較</div>
            <div id="pamRadarChart" class="echarts-wrap"></div>
          </div>
        </div>

        <div class="chart-container">
          <div class="chart-title">☁️ IaaS→PaaS→SaaS ID連続性フロー</div>
          <div id="sankeyChart" class="echarts-wrap-sm"></div>
        </div>
      </section>

      <!-- 4. アーキテクチャ設計 -->
      <section id="architecture" class="section">
        <div class="section-title">🏗️ アーキテクチャ設計 <span style="font-size:0.6em;font-weight:400;color:#888">Architecture Patterns</span></div>
        <div class="section-desc">日本企業に適したIDアーキテクチャパターンを比較します。</div>
        {architecture_content}

        <div class="filter-bar">
          <input type="text" id="archSearch" placeholder="アーキテクチャナレッジを検索..." oninput="filterKnowledge('archKnowledgeGrid', this.value, '')">
          <span class="filter-count" id="archCount"></span>
        </div>
        <div class="knowledge-grid" id="archKnowledgeGrid"></div>
      </section>

      <!-- 5. 業種別ガイド -->
      <section id="industry" class="section">
        <div class="section-title">🏭 業種別ガイド <span style="font-size:0.6em;font-weight:400;color:#888">Industry Guide</span></div>
        <div class="section-desc">業種固有の規制・要件・推奨製品スタックをまとめます。</div>
        {industry_cards}
      </section>

      <!-- 6. セキュリティ強化 -->
      <section id="security" class="section">
        <div class="section-title">🛡️ セキュリティ強化 <span style="font-size:0.6em;font-weight:400;color:#888">Security Hardening</span></div>
        <div class="section-desc">攻撃手法と被害対象のリスクマトリクスで優先対策を特定します。</div>

        <div class="chart-container">
          <div class="chart-title">🔥 セキュリティリスクヒートマップ</div>
          <div id="riskHeatmapChart" class="echarts-wrap-sm"></div>
        </div>

        <div class="filter-bar">
          <input type="text" id="secSearch" placeholder="セキュリティナレッジを検索..." oninput="filterKnowledge('secKnowledgeGrid', this.value, '')">
          <span class="filter-count" id="secCount"></span>
        </div>
        <div class="knowledge-grid" id="secKnowledgeGrid"></div>
      </section>

      <!-- 7. 移行パターン -->
      <section id="migration" class="section">
        <div class="section-title">🗺️ 移行パターン <span style="font-size:0.6em;font-weight:400;color:#888">Migration Patterns</span></div>
        <div class="section-desc">AD→Entra ID 移行ロードマップ（24ヶ月）。フェーズごとのマイルストーンと依存関係を示します。</div>

        <div class="chart-container">
          <div class="chart-title">📅 AD→Entra ID 移行ロードマップ</div>
          <div id="ganttChart" class="echarts-wrap-gantt"></div>
        </div>

        <div class="filter-bar">
          <input type="text" id="migSearch" placeholder="移行ナレッジを検索..." oninput="filterKnowledge('migKnowledgeGrid', this.value, '')">
          <span class="filter-count" id="migCount"></span>
        </div>
        <div class="knowledge-grid" id="migKnowledgeGrid"></div>
      </section>

      <!-- 8. フレームワーク -->
      <section id="frameworks" class="section">
        <div class="section-title">📋 フレームワーク対応 <span style="font-size:0.6em;font-weight:400;color:#888">Compliance Frameworks</span></div>
        <div class="section-desc">主要セキュリティフレームワークのID要件マトリクス。必須/推奨/任意の三段階で表示します。</div>

        <div class="chart-container">
          <div class="chart-title">📊 フレームワーク×セキュリティ要件 対応マトリクス</div>
          <div class="legend">
            <div class="legend-item"><div class="legend-dot" style="background:#C62828"></div>必須 (3)</div>
            <div class="legend-item"><div class="legend-dot" style="background:#F9A825"></div>推奨 (2)</div>
            <div class="legend-item"><div class="legend-dot" style="background:#81C784"></div>任意 (1)</div>
            <div class="legend-item"><div class="legend-dot" style="background:#E0E0E0"></div>N/A (0)</div>
          </div>
          <div id="frameworkHeatmapChart" class="echarts-wrap-sm"></div>
        </div>
      </section>

      <!-- 9. シナリオ -->
      <section id="scenarios" class="section">
        <div class="section-title">🎬 シナリオ <span style="font-size:0.6em;font-weight:400;color:#888">Practical Scenarios</span></div>
        <div class="section-desc">実際のIDM導入・運用シナリオをユースケース別にまとめます。</div>
        {scenario_cards}
      </section>

      <!-- 10. 知識グラフ -->
      <section id="knowledge-graph" class="section">
        <div class="section-title">🕸️ 知識グラフ <span style="font-size:0.6em;font-weight:400;color:#888">Knowledge Graph</span></div>
        <div class="section-desc">全JSONファイルのノード・エッジをForce-directed グラフで可視化します。ホバーで説明表示、スクロールでズーム。</div>

        <div class="legend">
          <div class="legend-item"><div class="legend-dot" style="background:#1B4F8A"></div>IdP</div>
          <div class="legend-item"><div class="legend-dot" style="background:#6A1B9A"></div>製品</div>
          <div class="legend-item"><div class="legend-dot" style="background:#00838F"></div>プロトコル</div>
          <div class="legend-item"><div class="legend-dot" style="background:#E65100"></div>概念</div>
          <div class="legend-item"><div class="legend-dot" style="background:#C62828"></div>リスク</div>
          <div class="legend-item"><div class="legend-dot" style="background:#2E7D32"></div>パターン</div>
          <div class="legend-item"><div class="legend-dot" style="background:#4E342E"></div>規制</div>
        </div>
        <div class="chart-container" style="padding:10px">
          <div id="knowledgeGraphChart" style="width:100%;height:620px"></div>
        </div>

        <div class="filter-bar" style="margin-top:16px">
          <input type="text" id="kgSearch" placeholder="全ナレッジを検索..." oninput="filterKnowledge('allKnowledgeGrid', this.value, document.getElementById('kgCatFilter').value)">
          <select id="kgCatFilter" onchange="filterKnowledge('allKnowledgeGrid', document.getElementById('kgSearch').value, this.value)">
            <option value="">すべて</option>
          </select>
          <span class="filter-count" id="kgCount"></span>
        </div>
        <div class="knowledge-grid" id="allKnowledgeGrid"></div>
      </section>

    </main>
  </div><!-- .body-wrap -->
</div><!-- .app -->

<script>
// ── Data ─────────────────────────────────────────────────────────
const GRAPH_NODES = {gn_js};
const GRAPH_EDGES = {ge_js};
const ALL_KNOWLEDGE = {kn_js};
const IDP_RADAR = {idp_js};
const PAM_RADAR = {pam_js};
const RISK_HEATMAP = {risk_js};
const FW_HEATMAP = {fw_js};
const SANKEY = {sankey_js};
const GANTT = {gantt_js};
const IDENTITY_TREE = {tree_js};
const MERMAID_FLOWS = {flows_js};
const DASHBOARD_STATS = {stats_js};

// ── Navigation ───────────────────────────────────────────────────
let chartInited = {{}};
let mermaidInited = false;

function showSection(id) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const sec = document.getElementById(id);
  if (sec) sec.classList.add('active');
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(n => {{
    if (n.getAttribute('onclick') && n.getAttribute('onclick').includes("'" + id + "'")) {{
      n.classList.add('active');
    }}
  }});
  initSectionCharts(id);
}}

function initSectionCharts(id) {{
  if (chartInited[id]) return;
  chartInited[id] = true;
  setTimeout(() => {{
    if (id === 'dashboard') initDashboardCharts();
    else if (id === 'subjects') initSubjectsCharts();
    else if (id === 'auth') {{ initAuthMermaid(); populateKnowledge('authKnowledgeGrid', 'authCount', ['サーバー認証','Kerberos','ハイブリッド','Entra連携']); }}
    else if (id === 'products') initProductCharts();
    else if (id === 'architecture') populateKnowledge('archKnowledgeGrid', 'archCount', ['アーキテクチャ','IdP']);
    else if (id === 'security') {{ initSecurityCharts(); populateKnowledge('secKnowledgeGrid', 'secCount', ['セキュリティ強化','PAM']); }}
    else if (id === 'migration') {{ initGanttChart(); populateKnowledge('migKnowledgeGrid', 'migCount', ['移行','AD→Entra']); }}
    else if (id === 'frameworks') initFrameworkChart();
    else if (id === 'knowledge-graph') {{ initKnowledgeGraph(); populateKnowledge('allKnowledgeGrid', 'kgCount', null, 'kgCatFilter'); }}
  }}, 50);
}}

// ── Dashboard Charts ─────────────────────────────────────────────
function initDashboardCharts() {{
  // Knowledge count by source
  const srcMap = {{}};
  ALL_KNOWLEDGE.forEach(k => {{
    const src = k.source.split('/').slice(0,1).join('/');
    srcMap[src] = (srcMap[src] || 0) + 1;
  }});
  const srcLabels = Object.keys(srcMap);
  const srcVals = srcLabels.map(s => srcMap[s]);
  const chart1 = echarts.init(document.getElementById('dashKnowledgeChart'));
  chart1.setOption({{
    tooltip: {{ trigger: 'axis' }},
    xAxis: {{ type: 'category', data: srcLabels, axisLabel: {{ rotate: 30, fontSize: 10 }} }},
    yAxis: {{ type: 'value', name: 'エントリ数' }},
    series: [{{ type: 'bar', data: srcVals, itemStyle: {{ color: '#1B4F8A' }},
      label: {{ show: true, position: 'top', fontSize: 11 }} }}],
    grid: {{ bottom: 70, left: 50 }}
  }});
  window.addEventListener('resize', () => chart1.resize());

  // Node type distribution
  const typeMap = {{}};
  GRAPH_NODES.forEach(n => {{ typeMap[n.category] = (typeMap[n.category] || 0) + 1; }});
  const typeColors = {{
    identity_provider: '#1B4F8A', product: '#6A1B9A', protocol: '#00838F',
    concept: '#E65100', risk: '#C62828', pattern: '#2E7D32', regulation: '#4E342E'
  }};
  const chart2 = echarts.init(document.getElementById('dashNodeTypeChart'));
  chart2.setOption({{
    tooltip: {{ trigger: 'item', formatter: '{{b}}: {{c}} ({{d}}%)' }},
    legend: {{ bottom: 0, fontSize: 10 }},
    series: [{{
      type: 'pie', radius: ['35%', '65%'], center: ['50%', '45%'],
      data: Object.entries(typeMap).map(([k,v]) => ({{
        name: k, value: v, itemStyle: {{ color: typeColors[k] || '#78909C' }}
      }}))
    }}]
  }});
  window.addEventListener('resize', () => chart2.resize());

  // Edge relationship distribution
  const relMap = {{}};
  GRAPH_EDGES.forEach(e => {{ const r = e.relationship || 'unknown'; relMap[r] = (relMap[r]||0)+1; }});
  const relLabels = Object.keys(relMap).sort((a,b) => relMap[b]-relMap[a]).slice(0,12);
  const chart3 = echarts.init(document.getElementById('dashEdgeTypeChart'));
  chart3.setOption({{
    tooltip: {{ trigger: 'axis' }},
    xAxis: {{ type: 'value' }},
    yAxis: {{ type: 'category', data: relLabels.slice().reverse(), axisLabel: {{ fontSize: 10 }} }},
    series: [{{ type: 'bar', data: relLabels.slice().reverse().map(l => relMap[l]),
      itemStyle: {{ color: '#0097A7' }},
      label: {{ show: true, position: 'right', fontSize: 10 }} }}],
    grid: {{ left: 120, right: 50 }}
  }});
  window.addEventListener('resize', () => chart3.resize());
}}

// ── Subjects Charts ───────────────────────────────────────────────
function initSubjectsCharts() {{
  function addTreeStyle(node) {{
    if (!node.itemStyle) node.itemStyle = {{ color: '#1B4F8A' }};
    if (!node.label) node.label = {{ fontSize: 12 }};
    if (node.children) node.children.forEach(c => addTreeStyle(c));
    return node;
  }}
  const treeData = JSON.parse(JSON.stringify(IDENTITY_TREE));
  addTreeStyle(treeData);

  const chart = echarts.init(document.getElementById('subjectTreeChart'));
  chart.setOption({{
    tooltip: {{ trigger: 'item', formatter: p => p.name }},
    series: [{{
      type: 'tree',
      data: [treeData],
      layout: 'orthogonal',
      orient: 'LR',
      initialTreeDepth: 2,
      symbolSize: 10,
      label: {{ position: 'left', verticalAlign: 'middle', align: 'right', fontSize: 12 }},
      leaves: {{ label: {{ position: 'right', verticalAlign: 'middle', align: 'left' }} }},
      expandAndCollapse: true,
      animationDuration: 300,
      left: '5%', right: '5%', top: '5%', bottom: '5%',
    }}]
  }});
  window.addEventListener('resize', () => chart.resize());
}}

// ── Auth Mermaid ──────────────────────────────────────────────────
function initAuthMermaid() {{
  if (mermaidInited) return;
  mermaidInited = true;
  mermaid.initialize({{ startOnLoad: false, theme: 'default', securityLevel: 'loose' }});
  Object.entries(MERMAID_FLOWS).forEach(([key, src]) => {{
    const el = document.getElementById('mmd-' + key);
    if (el) el.textContent = src;
  }});
  mermaid.run({{ nodes: document.querySelectorAll('.mermaid') }});
}}

function switchAuthTab(key, el) {{
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('.mermaid-pane').forEach(p => p.classList.remove('active'));
  const pane = document.getElementById('mermaid-' + key);
  if (pane) pane.classList.add('active');
}}

// ── Product Charts ────────────────────────────────────────────────
function initProductCharts() {{
  function makeRadar(domId, cfg) {{
    const chart = echarts.init(document.getElementById(domId));
    chart.setOption({{
      legend: {{ data: cfg.series.map(s=>s.name), bottom: 0, fontSize: 10, itemWidth: 12 }},
      tooltip: {{ trigger: 'item' }},
      radar: {{
        indicator: cfg.indicators,
        radius: '60%', center: ['50%', '45%'],
        axisName: {{ fontSize: 11, color: '#444' }},
      }},
      series: [{{
        type: 'radar',
        data: cfg.series.map(s => ({{
          name: s.name, value: s.values,
          lineStyle: {{ color: s.color, width: 2 }},
          areaStyle: {{ color: s.color, opacity: 0.08 }},
          itemStyle: {{ color: s.color }},
          symbol: 'circle', symbolSize: 5,
        }}))
      }}]
    }});
    window.addEventListener('resize', () => chart.resize());
  }}
  makeRadar('idpRadarChart', IDP_RADAR);
  makeRadar('pamRadarChart', PAM_RADAR);

  // Sankey
  const sankeyChart = echarts.init(document.getElementById('sankeyChart'));
  sankeyChart.setOption({{
    tooltip: {{ trigger: 'item', triggerOn: 'mousemove' }},
    series: [{{
      type: 'sankey',
      layout: 'none',
      data: SANKEY.nodes,
      links: SANKEY.links,
      orient: 'horizontal',
      left: 50, right: 50, top: 20, bottom: 20,
      nodeWidth: 18, nodeGap: 14,
      label: {{ show: true, fontSize: 11 }},
      lineStyle: {{ curveness: 0.5, opacity: 0.4 }},
      emphasis: {{ focus: 'adjacency' }},
      levels: [
        {{ depth: 0, itemStyle: {{ color: '#1B4F8A' }}, lineStyle: {{ color: 'source', opacity: 0.4 }} }},
        {{ depth: 1, itemStyle: {{ color: '#0097A7' }}, lineStyle: {{ color: 'source', opacity: 0.4 }} }},
        {{ depth: 2, itemStyle: {{ color: '#2E7D32' }}, lineStyle: {{ color: 'source', opacity: 0.4 }} }},
      ],
    }}]
  }});
  window.addEventListener('resize', () => sankeyChart.resize());
}}

// ── Security Charts ───────────────────────────────────────────────
function initSecurityCharts() {{
  const riskData = RISK_HEATMAP.data.map(d => [d[0], d[1], d[2]]);
  const chart = echarts.init(document.getElementById('riskHeatmapChart'));
  chart.setOption({{
    tooltip: {{
      position: 'top',
      formatter: p => `${{RISK_HEATMAP.y[p.data[1]]}} × ${{RISK_HEATMAP.x[p.data[0]]}}<br>リスクスコア: <strong>${{p.data[2]}}</strong>`
    }},
    xAxis: {{ type: 'category', data: RISK_HEATMAP.x, axisLabel: {{ rotate: 20, fontSize: 10 }} }},
    yAxis: {{ type: 'category', data: RISK_HEATMAP.y, axisLabel: {{ fontSize: 11 }} }},
    visualMap: {{
      min: 0, max: 100, calculable: true,
      orient: 'horizontal', left: 'center', bottom: 0,
      inRange: {{ color: ['#81C784', '#FFF176', '#EF5350'] }},
      text: ['高リスク', '低リスク'], textStyle: {{ fontSize: 10 }},
    }},
    series: [{{
      type: 'heatmap', data: riskData,
      label: {{ show: true, fontSize: 10, formatter: p => p.data[2] }},
      emphasis: {{ itemStyle: {{ shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' }} }}
    }}],
    grid: {{ left: 110, right: 20, bottom: 70, top: 10 }}
  }});
  window.addEventListener('resize', () => chart.resize());
}}

// ── Gantt Chart ───────────────────────────────────────────────────
function initGanttChart() {{
  const months = Array.from({{length:25}}, (_,i) => `M${{i}}`);
  const chart = echarts.init(document.getElementById('ganttChart'));
  chart.setOption({{
    tooltip: {{
      formatter: p => {{
        const g = GANTT[p.dataIndex];
        if (!g) return '';
        return `<strong>${{g.name}}</strong><br>${{g.desc}}<br><br>` +
               `マイルストーン:<br>` + g.milestones.map(m=>`・${{m}}`).join('<br>');
      }}
    }},
    xAxis: {{
      type: 'value', min: 0, max: 24,
      axisLabel: {{ formatter: v => `Month${{v}}`, fontSize: 10 }},
      name: '経過月数', nameLocation: 'middle', nameGap: 28,
      splitLine: {{ lineStyle: {{ type: 'dashed', color: '#ddd' }} }}
    }},
    yAxis: {{
      type: 'category',
      data: GANTT.map(g => g.name),
      axisLabel: {{ fontSize: 10, width: 200, overflow: 'truncate' }},
      inverse: true
    }},
    series: [
      {{
        type: 'bar', barWidth: 28,
        data: GANTT.map(g => ({{
          value: [g.start, g.end - g.start],
          itemStyle: {{ color: g.color, borderRadius: 4 }},
        }})),
        label: {{
          show: true, position: 'insideLeft', fontSize: 11, color: '#fff',
          formatter: p => GANTT[p.dataIndex].milestones[0] || ''
        }},
        encode: {{ x: [0,1] }},
        stack: false,
      }},
      // Baseline (invisible) for start offset
      {{
        type: 'bar', barWidth: 28,
        data: GANTT.map(g => ({{ value: g.start, itemStyle: {{ color: 'transparent' }} }})),
        stack: 'gantt',
        silent: true,
      }},
    ],
    grid: {{ left: 230, right: 20, top: 15, bottom: 45 }}
  }});
  window.addEventListener('resize', () => chart.resize());
}}

// ── Framework Heatmap ────────────────────────────────────────────
function initFrameworkChart() {{
  const chart = echarts.init(document.getElementById('frameworkHeatmapChart'));
  chart.setOption({{
    tooltip: {{
      position: 'top',
      formatter: p => {{
        const lvl = FW_HEATMAP.labels[p.data[2]] || '-';
        return `${{FW_HEATMAP.y[p.data[1]]}} — ${{FW_HEATMAP.x[p.data[0]]}}<br>要件レベル: <strong>${{lvl}}</strong>`;
      }}
    }},
    xAxis: {{ type: 'category', data: FW_HEATMAP.x, axisLabel: {{ rotate: 20, fontSize: 10 }} }},
    yAxis: {{ type: 'category', data: FW_HEATMAP.y, axisLabel: {{ fontSize: 11 }} }},
    visualMap: {{
      min: 0, max: 3, calculable: false,
      orient: 'horizontal', left: 'center', bottom: 0,
      inRange: {{ color: ['#E0E0E0', '#81C784', '#F9A825', '#C62828'] }},
    }},
    series: [{{
      type: 'heatmap', data: FW_HEATMAP.data,
      label: {{
        show: true, fontSize: 10,
        formatter: p => FW_HEATMAP.labels[p.data[2]] || '',
      }},
      emphasis: {{ itemStyle: {{ shadowBlur: 6 }} }}
    }}],
    grid: {{ left: 100, right: 20, bottom: 70, top: 10 }}
  }});
  window.addEventListener('resize', () => chart.resize());
}}

// ── Knowledge Graph ──────────────────────────────────────────────
function initKnowledgeGraph() {{
  const chart = echarts.init(document.getElementById('knowledgeGraphChart'));
  chart.setOption({{
    backgroundColor: '#fafafa',
    tooltip: {{
      show: true, trigger: 'item',
      formatter: p => {{
        if (p.dataType === 'node') {{
          return `<strong>${{p.data.name}}</strong><br>タイプ: ${{p.data.category}}<br>${{p.data.desc || ''}}`;
        }}
        return `${{p.data.relationship || ''}}: ${{p.data.desc || ''}}`;
      }}
    }},
    series: [{{
      type: 'graph',
      layout: 'force',
      data: GRAPH_NODES.map(n => ({{
        id: n.id, name: n.name, category: n.category,
        symbolSize: n.symbolSize,
        itemStyle: n.itemStyle,
        desc: n.desc,
        label: {{ show: n.symbolSize >= 28, fontSize: 10, color: '#222' }},
      }})),
      links: GRAPH_EDGES.map(e => ({{
        source: e.source, target: e.target,
        relationship: e.relationship, desc: e.desc,
        lineStyle: {{ width: 1.5, curveness: 0.1, color: '#aaa', opacity: 0.6 }},
      }})),
      roam: true,
      force: {{ repulsion: 300, gravity: 0.08, edgeLength: [80, 200], layoutAnimation: true }},
      emphasis: {{ focus: 'adjacency', lineStyle: {{ width: 3 }} }},
      edgeSymbol: ['none', 'arrow'], edgeSymbolSize: [0, 8],
    }}]
  }});
  window.addEventListener('resize', () => chart.resize());
}}

// ── Knowledge Cards ──────────────────────────────────────────────
function makeKCard(k) {{
  const ev = k.evidence_level;
  const evClass = ev === 'high' ? 'high' : ev === 'medium' ? 'medium' : 'low';
  const evLabel = ev === 'high' ? '証拠:高' : ev === 'medium' ? '証拠:中' : ev ? `証拠:${{ev}}` : '';
  const tags = (k.tags||[]).map(t => `<span class="tag">${{t}}</span>`).join('');
  const jpBadge = k.japan_specific ? '<span class="badge-jp">🇯🇵 日本固有</span>' : '';
  const evBadge = evLabel ? `<span class="badge-ev ${{evClass}}">${{evLabel}}</span>` : '';
  return `<div class="k-card" data-topic="${{k.topic||''}}" data-content="${{k.content||''}}" data-tags="${{(k.tags||[]).join(' ')}}">
    <div class="k-topic">${{k.topic || k.id}}</div>
    <div class="k-content">${{k.content || ''}}</div>
    ${{k.details ? `<div class="k-details">${{k.details}}</div>` : ''}}
    <div class="k-footer">${{tags}} ${{jpBadge}} ${{evBadge}}</div>
    <div class="k-source">📄 ${{k.source}}</div>
  </div>`;
}}

function populateKnowledge(gridId, countId, filterTags, catSelectId) {{
  const grid = document.getElementById(gridId);
  if (!grid) return;
  let items = ALL_KNOWLEDGE;
  if (filterTags && filterTags.length > 0) {{
    items = items.filter(k => filterTags.some(t => (k.tags||[]).includes(t) || (k.source||'').includes(t.split('→')[0])));
  }}
  if (catSelectId) {{
    const sel = document.getElementById(catSelectId);
    if (sel && sel.options.length <= 1) {{
      const cats = [...new Set(ALL_KNOWLEDGE.map(k => k.source.split('/')[0]))].sort();
      cats.forEach(c => {{
        const o = document.createElement('option');
        o.value = c; o.textContent = c;
        sel.appendChild(o);
      }});
    }}
  }}
  grid.innerHTML = items.length ? items.map(makeKCard).join('') : '<div class="empty-state">ナレッジエントリがありません</div>';
  const cnt = document.getElementById(countId);
  if (cnt) cnt.textContent = `${{items.length}}件表示`;
}}

function filterKnowledge(gridId, query, catFilter) {{
  const grid = document.getElementById(gridId);
  if (!grid) return;
  const q = (query || '').toLowerCase();
  const cards = grid.querySelectorAll('.k-card');
  let visible = 0;
  cards.forEach(c => {{
    const topic = (c.dataset.topic || '').toLowerCase();
    const content = (c.dataset.content || '').toLowerCase();
    const tags = (c.dataset.tags || '').toLowerCase();
    const src = (c.querySelector('.k-source') ? c.querySelector('.k-source').textContent : '').toLowerCase();
    const matchQ = !q || topic.includes(q) || content.includes(q) || tags.includes(q);
    const matchCat = !catFilter || src.includes(catFilter.toLowerCase());
    if (matchQ && matchCat) {{ c.classList.remove('hidden'); visible++; }}
    else c.classList.add('hidden');
  }});
  const gridId2 = gridId.replace('KnowledgeGrid', 'Count').replace('allKnowledgeGrid', 'kgCount');
  const cnt = document.getElementById(gridId2) || document.getElementById('kgCount');
  if (cnt) cnt.textContent = `${{visible}}件表示`;
}}

function onGlobalSearch(q) {{
  document.getElementById('globalSearch').value = q;
  const activeSection = document.querySelector('.section.active');
  if (!activeSection) return;
  const grid = activeSection.querySelector('.knowledge-grid');
  const countEl = activeSection.querySelector('[id$="Count"]');
  if (!grid) return;
  const countId = countEl ? countEl.id : '';
  filterKnowledge(grid.id, q, '');
}}

// ── Init ─────────────────────────────────────────────────────────
window.addEventListener('load', () => {{
  initSectionCharts('dashboard');
}});
</script>
</body>
</html>'''


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

def main():
    all_data = load_all_json()
    print(f"JSONファイル読み込み: {len(all_data)}件")

    graph_nodes, graph_edges = extract_graph(all_data)
    print(f"グラフノード: {len(graph_nodes)}個, エッジ: {len(graph_edges)}本")

    knowledge = extract_all_knowledge(all_data)
    print(f"ナレッジエントリ: {len(knowledge)}件")

    html = generate_html(graph_nodes, graph_edges, knowledge, all_data)

    output_path = BASE_DIR / 'index.html'
    output_path.write_text(html, encoding='utf-8')
    size_kb = output_path.stat().st_size / 1024
    print(f"\n✅ 生成完了: {output_path}")
    print(f"📦 ファイルサイズ: {size_kb:.0f} KB")
    if size_kb < 100:
        print("⚠️  警告: ファイルサイズが100KB未満です。")
    else:
        print("✅ サイズチェック: OK (100KB以上)")


if __name__ == '__main__':
    main()
