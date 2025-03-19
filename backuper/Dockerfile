FROM ubuntu:latest

# Обновление списка пакетов и установка postgresql-client (для pg_dump) и awscli


RUN apt-get update -y && \
    apt-get install -y curl unzip gnupg

RUN apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Установка AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

WORKDIR /app

# Копирование скрипта резервного копирования и выдача прав на выполнение
COPY backup.sh /app/backup.sh
RUN chmod +x /app/backup.sh

# Запуск скрипта при старте контейнера
CMD ["sh", "/app/backup.sh"]