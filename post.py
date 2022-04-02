import smtplib
from email.message import EmailMessage


def mail(msg, to, topic='No temes'):
    email_server = "smtp.yandex.ru"
    sender = "moonadiary@yandex.ru"
    em = EmailMessage()
    em.set_content(msg)
    em['To'] = to
    em['From'] = sender
    em['Subject'] = topic
    mailServer = smtplib.SMTP(email_server)
    mailServer.set_debuglevel(1)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login('moonadiary', 'fiX-2Vb-6a2-kCi')
    mailServer.ehlo()
    mailServer.send_message(em)
    mailServer.quit()
