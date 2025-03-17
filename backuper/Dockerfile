FROM amazon/aws-cli:2.13.7

# Устанавливаем PostgreSQL-клиент на Amazon Linux 2
RUN yum install -y postgresql16 && \
    yum clean all

WORKDIR /app

COPY backup.sh /app/backup.sh
RUN chmod +x /app/backup.sh

CMD ["sh /app/backup.sh"]
