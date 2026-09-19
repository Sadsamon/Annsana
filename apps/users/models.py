import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.feed.validators import validate_uploaded_image
from .managers import UserManager


class User(AbstractUser):
    """
    Custom user model for Annsana.

    Extends Django's AbstractUser with profile fields relevant to a
    platform that blends social expression with archival cultural research.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    display_name = models.CharField(_("display name"), max_length=80, blank=True)
    bio = models.TextField(_("bio"), max_length=500, blank=True)
    avatar = models.ImageField(
        _("avatar"),
        upload_to="avatars/%Y/%m/",
        blank=True,
        null=True,
        validators=[validate_uploaded_image],
    )
    location = models.CharField(_("location"), max_length=120, blank=True)
    cultural_affiliation = models.CharField(
        _("cultural affiliation"),
        max_length=120,
        blank=True,
        help_text=_(
            "Heritage, community, or region the user wishes to highlight on their profile."
        ),
    )
    is_contributor = models.BooleanField(
        _("contributor status"),
        default=False,
        help_text=_(
            "Whether this user has been granted archival contributor permissions."
        ),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]

    def __str__(self):
        return self.display_name or self.username

    @property
    def public_name(self):
        return self.display_name or self.username
