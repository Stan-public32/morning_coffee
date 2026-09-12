import requests
from datetime import date

today_date = date.today()
WEATHER_CITY = "100524901"

url = "https://admin.europaplus.ru/api/main?region=1"
r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
r.raise_for_status()

data = r.json()
horoscopes = [data["data"]["horoscope"]["type"]
              [f"{num}"]["today"] for num in range(1, 13)]

url = "https://api.foreca.net/data/favorites/100524901.json"
w = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
w.raise_for_status()
dataw = w.json()[WEATHER_CITY]
dataw = dataw[0]

forecast_text = f"Прогноз погоды:\nМинимальная температура: {dataw['tmin']} C,\nМаксимальная температура: {dataw['tmax']} C,\nВосход Солнца: {dataw['sunrise']},\nЗакат Солнца: {dataw['sunset']}"
print(forecast_text)
print(dataw)

print(f"Гороскоп на {today_date}")
for horoscope in horoscopes:
    print(horoscope)
