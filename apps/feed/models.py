import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from .validators import validate_uploaded_image


class PostQuerySet(models.QuerySet):
    def with_related(self):
        """Standard set of joins/prefetches for rendering a feed page."""
        return self.select_related("author").prefetch_related(
            "images", "likes", "comments__author"
        )


def post_image_upload_path(instance, filename):
    return f"posts/{instance.post_id}/{filename}"


class Post(models.Model):
    """A single feed post — the social-expression side of Annsana."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    caption = models.TextField(_("caption"), max_length=2200, blank=True)
    location = models.CharField(_("location"), max_length=120, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post {self.id} by {self.author}"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()


class PostImage(models.Model):
    """
    One image within a post's carousel.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        _("image"),
        upload_to=post_image_upload_path,
        validators=[validate_uploaded_image],
    )
    alt_text = models.CharField(_("alt text"), max_length=255, blank=True)
    position = models.PositiveSmallIntegerField(_("position"), default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"Image {self.position} for post {self.post_id}"
class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="liked_posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_like_per_user_post")
        ]

    def __str__(self):
        return f"{self.user} likes post {self.post_id}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    body = models.TextField(_("comment"), max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on post {self.post_id}"
