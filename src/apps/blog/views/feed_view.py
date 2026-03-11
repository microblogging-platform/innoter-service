from adrf.generics import ListAPIView

from apps.blog.pagination import StandardPagination
from apps.blog.serializers.post_serializer import PostSerializer
from apps.blog.services.post_service import PostService


class FeedView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return PostService.get_feed_queryset(user_id=self.request.user.id)
