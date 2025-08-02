#!/usr/bin/env python3
"""
TikTok Viral Video Detector MVP テストスクリプト

各コンポーネントの動作確認とデバッグ用
"""

import json
import os
import sys
from datetime import datetime, timedelta
import logging

# テスト用のダミーデータ
DUMMY_TIKTOK_RESPONSE = {
    "itemList": [
        {
            "id": "7123456789012345678",
            "desc": "Amazing dance trend everyone is doing! #viral #dance #fyp",
            "createTime": int((datetime.now() - timedelta(hours=18)).timestamp()),
            "stats": {
                "playCount": 1500000,
                "likeCount": 75000,
                "commentCount": 5000,
                "shareCount": 2000
            },
            "author": {
                "uniqueId": "dancer_pro",
                "followerCount": 250000,
                "verified": False
            },
            "textExtra": [
                {"hashtagName": "viral", "title": "viral"},
                {"hashtagName": "dance", "title": "dance"},
                {"hashtagName": "fyp", "title": "fyp"}
            ]
        },
        {
            "id": "7987654321098765432",
            "desc": "Cooking hack that will blow your mind 🤯",
            "createTime": int((datetime.now() - timedelta(hours=12)).timestamp()),
            "stats": {
                "playCount": 850000,
                "likeCount": 42000,
                "commentCount": 3200,
                "shareCount": 1500
            },
            "author": {
                "uniqueId": "chef_master",
                "followerCount": 180000,
                "verified": True
            },
            "textExtra": [
                {"hashtagName": "cooking", "title": "cooking"},
                {"hashtagName": "hack", "title": "hack"}
            ]
        },
        {
            "id": "7555666777888999000",
            "desc": "This trend is everywhere now",
            "createTime": int((datetime.now() - timedelta(hours=6)).timestamp()),
            "stats": {
                "playCount": 300000,  # 50万未満（バイラル条件に不適合）
                "likeCount": 15000,
                "commentCount": 800,
                "shareCount": 400
            },
            "author": {
                "uniqueId": "regular_user",
                "followerCount": 5000,
                "verified": False
            },
            "textExtra": []
        }
    ],
    "hasMore": True
}

def test_config_loading():
    """設定ファイル読み込みテスト"""
    print("🧪 設定ファイル読み込みテスト")
    print("-" * 40)
    
    try:
        # メインモジュールをインポート
        from main import TikTokViralMVP
        
        # 設定ファイルが存在しない場合のテスト
        if not os.path.exists('config.json'):
            print("⚠️ config.json が見つかりません。サンプル設定でテスト")
            mvp = TikTokViralMVP()
            mvp.create_sample_config()
        
        # 設定読み込み
        mvp = TikTokViralMVP('config.json')
        
        print(f"✅ TikAPIキー: {'設定済み' if mvp.config['tikapi_key'] != 'YOUR_TIKAPI_KEY_HERE' else '未設定'}")
        print(f"✅ 最小再生数: {mvp.config['min_views']:,}")
        print(f"✅ 時間制限: {mvp.config['time_limit_hours']}時間")
        print(f"✅ 検索地域: {mvp.config['countries']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 設定読み込みエラー: {e}")
        return False

def test_viral_detection():
    """バイラル検出ロジックテスト"""
    print("\n🧪 バイラル検出ロジックテスト")
    print("-" * 40)
    
    try:
        from main import ViralVideoDetector
        
        detector = ViralVideoDetector(min_views=500000, time_limit_hours=24)
        
        test_results = []
        for video in DUMMY_TIKTOK_RESPONSE["itemList"]:
            is_viral = detector.is_viral_video(video)
            video_info = detector.extract_video_info(video)
            
            test_results.append({
                'id': video['id'],
                'desc': video['desc'][:50] + '...',
                'views': video['stats']['playCount'],
                'hours': video_info['hours_since_post'],
                'is_viral': is_viral
            })
            
            status = "🔥 バイラル" if is_viral else "❌ 非バイラル"
            print(f"{status}: {video_info['description'][:30]}...")
            print(f"   👀 {video_info['views']:,}再生 | ⏰ {video_info['hours_since_post']}h経過")
        
        viral_count = sum(1 for r in test_results if r['is_viral'])
        print(f"\n📊 結果: {len(test_results)}件中 {viral_count}件がバイラル条件に適合")
        
        return viral_count > 0
        
    except Exception as e:
        print(f"❌ バイラル検出テストエラー: {e}")
        return False

def test_csv_export():
    """CSV出力テスト"""
    print("\n🧪 CSV出力テスト")
    print("-" * 40)
    
    try:
        from main import TikTokViralMVP, ViralVideoDetector
        
        # ダミーデータでバイラル動画を生成
        detector = ViralVideoDetector()
        viral_videos = []
        
        for video in DUMMY_TIKTOK_RESPONSE["itemList"]:
            if detector.is_viral_video(video):
                viral_info = detector.extract_video_info(video)
                viral_videos.append(viral_info)
        
        if not viral_videos:
            print("⚠️ バイラル動画がないため、ダミーデータを作成")
            viral_videos = [detector.extract_video_info(DUMMY_TIKTOK_RESPONSE["itemList"][0])]
        
        # CSV出力テスト
        mvp = TikTokViralMVP()
        csv_file = mvp.export_to_csv(viral_videos)
        
        if csv_file and os.path.exists(csv_file):
            file_size = os.path.getsize(csv_file)
            print(f"✅ CSV出力成功: {csv_file}")
            print(f"📄 ファイルサイズ: {file_size} bytes")
            
            # ファイル内容の確認
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
                print(f"📝 行数: {len(lines)}行")
                print(f"📋 ヘッダー: {lines[0].strip()}")
            
            return True
        else:
            print("❌ CSV出力失敗")
            return False
            
    except Exception as e:
        print(f"❌ CSV出力テストエラー: {e}")
        return False

def test_google_sheets_connection():
    """Google Sheets接続テスト"""
    print("\n🧪 Google Sheets接続テスト")
    print("-" * 40)
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # 認証ファイルの存在確認
        if not os.path.exists('credentials.json'):
            print("⚠️ credentials.json が見つかりません")
            print("💡 Google Sheets連携を使用する場合は、google_sheets_setup.md を参照してください")
            return False
        
        # 認証テスト
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        gc = gspread.authorize(creds)
        
        print("✅ Google Sheets API認証成功")
        
        # 設定ファイルからスプレッドシートIDを取得
        config = {}
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
        
        spreadsheet_id = config.get('spreadsheet_id', '')
        
        if spreadsheet_id and spreadsheet_id != 'YOUR_SPREADSHEET_ID_HERE':
            # 指定されたスプレッドシートに接続テスト
            spreadsheet = gc.open_by_key(spreadsheet_id)
            print(f"✅ スプレッドシート接続成功: {spreadsheet.title}")
            print(f"🔗 URL: {spreadsheet.url}")
            
            # テストデータ書き込み
            try:
                worksheet = spreadsheet.sheet1
                test_data = [
                    ['テスト項目', '結果', '実行時刻'],
                    ['接続テスト', '成功', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                ]
                worksheet.update('A1', test_data)
                print("✅ テストデータ書き込み成功")
                
            except Exception as e:
                print(f"⚠️ 書き込みテスト失敗: {e}")
        else:
            print("⚠️ スプレッドシートIDが設定されていません")
            print("💡 config.json でスプレッドシートIDを設定してください")
        
        return True
        
    except ImportError:
        print("⚠️ Google Sheets関連ライブラリがインストールされていません")
        print("💡 pip install gspread google-auth でインストールしてください")
        return False
    except Exception as e:
        print(f"❌ Google Sheets接続エラー: {e}")
        return False

def test_tikapi_mock():
    """TikAPI モック接続テスト"""
    print("\n🧪 TikAPI モック接続テスト")
    print("-" * 40)
    
    try:
        from main import TikAPIClient
        
        # ダミーキーでクライアント作成
        client = TikAPIClient("dummy_key_for_testing")
        
        print("✅ TikAPIクライアント初期化成功")
        print(f"🔗 ベースURL: {client.base_url}")
        print(f"⏱️ レート制限間隔: {client.min_request_interval}秒")
        
        # 実際のAPIコールはスキップ（ダミーキーのため）
        print("⚠️ 実際のAPI接続テストはスキップ（ダミーキー使用）")
        print("💡 実際のテストには有効なTikAPIキーが必要です")
        
        return True
        
    except Exception as e:
        print(f"❌ TikAPIクライアントテストエラー: {e}")
        return False

def test_data_processing():
    """データ処理テスト"""
    print("\n🧪 データ処理テスト")
    print("-" * 40)
    
    try:
        from main import TikTokViralMVP
        
        mvp = TikTokViralMVP()
        
        # 動画マージテスト
        fyp_videos = DUMMY_TIKTOK_RESPONSE["itemList"][:2]
        trending_videos = DUMMY_TIKTOK_RESPONSE["itemList"][1:]  # 重複あり
        
        merged = mvp._merge_videos(fyp_videos, trending_videos)
        print(f"✅ 動画マージ: {len(fyp_videos)} + {len(trending_videos)} → {len(merged)}件（重複除去）")
        
        # 重複除去テスト
        viral_videos = [
            {'video_id': '123', 'description': 'Test 1'},
            {'video_id': '456', 'description': 'Test 2'},
            {'video_id': '123', 'description': 'Test 1 Duplicate'},  # 重複
        ]
        
        unique = mvp._remove_duplicates(viral_videos)
        print(f"✅ 重複除去: {len(viral_videos)} → {len(unique)}件")
        
        return True
        
    except Exception as e:
        print(f"❌ データ処理テストエラー: {e}")
        return False

def run_all_tests():
    """全テストを実行"""
    print("🚀 TikTok Viral Video Detector MVP テスト開始")
    print("=" * 60)
    
    tests = [
        ("設定ファイル読み込み", test_config_loading),
        ("バイラル検出ロジック", test_viral_detection),
        ("CSV出力", test_csv_export),
        ("データ処理", test_data_processing),
        ("TikAPI モック接続", test_tikapi_mock),
        ("Google Sheets接続", test_google_sheets_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} テスト成功")
            else:
                print(f"❌ {test_name} テスト失敗")
        except Exception as e:
            print(f"💥 {test_name} テスト例外: {e}")
        
        print()  # 空行
    
    print("=" * 60)
    print(f"📊 テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 全テスト成功！MVPは正常に動作する準備ができています")
        print("\n📋 次のステップ:")
        print("1. TikAPIキーを config.json に設定")
        print("2. Google Sheets設定（オプション）")
        print("3. python main.py で実行")
    else:
        print("⚠️ 一部テストが失敗しました。問題を確認してください")
        
        if not os.path.exists('config.json'):
            print("\n💡 まず python main.py --create-config で設定ファイルを作成してください")

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TikTok Viral MVP テストスクリプト')
    parser.add_argument('--test', choices=[
        'config', 'viral', 'csv', 'sheets', 'tikapi', 'data', 'all'
    ], default='all', help='実行するテスト')
    
    args = parser.parse_args()
    
    # ログ設定
    logging.basicConfig(level=logging.WARNING)  # テスト中はWARNING以上のみ表示
    
    if args.test == 'all':
        run_all_tests()
    elif args.test == 'config':
        test_config_loading()
    elif args.test == 'viral':
        test_viral_detection()
    elif args.test == 'csv':
        test_csv_export()
    elif args.test == 'sheets':
        test_google_sheets_connection()
    elif args.test == 'tikapi':
        test_tikapi_mock()
    elif args.test == 'data':
        test_data_processing()

if __name__ == "__main__":
    main()

