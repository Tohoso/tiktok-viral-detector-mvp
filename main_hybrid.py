#!/usr/bin/env python3
"""
TikTok Viral Video Detector MVP - ハイブリッド版
設定に基づいてモックまたは実際のAPIを使用
"""

import json
import time
import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tiktok_viral_mvp_hybrid.log'),
        logging.StreamHandler()
    ]
)

# モックAPIクライアント
class MockTikAPIClient:
    """モックTikAPIクライアント"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
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
    
    def _generate_mock_video(self, video_id: str, is_viral: bool = False) -> dict:
        """モック動画データを生成"""
        import random
        now = datetime.now()
        
        if is_viral:
            # バイラル動画: 24時間以内、50万再生以上
            create_time = now - timedelta(hours=random.randint(1, 20))
            views = random.randint(500000, 2000000)
        else:
            # 通常動画: 24時間以内、50万再生未満
            create_time = now - timedelta(hours=random.randint(1, 24))
            views = random.randint(1000, 400000)
        
        return {
            "id": video_id,
            "desc": f"モック動画 {video_id} - {'バイラル' if is_viral else '通常'}動画",
            "createTime": int(create_time.timestamp()),
            "stats": {
                "playCount": views,
                "diggCount": random.randint(100, views // 10),
                "commentCount": random.randint(10, views // 100),
                "shareCount": random.randint(5, views // 200)
            },
            "author": {
                "uniqueId": f"user_{random.randint(1000, 9999)}",
                "followerCount": random.randint(1000, 100000),
                "verified": random.choice([True, False])
            },
            "video": {
                "playAddr": f"https://www.tiktok.com/@user/video/{video_id}"
            },
            "challenges": [
                {"title": f"#{random.choice(['dance', 'comedy', 'food', 'travel', 'fashion'])}"}
            ]
        }
    
    def get_fyp_videos(self, count: int = 30, country: str = "us") -> dict:
        """For You Page動画を取得（モック）"""
        self._wait_for_rate_limit()
        
        import random
        videos = []
        viral_count = random.randint(1, 5)  # 1-5件のバイラル動画
        
        for i in range(count):
            video_id = f"mock_{country}_{random.randint(1000000000, 9999999999)}"
            is_viral = i < viral_count
            videos.append(self._generate_mock_video(video_id, is_viral))
        
        return {
            "itemList": videos,
            "hasMore": True
        }
    
    def get_trending_videos(self, count: int = 30, country: str = "us") -> dict:
        """トレンド動画を取得（モック）"""
        self._wait_for_rate_limit()
        
        import random
        videos = []
        viral_count = random.randint(2, 8)  # 2-8件のバイラル動画
        
        for i in range(count):
            video_id = f"trend_{country}_{random.randint(1000000000, 9999999999)}"
            is_viral = i < viral_count
            videos.append(self._generate_mock_video(video_id, is_viral))
        
        return {
            "itemList": videos,
            "hasMore": True
        }

# 実際のTikAPIクライアント
class RealTikAPIClient:
    """実際のTikAPIクライアント"""
    
    def __init__(self, api_key: str):
        import requests
        self.api_key = api_key
        self.base_url = "https://tikapi.io/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        })
        
        # レート制限対応
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
        
        except Exception as e:
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
        
        except Exception as e:
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
                "動画ID": video.get("id", ""),
                "説明": video.get("desc", "")[:100],
                "再生数": views,
                "いいね数": video.get("stats", {}).get("diggCount", 0),
                "コメント数": video.get("stats", {}).get("commentCount", 0),
                "シェア数": video.get("stats", {}).get("shareCount", 0),
                "アカウント名": video.get("author", {}).get("uniqueId", ""),
                "フォロワー数": video.get("author", {}).get("followerCount", 0),
                "投稿日時": create_time.strftime("%Y-%m-%d %H:%M:%S") if create_time else "",
                "経過時間(h)": round(time_diff.total_seconds() / 3600, 1),
                "バイラル速度": int(viral_speed),
                "動画URL": f"https://www.tiktok.com/@{video.get('author', {}).get('uniqueId', '')}/video/{video.get('id', '')}",
                "ハッシュタグ": ", ".join([challenge.get("title", "") for challenge in video.get("challenges", [])]),
                "認証済み": "✓" if video.get("author", {}).get("verified", False) else ""
            }
            
        except Exception as e:
            logging.error(f"動画情報抽出エラー: {e}")
            return {}

class TikTokViralHybridMVP:
    """TikTokバイラル動画検出MVP（ハイブリッド版）"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        
        # 設定に基づいてAPIクライアントを選択
        if self.config.get("use_mock", True):
            logging.info("🧪 モックモードで実行します")
            self.tikapi_client = MockTikAPIClient(self.config.get("tikapi_key", "mock_key"))
        else:
            logging.info("🌐 実際のTikAPIで実行します")
            self.tikapi_client = RealTikAPIClient(self.config.get("tikapi_key", ""))
        
        self.detector = ViralVideoDetector(
            min_views=self.config.get("min_views", 500000),
            time_limit_hours=self.config.get("time_limit_hours", 24)
        )
    
    def _load_config(self, config_path: str) -> Dict:
        """設定ファイルを読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"設定ファイル読み込みエラー: {e}")
            return {}
    
    def collect_viral_videos(self) -> List[Dict]:
        """バイラル動画を収集"""
        viral_videos = []
        countries = self.config.get("countries", ["us", "jp"])
        max_requests = self.config.get("max_requests", 10)
        
        logging.info(f"🚀 TikTok バイラル動画検出を開始します")
        logging.info(f"📊 条件: {self.config.get('time_limit_hours', 24)}時間以内に{self.config.get('min_views', 500000):,}再生以上")
        
        for country in countries:
            logging.info(f"🌍 {country.upper()} 地域の動画を検索中...")
            
            for request_num in range(1, max_requests + 1):
                try:
                    # FYP動画取得
                    fyp_response = self.tikapi_client.get_fyp_videos(count=30, country=country)
                    fyp_videos = fyp_response.get("itemList", [])
                    
                    # トレンド動画取得
                    trending_response = self.tikapi_client.get_trending_videos(count=30, country=country)
                    trending_videos = trending_response.get("itemList", [])
                    
                    # 動画をマージ
                    all_videos = fyp_videos + trending_videos
                    
                    # バイラル動画を検出
                    request_viral_count = 0
                    for video in all_videos:
                        if self.detector.is_viral_video(video):
                            video_info = self.detector.extract_video_info(video)
                            if video_info:
                                viral_videos.append(video_info)
                                request_viral_count += 1
                    
                    logging.info(f"📈 リクエスト {request_num}/{max_requests}: {len(all_videos)}件処理, {request_viral_count}件バイラル検出")
                    
                    # バイラル動画の詳細ログ
                    for video in all_videos:
                        if self.detector.is_viral_video(video):
                            views = self.detector._extract_view_count(video)
                            create_time = self.detector._parse_create_time(video)
                            time_diff = datetime.now() - create_time if create_time else timedelta(0)
                            hours = time_diff.total_seconds() / 3600
                            logging.info(f"🔥 バイラル動画: {video.get('desc', '')[:50]}... ({views:,}再生, {hours:.1f}h経過)")
                    
                    # レート制限を考慮
                    time.sleep(1)
                    
                except Exception as e:
                    logging.error(f"リクエスト {request_num} エラー: {e}")
                    continue
        
        # 重複除去
        unique_videos = self._remove_duplicates(viral_videos)
        
        logging.info(f"✅ 収集完了: {len(unique_videos)}件のバイラル動画を検出")
        return unique_videos
    
    def _remove_duplicates(self, viral_videos: List[Dict]) -> List[Dict]:
        """重複動画を除去"""
        seen_ids = set()
        unique_videos = []
        
        for video in viral_videos:
            video_id = video.get("動画ID", "")
            if video_id and video_id not in seen_ids:
                seen_ids.add(video_id)
                unique_videos.append(video)
        
        return unique_videos
    
    def export_to_csv(self, viral_videos: List[Dict]) -> str:
        """CSVファイルに出力"""
        if not self.config.get("output_csv", True):
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.config.get("csv_filename", "viral_videos_{timestamp}.csv").format(timestamp=timestamp)
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if viral_videos:
                    fieldnames = viral_videos[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(viral_videos)
            
            logging.info(f"📄 CSVファイル: {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"CSV出力エラー: {e}")
            return ""
    
    def run(self):
        """メイン実行"""
        try:
            # バイラル動画収集
            viral_videos = self.collect_viral_videos()
            
            if not viral_videos:
                logging.info("❌ バイラル動画が見つかりませんでした")
                return
            
            logging.info(f"🎉 {len(viral_videos)}件のバイラル動画を検出しました！")
            
            # CSV出力
            csv_filename = self.export_to_csv(viral_videos)
            if csv_filename:
                logging.info(f"📄 CSVファイル: {csv_filename}")
            
            logging.info("✅ 処理完了")
            
        except Exception as e:
            logging.error(f"実行エラー: {e}")

def main():
    """メイン関数"""
    mvp = TikTokViralHybridMVP()
    mvp.run()

if __name__ == "__main__":
    main() 