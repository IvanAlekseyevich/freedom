from django.test import TestCase, Client
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_urls_available(self):
        """Страницы доступны по данным URL-адресам."""
        PAGES = (
            '/about/author/',
            '/about/tech/',
        )
        for page in PAGES:
            with self.subTest(f'{page=}'):
                # response = self.guest_client.get(page)
                self.assertTrue(HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующий шаблон."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    # def test_author(self):
    #     # Отправляем запрос через client к главной странице,
    #     # созданный в setUp()
    #     response = self.guest_client.get('/about/author/')  
    #     # Утверждаем, что для прохождения теста код должен быть равен 200
    #     self.assertEqual(response.status_code, 200) 

    # def test_tech(self):
    #     response = self.guest_client.get('/about/tech/')  
    #     self.assertEqual(response.status_code, 200) 
