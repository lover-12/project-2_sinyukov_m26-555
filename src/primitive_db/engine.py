import shlex

import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = "db_meta.json"


def print_help():
    """Выводит список доступных команд базы данных."""
    print("Доступные команды:")
    print("create_table <имя> <столбец:тип> ... - создать таблицу")
    print("drop_table <имя> - удалить таблицу")
    print("list_tables - показать список таблиц")
    print("help - показать справку")
    print("exit - выйти из режима базы данных")


def run():
    """Запускает режим работы с базой данных."""
    print("***Процесс работы с таблицей***")

    while True:
        command = prompt.string("Введите команду: ")

        try:
            parts = shlex.split(command)
        except ValueError as error:
            print(f"Ошибка: {error}")
            continue

        if not parts:
            continue

        action, *args = parts

        try:
            if action == "exit":
                break

            elif action == "help":
                print_help()

            elif action == "create_table":
                if len(args) < 2:
                    print("Ошибка: укажите имя таблицы и столбцы.")
                    continue

                metadata = load_metadata(METADATA_FILE)
                create_table(metadata, args[0], args[1:])
                save_metadata(METADATA_FILE, metadata)
                print(f'Таблица "{args[0]}" успешно создана.')

            elif action == "drop_table":
                if len(args) != 1:
                    print("Ошибка: укажите имя таблицы.")
                    continue

                metadata = load_metadata(METADATA_FILE)
                drop_table(metadata, args[0])
                save_metadata(METADATA_FILE, metadata)
                print(f'Таблица "{args[0]}" успешно удалена.')

            elif action == "list_tables":
                if args:
                    print("Ошибка: команда list_tables не принимает аргументы.")
                    continue

                metadata = load_metadata(METADATA_FILE)

                if not metadata:
                    print("Таблиц пока нет.")
                else:
                    for table_name in metadata:
                        print(f"- {table_name}")

            else:
                print("Неизвестная команда. Введите help.")

        except ValueError as error:
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
