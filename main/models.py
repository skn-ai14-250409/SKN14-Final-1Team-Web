from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author} : {self.content[:20]}'

class ChatMode(models.TextChoices):
    API = "api", "API"
    INTERNAL = "internal", "Internal"


# 채팅 세션
class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
    )
    title = models.CharField(max_length=200)
    mode = models.CharField(max_length=20, choices=ChatMode.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_session"
        ordering = ["-created_at"]  # 최신부터

    def __str__(self):
        return f"[{self.mode}] {self.title}"


# 채팅 메시지: 세션별 메시지
class ChatMessage(models.Model):
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(
        max_length=20, choices=[("user", "User"), ("assistant", "Assistant")]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_message"
        ordering = ["created_at"]  # 시간순

    def __str__(self):
        return f"{self.session.title}, {self.role}: {self.content[:30]}"


# 즐겨찾기 카드
class Card(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cards",
    )
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cards",
    )
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "card"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title}"


# 카드에 포함된 메시지
class CardMessage(models.Model):
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name="card_messages",
    )
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="in_cards",
    )
    position = models.IntegerField()

    class Meta:
        db_table = "card_message"
        unique_together = [("card", "message")]
        ordering = ["position"]

    def __str__(self):
        return f"{self.card.title} #{self.position}"

