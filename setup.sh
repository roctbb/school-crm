#!/bin/bash

# Имя файла, куда будет записан SECRET_KEY
ENV_FILE=".env"

# Функция для генерации случайного ключа (использует Python)
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(50))"
}

# Проверяем, существует ли файл .env
if [ ! -f "$ENV_FILE" ]; then
    echo "Файл $ENV_FILE не существует. Создаём..."
    touch "$ENV_FILE"
fi

# Проверяем, есть ли уже переменная SECRET_KEY в .env
if grep -q "SECRET_KEY=" "$ENV_FILE"; then
    echo "SECRET_KEY уже существует в $ENV_FILE. Пропускаем генерацию."
else
    # Генерируем новый SECRET_KEY
    SECRET_KEY=$(generate_secret_key)
    echo "SECRET_KEY=$SECRET_KEY" >> "$ENV_FILE"
    echo "Секретный ключ добавлен в $ENV_FILE"
fi