from adrf.serializers import ModelSerializer

from apps.blog.models.post import Post


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "page", "content", "reply_to", "created_at", "updated_at"]
        read_only_fields = ["id", "page", "created_at", "updated_at"]


class PostUpdateSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "page", "content", "reply_to", "created_at", "updated_at"]
        read_only_fields = ["id", "page", "reply_to", "created_at", "updated_at"]
