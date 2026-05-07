"""Analysis routes — batch sentiment analysis on collected data."""

from flask import Blueprint, jsonify, request
from services.batch_analysis_service import batch_analysis_service

analysis_bp = Blueprint('analysis', __name__)

# Health check endpoint for batch analysis service
@analysis_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'batch-analysis'})

# Endpoint to run batch analysis on a collected dataset
@analysis_bp.route('/run', methods=['POST'])
def run_analysis():
    """
    Run sentiment analysis on a collected batch.

    Request: { "collection_id": "csv-20260427T..." }
    Response: Full BatchAnalysisResult with per-row results and aggregates.
    """
    try:
        payload = request.get_json() or {}
        collection_id = (payload.get('collection_id') or '').strip()

        if not collection_id:
            return jsonify({'error': 'collection_id is required'}), 400

        result = batch_analysis_service.analyze_batch(collection_id)
        return jsonify(result)

    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500

# Endpoint to list past analysis jobs (metadata only)
@analysis_bp.route('/jobs', methods=['GET'])
def list_jobs():
    """List past analysis jobs (metadata only)."""
    limit = request.args.get('limit', 20, type=int)
    jobs = batch_analysis_service.list_jobs(limit=max(1, min(limit, 100)))
    return jsonify({'jobs': jobs, 'count': len(jobs)})

# Endpoint to get full results for a past analysis job
@analysis_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id: str):
    """Retrieve full results for a past analysis job."""
    result = batch_analysis_service.get_job(job_id)
    if not result:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(result)
