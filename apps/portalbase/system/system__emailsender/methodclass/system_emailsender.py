from system_emailsender_osis import system_emailsender_osis
import smtplib
from JumpScale import j
from email.mime.text import MIMEText

ujson = j.db.serializers.getSerializerType('j')


class system_emailsender(system_emailsender_osis):

    """
    Email sender
    """
    # Maybe we can add this later
    output_format_mapping = {
        'json': ujson.dumps
    }

    def __init__(self):
        self._te = {}
        self.actorname = "emailsender"
        self.appname = "system"
        self.server = 'msp.aserver.com:25'
        system_emailsender_osis.__init__(self)

    def format(self, obj, format=None):
        if not format or format not in self.output_format_mapping:
            format = 'json'
        output_formatter = self.output_format_mapping[format]
        return output_formatter(obj)

    def send(self, sender_name, sender_email, receiver_email, subject, body, format, *args, **kwargs):
        """
        param:sender_name The name of the sender
        param:sender_email The email of the sender
        param:receiver_email The email of the receiver
        param:subject Email subject
        param:body Email body
        param:format The request & response format of the HTTP request itself
        result 'Success' in case of success, or 'Failure: ERROR_MSG' in case of the error message.
        """

        # The idea behind honeypots is simple. Most spamming bots are stupid & fill all the form fields, so if I put
        # an invisible field in the form it will be filled by the bot, but not by humans.
        #
        # For better protection, I can encode the names & IDs of the fields here, but this should be done at a later
        # time
        honeypot = kwargs.pop('honeypot', None)
        if honeypot:
            return 'Error: SPAMMER'

        kwargs.pop('ctx', None)

        if sender_name:
            sender = '{0} <{1}>'.format(sender_name, sender_email)
        else:
            sender = sender_email

        # This is the same email pattern used in `contact_form` macro
        # TODO: abstract it in one place
        email_pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"
        if not j.codetools.regex.match(email_pattern, receiver_email):
            return 'Error: receiver email is not formatted well.'
        if not j.codetools.regex.match(email_pattern, sender_email):
            return 'Error: your email is not formatted well.'

        receivers = [receiver_email]

        if kwargs:
            other_params = []
            for k, v in kwargs.items():
                if isinstance(v, list):
                    v = ', '.join(v)
                other_params.append('<tr><th>{0}</th><td>{1}</td></tr>'.format(k, v))

            body = body + '<br /><table border=1>{0}</table>'.format(''.join(other_params))

        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ','.join(receivers)

        smtp = None
        try:
            smtp = smtplib.SMTP(self.server, timeout=5)
            smtp.sendmail(sender, receivers, msg.as_string())
        finally:
            if smtp:
                smtp.quit()

        return 'Success'
