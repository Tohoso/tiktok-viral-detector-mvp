#!/usr/bin/env python3
"""
TikTok Viral Video Detector MVP - v2.0 修正版
ベースURL修正とAPIキー検証機能を追加

主な修正点:
1. ベースURL修正: tikapi.io/api/v1 → api.tikapi.io
2. APIキー検証機能の追加
3. 403エラーの適切な処理
4. 起動時のAPI接続確認
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
        logging.FileHandler('tikapi_debug_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TikAPIClient:
    """TikAPI クライアント - v2.0 修正版"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # 修正: 正しいベースURL
        self.base_url = "https://api.tikapi.io"
        
        self.headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'TikTok-Viral-Detector-MVP/2.0'
        }
        
        # レート制限対応
        self.last_request_time = 0
        self.min_request_interval = 1.0
        
        logger.info(f"TikAPIClient v2.0 initialized")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"API Key: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else api_key}")
    
    def verify_api_key(self) -> bool:
        """
        APIキーの有効性を検証
        
        Returns:
            APIキーが有効かどうか
        """
        logger.info("🔑 APIキーの有効性を検証中...")
        
        # exploreエンドポイントで直接テスト
        endpoint = "public/explore"
        logger.info(f"Testing endpoint: {endpoint}")
        
        try:
            url = f"{self.base_url}/{endpoint}"
            params = {"count": 1, "country": "us"}
            
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params,
                timeout=10
            )
            
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("✅ JSON parse successful")
                    
                    # TikAPIの正常なレスポンス構造をチェック
                    if isinstance(data, dict):
                        if data.get('status') == 'success' or 'itemList' in data:
                            logger.info("✅ APIキーが有効です")
                            return True
                        elif data.get('status') == 'error':
                            logger.error(f"❌ API Error: {data.get('message', 'Unknown error')}")
                            return False
                        else:
                            # statusフィールドがなくても、itemListがあれば有効
                            if 'itemList' in data or 'data' in data:
                                logger.info("✅ APIキーが有効です (データ取得成功)")
                                return True
                            else:
                                logger.warning(f"Unexpected response structure: {list(data.keys())}")
                                return False
                    else:
                        logger.error(f"Unexpected response type: {type(data)}")
                        return False
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    return False
                    
            elif response.status_code == 403:
                try:
                    error_data = response.json()
                    logger.error(f"❌ APIキーが無効 (403): {error_data.get('message', 'Forbidden')}")
                except json.JSONDecodeError:
                    logger.error("❌ APIキーが無効: 403 Forbidden")
                return False
                
            elif response.status_code == 401:
                logger.error("❌ APIキーが無効: 401 Unauthorized")
                return False
            else:
                logger.error(f"❌ HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    logger.error(f"Error details: {error_data}")
                except:
                    logger.error(f"Response: {response.text[:500]}")
                return False
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error: {e}")
            return False
        
        logger.error("❌ APIキーの検証に失敗しました")
        return False
    
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
        APIリクエストの実行 - v2.0 強化版
        
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
            
            # ステータスコード別処理
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                        logger.debug("JSON parsed successfully")
                        
                        # TikAPIのレスポンス構造チェック
                        if isinstance(data, dict):
                            if data.get('status') == 'error':
                                logger.error(f"API Error: {data.get('message', 'Unknown error')}")
                                return None
                            elif data.get('status') == 'success' or 'data' in data:
                                logger.info("API request successful")
                                return data
                        
                        logger.info("Valid JSON response received")
                        return data
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        logger.error(f"Response content: {response.text[:1000]}")
                        return None
                else:
                    logger.error(f"Unexpected content type: {content_type}")
                    logger.error(f"Response content: {response.text[:1000]}")
                    return None
                    
            elif response.status_code == 403:
                try:
                    error_data = response.json()
                    logger.error(f"API Key Invalid (403): {error_data.get('message', 'Forbidden')}")
                except json.JSONDecodeError:
                    logger.error("API Key Invalid (403): Forbidden")
                return None
                
            elif response.status_code == 401:
                logger.error("API Key Invalid (401): Unauthorized")
                return None
                
            elif response.status_code == 429:
                logger.error("Rate limit exceeded (429)")
                return None
                
            else:
                logger.error(f"HTTP Error {response.status_code}")
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
        トレンド動画の取得 - v2.0版
        
        Args:
            count: 取得件数
            country: 国コード
            
        Returns:
            動画データのリスト
        """
        params = {
            'count': min(count, 30),
            'country': country
        }
        
        # v2.0: 修正されたエンドポイント
        endpoints = [
            'public/explore',
            'public/trending'
        ]
        
        for endpoint in endpoints:
            logger.info(f"Trying endpoint: {endpoint}")
            
            data = self._make_request(endpoint, params)
            
            if data:
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
        APIレスポンスから動画データを抽出 - v2.0版
        
        Args:
            data: APIレスポンス
            
        Returns:
            動画データのリスト
        """
        videos = []
        
        try:
            # TikAPI v2.0のレスポンス構造に対応
            if 'data' in data and isinstance(data['data'], list):
                videos = data['data']
            elif 'json' in data and 'itemList' in data['json']:
                videos = data['json']['itemList']
            elif 'itemList' in data:
                videos = data['itemList']
            elif 'items' in data:
                videos = data['items']
            elif isinstance(data, list):
                videos = data
            else:
                logger.warning(f"Unknown response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                logger.debug(f"Response sample: {str(data)[:500]}")
                
            logger.info(f"Extracted {len(videos)} videos from response")
            return videos
            
        except Exception as e:
            logger.error(f"Error extracting videos: {e}")
            return []

class ViralVideoDetector:
    """バイラル動画検出器 - v2.0版"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.tikapi_client = TikAPIClient(config['tikapi_key'])
        self.min_views = config.get('min_views', 500000)
        self.time_limit_hours = config.get('time_limit_hours', 24)
        
        logger.info(f"ViralVideoDetector v2.0 initialized")
        logger.info(f"Min views: {self.min_views:,}")
        logger.info(f"Time limit: {self.time_limit_hours} hours")
    
    def verify_setup(self) -> bool:
        """
        セットアップの検証
        
        Returns:
            セットアップが正常かどうか
        """
        logger.info("🔍 セットアップを検証中...")
        
        # APIキーの検証
        if not self.tikapi_client.verify_api_key():
            logger.error("❌ APIキーの検証に失敗しました")
            return False
        
        logger.info("✅ セットアップ検証完了")
        return True
    
    def is_viral_video(self, video_data: Dict) -> bool:
        """
        動画がバイラル条件を満たすかチェック - v2.0版
        
        Args:
            video_data: 動画データ
            
        Returns:
            バイラル条件を満たすかどうか
        """
        try:
            # 投稿時刻の取得（複数フィールドに対応）
            create_time = video_data.get('createTime') or video_data.get('create_time') or video_data.get('created_at')
            
            if not create_time:
                logger.debug("createTime not found in video data")
                return False
            
            # Unix timestampから datetime に変換
            if isinstance(create_time, str):
                try:
                    create_time = int(create_time)
                except ValueError:
                    logger.debug(f"Invalid createTime format: {create_time}")
                    return False
            
            post_time = datetime.fromtimestamp(create_time)
            current_time = datetime.now()
            time_diff = current_time - post_time
            
            # 24時間以内チェック
            if time_diff > timedelta(hours=self.time_limit_hours):
                logger.debug(f"Video too old: {time_diff}")
                return False
            
            # 再生数の取得（複数フィールドに対応）
            stats = video_data.get('stats', {})
            play_count = (
                stats.get('playCount') or 
                stats.get('play_count') or 
                stats.get('views') or 
                video_data.get('views') or 
                video_data.get('play_count') or 
                0
            )
            
            if isinstance(play_count, str):
                try:
                    play_count = int(play_count)
                except ValueError:
                    logger.debug(f"Invalid play_count format: {play_count}")
                    return False
            
            # 50万再生以上チェック
            if play_count >= self.min_views:
                logger.info(f"🔥 Viral video found: {play_count:,} views in {time_diff}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking viral status: {e}")
            return False
    
    def collect_viral_videos(self, max_requests: int = 10) -> List[Dict]:
        """
        バイラル動画の収集 - v2.0版
        
        Args:
            max_requests: 最大リクエスト数
            
        Returns:
            バイラル動画のリスト
        """
        viral_videos = []
        countries = self.config.get('countries', ['us', 'jp'])
        
        logger.info(f"🚀 バイラル動画収集開始 (v2.0)")
        logger.info(f"🌍 対象国: {countries}")
        logger.info(f"📊 最大リクエスト数: {max_requests}")
        
        request_count = 0
        
        for country in countries:
            if request_count >= max_requests:
                break
                
            logger.info(f"🌍 {country.upper()} 地域の動画を収集中...")
            
            videos = self.tikapi_client.get_trending_videos(count=30, country=country)
            request_count += 1
            
            if not videos:
                logger.warning(f"⚠️ {country} からの動画取得に失敗")
                continue
            
            logger.info(f"📊 {country} から {len(videos)} 件の動画を取得")
            
            viral_count_before = len(viral_videos)
            
            for video in videos:
                if self.is_viral_video(video):
                    processed_video = self._process_video_data(video)
                    if processed_video:
                        viral_videos.append(processed_video)
            
            viral_count_after = len(viral_videos)
            new_viral_count = viral_count_after - viral_count_before
            
            logger.info(f"🔥 {country} で {new_viral_count} 件のバイラル動画を発見")
            
            # レート制限対応
            time.sleep(1)
        
        logger.info(f"✅ 収集完了: 合計 {len(viral_videos)} 件のバイラル動画を検出")
        return viral_videos
    
    def _process_video_data(self, video_data: Dict) -> Optional[Dict]:
        """
        動画データの処理と正規化 - v2.0版
        
        Args:
            video_data: 生の動画データ
            
        Returns:
            処理済み動画データ
        """
        try:
            # 基本情報の抽出（複数フィールドに対応）
            video_id = video_data.get('id') or video_data.get('video_id') or ''
            desc = video_data.get('desc') or video_data.get('description') or video_data.get('title') or ''
            create_time = video_data.get('createTime') or video_data.get('create_time') or video_data.get('created_at') or 0
            
            # 統計情報の抽出
            stats = video_data.get('stats', {})
            play_count = stats.get('playCount') or stats.get('play_count') or stats.get('views') or video_data.get('views') or 0
            digg_count = stats.get('diggCount') or stats.get('digg_count') or stats.get('likes') or video_data.get('likes') or 0
            comment_count = stats.get('commentCount') or stats.get('comment_count') or stats.get('comments') or video_data.get('comments') or 0
            share_count = stats.get('shareCount') or stats.get('share_count') or stats.get('shares') or video_data.get('shares') or 0
            
            # 作者情報の抽出
            author = video_data.get('author', {})
            author_name = author.get('uniqueId') or author.get('username') or author.get('unique_id') or ''
            author_nickname = author.get('nickname') or author.get('display_name') or author.get('name') or ''
            follower_count = author.get('followerCount') or author.get('follower_count') or author.get('followers') or 0
            verified = author.get('verified', False)
            
            # ハッシュタグの抽出
            challenges = video_data.get('challenges', []) or video_data.get('hashtags', [])
            if isinstance(challenges, list):
                hashtags = ', '.join([
                    challenge.get('title', '') if isinstance(challenge, dict) else str(challenge) 
                    for challenge in challenges
                ])
            else:
                hashtags = str(challenges)
            
            # 時間計算
            if isinstance(create_time, str):
                try:
                    create_time = int(create_time)
                except ValueError:
                    create_time = 0
            
            if create_time > 0:
                post_time = datetime.fromtimestamp(create_time)
                current_time = datetime.now()
                time_diff = current_time - post_time
                hours_elapsed = time_diff.total_seconds() / 3600
            else:
                post_time = datetime.now()
                hours_elapsed = 0
            
            # バイラル速度計算
            viral_speed = int(play_count) / max(hours_elapsed, 1) if hours_elapsed > 0 else int(play_count)
            
            # 動画URL生成
            if author_name and video_id:
                video_url = f"https://www.tiktok.com/@{author_name}/video/{video_id}"
            else:
                video_url = f"https://www.tiktok.com/video/{video_id}" if video_id else ""
            
            return {
                'video_id': video_id,
                'description': desc[:100] + '...' if len(desc) > 100 else desc,
                'views': int(play_count) if play_count else 0,
                'likes': int(digg_count) if digg_count else 0,
                'comments': int(comment_count) if comment_count else 0,
                'shares': int(share_count) if share_count else 0,
                'author_name': author_name,
                'author_nickname': author_nickname,
                'follower_count': int(follower_count) if follower_count else 0,
                'post_time': post_time.strftime('%Y-%m-%d %H:%M:%S'),
                'hours_elapsed': round(hours_elapsed, 1),
                'viral_speed': round(viral_speed, 0),
                'video_url': video_url,
                'hashtags': hashtags,
                'verified': '✓' if verified else ''
            }
            
        except Exception as e:
            logger.error(f"Error processing video data: {e}")
            logger.debug(f"Video data: {video_data}")
            return None

class GoogleSheetsExporter:
    """Google Sheets エクスポーター - v2.0版"""
    
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
                'アカウント名', 'ニックネーム', 'フォロワー数', '投稿日時', '経過時間(h)',
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
                    video['author_nickname'],
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
            worksheet.format('A1:O1', {
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
    """サンプル設定ファイルの作成 - v2.0版"""
    sample_config = {
        "tikapi_key": "YOUR_TIKAPI_KEY_HERE",
        "min_views": 500000,
        "time_limit_hours": 24,
        "max_requests": 10,
        "countries": ["us", "jp"],
        "spreadsheet_id": "YOUR_SPREADSHEET_ID_HERE",
        "credentials_path": "credentials.json",
        "output_csv": True,
        "csv_filename": "viral_videos_{timestamp}.csv",
        "_comments": {
            "tikapi_key": "TikAPI.io から取得したAPIキー",
            "min_views": "バイラル判定の最小再生数",
            "time_limit_hours": "投稿からの時間制限（時間）",
            "max_requests": "最大API リクエスト数",
            "countries": "検索対象国（us, jp, uk, ca など）",
            "base_url_note": "v2.0では api.tikapi.io を使用"
        }
    }
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Sample configuration created: {config_path}")
        print("📝 Please edit the configuration file with your API keys and settings.")
        print("🔑 Get your TikAPI key from: https://tikapi.io/")
        return True
    except Exception as e:
        print(f"❌ Error creating configuration file: {e}")
        return False

def main():
    """メイン実行関数 - v2.0版"""
    parser = argparse.ArgumentParser(description='TikTok Viral Video Detector MVP v2.0')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--create-config', action='store_true', help='Create sample configuration file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--verify-only', action='store_true', help='Only verify API key and exit')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.create_config:
        create_sample_config(args.config)
        return
    
    print("🚀 TikTok バイラル動画検出器 v2.0")
    print("=" * 50)
    
    # 設定の読み込み
    config = load_config(args.config)
    if not config:
        print("❌ 設定ファイルの読み込みに失敗しました")
        print("💡 --create-config でサンプル設定を作成してください")
        return
    
    # 必須設定のチェック
    if not config.get('tikapi_key') or config['tikapi_key'] == 'YOUR_TIKAPI_KEY_HERE':
        print("❌ TikAPIキーが設定されていません")
        print("🔑 config.json でAPIキーを設定してください")
        print("📝 APIキー取得: https://tikapi.io/")
        return
    
    # バイラル動画検出器の初期化
    detector = ViralVideoDetector(config)
    
    # セットアップ検証
    if not detector.verify_setup():
        print("❌ セットアップ検証に失敗しました")
        print("🔍 APIキーとネットワーク接続を確認してください")
        return
    
    if args.verify_only:
        print("✅ APIキー検証完了 - 正常に動作します")
        return
    
    print(f"📊 検索条件: {config.get('time_limit_hours', 24)}時間以内に{config.get('min_views', 500000):,}再生以上")
    print(f"🌍 対象地域: {', '.join(config.get('countries', ['us', 'jp']))}")
    
    # バイラル動画の収集
    viral_videos = detector.collect_viral_videos(config.get('max_requests', 10))
    
    if not viral_videos:
        print("❌ バイラル動画が見つかりませんでした")
        print("💡 検索条件を調整するか、時間をおいて再実行してください")
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
        print(f"{i}. {video['views']:,}再生 ({video['hours_elapsed']}h) - {video['description']}")
    
    if len(viral_videos) > 5:
        print(f"... 他 {len(viral_videos) - 5}件")
    
    print(f"\n🎯 平均バイラル速度: {sum(v['viral_speed'] for v in viral_videos) / len(viral_videos):,.0f} 再生/時間")

if __name__ == "__main__":
    main()

