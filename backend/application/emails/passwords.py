from application.helpers import url
from application.tasks.mail import send_flask_mail


def send_password_reset_email(user):
    email = user.email
    subject = "Восстановление пароля в Силаэдр CRM"
    token = user.reset_token
    reset_link = url("/password/reset?token=" + token)

    # HTML-версия письма
    html_body = f"""
    <html>
      <body>
        <p>Здравствуйте!</p>
        <p>Вы запросили восстановление пароля в Силаэдр CRM. 
           Нажмите на ссылку, чтобы создать новый пароль:</p>
        <p>
          <a href="{reset_link}" 
             style="background-color: #0b5ed7; color: #ffffff; padding: 10px 20px; 
                    text-decoration: none; border-radius: 4px; margin-top: 10px; margin-bottom: 10px;">
            Сбросить пароль
          </a>
        </p>
        <p>Если вы не делали такой запрос, просто проигнорируйте это письмо.</p>
        <p>С уважением,<br/>
        Команда Силаэдр CRM</p>
      </body>
    </html>
    """

    # Предположим, что в send_flask_mail можно передать и текст, и HTML:
    send_flask_mail.delay(email, subject, html_body)
