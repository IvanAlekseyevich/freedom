from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Название группы', max_length=200)
    slug = models.SlugField(verbose_name='Сокращение', unique=True)
    description = models.TextField(verbose_name='Описание группы')
    class Meta:
        verbose_name_plural = 'Группы постов'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста')
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
        verbose_name='Группа'
    )
    class Meta:
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text
