#!/usr/bin/env python3

import imaplib
import smtplib
import os
import email
from email.header import decode_header
from email.utils import parseaddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from datetime import datetime
import time
from email.header import Header


def decode_mime_words(s):
    decoded_subject = ""
    for content, charset in decode_header(s):
        if isinstance(content, bytes):
            decoded_subject += content.decode(charset or 'utf-8',
                                              errors='ignore')
        else:
            decoded_subject += content
    return decoded_subject


def folders_list():
    EMAIL_ACCOUNT = ""
    APP_PASSWORD = ""
    with open("keys.txt", "r") as keys:
        lines = keys.readlines()
    EMAIL_ACCOUNT = str(lines[0])
    APP_PASSWORD = str(lines[1])
    EMAIL_ACCOUNT = EMAIL_ACCOUNT.strip('\n')
    APP_PASSWORD = APP_PASSWORD.strip('\n')
    IMAP_SERVER = "imap.yandex.ru"
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
    status, folders = mail.list()
    if status == 'OK':
        for folder in folders:
            print(folder)
    mail.logout()


def check_mail():
    EMAIL_ACCOUNT = ""
    APP_PASSWORD = ""
    MAX_RETRIES = 10
    TIMEOUT_SECONDS = 5
    with open("keys.txt", "r") as keys:
        lines = keys.readlines()
        EMAIL_ACCOUNT = str(lines[0])
        APP_PASSWORD = str(lines[1])
        EMAIL_ACCOUNT = EMAIL_ACCOUNT.strip('\n')
        APP_PASSWORD = APP_PASSWORD.strip('\n')
        IMAP_SERVER = "imap.yandex.ru"
        SMTP_SERVER = "smtp.yandex.ru"
        SEARCH_STRING = "газет"

        OUTPUT_DIR = Path("output")
        if not OUTPUT_DIR.exists() or not OUTPUT_DIR.is_dir():
            print(f"Ошибка: Папка '{OUTPUT_DIR}' не найдена!")
            return
        pdf_files = sorted(OUTPUT_DIR.glob("*.pdf"), reverse=True)
        if not pdf_files:
            print(f"Ошибка: В папке '{OUTPUT_DIR}' нет PDF-файлов!")
            return
        latest_file = pdf_files[0]
        FILE_PATH = str(latest_file)
        folders_to_search = ["inbox", "Spam"]
    if not os.path.isfile(FILE_PATH):
        print(f"Ошибка: Файл {FILE_PATH} не найден!")
        return
    recipients_to_notify = set()
    try:
        connection = False
        for attempt in range(0, MAX_RETRIES):
            try:
                mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=TIMEOUT_SECONDS)
                mail.sock.settimeout(TIMEOUT_SECONDS)
                connection = True
                break
            except Exception as e:
                with open("papers_sent_logs.txt", "a") as logs:
                    logs.write(datetime.now().strftime(
                        "%Y-%m-%d_%H-%M-%S") + " IMAP connection error, attempt: " + str(attempt) + "\n")
                print(datetime.now().strftime(
                    "%Y-%m-%d_%H-%M-%S") + " IMAP connection error, attempt: " + str(attempt) + "\n")
                time.sleep(3)
        if not connection:
            raise Exception("Failed to connect.")
        mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
        for folder in folders_to_search:
            status, _ = mail.select(str(folder))
            if status != 'OK':
                print(f"Папка {folder} недоступна, пропускаем")
                continue
            status, messages = mail.search(None, 'UNSEEN')
            if status != 'OK':
                print("Не удалось получить список писем.")
                return
            for num in messages[0].split():
                status, data = mail.fetch(num, '(RFC822.HEADER)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                subject_raw = msg.get('Subject', '')
                subject = decode_mime_words(subject_raw)
                if SEARCH_STRING.lower() in subject.lower():
                    from_raw = msg.get('From', '')
                    sender_name, sender_email = parseaddr(from_raw)
                    if sender_email:
                        recipients_to_notify.add(sender_email)
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        with open("papers_received_logs.txt", "a", encoding="utf-8") as logs:
                            logs.write(
                                f"{timestamp} received from: {sender_email}\n")
                mail.store(num, '+FLAGS', '\\Seen')
        mail.logout()
    except Exception as e:
        print(f"Ошибка при работе с IMAP: {e}")
        return

    if not recipients_to_notify:
        return

    try:
        connection = False
        for attempt in range(MAX_RETRIES):
            try:
                server = smtplib.SMTP_SSL(
                    SMTP_SERVER, 465, timeout=TIMEOUT_SECONDS)
                server.sock.settimeout(TIMEOUT_SECONDS)
                connection = True
                break
            except Exception as e:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                msg_log = f"{timestamp} SMTP connection error, attempt: {attempt}\n"
                with open("papers_sent_logs.txt", "a", encoding="utf-8") as logs:
                    logs.write(msg_log)
                print(msg_log.strip())
                time.sleep(3)
        if not connection:
            raise Exception("Failed to connect.")
        server.login(EMAIL_ACCOUNT, APP_PASSWORD)
        with open(FILE_PATH, "rb") as f:
            file_data = f.read()
        for recipient in recipients_to_notify:
            try:
                msg = MIMEMultipart()
                msg['From'] = EMAIL_ACCOUNT
                msg['To'] = recipient
                msg['Subject'] = Header(
                    "Свежий выпуск Morning_Coffee по вашему запросу", "utf-8")
                body = "Добрый день!\n\nВо вложении находится запрошенный вами свежий выпуск интерактивной газеты Morning_Coffee.\n\nС уважением,\nРазработчик\nСтанислав Конов\n\n\np.s. Настоящее письмо не является рассылкой, оно формируется автоматически в ответ на запрос, \nнаправленный на public32@yandex.ru с указанием слова 'газета' в теме письма.\n\nДля обратной связи: public32@xmail.ru"
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
                part = MIMEApplication(
                    file_data, Name=os.path.basename(FILE_PATH))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(FILE_PATH)}"'
                msg.attach(part)
                server.sendmail(EMAIL_ACCOUNT, recipient, msg.as_string())
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                with open("papers_sent_logs.txt", "a", encoding="utf-8") as logs:
                    logs.write(f"{timestamp} sent to: {recipient}\n")
            except Exception as e:
                print(f"Не удалось отправить {recipient}: {e}")
                continue
        server.quit()
    except Exception as e:
        print(f"Ошибка при работе с SMTP: {e}")


if __name__ == "__main__":
    # folders_list()
    check_mail()
