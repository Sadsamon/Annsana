from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Like, Post

User = get_user_model()


class PostModelTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="amara", password="testpass123")
        self.post = Post.objects.create(author=self.author, caption="Hello Annsana")

    def test_like_count_starts_at_zero(self):
        self.assertEqual(self.post.like_count, 0)

    def test_is_liked_by_reflects_like_state(self):
        liker = User.objects.create_user(username="kwame", password="testpass123")
        self.assertFalse(self.post.is_liked_by(liker))
        Like.objects.create(post=self.post, user=liker)
        self.assertTrue(self.post.is_liked_by(liker))


class FeedViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="amara", password="testpass123")
        Post.objects.create(author=self.author, caption="First post")

    def test_feed_list_renders(self):
        response = self.client.get(reverse("feed:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First post")
