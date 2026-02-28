from flask import Flask
from flask_cors import CORS
import os
from routes.sentiment import sentiment_bp
from routes.lexicon import lexicon_bp
from routes.dashboard import dashboard_bp
from routes.training import training_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(sentiment_bp, url_prefix='/api/sentiment')
    app.register_blueprint(lexicon_bp, url_prefix='/api/lexicon')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(training_bp, url_prefix='/api/training')
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "monolith_refactored": True}

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)