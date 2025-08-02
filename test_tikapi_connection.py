#!/usr/bin/env python3
"""
TikAPI 接続テストスクリプト
JSONパースエラーの原因を特定するためのデバッグツール
"""

import requests
import json
import sys
from datetime import datetime

def test_tikapi_connection(api_key: str):
    """
    TikAPI接続テスト
    
    Args:
        api_key: TikAPIキー
    """
    print("🔍 TikAPI 接続テスト開始")
    print("=" * 50)
    
    # テスト対象のエンドポイント
    endpoints = [
        "public/explore",
        "public/trending", 
        "public/feed",
        "public/check"
    ]
    
    base_url = "https://tikapi.io/api/v1"
    
    # 異なる認証方法をテスト
    auth_methods = [
        {"name": "X-API-KEY", "headers": {"X-API-KEY": api_key, "Content-Type": "application/json"}},
        {"name": "Authorization Bearer", "headers": {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}},
        {"name": "Authorization Basic", "headers": {"Authorization": f"Basic {api_key}", "Content-Type": "application/json"}},
    ]
    
    for auth_method in auth_methods:
        print(f"\n🔑 認証方法: {auth_method['name']}")
        print("-" * 30)
        
        for endpoint in endpoints:
            url = f"{base_url}/{endpoint}"
            
            print(f"\n📡 テスト中: {endpoint}")
            print(f"URL: {url}")
            
            try:
                # パラメータ設定
                params = {}
                if endpoint in ["public/explore", "public/trending", "public/feed"]:
                    params = {"count": 5, "country": "us"}
                
                print(f"Headers: {auth_method['headers']}")
                print(f"Params: {params}")
                
                # リクエスト実行
                response = requests.get(
                    url, 
                    headers=auth_method['headers'], 
                    params=params,
                    timeout=30
                )
                
                print(f"Status Code: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
                print(f"Content-Length: {len(response.content)} bytes")
                
                # レスポンス内容の分析
                content = response.text
                
                if response.status_code == 200:
                    # JSONパースを試行
                    try:
                        data = response.json()
                        print("✅ JSON パース成功")
                        
                        # レスポンス構造の分析
                        if isinstance(data, dict):
                            print(f"レスポンス構造: {list(data.keys())}")
                            
                            if 'status' in data:
                                print(f"Status: {data['status']}")
                                if data['status'] == 'error':
                                    print(f"Error Message: {data.get('message', 'N/A')}")
                                elif data['status'] == 'success':
                                    if 'json' in data and 'itemList' in data['json']:
                                        items = data['json']['itemList']
                                        print(f"✅ 動画データ取得成功: {len(items)}件")
                                        
                                        # 最初の動画データをサンプル表示
                                        if items:
                                            sample = items[0]
                                            print(f"サンプル動画ID: {sample.get('id', 'N/A')}")
                                            print(f"サンプル再生数: {sample.get('stats', {}).get('playCount', 'N/A')}")
                                    else:
                                        print("⚠️ itemList が見つかりません")
                            else:
                                print("⚠️ status フィールドが見つかりません")
                        else:
                            print(f"⚠️ 予期しないレスポンス形式: {type(data)}")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON パースエラー: {e}")
                        print("レスポンス内容（最初の500文字）:")
                        print(content[:500])
                        print("...")
                        
                        # HTMLかどうかチェック
                        if content.strip().startswith('<!'):
                            print("🔍 HTMLページが返されています")
                            
                            # タイトルを抽出
                            import re
                            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                            if title_match:
                                print(f"ページタイトル: {title_match.group(1)}")
                else:
                    print(f"❌ HTTP エラー: {response.status_code}")
                    print("レスポンス内容（最初の500文字）:")
                    print(content[:500])
                    
            except requests.exceptions.Timeout:
                print("❌ タイムアウトエラー")
            except requests.exceptions.ConnectionError:
                print("❌ 接続エラー")
            except Exception as e:
                print(f"❌ 予期しないエラー: {e}")
            
            print("-" * 50)

def test_api_key_validity(api_key: str):
    """APIキーの有効性をテスト"""
    print("\n🔑 APIキー有効性テスト")
    print("=" * 30)
    
    if not api_key or api_key == "YOUR_TIKAPI_KEY_HERE":
        print("❌ APIキーが設定されていません")
        return False
    
    print(f"APIキー: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else api_key}")
    print(f"APIキー長: {len(api_key)} 文字")
    
    # 一般的なAPIキー形式をチェック
    if len(api_key) < 10:
        print("⚠️ APIキーが短すぎる可能性があります")
    
    return True

def main():
    """メイン実行関数"""
    print("🚀 TikAPI 接続診断ツール")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # APIキーの取得
    api_key = input("TikAPI キーを入力してください: ").strip()
    
    if not test_api_key_validity(api_key):
        return
    
    # 接続テスト実行
    test_tikapi_connection(api_key)
    
    print("\n" + "=" * 50)
    print("🏁 テスト完了")
    print("\n💡 トラブルシューティングのヒント:")
    print("1. APIキーが正しいことを確認してください")
    print("2. TikAPI ダッシュボードで使用量制限を確認してください")
    print("3. 認証方法が正しいことを確認してください (X-API-KEY)")
    print("4. エンドポイントURLが正しいことを確認してください")

if __name__ == "__main__":
    main()

