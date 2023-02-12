from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post


User = get_user_model()

class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Test')
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date='Тестовая дата',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="Jag")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

# Проверяем шаблоны на корректность
    def test_correct_templates(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': 'Test'}),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}),
            'posts/create_post.html': reverse(
                'posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, 200)

# Проверяем шаблоны на соответствие контексту
    def test_index_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_title=first_object.group.title
        post_text = first_object.text
        post_author1 = first_object.author.username
        self.assertEqual(post_title, 'Тестовый заголовок')
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertEqual(post_author1, 'Test')