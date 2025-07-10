import os
import random
from django.core.files import File
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    """Назначает случайные аватарки пользователям, у которых их нет."""

    help = 'Назначение аватарок пользователям из папки data/avatars'

    def handle(self, *args, **options):
        avatars_dir = os.path.join(settings.BASE_DIR, 'data', 'avatars')

        if not os.path.exists(avatars_dir):
            self.stdout.write(self.style.ERROR(f"Директория с аватарками не найдена: {avatars_dir}"))
            self.stdout.write(self.style.WARNING("Пожалуйста, создайте ее и положите туда файлы изображений."))
            return

        available_avatars = [f for f in os.listdir(avatars_dir) if os.path.isfile(os.path.join(avatars_dir, f))]

        if not available_avatars:
            self.stdout.write(self.style.ERROR(f"В директории {avatars_dir} нет файлов аватарок."))
            return
            
        self.stdout.write(f"Найдено аватарок: {len(available_avatars)}. Начинаю обработку пользователей...")

        # Находим пользователей без аватарки (где поле avatar пустое)
        users_without_avatar = User.objects.filter(avatar='')

        if not users_without_avatar:
            self.stdout.write(self.style.SUCCESS("У всех пользователей уже есть аватарки."))
            return

        for user in users_without_avatar:
            random_avatar_name = random.choice(available_avatars)
            avatar_path = os.path.join(avatars_dir, random_avatar_name)

            with open(avatar_path, 'rb') as avatar_file:
                django_file = File(avatar_file)
                # Используем имя поля 'avatar'
                user.avatar.save(random_avatar_name, django_file, save=True)
            
            # self.stdout.write(self.style.SUCCESS(f"Пользователю '{user.username}' назначена аватарка: {random_avatar_name}"))

        self.stdout.write(self.style.SUCCESS("\nНазначение аватарок завершено!"))