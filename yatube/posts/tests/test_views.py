import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    """Тесты view-функций приложения Post."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='test_user')
        Follow.objects.create(user=cls.user, author=cls.user_author)
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug1',
            description='Тестовое описание 1'
        )
        cls.group_without_post = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2'
        )
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
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_show_correct_context(self):
        """Шаблоны index, group_list, profile сформированы
        с правильным контекстом.
        """
        pages = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        for reverse_name in pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(self.post, response.context.get('page_obj'))

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context['post'], self.post)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertEqual(response.context['form'].instance, self.post)

    def test_post_not_in_other_group(self):
        """Пост не попал в группу, для которой не был предназначен."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group_without_post.slug}))
        self.assertNotIn(self.post, response.context.get('page_obj'))

    def test_y_cache_index_page(self):
        """Тестирование кэширования постов главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.post.delete()
        response2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response2.content)
        cache.clear()
        response3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response3.content)

    def test_user_can_unfollow(self):
        """Авторизованный пользователь может отписываться."""
        response_unfollow = self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user_author.username})
        )
        self.assertRedirects(response_unfollow, reverse('posts:follow_index'))
        self.assertNotIn(
            self.user_author.pk,
            self.user.follower.values_list('author_id', flat=True)
        )

    def test_user_can_follow(self):
        """Авторизованный пользователь может подписываться."""
        response_follow = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_author.username})
        )
        self.assertRedirects(response_follow, reverse('posts:follow_index'))
        self.assertIn(
            self.user_author.pk,
            self.user.follower.values_list('author_id', flat=True)
        )

    def test_new_post_appears_in_follow_page(self):
        """Запись появляется в ленте подписчиков и не появляется
        в других лентах.
        """
        self.new_post = Post.objects.create(
            text='Новый пост',
            author=self.user_author,
        )
        response_user = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(self.new_post, response_user.context.get('page_obj'))
        self.authorized_client.force_login(self.user_author)
        response_author = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(
            self.new_post, response_author.context.get('page_obj')
        )
