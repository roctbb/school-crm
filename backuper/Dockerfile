FROM amazon/aws-cli:2.13.7

# Устанавливаем PostgreSQL-клиент, чтобы использовать pg_dump
RUN apt-get update \
    && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Папка, в которой будет лежать скрипт
WORKDIR /app

# Копируем скрипт в контейнер
COPY backup.sh /app/backup.sh

# Делаем скрипт исполняемым
RUN chmod +x /app/backup.sh

# По умолчанию запускаем скрипт
CMD ["/app/backup.sh"]