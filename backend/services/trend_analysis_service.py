"""
Trend Analysis Service
Business logic for political sentiment trend analysis
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from models import db, SocialMediaPost, SentimentAnalysis, PoliticalTrend
from sqlalchemy import func, and_, or_
import json

class TrendAnalysisService:
    def __init__(self):
        pass
    
    def get_overview_stats(self, start_date: datetime) -> Dict[str, Any]:
        """Get overview statistics for dashboard"""
        try:
            # Total posts in period
            total_posts = SocialMediaPost.query.filter(
                SocialMediaPost.collected_at >= start_date
            ).count()
            
            # Sentiment breakdown
            sentiment_stats = db.session.query(
                SentimentAnalysis.sentiment,
                func.count(SentimentAnalysis.id).label('count')
            ).join(SocialMediaPost).filter(
                SocialMediaPost.collected_at >= start_date
            ).group_by(SentimentAnalysis.sentiment).all()
            
            sentiment_breakdown = {stat.sentiment: stat.count for stat in sentiment_stats}
            
            # Language breakdown
            language_stats = db.session.query(
                SentimentAnalysis.detected_language,
                func.count(SentimentAnalysis.id).label('count')
            ).join(SocialMediaPost).filter(
                SocialMediaPost.collected_at >= start_date
            ).group_by(SentimentAnalysis.detected_language).all()
            
            language_breakdown = {stat.detected_language or 'Unknown': stat.count for stat in language_stats}
            
            # Platform breakdown
            platform_stats = db.session.query(
                SocialMediaPost.platform,
                func.count(SocialMediaPost.id).label('count')
            ).filter(
                SocialMediaPost.collected_at >= start_date
            ).group_by(SocialMediaPost.platform).all()
            
            platform_breakdown = {stat.platform: stat.count for stat in platform_stats}
            
            # Code-switching detection
            code_switching_count = db.session.query(SentimentAnalysis).join(SocialMediaPost).filter(
                and_(
                    SocialMediaPost.collected_at >= start_date,
                    SentimentAnalysis.code_switching_detected == True
                )
            ).count()
            
            return {
                'total_posts': total_posts,
                'sentiment_breakdown': sentiment_breakdown,
                'language_breakdown': language_breakdown,
                'platform_breakdown': platform_breakdown,
                'code_switching_posts': code_switching_count,
                'code_switching_percentage': (code_switching_count / total_posts * 100) if total_posts > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting overview stats: {e}")
            return {}
    
    def get_sentiment_trends(self, 
                           start_date: datetime, 
                           keyword: Optional[str] = None,
                           granularity: str = 'daily') -> List[Dict[str, Any]]:
        """Get sentiment trends over time"""
        try:
            # Determine date grouping based on granularity
            if granularity == 'hourly':
                date_func = func.date_trunc('hour', SocialMediaPost.created_at)
            else:
                date_func = func.date_trunc('day', SocialMediaPost.created_at)
            
            # Build base query
            query = db.session.query(
                date_func.label('period'),
                SentimentAnalysis.sentiment,
                func.count(SentimentAnalysis.id).label('count')
            ).join(SocialMediaPost).filter(
                SocialMediaPost.created_at >= start_date
            )
            
            # Add keyword filter if provided
            if keyword:
                query = query.filter(
                    or_(
                        SocialMediaPost.text.ilike(f'%{keyword}%'),
                        SentimentAnalysis.political_keywords.ilike(f'%{keyword}%')
                    )
                )
            
            # Group and order
            trends = query.group_by(
                date_func,
                SentimentAnalysis.sentiment
            ).order_by(date_func).all()
            
            # Format results
            trend_data = {}
            for trend in trends:
                period_str = trend.period.isoformat()
                if period_str not in trend_data:
                    trend_data[period_str] = {'positive': 0, 'negative': 0, 'neutral': 0}
                trend_data[period_str][trend.sentiment] = trend.count
            
            # Convert to list format
            formatted_trends = []
            for period, sentiments in sorted(trend_data.items()):
                total = sum(sentiments.values())
                formatted_trends.append({
                    'period': period,
                    'sentiments': sentiments,
                    'total': total,
                    'percentages': {
                        sentiment: (count / total * 100) if total > 0 else 0
                        for sentiment, count in sentiments.items()
                    }
                })
            
            return formatted_trends
            
        except Exception as e:
            print(f"Error getting sentiment trends: {e}")
            return []
    
    def get_posts_with_filters(self,
                              page: int = 1,
                              per_page: int = 20,
                              sentiment_filter: Optional[str] = None,
                              platform_filter: Optional[str] = None,
                              keyword_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get posts with filtering and pagination"""
        try:
            # Build query
            query = db.session.query(SocialMediaPost).join(SentimentAnalysis)
            
            # Apply filters
            if sentiment_filter:
                query = query.filter(SentimentAnalysis.sentiment == sentiment_filter)
            
            if platform_filter:
                query = query.filter(SocialMediaPost.platform == platform_filter)
            
            if keyword_filter:
                query = query.filter(
                    or_(
                        SocialMediaPost.text.ilike(f'%{keyword_filter}%'),
                        SentimentAnalysis.political_keywords.ilike(f'%{keyword_filter}%')
                    )
                )
            
            # Paginate
            posts = query.order_by(SocialMediaPost.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # Format results
            posts_data = []
            for post in posts.items:
                post_dict = post.to_dict()
                if post.sentiment_analysis:
                    post_dict['sentiment_analysis'] = post.sentiment_analysis.to_dict()
                posts_data.append(post_dict)
            
            return {
                'posts': posts_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': posts.total,
                    'pages': posts.pages,
                    'has_next': posts.has_next,
                    'has_prev': posts.has_prev
                },
                'filters': {
                    'sentiment': sentiment_filter,
                    'platform': platform_filter,
                    'keyword': keyword_filter
                }
            }
            
        except Exception as e:
            print(f"Error getting posts: {e}")
            return {'posts': [], 'pagination': {}, 'filters': {}}
    
    def get_political_entity_sentiment(self, start_date: datetime) -> List[Dict[str, Any]]:
        """Get sentiment breakdown by political entities"""
        try:
            # Get posts with political entities
            posts_with_entities = db.session.query(
                SocialMediaPost, SentimentAnalysis
            ).join(SentimentAnalysis).filter(
                and_(
                    SocialMediaPost.collected_at >= start_date,
                    SentimentAnalysis.political_entities.isnot(None),
                    SentimentAnalysis.political_entities != '[]'
                )
            ).all()
            
            entity_sentiment = {}
            
            for post, analysis in posts_with_entities:
                try:
                    entities = json.loads(analysis.political_entities) if analysis.political_entities else []
                    for entity_data in entities:
                        entity_name = entity_data.get('entity', '')
                        if entity_name:
                            if entity_name not in entity_sentiment:
                                entity_sentiment[entity_name] = {
                                    'positive': 0, 'negative': 0, 'neutral': 0,
                                    'type': entity_data.get('type', 'unknown')
                                }
                            entity_sentiment[entity_name][analysis.sentiment] += 1
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Format results
            formatted_entities = []
            for entity, sentiments in entity_sentiment.items():
                total = sentiments['positive'] + sentiments['negative'] + sentiments['neutral']
                if total > 0:
                    formatted_entities.append({
                        'entity': entity,
                        'type': sentiments['type'],
                        'sentiments': {
                            'positive': sentiments['positive'],
                            'negative': sentiments['negative'],
                            'neutral': sentiments['neutral']
                        },
                        'total': total,
                        'percentages': {
                            'positive': sentiments['positive'] / total * 100,
                            'negative': sentiments['negative'] / total * 100,
                            'neutral': sentiments['neutral'] / total * 100
                        }
                    })
            
            # Sort by total mentions
            formatted_entities.sort(key=lambda x: x['total'], reverse=True)
            
            return formatted_entities
            
        except Exception as e:
            print(f"Error getting political entity sentiment: {e}")
            return []
    
    def get_language_breakdown(self, start_date: datetime) -> Dict[str, Any]:
        """Get detailed language usage breakdown"""
        try:
            # Language distribution
            language_stats = db.session.query(
                SentimentAnalysis.detected_language,
                func.count(SentimentAnalysis.id).label('count'),
                func.avg(SentimentAnalysis.confidence).label('avg_confidence')
            ).join(SocialMediaPost).filter(
                SocialMediaPost.collected_at >= start_date
            ).group_by(SentimentAnalysis.detected_language).all()
            
            # Code-switching analysis
            code_switching_stats = db.session.query(
                SentimentAnalysis.code_switching_detected,
                func.count(SentimentAnalysis.id).label('count')
            ).join(SocialMediaPost).filter(
                SocialMediaPost.collected_at >= start_date
            ).group_by(SentimentAnalysis.code_switching_detected).all()
            
            language_breakdown = {}
            total_posts = 0
            
            for stat in language_stats:
                lang = stat.detected_language or 'Unknown'
                language_breakdown[lang] = {
                    'count': stat.count,
                    'avg_confidence': float(stat.avg_confidence) if stat.avg_confidence else 0.0
                }
                total_posts += stat.count
            
            # Add percentages
            for lang in language_breakdown:
                language_breakdown[lang]['percentage'] = (
                    language_breakdown[lang]['count'] / total_posts * 100
                ) if total_posts > 0 else 0
            
            code_switching_breakdown = {
                str(stat.code_switching_detected): stat.count 
                for stat in code_switching_stats
            }
            
            return {
                'language_distribution': language_breakdown,
                'code_switching_distribution': code_switching_breakdown,
                'total_posts': total_posts
            }
            
        except Exception as e:
            print(f"Error getting language breakdown: {e}")
            return {}
    
    def get_recent_sentiment_distribution(self, since: datetime) -> Dict[str, int]:
        """Get recent sentiment distribution for real-time stats"""
        try:
            stats = db.session.query(
                SentimentAnalysis.sentiment,
                func.count(SentimentAnalysis.id).label('count')
            ).join(SocialMediaPost).filter(
                SocialMediaPost.collected_at >= since
            ).group_by(SentimentAnalysis.sentiment).all()
            
            return {stat.sentiment: stat.count for stat in stats}
            
        except Exception as e:
            print(f"Error getting recent sentiment distribution: {e}")
            return {}
    
    def get_trending_keywords(self, since: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending political keywords"""
        try:
            # This is a simplified version - in production, you'd want more sophisticated keyword extraction
            posts = db.session.query(SentimentAnalysis.political_keywords).join(SocialMediaPost).filter(
                and_(
                    SocialMediaPost.collected_at >= since,
                    SentimentAnalysis.political_keywords.isnot(None),
                    SentimentAnalysis.political_keywords != '[]'
                )
            ).all()
            
            keyword_counts = {}
            for post in posts:
                try:
                    keywords = json.loads(post.political_keywords) if post.political_keywords else []
                    for keyword_data in keywords:
                        keyword = keyword_data.get('term', '') if isinstance(keyword_data, dict) else str(keyword_data)
                        if keyword:
                            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Sort and limit
            trending = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            return [{'keyword': k, 'count': v} for k, v in trending]
            
        except Exception as e:
            print(f"Error getting trending keywords: {e}")
            return []
    
    def get_active_platforms(self, since: datetime) -> Dict[str, int]:
        """Get active platforms for real-time stats"""
        try:
            stats = db.session.query(
                SocialMediaPost.platform,
                func.count(SocialMediaPost.id).label('count')
            ).filter(
                SocialMediaPost.collected_at >= since
            ).group_by(SocialMediaPost.platform).all()
            
            return {stat.platform: stat.count for stat in stats}
            
        except Exception as e:
            print(f"Error getting active platforms: {e}")
            return {}

# Global service instance
trend_service = TrendAnalysisService()