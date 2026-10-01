#!/usr/bin/env python3

import emails
import requests
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import date
from datetime import datetime
from random import randint
import time
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

    def get_currency(self):
        url = "https://www.cbr.ru/currency_base/daily/"
        r = requests.get(url, timeout=10, headers={
                         "User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        curr = soup.find("div", class_="table-wrapper")
        target_segment = curr.find_all("tr")
        curr_codes = ["<td>840</td>", "<td>978</td>", "<td>156</td>"]
        results = []
        for code in curr_codes:
            temp = str(target_segment)[str(target_segment).find(str(code)):]
            temp = temp[:str(temp).find("</tr>")]
            temp_list = temp.split('\n')
            temp = temp_list[1][4:-5] + ': '
            temp += temp_list[4][4:-7]
            results.append(temp)
        return ', '.join(results) + '.'

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
        icon_code = list(dataw['symb'][1:])
        if icon_code[0] == "0" or icon_code[0] == "1":
            icon_file = "img/clear.png"
        elif icon_code[0] == "2" or icon_code[0] == "3":
            icon_file = "img/sun_clouds.png"
        elif icon_code[1] == "4":
            icon_file = "img/lightning.png"
        elif (icon_code[1] == "1" or icon_code[1] == "2" or icon_code[1] == "3") and (icon_code[2] == "0" or icon_code[2] == "1"):
            icon_file = "img/raining.png"
        elif (icon_code[1] == "1" or icon_code[1] == "2" or icon_code[1] == "3") and (icon_code[2] == "2"):
            icon_file = "img/snowy.png"
        else:
            icon_file = "img/cloudy.png"
        return forecast_text, icon_file

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
        imgs = news.find_all("div", class_="news-item-image-inner")
        imgs_dict = {}
        for img_block in imgs:
            start_pos = str(img_block).find("href=")
            ref = str(img_block)[start_pos+6:]
            end_position = ref.find('"')
            ref = ref[:end_position]
            img = str(img_block)[end_position+1:]
            start_pos = img.find('src="')
            img = img[start_pos+5:]
            end_position = img.find('"')
            img = img[:end_position]
            imgs_dict[ref] = img
        news_blocks = []
        list_dict_sci_news = []
        if len(dates) != len(headers):
            raise Exception("Ошибка получения информации от Naked Science.")
        for i in range(len(dates)):
            if i < 8:
                dict_sci_news = {}
                link_str = str(headers[i].find(
                    "div", class_="news-item-title"))
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
                # for img_block in imgs:

                str_to_print += ". " + \
                    link_str
                dict_sci_news['summary'] = headers[i].find(
                    "div", class_="news-item-excerpt").text.strip() if headers[i].find(
                    "div", class_="news-item-excerpt") != None else "Инфографика по ссылке."
                str_to_print += "\n" + \
                    dict_sci_news['summary'] + "\n"
                dict_sci_news['img'] = ""
                for img_ref in imgs_dict.keys():
                    if img_ref == dict_sci_news["url"] and i % 3 == 0:
                        dict_sci_news['img'] = imgs_dict[img_ref]
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
        i = 0
        for block in news_block:
            if i < 8:
                dict_business_news = {}
                dict_business_news['title'] = block.find(
                    "a", class_="block-title").text
                another_string = dict_business_news['title'] + "\n"
                dict_business_news['date'] = str(self.today_date)
                another_string += dict_business_news['date'] + ", "
                position_start = str(block).find('href="')
                text_link = "https://www.bfm.ru" + \
                    str(block)[position_start + 6:]
                position_end = text_link.find('"')
                text_link = text_link[:position_end]
                dict_business_news['url'] = text_link
                another_string += dict_business_news['url'] + "\n"
                dict_business_news['summary'] = block.find(
                    "a", class_="description").text
                if dict_business_news['summary'][-1] != '.' or dict_business_news['summary'][-1] != '?' or dict_business_news['summary'][-1] != '!':
                    dict_business_news['summary'] += '.'
                another_string += dict_business_news['summary']
                another_string += "\n"
                news_list.append(another_string)
                img_block = str(block.find("img"))
                img_block = img_block[img_block.find("src=")+5:]
                img_block = img_block[:img_block.find('"')]
                if img_block.find("extralarge") != -1:
                    img_block = ""
                dict_business_news['img'] = img_block
                list_dict_business_news.append(dict_business_news)
            i += 1
        news_output = "\n\nГлавные новости - Россия и мир:\n\n" + \
            "--------\n".join(news_list)
        return news_output, list_dict_business_news

    def get_history(self):
        url = "https://www.calend.ru/events/"
        bn = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"})
        bn.raise_for_status()
        soup = BeautifulSoup(bn.text, "html.parser")
        histories = soup.find_all("li", class_="three-three")
        list_dict_histories = []
        histories_list = []
        i = 0
        for block in histories:
            if i < 8:
                dict_business_news = {}
                dict_business_news['title'] = block.find(
                    "span", class_="title").text
                another_string = dict_business_news['title'] + "\n"
                dict_business_news['date'] = block.find(
                    "span", class_="year").text + str(self.today_date)[4:]
                dict_business_news['title'] = dict_business_news['date'] + \
                    ": " + dict_business_news['title']
                another_string += dict_business_news['date'] + ", "
                position_start = str(block).find('href="')
                text_link = str(block)[position_start + 6:]
                position_end = text_link.find('"')
                text_link = text_link[:position_end]
                dict_business_news['url'] = text_link
                another_string += dict_business_news['url'] + "\n"
                formated_list = str(block.find(
                    "p", class_="descr descrFixed").text).split('.')
                dict_business_news['summary'] = '.'.join(
                    formated_list[:-4]) + '.'
                another_string += dict_business_news['summary']
                another_string += "\n"
                histories_list.append(another_string)
                if i % 3 == 0:
                    start_point = str(block).find("url('")
                    img_block = str(block)[start_point+5:]
                    end_point = str(img_block).find("'")
                    img_block = img_block[:end_point]
                    dict_business_news['img'] = img_block
                else:
                    dict_business_news["img"] = ""
                list_dict_histories.append(dict_business_news)
            i += 1
        return histories_list, list_dict_histories

    def get_prog_news(self):
        url = "https://tproger.ru/news"
        bn = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"})
        bn.raise_for_status()
        soup = BeautifulSoup(bn.text, "html.parser")
        news_all = soup.find_all("a", class_="tp-new-design-post-card__title")
        list_dict_progs = []
        progs_list = []
        i = 0
        for block in news_all:
            if i < 8:
                dict_prog_news = {}
                dict_prog_news['title'] = block.text
                another_string = dict_prog_news['title'] + "\n"
                position_start = str(block).find('href="')
                text_link = str(block)[position_start + 6:]
                position_end = text_link.find('"')
                text_link = "https://tproger.ru" + text_link[:position_end]
                dict_prog_news['url'] = text_link
                another_string += text_link
                progs_list.append(another_string)
                list_dict_progs.append(dict_prog_news)
            i += 1
        return progs_list, list_dict_progs


def prepare_report():
    report = Morning_report()
    text_greetings = report.get_greetings()
    currency = report.get_currency()
    horoscope = report.get_horoscope()
    text_horoscope = "\nГороскоп: " + str(horoscope['Весы'])
    weather, icon_file = report.get_weather()
    text_weather = weather
    text_news_business, society_news = report.get_business_news()
    text_news_sci, science_news = report.get_sci_news()
    society_img = society_news[0]['img']
    text_histories, histories = report.get_history()
    text_progs, progs = report.get_prog_news()
    time_stamp = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    print(time_stamp + ": parsed")
    context = {
        "greetings": text_greetings,
        "weather_icon": icon_file,
        "weather": weather,
        "currency": currency,
        "horoscope": horoscope,
        "society_news": society_news,
        "science_news": science_news,
        "histories": histories,
        "progs": progs
    }
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    html_string = template.render(context)
    Path("output").mkdir(exist_ok=True)
    HTML(string=html_string, base_url='.').write_pdf(
        "output/Morning_Coffee_" + str(report.today_date) + ".pdf",
        stylesheets=[CSS('style.css')]
    )
    time_stamp = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    print(time_stamp + ": output/Morning_Coffee_" +
          str(report.today_date) + ".pdf")


def main():
    mail_check_interval_base = 120
    new_report_cycle = 30
    cycle = 0
    while (True):
        time_now = datetime.now().hour
        if time_now < 6 or time_now > 23:
            mail_check_interval_base = 300
            new_report_cycle = 36
        elif time_now >= 6 and time_now < 10:
            mail_check_interval_base = 120
            new_report_cycle = 15
        else:
            mail_check_interval_base = 150
            new_report_cycle = 30
        mail_check_interval = mail_check_interval_base + randint(0, 20)

        if cycle > new_report_cycle:
            cycle = 0
        if cycle == 0:
            try:
                prepare_report()
            except Exception as e:
                print(f"Возникла ошибка при подготовке файла: {e}")
        try:
            emails.check_mail()
            time_stamp = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            print(time_stamp + ": mail checked")

        except Exception as e:
            print(f"Возникла ошибка при проверке почты: {e}")
        cycle += 1
        time.sleep(mail_check_interval)


if __name__ == '__main__':
    # prepare_report()
    main()
