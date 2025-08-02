#!/usr/bin/env python3
"""
認証ファイル確認スクリプト
credentials.jsonの内容を確認
"""

import json
import os

def check_credentials():
    """認証ファイルの内容を確認"""
    print("🔍 認証ファイル確認")
    print("=" * 30)
    
    # ファイルの存在確認
    if not os.path.exists('credentials.json'):
        print("❌ credentials.jsonファイルが見つかりません")
        print("📝 Google Cloud Consoleからダウンロードして配置してください")
        return
    
    try:
        # ファイルの内容を読み込み
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        print("✅ credentials.jsonファイルが見つかりました")
        print(f"📧 Client Email: {creds.get('client_email', 'N/A')}")
        print(f"🏢 Project ID: {creds.get('project_id', 'N/A')}")
        print(f"🔑 Private Key ID: {creds.get('private_key_id', 'N/A')[:10]}...")
        
        # 必要なフィールドの確認
        required_fields = ['client_email', 'private_key', 'project_id']
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"⚠️ 不足しているフィールド: {missing_fields}")
        else:
            print("✅ 必要なフィールドがすべて含まれています")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSONファイルの形式が不正: {e}")
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")

if __name__ == "__main__":
    check_credentials() 