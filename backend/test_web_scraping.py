#!/usr/bin/env python3
"""
Test Web Scraping Data Collection
Demonstrates collecting Botswana political content without Facebook API
"""

import requests
import json
from simple_data_collector import collect_simple_data

def test_web_scraping():
    """Test the web scraping functionality"""
    print("🕷️  Testing Web Scraping Data Collection")
    print("=" * 50)
    
    # Test direct collection
    print("1. Testing direct data collection...")
    try:
        result = collect_simple_data()
        
        if result['success']:
            print(f"✅ Success! Collected {result['total_collected']} items")
            print("📊 Sources breakdown:")
            for source, count in result['sources'].items():
                print(f"   - {source}: {count} items")
            
            # Show sample data
            if result['data']:
                print("\n📝 Sample collected data:")
                for i, item in enumerate(result['data'][:3]):
                    print(f"   {i+1}. [{item['platform']}] {item['text'][:80]}...")
        else:
            print("❌ Collection failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test API endpoint (if backend is running)
    print("2. Testing API endpoint...")
    try:
        response = requests.post('http://localhost:5000/api/collect/web-scraping', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Success! {data['message']}")
            print(f"📊 Total collected: {data['total_collected']}")
            print("📊 Sources:")
            for source, count in data['sources'].items():
                print(f"   - {source}: {count} items")
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("🔌 Backend not running - start with: python simple_app.py")
    except Exception as e:
        print(f"❌ API Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test collection status endpoint
    print("3. Testing collection status...")
    try:
        response = requests.get('http://localhost:5000/api/collect/status', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Available data sources:")
            for source, info in data['available_sources'].items():
                print(f"   - {source}: {info['status']} - {info['description']}")
            
            print(f"\n🎯 Target hashtags: {', '.join(data['target_hashtags'][:5])}...")
            print(f"🔑 Target keywords: {', '.join(data['target_keywords'][:5])}...")
            print(f"📱 Facebook API required: {data['facebook_api_required']}")
            print(f"🐦 Twitter API required: {data['twitter_api_required']}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("🔌 Backend not running for status check")
    except Exception as e:
        print(f"❌ Status Error: {e}")

def show_collection_capabilities():
    """Show what data sources are available"""
    print("\n🎯 Data Collection Capabilities (No Facebook API)")
    print("=" * 60)
    
    capabilities = {
        "Reddit r/Botswana": {
            "status": "✅ Active",
            "description": "Public Reddit API - no authentication required",
            "data_type": "Political discussions and posts",
            "example": "Real posts from Botswana subreddit about politics"
        },
        "Mock Social Media": {
            "status": "✅ Active",
            "description": "Generated realistic content for testing",
            "data_type": "Sample posts in English and Setswana",
            "example": "BDP's new policy looks promising #BDP2024"
        },
        "News Headlines": {
            "status": "✅ Active", 
            "description": "Botswana political news aggregation",
            "data_type": "Political news and announcements",
            "example": "President Masisi announces economic recovery plan"
        },
        "Web Scraping": {
            "status": "🔧 Available",
            "description": "Public websites, forums, news sites",
            "data_type": "Articles and discussions from public sources",
            "example": "Mmegi Online, The Voice, Botswana Guardian"
        }
    }
    
    for source, info in capabilities.items():
        print(f"\n📊 {source}")
        print(f"   Status: {info['status']}")
        print(f"   Description: {info['description']}")
        print(f"   Data Type: {info['data_type']}")
        print(f"   Example: {info['example']}")
    
    print("\n🎯 Target Content:")
    print("   Hashtags: #BotswanaPolitics, #BDP2024, #UDC2024, #Masisi, #Boko")
    print("   Keywords: Botswana politics, BDP, UDC, mmuso, polotiki, kgethololo")
    print("   Languages: English, Setswana, Code-switching")
    
    print("\n💡 Benefits:")
    print("   ✅ No Facebook API required")
    print("   ✅ No Twitter API required (for basic collection)")
    print("   ✅ Focuses on public, accessible sources")
    print("   ✅ Targets Botswana-specific political content")
    print("   ✅ Supports Setswana language content")

if __name__ == "__main__":
    show_collection_capabilities()
    test_web_scraping()