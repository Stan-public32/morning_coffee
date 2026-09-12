import requests
from datetime import date
from bs4 import BeautifulSoup

TODAY_DATE = date.today()
WEATHER_CITY = "100524901"
HOROSCOPE_SIGN = 7

url = "https://admin.europaplus.ru/api/main?region=1"
r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
r.raise_for_status()

data = r.json()
horoscopes = [data["data"]["horoscope"]["type"]
              [f"{num}"]["today"] for num in range(1, 13)]

print(f"\nГороскоп на {TODAY_DATE}")
print(horoscopes[HOROSCOPE_SIGN-1])

url = "https://api.foreca.net/data/favorites/100524901.json"
w = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
w.raise_for_status()
dataw = w.json()[WEATHER_CITY]
dataw = dataw[0]
moon = int(dataw['moonphase'])
if 10 < moon < 170:
    moon_percentage = moon * 100 // 180
    moon_text = "растущая, " + str(moon_percentage) + "%"
elif 170 <= moon <= 190:
    moon_percentage = (180 - abs(moon - 180)) * 100 // 180
    moon_text = "полнолуние, " + str(moon_percentage) + "%"
elif 190 < moon < 350:
    moon_percentage = (360 - moon) * 100 // 180
    moon_text = "убывающая, " + str(moon_percentage) + "%"
else:
    moon_percentage = (360 - moon) * \
        100 // 180 if moon > 180 else moon * 100 // 180
    moon_text = "новолуние, " + str(moon_percentage) + "%"


forecast_text = f"\nПрогноз погоды на {dataw['date']}:\nМинимальная температура: {dataw['tmin']}°C\n"
forecast_text += f"Максимальная температура: {dataw['tmax']}°C\nОсадков за сутки: {dataw['rain']} мм\n"
forecast_text += f"Вероятность дождя: {dataw['rainp']}%\nВероятность снега: {dataw['snowp']}%\n"
forecast_text += f"Относительная влажность: {dataw['rhum']}%\nСредняя скорость ветра: {dataw['winds']} м/с\n"
forecast_text += f"Восход: {dataw['sunrise']}\nЗакат: {dataw['sunset']}\nФаза Луны: {moon_text}"
print(forecast_text)


url = "https://naked-science.ru/"
web_sci = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
web_sci.raise_for_status()
soup = BeautifulSoup(web_sci.text, "html.parser")
news = soup.find("div", class_="feed-container active", id="feed-today")
dates = news.find_all("div", class_="post-meta-info")
headers = news.find_all("div", class_="community-item-midland")
news_blocks = []
if len(dates) != len(headers):
    raise Exception("Ошибка получения информации от Naked Science.")
for i in range(len(dates)):
    link_str = str(headers[i].find("div", class_="news-item-title"))
    start_pos = link_str.find("href=")
    link_str = link_str[start_pos + 6:]
    end_pos = link_str.find('"')
    link_str = link_str[:end_pos]
    str_to_print = headers[i].find(
        "div", class_="news-item-title").text.strip()
    str_to_print += "\n" + \
        dates[i].find("span", class_="echo_date").text.strip()
    str_to_print += ". " + \
        link_str
    str_to_print += "\n" + \
        headers[i].find("div", class_="news-item-excerpt").text.strip() + "\n"
    news_blocks.append(str_to_print)

print("\n\nНовости науки.\n")

for block in news_blocks:
    print(block)
