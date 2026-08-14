"""Tests for political entity CRUD and text-matching extraction (Phase 1)."""
from services.political_entity_service import political_entity_service


def test_seeded_entities_present(app):
    with app.app_context():
        entities = political_entity_service.list_entities()
    assert len(entities) >= 12
    names = {e['entity'] for e in entities}
    assert 'BDP' in names
    assert 'Masisi' in names


def test_extract_entities_matches_known_names(app):
    with app.app_context():
        matches = political_entity_service.extract_entities(
            "Masisi met with BDP officials in Gaborone today"
        )
    matched_names = {m['entity'] for m in matches}
    assert 'Masisi' in matched_names
    assert 'BDP' in matched_names
    assert 'Gaborone' in matched_names


def test_extract_entities_uses_prefetched_list_without_requery(app):
    """extract_entities(text, entities=...) should not hit the DB again —
    this is the N+1 fix from Phase 1; pass a deliberately wrong/empty list
    and confirm it's honored instead of silently re-querying.
    """
    with app.app_context():
        matches = political_entity_service.extract_entities("Masisi spoke today", entities=[])
    assert matches == []


def test_extract_entities_no_match(app):
    with app.app_context():
        matches = political_entity_service.extract_entities("The weather is nice today")
    assert matches == []


def test_add_and_delete_entity(app):
    with app.app_context():
        result = political_entity_service.add_entity('TestEntity', 'party', 'Test Entity Full', 'desc')
        assert result['ok'] is True
        entity_id = result['id']

        entities = political_entity_service.list_entities('party')
        assert any(e['id'] == entity_id for e in entities)

        deleted = political_entity_service.delete_entity(entity_id)
        assert deleted is True
        assert political_entity_service.delete_entity(entity_id) is False


def test_add_duplicate_entity_rejected(app):
    with app.app_context():
        first = political_entity_service.add_entity('DupeEntity', 'party')
        assert first['ok'] is True
        second = political_entity_service.add_entity('DupeEntity', 'party')
        assert second['ok'] is False


def test_entities_list_route(client):
    response = client.get('/api/entities/')
    assert response.status_code == 200
    assert response.get_json()['count'] >= 12


def test_entities_add_route_requires_fields(client):
    response = client.post('/api/entities/add', json={'entity': 'NoType'})
    assert response.status_code == 400


def test_entities_delete_route_404_for_missing(client):
    response = client.delete('/api/entities/999999')
    assert response.status_code == 404


def test_bulk_entity_stats_computed_from_real_analysis_jobs(app, stub_pipelines):
    """Phase 4: Entities.tsx used to show hardcoded 0/'N/A'/'LOW' for every
    entity regardless of data. Confirm the aggregation is now real.
    """
    import io
    client = app.test_client()

    csv_content = (
        b'text\n'
        b'Masisi praised the new policy\n'
    )
    upload = client.post(
        '/api/social/upload-csv',
        data={'file': (io.BytesIO(csv_content), 't.csv')},
        content_type='multipart/form-data',
    )
    collection_id = upload.get_json()['collection_id']
    client.post('/api/analysis/run', json={'collection_id': collection_id})

    response = client.get('/api/entities/stats')
    assert response.status_code == 200
    body = response.get_json()
    assert body['total_mentions'] >= 1
    assert 'Masisi' in body['entities']
    assert body['entities']['Masisi']['mentions'] == 1
    assert body['entities']['Masisi']['risk'] in ('LOW', 'MED', 'HIGH')


def test_bulk_entity_stats_empty_when_no_jobs(app):
    response = app.test_client().get('/api/entities/stats')
    assert response.status_code == 200
    body = response.get_json()
    assert body['entities'] == {}
    assert body['total_mentions'] == 0
    assert body['high_risk_count'] == 0
