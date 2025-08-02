# TikTok Viral Video Detector MVP

日本語動画に絞って24時間で50万再生以上のバイラル動画を検出し、DBに保存してGoogleスプレッドシートに転記するツール

## 🚀 機能

- **日本語動画収集**: 日本（jp）のTikTok動画を自動収集
- **バイラル検出**: 24時間で50万再生以上の動画を自動検出
- **DB保存**: SQLiteデータベースに全動画データを保存
- **Google Sheets連携**: 再生回数順にソートしてスプレッドシートに転記
- **レート制限対応**: API制限を考慮した安全な実行

## 📁 プロジェクト構造

```
tiktok-viral-detector-mvp/
├── main.py                    # メイン実行ファイル（DB保存版）
├── export_db_to_sheets.py     # DBからGoogle Sheets転記ツール
├── config.json               # 設定ファイル
├── credentials.json          # Google Sheets認証情報
├── requirements.txt          # Python依存関係
├── README.md                 # このファイル
├── SUCCESS_REPORT.md         # 成功レポート
├── export_summary.md         # 転記結果サマリー
├── google_sheets_setup.md    # Google Sheets設定ガイド
└── tiktok_viral_videos.db    # SQLiteデータベース
```

## 🛠️ セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 設定ファイルの準備

`config.json.template`を参考に`config.json`を作成：

```json
{
  "tikapi_key": "YOUR_TIKAPI_KEY",
  "min_views": 500000,
  "time_limit_hours": 24,
  "max_requests": 10,
  "countries": ["jp"],
  "spreadsheet_id": "YOUR_SPREADSHEET_ID",
  "credentials_path": "credentials.json",
  "output_csv": true,
  "csv_filename": "viral_videos_{timestamp}.csv",
  "use_mock": false
}
```

### 3. Google Sheets認証設定

`google_sheets_setup.md`を参考にGoogle Sheets APIの設定を行い、`credentials.json`を配置してください。

## 🎯 使用方法

### 動画収集とDB保存

```bash
python3 main.py
```

### DBからGoogle Sheetsへの転記

```bash
python3 export_db_to_sheets.py
```

## 📊 データベース構造

### all_videos テーブル
- `video_id`: 動画ID
- `description`: 動画説明
- `views`: 再生回数
- `likes`: いいね数
- `comments`: コメント数
- `shares`: シェア数
- `author_username`: 作者ユーザー名
- `author_nickname`: 作者ニックネーム
- `follower_count`: フォロワー数
- `create_time`: 投稿時間
- `hours_since_post`: 投稿からの経過時間
- `viral_speed`: バイラル速度
- `video_url`: 動画URL
- `hashtags`: ハッシュタグ
- `verified`: 認証済みフラグ
- `country`: 国
- `collected_at`: 収集日時
- `is_viral`: バイラル判定

### viral_videos テーブル
バイラル動画のみを格納（all_videosと同じ構造）

## 🔧 設定オプション

| 項目 | 説明 | デフォルト |
|------|------|------------|
| `tikapi_key` | TikAPIキー | 必須 |
| `min_views` | 最小再生回数 | 500000 |
| `time_limit_hours` | 時間制限（時間） | 24 |
| `max_requests` | 最大リクエスト数 | 10 |
| `countries` | 対象国リスト | ["jp"] |
| `spreadsheet_id` | Google Sheets ID | 必須 |
| `use_mock` | モックモード | false |

## 📈 実行結果例

### 最新実行結果（2025年8月2日）
- **収集動画数**: 231件
- **バイラル動画**: 0件（24時間で50万再生以上の条件を満たす動画なし）
- **最高再生数**: 261,800,000回
- **DB保存**: 完了
- **Google Sheets転記**: 完了

## 🔗 関連ファイル

- **SUCCESS_REPORT.md**: 詳細な成功レポート
- **export_summary.md**: 転記結果の詳細サマリー
- **google_sheets_setup.md**: Google Sheets設定ガイド

## ⚠️ 注意事項

- TikAPIキーが必要です
- Google Sheets APIの設定が必要です
- レート制限を考慮して実行してください
- DBファイルは自動生成されます

## 📝 ライセンス

MIT License

## ��‍💻 作者

Manus AI

