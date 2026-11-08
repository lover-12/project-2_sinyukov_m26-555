import json
from pathlib import Path


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    """Загружает записи таблицы из JSON-файла."""
    filepath = Path("data") / f"{table_name}.json"

    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в JSON-файл."""
    filepath = Path("data") / f"{table_name}.json"
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def create_cacher():
    """Создаёт замыкание для кеширования результатов запросов."""
    cache = {}

    def cacher(key=None, value=None, clear=False):
        if clear:
            cache.clear()
            return None

        if value is not None:
            cache[key] = value

        return cache.get(key)

    return cacher


def delete_table_data(table_name):
    """Удаляет JSON-файл с записями таблицы."""
    filepath = Path("data") / f"{table_name}.json"

    if filepath.exists():
        filepath.unlink()
