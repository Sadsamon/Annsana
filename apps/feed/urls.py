from django.urls import path

from . import views

app_name = "feed"

urlpatterns = [
    path("", views.FeedListView.as_view(), name="list"),
    path("new/", views.PostCreateView.as_view(), name="create"),
    path("<uuid:pk>/", views.PostDetailView.as_view(), name="detail"),
    path("<uuid:pk>/like/", views.toggle_like, name="like"),
    path("<uuid:pk>/comment/", views.add_comment, name="comment"),
]
