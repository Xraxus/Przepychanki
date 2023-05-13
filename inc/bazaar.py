class Bazaar():
    def __init__(self):
        self.available_goods = {"Spożywczy": [], "RTV-AGD": [], "Odzież": [], "Meblowy": [], "Kiosk": []}
        self.queue = []
        self.sale_category = "Spożywczy"

    def __repr__(self):
        return "%s" % (self.available_goods)
