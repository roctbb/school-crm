from flask import current_app
from application.infrastructure import mail, celery
from flask_mail import Message

@celery.task
def send_flask_mail(recipient_email, subject, html):
    with current_app.app_context():
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=html
        )

        print(mail.mail.server, mail.mail.port)

        mail.send(msg)
