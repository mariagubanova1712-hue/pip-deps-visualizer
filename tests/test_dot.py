"""Тесты формирования DOT и сохранения SVG."""

import os
import shutil
import tempfile
import unittest

from depviz.dot import save_svg, to_dot

GRAPH = {"A": ["B", "C"], "B": ["A"], "C": []}
CYCLES = [["A", "B", "A"]]


class DotTest(unittest.TestCase):
    """Проверка текста DOT и файла SVG."""

    def test_edges(self):
        """Каждое ребро графа есть в тексте DOT."""
        text = to_dot(GRAPH, "A")
        self.assertTrue(text.startswith('digraph "A" {'))
        self.assertIn('"A" -> "B";', text)
        self.assertIn('"A" -> "C";', text)

    def test_cycle_color(self):
        """Рёбра цикла выделяются цветом."""
        text = to_dot(GRAPH, "A", CYCLES)
        self.assertIn('"B" -> "A" [color=red];', text)
        self.assertIn('"A" -> "C";', text)

    @unittest.skipUnless(shutil.which("dot"), "нет Graphviz")
    def test_save_svg(self):
        """Файл SVG создаётся."""
        folder = tempfile.mkdtemp()
        output = os.path.join(folder, "graph.svg")
        save_svg(to_dot(GRAPH, "A"), output)
        with open(output, encoding="utf-8") as handle:
            self.assertIn("<svg", handle.read())
        shutil.rmtree(folder)


if __name__ == "__main__":
    unittest.main()
