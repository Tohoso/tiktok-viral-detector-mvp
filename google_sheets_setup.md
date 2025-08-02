# 📊 Google Sheets連携手順書

## 🎯 **概要**
TikTok Viral Video DetectorをGoogle Sheetsと連携して、検出されたバイラル動画データを自動的にスプレッドシートに出力します。

## 📋 **事前準備**

### **必要なもの**
- Googleアカウント
- Google Cloud Project（無料枠で十分）
- インターネット接続

## 🔧 **Step 1: Google Cloud Projectの設定**

### **1.1 Google Cloud Consoleにアクセス**
1. [Google Cloud Console](https://console.cloud.google.com/) を開く
2. Googleアカウントでログイン

### **1.2 プロジェクトを作成**
1. 画面上部のプロジェクト選択ドロップダウンをクリック
2. 「新しいプロジェクト」を選択
3. プロジェクト名を入力（例：「tiktok-viral-detector」）
4. 「作成」をクリック

### **1.3 APIを有効化**
1. 左側メニューから「APIとサービス」→「ライブラリ」を選択
2. 検索ボックスで「Google Sheets API」を検索
3. 「Google Sheets API」をクリックして「有効にする」をクリック
4. 同様に「Google Drive API」も有効化

## 👤 **Step 2: サービスアカウントの作成**

### **2.1 サービスアカウントを作成**
1. 左側メニューから「IAMと管理」→「サービスアカウント」を選択
2. 「サービスアカウントを作成」をクリック
3. 以下の情報を入力：
   - **サービスアカウント名**: `tiktok-viral-detector`
   - **サービスアカウントID**: 自動生成される
   - **説明**: `TikTok Viral Video Detector用サービスアカウント`
4. 「作成して続行」をクリック

### **2.2 権限を設定**
1. 「役割を選択」で「編集者」を選択
2. 「完了」をクリック

### **2.3 キーを作成**
1. 作成されたサービスアカウントをクリック
2. 「キー」タブを選択
3. 「キーを追加」→「新しいキーを作成」をクリック
4. 「JSON」を選択して「作成」をクリック
5. **`credentials.json`** ファイルがダウンロードされます

## 📊 **Step 3: Google Sheetsの準備**

### **3.1 スプレッドシートを作成**
1. [Google Sheets](https://sheets.google.com/) にアクセス
2. 「空白」をクリックして新しいスプレッドシートを作成
3. スプレッドシートの名前を変更（例：「TikTok Viral Videos」）

### **3.2 スプレッドシートIDを取得**
1. ブラウザのアドレスバーを確認
2. URLの形式：
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```
3. **SPREADSHEET_ID**部分をコピー（例：`1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`）

### **3.3 権限を設定**
1. スプレッドシートで「共有」ボタンをクリック
2. サービスアカウントのメールアドレスを追加：
   - 形式：`tiktok-viral-detector@PROJECT_ID.iam.gserviceaccount.com`
   - 例：`tiktok-viral-detector@my-project-123456.iam.gserviceaccount.com`
3. 権限を「編集者」に設定
4. 「送信」をクリック

## ⚙️ **Step 4: プロジェクトの設定**

### **4.1 ファイルを配置**
1. ダウンロードした `credentials.json` をプロジェクトのルートディレクトリに配置
2. ファイル構造：
   ```
   tiktok-viral-detector-mvp/
   ├── credentials.json          ← ここに配置
   ├── config.json
   ├── main_fixed_v2.py
   └── ...
   ```

### **4.2 設定ファイルを更新**
1. `config.json` を開く
2. 以下の項目を更新：
   ```json
   {
     "spreadsheet_id": "YOUR_ACTUAL_SPREADSHEET_ID",
     "use_mock": false,
     "google_sheets": {
       "enabled": true,
       "sheet_name": "バイラル動画_{timestamp}",
       "auto_format": true
     }
   }
   ```

## 🚀 **Step 5: 実行とテスト**

### **5.1 依存関係をインストール**
```bash
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
```

### **5.2 実行**
```bash
python3 main_fixed_v2.py
```

### **5.3 確認事項**
- ✅ CSVファイルが生成される
- ✅ Google Sheetsに新しいシートが作成される
- ✅ データが正しく出力される

## 🔍 **トラブルシューティング**

### **よくある問題**

#### **Q1: "credentials.jsonが見つかりません"エラー**
**A**: `credentials.json`ファイルがプロジェクトのルートディレクトリに配置されているか確認

#### **Q2: "権限がありません"エラー**
**A**: サービスアカウントのメールアドレスにスプレッドシートの編集権限が付与されているか確認

#### **Q3: "APIが無効です"エラー**
**A**: Google Cloud ConsoleでGoogle Sheets APIとGoogle Drive APIが有効化されているか確認

#### **Q4: "スプレッドシートが見つかりません"エラー**
**A**: `config.json`の`spreadsheet_id`が正しく設定されているか確認

## 📞 **サポート**

問題が解決しない場合は、以下を確認してください：
1. Google Cloud Consoleのログ
2. プロジェクトの実行ログ
3. 設定ファイルの内容

---

**🎉 設定完了後は、バイラル動画データが自動的にGoogle Sheetsに出力されます！**

