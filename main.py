#!/usr/bin/env python3
"""
TikTok Viral Video Detector MVP
TikAPIを使用してFor You Pageから24時間以内50万再生動画を検出

Author: Manus AI
Version: 1.0.0
Date: 2025-08-02
"""

import requests
import json
import time
import csv
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Google Sheets連携用
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    print("⚠️ Google Sheets連携ライブラリが見つかりません。pip install gspread google-auth でインストールしてください。")

class TikAPIClient:
    """TikAPI クライアント"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://tikapi.io/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        })
        
        # レート制限対応
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1秒間隔
    
    def _wait_for_rate_limit(self):
        """レート制限を考慮した待機"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def get_fyp_videos(self, count: int = 30, country: str = "us") -> Dict:
        """For You Page動画を取得"""
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}/public/explore"
        params = {
            "count": min(count, 30),  # TikAPIの制限
            "country": country
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logging.error(f"TikAPI リクエストエラー: {e}")
            return {"itemList": [], "hasMore": False}
    
    def get_trending_videos(self, count: int = 30, country: str = "us") -> Dict:
        """トレンド動画を取得（FYPの代替）"""
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}/public/trending"
        params = {
            "count": min(count, 30),
            "country": country
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logging.error(f"TikAPI トレンドリクエストエラー: {e}")
            return {"itemList": [], "hasMore": False}

class ViralVideoDetector:
    """バイラル動画検出器"""
    
    def __init__(self, min_views: int = 500000, time_limit_hours: int = 24):
        self.min_views = min_views
        self.time_limit_hours = time_limit_hours
    
    def is_viral_video(self, video: Dict) -> bool:
        """動画がバイラル条件を満たすかチェック"""
        try:
            # 投稿時刻の取得
            create_time = self._parse_create_time(video)
            if not create_time:
                return False
            
            # 24時間以内チェック
            time_diff = datetime.now() - create_time
            if time_diff > timedelta(hours=self.time_limit_hours):
                return False
            
            # 再生数チェック
            views = self._extract_view_count(video)
            return views >= self.min_views
            
        except Exception as e:
            logging.warning(f"バイラル判定エラー: {e}")
            return False
    
    def _parse_create_time(self, video: Dict) -> Optional[datetime]:
        """投稿時刻を解析"""
        try:
            # TikAPIの場合
            if 'createTime' in video:
                timestamp = video['createTime']
                if isinstance(timestamp, str):
                    timestamp = int(timestamp)
                return datetime.fromtimestamp(timestamp)
            
            # 他の形式の場合
            if 'create_time' in video:
                return datetime.fromtimestamp(video['create_time'])
            
            return None
            
        except (ValueError, TypeError) as e:
            logging.warning(f"時刻解析エラー: {e}")
            return None
    
    def _extract_view_count(self, video: Dict) -> int:
        """再生数を抽出"""
        try:
            # TikAPIの場合
            if 'stats' in video and 'playCount' in video['stats']:
                return int(video['stats']['playCount'])
            
            # 直接指定の場合
            if 'playCount' in video:
                return int(video['playCount'])
            
            if 'view_count' in video:
                return int(video['view_count'])
            
            return 0
            
        except (ValueError, TypeError):
            return 0
    
    def extract_video_info(self, video: Dict) -> Dict:
        """動画情報を抽出・整形"""
        create_time = self._parse_create_time(video)
        views = self._extract_view_count(video)
        
        # 経過時間計算
        hours_since_post = 0
        if create_time:
            time_diff = datetime.now() - create_time
            hours_since_post = round(time_diff.total_seconds() / 3600, 1)
        
        # バイラル速度計算
        viral_speed = 0
        if hours_since_post > 0:
            viral_speed = round(views / hours_since_post, 0)
        
        # 動画URL生成
        video_id = video.get('id', '')
        author_username = video.get('author', {}).get('uniqueId', '')
        video_url = f"https://www.tiktok.com/@{author_username}/video/{video_id}" if video_id and author_username else ""
        
        return {
            'video_id': video_id,
            'description': video.get('desc', '')[:100] + ('...' if len(video.get('desc', '')) > 100 else ''),
            'views': views,
            'likes': video.get('stats', {}).get('likeCount', 0),
            'comments': video.get('stats', {}).get('commentCount', 0),
            'shares': video.get('stats', {}).get('shareCount', 0),
            'author_username': author_username,
            'author_follower_count': video.get('author', {}).get('followerCount', 0),
            'create_time': create_time.strftime('%Y-%m-%d %H:%M:%S') if create_time else '',
            'hours_since_post': hours_since_post,
            'viral_speed': viral_speed,
            'video_url': video_url,
            'hashtags': ', '.join([tag.get('title', '') for tag in video.get('textExtra', []) if tag.get('hashtagName')]),
            'is_verified': video.get('author', {}).get('verified', False)
        }

class GoogleSheetsExporter:
    """Google Sheets出力クラス"""
    
    def __init__(self, credentials_path: str = "credentials.json"):
        self.credentials_path = credentials_path
        self.gc = None
        self._initialize()
    
    def _initialize(self):
        """Google Sheets API初期化"""
        if not GOOGLE_SHEETS_AVAILABLE:
            return
        
        try:
            if os.path.exists(self.credentials_path):
                scope = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                creds = Credentials.from_service_account_file(self.credentials_path, scopes=scope)
                self.gc = gspread.authorize(creds)
                logging.info("Google Sheets API初期化成功")
            else:
                logging.warning(f"認証ファイルが見つかりません: {self.credentials_path}")
        
        except Exception as e:
            logging.error(f"Google Sheets API初期化エラー: {e}")
    
    def export_to_sheets(self, viral_videos: List[Dict], spreadsheet_id: str = None, sheet_name: str = None) -> bool:
        """Google Sheetsに出力"""
        if not self.gc:
            logging.error("Google Sheets APIが初期化されていません")
            return False
        
        try:
            # スプレッドシート取得または作成
            if spreadsheet_id:
                spreadsheet = self.gc.open_by_key(spreadsheet_id)
            else:
                spreadsheet_name = f"TikTok Viral Videos {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                spreadsheet = self.gc.create(spreadsheet_name)
                logging.info(f"新しいスプレッドシートを作成: {spreadsheet_name}")
            
            # ワークシート取得または作成
            if not sheet_name:
                sheet_name = f"Viral_{datetime.now().strftime('%m%d_%H%M')}"
            
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                worksheet.clear()  # 既存データをクリア
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            
            # ヘッダー行
            headers = [
                '動画ID', '説明', '再生数', 'いいね数', 'コメント数', 'シェア数',
                'アカウント名', 'フォロワー数', '投稿日時', '経過時間(h)', 
                'バイラル速度', '動画URL', 'ハッシュタグ', '認証済み'
            ]
            
            # データ準備
            data = [headers]
            for video in viral_videos:
                row = [
                    video['video_id'],
                    video['description'],
                    video['views'],
                    video['likes'],
                    video['comments'],
                    video['shares'],
                    video['author_username'],
                    video['author_follower_count'],
                    video['create_time'],
                    video['hours_since_post'],
                    video['viral_speed'],
                    video['video_url'],
                    video['hashtags'],
                    '✓' if video['is_verified'] else ''
                ]
                data.append(row)
            
            # 一括更新
            worksheet.update('A1', data)
            
            # フォーマット設定
            self._format_worksheet(worksheet, len(viral_videos))
            
            logging.info(f"Google Sheetsに{len(viral_videos)}件のデータを出力しました")
            logging.info(f"スプレッドシートURL: {spreadsheet.url}")
            
            return True
            
        except Exception as e:
            logging.error(f"Google Sheets出力エラー: {e}")
            return False
    
    def _format_worksheet(self, worksheet, data_rows: int):
        """ワークシートのフォーマット設定"""
        try:
            # ヘッダー行のフォーマット
            worksheet.format('A1:N1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 1.0},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'horizontalAlignment': 'CENTER'
            })
            
            # 数値列のフォーマット
            if data_rows > 0:
                # 再生数、いいね数、コメント数、シェア数
                worksheet.format(f'C2:F{data_rows + 1}', {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}})
                
                # フォロワー数
                worksheet.format(f'H2:H{data_rows + 1}', {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}})
                
                # バイラル速度
                worksheet.format(f'K2:K{data_rows + 1}', {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}})
            
            # 列幅調整
            worksheet.columns_auto_resize(0, 13)
            
        except Exception as e:
            logging.warning(f"フォーマット設定エラー: {e}")

class TikTokViralMVP:
    """TikTok バイラル動画検出 MVP"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.tikapi = TikAPIClient(self.config['tikapi_key'])
        self.detector = ViralVideoDetector(
            min_views=self.config.get('min_views', 500000),
            time_limit_hours=self.config.get('time_limit_hours', 24)
        )
        self.sheets_exporter = GoogleSheetsExporter(self.config.get('credentials_path', 'credentials.json'))
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tiktok_viral_mvp.log'),
                logging.StreamHandler()
            ]
        )
    
    def _load_config(self, config_path: str) -> Dict:
        """設定ファイル読み込み"""
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"設定ファイル読み込みエラー: {e}")
        
        # デフォルト設定
        return {
            'tikapi_key': 'YOUR_TIKAPI_KEY_HERE',
            'min_views': 500000,
            'time_limit_hours': 24,
            'max_requests': 10,
            'countries': ['us', 'jp'],
            'spreadsheet_id': '',
            'credentials_path': 'credentials.json'
        }
    
    def create_sample_config(self):
        """サンプル設定ファイルを作成"""
        config = {
            "tikapi_key": "YOUR_TIKAPI_KEY_HERE",
            "min_views": 500000,
            "time_limit_hours": 24,
            "max_requests": 10,
            "countries": ["us", "jp"],
            "spreadsheet_id": "YOUR_SPREADSHEET_ID_HERE",
            "credentials_path": "credentials.json",
            "output_csv": True,
            "csv_filename": "viral_videos_{timestamp}.csv"
        }
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ サンプル設定ファイル config.json を作成しました")
        print("📝 TikAPIキーとGoogle Sheetsの設定を編集してください")
    
    async def collect_viral_videos(self) -> List[Dict]:
        """バイラル動画を収集"""
        all_viral_videos = []
        total_processed = 0
        
        logging.info("🚀 TikTok バイラル動画検出を開始します")
        logging.info(f"📊 条件: {self.config['time_limit_hours']}時間以内に{self.config['min_views']:,}再生以上")
        
        countries = self.config.get('countries', ['us'])
        max_requests = self.config.get('max_requests', 10)
        
        for country in countries:
            logging.info(f"🌍 {country.upper()} 地域の動画を検索中...")
            
            for request_num in range(max_requests):
                try:
                    # FYP動画を取得
                    fyp_response = self.tikapi.get_fyp_videos(count=30, country=country)
                    fyp_videos = fyp_response.get('itemList', [])
                    
                    # トレンド動画も取得（補完）
                    trending_response = self.tikapi.get_trending_videos(count=30, country=country)
                    trending_videos = trending_response.get('itemList', [])
                    
                    # 動画をマージ（重複除去）
                    all_videos = self._merge_videos(fyp_videos, trending_videos)
                    total_processed += len(all_videos)
                    
                    # バイラル動画をフィルタリング
                    viral_videos = []
                    for video in all_videos:
                        if self.detector.is_viral_video(video):
                            viral_info = self.detector.extract_video_info(video)
                            viral_videos.append(viral_info)
                    
                    all_viral_videos.extend(viral_videos)
                    
                    logging.info(f"📈 リクエスト {request_num + 1}/{max_requests}: "
                               f"{len(all_videos)}件処理, {len(viral_videos)}件バイラル検出")
                    
                    # 進捗表示
                    if viral_videos:
                        for video in viral_videos[:3]:  # 最初の3件を表示
                            logging.info(f"🔥 バイラル動画: {video['description'][:50]}... "
                                       f"({video['views']:,}再生, {video['hours_since_post']}h経過)")
                
                except Exception as e:
                    logging.error(f"データ収集エラー (リクエスト {request_num + 1}): {e}")
                    continue
        
        # 重複除去
        unique_viral_videos = self._remove_duplicates(all_viral_videos)
        
        logging.info(f"✅ 収集完了: {total_processed}件処理, {len(unique_viral_videos)}件のバイラル動画を検出")
        
        return unique_viral_videos
    
    def _merge_videos(self, fyp_videos: List[Dict], trending_videos: List[Dict]) -> List[Dict]:
        """動画リストをマージ（重複除去）"""
        seen_ids = set()
        merged_videos = []
        
        for video in fyp_videos + trending_videos:
            video_id = video.get('id')
            if video_id and video_id not in seen_ids:
                seen_ids.add(video_id)
                merged_videos.append(video)
        
        return merged_videos
    
    def _remove_duplicates(self, viral_videos: List[Dict]) -> List[Dict]:
        """バイラル動画の重複除去"""
        seen_ids = set()
        unique_videos = []
        
        for video in viral_videos:
            video_id = video.get('video_id')
            if video_id and video_id not in seen_ids:
                seen_ids.add(video_id)
                unique_videos.append(video)
        
        return unique_videos
    
    def export_to_csv(self, viral_videos: List[Dict]) -> str:
        """CSV出力"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"viral_videos_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                if not viral_videos:
                    csvfile.write("データなし\n")
                    return filename
                
                fieldnames = [
                    '動画ID', '説明', '再生数', 'いいね数', 'コメント数', 'シェア数',
                    'アカウント名', 'フォロワー数', '投稿日時', '経過時間(h)', 
                    'バイラル速度', '動画URL', 'ハッシュタグ', '認証済み'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for video in viral_videos:
                    writer.writerow({
                        '動画ID': video['video_id'],
                        '説明': video['description'],
                        '再生数': video['views'],
                        'いいね数': video['likes'],
                        'コメント数': video['comments'],
                        'シェア数': video['shares'],
                        'アカウント名': video['author_username'],
                        'フォロワー数': video['author_follower_count'],
                        '投稿日時': video['create_time'],
                        '経過時間(h)': video['hours_since_post'],
                        'バイラル速度': video['viral_speed'],
                        '動画URL': video['video_url'],
                        'ハッシュタグ': video['hashtags'],
                        '認証済み': '✓' if video['is_verified'] else ''
                    })
            
            logging.info(f"📄 CSV出力完了: {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"CSV出力エラー: {e}")
            return ""
    
    async def run(self):
        """メイン実行"""
        try:
            # バイラル動画収集
            viral_videos = await self.collect_viral_videos()
            
            if not viral_videos:
                logging.warning("⚠️ バイラル動画が見つかりませんでした")
                return
            
            # 結果表示
            logging.info(f"\n🎉 {len(viral_videos)}件のバイラル動画を検出しました！")
            logging.info("=" * 60)
            
            for i, video in enumerate(viral_videos[:5], 1):  # 上位5件表示
                logging.info(f"{i}. {video['description']}")
                logging.info(f"   👀 {video['views']:,}再生 | ⏰ {video['hours_since_post']}h経過 | 🚀 {video['viral_speed']:,}/h")
                logging.info(f"   🔗 {video['video_url']}")
                logging.info("")
            
            # CSV出力
            if self.config.get('output_csv', True):
                csv_file = self.export_to_csv(viral_videos)
                if csv_file:
                    logging.info(f"📄 CSVファイル: {csv_file}")
            
            # Google Sheets出力
            if GOOGLE_SHEETS_AVAILABLE and self.sheets_exporter.gc:
                spreadsheet_id = self.config.get('spreadsheet_id')
                success = self.sheets_exporter.export_to_sheets(viral_videos, spreadsheet_id)
                if success:
                    logging.info("📊 Google Sheetsに出力完了")
                else:
                    logging.warning("⚠️ Google Sheets出力に失敗しました")
            
            logging.info("✅ 処理完了")
            
        except Exception as e:
            logging.error(f"実行エラー: {e}")
            raise

def main():
    """メイン関数"""
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description='TikTok Viral Video Detector MVP')
    parser.add_argument('--create-config', action='store_true', help='サンプル設定ファイルを作成')
    parser.add_argument('--config', default='config.json', help='設定ファイルパス')
    
    args = parser.parse_args()
    
    if args.create_config:
        mvp = TikTokViralMVP()
        mvp.create_sample_config()
        return
    
    # 設定ファイルチェック
    if not os.path.exists(args.config):
        print(f"❌ 設定ファイルが見つかりません: {args.config}")
        print("💡 --create-config でサンプル設定ファイルを作成してください")
        sys.exit(1)
    
    # MVP実行
    mvp = TikTokViralMVP(args.config)
    
    # TikAPIキーチェック
    if mvp.config['tikapi_key'] == 'YOUR_TIKAPI_KEY_HERE':
        print("❌ TikAPIキーが設定されていません")
        print("📝 config.json でTikAPIキーを設定してください")
        sys.exit(1)
    
    # 実行
    try:
        asyncio.run(mvp.run())
    except KeyboardInterrupt:
        print("\n⏹️ 処理を中断しました")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

