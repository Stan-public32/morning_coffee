#!/usr/bin/env python3

import requests
from datetime import date
from bs4 import BeautifulSoup


class Morning_report:
    def __init__(self):
        self.today_date = date.today()
        self.weather_city = "100524901"
        self.horoscope_sign = 7
        self.weekdays_dict = {0: "понедельник", 1: "вторник", 2: "среда",
                              3: "четверг", 4: "пятница", 5: "суббота", 6: "воскресенье"}
        self.months_dict = {1: "январь", 2: "февраль", 3: "март", 4: "апрель", 5: "май", 6: "июнь",
                            7: "июль", 8: "август", 9: "сентябрь", 10: "октябрь", 11: "ноябрь", 12: "декабрь"}

    def get_horoscope(self):
        url = "https://admin.europaplus.ru/api/main?region=1"
        r = requests.get(url, timeout=10, headers={
                         "User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        horoscopes = [data["data"]["horoscope"]["type"]
                      [f"{num}"]["today"] for num in range(1, 13)]
        text_out = "\nГороскоп: " + \
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
        forecast_text = f"\nПрогноз погоды:\nМинимальная температура: {dataw['tmin']}°C, "
        forecast_text += f"Максимальная температура: {dataw['tmax']}°C\nОсадков за сутки: {dataw['rain']} мм, "
        forecast_text += f"Вероятность дождя: {dataw['rainp']}%, Вероятность снега: {dataw['snowp']}%\n"
        forecast_text += f"Относительная влажность: {dataw['rhum']}%\nСредняя скорость ветра: {dataw['winds']} м/с\n"
        forecast_text += f"Восход: {dataw['sunrise']}, Закат: {dataw['sunset']}\nФаза Луны: {moon_text}"
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
        text_news = "\nНовости науки и техники:\n\n"
        text_news += "--------\n".join(news_blocks)
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
        news_output = "\n\nГлавные новости - Россия и мир:\n\n" + \
            "--------\n".join(news_list)
        return news_output

    def get_greetings(self):
        if self.today_date.month == 3 or self.today_date.month == 8:
            text_month = self.months_dict[self.today_date.month] + "а"
        else:
            text_month = (self.months_dict[self.today_date.month])[:-1] + "я"
        text_output = "Сегодня " + \
            self.weekdays_dict[self.today_date.weekday()] + ", " + str(self.today_date.day) + " " + text_month + " " + \
            str(self.today_date.year) + " года!"
        return text_output


def main():
    report = Morning_report()
    text_greetings = report.get_greetings()
    text_horoscope = report.get_horoscope()
    text_weather = report.get_weather()
    text_news_business = report.get_business_news()
    text_news_sci = report.get_sci_news()
    total_text_report = text_greetings + "\n" + text_horoscope + \
        "\n" + text_weather + "\n" + text_news_business + "\n" + text_news_sci
    print(total_text_report)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(
            f"\n\n#####################\nВозникла непредвиденная ошибка:\n{e}\n#####################\n\n")
