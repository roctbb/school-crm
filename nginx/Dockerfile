FROM nginx:stable-alpine

# Удалим дефолтный конфиг из /etc/nginx/conf.d
RUN rm /etc/nginx/conf.d/default.conf

# Копируем наш шаблон
COPY nginx.conf /etc/nginx/templates/nginx.conf.template

# Установим утилиту envsubst (если её нет в базовом образе)
RUN apk add --no-cache gettext

# Установим переменную окружения по умолчанию, если нужно
ENV NGINX_PORT=80

# Запускаем Nginx, предварительно подставляя переменные
CMD ["/bin/sh", "-c", "envsubst '$NGINX_PORT' < /etc/nginx/templates/nginx.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]