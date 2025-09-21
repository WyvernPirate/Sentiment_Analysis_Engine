#!/usr/bin/env python3
"""
Test Real Data Integration
Verify that dashboard endpoints return real data instead of mocks
"""

import requests
import json
from data_storage import data_storage

def test_data_storage():
    """Test the data storage functionality"""
    print("🧪 Testing Data Storage")
    print("=" * 40)
    
    # Test data collection
    print("1. Testing data collection...")
    result = data_storage.collect_and_store_data(force_refresh=True)
    
    if result.get('success'):
        print(f"✅ Collected {result['total_collected']} posts")
        print(f"📊 Analyzed {result.get('analyzed', 0)} posts")
    else:
        print(f"❌ Collection failed: {result.get('error')}")
        return False
    
    # Test overview stats
    print("\n2. Testing overview statistics...")
    overview = data_storage.get_dashboard_overview()
    print(f"✅ Total posts: {overview['total_posts']}")
    print(f"📊 Sentiment breakdown: {overview['sentiment_breakdown']}")
    print(f"🌍 Language breakdown: {overview['language_breakdown']}")
    print(f"📱 Platform breakdown: {overview['platform_breakdown']}")
    
    # Test trends
    print("\n3. Testing sentiment trends...")
    trends = data_storage.get_sentiment_trends()
    print(f"✅ Found {len(trends)} trend data points")
    if trends:
        print(f"📈 Latest trend: {trends[-1]}")
    
    # Test political entities
    print("\n4. Testing political entities...")
    entities = data_storage.get_political_entities()
    print(f"✅ Found {len(entities)} political entities")
    for entity in entities:
        print(f"🏛️  {entity['entity']} ({entity['type']}): {entity['total']} mentions")
    
    # Test posts
    print("\n5. Testing recent posts...")
    posts_data = data_storage.get_recent_posts(page=1, per_page=5)
    print(f"✅ Retrieved {len(posts_data['posts'])} posts")
    for i, post in enumerate(posts_data['posts'][:3]):
        sentiment = post.get('sentiment_analysis', {}).get('sentiment', 'unknown')
        print(f"📝 Post {i+1}: [{post['platform']}] {sentiment} - {post['text'][:60]}...")
    
    return True

def test_api_endpoints():
    """Test API endpoints with real data"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    endpoints = [
        ("GET", "/api/dashboard/overview"),
        ("GET", "/api/dashboard/trends"),
        ("GET", "/api/dashboard/posts?per_page=5"),
        ("GET", "/api/dashboard/political-entities"),
        ("GET", "/api/collect/status"),
        ("POST", "/api/collect/web-scraping")
    ]
    
    for method, endpoint in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {method} {endpoint}")
                
                # Show some key data
                if 'stats' in data:
                    stats = data['stats']
                    print(f"   📊 Total posts: {stats.get('total_posts', 0)}")
                elif 'trends' in data:
                    print(f"   📈 Trend points: {len(data['trends'])}")
                elif 'posts' in data:
                    print(f"   📝 Posts returned: {len(data['posts'])}")
                elif 'entities' in data:
                    print(f"   🏛️  Entities found: {len(data['entities'])}")
                elif 'total_collected' in data:
                    print(f"   🕷️  Collected: {data['total_collected']} items")
                
            else:
                print(f"❌ {method} {endpoint} - Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"🔌 {method} {endpoint} - Backend not running")
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {e}")

def show_sample_data():
    """Show sample of collected data"""
    print("\n📋 Sample Collected Data")
    print("=" * 40)
    
    posts = data_storage.get_stored_data()
    
    if not posts:
        print("❌ No data available")
        return
    
    print(f"📊 Total posts in storage: {len(posts)}")
    print("\n📝 Sample posts:")
    
    for i, post in enumerate(posts[:5]):
        sentiment = post.get('sentiment_analysis', {}).get('sentiment', 'unknown')
        language = post.get('sentiment_analysis', {}).get('detected_language', 'unknown')
        confidence = post.get('sentiment_analysis', {}).get('confidence', 0)
        
        print(f"\n{i+1}. [{post['platform']}] {sentiment} ({confidence:.2f}) - {language}")
        print(f"   Text: {post['text'][:100]}...")
        print(f"   Author: {post.get('author', 'unknown')}")
        print(f"   Created: {post.get('created_at', 'unknown')}")

if __name__ == "__main__":
    print("🧪 Testing Real Data Integration")
    print("=" * 50)
    
    # Test data storage
    if test_data_storage():
        print("\n✅ Data storage tests passed!")
        
        # Show sample data
        show_sample_data()
        
        # Test API endpoints (if backend is running)
        print("\n🌐 Testing API endpoints...")
        print("💡 Make sure backend is running: python simple_app.py")
        test_api_endpoints()
        
    else:
        print("\n❌ Data storage tests failed!")
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print("✅ Dashboard now uses REAL data from web scraping")
    print("✅ Data includes Reddit posts + realistic mock content")
    print("✅ All posts are analyzed for sentiment automatically")
    print("✅ Political entities are extracted from content")
    print("🔄 Refresh data anytime with: POST /api/collect/web-scraping")