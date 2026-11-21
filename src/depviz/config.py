"""Разбор и проверка параметров командной строки."""

import argparse
import os
import re


DEFAULT_REPO = "https://pypi.org"
DEFAULT_OUTPUT = "graph.svg"
PACKAGE_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
TEST_PACKAGE_RE = re.compile(r"^[A-Z]+$")


class ConfigError(Exception):
    """Ошибка в параметрах, заданных пользователем."""


class Config:
    """Настройки приложения, заданные пользователем."""

    def __init__(self, package, repo, test_mode, output, load_order):
        """Сохранить все параметры."""
        self.package = package
        self.repo = repo
        self.test_mode = test_mode
        self.output = output
        self.load_order = load_order


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
    if name == "":
        raise ConfigError("имя пакета не может быть пустым")
    if test_mode:
        if not TEST_PACKAGE_RE.match(name):
            raise ConfigError(
                "в тестовом режиме пакет называется большими "
                "латинскими буквами, получено: " + name
            )
    elif not PACKAGE_NAME_RE.match(name):
        raise ConfigError("недопустимое имя пакета: " + name)


def check_repo(repo, test_mode):
    """Проверить URL репозитория или путь к тестовому файлу."""
    if test_mode:
        if not os.path.isfile(repo):
            raise ConfigError("файл тестового репозитория не найден: " + repo)
    elif not repo.startswith(("http://", "https://")):
        raise ConfigError(
            "URL репозитория должен начинаться с http:// или https://: "
            + repo
        )


def check_output(output):
    """Проверить имя файла для изображения графа."""
    if not output.endswith(".svg"):
        raise ConfigError(
            "файл изображения должен иметь расширение .svg: " + output
        )
    folder = os.path.dirname(output)
    if folder != "" and not os.path.isdir(folder):
        raise ConfigError(
            "папка для файла изображения не существует: " + folder
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
