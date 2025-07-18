
[![Main Foodgram workflow](https://github.com/MrFR0D0/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/MrFR0D0/foodgram/actions/workflows/main.yml)

# Проект Foodgram: Платформа для ваших рецептов

**Foodgram** — это полноценный веб-сервис, который позволяет пользователям публиковать свои кулинарные рецепты, подписываться на других авторов, добавлять рецепты в избранное и формировать список покупок на основе выбранных блюд.

> **Примечание:**
> Если вы не хотите разворачивать проект локально, вы можете ознакомиться с его статической версией, размещенной на GitHub Pages:
> 
> **[Посмотреть статическую версию Foodgram](https://mrfr0d0.github.io/foodgram/)**

---

## 🚀 Ключевые возможности

- **Создание и публикация рецептов:** Удобный интерфейс для добавления рецептов с ингредиентами, тегами и временем приготовления.
- **Подписки:** Следите за любимыми авторами и получайте их новые рецепты в своей ленте.
- **Список покупок:** Автоматически формируйте список необходимых продуктов для приготовления одного или нескольких блюд. Список можно скачать в формате `.txt`.
- **Избранное:** Сохраняйте понравившиеся рецепты, чтобы они всегда были под рукой.
- **Продвинутая фильтрация:** Ищите рецепты по автору, тегам и другим параметрам.

---

## 🛠️ Технологии

| Категория | Технология |
|---|---|
| **Бэкенд** | Python, Django, Django REST Framework, Gunicorn |
| **Фронтенд** | JavaScript, React |
| **База данных** | PostgreSQL |
| **Инфраструктура** | Docker, Docker Compose, Nginx |
| **CI/CD** | GitHub Actions |

---

## 🏛️ Архитектура проекта

```mermaid
graph TD
    user["User<br>External Actor"]

    subgraph proxy ["Reverse Proxy<br>Nginx"]
        nginx_config["Nginx Configuration<br>Nginx"]
    end

    subgraph frontend ["Frontend Application<br>React.js"]
        main_app["Main Application<br>React.js"]
        api_client["API Client<br>JavaScript"]
        ui_components["UI Components<br>React.js"]
        app_pages["Application Pages<br>React.js"]
        context_providers["Context Providers<br>React.js"]
        frontend_utils["Frontend Utilities<br>JavaScript"]

        main_app -->|sends API requests via| api_client
        main_app -->|uses| ui_components
        main_app -->|navigates to| app_pages
        main_app -->|provides context via| context_providers
        main_app -->|utilizes| frontend_utils
    end

    subgraph backend ["Backend API<br>Django, Python"]
        django_core["Django Core<br>Python"]
        api_views["API Views<br>Django REST Framework"]
        api_serializers["API Serializers<br>Django REST Framework"]
        db_models["Database Models<br>Django ORM"]
        data_commands["Data Management Commands<br>Django"]
        api_utils["API Utilities<br>Python"]

        django_core -->|defines routes for| api_views
        api_views -->|serializes/deserializes data with| api_serializers
        api_views -->|queries/updates| db_models
        api_views -->|applies logic from| api_utils
        data_commands -->|modifies| db_models
    end

    subgraph db ["Database<br>PostgreSQL"]
        postgres["PostgreSQL Database<br>SQL"]
    end

    user -->|accesses| proxy
    proxy -->|serves| frontend
    proxy -->|proxies API to| backend
    frontend -->|makes API calls to| backend
    backend -->|reads/writes data from| db
    db -->|stores data for| backend
```

---

## ⚙️ Локальная разработка

Эти шаги помогут вам запустить проект на вашем локальном компьютере для разработки и тестирования.

### 1. Клонирование проекта

```bash
git clone git@github.com:MrFR0D0/foodgram.git
cd foodgram
```

### 2. Создание файла `.env`

В корневой директории проекта создайте файл `.env` и заполните его по следующему шаблону. Для локального запуска достаточно указать `SECRET_KEY`.

```env
# Настройки Django
SECRET_KEY='ваш_секретный_ключ'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Настройки базы данных PostgreSQL
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
```

### 3. Запуск с помощью Docker Compose

Эта команда соберет все необходимые образы и запустит контейнеры для бэкенда, фронтенда, базы данных и веб-сервера.

```bash
docker-compose -f ./infra/docker-compose.yml -p foodgram up --build  
```

После успешного запуска проект будет доступен по адресу [http://localhost:8000/](http://localhost:8000/).

### 4. Запуск тестов

Для проверки корректной работы API вы можете запустить набор автоматических тестов. Убедитесь, что все контейнеры запущены, и выполните следующую команду:

```bash
docker-compose -f ./infra/docker-compose.yml -p foodgram exec -e PYTHONPATH=/app/src backend pytest
```

---

## 🚀 Автоматическое развертывание (CI/CD)

Процесс развертывания проекта на удаленном сервере полностью автоматизирован с помощью **GitHub Actions**. Воркфлоу активируется при каждом пуше в ветку `main`.

### Как это работает?

1.  **Тестирование:** Запускаются тесты с помощью `ruff`.
2.  **Сборка и публикация образов:** Проект собирает Docker-образы для бэкенда, фронтенда и Nginx-шлюза, после чего загружает их на Docker Hub.
3.  **Деплой на сервер:**
    -   GitHub Actions подключается к серверу по SSH.
    -   На сервер копируется файл `infra/docker-compose.production.yml`.
    -   Создается и копируется файл `.env` из секрета, хранящегося в GitHub.
    -   С помощью `docker-compose` останавливаются старые контейнеры, загружаются свежие образы из Docker Hub и запускается проект.
4.  **Уведомление:** После успешного развертывания отправляется сообщение в Telegram.

### Настройка для развертывания

Для автоматического развертывания вам необходимо настроить **Secrets** в вашем репозитории на GitHub. Перейдите в `Settings` > `Secrets and variables` > `Actions` и добавьте следующие секреты:

| Секрет | Описание | Пример |
|---|---|---|
| `DOCKER_USERNAME` | Ваш логин на Docker Hub. | `myusername` |
| `DOCKER_PASSWORD` | Пароль или токен доступа от Docker Hub. | `dckr_pat_...` |
| `HOST` | IP-адрес или домен вашего сервера. | `123.45.67.89` |
| `USER` | Имя пользователя для подключения по SSH. | `ubuntu` |
| `SSH_KEY` | Приватный SSH-ключ для доступа к серверу. | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SSH_PASSPHRASE` | (Опционально) Парольная фраза для вашего SSH-ключа. | `your_passphrase` |
| `DOT_ENV` | **Полное содержимое** вашего `.env` файла для продакшена. | `SECRET_KEY=...` `POSTGRES_PASSWORD=...` |
| `TELEGRAM_TO` | ID вашего чата или пользователя в Telegram. | `123456789` |
| `TELEGRAM_TOKEN` | Токен вашего Telegram-бота. | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |

После настройки этих секретов любой пуш в ветку `main` будет автоматически запускать процесс развертывания.

---

## 📚 API Документация

После запуска проекта документация API будет доступна по адресу:

- [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

---

## 👨‍💻 Автор

**Дмитрий Николаев**

- GitHub: [@MrFR0D0](https://github.com/MrFR0D0)
