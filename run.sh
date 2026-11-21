#!/bin/sh
Запуск: ./run.sh [опции]   Тесты: ./run.sh test
cd "$(dirname "$0")" || exit 1
export PYTHONPATH=src
if [ "$1" = "test" ]; then
    exec python3 -m unittest discover -s tests -v
fi
exec python3 -m depviz "$@"
