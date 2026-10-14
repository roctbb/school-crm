"""Flask-Mail connections with bounded network operations."""
import smtplib

from flask import current_app
from flask_mail import Connection, Mail


class TimeoutConnection(Connection):
    def configure_host(self):
        constructor = smtplib.SMTP_SSL if self.mail.use_ssl else smtplib.SMTP
        host = constructor(
            self.mail.server, self.mail.port,
            timeout=current_app.config['MAIL_TIMEOUT'],
        )
        try:
            host.set_debuglevel(int(self.mail.debug))
            if self.mail.use_tls:
                host.starttls()
            if self.mail.username and self.mail.password:
                host.login(self.mail.username, self.mail.password)
        except BaseException:
            host.close()
            raise
        return host

    def __exit__(self, exc_type, exc_value, tb):
        if self.host is not None:
            # SMTP DATA has already completed (or raised). Waiting for QUIT can
            # turn an accepted message into an apparent failure and a duplicate.
            self.host.close()


class TimeoutMail(Mail):
    def connect(self):
        app = getattr(self, 'app', None) or current_app
        return TimeoutConnection(app.extensions['mail'])
