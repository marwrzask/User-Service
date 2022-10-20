from app.main import engine


def test_db_connection():
    assert engine.connect() is not None
