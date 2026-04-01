from adrf.serializers import ModelSerializer

from apps.blog.models.follower import PageFollower


class FollowerSerializer(ModelSerializer):
    class Meta:
        model = PageFollower
        fields = ["user_id"]
        read_only_fields = ["user_id"]
