from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_public_name_falls_back_to_username(self):
        user = User.objects.create_user(username="amara", password="testpass123")
        self.assertEqual(user.public_name, "amara")

    def test_public_name_prefers_display_name(self):
        user = User.objects.create_user(
            username="amara", password="testpass123", display_name="Amara K."
        )
        self.assertEqual(user.public_name, "Amara K.")
