FROM amazon/aws-cli:2.13.7

RUN yum update -y && yum install -y postgresql

WORKDIR /app

COPY backup.sh /app/backup.sh
RUN chmod +x /app/backup.sh

CMD ["sh", "/app/backup.sh"]