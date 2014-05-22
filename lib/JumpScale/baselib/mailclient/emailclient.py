from JumpScale import j
import smtplib
import mimetypes
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailClient(object):
    def __init__(self):
        self._server = j.application.config.get('mail.relay.addr')
        self._port = j.application.config.getInt('mail.relay.port')
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
        if isinstance(recipients, basestring):
            recipients = [ recipients ]
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

        if files:
            txtmsg = msg
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = ','.join(recipients)
            msg.attach(txtmsg)
            for fl in files:
                # Guess the content type based on the file's extension.  Encoding
                # will be ignored, although we should check for simple things like
                # gzip'd or compressed files.
                filename = j.system.fs.getBaseName(fl)
                ctype, encoding = mimetypes.guess_type(fl)
                content = j.system.fs.fileGetContents(fl)
                if ctype is None or encoding is not None:
                    # No guess could be made, or the file is encoded (compressed), so
                    # use a generic bag-of-bits type.
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                if maintype == 'text':
                    attachement = MIMEText(content, _subtype=subtype)
                elif maintype == 'image':
                    attachement = MIMEImage(content, _subtype=subtype)
                elif maintype == 'audio':
                    attachement = MIMEAudio(content, _subtype=subtype)
                else:
                    attachement = MIMEBase(maintype, subtype)
                    attachement.set_payload(content)
                    # Encode the payload using Base64
                    encoders.encode_base64(attachement)
                # Set the filename parameter
                attachement.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(attachement)
        server.sendmail(sender, recipients, msg.as_string())
        server.close()
