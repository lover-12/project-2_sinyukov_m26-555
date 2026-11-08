
ALLOWED_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    """Создаёт таблицу и добавляет её структуру в метаданные."""
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    if not columns:
        raise ValueError("Необходимо указать хотя бы один столбец.")

    parsed_columns = {}

    for column in columns:
        parts = column.split(":")

        if len(parts) != 2 or not all(parts):
            raise ValueError(f"Некорректный столбец: {column}")

        column_name, column_type = parts

        if column_type not in ALLOWED_TYPES:
            raise ValueError(f"Неподдерживаемый тип данных: {column_type}")

        if column_name in parsed_columns:
            raise ValueError(f"Столбец {column_name} уже существует.")

        parsed_columns[column_name] = column_type

    if "ID" not in parsed_columns:
        parsed_columns = {"ID": "int", **parsed_columns}

    metadata[table_name] = parsed_columns
    return metadata



def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    return metadata
