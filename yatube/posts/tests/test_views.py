from datetime import datetime
from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.date = datetime.now()
        # Создадим запись в БД для проверки доступности адресов
        cls.test_author = User.objects.create_user(username='Test_author')
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        # Создаем пользователя
        # self.user = User.objects.create_user(username='Test_user')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.__class__.test_author)
        self.test_post = Post.objects.create(
            text='Тестовый пост',
            pub_date=self.__class__.date,
            author=self.__class__.test_author,
            group=self.__class__.test_group
        )

    def test_post_views_urls_uses_correct_template(self):
        """Views функции приложения posts используют соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args=(self.__class__.test_group.slug,)): 'posts/group_list.html',
            reverse('posts:profile', args=(self.__class__.test_author.username,)): 'posts/profile.html',
            reverse('posts:post_detail', args=(self.test_post.id,)): 'posts/post_detail.html',
            reverse('posts:post_edit', args=(self.test_post.id,)): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_index_page_show_correct_context(self):
        """Шаблон index приложения posts сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        context_post = response.context['page_obj'][0]
        self.assertEqual(context_post.text, self.test_post.text)
        self.assertEqual(context_post.pub_date, self.test_post.pub_date)
        self.assertEqual(context_post.author, self.test_post.author)

    def test_post_group_list_page_show_correct_context(self):
        """Шаблон group_list приложения posts сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:group_list', args=(self.__class__.test_group.slug,)))
        context_post = response.context['page_obj'][0]
        context_group = response.context['group']
        self.assertEqual(context_post.text, self.test_post.text)
        self.assertEqual(context_post.pub_date, self.test_post.pub_date)
        self.assertEqual(context_post.author, self.test_post.author)
        self.assertEqual(context_group.description, self.__class__.test_group.description)
        self.assertEqual(context_group.title, self.__class__.test_group.title)

    def test_post_profile_page_show_correct_context(self):
        """Шаблон profile приложения posts сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:profile', args=(self.__class__.test_author.username,)))
        context_post = response.context['page_obj'][0]
        context_count = response.context['count']
        self.assertEqual(context_post.text, self.test_post.text)
        self.assertEqual(context_post.pub_date, self.test_post.pub_date)
        self.assertEqual(context_post.author, self.test_post.author)
        self.assertEqual(context_count, self.test_post.author.posts.count())

    def test_post_post_detail_page_show_correct_context(self):
        """Шаблон post_detail приложения posts сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:post_detail', args=(self.test_post.id,)))
        context_post = response.context['post_detail']
        context_count = response.context['count']
        self.assertEqual(context_post.text, self.test_post.text)
        self.assertEqual(context_post.pub_date, self.test_post.pub_date)
        self.assertEqual(context_post.author, self.test_post.author)
        self.assertEqual(context_count, self.test_post.author.posts.count())

    def test_post_create_post_page_show_correct_context(self):
        """Шаблон создания поста приложения posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            # При создании формы поля модели типа TextField 
            # преобразуются в CharField с виджетом forms.Textarea           
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_post_page_show_correct_context(self):
        """Шаблон редактирования поста приложения posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit', args=(self.test_post.id,)))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_paginator_in_pages_with_posts(self):
        """Тест паджинатора на страницах с постами"""
        paginator_amount = 10
        second_page_amount = 3
        posts = [
            Post(
                text=f'text {num}', author=self.__class__.test_author,
                group=self.__class__.test_group
            ) for num in range(1, paginator_amount + second_page_amount)
        ]
        Post.objects.bulk_create(posts)
        paginator_page = (
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.__class__.test_group.slug,)),
            reverse('posts:profile', args=(self.__class__.test_author,)),
        )
        for reverse_name in paginator_page:
            with self.subTest(reverse_name=reverse_name):
                response_first_page = self.guest_client.get(reverse_name)
                response_second_page = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(response_first_page.status_code, HTTPStatus.OK)
                self.assertEqual(len(response_first_page.context['page_obj']), paginator_amount)
                self.assertEqual(response_second_page.status_code, HTTPStatus.OK)
                self.assertEqual(len(response_second_page.context['page_obj']), second_page_amount)
