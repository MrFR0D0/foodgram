import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """Назначает аватарки на основе гендера из users.csv."""

    help = (
        "Назначение аватарок пользователям с сайта randomuser.me на основе CSV"
    )

    def _get_gender_map(self):
        """Читает users.csv и возвращает словарь {username: gender}."""
        import csv

        gender_map = {}
        users_file_path = os.path.join(
            settings.BASE_DIR, "..", "data", "users.csv"
        )
        try:
            with open(users_file_path, encoding="utf-8") as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    if len(row) >= 6:
                        username = row[0].strip()
                        gender = row[5].strip().lower()
                        if gender in ["male", "female"]:
                            gender_map[username] = gender
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"Файл не найден: {users_file_path}!")
            )
        return gender_map

    def handle(self, *args, **options):
        """Обработчик данных."""
        import requests

        gender_map = self._get_gender_map()
        if not gender_map:
            self.stdout.write(
                self.style.ERROR(
                    "Не удалось получить данные о \
                        гендере пользователей из CSV!"
                )
            )
            return

        # self.stdout.write("Начинаю обработку пользователей...")
        users_without_avatar = User.objects.filter(avatar="", is_staff=False)

        if not users_without_avatar:
            self.stdout.write(
                self.style.SUCCESS("У всех пользователей уже есть аватарки.")
            )
            return

        for user in users_without_avatar:
            gender = gender_map.get(user.username)
            if not gender:
                self.stdout.write(
                    self.style.WARNING(
                        f"Гендер для пользователя {user.username} \
                            не найден в CSV! Пропускаю..."
                    )
                )
                continue

            api_url = f"https://randomuser.me/api/?gender={gender}"

            try:
                api_response = requests.get(api_url, timeout=10)
                api_response.raise_for_status()
                data = api_response.json()
                image_url = data["results"][0]["picture"]["large"]

                image_response = requests.get(
                    image_url, stream=True, timeout=10
                )
                image_response.raise_for_status()

                avatar_content = ContentFile(image_response.content)
                file_name = f"{user.username}_avatar.jpg"
                user.avatar.save(file_name, avatar_content, save=True)

                # self.stdout.write(self.style.SUCCESS(
                #     f"Пользователю '{user.username}' \
                #         назначена {gender} аватарка."
                # ))

            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Не удалось получить аватарку \
                            для {user.username}: {e}!"
                    )
                )
            except (KeyError, IndexError):
                self.stdout.write(
                    self.style.ERROR(
                        f"Не удалось разобрать ответ \
                            от API для {user.username}!"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Добавление аватарок завершено."))
