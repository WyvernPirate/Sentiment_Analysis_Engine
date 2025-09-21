#!/usr/bin/env python3
"""
Simple Data Collector for Botswana Political Content
Focuses on accessible public sources without complex APIs
"""

import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict
import time
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleDataCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Focus on specific Botswana political hashtags
        self.target_hashtags = [
            '#BotswanaPolitics', '#BDP2024', '#UDC2024', '#Masisi', '#Boko',
            '#BotswanaElections', '#BWPolitics', '#BotswanaGovernment'
        ]
        
        # Botswana political keywords in English and Setswana
        self.keywords = [
            'Botswana politics', 'BDP', 'UDC', 'BCP', 'Masisi', 'Boko',
            'mmuso', 'polotiki', 'kgethololo', 'setšhaba', 'palamente'
        ]
    
    def collect_reddit_botswana_politics(self) -> List[Dict]:
        """Collect political posts from r/Botswana (public JSON API)"""
        posts = []
        
        try:
            logger.info("Collecting from Reddit r/Botswana...")
            
            # Reddit public API - no authentication needed
            url = "https://www.reddit.com/r/Botswana.json?limit=25"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data['data']['children']:
                post = item['data']
                
                # Check if post is political
                title = post.get('title', '').lower()
                selftext = post.get('selftext', '').lower()
                
                is_political = any(
                    keyword.lower() in title or keyword.lower() in selftext
                    for keyword in self.keywords
                )
                
                if is_political and len(post.get('title', '')) > 10:
                    post_data = {
                        'platform': 'reddit',
                        'post_id': f"reddit_{post['id']}",
                        'text': f"{post['title']}. {post.get('selftext', '')}".strip(),
                        'author': f"u/{post.get('author', 'unknown')}",
                        'created_at': datetime.fromtimestamp(post['created_utc']).isoformat(),
                        'likes': post.get('ups', 0),
                        'shares': 0,
                        'comments': post.get('num_comments', 0),
                        'source': 'reddit_r_botswana',
                        'url': f"https://reddit.com{post.get('permalink', '')}"
                    }
                    posts.append(post_data)
            
            logger.info(f"Collected {len(posts)} political posts from Reddit")
            
        except Exception as e:
            logger.error(f"Error collecting from Reddit: {e}")
        
        return posts
    
    def generate_mock_social_media_data(self) -> List[Dict]:
        """Generate realistic mock social media data for testing"""
        mock_posts = []
        
        # Realistic Botswana political posts in English and Setswana
        sample_posts = [
            "BDP's new economic policy looks promising for Botswana's future #BDP2024",
            "Ke dumela gore UDC e tla fetola Botswana #UDC2024 #Change",
            "Masisi's leadership has brought stability to our nation",
            "Boko o bua nnete ka mathata a rona a ikonomi #UDC",
            "The government needs to do more for youth employment #BotswanaYouth",
            "Mmuso o tshwanetse go thusa babereki ba ba latlhegileng #Jobs",
            "Great to see progress in Gaborone infrastructure development",
            "Palamente e tshwanetse go sekaseka molao o mosha #Parliament",
            "BCP brings fresh ideas to Botswana politics #BCP2024",
            "Setšhaba se batla diphetogo tse di siameng #BotswanaFirst",
            "The education system needs urgent reform in Botswana",
            "Baithuti ba batla thuso ya mmuso go ithuta #Education",
            "Healthcare improvements are needed across the country",
            "Boitekanelo jwa setšhaba bo botlhokwa thata #Health",
            "Mining revenue should benefit all Batswana equally",
            "Merafo e tshwanetse go thusa setšhaba sotlhe #Mining"
        ]
        
        platforms = ['twitter', 'facebook', 'instagram']
        
        for i, text in enumerate(sample_posts):
            platform = random.choice(platforms)
            
            # Add some Setswana-English code-switching
            if random.random() > 0.7:
                if 'government' in text.lower():
                    text = text.replace('government', 'mmuso')
                elif 'people' in text.lower():
                    text = text.replace('people', 'batho')
            
            post = {
                'platform': platform,
                'post_id': f"{platform}_mock_{i+1}",
                'text': text,
                'author': f"user_{i+1}",
                'created_at': (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                'likes': random.randint(5, 150),
                'shares': random.randint(0, 50),
                'comments': random.randint(0, 30),
                'source': 'mock_data_generator',
                'hashtags': re.findall(r'#\w+', text)
            }
            
            mock_posts.append(post)
        
        logger.info(f"Generated {len(mock_posts)} mock social media posts")
        return mock_posts
    
    def collect_news_headlines(self) -> List[Dict]:
        """Collect news headlines from public RSS feeds (if available)"""
        headlines = []
        
        try:
            # Mock news headlines for now - in production, you'd use RSS feeds
            mock_headlines = [
                "President Masisi announces new economic recovery plan",
                "UDC leader Boko criticizes government's handling of unemployment",
                "Parliament debates new mining legislation",
                "BCP calls for education reform in rural areas",
                "Gaborone residents protest water shortages",
                "Botswana's GDP shows signs of recovery",
                "Opposition parties unite on healthcare issues",
                "Traditional leaders meet with government officials",
                "Youth unemployment remains a key challenge",
                "New infrastructure projects announced for northern regions"
            ]
            
            for i, headline in enumerate(mock_headlines):
                news_item = {
                    'platform': 'news_website',
                    'post_id': f"news_{i+1}",
                    'text': headline,
                    'author': 'Botswana News',
                    'created_at': (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                    'likes': 0,
                    'shares': random.randint(5, 25),
                    'comments': random.randint(0, 15),
                    'source': 'news_aggregator'
                }
                headlines.append(news_item)
            
            logger.info(f"Collected {len(headlines)} news headlines")
            
        except Exception as e:
            logger.error(f"Error collecting news headlines: {e}")
        
        return headlines
    
    def collect_all_simple_data(self) -> Dict:
        """Collect data from all simple sources"""
        logger.info("Starting simple data collection...")
        
        all_data = []
        
        # 1. Reddit posts (real data)
        reddit_posts = self.collect_reddit_botswana_politics()
        all_data.extend(reddit_posts)
        
        # 2. Mock social media data (for testing)
        mock_posts = self.generate_mock_social_media_data()
        all_data.extend(mock_posts)
        
        # 3. News headlines
        news_headlines = self.collect_news_headlines()
        all_data.extend(news_headlines)
        
        logger.info(f"Total collected: {len(all_data)} items")
        
        return {
            'success': True,
            'total_collected': len(all_data),
            'data': all_data,
            'sources': {
                'reddit': len(reddit_posts),
                'mock_social_media': len(mock_posts),
                'news': len(news_headlines)
            },
            'timestamp': datetime.now().isoformat()
        }

# Global simple collector
simple_collector = SimpleDataCollector()

def collect_simple_data():
    """Main function for simple data collection"""
    return simple_collector.collect_all_simple_data()