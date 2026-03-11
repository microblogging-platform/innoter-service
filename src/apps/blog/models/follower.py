from django.db import models


class PageFollower(models.Model):
    pk = models.CompositePrimaryKey("user_id", "page_id")
    user_id = models.UUIDField()
    page = models.ForeignKey("Page", on_delete=models.CASCADE, related_name="followers")
