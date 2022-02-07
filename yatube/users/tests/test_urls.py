from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Отправляем запрос через client к главной странице,
        # созданный в setUp()
        response = self.guest_client.get('/')  
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200) 
