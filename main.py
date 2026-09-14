#!/usr/bin/env python3

import requests
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import date
from bs4 import BeautifulSoup


class Morning_report:
    def __init__(self):
        self.today_date = date.today()
        self.weather_city = "100524901"
        self.weekdays_dict = {0: "понедельник", 1: "вторник", 2: "среда",
                              3: "четверг", 4: "пятница", 5: "суббота", 6: "воскресенье"}
        self.months_dict = {1: "январь", 2: "февраль", 3: "март", 4: "апрель", 5: "май", 6: "июнь",
                            7: "июль", 8: "август", 9: "сентябрь", 10: "октябрь", 11: "ноябрь", 12: "декабрь"}
        self.zodiac_signs = {0: "Овен", 1: "Телец", 2: "Близнецы", 3: "Рак", 4: "Лев", 5: "Дева",
                             6: "Весы", 7: "Скорпион", 8: "Стрелец", 9: "Козерог", 10: "Водолей", 11: "Рыбы"}

    def get_horoscope(self):
        url = "https://admin.europaplus.ru/api/main?region=1"
        r = requests.get(url, timeout=10, headers={
                         "User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        horoscopes = [data["data"]["horoscope"]["type"]
                      [f"{num}"]["today"] for num in range(1, 13)]
        dict_out = {}
        for i in range(12):
            start = horoscopes[i].find(',')
            horoscopes[i] = horoscopes[i][start+1:]
            dict_out[self.zodiac_signs[i]] = horoscopes[i]
        return dict_out

    def get_greetings(self):
        if self.today_date.month == 3 or self.today_date.month == 8:
            text_month = self.months_dict[self.today_date.month] + "а"
        else:
            text_month = (self.months_dict[self.today_date.month])[:-1] + "я"
        text_output = "Сегодня " + \
            self.weekdays_dict[self.today_date.weekday()] + ", " + str(self.today_date.day) + " " + text_month + " " + \
            str(self.today_date.year) + " года!"
        return text_output

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
        forecast_text = f"Минимальная температура: {dataw['tmin']}°C, "
        forecast_text += f"Максимальная температура: {dataw['tmax']}°C\nОсадков за сутки: {dataw['rain']} мм, "
        forecast_text += f"Вероятность дождя: {dataw['rainp']}%\n"
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
        list_dict_sci_news = []
        if len(dates) != len(headers):
            raise Exception("Ошибка получения информации от Naked Science.")
        for i in range(len(dates)):
            dict_sci_news = {}
            link_str = str(headers[i].find("div", class_="news-item-title"))
            start_pos = link_str.find("href=")
            link_str = link_str[start_pos + 6:]
            end_pos = link_str.find('"')
            link_str = link_str[:end_pos]
            dict_sci_news['title'] = headers[i].find(
                "div", class_="news-item-title").text.strip()
            str_to_print = dict_sci_news['title']
            dict_sci_news['date'] = dates[i].find(
                "span", class_="echo_date").text.strip()
            str_to_print += "\n" + \
                dict_sci_news['date']
            dict_sci_news['url'] = link_str
            str_to_print += ". " + \
                link_str
            dict_sci_news['summary'] = headers[i].find(
                "div", class_="news-item-excerpt").text.strip()
            str_to_print += "\n" + \
                dict_sci_news['summary'] + "\n"
            news_blocks.append(str_to_print)
            list_dict_sci_news.append(dict_sci_news)
        text_news = "\nНовости науки и техники:\n\n"
        text_news += "--------\n".join(news_blocks)
        return text_news, list_dict_sci_news

    def get_business_news(self):
        url = "https://www.bfm.ru/"
        bn = requests.get(url, timeout=10, headers={
                          "User-Agent": "Mozilla/5.0"})
        bn.raise_for_status()
        soup = BeautifulSoup(bn.text, "html.parser")
        news_block = soup.find_all("article", class_="main-block-news")
        news_list = []
        list_dict_business_news = []
        for block in news_block:
            dict_business_news = {}
            dict_business_news['title'] = block.find(
                "a", class_="block-title").text
            another_string = dict_business_news['title'] + "\n"
            dict_business_news['date'] = str(self.today_date)
            another_string += dict_business_news['date'] + ", "
            position_start = str(block).find('href="')
            text_link = "https://www.bfm.ru" + str(block)[position_start + 6:]
            position_end = text_link.find('"')
            text_link = text_link[:position_end]
            dict_business_news['url'] = text_link
            another_string += dict_business_news['url'] + "\n"
            dict_business_news['summary'] = block.find(
                "a", class_="description").text
            if dict_business_news['summary'][-1] != '.':
                dict_business_news['summary'] += '.'
            another_string += dict_business_news['summary']
            another_string += "\n"
            news_list.append(another_string)
            list_dict_business_news.append(dict_business_news)
        news_output = "\n\nГлавные новости - Россия и мир:\n\n" + \
            "--------\n".join(news_list)
        return news_output, list_dict_business_news


def main():
    report = Morning_report()
    text_greetings = report.get_greetings()
    horoscope = report.get_horoscope()
    text_horoscope = "\nГороскоп: " + str(horoscope['Весы'])
    weather = report.get_weather()
    text_weather = weather
    text_news_business, society_news = report.get_business_news()
    text_news_sci, science_news = report.get_sci_news()
    total_text_report = text_greetings + "\n" + text_horoscope + \
        "\n" + text_weather + "\n" + \
        text_news_business + "\n" + text_news_sci
    print(total_text_report)
    print('\n')
    context = {
        "weather": weather,
        "horoscope": horoscope,
        "society_news": society_news,
        "science_news": science_news,
    }
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    html_string = template.render(context)
    Path("output").mkdir(exist_ok=True)
    HTML(string=html_string, base_url='.').write_pdf(
        "output/Morning_Coffee.pdf",
        stylesheets=[CSS('style.css')]
    )

    print("✅ PDF создан: output/Morning_Coffee.pdf")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(
            f"\n\n#####################\nВозникла непредвиденная ошибка:\n{e}\n#####################\n\n")
