"""Главный модуль: меню программы и точка входа."""

import logging

from config import LEVELS, RECORDS_FILE, TOP_SIZE
from game import choose_level, start_game
from storage import Leaderboard
from utils import read_int, setup_logging


def show_leaderboard(board):
    """Пункт меню «Таблица лидеров»."""
    level = choose_level()
    items = board.top(level)
    print("\nТоп-{} — уровень «{}»".format(TOP_SIZE, LEVELS[level][0]))
    if len(items) == 0:
        print("Пока нет результатов.")
        return
    print("{:<4}{:<22}{:<9}{}".format("№", "Имя", "Попытки", "Дата"))
    for place, rec in enumerate(items, start=1):
        print("{:<4}{:<22}{:<9}{}".format(
            place, rec.name, rec.attempts, rec.played_on))


def clear_records(board):
    """Пункт меню «Сбросить рекорды» (с подтверждением)."""
    answer = input("Удалить все рекорды? (да/нет): ").strip().lower()
    if answer != "да":
        print("Отменено.")
    elif board.clear():
        print("Рекорды удалены.")
        logging.info("Пользователь очистил таблицу лидеров.")
    else:
        print("Не удалось обновить файл рекордов.")


def print_menu():
    """Выводит главное меню."""
    print("\n=== УГАДАЙ ЧИСЛО ===")
    print("1. Новая игра")
    print("2. Таблица лидеров")
    print("3. Сбросить рекорды")
    print("0. Выход")


def run_menu(board):
    """Главный цикл меню."""
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
            return


def main():
    """Точка входа в программу."""
    setup_logging()
    board = Leaderboard(RECORDS_FILE)
    if not board.load():
        print("Не удалось прочитать файл рекордов, "
              "начинаем с пустой таблицы.")
    try:
        run_menu(board)
    except (KeyboardInterrupt, EOFError):
        print("\nВвод прерван. До свидания!")
        logging.info("Ввод прерван пользователем")
    logging.info("=== Завершение программы ===")


if __name__ == "__main__":
    main()