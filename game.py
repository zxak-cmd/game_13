"""Игровая логика: выбор сложности и процесс угадывания."""

import logging
import random
from datetime import date

from config import LEVELS
from storage import Record
from utils import read_int, read_name


def choose_level():
    """Показывает уровни сложности и возвращает выбранный номер."""
    print("\nУровни сложности:")
    for number in LEVELS:
        title, low, high, tries = LEVELS[number]
        print("  {}. {} (от {} до {}, попыток: {})".format(
            number, title, low, high, tries))
    return read_int("Выберите уровень: ", 1, len(LEVELS))


def play_round(level):
    """Проводит один раунд игры на выбранном уровне.

    Возвращает число потраченных попыток или 0, если игрок проиграл.
    """
    title, low, high, max_tries = LEVELS[level]
    secret = random.randint(low, high)
    logging.info("Начата игра. Уровень: %s, диапазон: [%d, %d], "
                 "попыток: %d", title, low, high, max_tries)
    print("\nЯ загадал число от {} до {}. У вас {} попыток.".format(
        low, high, max_tries))

    for attempt in range(1, max_tries + 1):
        guess = read_int("Попытка {}/{}: ".format(attempt, max_tries),
                         low, high)
        if guess == secret:
            print("Верно! Вы угадали, попыток потрачено: {}.".format(
                attempt))
            logging.info("Победа! Угадано число %d с попытки %d.",
                         secret, attempt)
            return attempt
        if guess < secret:
            print("Загаданное число БОЛЬШЕ.")
        else:
            print("Загаданное число МЕНЬШЕ.")

    print("Попытки закончились. Было загадано число {}.".format(secret))
    logging.info("Проигрыш. Загаданное число было: %d.", secret)
    return 0


def start_game(board):
    """Пункт меню «Новая игра»: раунд и сохранение результата."""
    name = read_name()
    level = choose_level()
    attempts = play_round(level)
    if attempts == 0:
        return

    record = Record(name, level, attempts, str(date.today()))
    is_new, saved = board.add(record)
    if not saved:
        print("Внимание: результат не удалось сохранить в файл.")
    if is_new:
        print("*** НОВЫЙ РЕКОРД на уровне «{}»! ***".format(
            LEVELS[level][0]))
        logging.info("Новый рекорд: %s, уровень %d, попыток %d.",
                     name, level, attempts)
    else:
        best = board.best(level)
        print("Результат сохранён. Рекорд уровня: {} ({}).".format(
            best.attempts, best.name))