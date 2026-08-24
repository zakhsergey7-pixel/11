"""
Проверка покрытия: для каждого блока "base-строка + следующие за ней alt-строки"
(один курс одного приёма пищи) объединение назначенных столбцов должно быть
подмножеством полного набора столбцов данных, БЕЗ повторов (один столбец не
должен получать блюдо дважды в одном курсе) и, за вычётом заведомо неполных
курсов, перечисленных в order.PARTIAL_OK (если модуль его определяет), должно
покрывать весь набор столбцов.

Запуск: python3 src/coverage.py [модуль_заказа]  (по умолчанию order_grid)
"""
import importlib
import sys


def group_courses(rows):
    groups = []
    current = None
    for r in rows:
        if r["fill"] == "base":
            current = {"meal": r["meal"], "course": r["name"], "rows": [r]}
            groups.append(current)
        else:
            if current is None:
                current = {"meal": r["meal"], "course": r["name"], "rows": []}
                groups.append(current)
            current["rows"].append(r)
    return groups


def run(order_module="order_grid"):
    order = importlib.import_module(order_module)
    data_cols = set(order.COLUMNS) - {"D", "E"}
    partial_ok = getattr(order, "PARTIAL_OK", set())

    rows = order.build_rows()
    groups = group_courses(rows)
    issues = []
    for g in groups:
        union = set()
        for r in g["rows"]:
            cols = [c for c in r["cols"] if c in data_cols]
            dup = union & set(cols)
            if dup:
                issues.append(f"[{g['meal']}/{g['course']}] столбцы {sorted(dup)} получают >1 блюда в этом курсе (строка {r['name']!r})")
            union |= set(cols)
        missing = data_cols - union
        if missing and (g["meal"], g["course"]) not in partial_ok:
            issues.append(f"[{g['meal']}/{g['course']}] не покрыты столбцы {sorted(missing)}")

    print(f"Курсов найдено: {len(groups)}")
    if issues:
        print(f"\nПРОБЛЕМЫ ПОКРЫТИЯ ({len(issues)}):")
        for i in issues:
            print(" ", i)
    else:
        print("Покрытие полное, повторов нет.")
    return issues


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "order_grid")
