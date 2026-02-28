from flask import Blueprint, jsonify
from services.lexicon_service import lexicon_service

lexicon_bp = Blueprint('lexicon', __name__)

@lexicon_bp.route('/', methods=['GET'])
def get_lexicon():
    return jsonify(lexicon_service.get_stats())

@lexicon_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "lexicon"})