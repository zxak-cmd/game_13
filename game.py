"""Игровая логика: выбор сложности и процесс угадывания."""

import random
import logging
from datetime import date
from config import LEVELS
from storage import Record
from utils import read_int, read_name


def choose_level():
    """Показывает уровни сложности и возвращает выбранный номер."""
    print("\nУровни сложности:")
    for number in LEVELS:
        title, low, high, tries = LEVELS[number]
        print("  {}. {} (от {} до {}, попыток: {})".format(number, title, low, high, tries))
    return read_int("Выберите уровень: ", 1, len(LEVELS))


def play_round(level):
    """Один раунд игры. Возвращает число потраченных попыток или 0, если игрок проиграл."""
    title, low, high, max_tries = LEVELS[level]
    secret = random.randint(low, high)
    
    # Логируем начало игры
    logging.info(f"Начата игра. Уровень: {title}, диапазон: [{low}, {high}], попыток: {max_tries}")
    print("\nЯ загадал число от {} до {}. У вас {} попыток.".format(low, high, max_tries))

    for attempt in range(1, max_tries + 1):
        guess = read_int("Попытка {}/{}: ".format(attempt, max_tries), low, high)
        if guess == secret:
            print("Верно! Вы угадали, попыток потрачено: {}.".format(attempt))
            logging.info(f"Победа! Угадано число {secret} с {attempt} попытки.")
            return attempt
        if guess < secret:
            print("Загаданное число БОЛЬШЕ.")
        else:
            print("Загаданное число МЕНЬШЕ.")

    print("Попытки закончились. Было загадано число {}.".format(secret))
    logging.info(f"Проигрыш. Загаданное число было: {secret}.")
    return 0


def start_game(board):
    """Пункт меню «Новая игра»."""
    name = read_name()
    level = choose_level()
    attempts = play_round(level)
    
    if attempts == 0:
        return

    record = Record(name, level, attempts, str(date.today()))
    
    if board.add(record):
        print("*** НОВЫЙ РЕКОРД на уровне «{}»! ***".format(LEVELS[level][0]))
        logging.info(f"Новый рекорд: {name}, уровень {level}, попыток {attempts}.")
    else:
        best = board.best(level)
        print("Результат сохранён. Рекорд уровня: {} ({}).".format(best.attempts, best.name))