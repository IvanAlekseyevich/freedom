from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.signup_url = '/auth/signup/'
        cls.login_url = '/auth/login/'
        cls.logout_url = '/auth/logout/'
        cls.password_change_url = '/auth/password_change/'
        cls.password_change_done_url = '/auth/password_change/done/'
        cls.password_reset_url = '/auth/password_reset/'
        cls.password_reset_done_url = '/auth/password_reset/done/'
        cls.reset_done_url = '/auth/reset/done/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = User.objects.create_user(username='Test_user')
        self.authorized_client.force_login(self.user)

    def test_user_urls_available(self):
        """Страницы приложения users доступны по данным URL-адресам для любого пользователя."""
        pages = [
            UserURLTests.signup_url,
            UserURLTests.login_url,
            UserURLTests.password_reset_url,
        ]
        for page in pages:
            with self.subTest(url=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_reset_password_url_exists_at_authorized_user(self):
        """Страница /auth/password_change/ приложения users доступна авторизованному пользователю."""
        response = self.authorized_client.get(UserURLTests.password_change_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_url_password_change_redirect_anonymous(self):
        """Страница /auth/password_change/ приложения users перенаправляет анонимного пользователя."""
        response = self.guest_client.get(UserURLTests.password_change_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_user_urls_user_correct_template(self):
        """URL-адреса приложения users используют соответствующий шаблон."""
        templates_url_names = {
            UserURLTests.signup_url: 'users/signup.html',
            UserURLTests.password_change_url: 'users/password_change_form.html',
            UserURLTests.password_change_done_url: 'users/password_change_done.html',
            UserURLTests.password_reset_url: 'users/password_reset_form.html',
            UserURLTests.password_reset_done_url: 'users/password_reset_done.html',
            UserURLTests.reset_done_url: 'users/password_reset_complete.html',
            UserURLTests.logout_url: 'users/logged_out.html',
            UserURLTests.login_url: 'users/login.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
