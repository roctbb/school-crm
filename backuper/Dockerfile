FROM amazon/aws-cli:2.13.7

# Устанавливаем PostgreSQL-клиент для Alpine Linux
RUN apk add --no-cache postgresql-client

WORKDIR /app

COPY backup.sh /app/backup.sh
RUN chmod +x /app/backup.sh

CMD ["/app/backup.sh"]
