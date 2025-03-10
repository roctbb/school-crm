FROM node:18-alpine AS build

# Создадим рабочую директорию в контейнере
WORKDIR /app

# Скопируем package*.json и установим зависимости
COPY package*.json .
RUN npm install

# Скопируем весь проект и соберём
COPY . .

ENV VITE_API_BASE_URL=/api
ENV NODE_ENV=production

RUN npm run build