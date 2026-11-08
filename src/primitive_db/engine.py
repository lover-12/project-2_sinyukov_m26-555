import re
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
)
from primitive_db.parser import parse_condition, parse_value
from primitive_db.utils import (
    create_cacher,
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

METADATA_FILE = "db_meta.json"


select_cache = create_cacher()


def print_help():
    """Выводит справку по командам базы данных."""
    print("***Операции с данными***")
    print("create_table <имя> <столбец:тип> ... - создать таблицу")
    print("drop_table <имя> - удалить таблицу")
    print("list_tables - показать все таблицы")
    print("insert into <таблица> values (<значения>) - добавить запись")
    print("select from <таблица> [where <условие>] - показать записи")
    print("update <таблица> set <условие> where <условие> - обновить")
    print("delete from <таблица> where <условие> - удалить записи")
    print("info <таблица> - информация о таблице")
    print("help - справочная информация")
    print("exit - выход")


def parse_values(text):
    """Разбирает значения для команды insert."""
    if not text.strip():
        return []

    lexer = shlex.shlex(text, posix=False)
    lexer.whitespace = ","
    lexer.whitespace_split = True
    lexer.commenters = ""

    return [str(parse_value(value.strip())) for value in lexer]


def print_records(records, columns):
    """Выводит записи в формате PrettyTable."""
    table = PrettyTable()
    table.field_names = list(columns)

    for record in records:
        table.add_row([record.get(column) for column in columns])

    print(table)


def validate_where(where_clause, columns):
    """Проверяет существование столбцов в условии where."""
    if where_clause is None:
        return

    for column in where_clause:
        if column not in columns:
            raise ValueError(f"Столбец {column} не существует.")


def handle_crud(command, metadata):
    """Обрабатывает команды работы с записями."""
    match = re.fullmatch(
        r"insert\s+into\s+(\w+)\s+values\s*\((.*)\)",
        command,
        re.IGNORECASE,
    )

    if match:
        table_name, values_text = match.groups()
        values = parse_values(values_text)
        data = insert(metadata, table_name, values)

        if data is None:
            return True

        save_table_data(table_name, data)
        select_cache(clear=True)
        print(f"Запись с ID={data[-1]['ID']} успешно добавлена.")
        return True

    match = re.fullmatch(
        r"select\s+from\s+(\w+)(?:\s+where\s+(.+))?",
        command,
        re.IGNORECASE,
    )

    if match:
        table_name, condition = match.groups()
        if table_name not in metadata:
            raise ValueError(f'Таблица "{table_name}" не существует.')

        where_clause = parse_condition(condition) if condition else None
        validate_where(where_clause, metadata[table_name])
        cache_key = (table_name, condition)

        records = select_cache(cache_key)

        if records is None:
            data = load_table_data(table_name)
            records = select(data, where_clause)

            if records is None:
                return True

            select_cache(cache_key, records)

        print_records(records, metadata[table_name])
        return True

    match = re.fullmatch(
        r"update\s+(\w+)\s+set\s+(.+?)\s+where\s+(.+)",
        command,
        re.IGNORECASE,
    )

    if match:
        table_name, set_text, where_text = match.groups()
        if table_name not in metadata:
            raise ValueError(f'Таблица "{table_name}" не существует.')

        set_clause = parse_condition(set_text)
        where_clause = parse_condition(where_text)
        validate_where(where_clause, metadata[table_name])
        data = load_table_data(table_name)
        updated_data = update(
            data,
            set_clause,
            where_clause,
            metadata[table_name],
        )

        if updated_data is None:
            return True

        save_table_data(table_name, updated_data)
        select_cache(clear=True)
        print(f'Записи таблицы "{table_name}" успешно обновлены.')
        return True

    match = re.fullmatch(
        r"delete\s+from\s+(\w+)\s+where\s+(.+)",
        command,
        re.IGNORECASE,
    )

    if match:
        table_name, where_text = match.groups()
        if table_name not in metadata:
            raise ValueError(f'Таблица "{table_name}" не существует.')

        where_clause = parse_condition(where_text)
        validate_where(where_clause, metadata[table_name])
        data = load_table_data(table_name)
        updated_data = delete(data, where_clause)

        if updated_data is None:
            return True

        save_table_data(table_name, updated_data)
        select_cache(clear=True)
        print(f'Записи таблицы "{table_name}" успешно удалены.')
        return True

    match = re.fullmatch(r"info\s+(\w+)", command, re.IGNORECASE)

    if match:
        table_name = match.group(1)
        if table_name not in metadata:
            raise ValueError(f'Таблица "{table_name}" не существует.')

        columns = metadata[table_name]
        data = load_table_data(table_name)

        print(f"Таблица: {table_name}")
        print(
            "Столбцы: "
            + ", ".join(
                f"{name}:{column_type}" for name, column_type in columns.items()
            )
        )
        print(f"Количество записей: {len(data)}")
        return True

    return False


def run():
    """Запускает режим работы с базой данных."""
    print("***Процесс работы с таблицей***")
    print_help()

    while True:
        command = prompt.string("Введите команду: ").strip()

        if not command:
            continue

        try:
            metadata = load_metadata(METADATA_FILE)

            if handle_crud(command, metadata):
                continue

            parts = shlex.split(command)
            action, *args = parts

            if action == "exit":
                break

            elif action == "help":
                print_help()

            elif action == "create_table":
                if len(args) < 2:
                    print("Ошибка: укажите имя таблицы и столбцы.")
                    continue

                result = create_table(metadata, args[0], args[1:])

                if result is None:
                    continue

                save_metadata(METADATA_FILE, result)
                columns = metadata[args[0]]
                description = ", ".join(
                    f"{name}:{column_type}" for name, column_type in columns.items()
                )
                print(f'Таблица "{args[0]}" успешно создана.')
                print(f"Столбцы: {description}")

            elif action == "drop_table":
                if len(args) != 1:
                    print("Ошибка: укажите имя таблицы.")
                    continue

                result = drop_table(metadata, args[0])

                if result is None:
                    continue

                save_metadata(METADATA_FILE, result)
                delete_table_data(args[0])
                select_cache(clear=True)
                print(f'Таблица "{args[0]}" успешно удалена.')

            elif action == "list_tables":
                if args:
                    print("Ошибка: команда не принимает аргументы.")
                    continue

                if not metadata:
                    print("Таблиц пока нет.")
                else:
                    for table_name in metadata:
                        print(f"- {table_name}")

            else:
                print("Неизвестная команда. Введите help.")

        except (ValueError, KeyError, FileNotFoundError) as error:
            print(f"Ошибка: {error}")


def welcome():
    """Запускает главное меню программы."""
    print("Первая попытка запустить проект!")

    while True:
        print("<command> database - работать с базой данных")
        print("<command> help - справочная информация")
        print("<command> exit - выйти из программы")

        command = prompt.string("Введите команду: ").strip()

        if command == "exit":
            break
        elif command == "help":
            continue
        elif command == "database":
            run()
        else:
            print("Неизвестная команда. Введите help.")
