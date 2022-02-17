import shutil
import tempfile
from datetime import datetime
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, Comment, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.date = datetime.now()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.test_author = User.objects.create_user(username='Test_author')
        cls.test_user = User.objects.create_user(username='Test_user')
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый пост',
            pub_date=cls.date,
            author=cls.test_author,
            group=cls.test_group,
            image=cls.uploaded
        )
        cls.test_comment = Comment.objects.create(
            author=cls.test_author,
            post=cls.test_post,
            text='Тестовый комментарий'
        )
        cls.follow = Follow.objects.create(
            user=cls.test_user,
            author=cls.test_author
        )

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.test_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cache.clear()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_views_urls_uses_correct_template(self):
        """Views функции приложения posts используют соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args=(PostViewTests.test_group.slug,)): 'posts/group_list.html',
            reverse('posts:profile', args=(PostViewTests.test_author.username,)): 'posts/profile.html',
            reverse('posts:post_detail', args=(PostViewTests.test_post.id,)): 'posts/post_detail.html',
            reverse('posts:post_edit', args=(PostViewTests.test_post.id,)): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = PostViewTests.author_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_post_list_page_show_correct_context(self):
        """Проверка правильного вывода контекста поста в шаблоны"""
        cache.clear()
        reversed_name = {
            'posts:index': None,
            'posts:group_list': (PostViewTests.test_group.slug,),
            'posts:profile': (PostViewTests.test_author.username,),
        }
        for reverse_name, args in reversed_name.items():
            with self.subTest(reverse_name=reverse(reverse_name, args=args)):
                response = PostViewTests.guest_client.get(reverse(reverse_name, args=args))
                context_post = response.context['page_obj'][0]
                self.assertEqual(context_post.text, PostViewTests.test_post.text)
                self.assertEqual(context_post.pub_date, PostViewTests.test_post.pub_date)
                self.assertEqual(context_post.author, PostViewTests.test_post.author)
                self.assertEqual(context_post.image, PostViewTests.test_post.image)

    def test_post_group_list_page_show_correct_context(self):
        """Шаблон group_list приложения posts сформирован с правильным контекстом."""
        response = PostViewTests.guest_client.get(reverse('posts:group_list', args=(PostViewTests.test_group.slug,)))
        context_group = response.context['group']
        self.assertEqual(context_group.description, PostViewTests.test_post.group.description)
        self.assertEqual(context_group.title, PostViewTests.test_post.group.title)

    def test_post_profile_page_show_correct_context(self):
        """Шаблон profile приложения posts сформирован с правильным контекстом."""
        response = PostViewTests.guest_client.get(reverse('posts:profile', args=(PostViewTests.test_author.username,)))
        context_count = response.context['count']
        self.assertEqual(context_count, PostViewTests.test_post.author.posts.count())

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail приложения posts сформирован с правильным контекстом."""
        response = PostViewTests.guest_client.get(reverse('posts:post_detail', args=(PostViewTests.test_post.id,)))
        context_post = response.context['post_detail']
        context_count = response.context['count']
        context_comment = response.context['comments'][0]
        self.assertEqual(context_post.text, PostViewTests.test_post.text)
        self.assertEqual(context_post.pub_date, PostViewTests.test_post.pub_date)
        self.assertEqual(context_post.author, PostViewTests.test_post.author)
        self.assertEqual(context_post.image, PostViewTests.test_post.image)
        self.assertEqual(context_count, PostViewTests.test_post.author.posts.count())
        self.assertEqual(context_comment.text, PostViewTests.test_comment.text)

    def test_post_create_page_show_correct_context(self):
        """Шаблон создания и редактирования поста сформирован с правильным контекстом."""
        reversed_name = {
            'posts:post_create': None,
            'posts:post_edit': (PostViewTests.test_post.id,)
        }
        for reversed_name, args in reversed_name.items():
            response = PostViewTests.author_client.get(reverse(reversed_name, args=args))
            form_fields = {
                'text': forms.fields.CharField,
                # При создании формы поля модели типа TextField
                # преобразуются в CharField с виджетом forms.Textarea
                'group': forms.fields.ChoiceField,
                'image': forms.fields.ImageField,
            }
            for value, expected in form_fields.items():
                with self.subTest(reverse=reverse(reversed_name, args=args), value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_paginator_in_pages_with_posts(self):
        """Тест паджинатора на страницах с постами"""
        cache.clear()
        paginator_amount = 10
        second_page_amount = 3
        posts = [
            Post(
                text=f'text {num}', author=PostViewTests.test_author,
                group=PostViewTests.test_group
            ) for num in range(1, paginator_amount + second_page_amount)
        ]
        Post.objects.bulk_create(posts)
        paginator_page = {
            'posts:index': None,
            'posts:group_list': (PostViewTests.test_group.slug,),
            'posts:profile': (PostViewTests.test_author,),
            'posts:follow_index': None,
        }
        for reverse_name, args in paginator_page.items():
            post_page = {
                paginator_amount: '',
                second_page_amount: '?page=2'
            }
            for amount, page in post_page.items():
                with self.subTest(reverse=reverse(reverse_name, args=args), amount=amount, page=page):
                    response = PostViewTests.authorized_client.get(reverse(reverse_name, args=args) + page)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertEqual(len(response.context['page_obj']), amount)

    def test_caches_index_page(self):
        """Тестирование кэша страницы index"""
        count_post = Post.objects.count()
        response = PostViewTests.guest_client.get(reverse('posts:index'))
        origin_post = response.context['page_obj']
        Post.objects.all().delete()
        cashes_post = response.context['page_obj']
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEquals(count_post, 0)
        self.assertEqual(cashes_post, origin_post)

    def test_correct_work_follow(self):
        """Авторизированный пользователь может подписываться и отписываться от авторов постов."""
        follower = PostViewTests.test_author
        following = PostViewTests.test_user
        follow = PostViewTests.author_client.get(
            reverse('posts:profile_follow', args=(following.username,))
        )
        follow_exists = Follow.objects.filter(user=follower, author=following).exists()
        unfollow = PostViewTests.author_client.get(
            reverse('posts:profile_unfollow', args=(following.username,))
        )
        follow_dont_exists = Follow.objects.filter(user=follower, author=following).exists()
        self.assertTrue(follow_exists)
        self.assertRedirects(follow, reverse('posts:profile', args=(following.username,)))
        self.assertFalse(follow_dont_exists)
        self.assertRedirects(unfollow, reverse('posts:profile', args=(following.username,)))
