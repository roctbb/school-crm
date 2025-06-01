from flask import current_app
from application.infrastructure import mail, celery
from flask_mail import Message

@celery.task
def send_flask_mail(recipient_email, subject, html):
        print(mail.init_app(current_app))
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=html
        )
        print(mail.state.server, mail.state.port, mail.state.use_tls)

        mail.send(msg)
