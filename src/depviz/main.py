"""Главный сценарий работы приложения."""

import sys

from depviz.config import ConfigError, parse_config
from depviz.dot import VizError, save_svg, to_dot
from depviz.graph import build_graph, load_order
from depviz.pypi import RepoError, get_direct_dependencies, normalize
from depviz.testrepo import TestRepoError, load_test_repo

EXIT_OK = 0
EXIT_ERROR = 1
APP_ERRORS = (ConfigError, RepoError, TestRepoError, VizError)


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


def print_cycles(cycles):
    """Вывести найденные циклы в поток ошибок."""
    for cycle in cycles:
        print("Цикл: " + " -> ".join(cycle), file=sys.stderr)


def visualize(config, root, graph, cycles):
    """Вывести граф на языке DOT и сохранить изображение SVG."""
    dot_text = to_dot(graph, root, cycles)
    print(dot_text, end="")
    save_svg(dot_text, config.output)
    print_cycles(cycles)
    print(f"Изображение сохранено: {config.output}", file=sys.stderr)


def print_load_order(root, graph, cycles):
    """Вывести порядок загрузки зависимостей пакета."""
    print(f"Порядок загрузки {root}:")
    for number, name in enumerate(load_order(graph, root), start=1):
        print(f"  {number}. {name}")
    if cycles:
        print("Внимание: есть циклы, порядок пакетов в цикле условный:")
        for cycle in cycles:
            print("  " + " -> ".join(cycle))


def main(argv=None):
    """Запустить приложение и вернуть код завершения."""
    try:
        config = parse_config(argv)
        root, get_deps = make_source(config)
        graph, cycles = build_graph(root, get_deps)
        if config.load_order:
            print_load_order(root, graph, cycles)
        else:
            visualize(config, root, graph, cycles)
    except APP_ERRORS as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK
