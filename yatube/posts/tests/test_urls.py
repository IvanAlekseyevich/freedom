from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_author = User.objects.create_user(username='Test_author')
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый заголовок',
            pub_date='1854-03-14',
            author=cls.test_author,
            group=cls.test_group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = User.objects.create_user(username='Test_user')
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.__class__.test_author)

    def test_post_urls_unauth_user_available(self):
        """Страницы приложения posts доступны по данным URL-адресам для всех пользователей."""
        pages = (
            '/',
            f'/group/{self.__class__.test_group.slug}/',
            f'/profile/{self.__class__.test_author.username}/',
            f'/posts/{self.__class__.test_post.id}/',
        )
        for page in pages:
            with self.subTest(url=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_authorized_user(self):
        """Страница /create/ приложения posts доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_url_redirect_anonymous(self):
        """Страница /create/ приложения posts перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_url_exists_at_author(self):
        """Страница /edit/ приложения posts доступна автору поста."""
        response = self.author_client.post(f'/posts/{self.__class__.test_post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_no_author(self):
        """Страница /edit/ приложения posts перенаправляет не автора поста."""
        response = self.authorized_client.post(f'/posts/{self.__class__.test_post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_enexisting_page_url_redirect(self):
        """Несуществующая страница /enexisting_page/ вернет ошибку 404."""
        response = self.guest_client.get('/enexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_urls_uses_correct_template(self):
        """URL-адреса приложения posts используют соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.__class__.test_group.slug}/': 'posts/group_list.html',
            f'/profile/{self.__class__.test_author.username}/': 'posts/profile.html',
            f'/posts/{self.__class__.test_post.id}/': 'posts/post_detail.html',
            f'/posts/{self.__class__.test_post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
