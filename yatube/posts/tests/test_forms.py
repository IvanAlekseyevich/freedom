import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Post, Group

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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
            text='Тестовый пост',
            pub_date='1854-03-14',
            author=cls.test_author,
            group=cls.test_group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostFormTests.test_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с прекрасными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_auth_user_can_create_publish_post(self):
        """Авторизованный пользователь создает запись в Post при валидной форме."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        text = 'Тестовый пост формы'
        form_data = {
            'text': text,
            'group': {PostFormTests.test_group.id},
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse('posts:profile', args=(self.user.username,)))
        self.assertEqual(Post.objects.latest('pub_date').author, self.user)
        self.assertEqual(Post.objects.latest('pub_date').group, PostFormTests.test_group)
        self.assertTrue(
            Post.objects.filter(
                text=text,
                group=PostFormTests.test_group.id,
                image='posts/small.gif'
            ).exists()
        )

    def test_auth_user_cant_create_none_text_post(self):
        """Создание поста с отсутствующим текстом вызывает ошибку у авторизованного пользователя"""
        posts_count = Post.objects.count()
        form_data = {
            'text': '',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверим, что форма вернула ошибку с ожидаемым текстом:
        # из объекта responce берём словарь 'form',
        # указываем ожидаемую ошибку для поля 'text' этого словаря
        self.assertFormError(
            response,
            'form',
            'text',
            'Обязательное поле.'
        )

    def test_auth_author_edit_post_correct(self):
        """Валидная форма при редактировании поста автором изменяет запись в базе."""
        posts_count = Post.objects.count()
        text = 'Новый тестовый пост'
        form_data = {
            'text': text,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', args=(PostFormTests.test_post.id,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('posts:post_detail', args=(PostFormTests.test_post.id,)))
        self.assertEqual(Post.objects.get(id=PostFormTests.test_post.id).text, text)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.get(id=PostFormTests.test_post.id).author, PostFormTests.test_author)
        self.assertIsNone(Post.objects.get(id=PostFormTests.test_post.id).group)
