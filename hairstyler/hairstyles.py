import json
import pathlib
from typing import List

import redis

from hairstyler import core


class DatabaseFetchError(Exception):
    pass


class RedisDB(core.IDatabaseRepository):
    def __init__(self, host: str, port: int, hairstlye_data: pathlib.Path):
        self._db = redis.Redis(host=host, port=port)
        with open(hairstlye_data) as json_data:
            hairstyles_data = json.load(json_data)
        for feature, hairstyles in hairstyles_data["featured_hairstyles"].items():
            self._db.lpush(feature, *hairstyles)
        for hairstyle, image in hairstyles_data["hairstyle_images"].items():
            self._db.set(hairstyle, image)

    def get_featured_hairstyles(self, feature: str) -> List[str]:
        return [result.decode("utf-8") for result in self._db.lrange(feature, 0, -1)]

    def get_hairstyle_image(self, hairstyle: str) -> str:
        return self._db.get(hairstyle).decode("utf-8")
