from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserCreateFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_user_create(self):
        """Валидная форма создает пользователя в БД."""
        user_count = User.objects.count()
        password = 'test_p@ssw0rd'
        form_data = {
            'username': 'test_username',
            'password1': password,
            'password2': password
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('users:login'))
        self.assertEqual(User.objects.count(), user_count + 1)
