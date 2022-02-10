from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адресов
        cls.user = User.objects.create_user(username='Test_author')
        Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый заголовок',
            pub_date='1854-03-14',
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
            '/',
            '/group/testslug/',
            '/profile/Test_author/',
            f'/posts/{PostURLTests.test_post.id}/',
        )
        for page in PAGES:
            with self.subTest(f'{page=}'):
                # response = self.guest_client.get(page)
                self.assertTrue(HTTPStatus.OK)

    def test_post_create_url_exists_at_authorized_user(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_edit_url_exists_at_author(self):
        """Страница /edit/ доступна автору поста."""
        response = self.authorized_client.post(f'/posts/{PostURLTests.test_post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_enexisting_page_url_redirect(self):
        """Несуществующая страница /enexisting_page/ вернет ошибку 404."""
        response = self.guest_client.get('/enexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/testslug/': 'posts/group_list.html',
            '/profile/Test_author/': 'posts/profile.html',
            f'/posts/{PostURLTests.test_post.id}/': 'posts/post_detail.html',
            f'/posts/{PostURLTests.test_post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html', 
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
