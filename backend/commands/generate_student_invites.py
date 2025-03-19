import secrets

from application import create_app
from application.methods import create_invitations_for
app, _ = create_app()

with app.app_context():

    # Собираем ID всех объектов, у которых уже есть приглашение с ролью "student"
    print(f"Создано {len(create_invitations_for('students', 'student'))} новых приглашений для студентов.")
