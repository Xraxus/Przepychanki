class JostlingCard():
    def __init__(self, color, name):
        self.color = color
        self.name = name

    def __repr__(self):
        return "%s - %s" % (self.color, self.name)

# 1. Pan tu nie stał - przesuń swój pionek o 1 miejsce do przodu.
# 2. Zwiększona dostawa - dołóż 1 towar więcej do sklepu, w którym była dostawa w tej rundzie.
# 3. Lista społeczna - obróć wybraną kolejkę tył na przód.
# 4. Krytyka władzy - przesuń wybrany pionek o 2 miejsca do tyłu.
# 5. Kolega w Komitecie - podejrzyj dwie karty dostawy towaru z wierzchu stosu.
# 6. Towar spod lady - jeśli jesteś 1 w kolejce, zabierz towar do domu po zagraniu tej karty.
# 7. Szczęśliwy traf - przesuń swój pionek na drugie miejsce do innej kolejki.
# 8. Matka z dzieckiem na ręku - przesuń swój pionek na początek kolejki.
# 9. Pomyłka w dostawie - przełóż 1 towar do innego sklepu.
# 10. Remament - połóż na sklepie kartę remament, sklep będzie zamknięty w tej turze - nie będzie sprzedawał towaru w tej turze.
# Nie działają na niego karty "Zwiększona dostawa", "Pomyłka w dostawie", "Towar spod lady".
