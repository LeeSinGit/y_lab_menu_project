import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from api.config.config import SMTP_PASSWORD, SMTP_PORT, SMTP_SERVER, SMTP_USER


def send_email(subject, message, to_email):
    smtp_server = SMTP_SERVER
    smtp_port = SMTP_PORT
    smtp_username = SMTP_USER
    smtp_password = SMTP_PASSWORD

    # Создаем объект MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject

    # Добавляем текст сообщения
    msg.attach(MIMEText(message, 'plain'))

    # Подключение к SMTP-серверу
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    # Отправка письма
    server.sendmail(smtp_username, to_email, msg.as_string())
    server.quit()
