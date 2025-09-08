from django.contrib import admin
from .models import Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at", "views", "likes")
    list_display_links = ("id", "title")
    fields = ("title", "content", "author", "views", "likes")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at", "total_likes")


# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
