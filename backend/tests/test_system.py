"""Tests for system routes, including the Phase 0 fix for POST /api/system/event
500ing on an empty/missing JSON body.
"""


def test_health_route(client):
    response = client.get('/api/system/health')
    assert response.status_code == 200
    body = response.get_json()
    assert 'resources' in body
    assert 'cpu_usage' in body['resources']


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
