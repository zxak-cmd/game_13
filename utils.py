"""Утилиты: проверка ввода и настройка логирования."""

import logging
from config import LOG_FILE


def setup_logging():
    """Настраивает запись логов в файл game.log."""
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
        force=True  # Перезаписываем настройки, если они уже были заданы
    )
    logging.info("=== Запуск программы ===")


def read_int(prompt, low, high):
    """Запрашивает целое число в диапазоне [low, high] до тех пор, пока ввод не станет корректным."""
    while True:
        text = input(prompt).strip()
        negative = text.startswith("-")
        digits = text[1:] if negative else text
        if not digits.isdigit():
            print("Ошибка: введите целое число.")
            logging.warning(f"Некорректный ввод (не число): '{text}'")
            continue
        value = int(text)
        if value < low or value > high:
            print("Ошибка: число должно быть от {} до {}.".format(low, high))
            logging.warning(f"Число {value} вне диапазона [{low}, {high}]")
            continue
        return value


def read_name():
    """Запрашивает имя игрока (непустое, без символа ';')."""
    while True:
        name = input("Введите ваше имя: ").strip()
        if name == "":
            print("Ошибка: имя не может быть пустым.")
            logging.warning("Попытка ввода пустого имени")
        elif ";" in name:
            print("Ошибка: символ ';' в имени недопустим.")
            logging.warning(f"Попытка ввода имени с ';': '{name}'")
        elif len(name) > 20:
            print("Ошибка: имя не длиннее 20 символов.")
            logging.warning(f"Слишком длинное имя: '{name}'")
        else:
            return name