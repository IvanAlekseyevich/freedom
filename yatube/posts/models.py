from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название группы',
        max_length=200,
        help_text='Введите название группы')
    slug = models.SlugField(
        verbose_name='Сокращение',
        unique=True,
        help_text=(
            'Укажите уникальный адрес для страницы группы. Используйте только '
            'латиницу, цифры, дефисы и знаки подчёркивания'
        ))
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Введите название группы'
    )

    class Meta:
        verbose_name_plural = 'Группы постов'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста', help_text='Введите текст поста')
    pub_date = models.DateTimeField(verbose_name='Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Загрузите картинку'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]
