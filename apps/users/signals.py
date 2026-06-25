from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Every User gets exactly one UserProfile, created the moment they
    register. This keeps `request.user.profile` always safe to access
    in templates and views without a null check.
    """
    if created:
        UserProfile.objects.create(user=instance)
