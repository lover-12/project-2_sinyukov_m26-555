from primitive_db.constants import ALLOWED_TYPES
from primitive_db.decorators import (
    confirm_action,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data


@handle_db_errors
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


@handle_db_errors
@confirm_action("удалить таблицу")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    columns = metadata[table_name]
    data = load_table_data(table_name)

    user_columns = {
        name: column_type for name, column_type in columns.items() if name != "ID"
    }

    if len(values) != len(user_columns):
        raise ValueError("Неверное количество значений.")

    record = {}

    for (column_name, column_type), value in zip(
        user_columns.items(), values, strict=True
    ):
        if column_type == "int":
            try:
                converted_value = int(value)
            except ValueError as error:
                raise ValueError(
                    f"Столбец {column_name} должен иметь тип int."
                ) from error

        elif column_type == "bool":
            if value.lower() not in ("true", "false"):
                raise ValueError(f"Столбец {column_name} должен иметь тип bool.")
            converted_value = value.lower() == "true"

        else:
            converted_value = value

        record[column_name] = converted_value

    record_id = max((row["ID"] for row in data), default=0) + 1
    record = {"ID": record_id, **record}

    data.append(record)
    return data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает все записи или записи, подходящие под условие."""
    if where_clause is None:
        return table_data

    return [
        record
        for record in table_data
        if all(record.get(column) == value for column, value in where_clause.items())
    ]


@handle_db_errors
def update(table_data, set_clause, where_clause, columns):
    """Обновляет записи с проверкой типов по схеме таблицы."""
    for column, value in set_clause.items():
        if column == "ID":
            raise ValueError("Изменение столбца ID запрещено.")

        if column not in columns:
            raise ValueError(f"Столбец {column} не существует.")

        expected_type = columns[column]

        if type(value).__name__ != expected_type:
            raise ValueError(f"Неверный тип данных для столбца {column}.")

    for record in table_data:
        if all(record.get(column) == value for column, value in where_clause.items()):
            record.update(set_clause)

    return table_data


@handle_db_errors
@confirm_action("удалить записи")
def delete(table_data, where_clause):
    """Удаляет записи, соответствующие условию."""
    return [
        record
        for record in table_data
        if not all(
            record.get(column) == value for column, value in where_clause.items()
        )
    ]
