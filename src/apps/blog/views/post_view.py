from adrf.mixins import DestroyModelMixin, UpdateModelMixin
from adrf.viewsets import GenericViewSet

from apps.blog.models.post import Post
from apps.blog.serializers.post_serializer import PostSerializer
from apps.blog.services.post_service import PostService
from apps.users.permissions import IsAdmin, IsModerator, IsPageOwner


class PostViewSet(
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Post.objects.select_related("page").all()
    serializer_class = PostSerializer
    permission_classes = [IsAdmin | IsModerator | IsPageOwner]
    http_method_names = ["patch", "delete"]

    async def perform_update(self, serializer):
        serializer.instance = await PostService.update_post(
            post=serializer.instance,
            validated_data=serializer.validated_data,
        )

    async def perform_destroy(self, instance):
        await PostService.delete_post(instance)
