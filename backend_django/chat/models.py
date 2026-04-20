from django.db import models


class Conversation(models.Model):
    user_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_email} - {self.id}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    sender = models.CharField(
        max_length=10,
        choices=[("user", "User"), ("admin", "Admin")],
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
