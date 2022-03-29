import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ad_from = "POST@gmail.com"  # почта с которой отправляем (нужно включить возможно авторизации таким способом иначе не прокатит)
ad_to = "POST"  # почта на каоторую отправляем
password = "PASSWORD"  # пароль от почты
# создание наполнения письма
msg = MIMEMultipart()
msg['From'] = ad_from
msg['To'] = ad_to
msg['Subject'] = 'Тема'
body = 'Текст письма'
msg.attach(MIMEText(body, 'plain'))
# подключение к серверу, авторизация, отправка письма
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(ad_from, password)
server.send_message(msg)
server.quit()
