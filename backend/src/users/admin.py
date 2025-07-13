from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(UserAdmin):
    """Класс настройки раздела пользователей."""

    list_display = (
        "pk",
        "email",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "get_subscribers",
    )
    list_display_links = ("pk", "email")
    empty_value_display = "значение отсутствует"
    list_filter = ("is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")

    @admin.display(description="Подписчики")
    def get_subscribers(self, object):
        """Подсчет количества подписчиков."""
        return object.follower.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Класс настройки раздела подписок."""

    list_display = ("pk", "author", "user")

    def get_queryset(self, request):
        """Получение объекта подписчика."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("user", "author")
        return queryset


admin.site.site_title = "Администрирование Foodgram"
admin.site.site_header = "Администрирование Foodgram"
