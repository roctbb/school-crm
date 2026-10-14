import subprocess

from flask import current_app
from application.infrastructure import mail, celery
from flask_mail import Message

@celery.task(soft_time_limit=120, time_limit=150)
def send_flask_mail(recipient_email, subject, html):
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=html
        )

        mail.send(msg)
