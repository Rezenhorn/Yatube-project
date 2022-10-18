from math import ceil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorTests(TestCase):
    """Тесты работы паджинатора."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.NUM_OF_TEST_POSTS = 15
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug1',
            description='Тестовое описание 1'
        )
        for var in range(cls.NUM_OF_TEST_POSTS):
            Post.objects.create(
                text='Тестовый текст',
                group=cls.group,
                author=cls.user,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """Модуль паджинатор работает корректно."""
        num_of_last_page = ceil(self.NUM_OF_TEST_POSTS / settings.POSTS_NUM)
        test_pages = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        for test_page in test_pages:
            with self.subTest(test_page=test_page):
                response_first_page = self.authorized_client.get(test_page)
                self.assertEqual(
                    len(response_first_page.context['page_obj']),
                    settings.POSTS_NUM
                )
                response_last_page = self.authorized_client.get(
                    test_page + f'?page={num_of_last_page}'
                )
                self.assertEqual(
                    self.NUM_OF_TEST_POSTS - (
                        settings.POSTS_NUM * (num_of_last_page - 1)),
                    len(response_last_page.context['page_obj'])
                )
