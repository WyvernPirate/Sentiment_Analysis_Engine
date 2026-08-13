"""Tests for system routes, including the Phase 0 fix for POST /api/system/event
500ing on an empty/missing JSON body.
"""


def test_health_route(client):
    response = client.get('/api/system/health')
    assert response.status_code == 200
    body = response.get_json()
    assert 'resources' in body
    assert 'cpu_usage' in body['resources']

    # Phase 4: the service matrix now runs real checks instead of four
    # hardcoded "PASS" entries — confirm DATABASE and LEXICON (both real
    # in the test fixture) actually report PASS, not just that the key exists.
    service_status = {s['name']: s['status'] for s in body['services']}
    assert service_status['DATABASE'] == 'PASS'
    assert service_status['LEXICON'] == 'PASS'
    assert body['status'] in ('healthy', 'degraded')


def test_event_route_with_empty_body_returns_400_not_500(client):
    response = client.post('/api/system/event')
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_event_route_with_valid_body_logs_successfully(client):
    response = client.post('/api/system/event', json={'level': 'INFO', 'message': 'test event'})
    assert response.status_code == 200
    assert response.get_json()['status'] == 'logged'


def test_event_route_missing_message_returns_400(client):
    response = client.post('/api/system/event', json={'level': 'INFO'})
    assert response.status_code == 400


def test_logs_route(client):
    response = client.get('/api/system/logs')
    assert response.status_code == 200
    body = response.get_json()
    assert 'logs' in body
    assert 'count' in body
