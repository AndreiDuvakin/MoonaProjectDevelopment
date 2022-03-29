import smtplib


def mail(msg, to, topic='No temes'):
    email_server = "smtp.yandex.ru"
    sender = "moonadiary@yandex.ru"
    headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, to, topic)
    text = msg
    message = headers + text
    mailServer = smtplib.SMTP(email_server)
    mailServer.set_debuglevel(1)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login('moonadiary', 'fiX-2Vb-6a2-kCi')
    mailServer.ehlo()
    mailServer.sendmail(sender, to, message)
    mailServer.quit()
