# Google Sheets連携セットアップガイド 📊

TikTok Viral Video Detector MVPでGoogle Sheetsに結果を出力するための詳細セットアップ手順

## 🎯 概要

このガイドでは以下を設定します：
1. Google Cloud Console でのプロジェクト作成
2. Google Sheets API の有効化
3. サービスアカウントの作成と認証キー取得
4. スプレッドシートの作成と共有設定

## 📋 事前準備

- Googleアカウント（Gmail等）
- インターネット接続
- ブラウザ（Chrome推奨）

## 🛠️ ステップ1: Google Cloud Console設定

### 1.1 プロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. Googleアカウントでログイン
3. 画面上部の「プロジェクトを選択」をクリック
4. 「新しいプロジェクト」をクリック
5. プロジェクト名を入力（例：`tiktok-viral-detector`）
6. 「作成」をクリック

### 1.2 プロジェクト選択

1. 作成したプロジェクトが選択されていることを確認
2. 画面上部にプロジェクト名が表示されているかチェック

## 🔧 ステップ2: Google Sheets API有効化

### 2.1 APIライブラリにアクセス

1. 左側メニューから「APIとサービス」→「ライブラリ」をクリック
2. 検索ボックスに「Google Sheets API」と入力
3. 「Google Sheets API」をクリック

### 2.2 API有効化

1. 「有効にする」ボタンをクリック
2. 有効化完了まで数秒待機
3. 「Google Drive API」も同様に有効化（ファイル作成に必要）

## 🔑 ステップ3: サービスアカウント作成

### 3.1 認証情報の作成

1. 左側メニューから「APIとサービス」→「認証情報」をクリック
2. 「認証情報を作成」→「サービスアカウント」をクリック

### 3.2 サービスアカウント詳細

1. **サービスアカウント名**: `tiktok-viral-sheets`
2. **サービスアカウントID**: 自動生成（変更可能）
3. **説明**: `TikTok Viral Video Detector用のGoogle Sheets連携`
4. 「作成して続行」をクリック

### 3.3 ロール設定

1. **ロール**: 「編集者」を選択
2. 「続行」をクリック
3. 「完了」をクリック

### 3.4 認証キーのダウンロード

1. 作成されたサービスアカウントをクリック
2. 「キー」タブをクリック
3. 「鍵を追加」→「新しい鍵を作成」をクリック
4. **キーのタイプ**: 「JSON」を選択
5. 「作成」をクリック
6. JSONファイルが自動ダウンロードされる

### 3.5 認証ファイルの配置

1. ダウンロードしたJSONファイルを `credentials.json` にリネーム
2. TikTok Viral MVPのプロジェクトフォルダに配置

```
tiktok-viral-mvp/
├── main.py
├── config.json
├── credentials.json  ← ここに配置
└── README.md
```

## 📊 ステップ4: スプレッドシート設定

### 4.1 スプレッドシート作成

1. [Google Sheets](https://sheets.google.com/) にアクセス
2. 「空白」をクリックして新しいスプレッドシートを作成
3. スプレッドシート名を変更（例：`TikTok Viral Videos`）

### 4.2 スプレッドシートID取得

1. ブラウザのURLを確認
2. URLの形式：`https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
3. `SPREADSHEET_ID` 部分をコピー

**例**:
```
URL: https://docs.google.com/spreadsheets/d/1ABC123def456GHI789jkl012MNO345pqr678STU/edit
ID:  1ABC123def456GHI789jkl012MNO345pqr678STU
```

### 4.3 サービスアカウントとの共有

1. スプレッドシート右上の「共有」ボタンをクリック
2. `credentials.json` 内の `client_email` をコピー
   ```json
   {
     "client_email": "tiktok-viral-sheets@project-name.iam.gserviceaccount.com"
   }
   ```
3. 共有ダイアログにメールアドレスを貼り付け
4. **権限**: 「編集者」を選択
5. 「送信」をクリック

## ⚙️ ステップ5: 設定ファイル更新

### 5.1 config.json更新

```json
{
  "tikapi_key": "YOUR_TIKAPI_KEY_HERE",
  "spreadsheet_id": "1ABC123def456GHI789jkl012MNO345pqr678STU",
  "credentials_path": "credentials.json",
  "min_views": 500000,
  "time_limit_hours": 24,
  "max_requests": 10,
  "countries": ["us", "jp"],
  "output_csv": true
}
```

### 5.2 設定項目説明

| 項目 | 説明 | 例 |
|------|------|-----|
| `spreadsheet_id` | ステップ4.2で取得したID | `1ABC123def...` |
| `credentials_path` | 認証ファイルのパス | `credentials.json` |

## 🧪 ステップ6: 接続テスト

### 6.1 テストスクリプト作成

```python
# test_sheets.py
import gspread
from google.oauth2.service_account import Credentials

def test_google_sheets():
    try:
        # 認証
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        gc = gspread.authorize(creds)
        
        # スプレッドシート取得
        spreadsheet_id = "YOUR_SPREADSHEET_ID_HERE"  # 実際のIDに変更
        spreadsheet = gc.open_by_key(spreadsheet_id)
        
        # テストデータ書き込み
        worksheet = spreadsheet.sheet1
        worksheet.update('A1', 'テスト成功！')
        worksheet.update('B1', '接続確認完了')
        
        print("✅ Google Sheets接続テスト成功！")
        print(f"📊 スプレッドシートURL: {spreadsheet.url}")
        
    except Exception as e:
        print(f"❌ 接続テスト失敗: {e}")

if __name__ == "__main__":
    test_google_sheets()
```

### 6.2 テスト実行

```bash
python test_sheets.py
```

**成功例**:
```
✅ Google Sheets接続テスト成功！
📊 スプレッドシートURL: https://docs.google.com/spreadsheets/d/1ABC123def456GHI789jkl012MNO345pqr678STU/edit
```

## 🚨 トラブルシューティング

### よくあるエラーと解決方法

#### エラー1: `FileNotFoundError: credentials.json`

**原因**: 認証ファイルが見つからない
**解決方法**:
1. `credentials.json` がプロジェクトフォルダにあるか確認
2. ファイル名が正確か確認（拡張子含む）
3. パスが正しいか確認

#### エラー2: `gspread.exceptions.APIError: 403 Forbidden`

**原因**: スプレッドシートの共有設定が不正
**解決方法**:
1. サービスアカウントのメールアドレスを再確認
2. スプレッドシートの共有設定を再実行
3. 権限が「編集者」になっているか確認

#### エラー3: `google.auth.exceptions.DefaultCredentialsError`

**原因**: 認証情報の形式が不正
**解決方法**:
1. JSONファイルを再ダウンロード
2. ファイルが破損していないか確認
3. サービスアカウントを再作成

#### エラー4: `gspread.exceptions.SpreadsheetNotFound`

**原因**: スプレッドシートIDが不正
**解決方法**:
1. スプレッドシートIDを再確認
2. URLから正確にIDを抽出
3. スプレッドシートが削除されていないか確認

### デバッグ用コマンド

```python
# credentials.json の内容確認
import json
with open('credentials.json', 'r') as f:
    creds = json.load(f)
    print(f"Client Email: {creds['client_email']}")
    print(f"Project ID: {creds['project_id']}")
```

## 📊 出力例

### 正常な出力結果

Google Sheetsに以下のような表が作成されます：

| 動画ID | 説明 | 再生数 | いいね数 | コメント数 | シェア数 | アカウント名 | フォロワー数 | 投稿日時 | 経過時間(h) | バイラル速度 | 動画URL | ハッシュタグ | 認証済み |
|--------|------|--------|----------|------------|----------|--------------|------------|----------|-------------|-------------|---------|------------|----------|
| 7123456789 | Amazing dance trend everyone is doing... | 750,000 | 45,000 | 3,200 | 1,800 | user123 | 25,000 | 2025-08-02 10:30:00 | 18.5 | 40,540 | https://www.tiktok.com/@user123/video/7123456789 | dance, viral, trending | |

### フォーマット特徴

- **ヘッダー**: 青色背景、白文字、太字
- **数値**: カンマ区切り表示
- **URL**: クリック可能リンク
- **列幅**: 自動調整

## 🔧 高度な設定

### カスタムワークシート名

```python
# main.py の設定例
sheet_name = f"Viral_{datetime.now().strftime('%m%d_%H%M')}"
```

### 複数スプレッドシート対応

```json
{
  "spreadsheets": {
    "daily": "1ABC123def456GHI789jkl012MNO345pqr678STU",
    "weekly": "1XYZ789abc012DEF345ghi678JKL901mno234PQR",
    "archive": "1QWE456rty789UIO123asd456FGH789jkl012ZXC"
  }
}
```

### 自動バックアップ設定

```python
# 日次バックアップ用スプレッドシート作成
backup_name = f"TikTok_Viral_Backup_{datetime.now().strftime('%Y%m%d')}"
backup_spreadsheet = gc.create(backup_name)
```

## 📈 パフォーマンス最適化

### バッチ更新

```python
# 一括更新（推奨）
worksheet.update('A1', data)  # 全データを一度に更新

# 個別更新（非推奨）
for row in data:
    worksheet.append_row(row)  # 1行ずつ更新（遅い）
```

### API制限対策

- **読み取り**: 100リクエスト/100秒/ユーザー
- **書き込み**: 100リクエスト/100秒/ユーザー
- **推奨**: バッチ処理による一括更新

## 🔒 セキュリティ考慮事項

### 認証ファイルの管理

1. **Git除外**: `.gitignore` に `credentials.json` を追加
2. **権限制限**: ファイルの読み取り権限を制限
3. **定期更新**: 認証キーの定期的な更新

### スプレッドシートの権限

1. **最小権限**: 必要最小限の権限のみ付与
2. **共有制限**: 不要な共有は避ける
3. **監査**: アクセスログの定期確認

---

**最終更新**: 2025年8月2日  
**バージョン**: 1.0.0

