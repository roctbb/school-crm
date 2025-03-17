FROM amazon/aws-cli:2.13.7

RUN yum update -y && \
    # Устанавливаем репозиторий PostgreSQL (версия может отличаться в зависимости от поддержки на вашей платформе)
    yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm && \
    # Отключаем модуль PostgreSQL от Amazon Linux,
    yum -y module disable postgresql && \
    # Устанавливаем PostgreSQL 16 клиент
    yum install -y postgresql16

WORKDIR /app

COPY backup.sh /app/backup.sh
RUN chmod +x /app/backup.sh

CMD ["sh", "/app/backup.sh"]