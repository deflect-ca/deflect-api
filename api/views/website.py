from django.http import Http404

from rest_framework import mixins, generics
from rest_framework.response import Response

from api.models import Website, WebsiteOption
from api.serializers import WebsiteSerializer, WebsiteListSerializer, WebsiteOptionSerializer


class WebsiteList(mixins.ListModelMixin,
                  generics.GenericAPIView):
    """ /api/website/list """
    queryset = Website.objects.all()
    serializer_class = WebsiteListSerializer  # do not show options

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class WebsiteDetail(mixins.RetrieveModelMixin,
                    generics.GenericAPIView):
    """ /api/website/<int:pk> """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class WebsiteCreate(mixins.CreateModelMixin,
                    generics.GenericAPIView):
    """ /api/website/create """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class WebsiteModify(mixins.UpdateModelMixin,
                    generics.GenericAPIView):
    """ /api/website/modify/<int:pk> """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class WebsiteDelete(mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    """ /api/website/delete/<int:pk> """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class WebsiteListOptions(mixins.ListModelMixin,
                         generics.GenericAPIView):
    """ /api/website/<int:pk>/options """
    serializer_class = WebsiteOptionSerializer

    def get_queryset(self):
        try:
            website = Website.objects.get(
                pk=self.kwargs['pk'])
        except Website.DoesNotExist:
            raise Http404
        return website.options.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class WebsiteOptionsDetail(mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin,
                           generics.GenericAPIView):
    """ /api/website/<int:pk>/options/<str:name> """
    serializer_class = WebsiteOptionSerializer
    lookup_field = 'name'

    def get_queryset(self):
        return WebsiteOption.objects.filter(website_id=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
