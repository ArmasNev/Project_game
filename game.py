import random
from database import Database

db = Database()

class Game():
    def __init__(self, id, loc, money, time, player=None):
        self.location = loc
        self.airports = []
        self.goals = []
        self.money = money
        self.p_range = money * 4
        self.time = time
        self.player = player
        self.id = id


    def get_airports():
        sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
        FROM airport
        WHERE type='large_airport'
        ORDER by RAND()
        LIMIT 21;"""                                  #?
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def get_events(self):
        sql = "SELECT * FROM event;"
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result


    def new_game(self, a_ports):
        sql = """INSERT INTO game (name, location, time, bank) VALUES (%s, %s, %s, %s);"""
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (self.player, self.location, self.time, self.money))
        g_id = cursor.lastrowid

        events = self.get_events()
        event_id = {1: 0.4, 3: 0.4, 4: 0.2}
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
        return g_id

    # Get information about airport
    def get_airport_info(icao):
        sql=f'''SELECT iso_country, ident, name, latitude_deg, longitude_deg
                FROM airport
                WHERE ident = %s'''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (icao,))
        result = cursor.fetchall()
        return result


    def airport_distance(current, target):
        start = get_airport_info(current)[0]  # Access the first (and only) item in the list
        end = get_airport_info(target)[0]  # Access the first (and only) item in the list
        start_coords = (start['latitude_deg'], start['longitude_deg'])
        end_coords = (end['latitude_deg'], end['longitude_deg'])
        return distance.distance(start_coords, end_coords).km

    def airports_in_range(icao, a_ports, p_range):
        in_range = []
        for a_port in a_ports:
            dist = airport_distance(icao, a_port['ident'])
            if dist <= p_range and not dist == 0:
                in_range.append(a_port)
        return in_range



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
        return result


    def update_location(g_id, name, icao, m, time):
        sql = '''UPDATE game SET name = %s, location = %s,  bank = %s, time = %s  WHERE id = %s'''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (name, icao, money, time, g_id))


"""
    t_limit = 0
    while True:
        pet=input('What pet did you bring with you, a cat or a dog? ').lower()
        if pet == "cat":
            t_limit = 240
            break
        elif pet == "dog":
            t_limit = 168
            break
        else:
            print('Sorry, you can only take a cat or a dog.')


    # boolean for game over and win
    game_over = False
    win = False
    money = 10000

    score = 0
    pet_found = False

    # all airports
    all_airports = get_airports()
    # start_airport ident
    s_airport = all_airports[0]['ident']

    # current airport
    current_airport = s_airport

    game_id = new_game(player, s_airport, t_limit, money, all_airports)

    game_over = False


    while not game_over:
        event = check_event(game_id, current_airport)
        airports = airports_in_range(current_airport, all_airports, p_range)
        print(f'There are {len(airports)} airports in range: ')

        # Check if player is out of range
        if p_range < 0:
            print('You are out of range.')
            game_over = True


        # Get current airport info
        airport = get_airport_info(current_airport)

        # Show game status
        print(f"You are at {airport[0]['ident']} ({airport[0]['name']}).")
        print(f'You have {money:.0f}$and {t_limit} hours left to find the {pet}.')
        input(f"Press Enter to continue: ")
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
            print(f'You have {money:.0f}$ and {t_limit} hours left to find the {pet}.')
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
                print(f"Customs check! You just lost {temp_money}$ and 10 hours!")
            elif event_id == 2:
                print(f"Storm! Your next flight is delayed.")
                t_limit -= 20
            elif event_id == 3:
                temp_money = random.randrange(min_value, max_value, 100)
                money += temp_money
                print(f"Incoming money transfer received! You just got {temp_money}$!")

            elif event_id == 4:
                pass  # Do nothing for event 4
            elif event_id == 5:
                print(f"You found the {pet}!")
                win = True
            input(f"Press Enter to continue!")

        if money <= 0:
            print(f"You are out of money!")
            game_over = True


"""