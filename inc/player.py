from inc.pawn import Pawn
from inc.shoppingList import ShoppingList


class Player():

    def __init__(self, color, shopping_list_number, name='Anonymous', mode ='human'):
        self.name = name
        self.mode = mode
        self.color = color
        self.pass_status = False

        self.shopping_list = ShoppingList(shopping_list_number)
        self.equipment = []
        self.pawns = []
        #Karty przepychanek
        self.jostling_hand = []
        self.used_jostling_cards = [] #Stos z zużytymi kartami przep.

        for x in range (5):
            self.pawns.append(Pawn(self.color, x))


    def __repr__(self):
        return 'Name: %s, Color: %s, Mode: %s \nPawns: (%s) \nJost cards: (%s) \n' % (self.name, self.color, self.mode, self.pawns, self.jostling_hand)

    def draw_jostling_card(self, jostling_deck):
        if len(self.jostling_hand) < 3:
            for card in jostling_deck.deck:
                if card.color == self.color:
                    self.jostling_hand.append(card)
                    jostling_deck.deck.remove(card)
                    if len(self.jostling_hand) >= 3:
                        break

    def remove_jostling_card(self, card_name):
        for card in self.jostling_hand:
            if card.name == card_name:
                self.used_jostling_cards.append(self.jostling_hand.pop(self.jostling_hand.index(card)))

    #Jeśli gracz spasował to zresetuj jego status,
    #A jeśli nie ustaw mu status jako gracz, ktory spasowal
    def do_pass(self):
            self.pass_status = True

    def has_card(self, card):
        if any(card_in_hand.name == card for card_in_hand in self.jostling_hand):
            return True
        else:
            return False

    def remove_good(self, good_name):
        for good in self.equipment:
            if good.name == good_name:
                return self.equipment.pop(self.equipment.index(good))

    def get_good(self, good_name):
        for good in self.equipment:
            if good.name == good_name:
                return self.equipment[(self.equipment.index(good))]

    def check_shopping_list(self):
        category_counts = {category: 0 for category in self.shopping_list.needed_items.keys()}

        for item in self.equipment:
            if item.category in category_counts:
                category_counts[item.category] += 1

        for category, min_quantity in self.shopping_list.needed_items.items():
            if category_counts[category] < min_quantity:
                return False

        return True

    def count_goods_by_category(self, category):
        counter = 0
        for good in self.equipment:
            if good.category == category:
                counter += 1
        return counter

