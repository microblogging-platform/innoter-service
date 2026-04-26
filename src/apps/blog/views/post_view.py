from django.db.models import Count
from asgiref.sync import sync_to_async

from adrf.mixins import DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from adrf.viewsets import GenericViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.blog.models.post import Post
from apps.blog.pagination import StandardPagination
from apps.blog.serializers.post_serializer import PostSerializer, PostUpdateSerializer
from apps.blog.services.post_service import PostService
from apps.users.client import fetch_author_info_map
from apps.users.permissions import IsAdmin, IsModerator, IsPageOwner


class PostViewSet(
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Post.objects.select_related("page").annotate(likes_count=Count("likes")).all()
    serializer_class = PostUpdateSerializer
    permission_classes = [IsAdmin | IsModerator | IsPageOwner]
    http_method_names = ["patch", "delete", "get", "post", "head", "options"]

    async def aretrieve(self, request, *args, **kwargs):
        instance = await self.aget_object()
        auth_header = request.headers.get("Authorization")
        author_info_map = await fetch_author_info_map([str(instance.page.user_id)], auth_header)
        serializer = PostUpdateSerializer(instance, context={"author_info_map": author_info_map})
        return Response(await sync_to_async(lambda: serializer.data)())

    async def aupdate(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = await self.aget_object()
        serializer = PostUpdateSerializer(instance, data=request.data, partial=partial)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        await self.perform_aupdate(serializer)
        auth_header = request.headers.get("Authorization")
        author_info_map = await fetch_author_info_map([str(serializer.instance.page.user_id)], auth_header)
        response_serializer = PostUpdateSerializer(
            serializer.instance, context={"author_info_map": author_info_map}
        )
        return Response(await sync_to_async(lambda: response_serializer.data)())

    async def perform_aupdate(self, serializer):
        serializer.instance = await PostService.update_post(
            post=serializer.instance,
            validated_data=serializer.validated_data,
        )

    async def perform_adestroy(self, instance):
        await PostService.delete_post(instance)

    @action(detail=True, methods=["post", "delete"], url_path="like", permission_classes=[IsAuthenticated])
    async def like(self, request, pk=None):
        post = await self.aget_object()
        if request.method == "POST":
            await PostService.like_post(post=post, user_id=request.user.id)
        else:
            await PostService.unlike_post(post=post, user_id=request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="thread",
        permission_classes=[IsAuthenticated],
    )
    async def thread(self, request, pk=None):
        post = await Post.objects.select_related("page").aget(pk=pk)
        auth_header = request.headers.get("Authorization")
        author_info_map = await fetch_author_info_map([str(post.page.user_id)], auth_header)

        if request.method == "POST":
            serializer = PostSerializer(data=request.data)
            await sync_to_async(serializer.is_valid)(raise_exception=True)
            new_post = await PostService.create_post(
                page=post.page,
                validated_data={**serializer.validated_data, "reply_to": post},
            )
            new_post = await Post.objects.select_related("page").filter(pk=new_post.pk).annotate(likes_count=Count("likes")).aget()
            post_data = await sync_to_async(
                lambda: PostSerializer(new_post, context={"author_info_map": author_info_map}).data
            )()
            return Response(post_data, status=status.HTTP_201_CREATED)

        replies = (
            Post.objects.select_related("page")
            .filter(reply_to=post)
            .annotate(likes_count=Count("likes"))
            .order_by("created_at")
        )
        paginator = StandardPagination()

        def _build_response():
            page = paginator.paginate_queryset(replies, request)
            if page is not None:
                return paginator.get_paginated_response(
                    PostSerializer(page, many=True, context={"author_info_map": author_info_map}).data
                )
            return Response(PostSerializer(list(replies), many=True, context={"author_info_map": author_info_map}).data)

        return await sync_to_async(_build_response)()
