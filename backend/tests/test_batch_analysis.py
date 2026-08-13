"""Tests for the batch analysis pipeline (Phase 1 DB-backed jobs, Phase 2
language routing) and the job_id path-traversal fix (Phase 0/1).
"""
import io

from services.batch_analysis_service import batch_analysis_service


def _upload_csv(client, content: bytes, filename: str = 'test.csv'):
    return client.post(
        '/api/social/upload-csv',
        data={'file': (io.BytesIO(content), filename)},
        content_type='multipart/form-data',
    )


def test_upload_and_run_analysis_end_to_end(client, stub_pipelines):
    upload = _upload_csv(client, b'text\nThe BDP government made progress this year\n')
    assert upload.status_code == 200
    collection_id = upload.get_json()['collection_id']

    run = client.post('/api/analysis/run', json={'collection_id': collection_id})
    assert run.status_code == 200
    body = run.get_json()
    assert body['aggregate']['total_rows'] == 1
    assert body['rows'][0]['sentiment'] == 'positive'
    assert body['rows'][0]['language_detected'] == 'English'


def test_batch_analysis_language_distribution_reflects_mixed_input(client, stub_pipelines):
    csv_content = (
        b'text\n'
        b'The BDP government made progress this year\n'
        b'Mmuso o dira molemo thata mo bathong ba Botswana\n'
    )
    upload = _upload_csv(client, csv_content, 'mixed.csv')
    collection_id = upload.get_json()['collection_id']

    run = client.post('/api/analysis/run', json={'collection_id': collection_id})
    body = run.get_json()
    lang_dist = body['aggregate']['language_distribution']
    assert lang_dist.get('English', 0) >= 1
    assert any(k in lang_dist for k in ('Setswana', 'Setswana-English'))


def test_run_analysis_missing_collection_returns_400(client, stub_pipelines):
    response = client.post('/api/analysis/run', json={'collection_id': 'does-not-exist'})
    assert response.status_code == 400


def test_run_analysis_missing_collection_id_returns_400(client):
    response = client.post('/api/analysis/run', json={})
    assert response.status_code == 400


def test_list_and_get_job_round_trip(client, stub_pipelines):
    upload = _upload_csv(client, b'text\nSome political commentary here\n')
    collection_id = upload.get_json()['collection_id']
    run = client.post('/api/analysis/run', json={'collection_id': collection_id})
    job_id = run.get_json()['job_id']

    jobs = client.get('/api/analysis/jobs')
    assert jobs.status_code == 200
    assert any(j['job_id'] == job_id for j in jobs.get_json()['jobs'])

    fetched = client.get(f'/api/analysis/jobs/{job_id}')
    assert fetched.status_code == 200
    assert fetched.get_json()['job_id'] == job_id


def test_get_job_returns_404_for_missing_job(client):
    response = client.get('/api/analysis/jobs/does-not-exist')
    assert response.status_code == 404


def test_get_job_rejects_path_traversal_job_id(app):
    """Regression test: get_job() used to build a filesystem path directly
    from the job_id — confirm it can't be used to read arbitrary files, and
    that a job lookup with such an id simply returns None (not an error,
    not a file's contents).
    """
    with app.app_context():
        assert batch_analysis_service.get_job('../../../../etc/passwd') is None
        assert batch_analysis_service.get_job('..%2f..%2fetc%2fpasswd') is None
        assert batch_analysis_service.get_job('') is None


def test_get_job_route_rejects_path_traversal(client):
    response = client.get('/api/analysis/jobs/..%2f..%2fetc%2fpasswd')
    assert response.status_code in (404, 400)
