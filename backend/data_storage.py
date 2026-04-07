#!/usr/bin/env python3
"""
Simple Data Storage for Collected Social Media Data
Stores data in memory and JSON files for the simple app
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from simple_data_collector import collect_simple_data
from sentiment_analyzer import analyzer

class SimpleDataStorage:
    def __init__(self):
        self.data_file = 'data/collected_posts.json'
        self.analyzed_data_file = 'data/analyzed_posts.json'
        self.ensure_data_directory()
        self._cached_data = None
        self._last_collection = None
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs('data', exist_ok=True)
    
    def collect_and_store_data(self, force_refresh: bool = False) -> Dict:
        """Collect new data and store it"""
        try:
            # Check if we need to refresh (every 30 minutes)
            if not force_refresh and self._last_collection:
                time_diff = datetime.now() - self._last_collection
                if time_diff.total_seconds() < 1800:  # 30 minutes
                    return {"message": "Using cached data", "cached": True}
            
            print("🔄 Collecting fresh data...")
            
            # Collect data from web sources
            result = collect_simple_data()
            
            if result['success']:
                # Add timestamps and IDs
                for i, post in enumerate(result['data']):
                    post['id'] = i + 1
                    post['collected_at'] = datetime.now().isoformat()
                
                # Save raw data
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(result['data'], f, ensure_ascii=False, indent=2)
                
                # Analyze sentiment for each post
                analyzed_posts = []
                for post in result['data']:
                    try:
                        # Analyze sentiment
                        sentiment_result = analyzer.analyze_sentiment(post['text'])
                        
                        if sentiment_result:
                            post['sentiment_analysis'] = sentiment_result
                        else:
                            # Fallback basic analysis
                            post['sentiment_analysis'] = {
                                'sentiment': 'neutral',
                                'confidence': 0.5,
                                'detected_language': 'English',
                                'code_switching_detected': False
                            }
                        
                        analyzed_posts.append(post)
                        
                    except Exception as e:
                        print(f"Error analyzing post {post.get('id', 'unknown')}: {e}")
                        # Add post without analysis
                        post['sentiment_analysis'] = {
                            'sentiment': 'neutral',
                            'confidence': 0.5,
                            'detected_language': 'English',
                            'code_switching_detected': False
                        }
                        analyzed_posts.append(post)
                
                # Save analyzed data
                with open(self.analyzed_data_file, 'w', encoding='utf-8') as f:
                    json.dump(analyzed_posts, f, ensure_ascii=False, indent=2)
                
                # Cache in memory
                self._cached_data = analyzed_posts
                self._last_collection = datetime.now()
                
                print(f"✅ Collected and analyzed {len(analyzed_posts)} posts")
                
                return {
                    "success": True,
                    "total_collected": len(analyzed_posts),
                    "analyzed": len([p for p in analyzed_posts if 'sentiment_analysis' in p]),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": "Data collection failed"}
                
        except Exception as e:
            print(f"Error in collect_and_store_data: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stored_data(self) -> List[Dict]:
        """Get stored analyzed data"""
        try:
            # Try to load from cache first
            if self._cached_data:
                return self._cached_data
            
            # Load from file
            if os.path.exists(self.analyzed_data_file):
                with open(self.analyzed_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._cached_data = data
                    return data

            # No stored data yet - return quickly and let explicit refresh endpoints collect.
            return []
            
        except Exception as e:
            print(f"Error loading stored data: {e}")
            return []
    
    def get_dashboard_overview(self, days: int = 7) -> Dict:
        """Get overview statistics from real data"""
        posts = self.get_stored_data()
        
        if not posts:
            # Return empty stats if no data
            return {
                'total_posts': 0,
                'sentiment_breakdown': {'positive': 0, 'negative': 0, 'neutral': 0},
                'language_breakdown': {},
                'platform_breakdown': {},
                'code_switching_posts': 0,
                'code_switching_percentage': 0
            }
        
        # Filter posts by date range
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_posts = []
        
        for post in posts:
            try:
                post_date = datetime.fromisoformat(post.get('created_at', post.get('collected_at', datetime.now().isoformat())))
                if post_date >= cutoff_date:
                    recent_posts.append(post)
            except:
                # Include posts with invalid dates
                recent_posts.append(post)
        
        # Calculate statistics
        total_posts = len(recent_posts)
        
        # Sentiment breakdown
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for post in recent_posts:
            sentiment = post.get('sentiment_analysis', {}).get('sentiment', 'neutral')
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
        
        # Language breakdown
        language_counts = {}
        code_switching_count = 0
        for post in recent_posts:
            analysis = post.get('sentiment_analysis', {})
            language = analysis.get('detected_language', 'English')
            language_counts[language] = language_counts.get(language, 0) + 1
            
            if analysis.get('code_switching_detected', False):
                code_switching_count += 1
        
        # Platform breakdown
        platform_counts = {}
        for post in recent_posts:
            platform = post.get('platform', 'unknown')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        return {
            'total_posts': total_posts,
            'sentiment_breakdown': sentiment_counts,
            'language_breakdown': language_counts,
            'platform_breakdown': platform_counts,
            'code_switching_posts': code_switching_count,
            'code_switching_percentage': (code_switching_count / total_posts * 100) if total_posts > 0 else 0
        }
    
    def get_sentiment_trends(self, days: int = 7) -> List[Dict]:
        """Get sentiment trends from real data"""
        posts = self.get_stored_data()
        
        if not posts:
            return []
        
        # Group posts by date
        date_sentiments = {}
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for post in posts:
            try:
                post_date = datetime.fromisoformat(post.get('created_at', post.get('collected_at', datetime.now().isoformat())))
                if post_date >= cutoff_date:
                    date_key = post_date.date().isoformat()
                    
                    if date_key not in date_sentiments:
                        date_sentiments[date_key] = {'positive': 0, 'negative': 0, 'neutral': 0}
                    
                    sentiment = post.get('sentiment_analysis', {}).get('sentiment', 'neutral')
                    if sentiment in date_sentiments[date_key]:
                        date_sentiments[date_key][sentiment] += 1
            except:
                continue
        
        # Convert to trend format
        trends = []
        for date_str in sorted(date_sentiments.keys()):
            sentiments = date_sentiments[date_str]
            total = sum(sentiments.values())
            
            if total > 0:
                trends.append({
                    'period': date_str,
                    'sentiments': sentiments,
                    'total': total,
                    'percentages': {
                        sentiment: (count / total * 100) for sentiment, count in sentiments.items()
                    }
                })
        
        return trends
    
    def get_political_entities(self, days: int = 7) -> List[Dict]:
        """Get political entity sentiment from real data"""
        posts = self.get_stored_data()
        
        if not posts:
            return []
        
        # Track entity mentions
        entity_sentiments = {}
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for post in posts:
            try:
                post_date = datetime.fromisoformat(post.get('created_at', post.get('collected_at', datetime.now().isoformat())))
                if post_date >= cutoff_date:
                    analysis = post.get('sentiment_analysis', {})
                    sentiment = analysis.get('sentiment', 'neutral')
                    
                    # Check for political entities in text
                    text = post.get('text', '').lower()
                    entities_found = []
                    
                    # Check for parties
                    if 'bdp' in text:
                        entities_found.append(('BDP', 'party'))
                    if 'udc' in text:
                        entities_found.append(('UDC', 'party'))
                    if 'bcp' in text:
                        entities_found.append(('BCP', 'party'))
                    
                    # Check for leaders
                    if 'masisi' in text:
                        entities_found.append(('Masisi', 'leader'))
                    if 'boko' in text:
                        entities_found.append(('Boko', 'leader'))
                    
                    # Update entity sentiment counts
                    for entity, entity_type in entities_found:
                        if entity not in entity_sentiments:
                            entity_sentiments[entity] = {
                                'type': entity_type,
                                'sentiments': {'positive': 0, 'negative': 0, 'neutral': 0}
                            }
                        
                        if sentiment in entity_sentiments[entity]['sentiments']:
                            entity_sentiments[entity]['sentiments'][sentiment] += 1
            except:
                continue
        
        # Convert to entity format
        entities = []
        for entity, data in entity_sentiments.items():
            sentiments = data['sentiments']
            total = sum(sentiments.values())
            
            if total > 0:
                entities.append({
                    'entity': entity,
                    'type': data['type'],
                    'sentiments': sentiments,
                    'total': total,
                    'percentages': {
                        sentiment: (count / total * 100) for sentiment, count in sentiments.items()
                    }
                })
        
        # Sort by total mentions
        entities.sort(key=lambda x: x['total'], reverse=True)
        return entities
    
    def get_advanced_analytics(self, days: int = 7) -> Dict:
        """Get advanced analytics for political insights"""
        posts = self.get_stored_data()
        
        if not posts:
            return {}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_posts = []
        
        for post in posts:
            try:
                post_date = datetime.fromisoformat(post.get('created_at', post.get('collected_at', datetime.now().isoformat())))
                if post_date >= cutoff_date:
                    recent_posts.append(post)
            except:
                recent_posts.append(post)
        
        # Sentiment momentum (trend direction)
        sentiment_momentum = self._calculate_sentiment_momentum(recent_posts)
        
        # Top keywords and hashtags
        keywords_analysis = self._analyze_keywords(recent_posts)
        
        # Engagement analysis
        engagement_analysis = self._analyze_engagement(recent_posts)
        
        # Language usage patterns
        language_patterns = self._analyze_language_patterns(recent_posts)
        
        # Political party comparison
        party_comparison = self._compare_political_parties(recent_posts)
        
        # Sentiment confidence analysis
        confidence_analysis = self._analyze_confidence_levels(recent_posts)
        
        return {
            'sentiment_momentum': sentiment_momentum,
            'keywords_analysis': keywords_analysis,
            'engagement_analysis': engagement_analysis,
            'language_patterns': language_patterns,
            'party_comparison': party_comparison,
            'confidence_analysis': confidence_analysis,
            'total_posts_analyzed': len(recent_posts),
            'analysis_period': f"{days} days"
        }
    
    def _calculate_sentiment_momentum(self, posts: List[Dict]) -> Dict:
        """Calculate sentiment momentum (trending up/down)"""
        if len(posts) < 2:
            return {'trend': 'insufficient_data', 'change': 0}
        
        # Sort posts by date
        sorted_posts = sorted(posts, key=lambda x: x.get('created_at', x.get('collected_at', '')))
        
        # Split into first and second half
        mid_point = len(sorted_posts) // 2
        first_half = sorted_posts[:mid_point]
        second_half = sorted_posts[mid_point:]
        
        def get_sentiment_score(post_list):
            if not post_list:
                return 0
            scores = []
            for post in post_list:
                sentiment = post.get('sentiment_analysis', {}).get('sentiment', 'neutral')
                if sentiment == 'positive':
                    scores.append(1)
                elif sentiment == 'negative':
                    scores.append(-1)
                else:
                    scores.append(0)
            return sum(scores) / len(scores)
        
        first_score = get_sentiment_score(first_half)
        second_score = get_sentiment_score(second_half)
        
        change = second_score - first_score
        
        if change > 0.1:
            trend = 'improving'
        elif change < -0.1:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change': round(change, 3),
            'first_period_score': round(first_score, 3),
            'second_period_score': round(second_score, 3)
        }
    
    def _analyze_keywords(self, posts: List[Dict]) -> Dict:
        """Analyze most mentioned keywords and hashtags"""
        import re
        from collections import Counter
        
        keywords = Counter()
        hashtags = Counter()
        setswana_words = Counter()
        
        # Common Setswana political words
        setswana_political = {
            'mmuso', 'polotiki', 'kgethololo', 'palamente', 'setšhaba', 'batho',
            'boeteledipele', 'puso', 'dikgethololo', 'modulasetilo', 'tonakgolo'
        }
        
        for post in posts:
            text = post.get('text', '').lower()
            
            # Extract hashtags
            post_hashtags = re.findall(r'#\w+', text)
            hashtags.update(post_hashtags)
            
            # Extract keywords (political terms)
            words = re.findall(r'\b\w+\b', text)
            political_words = [w for w in words if w in ['bdp', 'udc', 'bcp', 'masisi', 'boko', 'government', 'politics', 'election']]
            keywords.update(political_words)
            
            # Extract Setswana words
            setswana_found = [w for w in words if w in setswana_political]
            setswana_words.update(setswana_found)
        
        return {
            'top_keywords': [{'word': word, 'count': count} for word, count in keywords.most_common(10)],
            'top_hashtags': [{'hashtag': tag, 'count': count} for tag, count in hashtags.most_common(10)],
            'top_setswana_words': [{'word': word, 'count': count} for word, count in setswana_words.most_common(10)]
        }
    
    def _analyze_engagement(self, posts: List[Dict]) -> Dict:
        """Analyze engagement patterns"""
        if not posts:
            return {}
        
        total_likes = sum(post.get('likes', 0) for post in posts)
        total_shares = sum(post.get('shares', 0) for post in posts)
        total_comments = sum(post.get('comments', 0) for post in posts)
        
        # Engagement by sentiment
        sentiment_engagement = {'positive': [], 'negative': [], 'neutral': []}
        
        for post in posts:
            sentiment = post.get('sentiment_analysis', {}).get('sentiment', 'neutral')
            engagement = post.get('likes', 0) + post.get('shares', 0) + post.get('comments', 0)
            if sentiment in sentiment_engagement:
                sentiment_engagement[sentiment].append(engagement)
        
        # Calculate average engagement by sentiment
        avg_engagement = {}
        for sentiment, engagements in sentiment_engagement.items():
            avg_engagement[sentiment] = sum(engagements) / len(engagements) if engagements else 0
        
        return {
            'total_engagement': {
                'likes': total_likes,
                'shares': total_shares,
                'comments': total_comments,
                'total': total_likes + total_shares + total_comments
            },
            'average_engagement_by_sentiment': avg_engagement,
            'most_engaging_sentiment': max(avg_engagement.items(), key=lambda x: x[1])[0] if avg_engagement else 'neutral'
        }
    
    def _analyze_language_patterns(self, posts: List[Dict]) -> Dict:
        """Analyze language usage patterns"""
        if not posts:
            return {}
        
        language_sentiment = {}
        code_switching_sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for post in posts:
            analysis = post.get('sentiment_analysis', {})
            language = analysis.get('detected_language', 'English')
            sentiment = analysis.get('sentiment', 'neutral')
            code_switching = analysis.get('code_switching_detected', False)
            
            if language not in language_sentiment:
                language_sentiment[language] = {'positive': 0, 'negative': 0, 'neutral': 0}
            
            language_sentiment[language][sentiment] += 1
            
            if code_switching:
                code_switching_sentiment[sentiment] += 1
        
        # Calculate sentiment percentages by language
        language_sentiment_pct = {}
        for lang, sentiments in language_sentiment.items():
            total = sum(sentiments.values())
            if total > 0:
                language_sentiment_pct[lang] = {
                    sentiment: (count / total * 100) for sentiment, count in sentiments.items()
                }
        
        return {
            'language_sentiment_breakdown': language_sentiment_pct,
            'code_switching_sentiment': code_switching_sentiment,
            'dominant_language': max(language_sentiment.items(), key=lambda x: sum(x[1].values()))[0] if language_sentiment else 'English'
        }
    
    def _compare_political_parties(self, posts: List[Dict]) -> Dict:
        """Compare sentiment across political parties"""
        party_mentions = {
            'BDP': {'positive': 0, 'negative': 0, 'neutral': 0, 'total_engagement': 0},
            'UDC': {'positive': 0, 'negative': 0, 'neutral': 0, 'total_engagement': 0},
            'BCP': {'positive': 0, 'negative': 0, 'neutral': 0, 'total_engagement': 0}
        }
        
        for post in posts:
            text = post.get('text', '').lower()
            sentiment = post.get('sentiment_analysis', {}).get('sentiment', 'neutral')
            engagement = post.get('likes', 0) + post.get('shares', 0) + post.get('comments', 0)
            
            for party in party_mentions.keys():
                if party.lower() in text:
                    party_mentions[party][sentiment] += 1
                    party_mentions[party]['total_engagement'] += engagement
        
        # Calculate percentages and rankings
        party_rankings = []
        for party, data in party_mentions.items():
            total_mentions = data['positive'] + data['negative'] + data['neutral']
            if total_mentions > 0:
                sentiment_score = (data['positive'] - data['negative']) / total_mentions
                party_rankings.append({
                    'party': party,
                    'total_mentions': total_mentions,
                    'sentiment_score': round(sentiment_score, 3),
                    'positive_pct': round(data['positive'] / total_mentions * 100, 1),
                    'negative_pct': round(data['negative'] / total_mentions * 100, 1),
                    'neutral_pct': round(data['neutral'] / total_mentions * 100, 1),
                    'avg_engagement': round(data['total_engagement'] / total_mentions, 1) if total_mentions > 0 else 0
                })
        
        # Sort by sentiment score
        party_rankings.sort(key=lambda x: x['sentiment_score'], reverse=True)
        
        return {
            'party_rankings': party_rankings,
            'most_positive_party': party_rankings[0]['party'] if party_rankings else None,
            'most_mentioned_party': max(party_rankings, key=lambda x: x['total_mentions'])['party'] if party_rankings else None
        }
    
    def _analyze_confidence_levels(self, posts: List[Dict]) -> Dict:
        """Analyze confidence levels of sentiment predictions"""
        if not posts:
            return {}
        
        confidences = []
        confidence_by_sentiment = {'positive': [], 'negative': [], 'neutral': []}
        
        for post in posts:
            analysis = post.get('sentiment_analysis', {})
            confidence = analysis.get('confidence', 0)
            sentiment = analysis.get('sentiment', 'neutral')
            
            confidences.append(confidence)
            if sentiment in confidence_by_sentiment:
                confidence_by_sentiment[sentiment].append(confidence)
        
        # Calculate statistics
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        confidence_stats = {}
        for sentiment, conf_list in confidence_by_sentiment.items():
            if conf_list:
                confidence_stats[sentiment] = {
                    'avg_confidence': round(sum(conf_list) / len(conf_list), 3),
                    'min_confidence': round(min(conf_list), 3),
                    'max_confidence': round(max(conf_list), 3),
                    'count': len(conf_list)
                }
        
        # Confidence quality assessment
        high_confidence_posts = len([c for c in confidences if c > 0.8])
        low_confidence_posts = len([c for c in confidences if c < 0.6])
        
        return {
            'overall_avg_confidence': round(avg_confidence, 3),
            'confidence_by_sentiment': confidence_stats,
            'high_confidence_posts': high_confidence_posts,
            'low_confidence_posts': low_confidence_posts,
            'confidence_quality': 'high' if avg_confidence > 0.75 else 'medium' if avg_confidence > 0.6 else 'low'
        }
    
    def get_recent_posts(self, page: int = 1, per_page: int = 20, sentiment_filter: Optional[str] = None) -> Dict:
        """Get recent posts with pagination and filtering"""
        posts = self.get_stored_data()
        
        # Apply sentiment filter
        if sentiment_filter:
            posts = [
                post for post in posts 
                if post.get('sentiment_analysis', {}).get('sentiment') == sentiment_filter
            ]
        
        # Sort by creation date (newest first)
        posts.sort(key=lambda x: x.get('created_at', x.get('collected_at', '')), reverse=True)
        
        # Paginate
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_posts = posts[start_idx:end_idx]
        
        return {
            'posts': page_posts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(posts),
                'pages': (len(posts) + per_page - 1) // per_page,
                'has_next': end_idx < len(posts),
                'has_prev': page > 1
            }
        }

# Global storage instance
data_storage = SimpleDataStorage()