import time
from functools import wraps


def handle_db_errors(func):
    """Обрабатывает ошибки при работе с базой данных."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.")
        except KeyError as error:
            print(f"Ошибка: Не найден ключ {error}.")
        except ValueError as error:
            print(f"Ошибка: {error}")

    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение перед опасной операцией."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(f'Вы уверены, что хотите "{action_name}"? [y/n]: ')

            if answer.lower() == "y":
                return func(*args, **kwargs)

            print("Операция отменена.")
            return None

        return wrapper

    return decorator


def log_time(func):
    """Измеряет и выводит время выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            execution_time = time.monotonic() - start_time
            print(
                f"Функция {func.__name__} выполнилась за {execution_time:.6f} секунды."
            )

    return wrapper


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
