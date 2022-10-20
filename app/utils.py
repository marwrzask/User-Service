from app.schemas import User
from redis import Redis

redis_data_cache = Redis(host="redis", port=6379, db=0)


def delete_cache(user: User):
    """ util to delete existing user cache - all get option"""
    none_request = redis_data_cache.keys("*(id=None,nickname=None,email=None)")
    id_request = redis_data_cache.keys(f"*(id=*{user.id}*)")
    nickname_request = redis_data_cache.keys(f"nickname={user.nickname}*")
    email_request = redis_data_cache.keys(f"email={user.email}*")

    if none_request:
        redis_data_cache.delete(*none_request)
    if id_request:
        redis_data_cache.delete(*id_request)
    if nickname_request:
        redis_data_cache.delete(*nickname_request)
    if email_request:
        redis_data_cache.delete(*email_request)

