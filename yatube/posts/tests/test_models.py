from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment

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
            text='Тестовый поста',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий'
        )

    def test_verbose_name_group(self):
        """verbose_name в полях group совпадает с ожидаемым."""
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Сокращение',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.group._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_name_post(self):
        """verbose_name в полях post совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_name_comment(self):
        """verbose_name в полях comment совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст комментария',
            'created': 'Дата публикации',
            'post': 'Пост',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.comment._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_group(self):
        """help_text в полях group совпадает с ожидаемым."""
        field_help_texts = {
            'title': 'Введите название группы',
            'slug': ('Укажите уникальный адрес для страницы группы. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания'),
            'description': 'Введите название группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.group._meta.get_field(field).help_text, expected_value)

    def test_help_text_post(self):
        """help_text в полях post совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
            'image': 'Загрузите картинку'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).help_text, expected_value)

    def test_help_text_comment(self):
        """help_text в полях comment совпадает с ожидаемым."""
        field = 'text'
        expected_value = 'Введите текст комментария'
        self.assertEqual(PostModelTest.comment._meta.get_field(field).help_text, expected_value)

    def test_models_have_correct_metod_str(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(PostModelTest.group.title, str(PostModelTest.group))
        self.assertEqual(PostModelTest.post.text[:15], str(PostModelTest.post))

