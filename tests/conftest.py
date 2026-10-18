import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def sample_path():
    from config import Config
    return Config.SAMPLE_FILE


@pytest.fixture(scope="session")
def analysis(sample_path):
    from services.recommendation import recommendation_engine as e
    return e.load(sample_path)


@pytest.fixture()
def client(tmp_path):
    from app import create_app
    from config import Config

    class T(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(tmp_path / "t.db")
        UPLOAD_FOLDER = str(tmp_path / "uploads")

    app = create_app(T)
    return app.test_client()


@pytest.fixture()
def logged_in(client):
    client.post("/register", data=dict(name="T", email="t@x.com", password="password123", confirm_password="password123"))
    client.post("/login", data=dict(email="t@x.com", password="password123"))
    return client
