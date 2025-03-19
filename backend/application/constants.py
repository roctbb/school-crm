import os

ROLES = ['student', 'teacher', 'admin']
OBJECT_TYPES = ['student', 'project', 'event']
# Папка, куда будем сохранять загруженные файлы
UPLOAD_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'storage')
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Разрешённые форматы (пример)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}
