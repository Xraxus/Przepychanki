import uuid
from datetime import datetime

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask_mysqldb import MySQL
from text_unidecode import unidecode

from db_config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

# from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__, static_url_path='/static')
app.secret_key = '40a1f8b6143c4436905d49a2aff4bf81'
# app.debug = True
#
# toolbar = DebugToolbarExtension(app)

# MYSQL connection
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB
mysql = MySQL(app)

games = {}  # dictionary to store single player game instances
multiplayer_games = {}  # dictionary to store multiplayer game instances

from inc.game import Game  # import Game class from inc/game.py


@app.template_filter('remove_pl_char')
def remove_polish_characters(string):
    return unidecode(string)


@app.route('/')
def home():
    if 'key' not in session:  # generate a unique key for each user and store it in session
        session['key'] = uuid.uuid4()

    # Create game history table if it doesnt exist
    cur = mysql.connection.cursor()
    cur.execute('''create table if not exists przepychanki_historia
    (
        ID_rozgrywki   int auto_increment
            primary key
            unique,
        lista_graczy   text                         not null,
        zwyciezca      text                         not null,
        tryb           enum ('Lokalny', 'Sieciowy') not null,
        nazwa_pokoju   text                         null,
        data_rozgrywki datetime                     not null
    )
        comment 'historia rozegranych gier';''')
    mysql.connection.commit()
    cur.close()

    return render_template('home.htm')  # render home.htm template


def check_simple():
    if session.get(
            'key') and 'games' in globals():  # check if session key exists and if games dictionary is defined in the global namespace
        return True
    return False


def check():
    if session.get('key') and 'games' in globals() and session.get(
            'key') in games:  # check if session key exists, if games dictionary is defined in the global namespace, and if the session key exists as a key in the games dictionary
        return True
    return False


def check_local_phase(phase_index):
    if games[session[
        'key']].current_phase != phase_index:  # check if the current phase of the game is not equal to the given phase index
        if games[session[
            'key']].current_phase == '0':  # redirect to the corresponding phase based on the current phase of the game
            return redirect('/20_kobylarz/przepychanki/local/phase0', code=302)
        elif games[session['key']].current_phase == '1':
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
        elif games[session['key']].current_phase == '1_kolega':
            return redirect('/20_kobylarz/przepychanki/local/phase1_use_kolega', code=302)
        elif games[session['key']].current_phase == '2':
            return redirect('/20_kobylarz/przepychanki/local/phase2', code=302)
        elif games[session['key']].current_phase == '3':
            return redirect('/20_kobylarz/przepychanki/local/phase3', code=302)
        elif games[session['key']].current_phase == 'tpz':
            return redirect('/20_kobylarz/przepychanki/local/phase_tpz', code=302)
        elif games[session['key']].current_phase == 'win':
            return redirect('/20_kobylarz/przepychanki/local/win', code=302)
        elif games[session['key']].current_phase == 'withdraw':
            return redirect('/20_kobylarz/przepychanki/local/phase_withdraw', code=302)
        else:
            return redirect('/20_kobylarz/przepychanki/local/form', code=302)
    else:
        return False


def multiplayer_check_simple():
    # check if game_uuid is in session and multiplayer_games exists
    if session.get('game_uuid') and 'multiplayer_games' in globals():
        return True  # return True if both conditions are met
    return False  # return False otherwise


def multiplayer_check():
    # check if game_uuid is in session, multiplayer_games exists, and game_uuid is in multiplayer_games
    if session.get('game_uuid') and 'multiplayer_games' in globals() and session.get('game_uuid') in multiplayer_games:
        return True  # return True if all conditions are met
    return False  # return False otherwise


def check_multiplayer_phase(phase_index):
    # check if the current phase of the game in multiplayer_games matches phase_index
    if multiplayer_games[session['game_uuid']].current_phase != phase_index:
        # redirect to the appropriate phase page based on the current phase of the game in multiplayer_games
        if multiplayer_games[session['game_uuid']].current_phase == '0':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase0', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == '1':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == '1_kolega':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase1_use_kolega', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == '2':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase2', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == '3':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase3', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == 'tpz':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase_tpz', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == 'win':
            return redirect('/20_kobylarz/przepychanki/multiplayer/win', code=302)
        elif multiplayer_games[session['game_uuid']].current_phase == 'withdraw':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase_withdraw', code=302)
        else:
            return redirect('/20_kobylarz/przepychanki/',
                            code=302)  # redirect to the home page if the current phase is not recognized
    else:
        return False  # return False if the current phase matches phase_index


@app.route('/info', methods=['GET'])
def info():
    return render_template('info.htm')


@app.route('/historia', methods=['GET'])
def historia():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM przepychanki_historia")
    rows = cur.fetchall()
    cur.close()
    return render_template('historia.htm', rows=rows)


@app.route('/zasady', methods=['GET'])
def zasady():
    return render_template('zasady.htm')


############################### LOCAL(HOTSEAT) ###############################

@app.route('/local', methods=['GET', 'POST'])
def local():
    # redirect to the form page for creating a new local game
    return redirect('/20_kobylarz/przepychanki/local/form', code=302)


@app.route('/local/form', methods=['GET', 'POST'])
def local_form():
    # check if session key exists and if the games dictionary is defined in the global namespace
    if not check_simple():
        # redirect to the homepage if the check fails
        return redirect('/20_kobylarz/przepychanki/', code=302)

    if request.method == 'POST':
        # get a list of player names submitted through the form
        players = [x for x in request.form.getlist('names') if x]
        # check if the number of players is valid (between 2 and 5, inclusive)
        if 2 <= len(players) <= 5:
            # create a new local game with the given player names
            return new_local_game(players)

    # render the form template if the request method is GET or the form data is invalid
    return render_template('local/form.htm')


def new_local_game(names):
    # check if session key exists and if the games dictionary is defined in the global namespace
    if not check_simple():
        # redirect to the homepage if the check fails
        return redirect('/20_kobylarz/przepychanki/', code=302)

    # create a new local game object and add it to the games dictionary with the session key as the key
    games[session['key']] = Game(names, 'local')

    # redirect to the first phase of the newly created game
    return redirect('/20_kobylarz/przepychanki/local/phase0', code=302)


# This route handles the phase of the game before the pawn placement phase in each round
# During this phase, players can withdraw their pawns to set them up in the next phase (phase 0)
@app.route('/local/phase_withdraw', methods=['GET', 'POST'])
def local_withdraw():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    if request.method == 'POST':
        if 'do_pass' in request.form and request.form['do_pass'] == 'yes':
            # If a player chooses to pass, call the do_pass() function and check if all players have passed
            games[session['key']].players[games[session['key']].current_player_index].do_pass()
            if not games[session['key']].did_all_players_pass():
                games[session['key']].move_to_next_player()
        else:
            # If a player chooses to withdraw a pawn, remove it from the queue and add it to their pawns list
            if games[session['key']].get_pawn_in_queue(request.form['pawn_id'], request.form['shop_name']) is not None:
                games[session['key']].players[games[session['key']].current_player_index].pawns.append(
                    games[session['key']].board.shops.get(request.form['shop_name']).queue.pop(
                        games[session['key']].board.shops.get(request.form['shop_name']).queue.index(
                            games[session['key']].get_pawn_in_queue(request.form['pawn_id'],
                                                                    request.form['shop_name']))))
                if not games[session['key']].did_all_players_pass():
                    games[session['key']].move_to_next_player()

    # Check if all players have passed or if no player has any pawns on the board
    # If so, move on to phase 0
    if games[session['key']].did_all_players_pass() or not games[session['key']].does_any_player_have_pawns_on_board():
        games[session['key']].current_player_index = 0
        games[session['key']].reset_players_pass_status()

        games[session['key']].current_phase = '0'
        return redirect('/20_kobylarz/przepychanki/local/phase0', code=302)

    # Render the withdraw phase template
    return render_template('local/phase_withdraw.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index])


# Phase 0 - placement of pawns + delivery of goods at the end of placement
@app.route('/local/phase0', methods=['GET', 'POST'])
def local_phase0():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    # Check if the current phase is phase 0
    phase_check = check_local_phase('0')
    if phase_check:
        return phase_check

    if request.method == 'POST':
        # Place a pawn and move to the next player that has a pawn
        games[session['key']].place_pawn(request.form['shop_name'])

        if not games[session['key']].does_any_player_have_pawns():
            if games[session['key']].day_count == 1:
                games[session['key']].place_all_speculants()
            games[session['key']].current_player_index = 0
            games[session['key']].board.draw_restock()

            # Move to phase 1
            games[session['key']].current_phase = '1'
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
        else:
            return render_template('local/phase0.htm', game=games[session['key']],
                                   player=games[session['key']].players[games[session['key']].current_player_index])
    else:
        games[session['key']].current_player_index = 0
        if not games[session['key']].does_any_player_have_pawns():
            if games[session['key']].day_count == 1:
                games[session['key']].place_all_speculants()
            games[session['key']].board.draw_restock()

            # Move to phase 1
            games[session['key']].current_phase = '1'
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
        else:
            if not games[session['key']].players[games[session['key']].current_player_index].pawns:
                games[session['key']].move_to_next_player_with_pawns()

            return render_template('local/phase0.htm', game=games[session['key']],
                                   player=games[session['key']].players[games[session['key']].current_player_index],
                                   pawns=games[session['key']].players[
                                       games[session['key']].current_player_index].pawns)


# Phase 1 - use queue-pushing cards to get the best position
@app.route('/local/phase1', methods=['GET', 'POST'])
def local_phase1():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    # check if it's the correct phase
    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    # if user chose a card
    if request.method == 'POST':
        # get the chosen card
        picked_card = request.form['card']

        # redirect to the appropriate function depending on the card chosen
        if picked_card == "Pan tu nie stał":
            return redirect('/20_kobylarz/przepychanki/local/phase1_use_pan')
        elif picked_card == "Matka z dzieckiem":
            return redirect('/20_kobylarz/przepychanki/local/phase1_use_matka')
        elif picked_card == "Krytyka władzy":
            return redirect('/20_kobylarz/przepychanki/local/phase1_use_krytyka')
        elif picked_card == "Lista społeczna":
            return redirect('/20_kobylarz/przepychanki/local/phase1_use_lista')
        elif picked_card == "Szczęśliwy traf":
            return redirect('/20_kobylarz/przepychanki/local/phase1_use_szczesliwy')
        elif picked_card == "Remanent":
            return redirect('/20_kobylarz/przepychanki/local/phase1_use_remanent')
        elif picked_card == "Towar spod lady":
            return redirect('/20_kobylarz/przepychanki/local/phase1_use_towar')
        elif picked_card == "Kolega w Komitecie":
            games[session['key']].current_phase = '1_kolega'
            return redirect('/20_kobylarz/przepychanki/local/phase1_use_kolega')
        elif picked_card == "Zwiększona dostawa":
            return redirect('/20_kobylarz/przepychanki/local/phase1_use_zwiekszona')
        elif picked_card == "Pomyłka w dostawie":
            return redirect('/20_kobylarz/przepychanki/local/phase1_use_pomylka')
        elif picked_card == "Spasuj":
            # player passes and checks if all other players also passed
            games[session['key']].players[games[session['key']].current_player_index].do_pass()
            if not games[session['key']].does_any_player_have_cards_and_didnt_pass():
                # if all players passed, move to phase 2
                games[session['key']].current_phase = '2'
                return redirect('/20_kobylarz/przepychanki/local/phase2', code=302)
            else:
                # if not all players passed, move to the next player
                games[session['key']].move_to_next_player()
                return render_template('local/phase1.htm', game=games[session['key']],
                                       player=games[session['key']].players[games[session['key']].current_player_index])

    else:
        if not games[session['key']].does_any_player_have_cards_and_didnt_pass():
            # if all players passed, move to phase 2
            games[session['key']].current_phase = '2'
            return redirect('/20_kobylarz/przepychanki/local/phase2', code=302)
        else:
            # if not all players passed, render the template with the current player
            return render_template('local/phase1.htm', game=games[session['key']],
                                   player=games[session['key']].players[games[session['key']].current_player_index])


@app.route('/local/phase1_use_pan', methods=['GET', 'POST'])
def local_phase1_use_pan():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Pan tu nie stał"):
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
        else:
            games[session['key']].use_pan(request.form['pawn_id'], request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Pan tu nie stał")
            games[session['key']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
    return render_template('local/phase1_use_pan.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Pan tu nie stał")


@app.route('/local/phase1_use_matka', methods=['GET', 'POST'])
def local_phase1_use_matka():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Matka z dzieckiem"):
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
        else:
            games[session['key']].use_matka(request.form['pawn_id'], request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Matka z dzieckiem")
            games[session['key']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
    return render_template('local/phase1_use_matka.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Matka z dzieckiem")


@app.route('/local/phase1_use_krytyka', methods=['GET', 'POST'])
def local_phase1_use_krytyka():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Krytyka władzy"):
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
        else:
            games[session['key']].use_krytyka(request.form['pawn_id'], request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Krytyka władzy")
            games[session['key']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
    return render_template('local/phase1_use_krytyka.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Krytyka władzy")


@app.route('/local/phase1_use_lista', methods=['GET', 'POST'])
def local_phase1_use_lista():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Lista społeczna"):
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
        else:
            games[session['key']].get_shop_queue(request.form['shop_name']).reverse()
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Lista społeczna")
            games[session['key']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
    return render_template('local/phase1_use_lista.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Lista społeczna")


@app.route('/local/phase1_use_szczesliwy', methods=['GET', 'POST'])
def local_phase1_use_szczesliwy():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Szczęśliwy traf"):
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
        else:
            split_values = request.form['pawn_id'].split('#', 1)
            games[session['key']].use_szczesliwy(split_values[0], split_values[1],
                                                 request.form['go_to_shop'])  # pawn_id, start_shop, go_to_shop
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Szczęśliwy traf")
            games[session['key']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
    return render_template('local/phase1_use_szczesliwy.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Szczęśliwy traf")


@app.route('/local/phase1_use_remanent', methods=['GET', 'POST'])
def local_phase1_use_remanent():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Remanent"):
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
        else:
            games[session['key']].use_remanent(request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card("Remanent")
            games[session['key']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
    return render_template('local/phase1_use_remanent.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Remanent")


@app.route('/local/phase1_use_towar', methods=['GET', 'POST'])
def local_phase1_use_towar():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Towar spod lady"):
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
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
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
    return render_template('local/phase1_use_towar.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Towar spod lady")


@app.route('/local/phase1_use_kolega', methods=['GET', 'POST'])
def local_phase1_use_kolega():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('1_kolega')
    if phase_check:
        return phase_check

    if request.method == 'POST' or not games[session['key']].can_use_card("Kolega w Komitecie"):
        games[session['key']].move_to_next_player()
        games[session['key']].current_phase = '1'
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
    else:
        games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
            "Kolega w Komitecie")

    return render_template('local/phase1_use_kolega.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Kolega w Komitecie")


@app.route('/local/phase1_use_zwiekszona', methods=['GET', 'POST'])
def local_phase1_use_zwiekszona():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Zwiększona dostawa"):
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
        else:
            games[session['key']].use_zwiekszona(request.form['shop_name'])
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Zwiększona dostawa")
            games[session['key']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
    return render_template('local/phase1_use_zwiekszona.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Zwiększona dostawa")


@app.route('/local/phase1_use_pomylka', methods=['GET', 'POST'])
def local_phase1_use_pomylka():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('1')
    if phase_check:
        return phase_check

    if not games[session['key']].can_use_card("Pomyłka w dostawie"):
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
        else:
            split_values = request.form['good_id'].split('#', 1)
            games[session['key']].use_pomylka(split_values[0], split_values[1],
                                              request.form['go_to_shop'])  # good_name, start_shop, go_to_shop
            games[session['key']].players[games[session['key']].current_player_index].remove_jostling_card(
                "Pomyłka w dostawie")
            games[session['key']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/local/phase1', code=302)
    return render_template('local/phase1_use_pomylka.htm', game=games[session['key']],
                           player=games[session['key']].players[games[session['key']].current_player_index],
                           picked_card="Pomyłka w dostawie")


# Players and speculators collect items
@app.route('/local/phase2', methods=['GET', 'POST'])
def local_phase2():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('2')
    if phase_check:
        return phase_check

    # Take a good from a shop
    if request.method == 'POST':
        if games[session['key']].board.shops.get(request.form['shop_name']).available_goods and games[
            session['key']].board.shops.get(request.form['shop_name']).queue:
            games[session['key']].take_good_player(
                games[session['key']].get_first_pawn(request.form['shop_name']),
                request.form['shop_name'], request.form['good_name'],
                games[session['key']].players[games[session['key']].get_pawn_owner_index(
                    games[session['key']].get_first_pawn(request.form['shop_name']))])

    # Loop over all shops
    for shop in games[session['key']].board.shops.values():
        for _ in shop.queue:
            # Check if shop is open and has available goods
            if shop.is_open and shop.available_goods:
                # Check if the pawn is not a speculant
                if shop.queue[0].color not in ['Kiosk', 'Meblowy', 'Spożywczy', 'Odzież', 'RTV-AGD']:
                    return render_template('local/phase2.htm', game=games[session['key']],
                                           player=games[session['key']].players[
                                               games[session['key']].get_pawn_owner_index(shop.queue[0])],
                                           shop=shop, owner='player')
                else:
                    # Check if speculant has already taken a good in this round
                    if not shop.did_speculant_take_good:
                        games[session['key']].take_good_speculant(games[session['key']].get_first_pawn(shop.name),
                                                                  shop.name)
                        shop.did_speculant_take_good = True

    # Reset the status of the speculant's goods for all shops
    games[session['key']].board.reset_speculant_good_status()
    # Move to the next phase
    games[session['key']].current_phase = '3'
    return redirect('/20_kobylarz/przepychanki/local/phase3', code=302)


# Bazaar trades
@app.route('/local/phase3', methods=['GET', 'POST'])
def local_phase3():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_local_phase('3')
    if phase_check:
        return phase_check

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/local/phase3', code=302)

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
        return redirect('/20_kobylarz/przepychanki/local/phase_tpz', code=302)


# Route for the TPZ phase
@app.route('/local/phase_tpz', methods=['GET', 'POST'])
def phase_tpz():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    # Check if it's the correct phase
    phase_check = check_local_phase('tpz')
    if phase_check:
        return phase_check

    # Check if any player has won the game
    if games[session['key']].check_if_any_player_won():
        games[session['key']].current_phase = 'win'
        return redirect('/20_kobylarz/przepychanki/local/win', code=302)

    # Remove used supply cards
    games[session['key']].board.todays_supply_cards.clear()

    # Stop 'remanent' cards
    games[session['key']].board.reset_remanents()

    # Reset player pass status
    games[session['key']].reset_players_pass_status()

    # If it's Friday, reset the supply deck and reshuffle the jostling deck
    if games[session['key']].board.current_day == "Piątek":
        games[session['key']].board.reset_supply_deck()
        games[session['key']].reshuffle_jostling_deck_at_end_of_week()

    # Draw jostling cards so every player has 3 of them in hand (unless the player ran out of cards)
    games[session['key']].jostling_draw()

    # Set next day of a week
    # Move to next sale_category on bazaar
    games[session['key']].go_to_next_day()

    # Move to the withdraw phase
    games[session['key']].current_phase = 'withdraw'
    return redirect('/20_kobylarz/przepychanki/local/phase_withdraw', code=302)


# This route is for displaying the win screen when a player wins the game
@app.route('/local/win', methods=['GET', 'POST'])
def local_win():
    if not check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    # Check the current game phase, if it's not the win phase, return to the previous phase
    phase_check = check_local_phase('win')
    if phase_check:
        return phase_check

    # get winners to variable
    winners = games[session['key']].check_if_any_player_won()

    # convert list to strings with only player.name's
    players_str = ", ".join([player.name for player in games[session['key']].players])
    winners_str = ", ".join([player.name for player in winners])

    # add record to table
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO przepychanki_historia (lista_graczy, zwyciezca, tryb, nazwa_pokoju, data_rozgrywki) VALUES (%s, %s, %s, %s, %s)",
        (players_str,  # lista_graczy
         winners_str,  # zwyciezca
         'Lokalny',  # tryb
         None,  # nazwa_pokoju
         datetime.now()))  # data_rozgrywki
    mysql.connection.commit()
    cur.close()

    # Render the win screen with the game object and winner(s) information
    return render_template('local/win.htm', game=games[session['key']], winners=winners)


############################### MULTIPLAYER ###############################

@app.route('/multiplayer/rooms')
def rooms():
    return render_template('multiplayer/rooms.htm', multiplayer_games=multiplayer_games)


@app.route('/multiplayer/form', methods=['GET', 'POST'])
def multiplayer_form():
    if request.method == 'POST':
        players = [x for x in request.form.getlist('names') if x]
        room_name = request.form['room_name']

        return new_multiplayer_game(players, room_name)

    return render_template('multiplayer/form.htm')


def new_multiplayer_game(name, room_name):
    session['game_uuid'] = str(uuid.uuid4())
    session['player_id'] = 0
    multiplayer_games[session['game_uuid']] = Game(name, 'multiplayer', room_name)
    return redirect('/20_kobylarz/przepychanki/multiplayer/wait', code=302)


@app.route('/multiplayer/form_join/<room>', methods=['GET', 'POST'])
def form_join(room):
    if request.method == 'POST':
        players = [x for x in request.form.getlist('names') if x]
        game_uuid = request.form.getlist('room')[0]
        session['player_id'] = multiplayer_games[game_uuid].add_player(players[0])
        session['game_uuid'] = game_uuid
        return redirect('/20_kobylarz/przepychanki/multiplayer/join', code=302)

    return render_template('multiplayer/form_join.htm', room=room)


@app.route('/multiplayer/wait')
def wait():
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    return render_template('multiplayer/wait.htm', game=multiplayer_games[session['game_uuid']])


@app.route('/multiplayer/join')
def join():
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    if multiplayer_games[session['game_uuid']].start:
        multiplayer_games[session['game_uuid']].current_player_index = 0
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase0', code=302)

    return render_template('multiplayer/join.htm')


@app.route('/multiplayer/start_game')
def start_game():
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    if not multiplayer_games[session['game_uuid']].start:
        multiplayer_games[session['game_uuid']].start_game()
        multiplayer_games[session['game_uuid']].current_player_index = 0
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase0', code=302)

    multiplayer_games[session['game_uuid']].current_player_index = 0
    return redirect('/20_kobylarz/przepychanki/multiplayer/phase0', code=302)


# @app.route('/multiplayer/board')
# def board():
#     return render_template('multiplayer/test.htm', game=multiplayer_games[session['game_uuid']],
#                            id_gracza=session['player_id'])


@app.route('/multiplayer/phase_withdraw', methods=['GET', 'POST'])
def multiplayer_withdraw():
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

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
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase0', code=302)

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
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

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
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
            else:
                if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
                    return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                                           player=multiplayer_games[session['game_uuid']].players[session['player_id']])
                else:
                    return render_template('local/phase0.htm', game=multiplayer_games[session['game_uuid']],
                                           player=multiplayer_games[session['game_uuid']].players[
                                               multiplayer_games[session['game_uuid']].current_player_index])
        else:
            if not multiplayer_games[session['game_uuid']].does_any_player_have_pawns():
                if multiplayer_games[session['game_uuid']].day_count == 1:
                    multiplayer_games[session['game_uuid']].place_all_speculants()
                multiplayer_games[session['game_uuid']].board.draw_restock()

                multiplayer_games[session['game_uuid']].current_phase = '1'
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
            else:
                if not multiplayer_games[session['game_uuid']].players[
                    multiplayer_games[session['game_uuid']].current_player_index].pawns:
                    multiplayer_games[session['game_uuid']].move_to_next_player_with_pawns()
                if not multiplayer_games[session['game_uuid']].current_player_index == session['player_id']:
                    return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                                           player=multiplayer_games[session['game_uuid']].players[session['player_id']])
                else:
                    return render_template('local/phase0.htm', game=multiplayer_games[session['game_uuid']],
                                           player=multiplayer_games[session['game_uuid']].players[
                                               multiplayer_games[session['game_uuid']].current_player_index])


# Faza 1 - użyj kart przepychanek kolejkowych, by zapewnić sobie najlepszą pozycje
@app.route('/multiplayer/phase1', methods=['GET', 'POST'])
def multiplayer_phase1():
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

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
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1_use_pan')
            elif picked_card == "Matka z dzieckiem":
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1_use_matka')
            elif picked_card == "Krytyka władzy":
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1_use_krytyka')
            elif picked_card == "Lista społeczna":
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1_use_lista')
            elif picked_card == "Szczęśliwy traf":
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1_use_szczesliwy')
            elif picked_card == "Remanent":
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1_use_remanent')
            elif picked_card == "Towar spod lady":
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1_use_towar')
            elif picked_card == "Kolega w Komitecie":
                multiplayer_games[session['game_uuid']].current_phase = '1_kolega'
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1_use_kolega')
            elif picked_card == "Zwiększona dostawa":
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1_use_zwiekszona')
            elif picked_card == "Pomyłka w dostawie":
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase1_use_pomylka')
            elif picked_card == "Spasuj":
                multiplayer_games[session['game_uuid']].players[
                    multiplayer_games[session['game_uuid']].current_player_index].do_pass()
                if not multiplayer_games[session['game_uuid']].does_any_player_have_cards_and_didnt_pass():

                    multiplayer_games[session['game_uuid']].current_phase = '2'
                    return redirect('/20_kobylarz/przepychanki/multiplayer/phase2', code=302)
                else:
                    multiplayer_games[session['game_uuid']].move_to_next_player()
                    return render_template('multiplayer/board.htm', game=multiplayer_games[session['game_uuid']],
                                           player=multiplayer_games[session['game_uuid']].players[session['player_id']])
        else:
            if not multiplayer_games[session['game_uuid']].does_any_player_have_cards_and_didnt_pass():
                multiplayer_games[session['game_uuid']].current_phase = '2'
                return redirect('/20_kobylarz/przepychanki/multiplayer/phase2', code=302)
            return render_template('local/phase1.htm', game=multiplayer_games[session['game_uuid']],
                                   player=multiplayer_games[session['game_uuid']].players[
                                       multiplayer_games[session['game_uuid']].current_player_index])


@app.route('/multiplayer/phase1_use_pan', methods=['GET', 'POST'])
def multiplayer_phase1_use_pan():
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Pan tu nie stał"):
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].use_pan(request.form['pawn_id'], request.form['shop_name'])
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Pan tu nie stał")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
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
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Matka z dzieckiem"):
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].use_matka(request.form['pawn_id'], request.form['shop_name'])
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Matka z dzieckiem")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
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
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Krytyka władzy"):
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].use_krytyka(request.form['pawn_id'], request.form['shop_name'])
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Krytyka władzy")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)

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
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Lista społeczna"):
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].get_shop_queue(request.form['shop_name']).reverse()
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Lista społeczna")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
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
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Szczęśliwy traf"):
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
        else:
            split_values = request.form['pawn_id'].split('#', 1)
            multiplayer_games[session['game_uuid']].use_szczesliwy(split_values[0], split_values[1],
                                                                   request.form[
                                                                       'go_to_shop'])  # pawn_id, start_shop, go_to_shop
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Szczęśliwy traf")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
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
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Remanent"):
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].use_remanent(request.form['shop_name'])
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card("Remanent")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
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
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Towar spod lady"):
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
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
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
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
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('1_kolega')
    if phase_check:
        return phase_check

    if request.method == 'POST' or not multiplayer_games[session['game_uuid']].can_use_card("Kolega w Komitecie"):
        multiplayer_games[session['game_uuid']].move_to_next_player()
        multiplayer_games[session['game_uuid']].current_phase = '1'
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
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
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Zwiększona dostawa"):
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
        else:
            multiplayer_games[session['game_uuid']].use_zwiekszona(request.form['shop_name'])
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Zwiększona dostawa")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)

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
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('1')
    if phase_check:
        return phase_check

    if not multiplayer_games[session['game_uuid']].can_use_card("Pomyłka w dostawie"):
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
        else:
            split_values = request.form['good_id'].split('#', 1)
            multiplayer_games[session['game_uuid']].use_pomylka(split_values[0], split_values[1],
                                                                request.form[
                                                                    'go_to_shop'])  # good_name, start_shop, go_to_shop
            multiplayer_games[session['game_uuid']].players[
                multiplayer_games[session['game_uuid']].current_player_index].remove_jostling_card(
                "Pomyłka w dostawie")
            multiplayer_games[session['game_uuid']].move_to_next_player()
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase1', code=302)
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
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

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
    return redirect('/20_kobylarz/przepychanki/multiplayer/phase3', code=302)


# Bazaar trades
@app.route('/multiplayer/phase3', methods=['GET', 'POST'])
def multiplayer_phase3():
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('3')
    if phase_check:
        return phase_check

    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/20_kobylarz/przepychanki/multiplayer/phase3', code=302)

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
        return redirect('/20_kobylarz/przepychanki/multiplayer/phase_tpz', code=302)


@app.route('/multiplayer/phase_tpz', methods=['GET', 'POST'])
def multiplayer_phase_tpz():
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('tpz')
    if phase_check:
        return phase_check

    if multiplayer_games[session['game_uuid']].check_if_any_player_won():
        multiplayer_games[session['game_uuid']].current_phase = 'win'
        return redirect('/20_kobylarz/przepychanki/multiplayer/win', code=302)

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
    return redirect('/20_kobylarz/przepychanki/multiplayer/phase_withdraw', code=302)


@app.route('/multiplayer/win', methods=['GET', 'POST'])
def multiplayer_win():
    if not multiplayer_check():
        return redirect('/20_kobylarz/przepychanki/', code=302)

    phase_check = check_multiplayer_phase('win')
    if phase_check:
        return phase_check

    # get winners to variable
    winners = multiplayer_games[session['game_uuid']].check_if_any_player_won()

    # convert list to strings with only player.name's
    players_str = ", ".join([player.name for player in multiplayer_games[session['game_uuid']].players])
    winners_str = ", ".join([player.name for player in winners])

    # check if game has already been recorded in database
    if not multiplayer_games[session['game_uuid']].recorded:
        # add record to table
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO przepychanki_historia (lista_graczy, zwyciezca, tryb, nazwa_pokoju, data_rozgrywki) VALUES (%s, %s, %s, %s, %s)",
            (players_str,  # lista_graczy
             winners_str,  # zwyciezca
             'Sieciowy',  # tryb
             multiplayer_games[session['game_uuid']].room_name,  # nazwa_pokoju
             datetime.now()))  # data_rozgrywki
        mysql.connection.commit()
        cur.close()
        # set recorded flag in  to True - prevents multiple records
        multiplayer_games[session['game_uuid']].recorded = True



    return render_template('local/win.htm', game=multiplayer_games[session['game_uuid']], winners=winners)


###############################
if __name__ == '__main__':
    app.run()
