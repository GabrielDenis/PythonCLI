import redis
import json
import os

r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)

def get_cache(key: str):
    return r.get(key)

def set_cache(key: str, value: str, expire_seconds: int = 60):
    return r.set(key, json.dumps(value), ex=expire_seconds)