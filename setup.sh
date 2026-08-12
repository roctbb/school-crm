#!/bin/bash

# Имя файла, куда будет записан SECRET_KEY
ENV_FILE=".env"

# Функция для генерации случайного ключа (использует Python)
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(50))"
}

# Создаём рабочий файл из шаблона, если его ещё нет.
if [ ! -f "$ENV_FILE" ]; then
    echo "Файл $ENV_FILE не существует. Создаём из .env.example..."
    cp .env.example "$ENV_FILE"
fi

# Проверяем, задан ли уже непустой SECRET_KEY в .env.
if grep -Eq '^SECRET_KEY=.+$' "$ENV_FILE"; then
    echo "SECRET_KEY уже существует в $ENV_FILE. Пропускаем генерацию."
else
    # Генерируем новый SECRET_KEY
    SECRET_KEY=$(generate_secret_key)
    if grep -q '^SECRET_KEY=' "$ENV_FILE"; then
        TEMP_ENV_FILE=$(mktemp)
        awk -v secret="$SECRET_KEY" '
            /^SECRET_KEY=/ && !replaced { print "SECRET_KEY=" secret; replaced=1; next }
            { print }
        ' "$ENV_FILE" > "$TEMP_ENV_FILE"
        mv "$TEMP_ENV_FILE" "$ENV_FILE"
    else
        echo "SECRET_KEY=$SECRET_KEY" >> "$ENV_FILE"
    fi
    echo "Секретный ключ добавлен в $ENV_FILE"
fi
