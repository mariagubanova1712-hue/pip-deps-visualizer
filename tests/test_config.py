"""Тесты разбора параметров командной строки."""

import os
import tempfile
import unittest

from depviz.config import ConfigError, parse_config


class ConfigTest(unittest.TestCase):
    """Проверка параметров и обработки ошибок."""

    def setUp(self):
        """Создать временный файл тестового репозитория."""
        handle, self.repo_file = tempfile.mkstemp(suffix=".txt")
        os.close(handle)

    def tearDown(self):
        """Удалить временный файл."""
        os.remove(self.repo_file)

    def test_defaults(self):
        """Параметры по умолчанию."""
        config = parse_config(["-p", "requests"])
        self.assertEqual(config.repo, "https://pypi.org")
        self.assertEqual(config.output, "graph.svg")
        self.assertFalse(config.test_mode)

    def test_test_mode(self):
        """Тестовый режим с файлом."""
        config = parse_config(["-p", "A", "-t", "-r", self.repo_file])
        self.assertTrue(config.test_mode)

    def test_bad_package(self):
        """Недопустимые имена пакетов."""
        for name in ["", "bad name", "x!"]:
            with self.assertRaises(ConfigError):
                parse_config(["-p", name])

    def test_test_mode_needs_capitals(self):
        """В тестовом режиме имена из больших букв."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "a", "-t", "-r", self.repo_file])

    def test_bad_url(self):
        """URL без схемы http/https."""
        for url in ["pypi.org", "ftp://pypi.org"]:
            with self.assertRaises(ConfigError):
                parse_config(["-p", "requests", "-r", url])

    def test_missing_file(self):
        """Файл тестового репозитория не существует."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "A", "-t", "-r", "no_such_file.txt"])

    def test_bad_output(self):
        """Неверное имя файла изображения."""
        for output in ["graph.png", "no_dir/graph.svg"]:
            with self.assertRaises(ConfigError):
                parse_config(["-p", "requests", "-o", output])


if __name__ == "__main__":
    unittest.main()
