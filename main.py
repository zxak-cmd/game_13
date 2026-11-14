"""Главный модуль: меню программы и точка входа."""

import logging
from config import RECORDS_FILE, LEVELS, TOP_SIZE  # Импортируем всё нужное из конфига
from storage import Leaderboard
from utils import setup_logging, read_int
from game import start_game, choose_level


def show_leaderboard(board):
    """Пункт меню «Таблица лидеров»."""
    level = choose_level()
    items = board.top(level)
    # Теперь используем переменную TOP_SIZE, а не хардкод "10"
    print("\nТоп-{} — уровень «{}»".format(TOP_SIZE, LEVELS[level][0]))
    
    if len(items) == 0:
        print("Пока нет результатов.")
        return
    print("{:<4}{:<22}{:<9}{}".format("№", "Имя", "Попытки", "Дата"))
    for place, rec in enumerate(items, start=1):
        print("{:<4}{:<22}{:<9}{}".format(place, rec.name, rec.attempts, rec.played_on))


def clear_records(board):
    """Пункт меню «Сбросить рекорды» (с подтверждением)."""
    answer = input("Удалить все рекорды? (да/нет): ").strip().lower()
    if answer == "да":
        board.clear()
        print("Рекорды удалены.")
        logging.info("Пользователь очистил таблицу лидеров.")
    else:
        print("Отменено.")


def print_menu():
    print("\n=== УГАДАЙ ЧИСЛО ===")
    print("1. Новая игра")
    print("2. Таблица лидеров")
    print("3. Сбросить рекорды")
    print("0. Выход")


def main():
    # Настраиваем логирование при запуске
    setup_logging()
    
    board = Leaderboard(RECORDS_FILE)
    board.load()

    while True:
        print_menu()
        choice = read_int("Ваш выбор: ", 0, 3)
        if choice == 1:
            start_game(board)
        elif choice == 2:
            show_leaderboard(board)
        elif choice == 3:
            clear_records(board)
        else:
            print("До свидания!")
            logging.info("=== Завершение программы ===")
            break


if __name__ == "__main__":
    main()