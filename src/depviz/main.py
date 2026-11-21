"""Главный сценарий работы приложения."""

import sys

from depviz.config import ConfigError, parse_config
from depviz.pypi import RepoError, get_direct_dependencies

EXIT_OK = 0
EXIT_ERROR = 1


def main(argv=None):
    """Запустить приложение и вернуть код завершения."""
    try:
        config = parse_config(argv)
        deps = get_direct_dependencies(config.repo, config.package)
    except (ConfigError, RepoError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    print(f"Прямые зависимости {config.package}:")
    for name in deps:
        print(f"  {name}")
    if not deps:
        print("  (нет)")
    return EXIT_OK
