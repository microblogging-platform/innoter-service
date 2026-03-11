from django.urls import path

from adrf.routers import DefaultRouter

from apps.blog.views.feed_view import FeedView
from apps.blog.views.page_view import PageViewSet
from apps.blog.views.post_view import PostViewSet
from apps.blog.views.tag_view import TagViewSet

router = DefaultRouter()
router.register(r"page", PageViewSet)
router.register(r"post", PostViewSet)
router.register(r"tags", TagViewSet)

urlpatterns = [
    path("feed", FeedView.as_view(), name="feed"),
    path("tag", TagViewSet.as_view({"post": "create"}), name="tag-create"),
] + router.urls
