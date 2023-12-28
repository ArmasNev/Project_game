import json
import random

from flask import Flask, jsonify, request
from flask_cors import CORS
from geopy import distance
from game import Game
import os
import requests

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/newgame')
def newgame():
    name = request.args.get("name", "default_player")
    pet = request.args.get("selectedPet", "default_pet")
    game = Game(name=name, pet=pet)
    game_id = game.new_game()
    return jsonify({'game_id': game_id, 'airports': game.airports})


@app.route('/flyto/<int:game_id>/<target>')
def flyto(game_id, target):
    game = Game(game_id=game_id)
    if not game.load_game():
        return jsonify({'error': 'Game not found'}), 404

    try:
        event_message = game.fly_to(target)
        event = game.check_event(game.game_id, game.current_location)
        game.handle_event(event) if event else None
        game_over = game.is_game_over()
        game_over_message = game.game_over_status() if game_over else ""
        print({
            'status': {
                'id': game.game_id,
                'location': game.current_location,
                'money': game.money,
                'time': game.time,
                'distance': game.money * 4,
                'event_info': event_message,
                'game_over': game_over,
                'game_over_message': game_over_message,
                'has_won': game.win,
                'prev_location': game.prev_location_coords,
                'curr_location': game.curr_location_coords
            },
            'game_id': game.game_id,
            'location': game.current_location
        })
        return jsonify({
            'status': {
                'id': game.game_id,
                'location': game.current_location,
                'money': game.money,
                'time': game.time,
                'distance': game.money * 4,
                'event_info': event_message,
                'game_over': game_over,
                'game_over_message': game_over_message,
                'has_won': game.win,
                'prev_location': game.prev_location_coords,
                'curr_location': game.curr_location_coords
            },
            'game_id': game.game_id,
            'location': game.current_location
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/get_weather/<lat>/<lon>')
def get_weather(lat, lon):
    apikey = os.environ.get("API_KEY")
    weather_request = "https://api.openweathermap.org/data/2.5/weather?lat=" + \
                      str(lat) + "&lon=" + str(lon) + "&appid=" + apikey
    response = requests.get(weather_request).json()
    print(response)
    return json.dumps(response)

@app.route('/time_update/<int:game_id>')
def time_update(game_id):
    game = Game(game_id=game_id)
    if not game.load_game():
        return jsonify({'error': 'Game not found'}), 404
    try:
        delay = random.randint(4, 24)
        game.time -= delay
        game.update_game_state()
        return jsonify({"game_id": game_id, "time_reduced_by": delay})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
