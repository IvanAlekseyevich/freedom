from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post, Group

User = get_user_model()


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
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.__class__.test_author)

    def test_auth_user_can_create_publish_post(self):
        """Авторизованный пользователь создает запись в Post при валидной форме."""
        posts_count = Post.objects.count()
        text = 'Тестовый пост формы'
        form_data = {
            'text': text,
            'group': {1: self.__class__.test_group.title}
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
        self.assertEqual(Post.objects.latest('pub_date').group, self.__class__.test_group)
        self.assertTrue(
            Post.objects.filter(
                text=text
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
            reverse('posts:post_edit', args=(self.__class__.test_post.id,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('posts:post_detail', args=(self.__class__.test_post.id,)))
        self.assertEqual(Post.objects.get(id=self.__class__.test_post.id).text, text)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.get(id=self.__class__.test_post.id).author, self.__class__.test_author)
        self.assertIsNone(Post.objects.get(id=self.__class__.test_post.id).group)
