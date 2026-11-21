# pip-deps-visualizer

Инструмент визуализации графа зависимостей для менеджера пакетов Python (pip).
Практическая работа №2 Вариант 8

Готовые менеджеры пакетов и библиотеки для получения зависимостей не
используются: только стандартная библиотека Python

## Требования

- Python 3.10 или новее
- Graphviz (команда `dot`) — для получения SVG

## Сборка и запуск

Сборка не требуется. Запуск приложения и тестов:

```sh
./run.sh -p <пакет> [опции]
./run.sh test
```

## Настройки (опции командной строки)

| Опция | По умолчанию | Описание |
| --- | --- | --- |
| `-p`, `--package` | — (обязательная) | Имя анализируемого пакета |
| `-r`, `--repo` | `https://pypi.org` | URL репозитория или путь к файлу тестового репозитория |
| `-t`, `--test-mode` | выключен | Режим работы с тестовым репозиторием (файлом) |
| `-o`, `--output` | `graph.svg` | Имя файла с изображением графа (`.svg`) |
| `-l`, `--load-order` | выключен | Вывести порядок загрузки зависимостей |

Ошибки в параметрах выводятся в виде `Ошибка: ...`, код завершения 1.

## Основной сценарий

```sh
./run.sh -p flask -o flask.svg      # DOT в консоль, картинка в flask.svg
./run.sh -p flask -l                # порядок загрузки зависимостей
./run.sh -t -r tests/data/cycle.txt -p A -o cycle.svg   # тестовый режим
```

## Структура и функции

| Файл | Функции |
| --- | --- |
| `src/depviz/config.py` | `parse_config` — разбор и проверка опций; `check_package`, `check_repo`, `check_output` — проверки отдельных параметров; класс `Config` — хранит настройки |
| `src/depviz/pypi.py` | `get_direct_dependencies` — прямые зависимости из PyPI; `fetch_json` — скачать JSON; `parse_requirement` — имя пакета из строки зависимости; `normalize` — привести имя к одному виду |
| `src/depviz/testrepo.py` | `load_test_repo` — чтение файла тестового репозитория; `parse_test_repo`, `parse_line`, `check_name` — разбор и проверка |
| `src/depviz/graph.py` | `build_graph` — граф рекурсивным DFS с поиском циклов; `load_order` — порядок загрузки |
| `src/depviz/dot.py` | `to_dot` — текст графа на языке DOT; `save_svg` — изображение SVG через `dot`; `cycle_edges` — рёбра циклов |
| `src/depviz/main.py` | `main` — общий сценарий; `make_source` — выбор источника (PyPI или файл); `visualize`, `print_load_order`, `print_cycles` — вывод |
| `tests/` | unit-тесты (`unittest`), примеры тестовых репозиториев в `tests/data/` |

Примеры вывода в разделах этапов 1–3 показывают поведение программы на
момент этих этапов: вывод параметров (этап 1) и прямых зависимостей
(этап 2) по условию нужен только на своём этапе.

## Этап 1. Минимальный прототип с конфигурацией

Приложение выводит все параметры в формате ключ-значение:

```
$ ./run.sh -p requests
package=requests
repo=https://pypi.org
test_mode=False
output=graph.svg
```

Обработка ошибок:

```
$ ./run.sh -p "bad name"
Ошибка: недопустимое имя пакета: bad name
$ ./run.sh -p a -t -r tests/data/simple.txt
Ошибка: в тестовом режиме пакет называется большими латинскими буквами, получено: a
$ ./run.sh -p A -t -r nofile.txt
Ошибка: файл тестового репозитория не найден: nofile.txt
$ ./run.sh -p requests -r ftp://pypi.org
Ошибка: URL репозитория должен начинаться с http:// или https://: ftp://pypi.org
$ ./run.sh -p requests -o graph.png
Ошибка: файл изображения должен иметь расширение .svg: graph.png
$ ./run.sh -p requests -o nodir/graph.svg
Ошибка: папка для файла изображения не существует: nodir
```

## Этап 2. Сбор данных

Модуль `src/depviz/pypi.py` получает прямые зависимости без pip и сторонних
библиотек:

1. Скачивает `<repo>/pypi/<пакет>/json` — описание пакета в репозитории
   PyPI в формате JSON.
2. Берёт поле `info.requires_dist`: это строки `Requires-Dist` из
   метаданных пакета, например `numpy>=1.25`.
3. Из каждой строки оставляет только имя пакета и пропускает
   необязательные зависимости (`extra == ...`).

```
$ ./run.sh -p matplotlib
Прямые зависимости matplotlib:
  contourpy
  cycler
  fonttools
  kiwisolver
  numpy
  packaging
  pillow
  pyparsing
  python-dateutil
$ ./run.sh -p no-such-package-xyz-123
Ошибка: пакет не найден (404): https://pypi.org/pypi/no-such-package-xyz-123/json
```

## Этап 3. Основные операции

Граф строится в `src/depviz/graph.py` рекурсивным обходом в глубину (DFS).
Путь от корня хранится в списке: если пакет снова встречается на текущем
пути, это цикл. Цикл запоминается, а обход по этому ребру не продолжается,
поэтому программа не зацикливается.

### Тестовый репозиторий

С опцией `-t` вместо URL указывается файл. Формат файла:

```
# комментарий
A: B C
B: D
D:
```

Пакеты называются большими латинскими буквами. Пакет без своей строки
считается пакетом без зависимостей. Примеры лежат в `tests/data/`.

```
$ ./run.sh -t -r tests/data/simple.txt -p A
Граф зависимостей A (пакетов: 5):
  A -> B, C
  B -> D
  D -> (нет)
  C -> D, E
  E -> (нет)
$ ./run.sh -t -r tests/data/cycle.txt -p A
Граф зависимостей A (пакетов: 4):
  A -> B
  B -> C, D
  C -> A
  D -> D
Циклические зависимости:
  A -> B -> C -> A
  D -> D
$ ./run.sh -t -r tests/data/diamond.txt -p A
Граф зависимостей A (пакетов: 6):
  A -> B, C
  B -> D
  D -> E, F
  E -> (нет)
  F -> (нет)
  C -> D
$ ./run.sh -t -r tests/data/simple.txt -p Z
Ошибка: пакет Z не описан в tests/data/simple.txt
$ ./run.sh -t -r tests/data/bad.txt -p A
Ошибка: строка 1: пакет должен называться большими латинскими буквами: c
```

Реальный пакет:

```
$ ./run.sh -p matplotlib
Граф зависимостей matplotlib (пакетов: 11):
  matplotlib -> contourpy, cycler, fonttools, kiwisolver, numpy, packaging, pillow, pyparsing, python-dateutil
  contourpy -> numpy
  numpy -> (нет)
  cycler -> (нет)
  fonttools -> (нет)
  kiwisolver -> (нет)
  packaging -> (нет)
  pillow -> (нет)
  pyparsing -> (нет)
  python-dateutil -> tzdata
  tzdata -> (нет)
```

## Этап 4. Дополнительные операции

Опция `-l` выводит порядок загрузки: каждый пакет идёт после всех своих
зависимостей. Это обратный (post-order) обход DFS по построенному графу
(`load_order` в `src/depviz/graph.py`). Общая зависимость загружается один
раз. В цикле строгого порядка не существует, поэтому замыкающее цикл ребро
пропускается, и программа об этом предупреждает.

```
$ ./run.sh -t -r tests/data/simple.txt -p A -l
Порядок загрузки A:
  1. D
  2. B
  3. E
  4. C
  5. A
$ ./run.sh -t -r tests/data/diamond.txt -p A -l
Порядок загрузки A:
  1. E
  2. F
  3. D
  4. B
  5. C
  6. A
$ ./run.sh -t -r tests/data/cycle.txt -p A -l
Порядок загрузки A:
  1. C
  2. D
  3. B
  4. A
Внимание: есть циклы, порядок пакетов в цикле условный:
  A -> B -> C -> A
  D -> D
```

### Сравнение с pip

Порядок pip взят из строки `Installing collected packages` команды
`pip install --target <папка> <пакет>` (Python 3.13, Linux).

| Пакет | depviz (`-l`) | pip |
| --- | --- | --- |
| requests | charset-normalizer, idna, urllib3, certifi, requests | urllib3, idna, charset_normalizer, certifi, requests |
| matplotlib | numpy, contourpy, cycler, fonttools, kiwisolver, packaging, pillow, pyparsing, tzdata, python-dateutil, matplotlib | tzdata, pyparsing, pillow, packaging, numpy, kiwisolver, fonttools, cycler, python-dateutil, contourpy, matplotlib |
| pytest | colorama, typing-extensions, exceptiongroup, iniconfig, packaging, pluggy, pygments, tomli, pytest | pygments, pluggy, packaging, iniconfig, pytest |

Объяснение расхождений:

1. **Порядок независимых пакетов.** И depviz, и pip ставят зависимости
   раньше пакета (numpy раньше contourpy, tzdata раньше python-dateutil).
   Но пакеты, которые друг от друга не зависят, можно загружать в любом
   порядке. depviz идёт по списку `Requires-Dist`, а pip использует свой
   порядок разрешения. Оба порядка правильные.
2. **Маркеры окружения.** У pytest есть зависимости вроде
   `colorama; sys_platform == "win32"` и `tomli; python_version < "3.11"`.
   pip проверяет маркеры для текущей системы (Linux, Python 3.13) и такие
   пакеты не ставит. depviz пропускает только `extra`, а остальные маркеры
   не вычисляет, поэтому показывает зависимости для всех платформ сразу.
3. **Версии.** depviz всегда берёт последнюю версию каждого пакета и не
   учитывает ограничения (`>=`, `<`). pip подбирает версии, совместимые
   между собой, поэтому в сложных случаях набор зависимостей может
   отличаться.
4. **Уже установленные пакеты.** Без `--target` pip не включает в список
   пакеты, которые уже установлены. depviz всегда строит полный граф.

## Этап 5. Визуализация

`src/depviz/dot.py` формирует текст графа на языке Graphviz (DOT) и
выводит его в консоль, а программа `dot` сохраняет изображение в SVG
(опция `-o`). Корневой пакет обведён жирной рамкой, рёбра циклов — красные.

```
$ ./run.sh -t -r tests/data/cycle.txt -p A -o cycle.svg
digraph "A" {
  rankdir=LR;
  node [shape=box, style=rounded];
  "A" [style="rounded,bold"];
  "A" -> "B" [color=red];
  "B" -> "C" [color=red];
  "B" -> "D";
  "C" -> "A" [color=red];
  "D" -> "D" [color=red];
}
Цикл: A -> B -> C -> A
Цикл: D -> D
Изображение сохранено: cycle.svg
```

### Три пакета

Команды создают текст DOT (`.dot`) и изображение (`.svg`) для каждого
пакета. Готовые изображения в репозиторий не добавляются: это файлы,
которые создаёт сама программа.

```sh
./run.sh -p requests   -o requests.svg   > requests.dot
./run.sh -p matplotlib -o matplotlib.svg > matplotlib.dot
./run.sh -p flask      -o flask.svg      > flask.dot
```

Вывод для flask:

```
digraph "flask" {
  rankdir=LR;
  node [shape=box, style=rounded];
  "flask" [style="rounded,bold"];
  "flask" -> "blinker";
  "flask" -> "click";
  "flask" -> "importlib-metadata";
  "flask" -> "itsdangerous";
  "flask" -> "jinja2";
  "flask" -> "markupsafe";
  "flask" -> "werkzeug";
  "importlib-metadata" -> "zipp";
  "importlib-metadata" -> "lazy-importer";
  "jinja2" -> "markupsafe";
  "werkzeug" -> "markupsafe";
}
Изображение сохранено: flask.svg
```

### Сравнение со штатным инструментом

Своего инструмента визуализации у pip нет, обычно используют `pipdeptree`.
Пакеты были установлены в чистое окружение (`python3 -m venv`,
`pip install requests matplotlib flask pipdeptree`), затем запущено
`pipdeptree -p <пакет>`:

```
Flask==3.1.3
├── blinker [required: >=1.9.0, installed: 1.9.0]
├── click [required: >=8.1.3, installed: 8.5.1]
├── itsdangerous [required: >=2.2.0, installed: 2.2.0]
├── Jinja2 [required: >=3.1.2, installed: 3.1.6]
│   └── MarkupSafe [required: >=2.0, installed: 3.0.4]
├── MarkupSafe [required: >=2.1.1, installed: 3.0.4]
└── Werkzeug [required: >=3.1.0, installed: 3.1.9]
    └── MarkupSafe [required: >=2.1.1, installed: 3.0.4]
```

Для requests и matplotlib набор пакетов и рёбер совпал с depviz. Для flask
есть расхождения:

1. **`importlib-metadata`, `zipp`, `lazy-importer` есть только у depviz.**
   У flask эта зависимость записана с маркером
   `importlib-metadata>=3.6; python_version < "3.10"`. pipdeptree показывает
   то, что реально установлено, а на Python 3.13 pip этот пакет не ставил.
   depviz маркеры окружения (кроме `extra`) не вычисляет и показывает
   зависимости для всех версий Python и платформ.
2. **Повторы.** pipdeptree рисует дерево, поэтому `MarkupSafe` выводится
   три раза. depviz строит граф: каждый пакет — одна вершина, в
   `markupsafe` входят три стрелки.
3. **Версии и имена.** pipdeptree показывает требования и установленные
   версии, depviz — только имена в нормализованном виде (`jinja2` вместо
   `Jinja2`), версии не учитывает и всегда берёт последнюю версию пакета.
4. **Источник данных.** pipdeptree читает установленные пакеты, а depviz —
   метаданные из репозитория PyPI, поэтому ему не нужна установка.
