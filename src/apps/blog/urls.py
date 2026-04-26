from django.urls import path

from adrf.routers import DefaultRouter

from apps.blog.views.feed_view import FeedView
from apps.blog.views.page_view import PageViewSet, UserPagesViewSet
from apps.blog.views.post_view import PostViewSet
from apps.blog.views.tag_view import TagViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"pages", PageViewSet)
router.register(r"posts", PostViewSet)
router.register(r"tags", TagViewSet)

user_pages_list = UserPagesViewSet.as_view({"get": "list"})

urlpatterns = [
    path("feed", FeedView.as_view(), name="feed"),
    path("users/me/pages", user_pages_list, {"user_id": "me"}, name="user-me-pages"),
    path("users/<uuid:user_id>/pages", user_pages_list, name="user-pages"),
] + router.urls
