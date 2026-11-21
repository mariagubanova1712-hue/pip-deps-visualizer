"""Получение прямых зависимостей пакета из репозитория PyPI.
Используется только стандартная библиотека: JSON API репозитория
<repo>/pypi/<пакет>/json. В поле info.requires_dist лежат строки
Requires-Dist из метаданных пакета.
"""

import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

TIMEOUT_SECONDS = 30
NAME_RE = re.compile(r"[A-Za-z0-9._-]+")


class RepoError(Exception):
    """Ошибка получения данных из репозитория."""


def normalize(name):
    """Привести имя к одному виду: Typing_Extensions -> typing-extensions."""
    return name.lower().replace("_", "-").replace(".", "-")


def parse_requirement(line):
    """Вернуть имя пакета из строки зависимости или None.

    Пример: 'idna<4,>=2.5' -> 'idna'. Необязательные зависимости
    (в строке есть extra) пропускаются.
    """
    requirement = line
    if ";" in line:
        requirement, marker = line.split(";", 1)
        if "extra" in marker:
            return None
    match = NAME_RE.match(requirement.strip())
    if match is None:
        return None
    return normalize(match.group())


def fetch_json(url):
    """Скачать JSON по адресу url и вернуть его как словарь."""
    try:
        with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return json.loads(response.read())
    except HTTPError as error:
        raise RepoError(f"пакет не найден ({error.code}): {url}")
    except URLError:
        raise RepoError(f"нет доступа к репозиторию: {url}")
    except ValueError:
        raise RepoError(f"неверный ответ репозитория: {url}")


def get_direct_dependencies(repo, package):
    """Вернуть список прямых зависимостей пакета без повторов."""
    url = f"{repo}/pypi/{package}/json"
    data = fetch_json(url)
    lines = data["info"]["requires_dist"]
    if lines is None:
        lines = []
    result = []
    for line in lines:
        name = parse_requirement(line)
        if name is not None and name not in result:
            result.append(name)
    return result
