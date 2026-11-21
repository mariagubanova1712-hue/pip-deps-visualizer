"""Получение прямых зависимостей пакета из репозитория PyPI.

Используется только стандартная библиотека: JSON API репозитория
(/pypi/<пакет>/json) и файл METADATA из wheel-пакета.
"""

import json
import re
from email.parser import Parser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

TIMEOUT_SECONDS = 30
HTTP_NOT_FOUND = 404
USER_AGENT = "depviz/1.0"
METADATA_KEYS = ("core-metadata", "data-dist-info-metadata")
NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


class RepoError(Exception):
    """Ошибка получения данных из репозитория."""


def normalize(name):
    """Привести имя пакета к стандартному виду (PEP 503)."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_requirement(line):
    """Вернуть имя пакета из строки Requires-Dist.

    Необязательные зависимости (маркер extra) пропускаются: возвращается
    None.
    """
    requirement, _, marker = line.partition(";")
    if "extra" in marker:
        return None
    match = NAME_RE.match(requirement)
    return normalize(match.group(1)) if match else None


def parse_metadata(text):
    """Вернуть строки Requires-Dist из текста файла METADATA."""
    message = Parser().parsestr(text)
    return message.get_all("Requires-Dist") or []


def fetch(url):
    """Скачать содержимое по URL и вернуть его как текст."""
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8")
    except HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            raise RepoError(f"не найдено в репозитории: {url}") from error
        raise RepoError(f"ошибка HTTP {error.code}: {url}") from error
    except (URLError, OSError) as error:
        raise RepoError(f"нет доступа к {url}: {error}") from error


def find_metadata_url(release_files):
    """Найти URL файла METADATA у wheel-пакета последней версии."""
    for item in release_files:
        is_wheel = item.get("packagetype") == "bdist_wheel"
        has_meta = any(item.get(key) for key in METADATA_KEYS)
        if is_wheel and has_meta:
            return item["url"] + ".metadata"
    return None


def get_direct_dependencies(repo, package):
    """Вернуть список прямых зависимостей пакета (без повторов)."""
    url = f"{repo.rstrip('/')}/pypi/{package}/json"
    try:
        data = json.loads(fetch(url))
    except json.JSONDecodeError as error:
        raise RepoError(f"неверный ответ репозитория: {url}") from error
    metadata_url = find_metadata_url(data.get("urls", []))
    if metadata_url:
        lines = parse_metadata(fetch(metadata_url))
    else:
        lines = data.get("info", {}).get("requires_dist") or []
    names = [parse_requirement(line) for line in lines]
    return list(dict.fromkeys(name for name in names if name))
