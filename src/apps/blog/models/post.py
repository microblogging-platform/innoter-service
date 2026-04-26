import uuid

from django.db import models

from apps.blog.models.mixins.timestamp import TimeStampedMixin


class Post(TimeStampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey("Page", on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    reply_to = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies"
    )
