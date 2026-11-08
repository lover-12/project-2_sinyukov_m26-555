import prompt


def welcome():
    """Запускает простой цикл обработки команд пользователя."""
    print("Первая попытка запустить проект!")
    print("***")

    while True:
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")

        command = prompt.string("Введите команду: ")

        if command == "exit":
            break
        elif command == "help":
            continue