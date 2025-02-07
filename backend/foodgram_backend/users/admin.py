from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс настройки раздела пользователей."""

    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'is_admin'
    )
    empty_value_display = 'значение отсутствует'
    list_editable = ('is_admin',)
    list_filter = ('username', 'email')
    search_fields = ('username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Класс настройки раздела подписок."""

    list_display = (
        'pk',
        'author',
        'user',
    )

    list_editable = ('author', 'user')
    list_filter = ('author',)
    search_fields = ('author',)


admin.site.site_title = 'Администрирование Foodgram'
admin.site.site_header = 'Администрирование Foodgram'
