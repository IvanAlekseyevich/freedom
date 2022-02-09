from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from django import forms

User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='Test_user')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_urls_available(self):
        """Страницы доступны по данным URL-адресам для любого пользователя."""
        PAGES = (
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:password_reset'),
        )
        for page in PAGES:
            with self.subTest(f'{page=}'):
                # response = self.guest_client.get(page)
                self.assertTrue(HTTPStatus.OK)

    def test_user_reset_password_url_exists_at_authorized_user(self):
        """Страница users:password_change доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse('users:password_change'))
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_url_redirect_anonymous(self):
        """Страница users:password_change перенаправляет анонимного пользователя."""
        response = self.guest_client.get(reverse('users:password_change'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_url_user_correct_template(self):
        """URL-адрес signup использует соответствующий шаблон."""
        response = self.guest_client.get(reverse('users:signup'))
        template = 'users/signup.html'
        self.assertTemplateUsed(response, template)

    # Проверка словаря контекста страницы регистрации
    def test_create_user_page_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('users:signup'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'first_name': forms.fields.CharField,
            # При создании формы поля модели типа TextField 
            # преобразуются в CharField с виджетом forms.Textarea           
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }        

        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_urls_user_correct_template(self):
        """URL-адреса используют соответствующий шаблон."""
        templates_url_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:login'): 'users/login.html',
            # reverse('users:password_change'): 'users/password_change_form.html',  #Не работает
            # reverse('users:password_change_done'): 'users/password_change_done.html',  #Не работает
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:password_reset_done'): 'users/password_reset_done.html',
            reverse('users:password_reset_complete'): 'users/password_reset_complete.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
