from adrf.serializers import ModelSerializer

from apps.blog.models.tag import Tag


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]
