"""Тесты игровой логики."""

import contextlib
import io
import logging
import os
import tempfile
import unittest
from unittest import mock

import game
from storage import Leaderboard


def setUpModule():
    logging.disable(logging.CRITICAL)


def play(level, secret, answers):
    """Запускает play_round с загаданным числом secret и вводом answers."""
    out = io.StringIO()
    with mock.patch("game.random.randint", return_value=secret):
        with mock.patch("builtins.input", side_effect=answers):
            with contextlib.redirect_stdout(out):
                result = game.play_round(level)
    return result, out.getvalue()


class PlayRoundTests(unittest.TestCase):
    """Проверка одного раунда."""

    def test_win_on_first_try(self):
        result, out = play(2, 42, ["42"])
        self.assertEqual(result, 1)
        self.assertIn("Верно", out)

    def test_win_after_hints(self):
        result, out = play(2, 42, ["10", "90", "42"])
        self.assertEqual(result, 3)
        self.assertIn("БОЛЬШЕ", out)
        self.assertIn("МЕНЬШЕ", out)

    def test_win_on_last_attempt(self):
        # уровень 2: 7 попыток
        result, _ = play(2, 50, ["1"] * 6 + ["50"])
        self.assertEqual(result, 7)

    def test_lose_returns_zero(self):
        result, out = play(2, 50, ["1"] * 7)
        self.assertEqual(result, 0)
        self.assertIn("Было загадано число 50", out)

    def test_invalid_input_does_not_spend_attempt(self):
        result, _ = play(2, 42, ["abc", "500", "42"])
        self.assertEqual(result, 1)

    def test_attempt_limits_by_level(self):
        self.assertEqual(play(1, 5, ["1"] * 10)[0], 0)  # 10 попыток
        self.assertEqual(play(3, 5, ["1"] * 9)[0], 0)   # 9 попыток


class StartGameTests(unittest.TestCase):
    """Проверка сохранения результата после игры."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "records.csv")
        self.board = Leaderboard(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def run_game(self, answers, secret=42):
        out = io.StringIO()
        with mock.patch("game.random.randint", return_value=secret):
            with mock.patch("builtins.input", side_effect=answers):
                with contextlib.redirect_stdout(out):
                    game.start_game(self.board)
        return out.getvalue()

    def test_win_saves_record(self):
        out = self.run_game(["Аня", "2", "42"])
        self.assertEqual(len(self.board.records), 1)
        record = self.board.records[0]
        self.assertEqual((record.name, record.level, record.attempts),
                         ("Аня", 2, 1))
        self.assertIn("НОВЫЙ РЕКОРД", out)

    def test_loss_does_not_save(self):
        self.run_game(["Аня", "2"] + ["1"] * 7, secret=50)
        self.assertEqual(self.board.records, [])
        self.assertFalse(os.path.exists(self.path))

    def test_second_worse_result_is_not_record(self):
        self.run_game(["Аня", "2", "42"])
        out = self.run_game(["Боб", "2", "1", "42"])
        self.assertEqual(len(self.board.records), 2)
        self.assertNotIn("НОВЫЙ РЕКОРД", out)
        self.assertIn("Рекорд уровня: 1 (Аня)", out)


if __name__ == "__main__":
    unittest.main()