from django.contrib.auth.models import UserManager as DjangoUserManager


class UserManager(DjangoUserManager):
    """
    Custom manager reserved for Annsana-specific user queries
    (e.g. surfacing archival contributors on the feed/profile pages).
    """

    def contributors(self):
        return self.filter(is_contributor=True)
