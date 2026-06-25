from django.contrib.auth import get_user_model
from django.views.generic import DetailView

User = get_user_model()


class ProfileView(DetailView):
    """Public profile page for a user — social side of Annsana."""

    model = User
    template_name = "users/profile.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"
