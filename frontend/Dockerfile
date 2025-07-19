# --- Этап 1: Сборка приложения ---
FROM node:21.7.1-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . ./
RUN npm run build

# --- Этап 2: Создание финального образа --- 
FROM nginx:1.29-alpine

# Копируем кастомный конфиг для Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем готовые файлы из сборщика в директорию веб-сервера Nginx
COPY --from=builder /app/build /usr/share/nginx/html
