"""Представление графа на языке Graphviz (DOT) и сохранение в SVG."""

import subprocess

DOT_COMMAND = "dot"
CYCLE_COLOR = "red"


class VizError(Exception):
    """Ошибка получения изображения графа."""


def cycle_edges(cycles):
    """Вернуть список рёбер, входящих в циклы.

    Цикл A -> B -> A даёт рёбра (A, B) и (B, A).
    """
    edges = []
    for cycle in cycles:
        for i in range(len(cycle) - 1):
            edges.append((cycle[i], cycle[i + 1]))
    return edges


def to_dot(graph, root, cycles=()):
    """Сформировать текст графа зависимостей на языке DOT."""
    red_edges = cycle_edges(cycles)
    text = 'digraph "' + root + '" {\n'
    text += "  rankdir=LR;\n"
    text += "  node [shape=box, style=rounded];\n"
    text += '  "' + root + '" [style="rounded,bold"];\n'
    for name in graph:
        for dep in graph[name]:
            text += '  "' + name + '" -> "' + dep + '"'
            if (name, dep) in red_edges:
                text += " [color=" + CYCLE_COLOR + "]"
            text += ";\n"
    text += "}\n"
    return text


def save_svg(dot_text, output):
    """Нарисовать граф программой dot и сохранить в файл SVG."""
    command = [DOT_COMMAND, "-Tsvg", "-o", output]
    try:
        subprocess.run(
            command, input=dot_text, text=True, check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        raise VizError("не найдена программа dot: установите Graphviz")
    except subprocess.CalledProcessError as error:
        raise VizError("dot завершился с ошибкой: " + error.stderr)
