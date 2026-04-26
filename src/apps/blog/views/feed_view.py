from asgiref.sync import sync_to_async

from adrf.generics import ListAPIView

from apps.blog.pagination import StandardPagination
from apps.blog.serializers.post_serializer import PostSerializer
from apps.blog.services.post_service import PostService
from apps.users.client import fetch_author_info_map


class FeedView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return PostService.get_feed_queryset(user_id=self.request.user.id)

    async def alist(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = StandardPagination()

        posts = await sync_to_async(paginator.paginate_queryset)(queryset, request)

        user_ids = {str(post.page.user_id) for post in posts}
        auth_header = request.headers.get("Authorization")
        author_info_map = await fetch_author_info_map(user_ids, auth_header)

        def _serialize():
            data = PostSerializer(posts, many=True, context={"author_info_map": author_info_map}).data
            return paginator.get_paginated_response(data)

        return await sync_to_async(_serialize)()
