from flask import Blueprint, jsonify, request
from services.system_service import SystemService

system_bp = Blueprint('system', __name__)

@system_bp.route('/health', methods=['GET'])
def get_health():
    """Returns detailed system health diagnostics."""
    health_data = SystemService.get_system_health()
    return jsonify(health_data)

@system_bp.route('/logs', methods=['GET'])
def get_logs():
    """Returns recent system logs."""
    limit = request.args.get('limit', default=50, type=int)
    logs = SystemService.get_logs(limit)
    return jsonify({
        "logs": logs,
        "count": len(logs)
    })

@system_bp.route('/event', methods=['POST'])
def log_event():
    """Endpoint for services/frontend to log custom events."""
    data = request.get_json()
    level = data.get('level', 'INFO')
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
        
    SystemService.log_event(level, message)
    return jsonify({"status": "logged"})
