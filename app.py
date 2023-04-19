import uuid

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import session

app = Flask(__name__, static_url_path='/static')
app.secret_key = '40a1f8b6143c4436905d49a2aff4bf81'

games = {}
multiplayer_games = {}

from inc.game import Game


@app.route('/')
def home():
    if 'key' not in session:
        session['key'] = uuid.uuid4()

    return render_template('home.htm')


def check_simple():
    if session.get('key') and 'games' in globals():
        return True
    return False


def check():
    if session.get('key') and 'games' in globals() and session.get('key') in games:
        return True
    return False


def check_local_phase(phase_index):
    if games[session['key']].current_phase != phase_index:
        if games[session['key']].current_phase == '0':
            return redirect('/local/phase0', code=302)
        elif games[session['key']].current_phase == '1':
            return redirect('/local/phase1', code=302)
        elif games[session['key']].current_phase == '1_kolega':
            return redirect('/local/phase1_use_kolega', code=302)
        elif games[session['key']].current_phase == '2':
            return redirect('/local/phase2', code=302)
        elif games[session['key']].current_phase == '3':
            return redirect('/local/phase3', code=302)
        elif games[session['key']].current_phase == 'tpz':
            return redirect('/local/phase_tpz', code=302)
        elif games[session['key']].current_phase == 'win':
            return redirect('/local/win', code=302)
        elif games[session['key']].current_phase == 'withdraw':
            return redirect('/local/phase_withdraw', code=302)
        else:
            return redirect('/local/form', code=302)
    else:
        return False

def multiplayer_check_simple():
    if session.get('game_uuid') and 'multiplayer_games' in globals():
        return True
    return False

def multiplayer_check():
    if session.get('game_uuid') and 'multiplayer_games' in globals() and session.get('game_uuid') in multiplayer_games:
        return True
    return False


def check_multiplayer_phase(phase_index):
    if multiplayer_games[session['game_uuid']].current_phase != phase_index:
        if multiplayer_games[session['game_uuid']].current_phase == '0':
            return redirect('/multiplayer/phase0', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == '1':
            return redirect('/multiplayer/phase1', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == '1_kolega':
            return redirect('/multiplayer/phase1_use_kolega', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == '2':
            return redirect('/multiplayer/phase2', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == '3':
            return redirect('/multiplayer/phase3', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == 'tpz':
            return redirect('/multiplayer/phase_tpz', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == 'win':
            return redirect('/multiplayer/win', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == 'withdraw':
            return redirect('/multiplayer/phase_withdraw', code=302)
        else:
            return redirect('/', code=302)
    else:
        return False


@app.route('/info', methods=['GET'])
def info():
    return render_template('info.htm')


############################### LOCAL(HOTSEAT) ###############################

@app.route('/local', methods=['GET', 'POST'])
def local():
    return redirect('/local/form', code=302)


@app.route('/local/form', methods=['GET', 'POST'])
def local_form():
    if not check_simple():
        return redirect('/', code=302)

    if request.method == 'POST':
        players = [x for x in request.form.getlist('names') if x]
        # print(players)

        if 2 <= len(players) <= 5:
            return new_local_game(players)

    return render_template('local/form.htm')


def new_local_game(names):
    if not check_simple():
        return redirect('/', code=302)

    games[session['key']] = Game(names, 'local')

    return redirect('/local/phase0', code=302, )


# Faza następująca w kolejnych rundach, przed faza ustawiania pionków
# Gracze mogą wycofać swoje pionki, żeby ustawić je w kolejnej fazie (fazie 0)
@app.route('/local/phase_withdraw', methods=['GET', 'POST'])
def local_withdraw():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('withdraw')
    if phase_check:
        return phase_check

    if request.method == 'POST':  # 'do_pass', 'shop_name', 'pawn_id'
        if 'do_pass' in request.form and request.form['do_pass'] == 'yes':
            games[session['key']].players[games[session['key']].current_player_index].do_pass()
            if not games[session['key']].did_all_players_pass():
                games[session['key']].move_to_next_player()
        else:
            if games[session['key']].get_pawn_in_queue(request.form['pawn_id'], request.form['shop_name']) is not None:
                print(games[session['key']].board.shops.get(request.form['shop_name']).queue)
                games[session['key']].players[games[session['key']].current_player_index].pawns.append(
                    games[session['key']].board.shops.get(request.form['shop_name']).queue.pop(
                        games[session['key']].board.shops.get(request.form['shop_name']).queue.index(
                            games[session['key']].get_pawn_in_queue(request.form['pawn_id'],
                                                                    request.form['shop_name']))))
                if not games[session['key']].did_all_players_pass():
                    games[session['key']].move_to_next_player()

    if games[session['key']].did_all_players_pass() or not games[session['key']].does_any_player_have_pawns_on_board():
        games[session['key']].current_player_index = 0
        games[session['key']].reset_players_pass_status()

        games[session['key']].current_phase = '0'
        return redirect('/local/phase0', code=302)

    return render_template('local/phase_withdraw.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index])


# Faza 0 - ustawianie pionków + dostarczenie towarów na koniec ustawiania
@app.route('/local/phase0', methods=['GET', 'POST'])
def local_phase0():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('0')
    if phase_check:
        return phase_check

    if request.method == 'POST':
        games[session['key']].place_pawn(
            request.form['shop_name'])  # places pawn and moves to the next player that has a pawn

        if not games[session['key']].does_any_player_have_pawns():
            if games[session['key']].day_count == 1:
                games[session['key']].place_all_speculants()
            games[session['key']].current_player_index = 0
            games[session['key']].board.draw_restock()

            games[session['key']].current_phase = '1'
            return redirect('/local/phase1', code=302)
        else:
            return render_template('local/phase0.htm', game=games[session['key']],
                                   player=games[session['key']].players[games[session['key']].current_player_index])
    else:
        games[session['key']].current_player_index = 0
        if not games[session['key']].does_any_player_have_pawns():
            if games[session['key']].day_count == 1:
                games[session['key']].place_all_speculants()
            games[session['key']].board.draw_restock()

            games[session['key']].current_phase = '1'
            return redirect('/local/phase1', code=302)
        else:
            if not games[session['key']].players[games[session['key']].current_player_index].pawns:
                games[session['key']].move_to_next_player_with_pawns()
            return render_template('local/phase0.htm', game=games[session['key']],
                                   player=games[session['key']].players[games[session['key']].current_player_index],
                                   pawns=games[session['key']].players[
                                       games[session['key']].current_player_index].pawns)


# Faza 1 - użyj kart przepychanek kolejkowych, by zapewnić sobie najlepszą pozycje
@app.route('/local/phase1', methods=['GET', 'POST'])
def local_phase1():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if request.method == 'POST':
        picked_card = request.form['card']

        if picked_card == "Pan tu nie stał":
            return redirect('/local/phase1_use_pan')
        elif picked_card == "Matka z dzieckiem":
            return redirect('/local/phase1_use_matka')
        elif picked_card == "Krytyka władzy":
            return redirect('/local/phase1_use_krytyka')
        elif picked_card == "Lista społeczna":
            return redirect('/local/phase1_use_lista')
        elif picked_card == "Szczęśliwy traf":
            return redirect('/local/phase1_use_szczesliwy')
        elif picked_card == "Remanent":
            return redirect('/local/phase1_use_remanent')
        elif picked_card == "Towar spod lady":
            return redirect('/local/phase1_use_towar')
        elif picked_card == "Kolega w Komitecie":
            games[session['key']].current_phase = '1_kolega'
            return redirect('/local/phase1_use_kolega')
        elif picked_card == "Zwiększona dostawa":
            return redirect('/local/phase1_use_zwiekszona')
        elif picked_card == "Pomyłka w dostawie":
            return redirect('/local/phase1_use_pomylka')
        elif picked_card == "Spasuj":
            games[session['key']].players[games[session['key']].current_player_index].do_pass()
            if not games[session['key']].does_any_player_have_cards_and_didnt_pass():

                games[session['key']].current_phase = '2'
                return redirect('/local/phase2', code=302)
            else:
                games[session['key']].move_to_next_player()
                return render_template('local/phase1.htm', game=games[session['key']],
                                       player=games[session['key']].players[games[session['key']].current_player_index])

    else:
        if not games[session['key']].does_any_player_have_cards_and_didnt_pass():
            games[session['key']].current_phase = '2'
            return redirect('/local/phase2', code=302)
        return render_template('local/phase1.htm', game=games[session['key']],
                               player=games[session['key']].players[games[session['key']].current_player_index])


@app.route('/local/phase1_use_pan', methods=['GET', 'POST'])
def local_phase1_use_pan():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Pan tu nie stał"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            games[session['key']].use_pan(request.form['pawn_id'], request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Pan tu nie stał")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_pan.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Pan tu nie stał")


@app.route('/local/phase1_use_matka', methods=['GET', 'POST'])
def local_phase1_use_matka():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Matka z dzieckiem"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            games[session['key']].use_matka(request.form['pawn_id'], request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Matka z dzieckiem")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_matka.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Matka z dzieckiem")


@app.route('/local/phase1_use_krytyka', methods=['GET', 'POST'])
def local_phase1_use_krytyka():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Krytyka władzy"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            games[session['key']].use_krytyka(request.form['pawn_id'], request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Krytyka władzy")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_krytyka.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Krytyka władzy")


@app.route('/local/phase1_use_lista', methods=['GET', 'POST'])
def local_phase1_use_lista():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Lista społeczna"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            games[session['key']].get_shop_queue(request.form['shop_name']).reverse()
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Lista społeczna")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_lista.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Lista społeczna")


@app.route('/local/phase1_use_szczesliwy', methods=['GET', 'POST'])
def local_phase1_use_szczesliwy():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Szczęśliwy traf"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            split_values = request.form['pawn_id'].split('#', 1)
            games[session['key']].use_szczesliwy(split_values[0], split_values[1],
                                                 request.form['go_to_shop'])  # pawn_id, start_shop, go_to_shop
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Szczęśliwy traf")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_szczesliwy.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Szczęśliwy traf")


@app.route('/local/phase1_use_remanent', methods=['GET', 'POST'])
def local_phase1_use_remanent():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Remanent"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            games[session['key']].use_remanent(request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card("Remanent")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_remanent.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Remanent")


@app.route('/local/phase1_use_towar', methods=['GET', 'POST'])
def local_phase1_use_towar():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Towar spod lady"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            outcome = games[session['key']].use_towar(request.form['shop_name'], request.form['good'],
                                                      games[session['key']].players[
                                                          games[session['key']].current_player_index])
            if outcome is None:
                games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                    "Towar spod lady")
                games[session['key']].move_to_next_player()
            else:
                return render_template('local/phase1_use_towar.htm', game=games[session['key']],
                                       player=games[session['key']].players[games[session['key']].current_player_index],
                                       picked_card="Towar spod lady", message=outcome)
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_towar.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Towar spod lady")


@app.route('/local/phase1_use_kolega', methods=['GET', 'POST'])
def local_phase1_use_kolega():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1_kolega')
    if phase_check:
        return phase_check

    if request.method == 'POST' or not games[session['key']].can_use_card("Kolega w Komitecie"):
        games[session['key']].move_to_next_player()
        games[session['key']].current_phase = '1'
        return redirect('/local/phase1', code=302)
    else:
        games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
            "Kolega w Komitecie")

    return render_template('local/phase1_use_kolega.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Kolega w Komitecie")


@app.route('/local/phase1_use_zwiekszona', methods=['GET', 'POST'])
def local_phase1_use_zwiekszona():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Zwiększona dostawa"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            games[session['key']].use_zwiekszona(request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Zwiększona dostawa")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_zwiekszona.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Zwiększona dostawa")


@app.route('/local/phase1_use_pomylka', methods=['GET', 'POST'])
def local_phase1_use_pomylka():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Pomyłka w dostawie"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            split_values = request.form['good_id'].split('#', 1)
            games[session['key']].use_pomylka(split_values[0], split_values[1],
                                              request.form['go_to_shop'])  # good_name, start_shop, go_to_shop
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Pomyłka w dostawie")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_pomylka.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Pomyłka w dostawie")


# Gracze i spekulanci zbierają przedmioty
@app.route('/local/phase2', methods=['GET', 'POST'])
def local_phase2():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('2')
    if phase_check:
        return phase_check

    if request.method == 'POST':
        if games[session['key']].board.shops.get(request.form['shop_name']).available_goods and games[
            session['key']].board.shops.get(request.form['shop_name']).queue:
            games[session['key']].take_good_player(games[session['key']].get_first_pawn(request.form['shop_name']),
                                                   request.form['shop_name'], request.form['good_name'],
                                                   games[session['key']].players[
                                                       games[session['key']].get_pawn_owner_index(
                                                           games[session['key']].get_first_pawn(
                                                               request.form['shop_name']))])

    for shop in games[session['key']].board.shops.values():
        # did_speculant_take_good = False
        for _ in shop.queue:
            if shop.is_open and shop.available_goods:
                if shop.queue[0].color not in ['Kiosk', 'Meblowy', 'Spożywczy', 'Odzież', 'RTV-AGD']:
                    return render_template('local/phase2.htm', game=games[session['key']],
                                           player=games[session['key']].players[
                                               games[session['key']].get_pawn_owner_index(shop.queue[0])],
                                           shop=shop, owner='player')
                else:
                    if not shop.did_speculant_take_good:  # Check if speculant took a good in this round, this variable determines if speculant took a good in this shop and round already.
                        games[session['key']].take_good_speculant(games[session['key']].get_first_pawn(shop.name),
                                                                  shop.name)
                        shop.did_speculant_take_good = True  # Speculant takes good, so make this True

    games[session['key']].board.reset_speculant_good_status()
    games[session['key']].current_phase = '3'
    return redirect('/local/phase3', code=302)


# Bazaar trades
@app.route('/local/phase3', methods=['GET', 'POST'])
def local_phase3():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('3')
    if phase_check:
        return phase_check

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase3', code=302)

        if 'cancel' in request.form and request.form['cancel'] == 'yes':
            games[session['key']].players[games[session['key']].get_pawn_owner_index(
                games[session['key']].board.bazaar.queue[0])].pawns.append(
                games[session['key']].board.bazaar.queue.pop(0))

        if 'stage' in request.form:
            if request.form[
                'stage'] == "1":  # Make decision depending on stage variable sent via form input of type hidden
                if request.form['shop_name'] == games[session['key']].board.bazaar.sale_category:
                    # Stage 2a - IF item is in sale category, select ONE item from your inventory you want to trade - radio button
                    return render_template('local/phase3.htm', game=games[session['key']],
                                           player=games[session['key']].players[
                                               games[session['key']].get_pawn_owner_index(
                                                   games[session['key']].board.bazaar.queue[0])],
                                           stage='2a', category=request.form['shop_name'])
                else:
                    # Stage 2b - if item is not in the sale category, select TWO items from your inventory you want to trade - checkbox with limit signaled by an alert
                    return render_template('local/phase3.htm', game=games[session['key']],
                                           player=games[session['key']].players[
                                               games[session['key']].get_pawn_owner_index(
                                                   games[session['key']].board.bazaar.queue[0])],
                                           stage='2b', category=request.form['shop_name'])

            elif request.form['stage'] == "2a" and 'item_name' in request.form:  # one to one
                item = request.form['item_name']
                category = request.form['category']

                games[session['key']].move_player_item_to_bazaar(item)

                # Add item of selected category to player's eq & pop the pawn back to player hand
                games[session['key']].give_player_bazaar_item_and_pop_queue_first_pawn(category)

            elif request.form['stage'] == "2b" and 'item_name' in request.form:  # two to one
                items = request.form.getlist('item_name')
                category = request.form['category']

                for item in items:
                    games[session['key']].move_player_item_to_bazaar(item)

                # Add item of selected category to player's eq & pop the pawn back to player hand
                games[session['key']].give_player_bazaar_item_and_pop_queue_first_pawn(category)

    if games[session['key']].board.bazaar.queue:
        # Stage 1 - choose the category from which you want to receive an item or go back and take your pawn with you
        return render_template('local/phase3.htm', game=games[session['key']],
                               player=games[session['key']].players[games[session['key']].get_pawn_owner_index(
                                   games[session['key']].board.bazaar.queue[0])],
                               stage='1')
    else:
        games[session['key']].current_phase = 'tpz'
        return redirect('/local/phase_tpz', code=302)


@app.route('/local/phase_tpz', methods=['GET', 'POST'])
def phase_tpz():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('tpz')
    if phase_check:
        return phase_check

    if games[session['key']].check_if_any_player_won():
        games[session['key']].current_phase = 'win'
        return redirect('/local/win', code=302)

    # Remove used supply cards
    games[session['key']].board.todays_supply_cards.clear()

    # Stop 'remanent' cards
    games[session['key']].board.reset_remanents()

    # Reset player pass status
    games[session['key']].reset_players_pass_status()

    if games[session['key']].board.current_day == "Piątek":
        games[session['key']].board.reset_supply_deck()
        games[session['key']].reshuffle_jostling_deck_at_end_of_week()

    # Draw jostling cards so every player has 3 of them in hand (unless the player ran out of cards)
    games[session['key']].jostling_draw()

    # Set next day of a week
    # Move to next sale_category on bazaar
    games[session['key']].go_to_next_day()

    games[session['key']].current_phase = 'withdraw'
    return redirect('/local/phase_withdraw', code=302)


@app.route('/local/win', methods=['GET', 'POST'])
def local_win():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('win')
    if phase_check:
        return phase_check

    winners = games[session['key']].check_if_any_player_won()
    return render_template('local/win.htm', game=games[session['key']], winners=winners)


###############################
############################### MULTIPLAYER ###############################

@app.route('/multiplayer/rooms')
def rooms():
    return render_template('multiplayer/rooms.htm', multiplayer_games=multiplayer_games)


@app.route('/multiplayer/form', methods=['GET', 'POST'])
def multiplayer_form():
    if not multiplayer_check_simple():
        return redirect('/', code=302)

    if request.method == 'POST':
        players = [x for x in request.form.getlist('names') if x]

        return new_multiplayer_game(players)

    return render_template('multiplayer/form.htm')


def new_multiplayer_game(name):
    if not multiplayer_check_simple():
        return redirect('/', code=302)
    session['game_uuid'] = str(uuid.uuid4())
    session['player_id'] = 0
    multiplayer_games[session['game_uuid']] = Game(name, 'multiplayer')
    return redirect('/multiplayer/wait', code=302)


@app.route('/multiplayer/form_join/<room>', methods=['GET', 'POST'])
def form_join(room):
    if not multiplayer_check_simple():
        return redirect('/', code=302)

    if request.method == 'POST':
        players = [x for x in request.form.getlist('names') if x]
        game_uuid = request.form.getlist('room')[0]
        print(players)
        print(game_uuid)
        print(multiplayer_games)
        session['player_id'] = multiplayer_games[game_uuid].add_player(players[0])
        session['game_uuid'] = game_uuid
        return redirect('/multiplayer/join', code=302)

    return render_template('multiplayer/form_join.htm', room=room)


@app.route('/multiplayer/wait')
def wait():
    if not multiplayer_check():
        return redirect('/', code=302)

    return render_template('multiplayer/wait.htm', game=multiplayer_games[session['game_uuid']])


@app.route('/multiplayer/join/')
def join():
    if not multiplayer_check():
        return redirect('/', code=302)

    if multiplayer_games[session['game_uuid']].start:
        multiplayer_games[session['game_uuid']].current_player_index = 0
        return redirect('/multiplayer/phase0', code=302)

    return render_template('multiplayer/join.htm')


@app.route('/multiplayer/start_game')
def start_game():
    if not multiplayer_check():
        return redirect('/', code=302)

    if not multiplayer_games[session['game_uuid']].start:
        multiplayer_games[session['game_uuid']].start_game()
        multiplayer_games[session['game_uuid']].current_player_index = 0
        return redirect('/multiplayer/phase0', code=302)

    multiplayer_games[session['game_uuid']].current_player_index = 0
    return redirect('/multiplayer/phase0', code=302)


# @app.route('/multiplayer/board')
# def board():
#     return render_template('multiplayer/test.htm', game=multiplayer_games[session['game_uuid']],
#                            id_gracza=session['player_id'])


@app.route('/multiplayer/phase_withdraw', methods=['GET', 'POST'])
def multiplayer_withdraw():
    if not multiplayer_check_simple():
        return redirect('/', code=302)

    phase_check = check_multiplayer_phase('withdraw')
    if phase_check:
        return phase_check

    if request.method == 'POST':  # 'do_pass', 'shop_name', 'pawn_id'
        if 'do_pass' in request.form and request.form['do_pass'] == 'yes':
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].do_pass()
            if not multiplayer_games[session['game_uuid']].did_all_players_pass():
                multiplayer_games[session['game_uuid']].move_to_next_player()
        else:
            if multiplayer_games[session['game_uuid']].get_pawn_in_queue(request.form['pawn_id'],
                                                                         request.form['shop_name']) is not None:
                multiplayer_games[session['game_uuid']].players[
                    multiplayer_games[session['game_uuid']].current_player_index].pawns.append(
                    multiplayer_games[session['game_uuid']].board.shops.get(request.form['shop_name']).queue.pop(
                        multiplayer_games[session['game_uuid']].board.shops.get(request.form['shop_name']).queue.index(
                            multiplayer_games[session['game_uuid']].get_pawn_in_queue(request.form['pawn_id'],
                                                                                      request.form['shop_name']))))
                if not multiplayer_games[session['game_uuid']].did_all_players_pass():
                    multiplayer_games[session['game_uuid']].move_to_next_player()

    if multiplayer_games[session['game_uuid']].did_all_players_pass() or not multiplayer_games[
        session['game_uuid']].does_any_player_have_pawns_on_board():
        multiplayer_games[session['game_uuid']].current_player_index = 0
        multiplayer_games[session['game_uuid']].reset_players_pass_status()

        multiplayer_games[session['game_uuid']].current_phase = '0'
        return redirect('/multiplayer/phase0', code=302)

    if not multiplayer_games[session['game_uuid']].current_player_index == session[
        'player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   session['player_id']])
    else:
        return render_template('local/phase_withdraw.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   multiplayer_games[session['game_uuid']].current_player_index])


@app.route('/multiplayer/phase0', methods=['GET', 'POST'])
def multiplayer_phase0():
    if not multiplayer_check_simple():
        return redirect('/', code=302)

    phase_check = check_multiplayer_phase('0')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        if request.method == 'POST':
            multiplayer_games[session['game_uuid']].place_pawn(
                request.form['shop_name'])  # places pawn and moves to the next player that has a pawn

            if not multiplayer_games[session[
                'game_uuid']].does_any_player_have_pawns():  # if none of the player has pawns, then initiate process of starting next phasenext
                if multiplayer_games[session['game_uuid']].day_count == 1:
                    multiplayer_games[session['game_uuid']].place_all_speculants()
                multiplayer_games[session['game_uuid']].current_player_index = 0
                multiplayer_games[session['game_uuid']].board.draw_restock()

                multiplayer_games[session['game_uuid']].current_phase = '1'
                return redirect('/multiplayer/phase1', code=302)
            else:
                if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
                    return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                                           player=multiplayer_games[session['game_uuid']].players[session['player_id']])
                else:
                    return render_template('local/phase0.htm', game=multiplayer_games[session['game_uuid']],
                                           player=games[session['key']].players[
                                               games[session['key']].current_player_index])
        else:
            if not multiplayer_games[session['game_uuid']].does_any_player_have_pawns():
                if multiplayer_games[session['game_uuid']].day_count == 1:
                    multiplayer_games[session['game_uuid']].place_all_speculants()
                multiplayer_games[session['game_uuid']].board.draw_restock()

                multiplayer_games[session['game_uuid']].current_phase = '1'
                return redirect('/multiplayer/phase1', code=302)
            else:
                if not multiplayer_games[session['game_uuid']].players[
                    multiplayer_games[session['game_uuid']].current_player_index].pawns:
                    multiplayer_games[session['game_uuid']].move_to_next_player_with_pawns()
                return render_template('local/phase0.htm', game=multiplayer_games[session['game_uuid']],
                                       player=multiplayer_games[session['game_uuid']].players[
                                           multiplayer_games[session['game_uuid']].current_player_index])


# Faza 1 - użyj kart przepychanek kolejkowych, by zapewnić sobie najlepszą pozycje
@app.route('/multiplayer/phase1', methods=['GET', 'POST'])
def multiplayer_phase1():
    if not multiplayer_check_simple():
        return redirect('/', code=302)

    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        if request.method == 'POST':
            picked_card = request.form['card']

            if picked_card == "Pan tu nie stał":
                return redirect('/multiplayer/phase1_use_pan')
            elif picked_card == "Matka z dzieckiem":
                return redirect('/multiplayer/phase1_use_matka')
            elif picked_card == "Krytyka władzy":
                return redirect('/multiplayer/phase1_use_krytyka')
            elif picked_card == "Lista społeczna":
                return redirect('/multiplayer/phase1_use_lista')
            elif picked_card == "Szczęśliwy traf":
                return redirect('/multiplayer/phase1_use_szczesliwy')
            elif picked_card == "Remanent":
                return redirect('/multiplayer/phase1_use_remanent')
            elif picked_card == "Towar spod lady":
                return redirect('/multiplayer/phase1_use_towar')
            elif picked_card == "Kolega w Komitecie":
                multiplayer_games[session['game_uuid']].current_phase = '1_kolega'
                return redirect('/multiplayer/phase1_use_kolega')
            elif picked_card == "Zwiększona dostawa":
                return redirect('/multiplayer/phase1_use_zwiekszona')
            elif picked_card == "Pomyłka w dostawie":
                return redirect('/multiplayer/phase1_use_pomylka')
            elif picked_card == "Spasuj":
                multiplayer_games[session['game_uuid']].players[
                    multiplayer_games[session['game_uuid']].current_player_index].do_pass()
                if not multiplayer_games[session['game_uuid']].does_any_player_have_cards_and_didnt_pass():

                    multiplayer_games[session['game_uuid']].current_phase = '2'
                    return redirect('/multiplayer/phase2', code=302)
                else:
                    multiplayer_games[session['game_uuid']].move_to_next_player()
                    return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                                           player=multiplayer_games[session['game_uuid']].players[session['player_id']])
        else:
            if not multiplayer_games[session['game_uuid']].does_any_player_have_cards_and_didnt_pass():
                multiplayer_games[session['game_uuid']].current_phase = '2'
                return redirect('/multiplayer/phase2', code=302)
            return render_template('local/phase1.htm', game=multiplayer_games[session['game_uuid']],
                                   player=multiplayer_games[session['game_uuid']].players[
                                       multiplayer_games[session['game_uuid']].current_player_index])


@app.route('/multiplayer/phase1_use_pan', methods=['GET', 'POST'])
def multiplayer_phase1_use_pan():
    if not multiplayer_check_simple():
        return redirect('/', code=302)

    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Pan tu nie stał"):
        return redirect('/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].use_pan(request.form['pawn_id'], request.form['shop_name'])
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Pan tu nie stał")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/multiplayer/phase1', code=302)
    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        return render_template('local/phase1_use_pan.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   multiplayer_games[session['game_uuid']].current_player_index],
                               picked_card="Pan tu nie stał")


@app.route('/multiplayer/phase1_use_matka', methods=['GET', 'POST'])
def multiplayer_phase1_use_matka():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Matka z dzieckiem"):
        return redirect('/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].use_matka(request.form['pawn_id'], request.form['shop_name'])
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Matka z dzieckiem")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/multiplayer/phase1', code=302)
    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        return render_template('local/phase1_use_matka.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   multiplayer_games[session['game_uuid']].current_player_index],
                               picked_card="Matka z dzieckiem")


@app.route('/multiplayer/phase1_use_krytyka', methods=['GET', 'POST'])
def multiplayer_phase1_use_krytyka():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Krytyka władzy"):
        return redirect('/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].use_krytyka(request.form['pawn_id'], request.form['shop_name'])
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Krytyka władzy")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/multiplayer/phase1', code=302)

    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        return render_template('local/phase1_use_krytyka.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   multiplayer_games[session['game_uuid']].current_player_index],
                               picked_card="Krytyka władzy")


@app.route('/multiplayer/phase1_use_lista', methods=['GET', 'POST'])
def multiplayer_phase1_use_lista():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Lista społeczna"):
        return redirect('/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].get_shop_queue(request.form['shop_name']).reverse()
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Lista społeczna")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/multiplayer/phase1', code=302)
    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        return render_template('local/phase1_use_lista.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   multiplayer_games[session['game_uuid']].current_player_index],
                               picked_card="Lista społeczna")


@app.route('/multiplayer/phase1_use_szczesliwy', methods=['GET', 'POST'])
def multiplayer_phase1_use_szczesliwy():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Szczęśliwy traf"):
        return redirect('/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/multiplayer/phase1', code=302)
        else:
            split_values = request.form['pawn_id'].split('#', 1)
            multiplayer_games[session['game_uuid']].use_szczesliwy(split_values[0], split_values[1],
                                                                   request.form[
                                                                       'go_to_shop'])  # pawn_id, start_shop, go_to_shop
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Szczęśliwy traf")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/multiplayer/phase1', code=302)
    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        return render_template('local/phase1_use_szczesliwy.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   multiplayer_games[session['game_uuid']].current_player_index],
                               picked_card="Szczęśliwy traf")


@app.route('/multiplayer/phase1_use_remanent', methods=['GET', 'POST'])
def multiplayer_phase1_use_remanent():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Remanent"):
        return redirect('/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].use_remanent(request.form['shop_name'])
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card("Remanent")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/multiplayer/phase1', code=302)
    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        return render_template('local/phase1_use_remanent.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   multiplayer_games[session['game_uuid']].current_player_index],
                               picked_card="Remanent")


@app.route('/multiplayer/phase1_use_towar', methods=['GET', 'POST'])
def multiplayer_phase1_use_towar():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Towar spod lady"):
        return redirect('/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/multiplayer/phase1', code=302)
        else:
            outcome = multiplayer_games[session['game_uuid']].use_towar(request.form['shop_name'], request.form['good'],
                                                                        multiplayer_games[session['game_uuid']].players[
                                                                            multiplayer_games[session[
                                                                                'game_uuid']].current_player_index])
            if outcome is None:
                multiplayer_games[session['game_uuid']].players[
                    multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                    "Towar spod lady")
                multiplayer_games[session['game_uuid']].move_to_next_player()
            else:
                if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
                    return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                                           player=multiplayer_games[session['game_uuid']].players[session['player_id']])
                else:
                    return render_template('local/phase1_use_towar.htm', game=multiplayer_games[session['game_uuid']],
                                           player=multiplayer_games[session['game_uuid']].players[
                                               multiplayer_games[session['game_uuid']].current_player_index],
                                           picked_card="Towar spod lady", message=outcome)
        return redirect('/multiplayer/phase1', code=302)
    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        return render_template('local/phase1_use_towar.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   multiplayer_games[session['game_uuid']].current_player_index],
                               picked_card="Towar spod lady")


@app.route('/multiplayer/phase1_use_kolega', methods=['GET', 'POST'])
def multiplayer_phase1_use_kolega():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('1_kolega')
    if phase_check:
        return phase_check

    if request.method == 'POST' or not multiplayer_games[session['game_uuid']].can_use_card("Kolega w Komitecie"):
        multiplayer_games[session['game_uuid']].move_to_next_player()
        multiplayer_games[session['game_uuid']].current_phase = '1'
        return redirect('/multiplayer/phase1', code=302)
    else:
        multiplayer_games[session['game_uuid']].players[
            multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
            "Kolega w Komitecie")

    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        return render_template('local/phase1_use_kolega.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   multiplayer_games[session['game_uuid']].current_player_index],
                               picked_card="Kolega w Komitecie")


@app.route('/multiplayer/phase1_use_zwiekszona', methods=['GET', 'POST'])
def multiplayer_phase1_use_zwiekszona():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Zwiększona dostawa"):
        return redirect('/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].use_zwiekszona(request.form['shop_name'])
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Zwiększona dostawa")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/multiplayer/phase1', code=302)

    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        return render_template('local/phase1_use_zwiekszona.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   multiplayer_games[session['game_uuid']].current_player_index],
                               picked_card="Zwiększona dostawa")


@app.route('/multiplayer/phase1_use_pomylka', methods=['GET', 'POST'])
def multiplayer_phase1_use_pomylka():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Pomyłka w dostawie"):
        return redirect('/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/multiplayer/phase1', code=302)
        else:
            split_values = request.form['good_id'].split('#', 1)
            multiplayer_games[session['game_uuid']].use_pomylka(split_values[0], split_values[1],
                                                                request.form[
                                                                    'go_to_shop'])  # good_name, start_shop, go_to_shop
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Pomyłka w dostawie")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/multiplayer/phase1', code=302)
    if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[session['player_id']])
    else:
        return render_template('local/phase1_use_pomylka.htm', game=multiplayer_games[session['game_uuid']],
                               player=multiplayer_games[session['game_uuid']].players[
                                   multiplayer_games[session['game_uuid']].current_player_index],
                               picked_card="Pomyłka w dostawie")


# Gracze i spekulanci zbierają przedmioty
@app.route('/multiplayer/phase2', methods=['GET', 'POST'])
def multiplayer_phase2():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('2')
    if phase_check:
        return phase_check

    if request.method == 'POST':
        if multiplayer_games[session['game_uuid']].board.shops.get(request.form['shop_name']).available_goods and \
                multiplayer_games[
                    session['game_uuid']].board.shops.get(request.form['shop_name']).queue:
            multiplayer_games[session['game_uuid']].take_good_player(
                multiplayer_games[session['game_uuid']].get_first_pawn(request.form['shop_name']),
                request.form['shop_name'], request.form['good_name'],
                multiplayer_games[session['game_uuid']].players[
                    multiplayer_games[session['game_uuid']].get_pawn_owner_index(
                        multiplayer_games[session['game_uuid']].get_first_pawn(
                            request.form['shop_name']))])

    for shop in multiplayer_games[session['game_uuid']].board.shops.values():
        for _ in shop.queue:
            if shop.is_open and shop.available_goods:
                if shop.queue[0].color not in ['Kiosk', 'Meblowy', 'Spożywczy', 'Odzież', 'RTV-AGD']:

                    if not multiplayer_games[session['game_uuid']].get_pawn_owner_index(shop.queue[0]) == session[
                        'player_id']:
                        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                                               player=multiplayer_games[session['game_uuid']].players[
                                                   session['player_id']])
                    else:
                        return render_template('local/phase2.htm', game=multiplayer_games[session['game_uuid']],
                                               player=multiplayer_games[session['game_uuid']].players[
                                                   multiplayer_games[session['game_uuid']].get_pawn_owner_index(
                                                       shop.queue[0])],
                                               shop=shop, owner='player')
                else:
                    if not shop.did_speculant_take_good:  # Check if speculant took a good in this round, this variable determines if speculant took a good in this shop and round already.
                        multiplayer_games[session['game_uuid']].take_good_speculant(
                            multiplayer_games[session['game_uuid']].get_first_pawn(shop.name),
                            shop.name)
                        shop.did_speculant_take_good = True  # Speculant takes good, so make this True

    multiplayer_games[session['game_uuid']].board.reset_speculant_good_status()
    multiplayer_games[session['game_uuid']].current_phase = '3'
    return redirect('/multiplayer/phase3', code=302)


# Bazaar trades
@app.route('/multiplayer/phase3', methods=['GET', 'POST'])
def multiplayer_phase3():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('3')
    if phase_check:
        return phase_check

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/multiplayer/phase3', code=302)

        if 'cancel' in request.form and request.form['cancel'] == 'yes':
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].get_pawn_owner_index(
                    multiplayer_games[session['game_uuid']].board.bazaar.queue[0])].pawns.append(
                multiplayer_games[session['game_uuid']].board.bazaar.queue.pop(0))

        if 'stage' in request.form:
            if request.form[
                'stage'] == "1":  # Make decision depending on stage variable sent via form input of type hidden
                if request.form['shop_name'] == multiplayer_games[session['game_uuid']].board.bazaar.sale_category:
                    if not multiplayer_games[session['game_uuid']].get_pawn_owner_index(
                            multiplayer_games[session['game_uuid']].board.bazaar.queue[0]) == session[
                               'player_id']:
                        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                                               player=multiplayer_games[session['game_uuid']].players[
                                                   session['player_id']])
                    else:
                        # Stage 2a - IF item is in sale category, select ONE item from your inventory you want to trade - radio button
                        return render_template('local/phase3.htm', game=multiplayer_games[session['game_uuid']],
                                               player=multiplayer_games[session['game_uuid']].players[
                                                   multiplayer_games[session['game_uuid']].get_pawn_owner_index(
                                                       multiplayer_games[session['game_uuid']].board.bazaar.queue[0])],
                                               stage='2a', category=request.form['shop_name'])
                else:
                    if not multiplayer_games[session['game_uuid']].get_pawn_owner_index(
                            multiplayer_games[session['game_uuid']].board.bazaar.queue[0]) == session[
                               'player_id']:
                        return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                                               player=multiplayer_games[session['game_uuid']].players[
                                                   session['player_id']])
                    else:
                        # Stage 2b - if item is not in the sale category, select TWO items from your inventory you want to trade - checkbox with limit signaled by an alert
                        return render_template('local/phase3.htm', game=multiplayer_games[session['game_uuid']],
                                               player=multiplayer_games[session['game_uuid']].players[
                                                   multiplayer_games[session['game_uuid']].get_pawn_owner_index(
                                                       multiplayer_games[session['game_uuid']].board.bazaar.queue[0])],
                                               stage='2b', category=request.form['shop_name'])

            elif request.form['stage'] == "2a" and 'item_name' in request.form:  # one to one
                item = request.form['item_name']
                category = request.form['category']

                multiplayer_games[session['game_uuid']].move_player_item_to_bazaar(item)

                # Add item of selected category to player's eq & pop the pawn back to player hand
                multiplayer_games[session['game_uuid']].give_player_bazaar_item_and_pop_queue_first_pawn(category)

            elif request.form['stage'] == "2b" and 'item_name' in request.form:  # two to one
                items = request.form.getlist('item_name')
                category = request.form['category']

                for item in items:
                    multiplayer_games[session['game_uuid']].move_player_item_to_bazaar(item)

                # Add item of selected category to player's eq & pop the pawn back to player hand
                multiplayer_games[session['game_uuid']].give_player_bazaar_item_and_pop_queue_first_pawn(category)

    if multiplayer_games[session['game_uuid']].board.bazaar.queue:
        if not multiplayer_games[session['game_uuid']].get_pawn_owner_index(
                multiplayer_games[session['game_uuid']].board.bazaar.queue[0]) == session[
                   'player_id']:
            return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                                   player=multiplayer_games[session['game_uuid']].players[
                                       session['player_id']])
        else:
            # Stage 1 - choose the category from which you want to receive an item or go back and take your pawn with you
            return render_template('local/phase3.htm', game=multiplayer_games[session['game_uuid']],
                                   player=multiplayer_games[session['game_uuid']].players[
                                       multiplayer_games[session['game_uuid']].get_pawn_owner_index(
                                           multiplayer_games[session['game_uuid']].board.bazaar.queue[0])], stage='1')
    else:
        multiplayer_games[session['game_uuid']].current_phase = 'tpz'
        return redirect('/multiplayer/phase_tpz', code=302)


@app.route('/multiplayer/phase_tpz', methods=['GET', 'POST'])
def multiplayer_phase_tpz():
    if not multiplayer_check_simple():
        return redirect('/', code=302)


    phase_check = check_multiplayer_phase('tpz')
    if phase_check:
        return phase_check

    if multiplayer_games[session['game_uuid']].check_if_any_player_won():
        multiplayer_games[session['game_uuid']].current_phase = 'win'
        return redirect('/multiplayer/win', code=302)

    # Remove used supply cards
    multiplayer_games[session['game_uuid']].board.todays_supply_cards.clear()

    # Stop 'remanent' cards
    multiplayer_games[session['game_uuid']].board.reset_remanents()

    # Reset player pass status
    multiplayer_games[session['game_uuid']].reset_players_pass_status()

    if multiplayer_games[session['game_uuid']].board.current_day == "Piątek":
        multiplayer_games[session['game_uuid']].board.reset_supply_deck()
        multiplayer_games[session['game_uuid']].reshuffle_jostling_deck_at_end_of_week()

    # Draw jostling cards so every player has 3 of them in hand (unless the player ran out of cards)
    multiplayer_games[session['game_uuid']].jostling_draw()

    # Set next day of a week
    # Move to next sale_category on bazaar
    multiplayer_games[session['game_uuid']].go_to_next_day()

    multiplayer_games[session['game_uuid']].current_phase = 'withdraw'
    return redirect('/multiplayer/phase_withdraw', code=302)

@app.route('/multiplayer/win', methods=['GET', 'POST'])
def multiplayer_win():
    if not multiplayer_check_simple():
        return redirect('/', code=302)

    phase_check = check_multiplayer_phase('win')
    if phase_check:
        return phase_check

    winners = multiplayer_games[session['game_uuid']].check_if_any_player_won()
    return render_template('local/win.htm', game=multiplayer_games[session['game_uuid']], winners=winners)



###############################

if __name__ == '__main__':
    app.run(host="wierzba.wzks.uj.edu.pl", port=5114, debug=True)
