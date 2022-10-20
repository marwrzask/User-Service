from app.utils import redis_data_cache


def test_redis_connection():
    assert redis_data_cache is not None
