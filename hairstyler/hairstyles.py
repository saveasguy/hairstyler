from typing import List

import sqlite3

from hairstyler import core


class DatabaseFetchError(Exception):
    pass


class FeaturedHairstylesDB(core.IDatabaseRepository):
    def __init__(self, db_path: str):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(
            """
            SELECT feature.name, hairstyle.name FROM match
            JOIN feature ON match.feature_id = feature.id
            JOIN hairstyle ON match.hairstyle_id = hairstyle.id
        """
        )
        if result is None:
            raise DatabaseFetchError(f"Failed to fetch database {db_path}")
        self._distributed_hairstyles = {}
        for feature, hairstyle in result:
            if not feature in self._distributed_hairstyles:
                self._distributed_hairstyles[feature] = [
                    hairstyle,
                ]
            else:
                self._distributed_hairstyles[feature].append(hairstyle)

    def filter_by_value(self, value: str) -> List[str]:
        if not value in self._distributed_hairstyles:
            raise ValueError(f"'{value}' feature doesn't exist!")
        return self._distributed_hairstyles[value]


class HairstyleImagesDB(core.IDatabaseRepository):
    def __init__(self, db_path: str):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(
            """
            SELECT hairstyle.name, hairstyle_image.base64_image FROM hairstyle
            JOIN hairstyle_image ON hairstyle_image.hairstyle_id = hairstyle.id
        """
        )
        if result is None:
            raise DatabaseFetchError(f"Failed to fetch database {db_path}")
        self._hairstyle_images = {}
        for hairstyle, base64_image in result:
            if not hairstyle in self._hairstyle_images:
                self._hairstyle_images[hairstyle] = [
                    base64_image,
                ]

    def filter_by_value(self, value: str) -> List[str]:
        if not value in self._hairstyle_images:
            raise ValueError(f"'{value}' hairstyle doesn't exist!")
        return self._hairstyle_images[value]
