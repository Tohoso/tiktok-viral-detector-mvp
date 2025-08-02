# TikTok Viral Video Detector MVP 🚀

TikAPIを使用してFor You Pageから24時間以内に50万再生を達成したバイラル動画を自動検出し、Google Sheetsに出力するMVPツール

## 🎯 機能

- **TikAPI連携**: For You Page + トレンド動画の網羅的取得
- **バイラル検出**: 24時間以内50万再生条件の自動判定
- **Google Sheets出力**: 表形式での結果整理・共有
- **CSV出力**: ローカルファイルでのデータ保存
- **複数地域対応**: 米国・日本等の地域別検索
- **リアルタイム処理**: 投稿時刻と再生数による即座判定

## 📋 出力データ

| 項目 | 説明 |
|------|------|
| 動画ID | TikTok動画の一意識別子 |
| 説明 | 動画の説明文（100文字まで） |
| 再生数 | 現在の再生数 |
| いいね数 | いいね数 |
| コメント数 | コメント数 |
| シェア数 | シェア数 |
| アカウント名 | 投稿者のユーザー名 |
| フォロワー数 | 投稿者のフォロワー数 |
| 投稿日時 | 動画の投稿日時 |
| 経過時間(h) | 投稿からの経過時間 |
| バイラル速度 | 再生数/時間の比率 |
| 動画URL | TikTok動画への直接リンク |
| ハッシュタグ | 使用されているハッシュタグ |
| 認証済み | アカウントの認証状態 |

## 🛠️ セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 設定ファイルの作成

```bash
python main.py --create-config
```

### 3. TikAPIキーの設定

1. [TikAPI](https://tikapi.io/) でアカウント作成
2. APIキーを取得
3. `config.json` の `tikapi_key` を更新

```json
{
  "tikapi_key": "your_actual_tikapi_key_here"
}
```

### 4. Google Sheets設定（オプション）

#### A. Google Cloud Console設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. Google Sheets API を有効化
3. サービスアカウントを作成
4. 認証キー（JSON）をダウンロード → `credentials.json`

#### B. スプレッドシート設定

1. Google Sheetsで新しいスプレッドシートを作成
2. スプレッドシートIDをコピー（URLの一部）
3. スプレッドシートをサービスアカウントと共有
4. `config.json` の `spreadsheet_id` を更新

```json
{
  "spreadsheet_id": "1ABC123def456GHI789jkl..."
}
```

## 🚀 使用方法

### 基本実行

```bash
python main.py
```

### カスタム設定ファイル使用

```bash
python main.py --config my_config.json
```

### 実行例

```
🚀 TikTok バイラル動画検出を開始します
📊 条件: 24時間以内に500,000再生以上
🌍 US 地域の動画を検索中...
📈 リクエスト 1/10: 45件処理, 3件バイラル検出
🔥 バイラル動画: Amazing dance trend everyone is doing... (750,000再生, 18.5h経過)
🔥 バイラル動画: Cooking hack that will blow your mind... (1,200,000再生, 12.3h経過)

✅ 収集完了: 450件処理, 12件のバイラル動画を検出

🎉 12件のバイラル動画を検出しました！
📄 CSVファイル: viral_videos_20250802_143022.csv
📊 Google Sheetsに出力完了
✅ 処理完了
```

## ⚙️ 設定オプション

### config.json 設定項目

```json
{
  "tikapi_key": "YOUR_TIKAPI_KEY_HERE",
  "min_views": 500000,
  "time_limit_hours": 24,
  "max_requests": 10,
  "countries": ["us", "jp"],
  "spreadsheet_id": "YOUR_SPREADSHEET_ID_HERE",
  "credentials_path": "credentials.json",
  "output_csv": true,
  "csv_filename": "viral_videos_{timestamp}.csv"
}
```

| 設定項目 | 説明 | デフォルト |
|----------|------|------------|
| `tikapi_key` | TikAPIのAPIキー | 必須 |
| `min_views` | 最小再生数（バイラル条件） | 500000 |
| `time_limit_hours` | 時間制限（時間） | 24 |
| `max_requests` | 地域あたりの最大リクエスト数 | 10 |
| `countries` | 検索対象国（ISO 2文字コード） | ["us", "jp"] |
| `spreadsheet_id` | Google SheetsのスプレッドシートID | オプション |
| `credentials_path` | Google認証ファイルパス | "credentials.json" |
| `output_csv` | CSV出力の有効/無効 | true |

## 📊 出力例

### CSV出力
```csv
動画ID,説明,再生数,いいね数,コメント数,シェア数,アカウント名,フォロワー数,投稿日時,経過時間(h),バイラル速度,動画URL,ハッシュタグ,認証済み
7123456789,Amazing dance trend everyone is doing...,750000,45000,3200,1800,user123,25000,2025-08-02 10:30:00,18.5,40540,https://www.tiktok.com/@user123/video/7123456789,dance viral trending,
```

### Google Sheets出力
- 自動フォーマット（ヘッダー色付け、数値カンマ区切り）
- 列幅自動調整
- 動画URLクリック可能
- 日時スタンプ付きシート名

## 🔧 技術仕様

### アーキテクチャ

```
TikTokViralMVP
├── TikAPIClient (API通信)
├── ViralVideoDetector (バイラル判定)
├── GoogleSheetsExporter (出力処理)
└── 設定管理・ログ・エラーハンドリング
```

### データフロー

1. **データ取得**: TikAPI → FYP + トレンド動画
2. **フィルタリング**: 24時間以内 + 50万再生以上
3. **データ整形**: 動画情報の抽出・計算
4. **重複除去**: 動画IDベースの重複排除
5. **出力**: CSV + Google Sheets

### レート制限対応

- **TikAPI**: 1秒間隔でのリクエスト制御
- **Google Sheets**: バッチ更新による効率化
- **エラーハンドリング**: 自動リトライとログ記録

## ⚠️ 注意事項

### API制限

- **TikAPI**: プランに応じた月間制限
- **取得件数**: 30件/リクエスト（TikAPI制限）
- **レート制限**: 1秒/リクエスト（安全マージン）

### データ品質

- **リアルタイム性**: API提供データに依存
- **完全性**: 24時間以内の全動画を保証するものではない
- **精度**: フィルタリング条件は目安として使用

### 利用規約

- **TikTok**: 利用規約の遵守
- **TikAPI**: サービス規約の確認
- **Google Sheets**: API利用制限の考慮

## 🚨 トラブルシューティング

### よくある問題

**Q: "TikAPIキーが設定されていません" エラー**
A: `config.json` の `tikapi_key` を実際のAPIキーに更新してください

**Q: Google Sheets出力ができない**
A: 
1. `credentials.json` ファイルの存在確認
2. スプレッドシートの共有設定確認
3. Google Sheets APIの有効化確認

**Q: バイラル動画が検出されない**
A:
1. 検索条件（再生数・時間制限）の調整
2. 検索地域の変更
3. リクエスト数の増加

**Q: "EmptyResponseException" エラー**
A: TikAPIの制限またはネットワークエラー。時間をおいて再実行

### ログファイル

実行ログは `tiktok_viral_mvp.log` に保存されます：

```
2025-08-02 14:30:22 - INFO - 🚀 TikTok バイラル動画検出を開始します
2025-08-02 14:30:22 - INFO - 📊 条件: 24時間以内に500,000再生以上
2025-08-02 14:30:25 - INFO - 📈 リクエスト 1/10: 45件処理, 3件バイラル検出
```

## 📈 パフォーマンス

### 処理速度

- **1リクエスト**: 約2-3秒（レート制限含む）
- **10リクエスト**: 約30-40秒
- **100動画処理**: 約5-10秒

### メモリ使用量

- **基本動作**: 約50MB
- **大量データ**: 約100-200MB（1000件処理時）

## 🔮 今後の拡張予定

### v1.1 予定機能

- **継続監視モード**: 定期実行による自動更新
- **Slack/Discord通知**: バイラル検出時の即座通知
- **詳細分析**: ハッシュタグ・音楽トレンド分析
- **フィルタ強化**: アカウント投稿数・認証状態フィルター

### v2.0 予定機能

- **Twitter連携**: X(Twitter)バイラル動画の同時検出
- **AI分析**: コンテンツパターン自動分析
- **ダッシュボード**: Web UIでのリアルタイム監視
- **API提供**: 他システムとの連携API

## 📄 ライセンス

MIT License

## 🤝 サポート

- **Issues**: GitHub Issues でバグ報告・機能要望
- **Email**: 技術的な質問・サポート
- **Documentation**: 詳細ドキュメントは Wiki を参照

---

**開発者**: Manus AI  
**バージョン**: 1.0.0  
**最終更新**: 2025年8月2日

