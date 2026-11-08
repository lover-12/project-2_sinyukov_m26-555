def parse_value(value):
    """Преобразует значение из команды в тип Python."""
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Некорректное значение: {value}") from None


def parse_condition(condition):
    """Преобразует условие 'столбец = значение' в словарь."""
    parts = condition.split("=", maxsplit=1)

    if len(parts) != 2:
        raise ValueError("Условие должно содержать знак '='.")

    column_name = parts[0].strip()
    value = parts[1].strip()

    if not column_name or not value:
        raise ValueError("Необходимо указать столбец и значение.")

    return {column_name: parse_value(value)}
