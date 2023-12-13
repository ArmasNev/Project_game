import os
import requests

from dotenv import load_dotenv
load_dotenv()


class Weather:
    def __init__(self, location, game):
        apikey = os.environ.get("API_KEY")

        if apikey is None:
            raise ValueError("API_KEY environment variable is not set")

        request = "https://api.openweathermap.org/data/2.5/weather?lat=" + \
                  str(location["latitude"]) + "&lon=" + str(location["longitude"]) + "&appid=" + apikey

        response = requests.get(request).json()

        self.main = response["weather"][0]["main"]
        self.weather_code = response["weather"][0]["id"]
        self.description = response["weather"][0]["description"]
        self.wind = {
            "speed": response["wind"]["speed"]
        }

    def kelvin_to_celsius(self, kelvin):
        return int(kelvin - 273.15)

    def check_weather_condition(self):
        if 500 <= int(self.weather_code) <= 622:
            print(f"Correct weather condition: {self.main}")
            return True
        else:
            print(f"Incorrect weather condition: {self.main}")
            return False
