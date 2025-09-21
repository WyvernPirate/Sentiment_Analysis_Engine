#!/usr/bin/env python3
"""
Quick test setup for Botswana Political Sentiment Analysis
This script helps you test the basic functionality before adding complex features
"""

import subprocess
import sys
import os
import time
import requests

def check_python_packages():
    """Check if required packages are installed"""
    required_packages = ['flask', 'flask-cors']
    optional_packages = ['transformers', 'torch']
    
    missing_required = []
    missing_optional = []
    
    # Check required packages
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_required.append(package)
            print(f"❌ {package} is missing (REQUIRED)")
    
    # Check optional packages
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed (enhanced English sentiment)")
        except ImportError:
            missing_optional.append(package)
            print(f"⚠️  {package} is missing (optional - will use basic English sentiment)")
    
    # Install required packages
    if missing_required:
        print(f"\n📦 Installing required packages: {', '.join(missing_required)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_required)
            print("✅ Required packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install required packages. Please run manually:")
            print(f"   pip install {' '.join(missing_required)}")
            return False
    
    # Offer to install optional packages
    if missing_optional:
        print(f"\n🔧 Optional packages missing: {', '.join(missing_optional)}")
        print("   These provide better English sentiment analysis.")
        print("   The system will work without them using basic keyword analysis.")
        
        response = input("\n   Install optional packages for better English sentiment? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_optional)
                print("✅ Optional packages installed successfully!")
            except subprocess.CalledProcessError:
                print("⚠️  Failed to install optional packages, continuing with basic analysis")
    
    return True

def test_api_endpoints():
    """Test the API endpoints"""
    base_url = "http://localhost:5000"
    
    print("\n🧪 Testing API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Setswana words: {data.get('lexicon_stats', {}).get('setswana_words', 'N/A')}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health endpoint failed: {e}")
        return False
    
    # Test sentiment analysis
    test_texts = [
        "Ke rata mmuso o, o dira sentle thata",  # Setswana positive
        "The government is doing botlhoko work",  # Code-switching negative
        "Masisi is a great leader",  # English positive with political entity
    ]
    
    for text in test_texts:
        try:
            response = requests.post(
                f"{base_url}/api/sentiment",
                json={"text": text},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ '{text}' -> {data.get('sentiment')} ({data.get('detected_language')})")
            else:
                print(f"❌ Sentiment analysis failed for '{text}': {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Sentiment analysis failed for '{text}': {e}")
    
    return True

def main():
    """Main test function"""
    print("🇧🇼 Botswana Political Sentiment Analysis - Test Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('simple_app.py'):
        print("❌ simple_app.py not found. Please run this from the backend directory.")
        return
    
    # Check Python packages
    if not check_python_packages():
        return
    
    print("\n🚀 Starting the Flask server...")
    print("   The server will start on http://localhost:5000")
    print("   You can test it by:")
    print("   1. Opening http://localhost:5000/api/health in your browser")
    print("   2. Running the React frontend (npm start in frontend directory)")
    print("   3. Using the test examples in the frontend")
    
    print("\n📝 Test Examples to try:")
    examples = [
        "Ke rata mmuso o, o dira sentle thata",
        "The government is doing botlhoko work", 
        "Masisi is a great leader for Botswana",
        "BDP le UDC ba lwantshana thata",
        "I love the new policy changes"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"   {i}. {example}")
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. Keep this terminal open (Flask server running)")
    print("2. Open a new terminal and run: cd ../frontend && npm start")
    print("3. Test the examples in the web interface")
    print("4. Once working, we can add the ML model and social media APIs")
    
    # Start the Flask server
    try:
        os.system('python simple_app.py')
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thanks for testing!")

if __name__ == "__main__":
    main()