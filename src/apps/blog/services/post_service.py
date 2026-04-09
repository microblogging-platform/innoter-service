from django.db.models import Count, QuerySet

from apps.blog.models.page import Page
from apps.blog.models.post import Post


class PostService:
    @staticmethod
    async def create_post(page: Page, validated_data: dict) -> Post:
        return await Post.objects.acreate(page=page, **validated_data)

    @staticmethod
    async def update_post(post: Post, validated_data: dict) -> Post:
        for attr, value in validated_data.items():
            setattr(post, attr, value)
        await post.asave()
        return post

    @staticmethod
    async def delete_post(post: Post) -> None:
        await post.adelete()

    @staticmethod
    def get_feed_queryset(user_id) -> QuerySet[Post]:
        return (
            Post.objects.filter(
                page__followers__user_id=user_id,
                page__is_blocked=False,
            )
            .select_related("page")
            .annotate(likes_count=Count("likes"))
            .order_by("-created_at")
        )
