"""Единая точка входа: самопроверка + сборка .xlsx для заданного заказа.

Запуск: python3 src/run.py [модуль_заказа]  (по умолчанию order_grid)
"""
import sys

import build_xlsx
import coverage
import validate


def main(order_module="order_grid"):
    problems, unknown, empty = validate.run(order_module)
    print()
    coverage.run(order_module)
    print()
    if problems or unknown or empty:
        print("ВНИМАНИЕ: самопроверка состава нашла проблемы, файл всё равно будет собран - проверьте вывод выше.")
    build_xlsx.main(order_module)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "order_grid"))
