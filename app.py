from flask import Flask
from flask import redirect
from flask import render_template
from flask import request

app = Flask(__name__)

from inc.game import Game


@app.route('/')
def home():
    return render_template('home.htm')

@app.route('/local/form', methods=['GET','POST'])
def local_form():
    if request.method == 'POST':
        return init(request.form.get('name'))
    return render_template('local/form.htm')

def init(name):
    global game
    game = Game(name)

    return redirect('/local/phase0', code=302, )


#Faza 0 - ustawianie pionków + dostarczenie towarów na koniec ustawiania
@app.route('/local/phase0', methods=['GET','POST'])
def local_phase0():
    if request.method== 'POST':
        category = request.form['shop_name']
        result = game.place_pawn(category, game.players[game.current_player_index].color)

        if result == 'player has no pawns':
            game.place_all_speculants()
            game.board.draw_restock()
            return redirect('/local/phase1', code=302)
        else:
            return render_template('local/phase0.htm',game=game, message='Pawn placed', player=game.players[game.current_player_index],
                           categories=['Bazaar'] + [x.name for x in game.board.shops.values()],
                           pawns=game.players[game.current_player_index].pawns)
    else:
        return render_template('local/phase0.htm',game=game, player=game.players[game.current_player_index],
                       categories=['Bazaar'] + [x.name for x in game.board.shops.values()],
                       pawns=game.players[game.current_player_index].pawns)

#Faza 1 - użyj kart przepychanek kolejkowych, by zapewnić sobie najlepszą pozycje
@app.route('/local/phase1', methods=['GET','POST'])
def local_phase1():
    if request.method == 'POST':
        picked_card = request.form['card']
        if picked_card == "Pan tu nie stał":
            return redirect('/local/phase1_use_pan')
        elif picked_card=="Matka z dzieckiem":
            return redirect('/local/phase1_use_matka')
        elif picked_card=="Krytyka władzy":
            return redirect('/local/phase1_use_krytyka')
        elif picked_card=="Lista społeczna":
            return redirect('/local/phase1_use_lista')
        elif picked_card=="Szczęśliwy traf":
            return redirect('/local/phase1_use_szczesliwy')
        elif picked_card=="Remanent":
            return redirect('/local/phase1_use_remanent')
        elif picked_card=="Towar spod lady":
            return redirect('/local/phase1_use_towar')
        elif picked_card=="Kolega w Komitecie":
            return redirect('/local/phase1_use_kolega')
        elif picked_card=="Zwiększona dostawa":
            return redirect('/local/phase1_use_zwiekszona')
        elif picked_card=="Pomyłka w dostawie":
            return redirect('/local/phase1_use_pomylka')
        elif picked_card == "Spasuj":
            game.players[game.current_player_index].do_pass()
            if game.did_all_players_pass():
                return redirect('/local/phase2', code=302)
            else:
                game.move_to_next_player()
                return render_template('local/phase1.htm', game=game, player=game.players[game.current_player_index])

    else:
        if not game.does_any_player_have_cards():
            return redirect('/local/phase2', code=302)
        return render_template('local/phase1.htm', game=game, player=game.players[game.current_player_index])

@app.route('/local/phase1_use_pan', methods=['GET','POST'] )
def local_phase1_use_pan():
    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            game.use_pan(request.form['pawn_id'],request.form['shop_name'])
            game.players[game.current_player_index].remove_jostling_card("Pan tu nie stał")
            game.move_to_next_player()
        return redirect('/local/phase1', code=302)
    return  render_template('local/phase1_use_pan.htm', game=game, player=game.players[game.current_player_index], picked_card="Pan tu nie stał")

@app.route('/local/phase1_use_matka', methods=['GET','POST'] )
def local_phase1_use_matka():
    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            game.use_matka(request.form['pawn_id'],request.form['shop_name'])
            game.players[game.current_player_index].remove_jostling_card("Matka z dzieckiem")
            game.move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_matka.htm', game=game, player=game.players[game.current_player_index],
                               picked_card="Matka z dzieckiem")

@app.route('/local/phase1_use_krytyka', methods=['GET','POST'] )
def local_phase1_use_krytyka():
    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            game.use_krytyka(request.form['pawn_id'],request.form['shop_name'])
            game.players[game.current_player_index].remove_jostling_card("Krytyka władzy")
            game.move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_krytyka.htm', game=game, player=game.players[game.current_player_index],
                               picked_card="Krytyka władzy")

@app.route('/local/phase1_use_lista', methods=['GET','POST'] )
def local_phase1_use_lista():
    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            game.get_shop_queue(request.form['shop_name']).reverse()
            game.players[game.current_player_index].remove_jostling_card("Lista społeczna")
            game.move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_lista.htm', game=game, player=game.players[game.current_player_index],
                               picked_card="Lista społeczna")

@app.route('/local/phase1_use_szczesliwy', methods=['GET', 'POST'])
def local_phase1_use_szczesliwy():
    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            split_values = request.form['pawn_id'].split('#',1)
            game.use_szczesliwy(split_values[0], split_values[1], request.form['go_to_shop']) #pawn_id, start_shop, go_to_shop
            game.players[game.current_player_index].remove_jostling_card("Szczęśliwy traf")
            game.move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_szczesliwy.htm', game=game, player=game.players[game.current_player_index], picked_card="Szczęśliwy traf")

@app.route('/local/phase1_use_remanent', methods=['GET', 'POST'])
def local_phase1_use_remanent():
    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            game.use_remanent(request.form['shop_name'])
            game.players[game.current_player_index].remove_jostling_card("Remanent")
            game.move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_remanent.htm', game=game, player=game.players[game.current_player_index], picked_card="Remanent")

@app.route('/local/phase1_use_towar', methods=['GET','POST'])
def local_phase1_use_towar():
    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            outcome = game.use_towar(request.form['shop_name'], request.form['good'], game.players[game.current_player_index])
            if outcome is None:
                game.players[game.current_player_index].remove_jostling_card("Towar spod lady")
                game.move_to_next_player()
            else:
                return render_template('local/phase1_use_towar.htm', game=game, player=game.players[game.current_player_index], picked_card="Towar spod lady", message = outcome)
        return  redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_towar.htm', game=game, player=game.players[game.current_player_index], picked_card="Towar spod lady")

@app.route('/local/phase1_use_kolega', methods=['GET','POST'])
def local_phase1_use_kolega():
    if request.method == 'POST':
        game.players[game.current_player_index].remove_jostling_card("Kolega w Komitecie")
        game.move_to_next_player()
        return  redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_kolega.htm', game=game, player=game.players[game.current_player_index], picked_card="Kolega w Komitecie")

@app.route('/local/phase1_use_zwiekszona', methods=['GET', 'POST'])
def local_phase1_use_zwiekszona():
    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            game.use_zwiekszona(request.form['shop_name'])
            game.players[game.current_player_index].remove_jostling_card("Zwiększona dostawa")
            game.move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_zwiekszona.htm', game=game, player=game.players[game.current_player_index], picked_card="Zwiększona dostawa")

@app.route('/local/phase1_use_pomylka', methods=['GET', 'POST'])
def local_phase1_use_pomylka():
    if request.method == 'POST':
        if 'go_back' in request.form and request.form['go_back'] == 'yes':
            return redirect('/local/phase1', code=302)
        else:
            split_values = request.form['good_id'].split('#',1)
            game.use_pomylka(split_values[0], split_values[1], request.form['go_to_shop']) #good_name, start_shop, go_to_shop
            game.players[game.current_player_index].remove_jostling_card("Pomyłka w dostawie")
            game.move_to_next_player()
        return redirect('/local/phase1', code=302)
    return render_template('local/phase1_use_pomylka.htm', game=game, player=game.players[game.current_player_index], picked_card="Pomyłka w dostawie")

#Gracze i spekulanci zbierają przedmioty
@app.route('/local/phase2', methods=['GET', 'POST'])
def local_phase2():
    if request.method=='POST':
        if game.board.shops.get(request.form['shop_name']).available_goods and game.board.shops.get(request.form['shop_name']).queue:
            game.take_good_player(game.get_first_pawn(request.form['shop_name']), request.form['shop_name'], request.form['good_name'], game.players[game.get_pawn_owner_index(game.get_first_pawn(request.form['shop_name']))] )
    for shop in game.board.shops.values():
        if shop.is_open:
            for item in shop.available_goods:
                if shop.queue:
                    if shop.queue[0].color not in ['Kiosk', 'Meblowy', 'Spożywczy', 'Odzież', 'RTV-AGD']:
                        return render_template('local/phase2.htm', game=game, player=game.players[game.get_pawn_owner_index(shop.queue[0])], shop = shop, owner='player')
                    else:
                        game.take_good_speculant(game.get_first_pawn(shop.name), shop.name)
    return  render_template('local/stats.htm', game=game )


if __name__ == '__main__':
    app.run(host="wierzba.wzks.uj.edu.pl", port=5114, debug=True)

