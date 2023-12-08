import json
import random
from database import Database
from flask import Flask
from flask_cors import CORS
from geopy import distance


db = Database()
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

money = 10000
@app.route('/get_airports')
def get_airports():
    sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
    FROM airport
    WHERE type='large_airport'
    ORDER by RAND()
    LIMIT 21;"""                                  #?
    cursor = db.get_conn().cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return json.dumps(result)
@app.route('/get_events')
def get_events():
    sql = "SELECT * FROM event;"
    cursor = db.get_conn().cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return json.dumps(result)

@app.route('/new_game')
def new_game(player, place, t_limit, money, a_ports):
    sql = """INSERT INTO game (name, location, time, bank) VALUES (%s, %s, %s, %s);"""
    cursor = db.get_conn().cursor(dictionary=True)
    cursor.execute(sql, (player, place, t_limit, money))
    g_id = cursor.lastrowid

    events = get_events()
    event_id = {1: 0.3, 2: 0.2, 3: 0.4, 4: 0.1}
    id_list = []

    for i in range(0, 19):
        random_id = random.choices(list(event_id.keys()),
                                   list(event_id.values()))
        id_list.append(random_id[0])
    id_list.append(5)
    random.shuffle(id_list)

    e_ports = a_ports[1:].copy()
    random.shuffle(e_ports)

    for i, event_id in enumerate(id_list):
        sql = "INSERT INTO events (location, event_id, game_id) VALUES (%s, %s, %s);"
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (e_ports[i]['ident'], event_id, g_id))
    return json.dumps(g_id)

# Get information about airport
def get_airport_info(icao):
    sql=f'''SELECT iso_country, ident, name, latitude_deg, longitude_deg
            FROM airport
            WHERE ident = %s'''
    cursor = db.get_conn().cursor(dictionary=True)
    cursor.execute(sql, (icao,))
    result = cursor.fetchall()

    return json.dumps(result)

@app.route('/airport_distance')
def airport_distance(current, target):
    start = get_airport_info(current)[0]  # Access the first (and only) item in the list
    end = get_airport_info(target)[0]  # Access the first (and only) item in the list
    start_coords = (start['latitude_deg'], start['longitude_deg'])
    end_coords = (end['latitude_deg'], end['longitude_deg'])
    return json.dumps(distance.distance(start_coords, end_coords).km)

@app.route('/airports_in_range')
def airports_in_range(icao, a_ports, p_range):
    in_range = []
    for a_port in a_ports:
        dist = airport_distance(icao, a_port['ident'])
        if dist <= p_range and not dist == 0:
            in_range.append(a_port)
    return json.dumps(in_range)


@app.route('/check_event')
def check_event(g_id, cur_airport):
    sql = '''
        SELECT events.id, event.id as event_id, event.min, event.max, events.game_id
        FROM events
        JOIN event ON event.id = events.event_id 
        WHERE game_id = %s 
        AND location = %s
    '''
    cursor = db.get_conn().cursor(dictionary=True)
    cursor.execute(sql, (g_id, cur_airport))
    result = cursor.fetchone()
    if result is None:
        return None
    return json.dumps(result)

@app.route('/update_location')
def update_location(g_id, name, icao, m, time):
    sql = '''UPDATE game SET name = %s, location = %s,  bank = %s, time = %s  WHERE id = %s'''
    cursor = db.get_conn().cursor(dictionary=True)
    cursor.execute(sql, (name, icao, money, time, g_id))

#t_limit = 0
#while True:
    #pet=input('What pet did you bring with you, a cat or a dog? ').lower()
    #if pet == "cat":
        #t_limit = 240
        #break
    #elif pet == "dog":
        #t_limit = 168
        #break
    #else:
        #print('Sorry, you can only take a cat or a dog.')


# boolean for game over and win
game_over = False
win = False
money = 10000
p_range = money*4
score = 0
pet_found = False

# all airports
all_airports = get_airports()
# start_airport ident

# current airport

game_over = False

"""while not game_over:
    event = check_event(game_id, current_airport)
    airports = airports_in_range(current_airport, all_airports, p_range)
    print(f'{bcolors.BLUE}There are {len(airports)} airports in range: {bcolors.ENDC}')

    # Check if player is out of range
    if p_range < 0:
        print('You are out of range.')
        game_over = True


    # Get current airport info
    airport = get_airport_info(current_airport)

    # Show game status
    print(f"You are at {airport[0]['ident']} ({airport[0]['name']}).")
    print(f'You have {bcolors.GREEN}{money:.0f}${bcolors.ENDC} and {bcolors.YELLOW}{t_limit}{bcolors.ENDC} hours left to find the {pet}.')
    input(f"{bcolors.CYAN}Press Enter to continue: {bcolors.ENDC}")
    print('Your pet is in one of these airports: ')

    sorted_airports = sorted(all_airports, key=lambda x: airport_distance(current_airport, x["ident"]))

    # Print sorted airports
    for i, airport in enumerate(sorted_airports):
        ap_distance = airport_distance(current_airport, airport["ident"])
        if ap_distance < p_range:
            print(f'{i + 1}. {airport["name"]}, icao: {airport["ident"]}, distance: {ap_distance:.0f}km)')

    # Ask for destination
    print(f'You have money left for a {p_range} km flight.')
    dest = input(f'Where do you want to go? ICAO: ')
    selected_distance = airport_distance(current_airport, dest)
    money -= selected_distance // 4
    t_limit -= selected_distance // 1000
    p_range = money * 4
    update_location(game_id, player, dest, money, t_limit)
    current_airport = dest

    # Check if pet is found and player is at start (game won)
    if win and current_airport == s_airport:
        print(f'You are at {airport[0]["name"]}.')
        print(f'You have {bcolors.GREEN}{money:.0f}${bcolors.ENDC} and {bcolors.YELLOW}{t_limit}{bcolors.ENDC} hours left to find the {pet}.')
        game_over = True

    event = check_event(game_id, current_airport)
    if event:
        event_id = event.get('event_id', None)
        min_value = event.get('min', 0)
        max_value = event.get('max', 0)

        if event_id == 1:
            temp_money = random.randrange(min_value, max_value, 100)
            money -= temp_money

            t_limit = t_limit - 10
            print(f"Customs check! You just lost {bcolors.RED}{bcolors.UNDERLINE}{temp_money}${bcolors.ENDC} and {bcolors.YELLOW}10{bcolors.ENDC} hours!")
        elif event_id == 2:
            print(f"{bcolors.RED}Storm! Your next flight is delayed.{bcolors.ENDC}")
            t_limit -= 20
        elif event_id == 3:
            temp_money = random.randrange(min_value, max_value, 100)
            money += temp_money
            print(f"Incoming money transfer received! You just got {bcolors.GREEN}{bcolors.UNDERLINE}{temp_money}${bcolors.ENDC}!")

        elif event_id == 4:
            pass  # Do nothing for event 4
        elif event_id == 5:
            print(f"You found the {bcolors.GREEN}{bcolors.UNDERLINE}{pet}{bcolors.ENDC}!")
            win = True
        input(f"{bcolors.CYAN}Press Enter to continue!{bcolors.ENDC}")

    if money <= 0:
        print(f"{bcolors.RED}{bcolors.BOLD}You are out of money!{bcolors.ENDC}")
        game_over = True"""

if __name__ == '__main__':
    app.run(use_reloader=True, host='127.0.0.1', port=5000)
