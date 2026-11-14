"""Курсовая работа №1. Тема 13: игра «Угадай число»
с сохранением рекордов и таблицей лидеров.

Консольное приложение. Данные хранятся в текстовом файле CSV.
"""

import os
import random
from datetime import date

RECORDS_FILE = "records.csv"
TOP_SIZE = 10

# Уровни сложности: название -> (минимум, максимум, число попыток)
LEVELS = {
    1: ("Лёгкий", 1, 50, 10),
    2: ("Средний", 1, 100, 7),
    3: ("Сложный", 1, 500, 9),
}


class Record:
    """Одна запись таблицы лидеров."""

    def __init__(self, name, level, attempts, played_on):
        self.name = name
        self.level = level          # номер уровня сложности (ключ LEVELS)
        self.attempts = attempts    # сколько попыток потрачено
        self.played_on = played_on  # дата в формате ГГГГ-ММ-ДД

    def to_line(self):
        """Строка для записи в CSV."""
        return "{};{};{};{}".format(self.name, self.level, self.attempts, self.played_on)

    @staticmethod
    def from_line(line):
        """Создаёт запись из строки CSV. Возвращает None, если строка некорректна."""
        parts = line.strip().split(";")
        if len(parts) != 4:
            return None
        name, level, attempts, played_on = parts
        if not (level.isdigit() and attempts.isdigit()):
            return None
        if int(level) not in LEVELS:
            return None
        return Record(name, int(level), int(attempts), played_on)


    class Leaderboard:
    """Таблица лидеров: хранит записи и работает с файлом."""

    def __init__(self, filename):
        self.filename = filename
        self.records = []

    def load(self):
        """Читает записи из файла (если файла нет - таблица пустая)."""
        self.records = []
        if not os.path.exists(self.filename):
            return
        with open(self.filename, "r", encoding="utf-8") as f:
            for line in f:
                rec = Record.from_line(line)
                if rec is not None:
                    self.records.append(rec)

    def save(self):
        """Записывает все записи в файл."""
        with open(self.filename, "w", encoding="utf-8") as f:
            for rec in self.records:
                f.write(rec.to_line() + "\n")

    def top(self, level):
        """Лучшие записи уровня: меньше попыток - выше место."""
        items = [r for r in self.records if r.level == level]
        items.sort(key=lambda r: (r.attempts, r.played_on))
        return items[:TOP_SIZE]

    def best(self, level):
        """Текущий рекорд уровня (запись) или None."""
        items = self.top(level)
        if len(items) == 0:
            return None
        return items[0]

    def add(self, record):
        """Добавляет запись и сохраняет файл. Возвращает True, если это новый рекорд."""
        old_best = self.best(record.level)
        is_new_record = old_best is None or record.attempts < old_best.attempts
        self.records.append(record)
        self.save()
        return is_new_record

    def clear(self):
        """Удаляет все записи."""
        self.records = []
        self.save()


        # ---------- Ввод и проверка данных ----------

def read_int(prompt, low, high):
    """Запрашивает целое число в диапазоне [low, high] до тех пор, пока ввод не станет корректным."""
    while True:
        text = input(prompt).strip()
        negative = text.startswith("-")
        digits = text[1:] if negative else text
        if not digits.isdigit():
            print("Ошибка: введите целое число.")
            continue
        value = int(text)
        if value < low or value > high:
            print("Ошибка: число должно быть от {} до {}.".format(low, high))
            continue
        return value


def read_name():
    """Запрашивает имя игрока (непустое, без символа ';')."""
    while True:
        name = input("Введите ваше имя: ").strip()
        if name == "":
            print("Ошибка: имя не может быть пустым.")
        elif ";" in name:
            print("Ошибка: символ ';' в имени недопустим.")
        elif len(name) > 20:
            print("Ошибка: имя не длиннее 20 символов.")
        else:
            return name


        # ---------- Игра ----------

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
    print("\nЯ загадал число от {} до {}. У вас {} попыток.".format(low, high, max_tries))

    for attempt in range(1, max_tries + 1):
        guess = read_int("Попытка {}/{}: ".format(attempt, max_tries), low, high)
        if guess == secret:
            print("Верно! Вы угадали, попыток потрачено: {}.".format(attempt))
            return attempt
        if guess < secret:
            print("Загаданное число БОЛЬШЕ.")
        else:
            print("Загаданное число МЕНЬШЕ.")

    print("Попытки закончились. Было загадано число {}.".format(secret))
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
    else:
        best = board.best(level)
        print("Результат сохранён. Рекорд уровня: {} ({}).".format(best.attempts, best.name))