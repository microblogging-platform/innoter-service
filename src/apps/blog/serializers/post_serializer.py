from rest_framework import serializers

from apps.blog.models.post import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "page", "content", "reply_to", "created_at", "updated_at"]
        read_only_fields = ["id", "page", "created_at", "updated_at"]
