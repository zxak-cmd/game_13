"""Классы для работы с данными и таблицей лидеров (сохранение в CSV)."""

import logging
import os

from config import LEVELS, TOP_SIZE

logger = logging.getLogger(__name__)


class Record:
    """Одна запись таблицы лидеров."""

    def __init__(self, name, level, attempts, played_on):
        """Создаёт запись: имя, номер уровня, число попыток, дата."""
        self.name = name
        self.level = level
        self.attempts = attempts
        self.played_on = played_on

    def to_line(self):
        """Возвращает строку для записи в CSV."""
        return "{};{};{};{}".format(
            self.name, self.level, self.attempts, self.played_on)

    @staticmethod
    def from_line(line):
        """Создаёт запись из строки CSV.

        Возвращает None, если строка некорректна.
        """
        parts = line.strip().split(";")
        if len(parts) != 4:
            return None
        name, level_text, attempts_text, played_on = parts
        try:
            level = int(level_text)
            attempts = int(attempts_text)
        except ValueError:
            return None
        if name == "" or level not in LEVELS or attempts < 1:
            return None
        return Record(name, level, attempts, played_on)


class Leaderboard:
    """Таблица лидеров: хранит записи и работает с файлом."""

    def __init__(self, filename):
        """Создаёт пустую таблицу, связанную с файлом filename."""
        self.filename = filename
        self.records = []

    def load(self):
        """Читает записи из файла (если файла нет - таблица пустая).

        Некорректные строки пропускаются и попадают в лог.
        Возвращает False, если файл не удалось прочитать.
        """
        self.records = []
        if not os.path.exists(self.filename):
            logger.info("Файл %s не найден, таблица пуста", self.filename)
            return True
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError) as error:
            logger.error("Не удалось прочитать %s: %s",
                         self.filename, error)
            return False

        for number, line in enumerate(lines, start=1):
            if line.strip() == "":
                continue
            rec = Record.from_line(line)
            if rec is None:
                logger.warning("Пропущена строка %d в %s",
                               number, self.filename)
            else:
                self.records.append(rec)
        logger.info("Загружено записей: %d", len(self.records))
        return True

    def save(self):
        """Записывает все записи в файл. Возвращает True при успехе."""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                for rec in self.records:
                    f.write(rec.to_line() + "\n")
        except OSError as error:
            logger.error("Не удалось записать %s: %s",
                         self.filename, error)
            return False
        return True

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
        """Добавляет запись и сохраняет файл.

        Возвращает пару (is_new_record, saved): новый ли это рекорд
        и удалось ли записать файл.
        """
        old_best = self.best(record.level)
        is_new_record = (old_best is None
                         or record.attempts < old_best.attempts)
        self.records.append(record)
        saved = self.save()
        return is_new_record, saved

    def clear(self):
        """Удаляет все записи. Возвращает True, если файл обновлён."""
        self.records = []
        return self.save()
