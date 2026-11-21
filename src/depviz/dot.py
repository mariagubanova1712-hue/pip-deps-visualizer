"""Представление графа на языке Graphviz (DOT) и сохранение в SVG."""

import subprocess

DOT_COMMAND = "dot"
CYCLE_COLOR = "red"


class VizError(Exception):
    """Ошибка получения изображения графа."""


def quote(name):
    """Взять имя пакета в кавычки для языка DOT."""
    return '"' + name.replace('"', '\\"') + '"'


def cycle_edges(cycles):
    """Вернуть множество рёбер (откуда, куда), входящих в циклы."""
    edges = set()
    for cycle in cycles:
        edges.update(zip(cycle, cycle[1:]))
    return edges


def to_dot(graph, root, cycles=()):
    """Сформировать текст графа зависимостей на языке DOT."""
    in_cycle = cycle_edges(cycles)
    lines = [
        f"digraph {quote(root)} {{",
        "  rankdir=LR;",
        "  node [shape=box, style=rounded];",
        f"  {quote(root)} [style=\"rounded,bold\"];",
    ]
    for name, deps in graph.items():
        for dep in deps:
            attrs = f" [color={CYCLE_COLOR}]" if (name, dep) in in_cycle else ""
            lines.append(f"  {quote(name)} -> {quote(dep)}{attrs};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def save_svg(dot_text, output):
    """Нарисовать граф программой dot и сохранить в файл SVG."""
    command = [DOT_COMMAND, "-Tsvg", "-o", output]
    try:
        subprocess.run(
            command, input=dot_text, text=True, check=True,
            capture_output=True,
        )
    except FileNotFoundError as error:
        raise VizError(
            "не найдена программа dot: установите Graphviz"
        ) from error
    except subprocess.CalledProcessError as error:
        raise VizError(f"dot завершился с ошибкой: {error.stderr}") from error
