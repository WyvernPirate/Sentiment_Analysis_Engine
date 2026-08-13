"""Shared pytest fixtures for the backend test suite.

Notably: the `app`/`client` fixtures point at a throwaway sqlite file per
test (not the real dev DB under backend/data/), and `stub_pipelines` swaps
in deterministic fake transformer pipelines so the suite runs without
downloading/loading real HuggingFace models.
"""
import pytest

from app import create_app
from config import Config
from extensions import db
from models import seed_defaults_if_empty


@pytest.fixture()
def app(tmp_path):
    flask_app = create_app(Config)
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{tmp_path / 'test.db'}"
    flask_app.config['TESTING'] = True

    with flask_app.app_context():
        db.create_all()
        seed_defaults_if_empty()

        from services.lexicon_manager import lexicon_manager
        lexicon_manager.refresh()

        yield flask_app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def _make_fake_pipeline(label: str, score: float):
    """A callable matching the shape of a HuggingFace sentiment pipeline:
    single text -> [{'label', 'score'}], list of texts -> one dict per text,
    top_k=None -> all-labels list (only the primary label/score matter here).
    """
    def fake(inputs, batch_size=None, top_k=None):
        if isinstance(inputs, list):
            return [{'label': label, 'score': score} for _ in inputs]
        return [{'label': label, 'score': score}]
    return fake


@pytest.fixture()
def stub_pipelines(app):
    """Stub both the English and multilingual pipelines with deterministic
    fakes. English -> positive/0.85, multilingual -> negative/0.6, so tests
    can assert on which pipeline actually got used.
    """
    from services.sentiment_service import sentiment_service

    original_pipeline = sentiment_service._pipeline
    original_multilingual = sentiment_service._multilingual_pipeline

    sentiment_service._pipeline = _make_fake_pipeline('positive', 0.85)
    sentiment_service._multilingual_pipeline = _make_fake_pipeline('negative', 0.6)

    yield sentiment_service

    sentiment_service._pipeline = original_pipeline
    sentiment_service._multilingual_pipeline = original_multilingual
