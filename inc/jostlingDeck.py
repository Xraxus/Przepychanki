import random

from inc.jostlingCard import JostlingCard


class JostlingDeck():
    def __init__(self):
        self.deck = list()

        for color in ['niebieski', 'zolty', 'czerwony', 'zielony', 'brazowy']:
            for card_name in ["Pan tu nie stał",
                              "Matka z dzieckiem",
                              "Krytyka władzy",
                              "Zwiększona dostawa",
                              "Pomyłka w dostawie",
                              "Kolega w Komitecie",
                              "Lista społeczna",
                              "Towar spod lady",
                              "Szczęśliwy traf",
                              "Remanent"]:
                self.deck.append(JostlingCard(color, card_name))
        random.shuffle(self.deck)

    def count_by_color(self, color):
        counter = 0
        for card in self.deck:
            if color == card.color:
                counter += 1

        return counter

    def __repr__(self):
        return "Jost deck: %d: %s" % (len(self.deck), self.deck)


