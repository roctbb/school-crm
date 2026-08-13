# 1. Этап сборки (build stage)
FROM node:18-alpine AS build

# Создадим рабочую директорию
WORKDIR /app

# Скопируем package*.json, установим зависимости
COPY package*.json .
RUN npm install

# Скопируем всё остальное и соберём проект
COPY . .
ARG VITE_APP_NAME
ENV VITE_API_BASE_URL=/api
ENV VITE_APP_NAME=${VITE_APP_NAME}
ENV NODE_ENV=production
RUN npm run build

# 2. Этап запуска (release stage)
FROM nginx:alpine

# Скопируем собственный конфиг Nginx (если у вас есть такой)
# Предположим, что ваш конфиг лежит в корне проекта и называется nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем собранные файлы из первого этапа
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
