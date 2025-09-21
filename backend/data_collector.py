import tweepy
import requests
import json
from datetime import datetime, timedelta
from models import db, SocialMediaPost
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterCollector:
    def __init__(self):
        self.bearer_token = Config.TWITTER_BEARER_TOKEN
        if not self.bearer_token:
            raise ValueError("Twitter Bearer Token not found in environment variables")
        
        # Initialize Twitter API v2 client
        self.client = tweepy.Client(bearer_token=self.bearer_token)
    
    def collect_political_tweets(self, max_results=100):
        """Collect tweets related to Botswana politics"""
        try:
            # Build search query for Botswana political content
            keywords = Config.POLITICAL_KEYWORDS[:5]  # Limit to avoid query length issues
            hashtags = Config.POLITICAL_HASHTAGS[:3]
            
            # Combine keywords and hashtags
            query_parts = []
            query_parts.extend([f'"{keyword}"' for keyword in keywords])
            query_parts.extend(hashtags)
            
            # Add location and language filters
            query = f"({' OR '.join(query_parts)}) lang:en OR lang:tn -is:retweet"
            
            logger.info(f"Searching Twitter with query: {query}")
            
            # Search for tweets
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang', 'geo'],
                user_fields=['username', 'public_metrics'],
                expansions=['author_id'],
                max_results=min(max_results, 100)  # API limit
            ).flatten(limit=max_results)
            
            collected_count = 0
            for tweet in tweets:
                try:
                    # Check if tweet already exists
                    existing = SocialMediaPost.query.filter_by(
                        platform='twitter',
                        post_id=str(tweet.id)
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Get author info
                    author_info = None
                    if hasattr(tweet, 'includes') and 'users' in tweet.includes:
                        author_info = tweet.includes['users'][0]
                    
                    # Create new post record
                    post = SocialMediaPost(
                        platform='twitter',
                        post_id=str(tweet.id),
                        text=tweet.text,
                        author=author_info.username if author_info else None,
                        author_followers=author_info.public_metrics['followers_count'] if author_info else None,
                        created_at=tweet.created_at,
                        likes=tweet.public_metrics.get('like_count', 0),
                        shares=tweet.public_metrics.get('retweet_count', 0),
                        comments=tweet.public_metrics.get('reply_count', 0),
                        raw_data=json.dumps(tweet.data)
                    )
                    
                    db.session.add(post)
                    collected_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing tweet {tweet.id}: {str(e)}")
                    continue
            
            db.session.commit()
            logger.info(f"Successfully collected {collected_count} new tweets")
            return collected_count
            
        except Exception as e:
            logger.error(f"Error collecting tweets: {str(e)}")
            db.session.rollback()
            return 0

class FacebookCollector:
    def __init__(self):
        self.access_token = Config.FACEBOOK_ACCESS_TOKEN
        if not self.access_token:
            logger.warning("Facebook Access Token not found - Facebook collection disabled")
            self.enabled = False
        else:
            self.enabled = True
    
    def collect_political_posts(self, max_results=50):
        """Collect posts from Botswana political Facebook pages"""
        if not self.enabled:
            logger.warning("Facebook collector not enabled - missing access token")
            return 0
        
        try:
            # List of Botswana political Facebook page IDs (you'll need to find these)
            political_pages = [
                # Add actual Facebook page IDs for:
                # - Botswana Democratic Party
                # - Umbrella for Democratic Change
                # - Botswana Congress Party
                # - Major political figures
                # - News outlets covering Botswana politics
            ]
            
            collected_count = 0
            
            for page_id in political_pages:
                try:
                    # Get posts from page
                    url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
                    params = {
                        'access_token': self.access_token,
                        'fields': 'id,message,created_time,likes.summary(true),shares,comments.summary(true)',
                        'limit': max_results // len(political_pages)
                    }
                    
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    for post_data in data.get('data', []):
                        try:
                            # Check if post already exists
                            existing = SocialMediaPost.query.filter_by(
                                platform='facebook',
                                post_id=post_data['id']
                            ).first()
                            
                            if existing:
                                continue
                            
                            # Create new post record
                            post = SocialMediaPost(
                                platform='facebook',
                                post_id=post_data['id'],
                                text=post_data.get('message', ''),
                                created_at=datetime.fromisoformat(post_data['created_time'].replace('Z', '+00:00')),
                                likes=post_data.get('likes', {}).get('summary', {}).get('total_count', 0),
                                shares=post_data.get('shares', {}).get('count', 0),
                                comments=post_data.get('comments', {}).get('summary', {}).get('total_count', 0),
                                raw_data=json.dumps(post_data)
                            )
                            
                            db.session.add(post)
                            collected_count += 1
                            
                        except Exception as e:
                            logger.error(f"Error processing Facebook post {post_data.get('id')}: {str(e)}")
                            continue
                
                except Exception as e:
                    logger.error(f"Error collecting from Facebook page {page_id}: {str(e)}")
                    continue
            
            db.session.commit()
            logger.info(f"Successfully collected {collected_count} new Facebook posts")
            return collected_count
            
        except Exception as e:
            logger.error(f"Error collecting Facebook posts: {str(e)}")
            db.session.rollback()
            return 0

def collect_all_data():
    """Main function to collect data from all sources"""
    logger.info("Starting data collection...")
    
    twitter_collector = TwitterCollector()
    facebook_collector = FacebookCollector()
    
    twitter_count = twitter_collector.collect_political_tweets()
    facebook_count = facebook_collector.collect_political_posts()
    
    total_collected = twitter_count + facebook_count
    logger.info(f"Data collection complete. Total new posts: {total_collected}")
    
    return {
        'twitter': twitter_count,
        'facebook': facebook_count,
        'total': total_collected
    }