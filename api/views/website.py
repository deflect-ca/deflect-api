from api.models import Website
from api.serializers import WebsiteSerializer
from rest_framework import mixins
from rest_framework import generics


class WebsiteList(mixins.ListModelMixin,
                  generics.GenericAPIView):
    """ /api/website/list """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

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
