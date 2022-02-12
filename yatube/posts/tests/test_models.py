from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
            group=cls.group,
        )

    def test_verbose_name_group(self):
        """verbose_name в полях group совпадает с ожидаемым."""
        task = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Сокращение',
            'description': 'Описание группы',          
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_name_post(self):
        """verbose_name в полях post совпадает с ожидаемым."""
        task = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',           
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_post(self):
        """help_text в полях post совпадает с ожидаемым."""
        task = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',             
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text, expected_value) 

    def test_help_text_group(self):
        """help_text в полях group совпадает с ожидаемым."""
        task = PostModelTest.group
        field_help_texts = {
            'title': 'Введите название группы',
            'slug': ('Укажите уникальный адрес для страницы группы. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания'),
            'description': 'Введите название группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text, expected_value) 

    def test_models_have_correct_object_text_post(self):
        """Проверяем, что у модели post корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(post.text, str(post)) 

    def test_models_have_correct_object_title_group(self):
        """Проверяем, что у модели group корректно работает __str__."""
        group = PostModelTest.group
        self.assertEqual(group.title, str(group)) 
