from adrf.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin
from adrf.viewsets import GenericViewSet

from apps.blog.models.tag import Tag
from apps.blog.pagination import StandardPagination
from apps.blog.serializers.tag_serializer import TagSerializer


class TagViewSet(
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = StandardPagination
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = Tag.objects.all()
        name = self.request.query_params.get("filter_by_name")
        if name:
            qs = qs.filter(name__icontains=name)
        return qs
