"""Разбор и проверка параметров командной строки."""

import argparse
import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

DEFAULT_REPO = "https://pypi.org"
DEFAULT_OUTPUT = "graph.svg"
OUTPUT_EXTENSION = ".svg"
URL_SCHEMES = ("http", "https")
PACKAGE_NAME_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$")
TEST_PACKAGE_RE = re.compile(r"^[A-Z]+$")


class ConfigError(Exception):
    """Ошибка в параметрах, заданных пользователем."""


@dataclass
class Config:
    """Настройки приложения, заданные пользователем."""

    package: str
    repo: str
    test_mode: bool
    output: str
    load_order: bool = False

    def as_pairs(self):
        """Вернуть параметры списком пар (ключ, значение)."""
        return [
            ("package", self.package),
            ("repo", self.repo),
            ("test_mode", str(self.test_mode)),
            ("output", self.output),
            ("load_order", str(self.load_order)),
        ]


def build_parser():
    """Создать парсер опций командной строки."""
    parser = argparse.ArgumentParser(
        prog="depviz",
        description="Визуализатор графа зависимостей пакетов Python.",
    )
    parser.add_argument(
        "-p", "--package", required=True,
        help="имя анализируемого пакета",
    )
    parser.add_argument(
        "-r", "--repo", default=DEFAULT_REPO,
        help="URL репозитория или путь к файлу тестового репозитория",
    )
    parser.add_argument(
        "-t", "--test-mode", action="store_true",
        help="режим работы с тестовым репозиторием (файл)",
    )
    parser.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT,
        help="имя файла с изображением графа (.svg)",
    )
    parser.add_argument(
        "-l", "--load-order", action="store_true",
        help="вывести порядок загрузки зависимостей",
    )
    return parser


def check_package(name, test_mode):
    """Проверить имя пакета."""
    if not name.strip():
        raise ConfigError("имя пакета не может быть пустым")
    if test_mode and not TEST_PACKAGE_RE.match(name):
        raise ConfigError(
            f"в тестовом режиме пакет называется большими "
            f"латинскими буквами, получено: {name!r}"
        )
    if not test_mode and not PACKAGE_NAME_RE.match(name):
        raise ConfigError(f"недопустимое имя пакета: {name!r}")


def check_repo(repo, test_mode):
    """Проверить URL репозитория или путь к тестовому файлу."""
    if not repo.strip():
        raise ConfigError("репозиторий не может быть пустым")
    if test_mode:
        if not os.path.isfile(repo):
            raise ConfigError(f"файл тестового репозитория не найден: {repo}")
        return
    parts = urlparse(repo)
    if parts.scheme not in URL_SCHEMES or not parts.netloc:
        raise ConfigError(
            f"URL репозитория должен начинаться с http:// или https://: {repo}"
        )


def check_output(output):
    """Проверить имя файла для изображения графа."""
    if not output.lower().endswith(OUTPUT_EXTENSION):
        raise ConfigError(
            f"файл изображения должен иметь расширение .svg: {output}"
        )
    folder = os.path.dirname(output) or "."
    if not os.path.isdir(folder):
        raise ConfigError(
            f"папка для файла изображения не существует: {folder}"
        )


def parse_config(argv=None):
    """Разобрать опции, проверить их и вернуть Config."""
    args = build_parser().parse_args(argv)
    check_package(args.package, args.test_mode)
    check_repo(args.repo, args.test_mode)
    check_output(args.output)
    return Config(
        args.package, args.repo, args.test_mode, args.output,
        args.load_order,
    )
