#!/usr/bin/env python3
"""
Quick CORS fix test - verify that all endpoints work
"""

import requests
import json

def test_endpoints():
    base_url = "http://localhost:5000"
    
    endpoints_to_test = [
        "/api/health",
        "/api/dashboard/overview?days=7",
        "/api/dashboard/trends?days=7",
        "/api/dashboard/posts?page=1&per_page=5",
        "/api/dashboard/political-entities?days=7",
        "/api/dashboard/language-breakdown?days=7",
        "/api/dashboard/real-time-stats",
        "/api/lexicon/stats",
        "/api/training/stats"
    ]
    
    print("🧪 Testing API endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"🔌 {endpoint} - Backend not running")
        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint} - Timeout")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    print("=" * 50)
    print("💡 If you see connection errors, start the backend:")
    print("   cd backend && python simple_app.py")

if __name__ == "__main__":
    test_endpoints()