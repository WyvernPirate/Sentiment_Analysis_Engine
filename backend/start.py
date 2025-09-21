#!/usr/bin/env python3
"""
Startup script for Botswana Political Sentiment Analysis Platform
Choose between simple testing mode or full production mode
"""

import sys
import os

def main():
    print("🇧🇼 Botswana Political Sentiment Analysis Platform")
    print("=" * 60)
    print("Choose your mode:")
    print("1. Simple Testing Mode (simple_app.py)")
    print("   - Basic sentiment analysis")
    print("   - Lexicon management")
    print("   - Mock dashboard data")
    print("   - Perfect for development and testing")
    print("")
    print("2. Production Mode (app_production.py)")
    print("   - Full database integration")
    print("   - Real social media data collection")
    print("   - Complete dashboard with real data")
    print("   - All production features")
    print("")
    
    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting Simple Testing Mode...")
            print("📍 Features available:")
            print("   ✅ Sentiment analysis with Setswana support")
            print("   ✅ Lexicon management")
            print("   ✅ Training data collection")
            print("   ✅ Mock dashboard (for frontend testing)")
            print("   ✅ All management endpoints")
            print("")
            print("🌐 Frontend will connect to: http://localhost:5000")
            print("💡 Perfect for testing and development!")
            print("")
            
            # Import and run simple app
            try:
                import simple_app
            except ImportError as e:
                print(f"❌ Error importing simple_app: {e}")
                print("Make sure you're in the backend directory")
                sys.exit(1)
            break
            
        elif choice == "2":
            print("\n🚀 Starting Production Mode...")
            print("📍 Features available:")
            print("   ✅ Full database integration")
            print("   ✅ Real-time social media data collection")
            print("   ✅ Complete dashboard with real data")
            print("   ✅ Advanced analytics and trends")
            print("   ✅ Admin panel with system management")
            print("")
            print("⚠️  Requirements:")
            print("   - Database configured (SQLite/PostgreSQL)")
            print("   - Social media API keys (optional)")
            print("   - All dependencies installed")
            print("")
            print("🌐 Frontend will connect to: http://localhost:5000")
            print("")
            
            # Import and run production app
            try:
                import app_production
            except ImportError as e:
                print(f"❌ Error importing app_production: {e}")
                print("Make sure all dependencies are installed:")
                print("   pip install -r requirements.txt")
                sys.exit(1)
            break
            
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()