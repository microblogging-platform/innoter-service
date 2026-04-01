from adrf.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from apps.blog.models.page import Page
from apps.blog.models.tag import Tag
from apps.blog.serializers.tag_serializer import TagSerializer


class PageSerializer(ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, write_only=True, required=False)
    tags_info = TagSerializer(source="tags", many=True, read_only=True)

    class Meta:
        model = Page
        fields = [
            "id",
            "name",
            "description",
            "user_id",
            "group_id",
            "image_url",
            "tags",
            "tags_info",
            "is_blocked",
            "unblock_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user_id", "group_id", "is_blocked", "unblock_date", "created_at", "updated_at"]
        extra_kwargs = {
            "image_url": {"required": False},
        }


class BlockPageSerializer(Serializer):
    block_days = serializers.IntegerField(
        required=True, min_value=1, max_value=365, help_text="Enter the number of days to block"
    )
