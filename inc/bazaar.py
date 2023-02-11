from inc.goodsDeck import GoodsDeck

class Bazaar():
    def __init__(self):
        self.available_goods = { "Spożywczy": [], "RTV-AGD": [],"Meblowy": [],"Odzież": [],"Kiosk": []}
        self.queue = []


    def __repr__(self):
        return "%s" % (self.available_goods)