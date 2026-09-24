# ☕ Morning_Coffee (Online Newspaper)

An automated generator of a regular online newspaper in PDF format. The project scrapes up-to-date information from multiple sources, formats a beautifully typeset issue, and emails it upon request.

## 🎯 About the Project
**Morning_Coffee** is a server-side script that automatically parses data and generates PDF newspaper issues on an adaptive schedule:
- Every **30 minutes** in the morning (06:00 – 10:00);
- Every **1.5 hours** during the day (10:00 – 23:00);
- Every **3 hours** at night (23:00 – 06:00).

In parallel, the script checks the project's email inbox every 2–5 minutes. If it finds an unread email with the word **«газет»** (Russian for "newspaper") or its derivatives in the subject line (case-insensitive), it automatically replies to the sender with the latest PDF issue attached.

## 📰 Issue Contents
Each PDF file contains structured and well-formatted information:
- A greeting with the current date and day of the week;
- Daily weather forecast (with icon and moon phase);
- Daily horoscope for all zodiac signs;
- Current currency exchange rates (USD, EUR, CNY);
- Society and politics news (up to 8 items);
- Science and technology news (up to 8 items);
- "This day in history" events (up to 8 facts);
- Fresh news and trends directly from the IT development sphere.

## 🌐 Data Sources
Information is collected and processed from the following 7 resources:
1. **Central Bank of Russia (CBR)** — currency exchange rates;
2. **Foreca.com** — weather forecast;
3. **Europa Plus Russia (Radio API)** — daily horoscope;
4. **Business FM Russia (Radio)** — society and politics news;
5. **Naked-science.ru** — science and technology;
6. **Calend.ru** — this day in history;
7. **Tproger.ru** — IT development news.

## 🚀 How to Run
### Requirements
- Python 3.11 or newer.
- System dependencies for `WeasyPrint` (Pango, Cairo, GDK-PixBuf, etc.).
- A `keys.txt` file in the project root, containing the email account on the first line and the app password on the second line (each line without extra spaces).

### Installing Dependencies
Create a `requirements.txt` file with the following content and install the packages:
```text
requests
beautifulsoup4
jinja2
weasyprint
```
```bash
pip install -r requirements.txt
```

### Instructions
* Clone the repository or download the project files.
* Ensure the keys.txt file is created and populated with correct credentials.
* Run the main script: python3 main.py

### How to get an issue
Simply send an email to public32@yandex.ru with the word «газет» (or its derivatives like "газета", "газеты") in the subject line. You will automatically receive the latest PDF issue in reply.

## 📁 Project Structure
.
├── main.py                 # Main file: data parsing, PDF generation, and main loop
├── emails.py               # Helper module: email checking (IMAP) and sending replies (SMTP)
├── template.html           # Jinja2 HTML template for newspaper layout
├── style.css               # CSS styles for the PDF document
├── output/                 # Folder for saving generated PDF issues
├── keys.txt                # Credentials file (Email and app password, line by line)
├── requirements.txt        # Project dependencies
├── README.md               # Project description in English
├── README(RUS).md          # Project description in Russian
└── LICENSE                 # License with mandatory author attribution clause

## ✒️ Author and License
The code is entirely written by Stanislav Konov (GitHub: Stan-public32).
The project is distributed as OpenSource, but with a mandatory condition: when using, modifying, or distributing this code, you must credit the original author (Stan-public32) and include a link to their GitHub profile. Details are specified in the LICENSE file.
