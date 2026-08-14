from flask import Blueprint, jsonify, request
from services.political_entity_service import political_entity_service


entities_bp = Blueprint('entities', __name__)

# Endpoint to list political entities, optionally filtered by type
@entities_bp.route('/', methods=['GET'])
def list_entities():
    entity_type = request.args.get('type', '').strip() or None
    entities = political_entity_service.list_entities(entity_type)
    return jsonify({'entities': entities, 'count': len(entities)})

# Endpoint returning real mention counts + net sentiment + risk level per
# entity, aggregated from recent analysis jobs. Replaces what used to be
# hardcoded 0/'N/A'/'LOW' values on the frontend.
@entities_bp.route('/stats', methods=['GET'])
def entity_stats():
    stats = political_entity_service.get_bulk_entity_stats()
    total_mentions = sum(s['mentions'] for s in stats.values())
    high_risk_count = sum(1 for s in stats.values() if s['risk'] == 'HIGH')
    return jsonify({
        'entities': stats,
        'total_mentions': total_mentions,
        'high_risk_count': high_risk_count,
    })

# Endpoint to add a new political entity
@entities_bp.route('/add', methods=['POST'])
def add_entity():
    payload = request.get_json() or {}
    entity = (payload.get('entity') or '').strip()
    entity_type = (payload.get('type') or '').strip()
    full_name = (payload.get('full_name') or '').strip()
    description = (payload.get('description') or '').strip()

    result = political_entity_service.add_entity(
        entity=entity,
        entity_type=entity_type,
        full_name=full_name,
        description=description,
    )

    if not result.get('ok'):
        return jsonify({'error': result.get('error', 'Failed to add entity')}), 400

    return jsonify({'message': 'Entity added successfully', 'id': result.get('id')})

# Endpoint to delete a political entity by ID
@entities_bp.route('/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_id: int):
    deleted = political_entity_service.delete_entity(entity_id)
    if not deleted:
        return jsonify({'error': 'Entity not found'}), 404
    return jsonify({'message': 'Entity deleted'})

# Health check endpoint for political entities service
@entities_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'political-entities'})
