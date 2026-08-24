"""
Проверка покрытия: для каждого блока "base-строка + следующие за ней alt-строки"
(один курс одного приёма пищи) объединение назначенных столбцов должно быть
подмножеством полного набора F..U, БЕЗ повторов (один столбец не должен получать
блюдо дважды в одном курсе) и, за вычётом заведомо неполных курсов (см.
PARTIAL_OK), должно покрывать весь набор F..U.

Курс "боул" (ЗАВТРАК 2) намеренно не покрывает стандарт-столбцы (M..U) - боулы
только премиум (правило #2), поэтому в PARTIAL_OK.
Курс "запеканка" (ЗАВТРАК) намеренно не покрывает F,H,K,O,Q,S - на эту позицию
меню нет безопасной замены, клиенты просто без неё (см. комментарий в коде).
Курс "суп" (ОБЕД) намеренно не покрывает I - все имеющиеся супы содержат овощи,
а I ("без овощей и рыбы") уже получает замену на курсе "салат" (йогурт).
"""
from order_grid import build_rows, COLUMNS

DATA_COLS = set("FGHIJKLMNOPQRSTU")

PARTIAL_OK = {
    ("ЗАВТРАК 2", "БОУЛ ОВОЩНОЙ"),
    ("ЗАВТРАК", "ЗАПЕКАНКА ТВОРОЖНАЯ 70 ГР."),
    ("ОБЕД", "ЩИ С КУРИЦЕЙ"),
}


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


def run():
    rows = build_rows()
    groups = group_courses(rows)
    issues = []
    for g in groups:
        seen = []
        union = set()
        for r in g["rows"]:
            cols = [c for c in r["cols"] if c in DATA_COLS]
            dup = union & set(cols)
            if dup:
                issues.append(f"[{g['meal']}/{g['course']}] столбцы {sorted(dup)} получают >1 блюда в этом курсе (строка {r['name']!r})")
            union |= set(cols)
        missing = DATA_COLS - union
        if missing and (g["meal"], g["course"]) not in PARTIAL_OK:
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
    run()
