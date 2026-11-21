"""Построение графа зависимостей обходом в глубину (DFS)."""


def build_graph(root, get_deps):
    """Построить граф зависимостей пакета с учётом транзитивности.

    get_deps(name) возвращает список прямых зависимостей пакета.
    Возвращает пару: граф {пакет: [зависимости]} и список найденных
    циклов, каждый цикл — список пакетов от начала до повтора.
    """
    graph = {}
    cycles = []
    _visit(root, get_deps, graph, [], cycles)
    return graph, cycles


def _visit(node, get_deps, graph, path, cycles):
    """Рекурсивно обойти пакет node и его зависимости.

    path — текущий путь от корня. Если пакет уже есть на пути, найден
    цикл: он запоминается, и обход по этому ребру не продолжается.
    """
    if node in path:
        cycles.append(path[path.index(node):] + [node])
        return
    if node in graph:
        return
    graph[node] = get_deps(node)
    path.append(node)
    for dep in graph[node]:
        _visit(dep, get_deps, graph, path, cycles)
    path.pop()


def load_order(graph, root):
    """Вернуть порядок загрузки: зависимости раньше зависящих от них.

    Это обратный (post-order) обход DFS. Ребро, замыкающее цикл,
    пропускается, поэтому у пакетов из цикла порядок условный.
    """
    order = []
    _collect(root, graph, set(), order)
    return order


def _collect(node, graph, seen, order):
    """Добавить в order зависимости пакета node, а затем сам пакет."""
    if node in seen:
        return
    seen.add(node)
    for dep in graph.get(node, []):
        _collect(dep, graph, seen, order)
    order.append(node)
