from flask import Flask, jsonify
from flask_cors import CORS

# Import configuration
from config import Config

# Import route blueprints (only essentials)
from routes.sentiment import sentiment_bp
from routes.lexicon import lexicon_bp
from routes.entities import entities_bp
from routes.social import social_bp


def create_app(config_class=Config):
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for frontend communication
    CORS(app)
    
    # Register only essential blueprints
    app.register_blueprint(sentiment_bp, url_prefix='/api/sentiment')
    app.register_blueprint(lexicon_bp, url_prefix='/api/lexicon')
    app.register_blueprint(entities_bp, url_prefix='/api/entities')
    app.register_blueprint(social_bp, url_prefix='/api/social')
    
    # Simple root endpoint
    @app.route('/')
    def index():
        return jsonify({
            "service": "Sentiment Analysis Engine",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "analyze": "POST /api/sentiment/analyze",
                "lexicon": "GET/POST /api/lexicon/*",
                "entities": "GET/POST/DELETE /api/entities/*",
                "social": "GET/POST /api/social/*"
            }
        })
    
    @app.route('/api/health')
    def health():
        """Simple health check"""
        return jsonify({"status": "healthy"})
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500
    
    return app


# Create app instance
app = create_app()

if __name__ == '__main__':
    print("Sentiment Analysis Engine")
    print("=" * 50)
    print("Endpoints:")
    print("   POST /api/sentiment/analyze - Analyze text")
    print("   GET  /api/sentiment/test-examples - Test examples")
    print("   POST /api/lexicon/add - Add word to lexicon")
    print("   GET  /api/lexicon/stats - Lexicon statistics")
    print("   GET  /api/lexicon/search - Search lexicon")
    print("   GET  /api/lexicon/health - Health check")
    print("   GET  /api/entities/ - List political entities")
    print("   POST /api/entities/add - Add political entity")
    print("   DELETE /api/entities/<id> - Delete political entity")
    print("   GET  /api/social/health - Social pipeline health")
    print("   POST /api/social/collect - Collect X posts")
    print("   GET  /api/social/collections - List collected batches")
    print("   POST /api/social/clean - Clean a collected batch")
    print("=" * 50)
    print("Starting on http://localhost:5000")
    print("CORS enabled for http://localhost:3000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
