from flask import current_app
from application.infrastructure import mail, celery
from flask_mail import Message

@celery.task
def send_flask_mail(recipient_email, subject, html):
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=html
        )
        print(current_app.extensions["mail"].server)

        mail.send(msg)
