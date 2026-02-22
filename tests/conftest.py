import pytest
from backend import app


@pytest.fixture()
def client():
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def song():
    song = {
        "id": 999,
        "title": "Test song title",
        "lyrics": "Test lyrics for the song."
    }
    return dict(song)