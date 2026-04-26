from asgiref.sync import sync_to_async

from adrf.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from adrf.viewsets import GenericViewSet
from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.blog.models.page import Page
from apps.blog.models.post import Post
from apps.blog.pagination import StandardPagination
from apps.blog.serializers.follower_serializer import FollowerSerializer
from apps.blog.serializers.page_serializer import BlockPageSerializer, CreatePageSerializer, PageSerializer
from apps.blog.serializers.post_serializer import PostSerializer
from apps.blog.services.page_service import PageService
from apps.blog.services.post_service import PostService
from apps.users.client import fetch_author_info_map
from apps.users.permissions import IsAdmin, IsModerator, IsPageOwner


class PageViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Page.objects.prefetch_related("tags", "followers").annotate(followers_count=Count("followers")).all()
    serializer_class = PageSerializer
    pagination_class = StandardPagination
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    def get_serializer_class(self):
        if self.action == "block":
            return BlockPageSerializer
        if self.action == "page_posts":
            return PostSerializer
        if self.action == "create":
            return CreatePageSerializer
        return PageSerializer

    def get_permissions(self):
        match self.action:
            case "create" | "retrieve" | "follow":
                return [IsAuthenticated()]
            case "partial_update":
                return [IsPageOwner()]
            case "page_posts":
                if self.request.method == "POST":
                    return [IsPageOwner()]
                return [IsAuthenticated()]
            case "destroy" | "followers":
                return [(IsAdmin | IsModerator | IsPageOwner)()]
            case "block":
                return [(IsAdmin | IsModerator)()]
            case _:
                return [IsAuthenticated()]

    async def acreate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        await self.perform_acreate(serializer)
        page = await (
            Page.objects.prefetch_related("tags", "followers")
            .annotate(followers_count=Count("followers"))
            .aget(pk=serializer.instance.pk)
        )
        response_data = await sync_to_async(lambda: PageSerializer(page).data)()
        return Response(response_data, status=status.HTTP_201_CREATED)

    async def perform_acreate(self, serializer):
        serializer.instance = await PageService.create_page(
            validated_data=serializer.validated_data,
            user_id=self.request.user.id,
            group_id=self.request.user.group_id,
        )

    async def perform_aupdate(self, serializer):
        serializer.instance = await PageService.update_page(
            page=serializer.instance,
            validated_data=serializer.validated_data,
        )

    async def perform_adestroy(self, instance):
        await PageService.delete_page(instance)

    async def aretrieve(self, request, *args, **kwargs):
        page_obj = await self.aget_object()

        paginator = StandardPagination()
        posts_qs = (
            page_obj.posts
            .select_related("page")
            .annotate(likes_count=Count("likes"))
            .order_by("-created_at")
        )

        auth_header = request.headers.get("Authorization")
        author_info_map = await fetch_author_info_map([str(page_obj.user_id)], auth_header)

        def _build_response():
            paginated_posts = paginator.paginate_queryset(posts_qs, request)
            page_data = dict(PageSerializer(page_obj).data)
            posts_data = PostSerializer(
                paginated_posts, many=True, context={"author_info_map": author_info_map}
            ).data
            page_data["posts"] = paginator.get_paginated_response(posts_data).data
            return page_data

        return Response(await sync_to_async(_build_response)())

    @action(detail=True, methods=["post", "delete"], url_path="follow")
    async def follow(self, request, pk=None):
        page_obj = await self.aget_object()
        if request.method == "POST":
            await PageService.follow_page(page=page_obj, user_id=request.user.id)
        else:
            await PageService.unfollow_page(page=page_obj, user_id=request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="followers")
    async def followers(self, request, pk=None):
        page_obj = await self.aget_object()
        followers_qs = PageService.get_followers_queryset(page_obj)
        paginator = StandardPagination()

        def _build_response():
            paginated = paginator.paginate_queryset(followers_qs, request)
            return paginator.get_paginated_response(FollowerSerializer(paginated, many=True).data)

        return await sync_to_async(_build_response)()

    @action(detail=True, methods=["patch"], url_path="block")
    async def block(self, request, pk=None):
        page_obj = await self.aget_object()
        serializer = self.get_serializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        await PageService.block_page(page_obj, serializer.validated_data["block_days"])
        page_obj = await (
            Page.objects.prefetch_related("tags", "followers")
            .annotate(followers_count=Count("followers"))
            .aget(pk=page_obj.pk)
        )
        page_data = await sync_to_async(lambda: PageSerializer(page_obj).data)()
        return Response(page_data)

    @action(detail=True, methods=["get", "post"], url_path="posts")
    async def page_posts(self, request, pk=None):
        page_obj = await self.aget_object()

        auth_header = request.headers.get("Authorization")
        author_info_map = await fetch_author_info_map([str(page_obj.user_id)], auth_header)

        if request.method == "POST":
            serializer = PostSerializer(data=request.data)
            await sync_to_async(serializer.is_valid)(raise_exception=True)
            post = await PostService.create_post(page=page_obj, validated_data=serializer.validated_data)
            post = await Post.objects.select_related("page").filter(pk=post.pk).annotate(likes_count=Count("likes")).aget()
            post_data = await sync_to_async(
                lambda: PostSerializer(post, context={"author_info_map": author_info_map}).data
            )()
            return Response(post_data, status=status.HTTP_201_CREATED)

        posts_qs = (
            page_obj.posts
            .select_related("page")
            .filter(reply_to__isnull=True)
            .annotate(likes_count=Count("likes"))
            .order_by("-created_at")
        )
        paginator = StandardPagination()

        def _build_response():
            paginated = paginator.paginate_queryset(posts_qs, request)
            return paginator.get_paginated_response(
                PostSerializer(paginated, many=True, context={"author_info_map": author_info_map}).data
            )

        return await sync_to_async(_build_response)()


class UserPagesViewSet(ListModelMixin, GenericViewSet):
    serializer_class = PageSerializer
    pagination_class = StandardPagination

    def _get_user_id(self):
        user_id = self.kwargs.get("user_id")
        if user_id == "me":
            return str(self.request.user.id)
        return str(user_id)

    def get_queryset(self):
        return (
            Page.objects.prefetch_related("tags", "followers")
            .annotate(followers_count=Count("followers"))
            .filter(user_id=self._get_user_id())
        )

    async def alist(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = StandardPagination()

        def _build_response():
            page = paginator.paginate_queryset(queryset, request)
            data = PageSerializer(page, many=True).data
            return paginator.get_paginated_response(data)

        return await sync_to_async(_build_response)()
