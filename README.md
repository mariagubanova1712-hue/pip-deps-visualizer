# pip-deps-visualizer

Инструмент визуализации графа зависимостей для менеджера пакетов Python (pip).
Практическая работа №2 по дисциплине «Конфигурационное управление», вариант 8.

Готовые менеджеры пакетов и библиотеки для получения зависимостей не
используются: только стандартная библиотека Python.

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
Ошибка: недопустимое имя пакета: 'bad name'
$ ./run.sh -p a -t -r tests/data/simple.txt
Ошибка: в тестовом режиме пакет называется большими латинскими буквами, получено: 'a'
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

1. Запрашивает `<repo>/pypi/<пакет>/json` (JSON API репозитория PyPI).
2. Находит wheel-пакет последней версии и скачивает его файл `METADATA`
   (`<url wheel>.metadata`). Если такого файла нет, берёт поле
   `info.requires_dist` из JSON.
3. Читает строки `Requires-Dist`, оставляет имена пакетов (приводит их к
   виду PEP 503) и пропускает необязательные зависимости (`extra == ...`).

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
Ошибка: не найдено в репозитории: https://pypi.org/pypi/no-such-package-xyz-123/json
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
Ошибка: строка 1: пакет должен называться большими латинскими буквами: 'c'
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
