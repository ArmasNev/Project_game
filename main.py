import json
from flask import Flask, request
from flask_cors import CORS
from geopy import distance
from game import Game


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/newgame')
def newgame():
    args = request.args
    name = args.get("name")
    peli = Game(0, 'EFHK', 10000, 240, name)
    airports = peli.get_airports()
    game_id = peli.new_game(airports)
    response = {'game_id': game_id, 'airports': airports}
    return json.dumps(response)

def fly(id, dest, consumption=0, player=None):
    if id==0:
        game = Game(0, dest, consumption, player)
    else:
        game = Game(id, dest, consumption)
    game.location[0].fetchWeather(game)
    nearby = game.location[0].find_nearby_airports()
    for a in nearby:
        game.location.append(a)
    json_data = json.dumps(game, default=lambda o: o.__dict__, indent=4)
    return json_data

@app.route('/flyto/<game_id>/<target>')
def flyto(game_id, target):
    peli = Game(game_id, target)
    response = {peli}
    print(json.dumps(response))
    return json.dumps(response)

if __name__ == '__main__':
    app.run(use_reloader=True, host='127.0.0.1', port=5000)


