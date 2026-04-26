from adrf.serializers import ModelSerializer
from rest_framework import serializers

from apps.blog.models.post import Post


class _AuthorInfoMixin:
    def _get_author_info(self, obj) -> dict | None:
        author_info_map = self.context.get("author_info_map", {})
        if not author_info_map:
            return None
        try:
            user_id = str(obj.page.user_id)
        except Exception:
            return None
        return author_info_map.get(user_id)

    def get_author_username(self, obj) -> str | None:
        info = self._get_author_info(obj)
        return info.get("username") if info else None

    def get_author_avatar_url(self, obj) -> str | None:
        info = self._get_author_info(obj)
        return info.get("avatar_url") if info else None


class PostSerializer(_AuthorInfoMixin, ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    author_username = serializers.SerializerMethodField()
    author_avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "page", "content", "reply_to", "likes_count",
            "author_username", "author_avatar_url",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "page", "created_at", "updated_at"]

    def get_likes_count(self, obj) -> int:
        if hasattr(obj, "likes_count"):
            return obj.likes_count
        return obj.likes.count()


class PostUpdateSerializer(_AuthorInfoMixin, ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    author_username = serializers.SerializerMethodField()
    author_avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "page", "content", "reply_to", "likes_count",
            "author_username", "author_avatar_url",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "page", "reply_to", "created_at", "updated_at"]

    def get_likes_count(self, obj) -> int:
        if hasattr(obj, "likes_count"):
            return obj.likes_count
        return obj.likes.count()
