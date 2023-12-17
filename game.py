import random
from database import Database
from geopy import distance
from geopy.distance import great_circle

db = Database()


class Game:
    def __init__(self, game_id=None, name='Default'):
        self.game_id = game_id
        self.name = name
        self.airports = []
        self.current_location = None
        self.money = 10000
        self.time = 240
        self.win = False

        if self.game_id is None:
            self.airports = self.get_airports()
            if self.airports:
                self.current_location = self.airports[0]['ident']

    def get_airports(self):
        sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
                 FROM airport
                 WHERE type='large_airport'
                 ORDER BY RAND()
                 LIMIT 20;"""
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql)
        return cursor.fetchall()

    def get_airport_info(self, icao):
        sql = f'''SELECT iso_country, ident, name, latitude_deg, longitude_deg
                FROM airport
                WHERE ident = %s'''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (icao,))
        result = cursor.fetchall()
        return result

    def get_events(self):
        sql = "SELECT * FROM event;"
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def airport_distance(self, current, target):
        start = self.get_airport_info(current)[0]  # Access the first (and only) item in the list
        end = self.get_airport_info(target)[0]  # Access the first (and only) item in the list
        start_coords = (start['latitude_deg'], start['longitude_deg'])
        end_coords = (end['latitude_deg'], end['longitude_deg'])
        return distance.distance(start_coords, end_coords).km

    def airports_in_range(self, icao, a_ports, p_range):
        in_range = []
        for a_port in a_ports:
            dist = self.airport_distance(icao, a_port['ident'])
            if dist <= p_range and not dist == 0:
                in_range.append(a_port)
        return in_range

    def check_event(self, g_id, cur_airport):
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

    def update_location(self, g_id, name, icao, m, time):
        sql = '''UPDATE game SET name = %s, location = %s,  bank = %s, time = %s  WHERE id = %s'''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (name, icao, self.money, time, g_id))

    def new_game(self):
        if self.current_location is None and self.airports:
            self.current_location = self.airports[0]['ident']

        sql = """INSERT INTO game (name, location, bank, time) VALUES (%s, %s, %s, %s);"""
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (self.name, self.current_location, self.money, self.time))
        self.game_id = cursor.lastrowid

        pet_airport = random.choice(self.airports)
        sql = "INSERT INTO events (location, event_id, game_id) VALUES (%s, 5, %s);"
        cursor.execute(sql, (pet_airport['ident'], self.game_id))

        remaining_airports = [airport for airport in self.airports if airport['ident'] != pet_airport['ident']]

        event_id_weights = {1: 0.3, 3: 0.2, 4: 0.5}

        for airport in remaining_airports:
            event_id = random.choices(list(event_id_weights.keys()), weights=event_id_weights.values(), k=1)[0]
            sql = "INSERT INTO events (location, event_id, game_id) VALUES (%s, %s, %s);"
            cursor.execute(sql, (airport['ident'], event_id, self.game_id))

        db.get_conn().commit()
        return self.game_id

    def load_game(self):
        if self.game_id is None:
            return False

        sql = "SELECT * FROM game WHERE id = %s;"
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (self.game_id,))
        result = cursor.fetchone()

        if not result:
            return False

        self.current_location = result['location']
        self.money = result['bank']
        self.time = result['time']

        return True

    def fly_to(self, target_airport_id):
        print(self.current_location, target_airport_id)
        if self.current_location == target_airport_id:
            raise Exception("You are already at this airport.")

        current_airport = self.get_airport_info(self.current_location)
        target_airport = self.get_airport_info(target_airport_id)

        if not current_airport or not target_airport:
            raise Exception("Airport information not found.")

        try:
            distance_km = great_circle((current_airport[0]['latitude_deg'], current_airport[0]['longitude_deg']),
                                       (target_airport[0]['latitude_deg'],
                                        target_airport[0]['longitude_deg'])).kilometers
        except Exception as e:
            raise Exception(f"Error calculating distance: {str(e)}")

        cost = distance_km / 40
        if self.money < cost:
            raise Exception(f"Insufficient funds for this flight. Required: {cost}, Available: {self.money}")

        self.current_location = target_airport_id
        self.money -= cost
        self.time -= 30
        self.update_game_state()
        event = self.check_event(self.game_id, self.current_location)
        event_message = ""
        if event:
            event_message = self.handle_event(event)

        return event_message

    def handle_event(self, event):
        event_id = event.get('event_id')
        min_value = event.get('min', 0)
        max_value = event.get('max', 0)

        if event_id == 1:
            temp_money = random.randrange(min_value, max_value + 1, 100)
            self.money -= temp_money
            self.time -= 10
            event_message = f"Customs check!{temp_money}$ and 10 hours lost!"
            return event_message

        elif event_id == 2:
            pass

        elif event_id == 3:
            temp_money = random.randrange(min_value, max_value + 1, 100)
            self.money += temp_money
            event_message = f"Incoming money transfer received! {temp_money}$!"
            return event_message

        elif event_id == 4:
            pass

        elif event_id == 5:
            self.win = True
            event_message = "Congratulations! You found the pet and won the game!"
            print(event_message)
            return event_message

    def is_game_over(self):
        return self.money <= 0 or self.time <= 0

    def game_over_status(self):
        if self.money <= 1000:
            return "Game Over: You have not enough money to flight!"
        elif self.time <= 0:
            return "Game Over: You are out of time!"
        else:
            return "Game continues"

    def update_game_state(self):
        sql = '''UPDATE game SET location = %s, bank = %s, time = %s WHERE id = %s'''
        cursor = db.get_conn().cursor(dictionary=True)
        cursor.execute(sql, (self.current_location, self.money, self.time, self.game_id))
        db.get_conn().commit()
