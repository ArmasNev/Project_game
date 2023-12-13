from dotenv import load_dotenv
from database import Database
from weather import Weather
from geopy import distance
load_dotenv()

conn = Database.get_conn()


class Airport:
    def __init__(self, ident, active=False, data=None):
        self.weather = None
        self.ident = ident
        self.active = active

        if data is None:
            # find airport from database
            sql = "SELECT ident, name, latitude_deg, longitude_deg FROM airport WHERE ident='" + ident + "'"
            print(sql)
            cur = conn.cursor()
            cur.execute(sql)
            res = cur.fetchall()
            if len(res) == 1:
                # game was found
                self.ident = res[0][0]
                self.latitude = res[0][1]
                self.longitude = res[0][3]
            else:
                # wasn't found
                self.name = data['name']
                self.latitude = float(data['latitude'])
                self.longitude = float(data['longitude'])

    def find_nearby_airports(self, max_distance):
        airport_list = []

        sql = "SELECT ident, name, latitude_deg, longitude_deg FROM Airport WHERE latitude_deg BETWEEN "
        sql += str(self.latitude - max_distance) + " AND " + str(self.latitude +max_distance)
        sql += " AND longitude_deg BETWEEN "
        sql += str(self.longitude - max_distance) + " AND " + str(self.longitude + max_distance)
        print(sql)
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        for r in res:
            if r[0] != self.ident:
                data = {'name' : r[1], 'latitude' : r[2], 'longitude' : r[3]}
                print(data)
                nearby_apt = Airport(r[0], False, data)
                nearby_apt.distance = self.distance_to(nearby_apt)
                if nearby_apt <= max_distance:
                    airport_list.append(nearby_apt)


    def fetch_weather(self, game):
        self.weather = Weather(self, game)

    def distance_to(self, target):
        pos1 = (self.latitude, self.longitude)
        pos2 = (target.latitude, target.longitude)
        dist = distance.distance(pos1, pos2).km

    def remove_distance(self, km, distance):
        dist = distance - km
        return dist


