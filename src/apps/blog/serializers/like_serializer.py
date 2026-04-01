from adrf.serializers import ModelSerializer

from apps.blog.models.like import PostLike


class LikeSerializer(ModelSerializer):
    class Meta:
        model = PostLike
        fields = ["user_id", "post"]
        read_only_fields = ["user_id", "post"]
