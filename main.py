import requests
from datetime import date
from bs4 import BeautifulSoup


class Morning_report:
    def __init__(self):
        self.today_date = date.today()
        self.weather_city = "100524901"
        self.horoscope_sign = 7

    def get_horoscope(self):
        url = "https://admin.europaplus.ru/api/main?region=1"
        r = requests.get(url, timeout=10, headers={
                         "User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        horoscopes = [data["data"]["horoscope"]["type"]
                      [f"{num}"]["today"] for num in range(1, 13)]
        text_out = f"\nГороскоп на {self.today_date}" + \
            horoscopes[self.horoscope_sign-1]
        return text_out

    def get_weather(self):
        url = "https://api.foreca.net/data/favorites/" + self.weather_city + ".json"
        w = requests.get(url, timeout=10, headers={
                         "User-Agent": "Mozilla/5.0"})
        w.raise_for_status()
        dataw = w.json()[self.weather_city]
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
        forecast_text = f"\n\nПрогноз погоды на {dataw['date']}:\nМинимальная температура: {dataw['tmin']}°C\n"
        forecast_text += f"Максимальная температура: {dataw['tmax']}°C\nОсадков за сутки: {dataw['rain']} мм\n"
        forecast_text += f"Вероятность дождя: {dataw['rainp']}%\nВероятность снега: {dataw['snowp']}%\n"
        forecast_text += f"Относительная влажность: {dataw['rhum']}%\nСредняя скорость ветра: {dataw['winds']} м/с\n"
        forecast_text += f"Восход: {dataw['sunrise']}\nЗакат: {dataw['sunset']}\nФаза Луны: {moon_text}"
        return forecast_text

    def get_sci_news(self):
        url = "https://naked-science.ru/"
        web_sci = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"})
        web_sci.raise_for_status()
        soup = BeautifulSoup(web_sci.text, "html.parser")
        news = soup.find(
            "div", class_="feed-container active", id="feed-today")
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
                headers[i].find(
                    "div", class_="news-item-excerpt").text.strip() + "\n"
            news_blocks.append(str_to_print)
        text_news = "\n\nНовости науки.\n"
        text_news += "\n\n".join(news_blocks)
        return text_news

    def get_business_news(self):
        url = "https://www.bfm.ru/"
        bn = requests.get(url, timeout=10, headers={
                          "User-Agent": "Mozilla/5.0"})
        bn.raise_for_status()
        soup = BeautifulSoup(bn.text, "html.parser")
        news_block = soup.find_all("article", class_="main-block-news")
        news_list = []
        for block in news_block:
            another_string = block.find("a", class_="block-title").text + "\n"
            another_string += str(self.today_date) + ", "
            position_start = str(block).find('href="')
            text_link = "https://www.bfm.ru" + str(block)[position_start + 6:]
            position_end = text_link.find('"')
            text_link = text_link[:position_end]
            another_string += text_link + "\n"
            another_string += block.find("a", class_="description").text
            if another_string[-1] != '.':
                another_string += '.'
            another_string += "\n"
            news_list.append(another_string)
        news_output = "\n--------\n".join(news_list)
        return news_output


if __name__ == '__main__':
    try:
        main()
    except Exception as {e}:
        print(
            f"\n\n#####################\nВозникла непредвиденная ошибка:\n{e}\n#####################\n\n")
