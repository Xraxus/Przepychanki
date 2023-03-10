import uuid

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import session

app = Flask(__name__)
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




### LOCAL(HOTSEAT) ###

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


# Faza nast??puj??ca w kolejnych rundach, przed faza ustawiania pionk??w
# Gracze mog?? wycofa?? swoje pionki, ??eby ustawi?? je w kolejnej fazie (fazie 0)
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
                            games[session['key']].get_pawn_in_queue(request.form['pawn_id'], request.form['shop_name']))))
                if not games[session['key']].did_all_players_pass():
                    games[session['key']].move_to_next_player()

    if games[session['key']].did_all_players_pass() or not games[session['key']].does_any_player_have_pawns_on_board():
        games[session['key']].current_player_index = 0
        games[session['key']].reset_players_pass_status()

        games[session['key']].current_phase = '0'
        return redirect('/local/phase0', code=302)

    return render_template('local/phase_withdraw.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index])


# Faza 0 - ustawianie pionk??w + dostarczenie towar??w na koniec ustawiania
@app.route('/local/phase0', methods=['GET', 'POST'])
def local_phase0():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('0')
    if phase_check:
        return phase_check

    if request.method == 'POST':
        print("jest post")
        games[session['key']].place_pawn(
            request.form['shop_name'])  # places pawn and moves to the next player that has a pawn
        print(request.form['shop_name'])

        if not games[session['key']].does_any_player_have_pawns():
            if games[session['key']].day_count == 1:
                games[session['key']].place_all_speculants()
            games[session['key']].current_player_index = 0
            games[session['key']].board.draw_restock()

            games[session['key']].current_phase = '1'
            return redirect('/local/phase1', code=302)
        else:
            return render_template('local/phase0.htm', game=games[session['key']],
                                   player=games[session['key']].players[games[session['key']].current_player_index],
                                   pawns=games[session['key']].players[
                                       games[session['key']].current_player_index].pawns)
    else:
        print("nie ma posta")
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


# Faza 1 - u??yj kart przepychanek kolejkowych, by zapewni?? sobie najlepsz?? pozycje
@app.route('/local/phase1', methods=['GET', 'POST'])
def local_phase1():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if request.method == 'POST':
        picked_card = request.form['card']

        if picked_card == "Pan tu nie sta??":
            return redirect('/local/phase1_use_pan')
        elif picked_card == "Matka z dzieckiem":
            return redirect('/local/phase1_use_matka')
        elif picked_card == "Krytyka w??adzy":
            return redirect('/local/phase1_use_krytyka')
        elif picked_card == "Lista spo??eczna":
            return redirect('/local/phase1_use_lista')
        elif picked_card == "Szcz????liwy traf":
            return redirect('/local/phase1_use_szczesliwy')
        elif picked_card == "Remanent":
            return redirect('/local/phase1_use_remanent')
        elif picked_card == "Towar spod lady":
            return redirect('/local/phase1_use_towar')
        elif picked_card == "Kolega w Komitecie":
            games[session['key']].current_phase = '1_kolega'
            return redirect('/local/phase1_use_kolega')
        elif picked_card == "Zwi??kszona dostawa":
            return redirect('/local/phase1_use_zwiekszona')
        elif picked_card == "Pomy??ka w dostawie":
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

    if not games[session['key']].can_use_card("Pan tu nie sta??"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            games[session['key']].use_pan(request.form['pawn_id'], request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Pan tu nie sta??")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_pan.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Pan tu nie sta??")


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

    if not games[session['key']].can_use_card("Krytyka w??adzy"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            games[session['key']].use_krytyka(request.form['pawn_id'], request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Krytyka w??adzy")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_krytyka.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Krytyka w??adzy")


@app.route('/local/phase1_use_lista', methods=['GET', 'POST'])
def local_phase1_use_lista():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Lista spo??eczna"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            games[session['key']].get_shop_queue(request.form['shop_name']).reverse()
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Lista spo??eczna")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_lista.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Lista spo??eczna")


@app.route('/local/phase1_use_szczesliwy', methods=['GET', 'POST'])
def local_phase1_use_szczesliwy():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Szcz????liwy traf"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            split_values = request.form['pawn_id'].split('#', 1)
            games[session['key']].use_szczesliwy(split_values[0], split_values[1],
                                                 request.form['go_to_shop'])  # pawn_id, start_shop, go_to_shop
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Szcz????liwy traf")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_szczesliwy.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Szcz????liwy traf")


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
        games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card("Kolega w Komitecie")

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

    if not games[session['key']].can_use_card("Zwi??kszona dostawa"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            games[session['key']].use_zwiekszona(request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Zwi??kszona dostawa")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_zwiekszona.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Zwi??kszona dostawa")


@app.route('/local/phase1_use_pomylka', methods=['GET', 'POST'])
def local_phase1_use_pomylka():
    if not check():
        return redirect('/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Pomy??ka w dostawie"):
        return redirect('/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            split_values = request.form['good_id'].split('#', 1)
            games[session['key']].use_pomylka(split_values[0], split_values[1],
                                              request.form['go_to_shop'])  # good_name, start_shop, go_to_shop
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Pomy??ka w dostawie")
            games[session['key']].move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_pomylka.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Pomy??ka w dostawie")


# Gracze i spekulanci zbieraj?? przedmioty
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
                if shop.queue[0].color not in ['Kiosk', 'Meblowy', 'Spo??ywczy', 'Odzie??', 'RTV-AGD']:
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

    if games[session['key']].board.current_day == "Pi??tek":
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




if __name__ == '__main__':
    app.run(host="wierzba.wzks.uj.edu.pl", port=5114, debug=True)
