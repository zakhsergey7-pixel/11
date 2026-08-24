"""
Движок сопоставления состава блюд с исключениями (аллергии/диеты).

Логика взята из docs/ПРАВИЛА_ОБРАБОТКИ.md, раздел 4-5:
- синонимы категорий (лактоза/рыба/мясо/злаки/цитрус и т.п.)
- "мускатный орех" не триггерит "без орехов"
- "яйцо куриное" не триггерит "без мяса"/"без курицы"
- сопоставление терпимо к опечатке в 1 букву
"""
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_recipes():
    with open(DATA_DIR / "all_recipes.json", encoding="utf-8") as f:
        return json.load(f)


def load_menu():
    with open(DATA_DIR / "full_menu.json", encoding="utf-8") as f:
        return json.load(f)


# Категория -> список ключевых подстрок (нижний регистр), по которым ищем совпадение в составе.
CATEGORY_KEYWORDS = {
    "лактоза": ["молок", "слив", "творог", "сыр", "кефир", "йогурт", "сметан", "мусс", "брынз", "фета", "рикотт", "моцарелл"],
    "рыба": ["треска", "форель", "кефал", "судак", "лосос", "сельд", "рыба", "рыбн"],
    "мясо": ["куриц", "курин", "говядин", "свинин", "баранин", "индей", "ветчин"],
    "курица": ["куриц", "курин"],
    "злаки": ["круп", "мук", "хлеб", "булочк", "кекс", "печень", "макарон", "батон"],
    "цитрус": ["лимон", "апельсин", "мандарин"],
    "орехи": ["орех"],
    "сахар": ["сахар"],
    "грибы": ["гриб"],
    "груша": ["груш"],
    "корица": ["корице", "корицы", "корица"],
}


_WORD_RE = re.compile(r"[а-яёa-z]+", re.IGNORECASE)


def _words(text_lower):
    return _WORD_RE.findall(text_lower)


def _has_keyword(words, keyword):
    # Совпадение по началу слова (терпит склонения: "молоко"/"молочный"/"молока"),
    # без fuzzy-подстрочного поиска - он ловит слишком много случайных совпадений
    # между разными словами схожей длины (например "курица"/"корица", "молоко"/
    # "молотый", "кукуруза"/keyword "мук"). Fuzzy-допуск на опечатку нужен только
    # при сопоставлении НАЗВАНИЙ блюд (см. Kitchen.composition_text), не тут.
    return any(w.startswith(keyword) for w in words)


def tag_composition(text):
    """Возвращает множество категорий, присутствующих в составе блюда (текст на русском)."""
    if not text:
        return set()
    low = text.lower()
    words = _words(low)

    # спец-случай: "яйцо куриное" - это яйцо, а не мясо курицы (правило #48).
    # Убираем из рассмотрения такие слова перед проверкой категорий мясо/курица.
    meat_words = list(words)
    for m in re.finditer(r"\bяйцо\s+(куриц\w*|курин\w*)", low):
        egg_word = m.group(1)
        if egg_word in meat_words:
            meat_words.remove(egg_word)

    tags = set()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "орехи":
            # спец-случай: "мускатный орех" - это специя, не аллерген-орех (правило #47)
            for m in re.finditer(r"\bорех", low):
                start = m.start()
                prefix = low[max(0, start - 12):start]
                if "мускатн" not in prefix:
                    tags.add("орехи")
                    break
            continue
        source_words = meat_words if category in ("мясо", "курица") else words
        if any(_has_keyword(source_words, kw) for kw in keywords):
            tags.add(category)
    return tags


class Kitchen:
    """Обёртка над словарём рецептов с fuzzy-поиском состава по названию блюда."""

    def __init__(self, recipes=None, overrides=None):
        self.recipes = dict(recipes or load_recipes())
        if overrides:
            self.recipes.update(overrides)
        self._names = list(self.recipes.keys())

    def composition_text(self, dish_name):
        if dish_name in self.recipes:
            return self.recipes[dish_name]
        # терпимость к опечатке в названии блюда (правило #45)
        norm = dish_name.strip().upper()
        for name in self._names:
            if name.strip().upper() == norm:
                return self.recipes[name]
        best = None
        best_dist = None
        for name in self._names:
            n = name.strip().upper()
            if abs(len(n) - len(norm)) > 2:
                continue
            dist = _levenshtein(n, norm)
            if best_dist is None or dist < best_dist:
                best, best_dist = name, dist
        if best is not None and best_dist is not None and best_dist <= 2:
            return self.recipes[best]
        return None

    def tags(self, dish_name):
        text = self.composition_text(dish_name)
        return tag_composition(text) if text else set()

    def violates(self, dish_name, excluded_categories):
        return bool(self.tags(dish_name) & set(excluded_categories))


def _levenshtein(a, b):
    if a == b:
        return 0
    la, lb = len(a), len(b)
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * lb
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[lb]
