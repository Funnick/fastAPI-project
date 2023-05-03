from .connection import redis_client


def save_redis(key: str, data: int):
    redis_client.set(key, data)


def exist_redis(key: str):
    return redis_client.exists(key) == 1


def get_redis(key: str):
    return redis_client.get(key)
