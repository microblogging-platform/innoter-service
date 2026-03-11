from django.db import models


class PostLike(models.Model):
    pk = models.CompositePrimaryKey("user_id", "post_id")
    user_id = models.UUIDField()
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="likes")
