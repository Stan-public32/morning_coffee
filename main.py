import requests

url = "https://admin.europaplus.ru/api/main?region=1"
r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
r.raise_for_status()

data = r.json()
num = 7
horoscopes = [data["data"]["horoscope"]["type"]
              [f"{num}"]["today"] for num in range(1, 13)]
for horoscope in horoscopes:
    print(horoscope)
