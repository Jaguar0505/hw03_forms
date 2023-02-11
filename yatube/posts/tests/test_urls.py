from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Jag')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем автора поста
        self.post_author = Client()
        self.post_author.force_login(PostsURLTests.post.author)
        # Страницы которые доступны всем

    def test_startpage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_page(self):
        response = self.guest_client.get('/group/test_slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_page(self):
        response = self.guest_client.get(
            f'/profile/{PostsURLTests.user.username}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_post_page(self):
        response = self.guest_client.get(f'/posts/{self.post.pk}/')
        self.assertEqual(response.status_code, 200)

        # Страница редактирования доступна только автору поста

    def test_post_edit_author(self):
        self.post_author.username = self.post.author
        response = self.post_author.get(
            f'/posts/{PostsURLTests.post.pk}/edit/')
        self.assertEqual(response.status_code, 200)

        # Проверка создания поста авторизированным пользователем

    def test_url_create_page(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

        # 404

    def test_url_404(self):
        response = self.guest_client.get('/unexistsng_page/')
        self.assertEqual(response.status_code, 404)
