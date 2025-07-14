import os
from csv import reader

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """Загружает списка пользователей и создание суперпользователя."""

    help = (
        "Загрузка пользователей из data/users.csv и создание суперпользователя"
    )

    def handle(self, *args, **options):
        """Обрабатывает логику загрузки пользователей и создания админа."""
        users_file_path = os.path.join(
            settings.BASE_DIR, "..", "data", "users.csv"
        )

        try:
            with open(users_file_path, encoding="utf-8") as csv_file:
                csv_reader = reader(csv_file)
                # self.stdout.write("Начинаю загрузку пользователей...")
                for row in csv_reader:
                    username = row[0].strip()
                    if User.objects.filter(username=username).exists():
                        # self.stdout.write(self.style.WARNING(
                        #     f"Пользователь '{username}' \
                        #         уже существует. Пропускаю."
                        # ))
                        continue

                    # Используем только первые 5 столбцов
                    User.objects.create_user(
                        username=username,
                        password=row[1].strip(),
                        first_name=row[2].strip(),
                        last_name=row[3].strip(),
                        email=row[4].strip(),
                    )
                    # self.stdout.write(self.style.SUCCESS(
                    #     f"Пользователь '{username}' успешно создан."
                    # ))
            self.stdout.write(
                self.style.SUCCESS("Загрузка пользователей завершена.")
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"Файл не найден: {users_file_path}!")
            )

        # self.stdout.write("\nПроверяю наличие суперпользователя...")
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@admin.com", "admin")
            self.stdout.write(
                self.style.SUCCESS(
                    "Суперпользователь для администрирования - \
                        email: admin@admin.com пароль: admin"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Суперпользователь для администрирования - \
                        email: admin@admin.com пароль: admin"
                )
            )
