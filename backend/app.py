"""
Main Flask Application
Botswana Political Sentiment Analysis Platform
"""
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import os

# Import configuration and models
from config import Config
from models import db

# Import route blueprints
from routes.sentiment import sentiment_bp
from routes.dashboard import dashboard_bp
from routes.lexicon import lexicon_bp
from routes.training import training_bp
from routes.admin import admin_bp

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(sentiment_bp, url_prefix='/api/sentiment')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(lexicon_bp, url_prefix='/api/lexicon')
    app.register_blueprint(training_bp, url_prefix='/api/training')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Root endpoints
    @app.route('/')
    def index():
        return jsonify({
            "service": "Botswana Political Sentiment Analysis API",
            "version": "1.0.0",
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "sentiment": "/api/sentiment/*",
                "dashboard": "/api/dashboard/*", 
                "lexicon": "/api/lexicon/*",
                "training": "/api/training/*",
                "admin": "/api/admin/*"
            }
        })
    
    @app.route('/api/health')
    def health():
        """Comprehensive health check"""
        try:
            # Check database connection
            db.session.execute('SELECT 1')
            
            # Check model availability
            model_available = os.path.exists(Config.SENTIMENT_MODEL_PATH)
            
            # Get system stats
            from models import SocialMediaPost, SentimentAnalysis
            recent_posts = SocialMediaPost.query.filter(
                SocialMediaPost.collected_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            unprocessed_posts = db.session.query(SocialMediaPost)\
                .outerjoin(SentimentAnalysis)\
                .filter(SentimentAnalysis.id.is_(None))\
                .count()
            
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "custom_model_available": model_available,
                "model_path": Config.SENTIMENT_MODEL_PATH,
                "fallback_model": Config.FALLBACK_MODEL,
                "stats": {
                    "posts_last_24h": recent_posts,
                    "unprocessed_posts": unprocessed_posts
                },
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Botswana Political Sentiment Analysis Platform")
    print("=" * 70)
    print("📍 API Endpoints:")
    print("   GET  / - Service information")
    print("   GET  /api/health - Health check")
    print("")
    print("📊 Sentiment Analysis:")
    print("   POST /api/sentiment/analyze - Analyze text sentiment")
    print("   POST /api/sentiment/batch - Batch analysis")
    print("   POST /api/sentiment/feedback - Submit feedback")
    print("")
    print("📈 Dashboard:")
    print("   GET  /api/dashboard/overview - Overview statistics")
    print("   GET  /api/dashboard/trends - Sentiment trends")
    print("   GET  /api/dashboard/posts - Recent posts")
    print("   GET  /api/dashboard/political-entities - Entity sentiment")
    print("   GET  /api/dashboard/language-breakdown - Language analysis")
    print("   GET  /api/dashboard/real-time-stats - Real-time statistics")
    print("")
    print("📚 Lexicon Management:")
    print("   GET  /api/lexicon/stats - Lexicon statistics")
    print("   POST /api/lexicon/add - Add new word")
    print("   GET  /api/lexicon/search - Search words")
    print("   POST /api/lexicon/suggest - Suggest word for review")
    print("   GET  /api/lexicon/export - Export lexicon")
    print("")
    print("🎓 Training:")
    print("   POST /api/training/prepare-dataset - Prepare training data")
    print("   POST /api/training/train-model - Train model")
    print("   POST /api/training/quick-retrain - Quick retrain")
    print("   GET  /api/training/stats - Training statistics")
    print("   POST /api/training/export - Export training data")
    print("   POST /api/training/feedback - Submit feedback")
    print("")
    print("🔧 Admin:")
    print("   GET  /api/admin/pending-suggestions - Review suggestions")
    print("   POST /api/admin/approve-word - Approve word suggestion")
    print("   GET  /api/admin/system-stats - System statistics")
    print("   POST /api/admin/data-collection/trigger - Trigger data collection")
    print("   POST /api/admin/analysis/trigger - Trigger analysis")
    print("   POST /api/admin/cleanup/old-data - Cleanup old data")
    print("")
    print("🌐 Frontend should connect to: http://localhost:5000")
    print("=" * 70)

    debug_env = os.getenv('FLASK_DEBUG')
    if debug_env is not None:
        debug_mode = debug_env.lower() == 'true'
    else:
        debug_mode = getattr(Config, 'DEBUG', False)

    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
