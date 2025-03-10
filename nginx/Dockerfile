FROM nginx:stable-alpine

# Удалим дефолтный конфиг из /etc/nginx/conf.d
RUN rm /etc/nginx/conf.d/default.conf

# Копируем конфигурационный файл NGINX
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Запускаем NGINX
CMD ["nginx", "-g", "daemon off;"]