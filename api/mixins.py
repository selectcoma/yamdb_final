from rest_framework import mixins, viewsets


class CustomMixin(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):

    class Meta:
        abstract = True
