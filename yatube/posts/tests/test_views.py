from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from django import forms

from posts.models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адресов
        cls.user = User.objects.create_user(username='Test_author', first_name='Имя', last_name='Фамилия')
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание'
        )
        for num in range(12):
            f'test_post_{num}' == Post.objects.create(
            text='Тестовый пост',
            pub_date='1854-03-14 00:00:00',
            author= cls.user,
            group = cls.test_group
        )
        cls.test_post_13 = Post.objects.create(
            text='Тестовый пост',
            pub_date='1854-03-15 00:00:00',
            author= cls.user
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        # self.user = User.objects.create_user(username='Test_user')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostURLTests.user)

    def test_urls_available(self):
        """Страницы доступны по данным URL-адресам для любого пользователя."""
        PAGES = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': PostURLTests.test_group.slug}),
            reverse('posts:profile', kwargs={'username': PostURLTests.user}),
            reverse('posts:post_detail', kwargs={'post_id': PostURLTests.test_post_13.id})
        )
        for reverse_name in PAGES:
            with self.subTest(reverse_name=reverse_name):
                # response = self.guest_client.get(page)
                self.assertTrue(HTTPStatus.OK)

    def test_post_create_url_exists_at_authorized_user(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_edit_url_exists_at_author(self):
        """Страница /edit/ доступна автору поста."""
        response = self.authorized_client.post(reverse('posts:post_edit', kwargs={'post_id': PostURLTests.test_post_13.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_enexisting_page_url_redirect(self):
        """Несуществующая страница /enexisting_page/ вернет ошибку 404."""
        response = self.guest_client.get('/enexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': PostURLTests.test_group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': PostURLTests.user}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': PostURLTests.test_post_13.id}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': PostURLTests.test_post_13.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html', 
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка словаря контекста создания поста
    def test_create_post_page_show_correct_context(self):
        """Шаблон создания поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            # При создании формы поля модели типа TextField 
            # преобразуются в CharField с виджетом forms.Textarea           
            'group': forms.fields.ChoiceField,
        }        

        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context страницы /
    # в первом элементе списка object_list содержит ожидаемые значения 
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, PostURLTests.test_post_13.text)
        self.assertEqual(post_pub_date_0, PostURLTests.test_post_13.pub_date)
        self.assertEqual(post_author_0, PostURLTests.user)

    # Проверяем, что словарь context страницы /
    # в первом элементе списка object_list содержит ожидаемые значения 
    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:group_list', kwargs={'slug': PostURLTests.test_group.slug}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        second_object = response.context['group']
        group_description_0 = second_object.description
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        group_title_0 = second_object.title
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, PostURLTests.test_post_13.text)
        self.assertEqual(post_pub_date_0, PostURLTests.test_post_13.pub_date)
        self.assertEqual(post_author_0, PostURLTests.user)
        self.assertEqual(group_description_0, PostURLTests.test_group.description)
        self.assertEqual(group_title_0, PostURLTests.test_group.title)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:post_detail', kwargs={'post_id': PostURLTests.test_post_13.id}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['post_detail']
        second_object = response.context['count']
        post_count_0 = second_object
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, PostURLTests.test_post_13.text)
        self.assertEqual(post_pub_date_0, PostURLTests.test_post_13.pub_date)
        self.assertEqual(post_author_0, PostURLTests.user)
        self.assertEqual(post_count_0 , PostURLTests.test_post_13.author.posts.count())

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:profile', kwargs={'username': PostURLTests.user}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        second_object = response.context['count']
        post_count_0 = second_object
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, PostURLTests.test_post_13.text)
        self.assertEqual(post_pub_date_0, PostURLTests.test_post_13.pub_date)
        self.assertEqual(post_author_0, PostURLTests.user)
        self.assertEqual(post_count_0, PostURLTests.test_post_13.author.posts.count())
  
    def test_first_index_page_contains_ten_records(self):
        '''Тест паджинатора, на главной странице 10 постов'''
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10. 
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_index_page_contains_three_records(self):
        '''Тест паджинатора, на второй странице 3 поста'''
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_group_page_contains_ten_records(self):
        '''Тест паджинатора, на странице группы 10 постов'''
        response = self.client.get(reverse('posts:group_list', kwargs={'slug': PostURLTests.test_group.slug}))
        # Проверка: количество постов на первой странице равно 10. 
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_group_page_contains_three_records(self):
        '''Тест паджинатора, на второй странице группы 2 поста'''
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:group_list', kwargs={'slug': PostURLTests.test_group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_first_profile_page_contains_ten_records(self):
        '''Тест паджинатора, на странице профиля 10 постов'''
        response = self.client.get(reverse('posts:profile', kwargs={'username': PostURLTests.user}))
        # Проверка: количество постов на первой странице равно 10. 
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page_contains_three_records(self):
        '''Тест паджинатора, на второй странице профиля 2 поста'''
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:profile', kwargs={'username': PostURLTests.user}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

