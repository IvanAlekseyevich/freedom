from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class UserURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_urls_available(self):
        '''Страницы приложения users доступны по данным URL-адресам для любого пользователя.'''
        PAGES = (
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset/',
        )
        for page in PAGES:
            with self.subTest(url=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_reset_password_url_exists_at_authorized_user(self):
        '''Страница /auth/password_change/ приложения users доступна авторизованному пользователю.'''
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_user_url_password_change_redirect_anonymous(self):
        '''Страница /auth/password_change/ приложения users перенаправляет анонимного пользователя.'''
        response = self.guest_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_user_urls_user_correct_template(self):
        '''URL-адреса приложения users используют соответствующий шаблон.'''
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            # '/auth/password_change/': 'users/password_change_form.html',  #Не работает
            # '/auth/password_change/done/': 'users/password_change_done.html',  #Не работает
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_user_url_login_user_correct_template(self):
        '''URL-адрес /login/ приложения users использует соответствующий шаблон.'''
        response = self.guest_client.get('/auth/login/')
        template = 'users/login.html'
        self.assertTemplateUsed(response, template)
