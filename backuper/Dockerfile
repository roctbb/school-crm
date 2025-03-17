FROM amazon/aws-cli:2.13.7

# Устанавливаем необходимые пакеты и репозиторий PostgreSQL 16
RUN yum -y update && \
 yum -y install \
     https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-all.repo && \
 # Отключаем встроенный модуль PostgreSQL (если требуется)
 yum -y module disable postgresql || true && \
 yum -y install postgresql16 && \
 yum clean all

WORKDIR /app

COPY backup.sh /app/backup.sh
RUN chmod +x /app/backup.sh

CMD ["sh", "/app/backup.sh"]