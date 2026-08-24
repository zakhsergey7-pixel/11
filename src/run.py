"""Единая точка входа: самопроверка + сборка .xlsx.

Запуск: python3 src/run.py
"""
import sys

import build_xlsx
import coverage
import validate


def main():
    problems, unknown, empty = validate.run()
    print()
    issues = coverage.run()
    print()
    if problems or unknown or empty:
        print("ВНИМАНИЕ: самопроверка состава нашла проблемы, файл всё равно будет собран - проверьте вывод выше.")
    build_xlsx.main()


if __name__ == "__main__":
    sys.exit(main())
