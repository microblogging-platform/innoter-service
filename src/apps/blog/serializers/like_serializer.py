from rest_framework import serializers

from apps.blog.models.like import PostLike


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ["user_id", "post"]
        read_only_fields = ["user_id", "post"]
