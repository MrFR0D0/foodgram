# Преобразование Foodgram в статический сайт

Этот документ описывает ключевые доработки, которые были выполнены для преобразования динамического веб-приложения Foodgram (Django + React) в полностью статический сайт, размещенный на GitHub Pages.

## 1. Создание генератора данных

Для того чтобы сайт мог работать без бэкенда, был создан специальный скрипт, который извлекает все необходимые данные из базы данных и упаковывает их в один файл.

- **Файл:** `backend/src/recipes/management/commands/export_data.py`
- **Описание:** Скрипт собирает всех пользователей, рецепты, теги и ингредиенты. Изображения (аватары и картинки рецептов) кодируются в Base64 и встраиваются прямо в итоговый `data.json`.

```python
# backend/src/recipes/management/commands/export_data.py
# (Финальная версия)
import base64
import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class Command(BaseCommand):
    """Команда управления Django для экспорта данных в файл JSON."""

    help = "Экспорт данных в JSON"

    def handle(self, *args, **options):
        """Обработка выполнения команды."""
        self.stdout.write("Экспорт данных...")

        users = User.objects.all()
        recipes = Recipe.objects.all()
        tags = Tag.objects.all()
        ingredients = Ingredient.objects.all()

        data = {"users": [], "recipes": [], "tags": [], "ingredients": []}

        for user in users:
            avatar_data = None
            if user.avatar:
                try:
                    with open(user.avatar.path, "rb") as image_file:
                        avatar_data = (
                            f"data:image/png;base64,"
                            f"{base64.b64encode(image_file.read()).decode('utf-8')}"
                        )
                except FileNotFoundError:
                    self.stdout.write(self.style.WARNING(f'Avatar not found for user {user.id}'))

            data["users"].append(
                {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "avatar": avatar_data,
                }
            )

        for tag in tags:
            data["tags"].append(
                {"id": tag.id, "name": tag.name, "slug": tag.slug}
            )

        for ingredient in ingredients:
            data["ingredients"].append(
                {
                    "id": ingredient.id,
                    "name": ingredient.name,
                    "measurement_unit": ingredient.measurement_unit,
                }
            )

        for recipe in recipes:
            image_data = None
            if recipe.image:
                try:
                    with open(recipe.image.path, "rb") as image_file:
                        image_data = (
                            f"data:image/png;base64,"
                            f"{base64.b64encode(image_file.read()).decode('utf-8')}"
                        )
                except FileNotFoundError:
                    self.stdout.write(self.style.WARNING(f'Image not found for recipe {recipe.id}'))

            ingredients_data = [
                {
                    "id": item.ingredient.id,
                    "name": item.ingredient.name,
                    "measurement_unit": item.ingredient.measurement_unit,
                    "amount": item.amount,
                }
                for item in recipe.recipe_ingredients.all()
            ]
            data["recipes"].append(
                {
                    "id": recipe.id,
                    "author": recipe.author.id,
                    "name": recipe.name,
                    "image": image_data,
                    "text": recipe.text,
                    "cooking_time": recipe.cooking_time,
                    "tags": [tag.id for tag in recipe.tags.all()],
                    "ingredients": ingredients_data,
                }
            )

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        self.stdout.write(
            self.style.SUCCESS("Данные успешно экспортированы в data.json")
        )
```

## 2. Адаптация фронтенда для работы с локальными данными

Фронтенд-приложение на React было модифицировано, чтобы вместо запросов к API оно использовало локальный файл `data.json`.

- **Файл:** `frontend/src/api/index.js`
- **Описание:** Класс `Api` был полностью переписан. Вместо `fetch`-запросов к бэкенду он теперь импортирует `data.json` и эмулирует ответы API, работая с данными как с локальной базой. Была добавлена логика для "обогащения" данных (подстановки авторов и тегов в рецепты).

**Было (фрагмент):**
```javascript
// frontend/src/api/index.js
class Api {
  constructor(url, headers) {
    this._url = url;
    this._headers = headers;
  }
  
  getRecipes({ page = 1, limit = 6 }) {
    const token = localStorage.getItem("token");
    // ...
    return fetch(
      `/api/recipes/?page=${page}&limit=${limit}`,
      {
        // ...
      }
    ).then(this.checkResponse);
  }
  // ...
}
```

**Стало (фрагмент):**
```javascript
// frontend/src/api/index.js
import data from '../data.json';

class Api {
  constructor() {
    this._data = data;
    // ... pre-calculating maps for users and tags
  }

  // Helper to enrich recipe data
  enrichRecipe(recipe) {
    return {
      ...recipe,
      author: this._usersById[recipe.author] || null,
      tags: recipe.tags.map(tagId => this._tagsById[tagId]).filter(Boolean),
    };
  }

  getRecipes({ page = 1, limit = 6, author, tags } = {}) {
    let recipes = [...this._data.recipes];
    // ... filtering logic
    const enrichedRecipes = recipes.map(this.enrichRecipe.bind(this));
    // ... pagination logic
    return this.simulateDelay({
      count: enrichedRecipes.length,
      results: paginatedRecipes,
    });
  }
  // ...
}
```

## 3. Настройка для хостинга на GitHub Pages

Для корректного развертывания на GitHub Pages были выполнены критически важные настройки.

### 3.1. Переход на `HashRouter`
- **Файл:** `frontend/src/index.js`
- **Описание:** `BrowserRouter` был заменен на `HashRouter` для корректной обработки навигации на статическом хостинге.

**Было:**
```javascript
// frontend/src/index.js
import { BrowserRouter } from 'react-router-dom'

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById('root')
);
```

**Стало:**
```javascript
// frontend/src/index.js
import { HashRouter } from 'react-router-dom'

ReactDOM.render(
  <React.StrictMode>
    <HashRouter>
      <App />
    </HashRouter>
  </React.StrictMode>,
  document.getElementById('root')
);
```

### 3.2. Настройка путей к ресурсам
- **Файл:** `frontend/package.json`
- **Описание:** Был добавлен параметр `homepage` для корректной сборки путей к файлам CSS и JavaScript.

**Было (отсутствовало):**
```json
{
  "name": "foodgram-project-react",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    // ...
  }
}
```

**Стало:**
```json
{
  "name": "foodgram-project-react",
  "version": "0.1.0",
  "private": true,
  "homepage": "/foodgram_static",
  "dependencies": {
    // ...
  }
}
```

### 3.3. Исправление навигации
- **Файл:** `frontend/src/configs/navigation.js`
- **Описание:** Путь для главной страницы "Рецепты" был изменен на `/` для избежания ошибок с относительными путями при навигации.

**Было:**
```javascript
// frontend/src/configs/navigation.js
export default [
  {
    title: 'Рецепты',
    href: '/recipes',
    auth: false
  }, 
  // ...
]
```

**Стало:**
```javascript
// frontend/src/configs/navigation.js
export default [
  {
    title: 'Рецепты',
    href: '/',
    auth: false
  }, 
  // ...
]
```