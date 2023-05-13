import random

from inc.board import Board
from inc.player import Player


class Game():

    def __init__(self, names, mode, *room_name):
        self.colors_iterator = iter(['niebieski', 'zolty', 'czerwony', 'zielony', 'brazowy'])

        shopping_list_numbers = [1, 2, 3, 4, 5]
        random.shuffle(shopping_list_numbers)
        self.shopping_list_iterator = iter(shopping_list_numbers)

        self.current_player_index = 0
        self.day_count = 1
        self.current_phase = '0'
        self.mode = mode

        self.players = list()
        if self.mode == 'local':
            for name in names:
                self.players.append(Player(next(self.colors_iterator), next(self.shopping_list_iterator), name))
        elif self.mode == 'multiplayer':
            for name in names:
                self.players.append(Player(next(self.colors_iterator), next(self.shopping_list_iterator), name))
            self.start = False
        self.board = Board()

        if self.mode == 'local':
            self.jostling_draw()
        elif self.mode == 'multiplayer':
            self.room_name = room_name
            self.recorded = False

    def __repr__(self):
        return "%s" % (self.room_name)

        # print("Deck przepychanek:" + str(self.board.jostling_deck))
        #
        # print(self.board.bazaar)
        # print("Decki z towarami:" + str(self.board.goods_deck) + "\n~~~~\n")
        # # do testu dostaw
        # print("Sklepy wraz z dostawionymi towarami:\n" + str(self.board.shops) + "\n~~~~\n")

        # # Test obiektów
        # print("Deck kart dostawy:\n" + str(self.board.supply_deck) + "\n~~~~\n")
        # print("Gracze i ich staty:\n" + str(self.players) + "\n~~~~\n")

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
            if not self.players[self.current_player_index].pass_status:
                break

    # Zwraca fałsz jeśli jakiś gracz jeszcze nie spasował, prawde jesli wszyscy spasowali
    def did_all_players_pass(self):
        for player in self.players:
            if not player.pass_status:
                return False
        return True

    # Zwraca prawde jeśli jakiś gracz ma jeszcze karty, a jak żaden nie ma kart to fałsz
    def does_any_player_have_cards(self):
        for player in self.players:
            print(player.jostling_hand)
            if player.jostling_hand and not player.pass_status:
                return True
        return False

    def does_any_player_have_pawns(self):
        for player in self.players:
            if player.pawns:
                return True
        return False

    def place_pawn(self, category):
        # print("placing pawn 1")
        # next_player = self.players[self.get_next_player_index()]
        player = self.players[self.current_player_index]

        # print("placing pawn 2")

        if category == 'Bazaar':
            if player.pawns:
                self.board.bazaar.queue.append(player.pawns.pop())
                if self.does_any_player_have_pawns():  # next_player.pawns:
                    self.move_to_next_player_with_pawns()  # self.move_to_next_player()
                else:
                    return 'next players have no pawns'
            elif self.does_any_player_have_pawns():  # next_player.pawns:
                self.move_to_next_player_with_pawns()  # self.move_to_next_player()
        else:
            shop_queue = self.get_shop_queue(category)
            if player.pawns:
                shop_queue.append(player.pawns.pop())
                self.set_shop_queue(category, shop_queue)
                if self.does_any_player_have_pawns():  # next_player.pawns:
                    self.move_to_next_player_with_pawns()  # self.move_to_next_player()
                else:
                    # self.move_to_next_player()
                    return 'next players have no pawns'

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

    def get_pawn_in_queue(self, pawn_id, category):
        shop_queue = self.get_shop_queue(category)
        for obj in shop_queue:
            if obj.pawn_id == pawn_id:
                match = obj
                return match

    def use_pan(self, pawn_id, category):
        shop_queue = self.get_shop_queue(category)
        pawn = self.get_pawn_in_queue(pawn_id, category)
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
        shop_queue.insert(index + 2, pawn)
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
        player.equipment.append(
            shop.available_goods.pop(shop.available_goods.index(self.get_good_item(shop_name, good_name))))
        player.pawns.append(shop.queue.pop(shop.queue.index(pawn_id)))

    def take_good_speculant(self, pawn_id, shop_name):
        shop = self.board.shops.get(shop_name)
        self.board.bazaar.available_goods.get(shop_name).append(shop.available_goods.pop(0))
        shop.queue.append(shop.queue.pop(shop.queue.index(pawn_id)))

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
        if not shop.is_open:
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
        if not shop.is_open:
            print("remanent")
            return "remanent"
        else:
            print("zwiekszenie dostawy " + shop_name)
            if self.board.goods_deck.get(shop_name).cards:
                self.board.shops[shop_name].delivery(1, self.board.goods_deck[shop_name])

    def use_pomylka(self, good_name, start_shop, go_to_shop):
        if self.board.shops.get(start_shop).is_open == False or self.board.shops.get(go_to_shop).is_open == False:
            print("remanent")
            return "remanent"
        else:
            self.board.shops.get(go_to_shop).available_goods.append(
                self.board.shops.get(start_shop).available_goods.pop(
                    self.board.shops.get(start_shop).available_goods.index(self.get_good_item(start_shop, good_name))))

    def get_pawn_owner_index(self, pawn):
        for player in self.players:
            if player.color == pawn.color:
                return self.players.index(player)

    def get_first_pawn(self, shop_name):
        return self.board.shops.get(shop_name).queue[0]

    def can_use_card(self, card_name):
        print(self.players[self.current_player_index])
        if card_name == "Spasuj":
            return True
        elif self.players[self.current_player_index].has_card(card_name):
            return True
        else:
            return False

    def go_to_next_day(self):
        self.board.set_next_day()  # sets current_day attribute for the next day, also changes the bazaar on sale category accordingly
        self.day_count = self.day_count + 1
        if self.mode != 'multiplayer':
            self.right_shift_players()
        self.current_player_index = 0

    def move_player_item_to_bazaar(self, item_name):
        self.board.bazaar.available_goods.get(self.players[
                                                  self.get_pawn_owner_index(self.board.bazaar.queue[0])].get_good(
            item_name).category).append(
            # Remove selected item from player's eq
            self.players[self.get_pawn_owner_index(
                self.board.bazaar.queue[0])].remove_good(item_name)
        )

    def give_player_bazaar_item_and_pop_queue_first_pawn(self, category):
        self.players[self.get_pawn_owner_index(self.board.bazaar.queue[0])].equipment.append(
            self.board.bazaar.available_goods.get(category).pop(0))

        self.players[self.get_pawn_owner_index(self.board.bazaar.queue[0])].pawns.append(self.board.bazaar.queue.pop(0))

    def right_shift_players(self):
        self.players.append(self.players.pop(0))

    def reset_players_pass_status(self):
        for player in self.players:
            player.pass_status = False

    def get_next_player_with_pawns(self):
        for player in self.players:
            if self.players.index(player) == self.current_player_index:
                continue
            if player.pawns:
                return player
            return self.players[self.current_player_index]

    def move_to_next_player_with_pawns(self):
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            if not self.players[self.current_player_index].pass_status and self.players[
                self.current_player_index].pawns:
                break

    def does_any_player_have_pawns_on_board(self):
        for player in self.players:
            if len(player.pawns) < 5:
                return player
        return False

    def reshuffle_jostling_deck_at_end_of_week(self):
        for player in self.players:
            self.board.jostling_deck.deck.extend(player.used_jostling_cards)
            player.used_jostling_cards.clear()
        random.shuffle(self.board.jostling_deck.deck)

        print("~~reshuffled jostling deck")
        print("self.board.jostling_deck")

    def check_if_any_player_won(self):
        winners = []

        for player in self.players:
            if player.check_shopping_list():
                print("\n!!! " + player.name + "completed his shopping list")
                winners.append(player)
            else:
                print("\n? " + player.name + "still needs some items")

        return winners

    def does_any_player_have_cards_and_didnt_pass(self):
        for player in self.players:
            if not player.pass_status and player.jostling_hand:  # If status is True - this player did pass, we are looking for active players, so we do not care about this player
                return True
            # elif player.jostling_hand:
            #     return True
        return False

    #### MULTIPLAYER

    def add_player(self, name):
        if not self.start:
            self.players.append(Player(next(self.colors_iterator), next(self.shopping_list_iterator), name))
            return len(self.players) - 1
        else:
            return -1

    def start_game(self):
        self.start = True
        self.jostling_draw()
