from JumpScale import j
import smtplib
from email.mime.text import MIMEText

class EmailClient(object):
    def __init__(self):
        self._server = j.application.config.get('mail.relay.addr')
        self._port = j.application.config.get('mail.relay.port')
        self._username = None
        self._password = None
        self._ssl = False
        if j.application.config.exists('mail.relay.username'):
            self._username = j.application.config.get('mail.relay.username')
        if j.application.config.exists('mail.relay.passwd'):
            self._password = j.application.config.get('mail.relay.passwd')
        if j.application.config.exists('mail.relay.ssl'):
            self._ssl = j.application.config.getBool('mail.relay.ssl')

    def send(self, recipients, sender, subject, message, files=None):
        """
        """
        # TODO handle files
        server = smtplib.SMTP(self._server, self._port) 
        server.ehlo()
        if self._ssl:
            server.starttls()
        if self._username:
            server.login(self._username, self._password)

        msg = MIMEText(message, 'html')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ','.join(recipients)
        server.sendmail(sender, recipients, msg.as_string())
        server.close()
