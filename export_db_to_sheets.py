#!/usr/bin/env python3
"""
DBから動画データを再生回数順に抽出してGoogleスプレッドシートに転記
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import List, Dict
import logging

# Google Sheets連携用
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    print("⚠️ Google Sheets連携ライブラリが見つかりません。pip install gspread google-auth でインストールしてください。")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('export_db_to_sheets.log'),
        logging.StreamHandler()
    ]
)

class DatabaseExporter:
    """DBからデータを抽出するクラス"""
    
    def __init__(self, db_path: str = "tiktok_viral_videos.db"):
        self.db_path = db_path
    
    def get_videos_by_views(self, limit: int = None) -> List[Dict]:
        """再生回数順に動画データを取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT 
                video_id,
                description,
                views,
                likes,
                comments,
                shares,
                author_username,
                author_nickname,
                follower_count,
                create_time,
                hours_since_post,
                viral_speed,
                video_url,
                hashtags,
                verified,
                country,
                collected_at,
                is_viral
            FROM all_videos 
            ORDER BY views DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            videos = []
            for row in rows:
                video = {
                    'video_id': row[0],
                    'description': row[1] or '',
                    'views': row[2] or 0,
                    'likes': row[3] or 0,
                    'comments': row[4] or 0,
                    'shares': row[5] or 0,
                    'author_username': row[6] or '',
                    'author_nickname': row[7] or '',
                    'follower_count': row[8] or 0,
                    'create_time': row[9] or '',
                    'hours_since_post': row[10] or 0,
                    'viral_speed': row[11] or 0,
                    'video_url': row[12] or '',
                    'hashtags': row[13] or '',
                    'verified': row[14] or False,
                    'country': row[15] or '',
                    'collected_at': row[16] or '',
                    'is_viral': row[17] or False
                }
                videos.append(video)
            
            conn.close()
            logging.info(f"✅ {len(videos)}件の動画データを取得しました")
            return videos
            
        except Exception as e:
            logging.error(f"❌ DBからのデータ取得エラー: {e}")
            return []

class GoogleSheetsExporter:
    """Google Sheetsにデータを転記するクラス"""
    
    def __init__(self, credentials_path: str = "credentials.json"):
        self.credentials_path = credentials_path
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Google Sheets APIクライアントを初期化"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE:
                logging.error("❌ Google Sheetsライブラリが利用できません")
                return False
            
            if not os.path.exists(self.credentials_path):
                logging.error(f"❌ credentials.jsonが見つかりません: {self.credentials_path}")
                return False
            
            # スコープ設定
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # 認証情報読み込み
            credentials = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scope
            )
            
            self.client = gspread.authorize(credentials)
            logging.info("✅ Google Sheets APIクライアント初期化完了")
            return True
            
        except Exception as e:
            logging.error(f"❌ Google Sheets初期化エラー: {e}")
            return False
    
    def export_to_sheets(self, videos: List[Dict], spreadsheet_id: str, sheet_name: str = "DB動画データ") -> bool:
        """動画データをスプレッドシートに転記"""
        try:
            if not self.client:
                logging.error("❌ Google Sheetsクライアントが初期化されていません")
                return False
            
            # スプレッドシートを開く
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            logging.info(f"✅ スプレッドシートを開きました: {spreadsheet.title}")
            
            # シートを取得または作成
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                logging.info(f"✅ 既存のシートを使用: {sheet_name}")
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
                logging.info(f"✅ 新しいシートを作成: {sheet_name}")
            
            # ヘッダー行を準備
            headers = [
                '順位', '動画ID', '説明', '再生回数', 'いいね数', 'コメント数', 'シェア数',
                '作者ユーザー名', '作者ニックネーム', 'フォロワー数', '投稿時間', '投稿からの時間(時間)',
                'バイラル速度', '動画URL', 'ハッシュタグ', '認証済み', '国', '収集日時', 'バイラル判定'
            ]
            
            # データ行を準備
            data_rows = [headers]
            for i, video in enumerate(videos, 1):
                row = [
                    i,  # 順位
                    video['video_id'],
                    video['description'][:100] + '...' if len(video['description']) > 100 else video['description'],  # 説明を100文字に制限
                    video['views'],
                    video['likes'],
                    video['comments'],
                    video['shares'],
                    video['author_username'],
                    video['author_nickname'],
                    video['follower_count'],
                    video['create_time'],
                    round(video['hours_since_post'], 1) if video['hours_since_post'] else 0,
                    video['viral_speed'],
                    video['video_url'],
                    video['hashtags'][:50] + '...' if len(video['hashtags']) > 50 else video['hashtags'],  # ハッシュタグを50文字に制限
                    '✓' if video['verified'] else '✗',
                    video['country'],
                    video['collected_at'],
                    '✓' if video['is_viral'] else '✗'
                ]
                data_rows.append(row)
            
            # 既存データをクリア
            worksheet.clear()
            
            # データを一括更新
            worksheet.update('A1', data_rows)
            
            # フォーマット設定
            self._format_worksheet(worksheet, len(data_rows))
            
            logging.info(f"✅ {len(videos)}件の動画データをスプレッドシートに転記完了")
            logging.info(f"📊 スプレッドシートURL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ スプレッドシート転記エラー: {e}")
            return False
    
    def _format_worksheet(self, worksheet, data_rows: int):
        """ワークシートのフォーマットを設定"""
        try:
            # ヘッダー行のフォーマット
            worksheet.format('A1:S1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'horizontalAlignment': 'CENTER'
            })
            
            # 再生回数列のフォーマット（数値）
            worksheet.format(f'D2:D{data_rows}', {
                'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}
            })
            
            # いいね数、コメント数、シェア数列のフォーマット
            for col in ['E', 'F', 'G']:
                worksheet.format(f'{col}2:{col}{data_rows}', {
                    'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}
                })
            
            # フォロワー数列のフォーマット
            worksheet.format(f'J2:J{data_rows}', {
                'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}
            })
            
            # 投稿からの時間列のフォーマット
            worksheet.format(f'L2:L{data_rows}', {
                'numberFormat': {'type': 'NUMBER', 'pattern': '0.0'}
            })
            
            # 列幅の自動調整
            worksheet.columns_auto_resize(0, 18)
            
            logging.info("✅ ワークシートのフォーマット設定完了")
            
        except Exception as e:
            logging.warning(f"⚠️ フォーマット設定エラー: {e}")

class DBToSheetsExporter:
    """DBからGoogle Sheetsへの一括エクスポート"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.db_exporter = DatabaseExporter()
        self.sheets_exporter = GoogleSheetsExporter(self.config.get('credentials_path', 'credentials.json'))
    
    def _load_config(self, config_path: str) -> Dict:
        """設定ファイルを読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"❌ 設定ファイル読み込みエラー: {e}")
            return {}
    
    def export_all_videos(self, limit: int = None) -> bool:
        """全動画データをスプレッドシートに転記"""
        try:
            logging.info("🚀 DBからGoogle Sheetsへの転記開始")
            
            # DBから動画データを取得
            videos = self.db_exporter.get_videos_by_views(limit)
            
            if not videos:
                logging.error("❌ 転記する動画データがありません")
                return False
            
            # Google Sheetsに転記
            spreadsheet_id = self.config.get('spreadsheet_id')
            if not spreadsheet_id:
                logging.error("❌ スプレッドシートIDが設定されていません")
                return False
            
            success = self.sheets_exporter.export_to_sheets(
                videos, 
                spreadsheet_id, 
                f"DB動画データ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if success:
                logging.info("✅ DBからGoogle Sheetsへの転記が完了しました")
                return True
            else:
                logging.error("❌ 転記に失敗しました")
                return False
                
        except Exception as e:
            logging.error(f"❌ 転記処理エラー: {e}")
            return False

def main():
    """メイン実行関数"""
    print("📊 DBからGoogle Sheetsへの転記ツール")
    print("=" * 50)
    
    exporter = DBToSheetsExporter()
    
    # 全動画データを転記
    success = exporter.export_all_videos()
    
    if success:
        print("✅ 転記が正常に完了しました！")
        print(f"📊 スプレッドシートURL: https://docs.google.com/spreadsheets/d/{exporter.config.get('spreadsheet_id')}")
    else:
        print("❌ 転記に失敗しました。ログを確認してください。")

if __name__ == "__main__":
    main() 