FROM ubuntu:latest

# Обновление списка пакетов и установка postgresql-client (для pg_dump) и awscli
RUN apt-get update && \
    apt-get install -y postgresql-client awscli && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование скрипта резервного копирования и выдача прав на выполнение
COPY backup.sh /app/backup.sh
RUN chmod +x /app/backup.sh

# Запуск скрипта при старте контейнера
CMD ["sh", "/app/backup.sh"]