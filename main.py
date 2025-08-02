#!/usr/bin/env python3
"""
TikTok Viral Video Detector MVP - DB保存版
日本語動画に絞って24時間で50万再生以上の動画を取得し、DBに保存
"""

import json
import time
import csv
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import requests

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tiktok_viral_mvp_db.log'),
        logging.StreamHandler()
    ]
)

class TikAPIClient:
    """TikAPIクライアント v2.0"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tikapi.io"
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        })
        self.last_request_time = 0
        self.min_request_interval = 1.0
    
    def _wait_for_rate_limit(self):
        """レート制限を考慮した待機"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def verify_api_key(self) -> bool:
        """APIキーの有効性を検証"""
        try:
            logging.info("🔑 APIキーの有効性を検証中...")
            logging.info("Testing endpoint: public/explore")
            
            url = f"{self.base_url}/public/explore"
            params = {"count": 5, "country": "jp"}
            
            response = self.session.get(url, params=params, timeout=30)
            logging.info(f"Status: {response.status_code}")
            logging.info(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                data = response.json()
                logging.info("✅ JSON parse successful")
                logging.info("✅ APIキーが有効です")
                return True
            else:
                logging.error(f"❌ APIキーが無効: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ APIキー検証エラー: {e}")
            return False
    
    def get_videos(self, count: int = 30, country: str = "jp") -> Dict:
        """動画を取得"""
        self._wait_for_rate_limit()
        
        try:
            logging.info(f"Trying endpoint: public/explore")
            logging.info(f"Making request to: {self.base_url}/public/explore")
            
            url = f"{self.base_url}/public/explore"
            params = {"count": count, "country": country}
            
            response = self.session.get(url, params=params, timeout=30)
            logging.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get('itemList', [])
                logging.info(f"API request successful")
                logging.info(f"Extracted {len(videos)} videos from response")
                logging.info(f"Successfully retrieved {len(videos)} videos from public/explore")
                return {"itemList": videos, "hasMore": True}
            else:
                logging.error(f"API request failed: {response.status_code}")
                return {"itemList": [], "hasMore": False}
                
        except Exception as e:
            logging.error(f"API request error: {e}")
            return {"itemList": [], "hasMore": False}

class ViralVideoDetector:
    """バイラル動画検出器 v2.0"""
    
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
            
            # 時間制限チェック
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
            if 'createTime' in video:
                timestamp = video['createTime']
                if isinstance(timestamp, str):
                    timestamp = int(timestamp)
                return datetime.fromtimestamp(timestamp)
            
            if 'create_time' in video:
                return datetime.fromtimestamp(video['create_time'])
            
            return None
            
        except (ValueError, TypeError) as e:
            logging.warning(f"時刻解析エラー: {e}")
            return None
    
    def _extract_view_count(self, video: Dict) -> int:
        """再生数を抽出"""
        try:
            if 'stats' in video and 'playCount' in video['stats']:
                return int(video['stats']['playCount'])
            
            if 'playCount' in video:
                return int(video['playCount'])
            
            if 'view_count' in video:
                return int(video['view_count'])
            
            return 0
            
        except (ValueError, TypeError):
            return 0
    
    def extract_video_info(self, video: Dict) -> Dict:
        """動画情報を抽出"""
        try:
            create_time = self._parse_create_time(video)
            time_diff = datetime.now() - create_time if create_time else timedelta(0)
            
            views = self._extract_view_count(video)
            viral_speed = views / (time_diff.total_seconds() / 3600) if time_diff.total_seconds() > 0 else 0
            
            return {
                "video_id": video.get("id", ""),
                "description": video.get("desc", "")[:200],
                "views": views,
                "likes": video.get("stats", {}).get("diggCount", 0),
                "comments": video.get("stats", {}).get("commentCount", 0),
                "shares": video.get("stats", {}).get("shareCount", 0),
                "author_username": video.get("author", {}).get("uniqueId", ""),
                "author_nickname": video.get("author", {}).get("nickname", ""),
                "follower_count": video.get("author", {}).get("followerCount", 0),
                "create_time": create_time.strftime("%Y-%m-%d %H:%M:%S") if create_time else "",
                "hours_since_post": round(time_diff.total_seconds() / 3600, 1),
                "viral_speed": int(viral_speed),
                "video_url": f"https://www.tiktok.com/@{video.get('author', {}).get('uniqueId', '')}/video/{video.get('id', '')}",
                "hashtags": ", ".join([challenge.get("title", "") for challenge in video.get("challenges", [])]),
                "verified": video.get("author", {}).get("verified", False),
                "country": "jp",
                "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logging.error(f"動画情報抽出エラー: {e}")
            return {}

class DatabaseManager:
    """データベース管理クラス"""
    
    def __init__(self, db_path: str = "tiktok_viral_videos.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベースを初期化"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # バイラル動画テーブルを作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS viral_videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT UNIQUE,
                    description TEXT,
                    views INTEGER,
                    likes INTEGER,
                    comments INTEGER,
                    shares INTEGER,
                    author_username TEXT,
                    author_nickname TEXT,
                    follower_count INTEGER,
                    create_time TEXT,
                    hours_since_post REAL,
                    viral_speed INTEGER,
                    video_url TEXT,
                    hashtags TEXT,
                    verified BOOLEAN,
                    country TEXT,
                    collected_at TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 全動画テーブルを作成（バイラルでない動画も保存）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS all_videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT UNIQUE,
                    description TEXT,
                    views INTEGER,
                    likes INTEGER,
                    comments INTEGER,
                    shares INTEGER,
                    author_username TEXT,
                    author_nickname TEXT,
                    follower_count INTEGER,
                    create_time TEXT,
                    hours_since_post REAL,
                    viral_speed INTEGER,
                    video_url TEXT,
                    hashtags TEXT,
                    verified BOOLEAN,
                    country TEXT,
                    collected_at TEXT,
                    is_viral BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logging.info(f"✅ データベース初期化完了: {self.db_path}")
            
        except Exception as e:
            logging.error(f"データベース初期化エラー: {e}")
    
    def save_video(self, video_info: Dict, is_viral: bool = False):
        """動画情報をデータベースに保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 全動画テーブルに保存
            cursor.execute('''
                INSERT OR REPLACE INTO all_videos (
                    video_id, description, views, likes, comments, shares,
                    author_username, author_nickname, follower_count, create_time,
                    hours_since_post, viral_speed, video_url, hashtags, verified,
                    country, collected_at, is_viral
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_info.get('video_id'), video_info.get('description'),
                video_info.get('views'), video_info.get('likes'),
                video_info.get('comments'), video_info.get('shares'),
                video_info.get('author_username'), video_info.get('author_nickname'),
                video_info.get('follower_count'), video_info.get('create_time'),
                video_info.get('hours_since_post'), video_info.get('viral_speed'),
                video_info.get('video_url'), video_info.get('hashtags'),
                video_info.get('verified'), video_info.get('country'),
                video_info.get('collected_at'), is_viral
            ))
            
            # バイラル動画の場合、バイラル動画テーブルにも保存
            if is_viral:
                cursor.execute('''
                    INSERT OR REPLACE INTO viral_videos (
                        video_id, description, views, likes, comments, shares,
                        author_username, author_nickname, follower_count, create_time,
                        hours_since_post, viral_speed, video_url, hashtags, verified,
                        country, collected_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    video_info.get('video_id'), video_info.get('description'),
                    video_info.get('views'), video_info.get('likes'),
                    video_info.get('comments'), video_info.get('shares'),
                    video_info.get('author_username'), video_info.get('author_nickname'),
                    video_info.get('follower_count'), video_info.get('create_time'),
                    video_info.get('hours_since_post'), video_info.get('viral_speed'),
                    video_info.get('video_url'), video_info.get('hashtags'),
                    video_info.get('verified'), video_info.get('country'),
                    video_info.get('collected_at')
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"データベース保存エラー: {e}")
    
    def get_viral_videos(self) -> List[Dict]:
        """バイラル動画を取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM viral_videos 
                ORDER BY collected_at DESC
            ''')
            
            columns = [description[0] for description in cursor.description]
            videos = []
            
            for row in cursor.fetchall():
                video = dict(zip(columns, row))
                videos.append(video)
            
            conn.close()
            return videos
            
        except Exception as e:
            logging.error(f"バイラル動画取得エラー: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """データベース統計を取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 全動画数
            cursor.execute('SELECT COUNT(*) FROM all_videos')
            total_videos = cursor.fetchone()[0]
            
            # バイラル動画数
            cursor.execute('SELECT COUNT(*) FROM viral_videos')
            viral_videos = cursor.fetchone()[0]
            
            # 最新の収集日時
            cursor.execute('SELECT MAX(collected_at) FROM all_videos')
            latest_collection = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_videos": total_videos,
                "viral_videos": viral_videos,
                "latest_collection": latest_collection
            }
            
        except Exception as e:
            logging.error(f"統計取得エラー: {e}")
            return {}

class TikTokViralDBMVP:
    """TikTokバイラル動画検出MVP（DB保存版）"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.tikapi_client = TikAPIClient(self.config.get("tikapi_key", ""))
        self.detector = ViralVideoDetector(
            min_views=self.config.get("min_views", 500000),
            time_limit_hours=self.config.get("time_limit_hours", 24)
        )
        self.db_manager = DatabaseManager()
    
    def _load_config(self, config_path: str) -> Dict:
        """設定ファイルを読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"設定ファイル読み込みエラー: {e}")
            return {}
    
    def collect_and_save_videos(self) -> List[Dict]:
        """動画を収集してDBに保存"""
        all_viral_videos = []
        max_requests = self.config.get("max_requests", 10)
        
        logging.info(f"🚀 日本語動画収集開始 (24時間で50万再生以上)")
        logging.info(f"📊 最大リクエスト数: {max_requests}")
        
        for request_num in range(1, max_requests + 1):
            try:
                logging.info(f"🌍 リクエスト {request_num}/{max_requests} - 日本語動画を収集中...")
                
                # 動画を取得
                response = self.tikapi_client.get_videos(count=30, country="jp")
                videos = response.get("itemList", [])
                
                if not videos:
                    logging.warning(f"リクエスト {request_num}: 動画が取得できませんでした")
                    continue
                
                logging.info(f"📊 リクエスト {request_num}: {len(videos)}件の動画を取得")
                
                # 各動画を処理
                request_viral_count = 0
                for video in videos:
                    # 動画情報を抽出
                    video_info = self.detector.extract_video_info(video)
                    if not video_info:
                        continue
                    
                    # バイラル判定
                    is_viral = self.detector.is_viral_video(video)
                    
                    # DBに保存
                    self.db_manager.save_video(video_info, is_viral)
                    
                    if is_viral:
                        all_viral_videos.append(video_info)
                        request_viral_count += 1
                        
                        # バイラル動画の詳細ログ
                        views = video_info.get('views', 0)
                        hours = video_info.get('hours_since_post', 0)
                        desc = video_info.get('description', '')[:50]
                        logging.info(f"🔥 バイラル動画: {desc}... ({views:,}再生, {hours}h経過)")
                
                logging.info(f"📈 リクエスト {request_num}: {request_viral_count}件のバイラル動画を検出")
                
                # レート制限を考慮
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"リクエスト {request_num} エラー: {e}")
                continue
        
        logging.info(f"✅ 収集完了: 合計 {len(all_viral_videos)}件のバイラル動画を検出")
        return all_viral_videos
    
    def export_to_csv(self, viral_videos: List[Dict]) -> str:
        """CSVファイルに出力"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"viral_videos_db_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if viral_videos:
                    fieldnames = viral_videos[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(viral_videos)
            
            logging.info(f"📄 CSVファイル出力完了: {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"CSV出力エラー: {e}")
            return ""
    
    def run(self):
        """メイン実行"""
        try:
            # APIキー検証
            if not self.tikapi_client.verify_api_key():
                logging.error("❌ APIキーの検証に失敗しました")
                return
            
            logging.info("✅ セットアップ検証完了")
            
            # 動画収集とDB保存
            viral_videos = self.collect_and_save_videos()
            
            if not viral_videos:
                logging.info("❌ バイラル動画が見つかりませんでした")
                return
            
            logging.info(f"🎉 {len(viral_videos)}件のバイラル動画を検出しました！")
            
            # CSV出力
            csv_filename = self.export_to_csv(viral_videos)
            
            # 統計情報を表示
            stats = self.db_manager.get_stats()
            logging.info(f"📊 データベース統計:")
            logging.info(f"   全動画数: {stats.get('total_videos', 0)}件")
            logging.info(f"   バイラル動画数: {stats.get('viral_videos', 0)}件")
            logging.info(f"   最新収集: {stats.get('latest_collection', 'N/A')}")
            
            logging.info("✅ 処理完了")
            
        except Exception as e:
            logging.error(f"実行エラー: {e}")

def main():
    """メイン関数"""
    mvp = TikTokViralDBMVP()
    mvp.run()

if __name__ == "__main__":
    main() 