"""Tests for language-aware sentiment routing (Phase 2): English text should
use the English model, Setswana/code-switched text should use the
multilingual model blended with lexicon polarity.
"""
from services.lexicon_service import lexicon_service


def test_detect_language_pure_english(app, stub_pipelines):
    with app.app_context():
        lexicon_service.refresh_lexicon()
        language, code_switching, details = stub_pipelines.detect_language(
            "The government made great progress this year", lexicon_service.legacy_lexicon
        )
    assert language == "English"
    assert code_switching is False
    assert details['setswana_ratio'] == 0.0


def test_detect_language_setswana_heavy(app, stub_pipelines):
    with app.app_context():
        lexicon_service.refresh_lexicon()
        language, code_switching, details = stub_pipelines.detect_language(
            "Mmuso o dira molemo thata mo bathong, re a itumela", lexicon_service.legacy_lexicon
        )
    assert language in ("Setswana", "Setswana-English")
    assert details['setswana_ratio'] > 0.1


def test_detect_language_empty_text(app, stub_pipelines):
    with app.app_context():
        lexicon_service.refresh_lexicon()
        language, code_switching, details = stub_pipelines.detect_language("", lexicon_service.legacy_lexicon)
    assert language == "unknown"
    assert details['total_words'] == 0


def test_analyze_sentiment_routes_english_to_english_model(app, stub_pipelines):
    with app.app_context():
        lexicon_service.refresh_lexicon()
        sentiment, confidence, details = stub_pipelines.analyze_sentiment(
            "The government made great progress this year",
            lexicon_service.legacy_lexicon,
            use_code_switching=True,
        )
    assert details['language_detected'] == 'English'
    assert 'roberta' in details['model'].lower()
    assert sentiment == 'positive'  # from the stubbed English pipeline
    assert confidence == 0.85


def test_analyze_sentiment_routes_setswana_to_multilingual_model(app, stub_pipelines):
    with app.app_context():
        lexicon_service.refresh_lexicon()
        sentiment, confidence, details = stub_pipelines.analyze_sentiment(
            "Mmuso o dira molemo thata mo bathong ba Botswana, re a itumela ka kagiso",
            lexicon_service.legacy_lexicon,
            use_code_switching=True,
        )
    assert details['language_detected'] in ('Setswana', 'Setswana-English')
    assert 'xlm-roberta' in details['model'].lower()
    # lexicon_polarity should be present since this path blends with the lexicon
    assert 'lexicon_polarity' in details


def test_analyze_sentiment_use_code_switching_false_forces_english_path(app, stub_pipelines):
    with app.app_context():
        lexicon_service.refresh_lexicon()
        sentiment, confidence, details = stub_pipelines.analyze_sentiment(
            "Mmuso o dira molemo thata mo bathong",
            lexicon_service.legacy_lexicon,
            use_code_switching=False,
        )
    assert details['language_detected'] == 'English'
    assert 'roberta' in details['model'].lower()
    assert 'xlm' not in details['model'].lower()


def test_analyze_batch_with_routing_splits_by_language(app, stub_pipelines):
    with app.app_context():
        lexicon_service.refresh_lexicon()
        texts = [
            "The BDP government made progress this year",
            "Mmuso o dira molemo thata mo bathong ba Botswana",
        ]
        results = stub_pipelines.analyze_batch_with_routing(
            texts, lexicon_service.legacy_lexicon, use_code_switching=True
        )
    assert len(results) == 2
    english_details = results[0][2]
    setswana_details = results[1][2]
    assert english_details['language_detected'] == 'English'
    assert setswana_details['language_detected'] in ('Setswana', 'Setswana-English')
    assert english_details['model'] != setswana_details['model']


def test_analyze_endpoint_surfaces_language_detected(client, stub_pipelines):
    response = client.post('/api/sentiment/analyze', json={'text': 'The reform plan is terrible'})
    assert response.status_code == 200
    body = response.get_json()
    assert body['language_detected'] == 'English'
    assert 'code_switching' in body
    assert body['sentiment'] == 'positive'  # stubbed pipeline always returns positive/0.85


def test_analyze_endpoint_rejects_empty_text(client, stub_pipelines):
    response = client.post('/api/sentiment/analyze', json={'text': '   '})
    assert response.status_code == 400
