"""
Самопроверка сетки заказа (правило #5 docs/ПРАВИЛА_ОБРАБОТКИ.md):
для каждой строки блюда и каждого назначенного ей столбца-исключения проверяем,
что состав блюда не нарушает исключение этого столбца.

Проверяются только категории из явного списка синонимов правил (лактоза, рыба,
мясо/курица, злаки, цитрус, орехи, сахар, грибы, груша, корица). Категория
"овощи" (для столбца I) в правилах не формализована и не проверяется - там мы
полагаемся на предыдущий прецедент.

Запуск: python3 src/validate.py [модуль_заказа]  (по умолчанию order_grid)
"""
import importlib
import sys

from composition import Kitchen


def run(order_module="order_grid"):
    order = importlib.import_module(order_module)
    kitchen = Kitchen(overrides=order.COMPOSITION_OVERRIDES)
    rows = order.build_rows()
    problems = []
    unknown_dishes = []

    for row in rows:
        text = kitchen.composition_text(row["name"])
        if text is None:
            unknown_dishes.append(row["name"])
            continue
        tags = kitchen.tags(row["name"])
        for col in row["cols"]:
            excluded = order.EXCLUDED_CATEGORIES.get(col, set())
            hit = tags & excluded
            if hit:
                problems.append((row["name"], col, sorted(hit)))

    # проверка на полностью пустые строки (правило #5)
    empty_rows = [r["name"] for r in rows if not r["cols"]]

    print(f"Строк: {len(rows)}")
    print(f"Не найден состав (пропущена проверка): {unknown_dishes or 'нет'}")
    print(f"Пустые строки: {empty_rows or 'нет'}")
    if problems:
        print(f"\nНАЙДЕНЫ КОНФЛИКТЫ СОСТАВА ({len(problems)}):")
        for name, col, cats in problems:
            print(f"  [{col}] {name!r} содержит {cats}, а столбец это исключает")
    else:
        print("\nКонфликтов состава не найдено.")

    return problems, unknown_dishes, empty_rows


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "order_grid")
