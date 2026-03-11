from asgiref.sync import sync_to_async

from adrf.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from adrf.viewsets import GenericViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.blog.models.page import Page
from apps.blog.pagination import StandardPagination
from apps.blog.serializers.follower_serializer import FollowerSerializer
from apps.blog.serializers.page_serializer import BlockPageSerializer, PageSerializer
from apps.blog.serializers.post_serializer import PostSerializer
from apps.blog.services.page_service import PageService
from apps.blog.services.post_service import PostService
from apps.users.permissions import IsAdmin, IsModerator, IsPageOwner


class PageViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Page.objects.prefetch_related("tags").all()
    serializer_class = PageSerializer
    pagination_class = StandardPagination
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action == "block":
            return BlockPageSerializer
        if self.action == "create_post":
            return PostSerializer
        return PageSerializer

    def get_permissions(self):
        match self.action:
            case "create" | "retrieve" | "follow" | "unfollow":
                return [IsAuthenticated()]
            case "partial_update" | "create_post":
                return [IsPageOwner()]
            case "destroy" | "followers":
                return [(IsAdmin | IsModerator | IsPageOwner)()]
            case "block":
                return [(IsAdmin | IsModerator)()]
            case _:
                return [IsAuthenticated()]

    async def perform_create(self, serializer):
        serializer.instance = await PageService.create_page(
            validated_data=serializer.validated_data,
            user_id=self.request.user.id,
            group_id=self.request.user.group_id,
        )

    async def perform_update(self, serializer):
        serializer.instance = await PageService.update_page(
            page=serializer.instance,
            validated_data=serializer.validated_data,
        )

    async def perform_destroy(self, instance):
        await PageService.delete_page(instance)

    async def retrieve(self, request, *args, **kwargs):
        """GET /page/<page_id>?page=1&limit=30 — page info + paginated posts."""
        page_obj = await sync_to_async(self.get_object)()
        page_data = await sync_to_async(lambda: PageSerializer(page_obj).data)()

        posts_qs = page_obj.posts.order_by("-created_at")
        paginator = StandardPagination()
        paginated_posts = await sync_to_async(paginator.paginate_queryset)(posts_qs, request)
        posts_data = PostSerializer(paginated_posts, many=True).data
        paginated_response = await sync_to_async(paginator.get_paginated_response)(posts_data)
        page_data["posts"] = paginated_response.data

        return Response(page_data)

    @action(detail=True, methods=["patch"], url_path="follow")
    async def follow(self, request, pk=None):
        page_obj = await sync_to_async(self.get_object)()
        await PageService.follow_page(page=page_obj, user_id=request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="unfollow")
    async def unfollow(self, request, pk=None):
        page_obj = await sync_to_async(self.get_object)()
        await PageService.unfollow_page(page=page_obj, user_id=request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="followers")
    async def followers(self, request, pk=None):
        page_obj = await sync_to_async(self.get_object)()
        followers_qs = PageService.get_followers_queryset(page_obj)
        paginator = StandardPagination()
        paginated = await sync_to_async(paginator.paginate_queryset)(followers_qs, request)
        serializer = FollowerSerializer(paginated, many=True)
        return await sync_to_async(paginator.get_paginated_response)(serializer.data)

    @action(detail=True, methods=["patch"], url_path="block")
    async def block(self, request, pk=None):
        page_obj = await sync_to_async(self.get_object)()
        serializer = self.get_serializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        page_obj = await PageService.block_page(page_obj, serializer.validated_data["block_days"])
        return Response(PageSerializer(page_obj).data)

    @action(detail=True, methods=["post"], url_path="post")
    async def create_post(self, request, pk=None):
        page_obj = await sync_to_async(self.get_object)()
        serializer = PostSerializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        post = await PostService.create_post(page=page_obj, validated_data=serializer.validated_data)
        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
