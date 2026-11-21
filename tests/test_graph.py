"""Тесты построения графа и тестового репозитория."""

import os
import unittest

from depviz.graph import build_graph, load_order
from depviz.testrepo import TestRepoError, load_test_repo, parse_test_repo

DATA = os.path.join(os.path.dirname(__file__), "data")


def repo_source(name):
    """Вернуть функцию зависимостей для файла из tests/data."""
    repo = load_test_repo(os.path.join(DATA, name))
    return lambda package: repo.get(package, [])


class GraphTest(unittest.TestCase):
    """Проверка DFS, циклов и разбора файла."""

    def test_simple(self):
        """Транзитивные зависимости без циклов."""
        graph, cycles = build_graph("A", repo_source("simple.txt"))
        self.assertEqual(set(graph), {"A", "B", "C", "D", "E"})
        self.assertEqual(cycles, [])

    def test_sub_package(self):
        """Граф строится от любого пакета."""
        graph, _ = build_graph("C", repo_source("simple.txt"))
        self.assertEqual(set(graph), {"C", "D", "E"})

    def test_cycles(self):
        """Циклы находятся, обход не зацикливается."""
        graph, cycles = build_graph("A", repo_source("cycle.txt"))
        self.assertEqual(set(graph), {"A", "B", "C", "D"})
        self.assertIn(["A", "B", "C", "A"], cycles)
        self.assertIn(["D", "D"], cycles)

    def test_undefined_package(self):
        """Пакет без строки — пакет без зависимостей."""
        graph, _ = build_graph("A", repo_source("diamond.txt"))
        self.assertEqual(graph["F"], [])

    def test_bad_names(self):
        """Имена не из больших букв — ошибка."""
        with self.assertRaises(TestRepoError):
            load_test_repo(os.path.join(DATA, "bad.txt"))

    def test_bad_lines(self):
        """Строка без двоеточия и повтор пакета — ошибка."""
        for text in ["A B", "A: B\nA: C"]:
            with self.assertRaises(TestRepoError):
                parse_test_repo(text)


class LoadOrderTest(unittest.TestCase):
    """Проверка порядка загрузки."""

    def check_order(self, graph, order):
        """Каждая зависимость загружается раньше пакета."""
        position = {name: index for index, name in enumerate(order)}
        for name, deps in graph.items():
            for dep in deps:
                self.assertLess(position[dep], position[name])

    def test_simple(self):
        """Порядок для графа без циклов."""
        graph, _ = build_graph("A", repo_source("simple.txt"))
        order = load_order(graph, "A")
        self.assertEqual(order, ["D", "B", "E", "C", "A"])
        self.check_order(graph, order)

    def test_diamond(self):
        """Общая зависимость загружается один раз."""
        graph, _ = build_graph("A", repo_source("diamond.txt"))
        order = load_order(graph, "A")
        self.assertEqual(len(order), len(set(order)))
        self.check_order(graph, order)

    def test_cycle(self):
        """С циклом все пакеты всё равно попадают в порядок."""
        graph, _ = build_graph("A", repo_source("cycle.txt"))
        self.assertEqual(load_order(graph, "A"), ["C", "D", "B", "A"])


if __name__ == "__main__":
    unittest.main()
