from django.conf import settings
from django.db import models


def avatar_upload_path(instance, filename):
    """media/avatars/<user_id>/<filename>"""
    return f'avatars/{instance.user_id}/{filename}'


class UserProfile(models.Model):
    """
    One-to-one extension of Django's built-in User model.

    Schema mirrors TSD Section 5.1 (users_userprofile) exactly. Do not add
    fields here without updating the TSD first — this table is the anchor
    for the Griot role system and the Trust Layer's reputation scoring.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    is_griot = models.BooleanField(
        default=False,
        help_text='Vetted expert/enthusiast. Promoted manually via the admin at MVP.',
    )
    reputation_score = models.IntegerField(default=0)
    location = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.username} ({"Griot" if self.is_griot else "Member"})'

    def recalculate_reputation(self):
        """
        Explicit, testable reputation calculation (TSD Section 12).

        Deliberately decoupled from a Django signal receiver — this method
        is what the signal calls, and it can also be invoked manually from
        the Django shell or admin when diagnosing a reputation discrepancy.

        The `trust` app (Vote model) doesn't exist until Phase 5, so this
        is a safe no-op until then: it looks the model up by name rather
        than importing it directly, which means nothing here needs to
        change when Phase 5 lands.
        """
        from django.apps import apps

        try:
            Vote = apps.get_model('trust', 'Vote')
        except LookupError:
            # Trust app not installed yet (pre-Phase 5). Nothing to do.
            return

        upvotes = Vote.objects.filter(
            target_entry__author=self.user, vote_type='up'
        ).count()
        downvotes = Vote.objects.filter(
            target_entry__author=self.user, vote_type='down'
        ).count()

        link_upvotes = Vote.objects.filter(
            target_link__suggested_by=self.user, vote_type='up'
        ).count()
        link_downvotes = Vote.objects.filter(
            target_link__suggested_by=self.user, vote_type='down'
        ).count()

        self.reputation_score = (upvotes - downvotes) + (link_upvotes - link_downvotes)
        self.save(update_fields=['reputation_score'])
