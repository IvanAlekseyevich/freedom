from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_available(self):
        """Страницы приложения about доступны по данным URL-адресам."""
        PAGES = (
            '/about/author/',
            '/about/tech/',
        )
        for page in PAGES:
            with self.subTest(f'{page=}'):
                self.assertTrue(HTTPStatus.OK)

    def test_about_urls_uses_correct_template(self):
        """URL-адреса страниц приложения about используют соответствующий шаблон."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template(self):
        """В view функциях приложения about используются соответствующий шаблон."""
        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
