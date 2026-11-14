"""Модульные тесты для игры «Угадай число»."""

import unittest
import os
from storage import Record, Leaderboard


class TestRecord(unittest.TestCase):
    def test_to_line(self):
        """Проверка сериализации записи в строку."""
        rec = Record("Иван", 1, 5, "2026-05-15")
        self.assertEqual(rec.to_line(), "Иван;1;5;2026-05-15")

    def test_from_line_valid(self):
        """Проверка десериализации корректной строки."""
        line = "Анна;2;3;2026-05-16"
        rec = Record.from_line(line)
        self.assertIsNotNone(rec)
        self.assertEqual(rec.name, "Анна")
        self.assertEqual(rec.level, 2)
        self.assertEqual(rec.attempts, 3)

    def test_from_line_invalid(self):
        """Проверка, что некорректная строка возвращает None."""
        self.assertIsNone(Record.from_line("плохая строка"))
        self.assertIsNone(Record.from_line("Имя;4;5;2026-01-01")) # несуществующий уровень


class TestLeaderboard(unittest.TestCase):
    def setUp(self):
        """Создаём временный файл перед каждым тестом."""
        self.test_file = "test_records.csv"
        self.board = Leaderboard(self.test_file)

    def tearDown(self):
        """Удаляем временный файл после каждого теста."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_and_load(self):
        """Проверка добавления записи и её загрузки из файла."""
        rec = Record("Тест", 1, 4, "2026-01-01")
        self.board.add(rec)
        
        # Создаём новый объект, чтобы проверить чтение с диска
        new_board = Leaderboard(self.test_file)
        new_board.load()
        self.assertEqual(len(new_board.records), 1)
        self.assertEqual(new_board.records[0].name, "Тест")

    def test_best_record(self):
        """Проверка, что лучшая запись (с меньшим числом попыток) находится верно."""
        self.board.add(Record("Игрок1", 2, 5, "2026-01-01"))
        self.board.add(Record("Игрок2", 2, 3, "2026-01-02"))
        self.board.add(Record("Игрок3", 2, 4, "2026-01-03"))
        
        best = self.board.best(2)
        self.assertEqual(best.name, "Игрок2")
        self.assertEqual(best.attempts, 3)


if __name__ == "__main__":
    unittest.main()