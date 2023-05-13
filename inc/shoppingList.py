class ShoppingList:

    def __init__(self, shopping_list_number):
        self.shopping_list_number = shopping_list_number
        self.needed_items = dict()
        self.shopping_list_name = ""

        original_lists = {
            1: {  # Urządzić kuchie
                "Spożywczy": 0,
                "RTV-AGD": 4,
                "Odzież": 2,
                "Meblowy": 3,
                "Kiosk": 1
            },
            2: {  # Pierwsza komunia
                "Spożywczy": 4,
                "RTV-AGD": 3,
                "Odzież": 1,
                "Meblowy": 2,
                "Kiosk": 0
            },
            3: {  # Impreza na działce
                "Spożywczy": 3,
                "RTV-AGD": 2,
                "Odzież": 0,
                "Meblowy": 1,
                "Kiosk": 4
            },
            4: {  # Wycieczka szkolna dzieci
                "Spożywczy": 2,
                "RTV-AGD": 1,
                "Odzież": 4,
                "Meblowy": 0,
                "Kiosk": 3
            },
            5: {  # Umeblować mieszkanie
                "Spożywczy": 1,
                "RTV-AGD": 0,
                "Odzież": 3,
                "Meblowy": 4,
                "Kiosk": 2
            }
        }

        if self.shopping_list_number == 1:
            self.shopping_list_name = "Urządzić kuchnię"
        elif self.shopping_list_number == 2:
            self.shopping_list_name = "Pierwsza komunia"
        elif self.shopping_list_number == 3:
            self.shopping_list_name = "Impreza na działce"
        elif self.shopping_list_number == 4:
            self.shopping_list_name = "Wycieczka szkolna dzieci"
        elif self.shopping_list_number == 5:
            self.shopping_list_name = "Umeblować mieszkanie"

        for x in original_lists[shopping_list_number].items():
            self.needed_items.update({x})

    def __repr__(self):
        return "%s. %s: %s" % (self.shopping_list_number, self.shopping_list_name, self.needed_items)
