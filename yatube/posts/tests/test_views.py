from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from datetime import datetime

from posts.models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.date = datetime.now()
        # Создадим запись в БД для проверки доступности адресов
        cls.user = User.objects.create_user(username='Test_author')
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание'
        )
        for i in range(12):
            Post.objects.create(
            text='Тестовый пост',
            pub_date='1854-03-14',
            author= cls.user,
            group = cls.test_group
        )
        cls.test_post = Post.objects.create(
            text='Тестовый пост',
            pub_date=cls.date,
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        # Создаем пользователя
        # self.user = User.objects.create_user(username='Test_user')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostURLTests.user)

    def test_post_views_urls_uses_correct_template(self):
        """Views функции приложения posts используют соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args=(PostURLTests.test_group.slug,)): 'posts/group_list.html',
            reverse('posts:profile', args=(PostURLTests.user,)): 'posts/profile.html',
            reverse('posts:post_detail', args=(PostURLTests.test_post.id,)): 'posts/post_detail.html',
            reverse('posts:post_edit', args=(PostURLTests.test_post.id,)): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html', 
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_index_page_show_correct_context(self):
        """Шаблон index приложения posts сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, PostURLTests.test_post.text)
        self.assertEqual(post_pub_date_0, PostURLTests.test_post.pub_date)
        self.assertEqual(post_author_0, PostURLTests.user)

    def test_post_group_list_page_show_correct_context(self):
        """Шаблон group_list приложения posts сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:group_list', args=(PostURLTests.test_group.slug,)))
        first_object = response.context['page_obj'][0]
        second_object = response.context['group']
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        group_description_0 = second_object.description
        group_title_0 = second_object.title
        self.assertEqual(post_text_0, PostURLTests.test_post.text)
        self.assertEqual(post_pub_date_0, PostURLTests.test_post.pub_date)
        self.assertEqual(post_author_0, PostURLTests.user)
        self.assertEqual(group_description_0, PostURLTests.test_group.description)
        self.assertEqual(group_title_0, PostURLTests.test_group.title)

    def test_post_profile_page_show_correct_context(self):
        """Шаблон profile приложения posts сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:profile', args=(PostURLTests.user,)))
        first_object = response.context['page_obj'][0]
        second_object = response.context['count']
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_count_0 = second_object
        self.assertEqual(post_text_0, PostURLTests.test_post.text)
        self.assertEqual(post_pub_date_0, PostURLTests.test_post.pub_date)
        self.assertEqual(post_author_0, PostURLTests.user)
        self.assertEqual(post_count_0, PostURLTests.test_post.author.posts.count())

    def test_post_post_detail_page_show_correct_context(self):
        """Шаблон post_detail приложения posts сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:post_detail', args=(PostURLTests.test_post.id,)))
        first_object = response.context['post_detail']
        second_object = response.context['count']
        post_count_0 = second_object
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, PostURLTests.test_post.text)
        self.assertEqual(post_pub_date_0, PostURLTests.test_post.pub_date)
        self.assertEqual(post_author_0, PostURLTests.user)
        self.assertEqual(post_count_0 , PostURLTests.test_post.author.posts.count())

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
        response = self.authorized_client.get(reverse('posts:post_edit', args=(PostURLTests.test_post.id,)))
        form_fields = {
            'text': forms.fields.CharField,         
            'group': forms.fields.ChoiceField,
        }        
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
  
    def test_post_first_index_page_contains_ten_records(self):
        '''Тест паджинатора страницы index, на главной странице 10 постов'''
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10. 
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_post_second_index_page_contains_three_records(self):
        '''Тест паджинатора страницы index, на второй странице 3 поста'''
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_post_first_group_page_contains_ten_records(self):
        '''Тест паджинатора, на странице группы 10 постов'''
        response = self.client.get(reverse('posts:group_list', args=(PostURLTests.test_group.slug,)))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_post_second_group_page_contains_three_records(self):
        '''Тест паджинатора, на второй странице группы 2 поста'''
        response = self.client.get(reverse('posts:group_list', args=(PostURLTests.test_group.slug,)) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_post_first_profile_page_contains_ten_records(self):
        '''Тест паджинатора, на странице профиля 10 постов'''
        response = self.client.get(reverse('posts:profile', args=(PostURLTests.user,)))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_post_second_profile_page_contains_three_records(self):
        '''Тест паджинатора, на второй странице профиля 3 поста'''
        response = self.client.get(reverse('posts:profile', args=(PostURLTests.user,)) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
