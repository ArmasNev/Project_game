import json


from flask import Flask
from flask_cors import CORS
from geopy import distance
from game import Game


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/newgame/<nimi>')
def newgame(nimi):
    peli = Game(0, 'EFHK', 10000, 240, nimi)
    airports = peli.get_airports()
    game_id = peli.new_game(airports)
    response = {'game_id': game_id}
    return json.dumps(response)

@app.route('/flyto/<game_id>/<target>')
def flyto(game_id, target):
    peli = Game(game_id, target)
    response = {peli}
    print(json.dumps(response))
    return json.dumps(response)






if __name__ == '__main__':
    app.run(use_reloader=True, host='127.0.0.1', port=5000)


