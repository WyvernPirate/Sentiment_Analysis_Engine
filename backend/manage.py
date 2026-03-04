#!/usr/bin/env python3
import argparse
import sys
import os

# Add the current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def collect_data(source, keyword=None):
    print(f"🚀 Starting data collection from: {source}")
    if source == 'simple':
        from simple_data_collector import collect_simple_data
        collect_simple_data()
    elif source in ['twitter', 'facebook', 'reddit']:
        from data_collector import BotswanaPoliticalDataCollector
        collector = BotswanaPoliticalDataCollector()
        if source == 'twitter':
            collector.collect_political_tweets(max_results=100)
        # Add other sources as needed...
    else:
        print(f"❌ Unknown source: {source}")

def train_model(quick=False):
    print(f"🧠 Starting model training (quick={quick})...")
    if quick:
        from train_sentiment_model_quick import main as train_quick
        train_quick()
    else:
        from train_sentiment_model import main as train_full
        train_full()

def main():
    parser = argparse.ArgumentParser(description='Sentiment Analysis Engine Management CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect data from various sources')
    collect_parser.add_argument('--source', choices=['twitter', 'facebook', 'reddit', 'news', 'simple'], default='simple')
    collect_parser.add_argument('--keyword', help='Specific keyword to search for')

    # Train command
    train_parser = subparsers.add_parser('train', help='Train sentiment models')
    train_parser.add_argument('--quick', action='store_true', help='Run a quick training session')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run the Flask server')

    args = parser.parse_args()

    if args.command == 'collect':
        collect_data(args.source, args.keyword)
    elif args.command == 'train':
        train_model(args.quick)
    elif args.command == 'run':
        from app import create_app
        app = create_app()
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
