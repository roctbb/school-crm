import subprocess

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

        ping_command = ["ping", "-c", "3", "postbox.cloud.yandex.net"]
        result = subprocess.run(ping_command, capture_output=True, text=True)
        print("Ping result:")
        print(result.stdout)

        mail.send(msg)
