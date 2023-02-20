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
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def setUp(self) -> None:
        self.guest = Client()
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
                'posts:post_create')
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, 200)

# Проверяем шаблоны на соответствие контексту
    # index

    def test_index_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_title = first_object.group.title
        post_text = first_object.text
        post_author1 = first_object.author.username
        self.assertEqual(post_title, 'Тестовый заголовок')
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertEqual(post_author1, 'Test')
    # Group_list

    def test_group_list_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        post_title = first_object.group.title
        post_text = first_object.text
        post_author1 = first_object.author.username
        self.assertEqual(post_title, 'Тестовый заголовок')
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertEqual(post_author1, 'Test')
    # Profile

    def test_profile_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Test'}))
        first_object = response.context['page_obj'][0]
        post_title = first_object.group.title
        post_text = first_object.text
        post_author1 = first_object.author.username
        self.assertEqual(post_title, 'Тестовый заголовок')
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertEqual(post_author1, 'Test')
    # Post_detail

    def test_post_detail_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        first_object = response.context['post']
        post_title = first_object.group.title
        post_text = first_object.text
        post_author1 = first_object.author.username
        self.assertEqual(post_title, 'Тестовый заголовок')
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertEqual(post_author1, 'Test')

    # Post_create

    def test_post_create_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = (
                    response.context.get('form').fields.get(value)
                )
                self.assertIsInstance(form_field, expected)

    # Post_edit
    def test_post_edit_context(self):
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # Post_on_pages
    def test_post_on_pages(self):
        templates = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Test'})
        )
        for temp in templates:
            response = self.authorized_client.get(temp)
            self.assertEqual(len(response.context['page_obj'].object_list), 1)
    # Post_in_group

    def test_post_in_group(self):
        response = self.guest.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        posts = response.context['page_obj'].object_list
        self.assertNotIn(self.post.pk, posts)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Jag')
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug='test-slug',
            description='Тестовое описание',
        )
        posts_num = 13
        for i in range(posts_num):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group,
            )
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)

    def setUp(self):
        self.guest = Client()
        self.user = User.objects.get(username='Jag')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # posts=10

    def test_first_page(self):
        list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Jag'}),
        ]
        for name in list:
            with self.subTest(reverse_name=name):
                response = self.guest.get(name)
                self.assertEqual(len(response.context['page_obj']), 10)
    # second_page

    def test_second_page(self):
        list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Jag'}),
        ]
        for name in list:
            with self.subTest(reverse_name=name):
                response = self.guest.get(name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)