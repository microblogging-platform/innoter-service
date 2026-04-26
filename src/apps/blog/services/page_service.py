from datetime import timedelta

from django.db.models import QuerySet
from django.utils import timezone

from apps.blog.models.follower import PageFollower
from apps.blog.models.page import Page


class PageService:
    @staticmethod
    async def create_page(validated_data: dict, user_id, group_id=None) -> Page:
        tags = validated_data.pop("tags", [])
        page = await Page.objects.acreate(**validated_data, user_id=user_id, group_id=group_id)
        if tags:
            await page.tags.aset(tags)
        return page

    @staticmethod
    async def update_page(page: Page, validated_data: dict) -> Page:
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(page, attr, value)
        await page.asave()
        if tags is not None:
            await page.tags.aset(tags)
        return page

    @staticmethod
    async def delete_page(page: Page) -> None:
        await page.adelete()

    @staticmethod
    async def block_page(page: Page, block_days: int) -> Page:
        page.is_blocked = True
        page.unblock_date = timezone.now() + timedelta(days=block_days)
        await page.asave(update_fields=["is_blocked", "unblock_date"])
        return page

    @staticmethod
    async def unblock_page(page: Page) -> Page:
        page.is_blocked = False
        page.unblock_date = None
        await page.asave(update_fields=["is_blocked", "unblock_date"])
        return page

    @staticmethod
    async def follow_page(page: Page, user_id) -> PageFollower:
        follower, _ = await PageFollower.objects.aget_or_create(user_id=user_id, page=page)
        return follower

    @staticmethod
    async def unfollow_page(page: Page, user_id) -> None:
        await PageFollower.objects.filter(user_id=user_id, page=page).adelete()

    @staticmethod
    def get_followers_queryset(page: Page) -> QuerySet[PageFollower]:
        return page.followers.all()
