"""Главный сценарий работы приложения."""

import sys

from depviz.config import ConfigError, parse_config
from depviz.graph import build_graph
from depviz.pypi import RepoError, get_direct_dependencies, normalize
from depviz.testrepo import TestRepoError, load_test_repo

EXIT_OK = 0
EXIT_ERROR = 1
APP_ERRORS = (ConfigError, RepoError, TestRepoError)


def make_source(config):
    """Вернуть корневой пакет и функцию получения прямых зависимостей."""
    if config.test_mode:
        repo = load_test_repo(config.repo)
        if config.package not in repo:
            raise TestRepoError(
                f"пакет {config.package} не описан в {config.repo}"
            )
        return config.package, lambda name: repo.get(name, [])
    root = normalize(config.package)
    return root, lambda name: get_direct_dependencies(config.repo, name)


def print_graph(root, graph, cycles):
    """Вывести граф зависимостей и найденные циклы."""
    print(f"Граф зависимостей {root} (пакетов: {len(graph)}):")
    for name, deps in graph.items():
        print(f"  {name} -> {', '.join(deps) if deps else '(нет)'}")
    if cycles:
        print("Циклические зависимости:")
        for cycle in cycles:
            print("  " + " -> ".join(cycle))


def main(argv=None):
    """Запустить приложение и вернуть код завершения."""
    try:
        config = parse_config(argv)
        root, get_deps = make_source(config)
        graph, cycles = build_graph(root, get_deps)
    except APP_ERRORS as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    print_graph(root, graph, cycles)
    return EXIT_OK
