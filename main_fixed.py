#!/usr/bin/env python3
"""
TikTok Viral Video Detector MVP - 修正版
TikAPIのJSONパースエラーを解決した改良版

主な修正点:
1. 認証ヘッダーの修正 (Authorization → X-API-KEY)
2. エラーハンドリングの強化
3. Content-Typeチェックの追加
4. デバッグ情報の詳細化
5. 複数エンドポイントの対応
"""

import json
import csv
import requests
import time
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import gspread
from google.oauth2.service_account import Credentials
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tikapi_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TikAPIClient:
    """TikAPI クライアント - 修正版"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://tikapi.io/api/v1"
        
        # 修正: 正しい認証ヘッダー
        self.headers = {
            'X-API-KEY': api_key,  # Authorization から X-API-KEY に変更
            'Content-Type': 'application/json',
            'User-Agent': 'TikTok-Viral-Detector-MVP/1.0'
        }
        
        # レート制限対応
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1秒間隔
        
        logger.info(f"TikAPIClient initialized with base_url: {self.base_url}")
    
    def _wait_for_rate_limit(self):
        """レート制限対応の待機"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        APIリクエストの実行 - 強化されたエラーハンドリング
        
        Args:
            endpoint: APIエンドポイント
            params: クエリパラメータ
            
        Returns:
            APIレスポンス（JSON）またはNone
        """
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        logger.info(f"Making request to: {url}")
        logger.debug(f"Headers: {self.headers}")
        logger.debug(f"Params: {params}")
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # ステータスコードチェック
            if response.status_code != 200:
                logger.error(f"HTTP Error {response.status_code}")
                logger.error(f"Response content: {response.text[:1000]}")
                return None
            
            # Content-Typeチェック
            content_type = response.headers.get('content-type', '').lower()
            logger.debug(f"Content-Type: {content_type}")
            
            if 'application/json' not in content_type:
                logger.error(f"Unexpected content type: {content_type}")
                logger.error(f"Expected: application/json")
                logger.error(f"Response content: {response.text[:1000]}")
                return None
            
            # JSONパース
            try:
                data = response.json()
                logger.debug(f"JSON parsed successfully")
                
                # TikAPIのレスポンス構造チェック
                if isinstance(data, dict):
                    if 'status' in data:
                        if data['status'] == 'error':
                            logger.error(f"API Error: {data.get('message', 'Unknown error')}")
                            return None
                        elif data['status'] == 'success':
                            logger.info("API request successful")
                            return data
                    
                    # statusフィールドがない場合でも、有効なJSONなら返す
                    logger.info("Valid JSON response received")
                    return data
                else:
                    logger.error(f"Unexpected response format: {type(data)}")
                    return None
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Response content: {response.text[:1000]}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            return None
    
    def get_trending_videos(self, count: int = 30, country: str = "us") -> List[Dict]:
        """
        トレンド動画の取得 - 複数エンドポイント対応
        
        Args:
            count: 取得件数
            country: 国コード
            
        Returns:
            動画データのリスト
        """
        params = {
            'count': min(count, 30),  # TikAPIの制限
            'country': country
        }
        
        # 複数のエンドポイントを試行
        endpoints = [
            'public/explore',
            'public/trending', 
            'public/feed'
        ]
        
        for endpoint in endpoints:
            logger.info(f"Trying endpoint: {endpoint}")
            
            data = self._make_request(endpoint, params)
            
            if data:
                # レスポンス構造の解析
                videos = self._extract_videos_from_response(data)
                if videos:
                    logger.info(f"Successfully retrieved {len(videos)} videos from {endpoint}")
                    return videos
                else:
                    logger.warning(f"No videos found in response from {endpoint}")
            else:
                logger.warning(f"Failed to get data from {endpoint}")
        
        logger.error("All endpoints failed")
        return []
    
    def _extract_videos_from_response(self, data: Dict) -> List[Dict]:
        """
        APIレスポンスから動画データを抽出
        
        Args:
            data: APIレスポンス
            
        Returns:
            動画データのリスト
        """
        videos = []
        
        try:
            # TikAPIの標準的なレスポンス構造
            if 'json' in data and 'itemList' in data['json']:
                videos = data['json']['itemList']
            elif 'itemList' in data:
                videos = data['itemList']
            elif 'data' in data and isinstance(data['data'], list):
                videos = data['data']
            elif isinstance(data, list):
                videos = data
            else:
                logger.warning(f"Unknown response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                
            logger.info(f"Extracted {len(videos)} videos from response")
            return videos
            
        except Exception as e:
            logger.error(f"Error extracting videos: {e}")
            return []

class ViralVideoDetector:
    """バイラル動画検出器 - 修正版"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.tikapi_client = TikAPIClient(config['tikapi_key'])
        self.min_views = config.get('min_views', 500000)
        self.time_limit_hours = config.get('time_limit_hours', 24)
        
        logger.info(f"ViralVideoDetector initialized")
        logger.info(f"Min views: {self.min_views:,}")
        logger.info(f"Time limit: {self.time_limit_hours} hours")
    
    def is_viral_video(self, video_data: Dict) -> bool:
        """
        動画がバイラル条件を満たすかチェック
        
        Args:
            video_data: 動画データ
            
        Returns:
            バイラル条件を満たすかどうか
        """
        try:
            # 投稿時刻の取得
            create_time = video_data.get('createTime')
            if not create_time:
                logger.debug("createTime not found in video data")
                return False
            
            # Unix timestampから datetime に変換
            if isinstance(create_time, str):
                create_time = int(create_time)
            
            post_time = datetime.fromtimestamp(create_time)
            current_time = datetime.now()
            time_diff = current_time - post_time
            
            # 24時間以内チェック
            if time_diff > timedelta(hours=self.time_limit_hours):
                logger.debug(f"Video too old: {time_diff}")
                return False
            
            # 再生数の取得
            stats = video_data.get('stats', {})
            play_count = stats.get('playCount', 0)
            
            if isinstance(play_count, str):
                play_count = int(play_count)
            
            # 50万再生以上チェック
            if play_count >= self.min_views:
                logger.info(f"Viral video found: {play_count:,} views in {time_diff}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking viral status: {e}")
            return False
    
    def collect_viral_videos(self, max_requests: int = 10) -> List[Dict]:
        """
        バイラル動画の収集
        
        Args:
            max_requests: 最大リクエスト数
            
        Returns:
            バイラル動画のリスト
        """
        viral_videos = []
        countries = self.config.get('countries', ['us', 'jp'])
        
        logger.info(f"Starting viral video collection")
        logger.info(f"Countries: {countries}")
        logger.info(f"Max requests: {max_requests}")
        
        request_count = 0
        
        for country in countries:
            if request_count >= max_requests:
                break
                
            logger.info(f"🌍 Collecting videos from {country.upper()}")
            
            videos = self.tikapi_client.get_trending_videos(count=30, country=country)
            request_count += 1
            
            if not videos:
                logger.warning(f"No videos retrieved for {country}")
                continue
            
            logger.info(f"📊 Processing {len(videos)} videos from {country}")
            
            for video in videos:
                if self.is_viral_video(video):
                    processed_video = self._process_video_data(video)
                    if processed_video:
                        viral_videos.append(processed_video)
                        logger.info(f"🔥 Viral video added: {processed_video['views']:,} views")
            
            # レート制限対応
            time.sleep(1)
        
        logger.info(f"✅ Collection complete: {len(viral_videos)} viral videos found")
        return viral_videos
    
    def _process_video_data(self, video_data: Dict) -> Optional[Dict]:
        """
        動画データの処理と正規化
        
        Args:
            video_data: 生の動画データ
            
        Returns:
            処理済み動画データ
        """
        try:
            # 基本情報の抽出
            video_id = video_data.get('id', '')
            desc = video_data.get('desc', '')
            create_time = video_data.get('createTime', 0)
            
            # 統計情報の抽出
            stats = video_data.get('stats', {})
            play_count = stats.get('playCount', 0)
            digg_count = stats.get('diggCount', 0)
            comment_count = stats.get('commentCount', 0)
            share_count = stats.get('shareCount', 0)
            
            # 作者情報の抽出
            author = video_data.get('author', {})
            author_name = author.get('uniqueId', '')
            author_nickname = author.get('nickname', '')
            follower_count = author.get('followerCount', 0)
            verified = author.get('verified', False)
            
            # ハッシュタグの抽出
            challenges = video_data.get('challenges', [])
            hashtags = ', '.join([challenge.get('title', '') for challenge in challenges])
            
            # 時間計算
            if isinstance(create_time, str):
                create_time = int(create_time)
            
            post_time = datetime.fromtimestamp(create_time)
            current_time = datetime.now()
            time_diff = current_time - post_time
            hours_elapsed = time_diff.total_seconds() / 3600
            
            # バイラル速度計算
            viral_speed = play_count / max(hours_elapsed, 1)
            
            # 動画URL生成
            video_url = f"https://www.tiktok.com/@{author_name}/video/{video_id}"
            
            return {
                'video_id': video_id,
                'description': desc,
                'views': play_count,
                'likes': digg_count,
                'comments': comment_count,
                'shares': share_count,
                'author_name': author_name,
                'author_nickname': author_nickname,
                'follower_count': follower_count,
                'post_time': post_time.strftime('%Y-%m-%d %H:%M:%S'),
                'hours_elapsed': round(hours_elapsed, 1),
                'viral_speed': round(viral_speed, 0),
                'video_url': video_url,
                'hashtags': hashtags,
                'verified': '✓' if verified else ''
            }
            
        except Exception as e:
            logger.error(f"Error processing video data: {e}")
            return None

class GoogleSheetsExporter:
    """Google Sheets エクスポーター"""
    
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        
        try:
            self._initialize_client()
            logger.info("Google Sheets client initialized")
        except Exception as e:
            logger.warning(f"Google Sheets initialization failed: {e}")
    
    def _initialize_client(self):
        """Google Sheets クライアントの初期化"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_file(
            self.credentials_path, scopes=scopes
        )
        self.client = gspread.authorize(credentials)
    
    def export_to_sheets(self, viral_videos: List[Dict]) -> bool:
        """
        バイラル動画データをGoogle Sheetsにエクスポート
        
        Args:
            viral_videos: バイラル動画のリスト
            
        Returns:
            エクスポート成功可否
        """
        if not self.client:
            logger.error("Google Sheets client not initialized")
            return False
        
        try:
            # スプレッドシートを開く
            sheet = self.client.open_by_key(self.spreadsheet_id)
            worksheet = sheet.sheet1
            
            # ヘッダー行
            headers = [
                '動画ID', '説明', '再生数', 'いいね数', 'コメント数', 'シェア数',
                'アカウント名', 'フォロワー数', '投稿日時', '経過時間(h)',
                'バイラル速度', '動画URL', 'ハッシュタグ', '認証済み'
            ]
            
            # データの準備
            data = [headers]
            for video in viral_videos:
                row = [
                    video['video_id'],
                    video['description'],
                    video['views'],
                    video['likes'],
                    video['comments'],
                    video['shares'],
                    video['author_name'],
                    video['follower_count'],
                    video['post_time'],
                    video['hours_elapsed'],
                    video['viral_speed'],
                    video['video_url'],
                    video['hashtags'],
                    video['verified']
                ]
                data.append(row)
            
            # シートをクリアして新しいデータを書き込み
            worksheet.clear()
            worksheet.update('A1', data)
            
            # フォーマット設定
            worksheet.format('A1:N1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 1.0},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })
            
            logger.info(f"Successfully exported {len(viral_videos)} videos to Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to Google Sheets: {e}")
            return False

def export_to_csv(viral_videos: List[Dict], filename: str) -> bool:
    """
    バイラル動画データをCSVファイルにエクスポート
    
    Args:
        viral_videos: バイラル動画のリスト
        filename: 出力ファイル名
        
    Returns:
        エクスポート成功可否
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            if not viral_videos:
                logger.warning("No viral videos to export")
                return False
            
            fieldnames = viral_videos[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # ヘッダー行を日本語に変換
            header_mapping = {
                'video_id': '動画ID',
                'description': '説明',
                'views': '再生数',
                'likes': 'いいね数',
                'comments': 'コメント数',
                'shares': 'シェア数',
                'author_name': 'アカウント名',
                'author_nickname': 'ニックネーム',
                'follower_count': 'フォロワー数',
                'post_time': '投稿日時',
                'hours_elapsed': '経過時間(h)',
                'viral_speed': 'バイラル速度',
                'video_url': '動画URL',
                'hashtags': 'ハッシュタグ',
                'verified': '認証済み'
            }
            
            # ヘッダー行の書き込み
            writer.writerow(header_mapping)
            
            # データ行の書き込み
            writer.writerows(viral_videos)
        
        logger.info(f"Successfully exported {len(viral_videos)} videos to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return False

def load_config(config_path: str = 'config.json') -> Dict:
    """設定ファイルの読み込み"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        return {}

def create_sample_config(config_path: str = 'config.json'):
    """サンプル設定ファイルの作成"""
    sample_config = {
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
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Sample configuration created: {config_path}")
        print("Please edit the configuration file with your API keys and settings.")
        return True
    except Exception as e:
        print(f"❌ Error creating configuration file: {e}")
        return False

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='TikTok Viral Video Detector MVP - Fixed Version')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--create-config', action='store_true', help='Create sample configuration file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.create_config:
        create_sample_config(args.config)
        return
    
    # 設定の読み込み
    config = load_config(args.config)
    if not config:
        print("❌ Failed to load configuration. Use --create-config to create a sample.")
        return
    
    # 必須設定のチェック
    if not config.get('tikapi_key') or config['tikapi_key'] == 'YOUR_TIKAPI_KEY_HERE':
        print("❌ Please set your TikAPI key in the configuration file.")
        return
    
    print("🚀 TikTok バイラル動画検出を開始します")
    print(f"📊 条件: {config.get('time_limit_hours', 24)}時間以内に{config.get('min_views', 500000):,}再生以上")
    
    # バイラル動画検出器の初期化
    detector = ViralVideoDetector(config)
    
    # バイラル動画の収集
    viral_videos = detector.collect_viral_videos(config.get('max_requests', 10))
    
    if not viral_videos:
        print("❌ バイラル動画が見つかりませんでした")
        return
    
    print(f"✅ {len(viral_videos)}件のバイラル動画を検出しました")
    
    # CSV出力
    if config.get('output_csv', True):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = config.get('csv_filename', 'viral_videos_{timestamp}.csv').format(timestamp=timestamp)
        
        if export_to_csv(viral_videos, csv_filename):
            print(f"📄 CSVファイル出力完了: {csv_filename}")
    
    # Google Sheets出力
    if config.get('spreadsheet_id') and config.get('credentials_path'):
        try:
            exporter = GoogleSheetsExporter(
                config['credentials_path'],
                config['spreadsheet_id']
            )
            
            if exporter.export_to_sheets(viral_videos):
                print("📊 Google Sheetsに出力完了")
            else:
                print("⚠️ Google Sheets出力に失敗しました")
                
        except Exception as e:
            print(f"⚠️ Google Sheets出力エラー: {e}")
    
    # 結果サマリー
    print("\n📈 検出結果サマリー:")
    for i, video in enumerate(viral_videos[:5], 1):
        print(f"{i}. {video['views']:,}再生 - {video['description'][:50]}...")
    
    if len(viral_videos) > 5:
        print(f"... 他 {len(viral_videos) - 5}件")

if __name__ == "__main__":
    main()

