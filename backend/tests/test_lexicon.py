"""Tests for the DB-backed lexicon (Phase 1): CRUD through both the service
layer and the HTTP routes, and the seed data itself.
"""
from services.lexicon_manager import lexicon_manager


def test_seeded_lexicon_has_no_cross_category_duplicates(app):
    with app.app_context():
        lexicon_manager.refresh()
        seen = {}
        duplicates = []
        for category, words in lexicon_manager.lexicon.items():
            if category == 'metadata':
                continue
            for word in words:
                if word in seen:
                    duplicates.append((word, seen[word], category))
                seen[word] = category
    assert duplicates == []


def test_seeded_lexicon_word_count_matches_stats(app):
    with app.app_context():
        lexicon_manager.refresh()
        assert lexicon_manager.count_total_words() > 0
        assert lexicon_manager.lexicon['metadata']['total_words'] == lexicon_manager.count_total_words()


def test_add_word_persists_and_is_searchable(app):
    with app.app_context():
        ok = lexicon_manager.add_word('testword123', 'positive', 'a test word', intensity='medium')
        assert ok is True

        results = lexicon_manager.search_words('testword123')
        assert len(results) == 1
        assert results[0]['category'] == 'positive'
        assert results[0]['details']['meaning'] == 'a test word'


def test_add_word_twice_updates_in_place_not_duplicates(app):
    with app.app_context():
        lexicon_manager.add_word('dupeword', 'positive', 'first meaning')
        before_count = lexicon_manager.count_total_words()

        lexicon_manager.add_word('dupeword', 'positive', 'updated meaning')
        after_count = lexicon_manager.count_total_words()

        assert after_count == before_count
        results = lexicon_manager.search_words('dupeword')
        assert results[0]['details']['meaning'] == 'updated meaning'


def test_remove_word(app):
    with app.app_context():
        lexicon_manager.add_word('removeme', 'negative', 'temp')
        assert lexicon_manager.remove_word('removeme', 'negative') is True
        assert lexicon_manager.search_words('removeme') == []


def test_lexicon_stats_route(client):
    response = client.get('/api/lexicon/stats')
    assert response.status_code == 200
    body = response.get_json()
    assert body['total_words'] > 0
    assert 'positive' in body['category_stats']


def test_lexicon_add_route_requires_fields(client):
    response = client.post('/api/lexicon/add', json={'word': 'onlyword'})
    assert response.status_code == 400


def test_lexicon_add_route_end_to_end(client):
    response = client.post('/api/lexicon/add', json={
        'word': 'routetestword', 'category': 'positive', 'meaning': 'added via route'
    })
    assert response.status_code == 200

    search = client.get('/api/lexicon/search?q=routetestword')
    assert search.status_code == 200
    assert search.get_json()['count'] == 1
