#!/usr/bin/env bash
set -e

echo "Начинаем резервное копирование..."

# Делаем дамп базы (замените db, postgres и т.п. при необходимости)
pg_dump -h db -U postgres -d postgres > /tmp/db_backup.sql
echo "Дамп базы выполнен."

# Загружаем дамп в S3 (переменные окружения заранее должны быть заданы)
aws s3 cp /tmp/db_backup.sql s3://${S3_BUCKET_NAME}/db_backup_$(date +%Y%m%d_%H%M%S).sql --endpoint-url "${S3_ENDPOINT_URL}"
echo "Дамп базы загружен в S3."

# Синхронизируем файлы из нужной папки с S3
aws s3 sync /data_to_backup s3://${S3_BUCKET_NAME}/backend_storage --endpoint-url "${S3_ENDPOINT_URL}"
echo "Файлы синхронизированы."

echo "Резервное копирование завершено."