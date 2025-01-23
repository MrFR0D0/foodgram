from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единицы измерения',
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Уникальное название',
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name='Уникальный слаг',
    )

    def __str__(self):
        return self.name


# class Recipe(models.Model):
#     tags = models.ManyToManyField(
#         Tag, through='RecipeTag'
#     )



#     name = models.CharField(max_length=16)
#     color = models.CharField(max_length=16)
#     birth_year = models.IntegerField()
#     owner = models.ForeignKey(
#         User, related_name='cats',
#         on_delete=models.CASCADE
#     )
#     achievements = models.ManyToManyField(Achievement,
#                                           through='AchievementCat')
#     image = models.ImageField(
#         upload_to='cats/images/',
#         null=True,
#         default=None
#     )

#     def __str__(self):
#         return self.name
