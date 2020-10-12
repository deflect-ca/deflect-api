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

class WebsiteListOptions(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
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

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class WebsiteOptionsDetails(generics.RetrieveUpdateDestroyAPIView):
    """ /api/website/<int:website_pk>/options/<int:pk> """
    serializer_class = WebsiteOptionSerializer
    queryset = WebsiteOption.objects.all()

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
