#!/usr/bin/env python3
"""
Web Scraping Data Collector for Botswana Political Content
Focuses on public sources and specific hashtags without requiring Facebook API
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import random
from urllib.parse import quote_plus, urljoin
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotswanaWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Botswana political hashtags and keywords
        self.political_hashtags = [
            '#BotswanaPolitics', '#BDP2024', '#UDC2024', '#BotswanaElections',
            '#Masisi', '#Boko', '#BotswanaNews', '#BWPolitics', '#Gaborone',
            '#BotswanaGovernment', '#BotswanaParliament', '#BotswanaVotes'
        ]
        
        self.political_keywords = [
            'Botswana politics', 'BDP', 'UDC', 'BCP', 'AP', 'Masisi', 'Boko',
            'Saleshando', 'Botswana election', 'Botswana government', 'Parliament Botswana',
            'mmuso', 'polotiki', 'kgethololo', 'palamente', 'setšhaba'
        ]
        
        # Public news sources (no API required)
        self.news_sources = [
            {
                'name': 'Mmegi Online',
                'base_url': 'https://www.mmegi.bw',
                'search_path': '/search?q={}',
                'selectors': {
                    'articles': 'article, .article-item, .news-item',
                    'title': 'h1, h2, h3, .title, .headline',
                    'content': '.content, .article-body, p',
                    'date': '.date, .published, time'
                }
            },
            {
                'name': 'The Voice Botswana',
                'base_url': 'https://www.thevoicebw.com',
                'search_path': '/search?q={}',
                'selectors': {
                    'articles': 'article, .post, .news-item',
                    'title': 'h1, h2, .entry-title, .post-title',
                    'content': '.entry-content, .post-content, p',
                    'date': '.date, .post-date, time'
                }
            },
            {
                'name': 'Botswana Guardian',
                'base_url': 'https://www.botswanaguardian.co.bw',
                'search_path': '/search?q={}',
                'selectors': {
                    'articles': 'article, .article, .post',
                    'title': 'h1, h2, .title',
                    'content': '.content, .article-content, p',
                    'date': '.date, .published'
                }
            }
        ]
    
    def scrape_twitter_hashtag_public(self, hashtag: str, max_results: int = 20) -> List[Dict]:
        """
        Scrape Twitter hashtag data using public search (no API required)
        Note: This is for educational purposes - respect Twitter's terms of service
        """
        collected_posts = []
        
        try:
            # Use Twitter's public search (limited but accessible)
            search_url = f"https://twitter.com/search?q={quote_plus(hashtag)}&src=typed_query&f=live"
            
            logger.info(f"Searching Twitter for hashtag: {hashtag}")
            
            # Note: Twitter's public scraping is limited and may require additional tools
            # For production, recommend using Twitter API v2 (free tier available)
            
            # Mock data for demonstration - replace with actual scraping logic
            for i in range(min(max_results, 10)):
                mock_post = {
                    'platform': 'twitter_public',
                    'post_id': f'twitter_mock_{hashtag}_{i}',
                    'text': f'Mock tweet about {hashtag} - Botswana political discussion {i+1}',
                    'author': f'user_{i+1}',
                    'created_at': (datetime.now() - timedelta(hours=i)).isoformat(),
                    'likes': random.randint(1, 50),
                    'shares': random.randint(0, 20),
                    'comments': random.randint(0, 15),
                    'hashtags': [hashtag],
                    'source': 'twitter_public_scrape'
                }
                collected_posts.append(mock_post)
                
            logger.info(f"Collected {len(collected_posts)} posts for {hashtag}")
            
        except Exception as e:
            logger.error(f"Error scraping Twitter hashtag {hashtag}: {e}")
        
        return collected_posts
    
    def scrape_news_source(self, source: Dict, keyword: str, max_articles: int = 10) -> List[Dict]:
        """Scrape news articles from Botswana news websites"""
        collected_articles = []
        
        try:
            search_url = source['base_url'] + source['search_path'].format(quote_plus(keyword))
            
            logger.info(f"Scraping {source['name']} for keyword: {keyword}")
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find articles using the source's selectors
            articles = soup.select(source['selectors']['articles'])[:max_articles]
            
            for i, article in enumerate(articles):
                try:
                    # Extract title
                    title_elem = article.select_one(source['selectors']['title'])
                    title = title_elem.get_text(strip=True) if title_elem else f"Article {i+1}"
                    
                    # Extract content
                    content_elems = article.select(source['selectors']['content'])
                    content = ' '.join([elem.get_text(strip=True) for elem in content_elems[:3]])  # First 3 paragraphs
                    
                    # Extract date
                    date_elem = article.select_one(source['selectors']['date'])
                    date_text = date_elem.get_text(strip=True) if date_elem else ''
                    
                    # Clean and validate content
                    if len(content) < 50:  # Skip very short content
                        continue
                    
                    article_data = {
                        'platform': 'news_website',
                        'post_id': f"{source['name'].lower().replace(' ', '_')}_{i}_{int(time.time())}",
                        'text': f"{title}. {content}",
                        'title': title,
                        'content': content,
                        'author': source['name'],
                        'created_at': self._parse_date(date_text),
                        'likes': 0,
                        'shares': 0,
                        'comments': 0,
                        'source': source['name'],
                        'url': search_url,
                        'keyword': keyword
                    }
                    
                    collected_articles.append(article_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing article from {source['name']}: {e}")
                    continue
            
            logger.info(f"Collected {len(collected_articles)} articles from {source['name']}")
            
        except Exception as e:
            logger.error(f"Error scraping {source['name']}: {e}")
        
        return collected_articles
    
    def scrape_reddit_botswana(self, max_posts: int = 15) -> List[Dict]:
        """Scrape Reddit r/Botswana for political discussions"""
        collected_posts = []
        
        try:
            # Reddit public JSON API (no authentication required for public posts)
            reddit_url = "https://www.reddit.com/r/Botswana.json"
            
            logger.info("Scraping Reddit r/Botswana")
            
            response = self.session.get(reddit_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for post_data in data['data']['children'][:max_posts]:
                post = post_data['data']
                
                # Filter for political content
                title = post.get('title', '').lower()
                selftext = post.get('selftext', '').lower()
                
                # Check if post contains political keywords
                is_political = any(
                    keyword.lower() in title or keyword.lower() in selftext
                    for keyword in self.political_keywords
                )
                
                if is_political:
                    reddit_post = {
                        'platform': 'reddit',
                        'post_id': f"reddit_{post['id']}",
                        'text': f"{post['title']}. {post.get('selftext', '')}",
                        'title': post['title'],
                        'author': f"u/{post['author']}",
                        'created_at': datetime.fromtimestamp(post['created_utc']).isoformat(),
                        'likes': post.get('ups', 0),
                        'shares': 0,
                        'comments': post.get('num_comments', 0),
                        'subreddit': 'r/Botswana',
                        'url': f"https://reddit.com{post['permalink']}",
                        'source': 'reddit_public'
                    }
                    
                    collected_posts.append(reddit_post)
            
            logger.info(f"Collected {len(collected_posts)} political posts from Reddit")
            
        except Exception as e:
            logger.error(f"Error scraping Reddit: {e}")
        
        return collected_posts
    
    def scrape_youtube_comments(self, search_term: str, max_comments: int = 20) -> List[Dict]:
        """
        Scrape YouTube comments from Botswana political videos
        Note: This is a simplified version - for production, use YouTube Data API
        """
        collected_comments = []
        
        try:
            # Mock YouTube comments for demonstration
            # In production, you'd use YouTube Data API or specialized scraping tools
            
            logger.info(f"Collecting YouTube comments for: {search_term}")
            
            for i in range(max_comments):
                mock_comment = {
                    'platform': 'youtube',
                    'post_id': f'youtube_comment_{search_term}_{i}',
                    'text': f'Mock YouTube comment about {search_term} in Botswana politics',
                    'author': f'YouTubeUser{i+1}',
                    'created_at': (datetime.now() - timedelta(hours=i*2)).isoformat(),
                    'likes': random.randint(0, 25),
                    'shares': 0,
                    'comments': 0,
                    'video_title': f'Botswana Political Discussion: {search_term}',
                    'source': 'youtube_comments'
                }
                collected_comments.append(mock_comment)
            
            logger.info(f"Collected {len(collected_comments)} YouTube comments")
            
        except Exception as e:
            logger.error(f"Error collecting YouTube comments: {e}")
        
        return collected_comments
    
    def _parse_date(self, date_text: str) -> str:
        """Parse various date formats to ISO format"""
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%B %d, %Y', '%d %B %Y']:
                try:
                    return datetime.strptime(date_text, fmt).isoformat()
                except ValueError:
                    continue
            
            # If parsing fails, return current time
            return datetime.now().isoformat()
            
        except Exception:
            return datetime.now().isoformat()
    
    def collect_all_data(self, max_per_source: int = 10) -> Dict[str, List[Dict]]:
        """Collect data from all available sources"""
        all_data = {
            'twitter_hashtags': [],
            'news_articles': [],
            'reddit_posts': [],
            'youtube_comments': []
        }
        
        logger.info("Starting comprehensive data collection...")
        
        # 1. Collect Twitter hashtag data
        for hashtag in self.political_hashtags[:3]:  # Limit to avoid rate limits
            posts = self.scrape_twitter_hashtag_public(hashtag, max_per_source)
            all_data['twitter_hashtags'].extend(posts)
            time.sleep(2)  # Rate limiting
        
        # 2. Collect news articles
        for keyword in self.political_keywords[:3]:  # Limit keywords
            for source in self.news_sources:
                articles = self.scrape_news_source(source, keyword, max_per_source//3)
                all_data['news_articles'].extend(articles)
                time.sleep(1)  # Rate limiting
        
        # 3. Collect Reddit posts
        reddit_posts = self.scrape_reddit_botswana(max_per_source)
        all_data['reddit_posts'].extend(reddit_posts)
        
        # 4. Collect YouTube comments
        for keyword in ['Botswana politics', 'BDP', 'UDC']:
            comments = self.scrape_youtube_comments(keyword, max_per_source//3)
            all_data['youtube_comments'].extend(comments)
        
        # Summary
        total_collected = sum(len(posts) for posts in all_data.values())
        logger.info(f"Data collection complete! Total items: {total_collected}")
        
        for source, posts in all_data.items():
            logger.info(f"  {source}: {len(posts)} items")
        
        return all_data
    
    def save_collected_data(self, data: Dict[str, List[Dict]], filename: Optional[str] = None) -> str:
        """Save collected data to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/collected_data_{timestamp}.json'
        
        try:
            import os
            os.makedirs('data', exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Data saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return ""

# Global scraper instance
web_scraper = BotswanaWebScraper()

def collect_web_data():
    """Main function to collect data from web sources"""
    logger.info("Starting web-based data collection for Botswana political content")
    
    try:
        # Collect data from all sources
        collected_data = web_scraper.collect_all_data(max_per_source=15)
        
        # Save to file
        filename = web_scraper.save_collected_data(collected_data)
        
        # Return summary
        total_items = sum(len(posts) for posts in collected_data.values())
        
        return {
            'success': True,
            'total_collected': total_items,
            'sources': {source: len(posts) for source, posts in collected_data.items()},
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in web data collection: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Test the scraper
    result = collect_web_data()
    print(json.dumps(result, indent=2))