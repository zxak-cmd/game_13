"""Тесты функций ввода."""

import contextlib
import io
import logging
import unittest
from unittest import mock

from config import MAX_NAME_LEN
from utils import read_int, read_name


def setUpModule():
    logging.disable(logging.CRITICAL)


def run_with_input(func, answers, *args):
    """Вызывает func с подменённым input(); возвращает (результат, вывод)."""
    out = io.StringIO()
    with mock.patch("builtins.input", side_effect=answers):
        with contextlib.redirect_stdout(out):
            result = func(*args)
    return result, out.getvalue()


class ReadIntTests(unittest.TestCase):
    """Проверка read_int."""

    def test_valid_number(self):
        result, _ = run_with_input(read_int, ["5"], "> ", 1, 10)
        self.assertEqual(result, 5)

    def test_spaces_are_stripped(self):
        result, _ = run_with_input(read_int, ["  7  "], "> ", 1, 10)
        self.assertEqual(result, 7)

    def test_boundaries(self):
        self.assertEqual(run_with_input(read_int, ["1"], "> ", 1, 10)[0], 1)
        self.assertEqual(run_with_input(read_int, ["10"], "> ", 1, 10)[0],
                         10)

    def test_not_a_number_then_valid(self):
        result, out = run_with_input(
            read_int, ["abc", "", "3.5", "4"], "> ", 1, 10)
        self.assertEqual(result, 4)
        self.assertEqual(out.count("введите целое число"), 3)

    def test_out_of_range_then_valid(self):
        result, out = run_with_input(
            read_int, ["0", "11", "-5", "2"], "> ", 1, 10)
        self.assertEqual(result, 2)
        self.assertEqual(out.count("от 1 до 10"), 3)

    def test_underscore_rejected(self):
        result, _ = run_with_input(read_int, ["1_0", "10"], "> ", 1, 100)
        self.assertEqual(result, 10)


class ReadNameTests(unittest.TestCase):
    """Проверка read_name."""

    def test_valid_name(self):
        result, _ = run_with_input(read_name, ["  Аня  "])
        self.assertEqual(result, "Аня")

    def test_empty_name_rejected(self):
        result, out = run_with_input(read_name, ["", "   ", "Боб"])
        self.assertEqual(result, "Боб")
        self.assertEqual(out.count("не может быть пустым"), 2)

    def test_semicolon_rejected(self):
        result, out = run_with_input(read_name, ["a;b", "ab"])
        self.assertEqual(result, "ab")
        self.assertIn("';'", out)

    def test_too_long_rejected(self):
        long_name = "x" * (MAX_NAME_LEN + 1)
        ok_name = "x" * MAX_NAME_LEN
        result, out = run_with_input(read_name, [long_name, ok_name])
        self.assertEqual(result, ok_name)
        self.assertIn("не длиннее", out)


if __name__ == "__main__":
    unittest.main()