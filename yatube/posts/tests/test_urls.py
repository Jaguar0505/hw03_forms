from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from deals.models import Task

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        Task.objects.create(