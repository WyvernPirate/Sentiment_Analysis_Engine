#!/usr/bin/env python3
"""
Setup script for Botswana Political Sentiment Analysis Platform
"""

import os
import sys
from flask import Flask
from config import Config
from models import db

def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def setup_database():
    """Initialize database tables"""
    print("Setting up database...")
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully")

def check_environment():
    """Check if required environment variables are set"""
    print("Checking environment configuration...")
    
    required_vars = [
        'TWITTER_BEARER_TOKEN',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease copy .env.example to .env and fill in the required values.")
        return False
    
    print("✓ Environment configuration looks good")
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'flask', 'transformers', 'torch', 'tweepy', 'sqlalchemy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease run: pip install -r requirements.txt")
        return False
    
    print("✓ All required packages are installed")
    return True

def setup_directories():
    """Create necessary directories"""
    print("Setting up directories...")
    
    directories = [
        'models',
        'logs',
        'data/training_data',
        'data/models'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🚀 Setting up Botswana Political Sentiment Analysis Platform")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Setup database
    setup_database()
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Train your sentiment model: python train_sentiment_model.py")
    print("2. Start data collection: python -c 'from data_collector import collect_all_data; collect_all_data()'")
    print("3. Run the Flask app: python app.py")
    print("4. Visit http://localhost:5000/api/health to check status")

if __name__ == "__main__":
    main()