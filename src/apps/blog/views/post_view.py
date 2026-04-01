from adrf.mixins import DestroyModelMixin, UpdateModelMixin
from adrf.viewsets import GenericViewSet

from apps.blog.models.post import Post
from apps.blog.serializers.post_serializer import PostUpdateSerializer
from apps.blog.services.post_service import PostService
from apps.users.permissions import IsAdmin, IsModerator, IsPageOwner


class PostViewSet(
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Post.objects.select_related("page").all()
    serializer_class = PostUpdateSerializer
    permission_classes = [IsAdmin | IsModerator | IsPageOwner]
    http_method_names = ["patch", "delete"]

    async def perform_aupdate(self, serializer):
        serializer.instance = await PostService.update_post(
            post=serializer.instance,
            validated_data=serializer.validated_data,
        )

    async def perform_adestroy(self, instance):
        await PostService.delete_post(instance)
