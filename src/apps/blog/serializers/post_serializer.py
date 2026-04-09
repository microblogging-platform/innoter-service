from adrf.serializers import ModelSerializer
from rest_framework import serializers

from apps.blog.models.post import Post


class PostSerializer(ModelSerializer):
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "page", "content", "reply_to", "likes_count", "created_at", "updated_at"]
        read_only_fields = ["id", "page", "created_at", "updated_at"]

    def get_likes_count(self, obj) -> int:
        if hasattr(obj, "likes_count"):
            return obj.likes_count
        return obj.likes.count()


class PostUpdateSerializer(ModelSerializer):
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "page", "content", "reply_to", "likes_count", "created_at", "updated_at"]
        read_only_fields = ["id", "page", "reply_to", "created_at", "updated_at"]

    def get_likes_count(self, obj) -> int:
        if hasattr(obj, "likes_count"):
            return obj.likes_count
        return obj.likes.count()
