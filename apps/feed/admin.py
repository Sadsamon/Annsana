from django.contrib import admin

from .models import Comment, Like, Post, PostImage


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "location", "created_at", "like_count", "comment_count")
    search_fields = ("caption", "author__username")
    inlines = [PostImageInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
