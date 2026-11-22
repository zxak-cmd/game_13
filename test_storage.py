"""Тесты модуля storage: классы Record и Leaderboard."""

import logging
import os
import tempfile
import unittest

from config import TOP_SIZE
from storage import Leaderboard, Record


def setUpModule():
    logging.disable(logging.CRITICAL)


class RecordTests(unittest.TestCase):
    """Проверка преобразования записи в строку CSV и обратно."""

    def test_to_line(self):
        record = Record("Аня", 2, 5, "2026-11-01")
        self.assertEqual(record.to_line(), "Аня;2;5;2026-11-01")

    def test_from_line_roundtrip(self):
        record = Record.from_line("Аня;2;5;2026-11-01\n")
        self.assertEqual(record.name, "Аня")
        self.assertEqual(record.level, 2)
        self.assertEqual(record.attempts, 5)
        self.assertEqual(record.played_on, "2026-11-01")

    def test_from_line_wrong_parts_count(self):
        self.assertIsNone(Record.from_line("Аня;2;5"))
        self.assertIsNone(Record.from_line("Аня;2;5;2026-11-01;лишнее"))
        self.assertIsNone(Record.from_line(""))

    def test_from_line_not_numbers(self):
        self.assertIsNone(Record.from_line("Аня;два;5;2026-11-01"))
        self.assertIsNone(Record.from_line("Аня;2;пять;2026-11-01"))

    def test_from_line_unknown_level(self):
        self.assertIsNone(Record.from_line("Аня;9;5;2026-11-01"))
        self.assertIsNone(Record.from_line("Аня;0;5;2026-11-01"))

    def test_from_line_bad_attempts(self):
        self.assertIsNone(Record.from_line("Аня;2;0;2026-11-01"))
        self.assertIsNone(Record.from_line("Аня;2;-3;2026-11-01"))

    def test_from_line_empty_name(self):
        self.assertIsNone(Record.from_line(";2;5;2026-11-01"))


class LeaderboardTests(unittest.TestCase):
    """Проверка загрузки, сохранения и подсчёта рекордов."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "records.csv")
        self.board = Leaderboard(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def write_file(self, text):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(text)

    # --- загрузка ---

    def test_load_missing_file(self):
        self.assertTrue(self.board.load())
        self.assertEqual(self.board.records, [])

    def test_load_empty_file(self):
        self.write_file("")
        self.assertTrue(self.board.load())
        self.assertEqual(self.board.records, [])

    def test_load_skips_bad_lines(self):
        self.write_file("мусор\nАня;2;3;2026-11-01\n\nx;9;1;d\n")
        self.assertTrue(self.board.load())
        self.assertEqual(len(self.board.records), 1)
        self.assertEqual(self.board.records[0].name, "Аня")

    def test_load_unreadable_path(self):
        board = Leaderboard(self.tmp.name)  # каталог вместо файла
        self.assertFalse(board.load())
        self.assertEqual(board.records, [])

    def test_load_bad_encoding(self):
        with open(self.path, "wb") as file:
            file.write(b"\xff\xfe\xfa;1;1;d\n")
        self.assertFalse(self.board.load())

    # --- сохранение ---

    def test_save_and_load_roundtrip(self):
        self.board.records = [
            Record("Аня", 1, 4, "2026-11-01"),
            Record("Боб", 3, 8, "2026-11-02"),
        ]
        self.assertTrue(self.board.save())
        other = Leaderboard(self.path)
        self.assertTrue(other.load())
        self.assertEqual([r.to_line() for r in other.records],
                         [r.to_line() for r in self.board.records])

    def test_save_failure(self):
        bad_path = os.path.join(self.tmp.name, "нет_папки", "r.csv")
        board = Leaderboard(bad_path)
        self.assertFalse(board.save())

    # --- топ и рекорд ---

    def test_top_filters_by_level_and_sorts(self):
        self.board.records = [
            Record("A", 1, 5, "2026-11-03"),
            Record("B", 1, 2, "2026-11-02"),
            Record("C", 2, 1, "2026-11-01"),
            Record("D", 1, 2, "2026-11-01"),
        ]
        names = [r.name for r in self.board.top(1)]
        self.assertEqual(names, ["D", "B", "A"])
        self.assertEqual([r.name for r in self.board.top(2)], ["C"])
        self.assertEqual(self.board.top(3), [])

    def test_top_is_limited(self):
        self.board.records = [
            Record("P{}".format(i), 1, i + 1, "2026-11-01")
            for i in range(TOP_SIZE + 5)
        ]
        top = self.board.top(1)
        self.assertEqual(len(top), TOP_SIZE)
        self.assertEqual(top[0].attempts, 1)

    def test_best(self):
        self.assertIsNone(self.board.best(1))
        self.board.records = [Record("A", 1, 6, "d"), Record("B", 1, 3, "d")]
        self.assertEqual(self.board.best(1).name, "B")

    # --- добавление и сброс ---

    def test_add_first_record_is_new(self):
        is_new, saved = self.board.add(Record("A", 1, 5, "2026-11-01"))
        self.assertTrue(is_new)
        self.assertTrue(saved)
        self.assertTrue(os.path.exists(self.path))

    def test_add_worse_and_equal_are_not_new(self):
        self.board.add(Record("A", 1, 5, "2026-11-01"))
        self.assertFalse(self.board.add(Record("B", 1, 7, "d"))[0])
        self.assertFalse(self.board.add(Record("C", 1, 5, "d"))[0])

    def test_add_better_is_new(self):
        self.board.add(Record("A", 1, 5, "2026-11-01"))
        self.assertTrue(self.board.add(Record("B", 1, 3, "d"))[0])

    def test_add_record_other_level_is_new(self):
        self.board.add(Record("A", 1, 2, "2026-11-01"))
        self.assertTrue(self.board.add(Record("B", 2, 9, "d"))[0])

    def test_add_saves_to_file(self):
        self.board.add(Record("A", 1, 5, "2026-11-01"))
        with open(self.path, encoding="utf-8") as file:
            self.assertEqual(file.read(), "A;1;5;2026-11-01\n")

    def test_clear(self):
        self.board.add(Record("A", 1, 5, "2026-11-01"))
        self.assertTrue(self.board.clear())
        self.assertEqual(self.board.records, [])
        with open(self.path, encoding="utf-8") as file:
            self.assertEqual(file.read(), "")


if __name__ == "__main__":
    unittest.main()