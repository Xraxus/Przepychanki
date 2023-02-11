from inc.supplyCard import SupplyCard
import random

class SupplyDeck():
    def __init__(self):
        self.deck = list()

        #Zapełnij deck oryginalnymi kartami
        for categories in ["Spożywczy", "RTV-AGD", "Odzież", "Meblowy", "Kiosk"]:
            for amounts in [3,2,1]:
                self.deck.append(SupplyCard(categories,amounts))
        random.shuffle(self.deck)

    def draw(self):
        if self.deck:
            return self.deck.pop()

    def count(self):
        return len(self.deck)

    def __repr__(self):
        return "%s" % (self.deck)

