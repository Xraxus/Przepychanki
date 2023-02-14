from inc.supplyDeck import SupplyDeck
from inc.shop import Shop
from inc.bazaar import Bazaar
from inc.goodsDeck import GoodsDeck
from inc.jostlingDeck import JostlingDeck

class Board():

    def __init__(self):
        self.shop_types = ["Spożywczy", "RTV-AGD", "Odzież", "Meblowy", "Kiosk"]
        self.week_days = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"]
        self.current_day = self.week_days[0]

        self.supply_deck = SupplyDeck()  #Dostawy
        self.jostling_deck = JostlingDeck() #Przepychanki
        self.goods_deck = {
            "Spożywczy": GoodsDeck("Spożywczy"),
            "RTV-AGD": GoodsDeck("RTV-AGD"),
            "Odzież": GoodsDeck("Odzież"),
            "Meblowy": GoodsDeck("Meblowy"),
            "Kiosk": GoodsDeck("Kiosk")
        }


        self.shops = {
            "Spożywczy": Shop("Spożywczy"),
            "RTV-AGD": Shop("RTV-AGD"),
            "Odzież": Shop("Odzież"),
            "Meblowy": Shop("Meblowy"),
            "Kiosk": Shop("Kiosk")
        }

        self.bazaar = Bazaar()
        self.todays_supply_cards = []

        for shop_type in self.shop_types:
            self.bazaar.available_goods[shop_type].append(self.goods_deck[shop_type].draw())


    def draw_restock(self):
            for i in range(3):
                drawn_card = self.supply_deck.draw()
                if drawn_card is not None:
                    self.todays_supply_cards.append(drawn_card)
                    self.shops[drawn_card.category].delivery(drawn_card.amount, self.goods_deck[drawn_card.category])

    def count_by_shop_type(self, shop_type):
        return len(self.goods_deck[shop_type].cards)

    def update_bazaar_sale(self):
        self.bazaar.sale_category = self.shop_types[self.week_days.index(self.current_day)]

    #Goes to the next day of the week & updates bazaar sale accordingly
    def set_next_day(self):
        self.current_day = self.week_days[(self.week_days.index(self.current_day) + 1) % 5]
        self.update_bazaar_sale()




