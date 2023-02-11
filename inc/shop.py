from inc.pawn import Pawn

class Shop():
    def __init__(self, name):
        self.name = name
        self.available_goods = []
        self.queue = []
        self.speculant = [Pawn(name, '#')]
        self.is_open = True
    def __repr__(self):
        return "\n%s,\n  Towary: %s,\n  Kolejka: %s\n" % (self.name, self.available_goods, self.queue)

    def delivery(self, amount, goods_deck):
        #bierze ilość i stos kart i dodaje pierwsze z góry
        for x in range(amount):
            self.available_goods.append(goods_deck.draw())







