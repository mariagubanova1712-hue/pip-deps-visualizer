"""Тестовый репозиторий: описание графа пакетов в текстовом файле.

Формат файла — по строке на пакет:

    A: B C
    B: C
    C:

Пакеты называются большими латинскими буквами. Пустые строки и строки,
начинающиеся с #, пропускаются. Пакет без строки считается пакетом без
зависимостей.
"""

import re

NAME_RE = re.compile(r"^[A-Z]+$")


class TestRepoError(Exception):
    """Ошибка в файле тестового репозитория."""


def check_name(name, line_number):
    """Проверить имя пакета в строке файла."""
    if not NAME_RE.match(name):
        raise TestRepoError(
            f"строка {line_number}: пакет должен называться большими "
            f"латинскими буквами: {name!r}"
        )


def parse_line(line, line_number):
    """Разобрать строку вида 'A: B C' и вернуть (пакет, [зависимости])."""
    name, colon, rest = line.partition(":")
    if not colon:
        raise TestRepoError(f"строка {line_number}: нет двоеточия: {line!r}")
    name = name.strip()
    deps = rest.split()
    for item in [name] + deps:
        check_name(item, line_number)
    return name, deps


def parse_test_repo(text):
    """Разобрать текст тестового репозитория в словарь пакетов."""
    repo = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name, deps = parse_line(line, number)
        if name in repo:
            raise TestRepoError(f"строка {number}: пакет {name} уже описан")
        repo[name] = deps
    return repo


def load_test_repo(path):
    """Прочитать файл тестового репозитория."""
    try:
        with open(path, encoding="utf-8") as handle:
            return parse_test_repo(handle.read())
    except OSError as error:
        raise TestRepoError(f"не удалось прочитать {path}: {error}") from error
