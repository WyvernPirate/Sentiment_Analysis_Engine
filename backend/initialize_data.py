#!/usr/bin/env python3
"""
Initialize Data for Simple App
Collects initial data on startup so dashboard has content immediately
"""

import os
import sys
from data_storage import data_storage

def initialize_dashboard_data():
    """Initialize dashboard with fresh data"""
    print("🔄 Initializing dashboard data...")
    
    try:
        # Collect and analyze data
        result = data_storage.collect_and_store_data(force_refresh=True)
        
        if result.get('success'):
            print(f"✅ Successfully initialized with {result['total_collected']} posts")
            print(f"📊 Analyzed {result.get('analyzed', 0)} posts for sentiment")
            
            # Show overview stats
            overview = data_storage.get_dashboard_overview()
            print(f"📈 Dashboard stats:")
            print(f"   Total posts: {overview['total_posts']}")
            print(f"   Sentiment: +{overview['sentiment_breakdown']['positive']} "
                  f"~{overview['sentiment_breakdown']['neutral']} "
                  f"-{overview['sentiment_breakdown']['negative']}")
            print(f"   Code-switching: {overview['code_switching_percentage']:.1f}%")
            
            return True
        else:
            print(f"❌ Initialization failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return False

if __name__ == "__main__":
    success = initialize_dashboard_data()
    if success:
        print("\n🚀 Data initialization complete! You can now:")
        print("   1. Start the backend: python simple_app.py")
        print("   2. View dashboard with real data")
        print("   3. Refresh data anytime with: POST /api/collect/web-scraping")
    else:
        print("\n⚠️  Initialization failed, but you can still:")
        print("   1. Start the backend: python simple_app.py") 
        print("   2. Manually collect data via the API")
        sys.exit(1)