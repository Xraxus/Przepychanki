from inc.goodsCard import GoodsCard
import random
class GoodsDeck():
    shop_types = ["Spożywczy", "RTV-AGD", "Odzież", "Meblowy", "Kiosk"]
    def __init__(self, shop_name):
        self.shop_name = shop_name
        self.cards = list()

        original_cards = {
            "Spożywczy": [
                ("Piwo", "To jest moje paliwo"),
                ("Chleb", "Jeszcze gorący"),
                ("Bombonierka", "Pełna czekoladowych bomb"),
                ("Konserwa", "Polskie mięsko"),
                ("Kiszka", "Wyrób mięsny"),
                ("Oranżada", "Smak z dzieciństwa"),
                ("Twaróg", "Dobre źródło białka"),
                ("Sól", "Żeby zupa była słona"),
                ("Herbata", "Chwila relaksu"),
                ("Cukier", "Dla osłody życia"),
                ("Kawa", "Doda ci siły!"),
                ("Ocet", "Zawsze się przyda")
            ],
            "RTV-AGD": [
                ("Termos", "By ciepło zawsze było blisko"),
                ("Lodówka", "Mrozi..."),
                ("Mikser", "Wszędzie potrafi namieszać"),
                ("Maszyna do szycia", "Dla samodzielnych"),
                ("Syfon", "Francuski wynalazek"),
                ("Magnetofon", "Zapamięta wszystko"),
                ("Projektor", "Do kina domowego"),
                ("Kuchenka", "Nie poparz się!"),
                ("Aparat", "Zdjęcia najlepszej jakości"),
                ("Telefon", "Przedzwoń do sąsiada!"),
                ("Telewizor", "Atrakcja dla każdego domu"),
                ("Radiomagnetofon", "Dwa w jednym!")
            ],
            "Meblowy": [
                ("Stołek", "Solidny i stabilny"),
                ("Lampa", "Do przytulnego pokoju"),
                ("Krzesło", "Pełna wygoda"),
                ("Żyrandol", "Blask i urok"),
                ("Lampka", "Dla oświecenia umysłu"),
                ("Schowek", "Przetestuj jego pojemność!"),
                ("Stolik składany", "Cóż za oszczędność miejsca"),
                ("Stolik kawowy", "Sąsiad ci pozazdrości..."),
                ("Fotel", "Cóż za luksus"),
                ("Obraz", "Kultura wyższa"),
                ("Wersalka", "Do siedzenia i spania"),
                ("Meblościanka", "Królowa salonów")
            ],
            "Odzież":[
                ("Czapka z daszkiem", "Chroni przed słońcem"),
                ("Futro", "Pełen styl"),
                ("Krawat", "Kultura i elegancja"),
                ("Sandały", "Wygodne i przewiewne"),
                ("Koszula", "W piękne paski"),
                ("Kozaki", "Relaks..."),
                ("Palto", "Polska skóra"),
                ("Pasek", "Skóra naturalna"),
                ("Sukienka", "Niejedna ci pozazdrości"),
                ("Okulary", "Stylowe akcesorium"),
                ("Torebka", "Dla kobiety nowoczesnej"),
                ("Zestaw koszul", "Dla poważnych")
            ],
            "Kiosk":[
                ("Perfumy", "By uwodzić zapachem"),
                ("Gra elektroniczna", "Marzenie dzeciaków"),
                ("Mydło", "Wszystko umyje"),
                ("Przemysławka", "Lekki zapach cytrusów"),
                ("Szczoteczka", "Dla zdrowych zębów"),
                ("Przewodnik", "Malbork i okolice"),
                ("Proszek do prania", "Sam pierze!"),
                ("Lalka czarnulka", "Czarna perła"),
                ("Golarka", "Ostra jak przecinak"),
                ("Płyn do naczyń", "Ludwiku, do rondla"),
                ("Papierosy", "Klubowe"),
                ("Kredki", "Pomaluj mi życie")
            ]
        }


        for category in self.shop_types:
            random.shuffle(original_cards[category])
            if self.shop_name == category:
                for card, description in original_cards[category]:
                    self.cards.append(GoodsCard(self.shop_name, card, description))

    def __repr__(self):
         return "%s: \n%s" % (self.shop_name, self.cards)

    def draw(self):
        if self.count() > 0:
            return self.cards.pop()
        else:
            return "nic"

    def count(self):
        return len(self.cards)



