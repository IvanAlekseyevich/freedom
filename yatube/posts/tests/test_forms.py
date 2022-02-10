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
        cls.user = User.objects.create_user(username='Test_author', first_name='Имя', last_name='Фамилия')
        # Создадим запись в БД
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый пост',
            pub_date='1854-03-14',
            author= cls.user,
            group = cls.test_group
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(PostFormTests.user)

    def test_create_post(self):
        '''Валидная форма создает запись в Post.'''
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()  
        form_data = {
            'text': 'Тестовый пост формы',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile', args=('Test_user',)))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count+1)
        # Проверяем, что создалась запись с заданным текстом
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост формы'
            ).exists()
        ) 
        
    def test_cant_create_none_text_post(self):
        '''Создание поста с отсутствующим текстом вызывает ошибку'''
        tasks_count = Post.objects.count()
        form_data = {
            'text': '',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Убедимся, что запись в базе данных не создалась: 
        # сравним количество записей в Task до и после отправки формы
        self.assertEqual(Post.objects.count(), tasks_count)
        # Проверим, что форма вернула ошибку с ожидаемым текстом:
        # из объекта responce берём словарь 'form', 
        # указываем ожидаемую ошибку для поля 'text' этого словаря
        self.assertFormError(
            response, 
            'form',
            'text',
            'Обязательное поле.'
        )
        # Проверим, что ничего не упало и страница отдаёт код 200
        self.assertEqual(response.status_code, 200) 

    def test_edit_post(self):
        '''Валидная форма при редактировании поста изменяет запись в базе.''' 
        text = 'Новый тестовый пост'
        form_data = {
            'text': text,
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit', args=(PostFormTests.test_post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', args=(PostFormTests.test_post.id,)))
        # Проверяем, изменился ли текст поста
        self.assertEqual(Post.objects.get(id=1).text, text)
