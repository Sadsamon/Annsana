from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView

from .forms import CommentForm, PostForm
from .models import Like, Post, PostImage


class FeedListView(ListView):
    """The main feed — chronological for Phase 2, rankable later."""

    model = Post
    template_name = "feed/feed_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.with_related().order_by("-created_at")

    def get_template_names(self):
        # HTMX "infinite scroll" requests for page 2+ only need the partial.
        if getattr(self.request, "htmx", False) and self.request.GET.get("page"):
            return ["feed/partials/post_list.html"]
        return [self.template_name]


class PostDetailView(DetailView):
    model = Post
    template_name = "feed/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.with_related()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.select_related("author")
        context["comment_form"] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "feed/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        for position, image in enumerate(form.cleaned_data.get("images") or []):
            PostImage.objects.create(post=self.object, image=image, position=position)
        return response

    def get_success_url(self):
        return reverse("feed:detail", args=[self.object.pk])


@login_required
@require_POST
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return render(request, "feed/partials/like_button.html", {"post": post})


@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    context = {
        "post": post,
        "comments": post.comments.select_related("author"),
        "comment_form": CommentForm(),
    }
    return render(request, "feed/partials/comment_list.html", context)
