from inc.board import Board
from inc.player import Player
from inc.shop import Shop
from inc.supplyDeck import SupplyDeck
from inc.goodsDeck import GoodsDeck
from inc.shoppingList import ShoppingList

import random

class Game():

    def __init__(self, names, mode):
        colors_iterator = iter(['niebieski', 'żółty', 'czerwony', 'zielony', 'brązowy'])
        shopping_list_numbers = [1, 2, 3, 4, 5]
        random.shuffle(shopping_list_numbers)
        shopping_list_iterator = iter(shopping_list_numbers)
        self.current_player_index = 0

        self.players = list()
        if mode =='local':
            for name in names:
                self.players.append(Player(next(colors_iterator), next(shopping_list_iterator), name))

        

        self.board = Board()

        self.jostling_draw()
        print("Deck przepychanek:" + str(self.board.jostling_deck))


        print(self.board.bazaar)
        print("Decki z towarami:" + str(self.board.goods_deck) + "\n~~~~\n")
        #do testu dostaw
        print("Sklepy wraz z dostawionymi towarami:\n" + str(self.board.shops) + "\n~~~~\n")

        #Test obiektów
        print("Deck kart dostawy:\n" + str(self.board.supply_deck) + "\n~~~~\n")
        print("Gracze i ich staty:\n" + str(self.players) + "\n~~~~\n")

    def get_next_player_index(self):
        return (self.current_player_index + 1) % len(self.players)

    def get_next_player(self):
        return self.players[self.get_next_player_index()]

    def get_shop_queue(self, shop_name):
        shop = self.board.shops.get(shop_name)
        if shop:
            return shop.queue
        else:
            return None

    def set_shop_queue(self, shop_name, queue):
        shop = self.board.shops.get(shop_name)
        if shop:
            shop.queue = queue
        else:
            return None

    def move_to_next_player(self):
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            if self.players[self.current_player_index].pass_status == False:
                break

    #Zwraca fałsz jeśli jakiś gracz jeszcze nie spasował, prawde jesli wszyscy spasowali
    def did_all_players_pass(self):
        for player in self.players:
            if player.pass_status == False:
                return False
        return True

    #Zwraca prawde jeśli jakiś gracz ma jeszcze karty, a jak żaden nie ma kart to fałsz
    def does_any_player_have_cards(self):
        for player in self.players:
            print(player.jostling_hand)
            if player.jostling_hand:
                return True
        return False

    def place_pawn(self, category, player_color):
        next_player = self.players[self.get_next_player_index()]
        player = [x for x in self.players if x.color == player_color][0]

        if category == 'Bazaar':
            if player.pawns:
                self.board.bazaar.queue.append(player.pawns.pop())
                if next_player.pawns:
                    self.move_to_next_player()
                else:
                    return 'player has no pawns'
        else:
            shop_queue = self.get_shop_queue(category)
            if player.pawns:
                shop_queue.append(player.pawns.pop())
                self.set_shop_queue(category, shop_queue)
                if next_player.pawns:
                    self.move_to_next_player()
                else:
                    self.move_to_next_player()
                    return 'player has no pawns'

    def place_speculant(self, shop_name):
        shop = self.board.shops.get(shop_name)
        shop.queue.append(shop.speculant.pop())

    def place_all_speculants(self):
        for shop in self.board.shops:
            self.place_speculant(shop)

    def jostling_draw(self):
        for player in self.players:
            player.draw_jostling_card(self.board.jostling_deck)
            # print("\n\n" + str(player.jostling_hand) + "\n\n")

    def get_pawn_in_queue(self,pawn_id, category):
        shop_queue = self.get_shop_queue(category)
        for obj in shop_queue:
            if obj.pawn_id == pawn_id:
                match = obj
                return match

    def use_pan(self, pawn_id, category):
        shop_queue = self.get_shop_queue(category)
        pawn = self.get_pawn_in_queue(pawn_id,category)
        index = shop_queue.index(pawn)
        if index != 0:
            shop_queue.pop(index)
            shop_queue.insert(index - 1, pawn)
            self.set_shop_queue(category, shop_queue)

    def use_matka(self, pawn_id, category):
        shop_queue = self.get_shop_queue(category)
        pawn = self.get_pawn_in_queue(pawn_id, category)
        index = shop_queue.index(pawn)
        if index != 0:
            shop_queue.pop(index)
            shop_queue.insert(0, pawn)
            self.set_shop_queue(category, shop_queue)

    def use_krytyka(self, pawn_id, category):
        shop_queue = self.get_shop_queue(category)
        pawn = self.get_pawn_in_queue(pawn_id, category)
        index = shop_queue.index(pawn)
        shop_queue.pop(index)
        shop_queue.insert(index+2, pawn)
        self.set_shop_queue(category, shop_queue)

    def use_szczesliwy(self, pawn_id, start_category, go_to_category):
        start_shop_queue = self.get_shop_queue(start_category)
        go_to_shop_queue = self.get_shop_queue(go_to_category)
        pawn = self.get_pawn_in_queue(pawn_id, start_category)
        index = start_shop_queue.index(pawn)
        start_shop_queue.pop(index)
        go_to_shop_queue.insert(1, pawn)
        self.set_shop_queue(go_to_category, go_to_shop_queue)

    def use_remanent(self, shop_name):
        shop = self.board.shops.get(shop_name)
        shop.is_open = False

    def get_good_item(self, shop_name, good_name):
        shop_goods = self.board.shops.get(shop_name).available_goods
        for obj in shop_goods:
            if obj.name == good_name:
                match = obj
                return match

    def take_good_player(self, pawn_id, shop_name, good_name, player):
        shop = self.board.shops.get(shop_name)
        player.equipment.append(shop.available_goods.pop( shop.available_goods.index(self.get_good_item(shop_name, good_name)) ))
        player.pawns.append(shop.queue.pop(shop.queue.index(pawn_id)))

    def take_good_speculant(self, pawn_id, shop_name):
        shop = self.board.shops.get(shop_name)
        self.board.bazaar.available_goods.get(shop_name).append(shop.available_goods.pop())
        shop.speculant.append(shop.queue.pop(shop.queue.index(pawn_id)))

    def is_player_pawn_first(self, shop_name, player_color):
        shop_queue = self.get_shop_queue(shop_name)
        first_pawn = shop_queue[0]
        if first_pawn.color == player_color:
            print("Pionek gracza" + player_color + "jest pierwszy")
            return True
        else:
            return False

    def use_towar(self, shop_name, good_name, player):
        shop = self.board.shops.get(shop_name)
        if shop.is_open == False:
            print("remanent")
            return "Nie możesz tego zrobić - sklep jest zamknięty z powodu remanentu."
        elif not self.is_player_pawn_first(shop_name, player.color):
            print("not first")
            return "Nie możesz tego zrobić - twój pionek nie jest pierwszy"
        else:
            print("bierze se towar")
            self.take_good_player(shop.queue[0], shop_name, good_name, player)

    def use_zwiekszona(self, shop_name):
        shop = self.board.shops.get(shop_name)
        if shop.is_open == False:
            print("remanent")
            return "remanent"
        else:
            print("zwiekszenie dostawy " + shop_name)
            self.board.shops[shop_name].delivery(1, self.board.goods_deck[shop_name])

    def use_pomylka(self, good_name, start_shop, go_to_shop):
        if self.board.shops.get(start_shop).is_open == False or self.board.shops.get(go_to_shop).is_open == False:
            print("remanent")
            return "remanent"
        else:
            self.board.shops.get(go_to_shop).available_goods.append(self.board.shops.get(start_shop).available_goods.pop(self.board.shops.get(start_shop).available_goods.index(self.get_good_item(start_shop, good_name))))

    def get_pawn_owner_index(self, pawn):
        for player in self.players:
            if player.color == pawn.color:
                return self.players.index(player)

    def get_first_pawn(self, shop_name):
        return self.board.shops.get(shop_name).queue[0]

    def can_use_card(self, card_name):
        if card_name=="Spasuj":
            return True
        elif self.players[self.current_player_index].has_card(card_name):
            return True
        else:
            return False
