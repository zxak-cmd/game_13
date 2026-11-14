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