FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y iputils-ping

# Копируем требования
COPY requirements.txt .

# Устанавливаем зависимости вместе с Gunicorn
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Копируем исходный код приложения
COPY . /app

# Открываем порт 5000 (для Gunicorn)
EXPOSE 5000

# Запускаем приложение через Gunicorn
CMD ["/bin/sh", "-c", "flask db upgrade && gunicorn -b 0.0.0.0:5000 wsgi:app"]
