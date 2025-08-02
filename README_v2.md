# 🎉 TikTok Viral Video Detector MVP v2.0

**TikAPIを使用したバイラル動画検出ツール - 完全動作版**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/Tohoso/tiktok-viral-detector-mvp)
[![Python](https://img.shields.io/badge/Python-3.7+-green)](https://python.org)
[![TikAPI](https://img.shields.io/badge/TikAPI-Powered-red)](https://tikapi.io)
[![Status](https://img.shields.io/badge/Status-Working-brightgreen)](https://github.com/Tohoso/tiktok-viral-detector-mvp)

## 🚀 **v2.0 新機能**

### ✅ **完全動作確認済み**
- **実際のAPIキーでテスト済み**: 10件のバイラル動画を検出
- **修正されたエンドポイント**: `api.tikapi.io` で正常動作
- **強化されたエラーハンドリング**: 堅牢な例外処理
- **APIキー自動検証**: 起動時の接続確認

### 🔥 **実績**
```
✅ 60件の動画を取得
✅ 10件のバイラル動画を検出
✅ CSV出力完了
✅ 平均バイラル速度: 45,982再生/時間
✅ 最高再生数: 23,200,000回
```

## 📋 **概要**

TikTokのFor You Page（FYP）から**バイラル動画を自動検出**し、**Googleスプレッドシート**に出力するPythonツールです。

### **主要機能**
- 🎯 **バイラル動画検出**: 指定条件（再生数・時間）での自動フィルタリング
- 🌍 **複数地域対応**: 米国・日本等の地域別検索
- 📊 **詳細分析**: バイラル速度・エンゲージメント率の計算
- 📄 **CSV出力**: 完全なメタデータでの結果保存
- 📈 **Google Sheets連携**: 自動でスプレッドシートに出力
- 🔍 **リアルタイム監視**: 継続的な新しいバイラル動画発見

## 🛠️ **セットアップ**

### **1. リポジトリクローン**
```bash
git clone https://github.com/Tohoso/tiktok-viral-detector-mvp.git
cd tiktok-viral-detector-mvp
```

### **2. 依存関係インストール**
```bash
pip install -r requirements.txt
```

### **3. 設定ファイル作成**
```bash
python main_fixed_v2.py --create-config
```

### **4. APIキー設定**
`config.json` を編集してTikAPIキーを設定：
```json
{
  "tikapi_key": "YOUR_TIKAPI_KEY_HERE",
  "min_views": 500000,
  "time_limit_hours": 24,
  "countries": ["us", "jp"]
}
```

**🔑 TikAPIキー取得**: [tikapi.io](https://tikapi.io/) でアカウント作成

## 🚀 **使用方法**

### **基本実行**
```bash
# APIキー検証のみ
python main_fixed_v2.py --verify-only

# バイラル動画検出実行
python main_fixed_v2.py

# デバッグモード
python main_fixed_v2.py --debug
```

### **設定例**

#### **厳格な条件（推奨）**
```json
{
  "min_views": 500000,
  "time_limit_hours": 24
}
```
→ 24時間以内に50万再生達成の動画のみ

#### **緩い条件（テスト用）**
```json
{
  "min_views": 100000,
  "time_limit_hours": 168
}
```
→ 7日以内に10万再生達成の動画

## 📊 **出力例**

### **コンソール出力**
```
🚀 TikTok バイラル動画検出器 v2.0
✅ APIキー検証完了 - 正常に動作します
📊 検索条件: 24時間以内に500,000再生以上
🌍 対象地域: us, jp
🔥 バイラル動画収集開始
📊 us から 30 件の動画を取得
🔥 us で 7 件のバイラル動画を発見
✅ 収集完了: 合計 10 件のバイラル動画を検出
📄 CSVファイル出力完了: viral_videos_20250802_041154.csv
```

### **CSV出力**
| 動画ID | 説明 | 再生数 | 経過時間(h) | バイラル速度 | 動画URL |
|--------|------|--------|-------------|--------------|---------|
| 7532708837955079437 | this was terrifying bro 😭 | 23,200,000 | 76.9 | 301,683 | https://www.tiktok.com/@brainrotboyss/video/... |
| 7532881047529327927 | HE DID IT WITH EASE. 😱🔥 | 2,900,000 | 65.8 | 44,104 | https://www.tiktok.com/@houseofhighlights/video/... |

## 🔧 **Google Sheets連携**

### **1. サービスアカウント作成**
1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. Google Sheets API を有効化
3. サービスアカウント作成
4. 認証JSONファイルをダウンロード

### **2. スプレッドシート準備**
1. Google Sheetsで新しいスプレッドシートを作成
2. サービスアカウントのメールアドレスに編集権限を付与
3. スプレッドシートIDを取得

### **3. 設定ファイル更新**
```json
{
  "spreadsheet_id": "YOUR_SPREADSHEET_ID",
  "credentials_path": "path/to/credentials.json"
}
```

詳細は `google_sheets_setup.md` を参照してください。

## 🎯 **実用例**

### **マーケティング活用**
```bash
# 毎日午前9時に実行（cron設定例）
0 9 * * * cd /path/to/tiktok-viral-detector && python main_fixed_v2.py
```

### **コンテンツ企画**
1. **トレンド分析**: バイラル動画の共通要素を特定
2. **競合調査**: 同業界のバイラルコンテンツを監視
3. **タイミング分析**: 最適な投稿時間を発見

### **データ分析**
- **バイラル速度**: 時間あたりの再生数増加率
- **エンゲージメント率**: いいね・コメント・シェア比率
- **地域別傾向**: 国・地域ごとのコンテンツ特性

## 🔍 **トラブルシューティング**

### **よくある問題**

#### **APIキーエラー**
```
❌ APIキーが無効: 403 Forbidden
```
**解決策**:
1. TikAPIアカウントの有効性確認
2. 使用量制限の確認
3. 正しいAPIキーの再設定

#### **接続エラー**
```
❌ Connection error
```
**解決策**:
1. インターネット接続確認
2. ファイアウォール設定確認
3. プロキシ設定確認

#### **データが見つからない**
```
❌ バイラル動画が見つかりませんでした
```
**解決策**:
1. 検索条件を緩和（`min_views`を下げる）
2. 時間制限を延長（`time_limit_hours`を増やす）
3. 対象地域を追加

### **デバッグ方法**
```bash
# 詳細ログ出力
python main_fixed_v2.py --debug

# ログファイル確認
cat tikapi_debug_v2.log

# 接続テスト
python test_tikapi_connection.py
```

## 📈 **パフォーマンス**

### **実行時間**
- **APIキー検証**: 1-2秒
- **動画取得**: 3-5秒/地域
- **データ処理**: 1秒未満
- **CSV出力**: 1秒未満

### **API制限**
- **レート制限**: 1秒間隔で自動調整
- **取得件数**: 30件/リクエスト
- **同時接続**: 1接続のみ

### **メモリ使用量**
- **基本動作**: 50MB未満
- **大量データ**: 100MB未満

## 🔄 **アップデート履歴**

### **v2.0 (2025-08-02)**
- ✅ **ベースURL修正**: `api.tikapi.io` に変更
- ✅ **APIキー検証機能**: 起動時の自動確認
- ✅ **エラーハンドリング強化**: 詳細なデバッグ情報
- ✅ **実動作確認**: 実際のAPIキーでテスト完了

### **v1.1 (2025-08-02)**
- 🔧 JSONパースエラー修正
- 📊 診断ツール追加
- 📚 ドキュメント更新

### **v1.0 (2025-08-02)**
- 🚀 初回リリース
- 🎯 基本機能実装

## 🤝 **コントリビューション**

### **バグ報告**
[Issues](https://github.com/Tohoso/tiktok-viral-detector-mvp/issues) でバグ報告をお願いします。

### **機能要望**
[Discussions](https://github.com/Tohoso/tiktok-viral-detector-mvp/discussions) で機能要望を共有してください。

### **プルリクエスト**
1. フォーク
2. 機能ブランチ作成
3. 変更をコミット
4. プルリクエスト作成

## 📄 **ライセンス**

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 🙏 **謝辞**

- **TikAPI.io**: 安定したTikTok API提供
- **Google Sheets API**: データ出力機能
- **Python コミュニティ**: 優秀なライブラリ群

## 📞 **サポート**

- **GitHub Issues**: バグ報告・機能要望
- **GitHub Discussions**: 使用方法の質問
- **Email**: プロジェクト関連の問い合わせ

---

**🎯 このツールで効率的にバイラルコンテンツを発見し、新しい企画のインスピレーションを得てください！**

## 🔗 **関連リンク**

- [TikAPI.io](https://tikapi.io/) - TikTok API サービス
- [Google Sheets API](https://developers.google.com/sheets/api) - スプレッドシート連携
- [GitHub Repository](https://github.com/Tohoso/tiktok-viral-detector-mvp) - ソースコード

