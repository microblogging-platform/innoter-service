import uuid
from django.db import models
from apps.blog.models.mixins.timestamp import TimeStampedMixin


class Page(TimeStampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=144, unique=True)
    description = models.TextField(blank=True)
    user_id = models.UUIDField(editable=False)
    group_id = models.IntegerField(null=True, blank=True, editable=False)
    image_url = models.URLField(max_length=1024, blank=True, null=True)
    tags = models.ManyToManyField("Tag", related_name="tags", blank=True)
    is_blocked = models.BooleanField(default=False)
    unblock_date = models.DateTimeField(null=True, blank=True, default=None)