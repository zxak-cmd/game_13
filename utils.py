"""Утилиты: проверка ввода и настройка логирования."""

import logging

from config import LOG_FILE, MAX_NAME_LEN


def setup_logging():
    """Настраивает запись логов в файл game.log."""
    root = logging.getLogger()
    for old_handler in root.handlers[:]:
        root.removeHandler(old_handler)
        old_handler.close()
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"))
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    logging.info("=== Запуск программы ===")


def read_int(prompt, low, high):
    """Запрашивает целое число из диапазона [low, high].

    Повторяет запрос, пока ввод не станет корректным.
    """
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
            if "_" in text:  # int("1_0") вернул бы 10
                raise ValueError(text)
        except ValueError:
            print("Ошибка: введите целое число.")
            logging.warning("Некорректный ввод (не число): %r", text)
            continue
        if value < low or value > high:
            print("Ошибка: число должно быть от {} до {}.".format(
                low, high))
            logging.warning("Число %d вне диапазона [%d, %d]",
                            value, low, high)
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
            logging.warning("Попытка ввода имени с ';': %r", name)
        elif len(name) > MAX_NAME_LEN:
            print("Ошибка: имя не длиннее {} символов.".format(
                MAX_NAME_LEN))
            logging.warning("Слишком длинное имя: %r", name)
        else:
            return name